"""Hitung tautan rantai dampak yang BISA dihitung dari sistem sendiri.

    python -m scripts.19_rantai_dampak
    python -m scripts.19_rantai_dampak --pasangan 500

APA YANG DIISI SKRIP INI, DAN APA YANG TETAP KOSONG.

Rantai estimasi dampak di proposal punya tujuh tautan. Sebagian berasal dari
sumber luar dan tidak boleh dikarang; sebagian lagi adalah keluaran sistem
ini sendiri dan justru TIDAK BOLEH dibiarkan kosong, karena kita memilikinya.

Yang DIHITUNG di sini, dari menjalankan mesin perutean berulang kali:

    selisih waktu per perjalanan
    selisih jarak per perjalanan
    selisih bahan bakar per perjalanan
    selisih emisi per perjalanan
    proporsi perjalanan yang rutenya memang berubah

Yang TETAP kosong dan wajib ditandai TODO(sumber) di proposal:

    panjang total jaringan jalan Kota Semarang   perlu sumber resmi
    jumlah perjalanan terdampak per hari         perlu data lalu lintas
    tingkat adopsi                               asumsi, bukan pengukuran

CARA PENGAMBILAN SAMPEL, DAN KENAPA BEGITU.

Pasangan asal-tujuan diambil acak dari titik tengah ruas, dengan dua syarat:
jaraknya minimal dua kilometer supaya bukan perjalanan sepele, dan keduanya
berada di dalam AOI.

Yang dilaporkan MEDIAN beserta kuartil, bukan rata-rata. Sebaran selisih rute
sangat menceng: sebagian besar perjalanan tidak terpengaruh sama sekali,
sementara segelintir yang melewati kawasan tergenang berputar jauh.
Rata-ratanya akan ditarik oleh ekor itu dan menghasilkan angka yang tidak
mewakili perjalanan mana pun.

Dihitung pada JAM PASUT TERTINGGI di dalam jendela prediksi. Itu keadaan
terburuk, dan dinyatakan demikian di proposal — bukan disamarkan sebagai
rata-rata harian.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import numpy as np

from app import config, db
from app.domain import dampak, routing

BERKAS = config.DIR_DATA_REFERENSI / "rantai_dampak.json"
JARAK_MIN_KM = 2.0
PASANGAN = 300
MODA = "mobil"


def muat_graf():
    with db.koneksi() as kon:
        ruas = db.RepositoriRuas(kon).semua_untuk_routing()
        ambang = db.RepositoriRuas(kon).ambang_moda()
    return routing.GrafJalan(ruas), ambang, ruas


def jam_puncak(peta_kedalaman: dict) -> datetime | None:
    """Jam dengan ruas tergenang terbanyak. Keadaan terburuk, bukan rata-rata."""
    if not peta_kedalaman:
        return None
    return max(peta_kedalaman, key=lambda w: len(peta_kedalaman[w]))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pasangan", type=int, default=PASANGAN)
    p.add_argument("--moda", default=MODA)
    a = p.parse_args()

    print("memuat graf ...")
    graf, ambang_semua, ruas = muat_graf()
    ambang = ambang_semua[a.moda]

    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        awal, akhir = repo.rentang_waktu()
        peta = repo.peta_kedalaman(awal, akhir) if awal else {}
    puncak = jam_puncak(peta)
    if puncak is None:
        raise SystemExit("Tabel prediksi kosong. Jalankan skrip 11 lebih dulu.")
    print(f"jam puncak : {puncak.astimezone(config.ZONA_WAKTU_LOKAL)} WIB")
    print(f"ruas tergenang pada jam itu: {len(peta[puncak]):,}")
    print(f"moda       : {a.moda}\n")

    titik = np.array([[r["koordinat"][0][0], r["koordinat"][0][1]]
                      for r in ruas])
    acak = np.random.default_rng(2026)

    selisih_menit, selisih_km, berubah = [], [], 0
    pasangan_dipakai = []
    dicoba = 0
    while len(selisih_menit) < a.pasangan and dicoba < a.pasangan * 6:
        dicoba += 1
        i, j = acak.integers(0, len(titik), 2)
        asal, tujuan = titik[i], titik[j]
        # Jarak garis lurus kasar, hanya untuk menyaring pasangan sepele.
        dx = (asal[0] - tujuan[0]) * 110.6
        dy = (asal[1] - tujuan[1]) * 110.9
        if (dx * dx + dy * dy) ** 0.5 < JARAK_MIN_KM:
            continue

        hasil = routing.dua_rute(graf, tuple(asal), tuple(tujuan),
                                 puncak, ambang, peta)
        if "galat" in hasil:
            continue
        abai, sadar = hasil["rute_abai_rob"], hasil["rute_sadar_rob"]
        if not (abai.ditemukan and sadar.ditemukan):
            continue

        pasangan_dipakai.append((asal, tujuan))
        selisih_menit.append((sadar.detik - abai.detik) / 60.0)
        selisih_km.append((sadar.jarak_m - abai.jarak_m) / 1000.0)
        if abai.edge_ids != sadar.edge_ids:
            berubah += 1

        if len(selisih_menit) % 50 == 0:
            print(f"  {len(selisih_menit):>3}/{a.pasangan} pasangan",
                  flush=True)

    # ── NILAI SARAN WAKTU, BUKAN NILAI MEMUTAR ─────────────────────────
    #
    # Ukuran di atas menjawab pertanyaan "berapa mahal memutar". Itu bukan
    # klaim utama sistem ini. Klaim utamanya adalah memprediksi KAPAN ruas
    # berisiko, dan nilainya muncul saat orang MENGGESER JAM BERANGKAT,
    # bukan saat ia memutar pada jam yang sama.
    #
    # Diukur di sini: berapa lama perjalanan yang sama pada jam puncak
    # dibandingkan pada jam paling lapang dalam enam jam sesudahnya. Itulah
    # yang benar-benar ditawarkan tombol "berangkat pukul sekian".
    from datetime import timedelta

    jam_calon = [puncak + timedelta(hours=h) for h in range(0, 7)]
    jam_calon = [j for j in jam_calon if j in peta or not peta.get(j)]
    hemat_geser = []
    for i in range(min(len(pasangan_dipakai), 120)):
        asal, tujuan = pasangan_dipakai[i]
        terbaik = None
        pada_puncak = None
        for j in jam_calon:
            h = routing.dua_rute(graf, tuple(asal), tuple(tujuan), j,
                                 ambang, peta)
            if "galat" in h or not h["rute_sadar_rob"].ditemukan:
                continue
            detik = h["rute_sadar_rob"].detik
            if j == puncak:
                pada_puncak = detik
            terbaik = detik if terbaik is None else min(terbaik, detik)
        if pada_puncak is not None and terbaik is not None:
            hemat_geser.append((pada_puncak - terbaik) / 60.0)

    if len(selisih_menit) < 30:
        raise SystemExit(f"Hanya {len(selisih_menit)} pasangan berhasil.")

    m = np.array(selisih_menit)
    k = np.array(selisih_km)
    n = len(m)
    p_berubah = berubah / n

    def kuartil(x):
        return {"p25": round(float(np.percentile(x, 25)), 3),
                "median": round(float(np.median(x)), 3),
                "p75": round(float(np.percentile(x, 75)), 3),
                "rata": round(float(x.mean()), 3)}

    # Bahan bakar dan emisi dihitung lewat modul dampak yang sama dengan yang
    # dipakai antarmuka, supaya angka di proposal dan angka di layar tidak
    # pernah bisa berbeda.
    d_median = dampak.hitung(float(np.median(m)), float(np.median(k)), ambang)
    d_p75 = dampak.hitung(float(np.percentile(m, 75)),
                          float(np.percentile(k, 75)), ambang)

    print()
    print(f"pasangan berhasil          : {n}")
    print(f"rute BERUBAH karena rob    : {berubah} ({100 * p_berubah:.1f} persen)")
    print()
    print(f"{'':<28}{'p25':>9}{'median':>9}{'p75':>9}{'rata':>9}")
    for nama, x in (("selisih waktu (menit)", m), ("selisih jarak (km)", k)):
        q = kuartil(x)
        print(f"{nama:<28}{q['p25']:>9.2f}{q['median']:>9.2f}"
              f"{q['p75']:>9.2f}{q['rata']:>9.2f}")
    print()
    if hemat_geser:
        g = np.array(hemat_geser)
        print(f"NILAI MENGGESER JAM BERANGKAT ({len(g)} perjalanan, "
              "puncak vs jam terlapang dalam 6 jam berikutnya)")
        print(f"  median : {np.median(g):.2f} menit")
        print(f"  p75    : {np.percentile(g, 75):.2f} menit")
        print(f"  p90    : {np.percentile(g, 90):.2f} menit")
        print(f"  maks   : {g.max():.2f} menit")
        print()

    print("pada perjalanan MEDIAN:")
    print(f"  bahan bakar : {d_median['liter']['bawah']:.3f} sampai "
          f"{d_median['liter']['atas']:.3f} L")
    print(f"  emisi       : {d_median['kg_co2e']['bawah']:.3f} sampai "
          f"{d_median['kg_co2e']['atas']:.3f} kg CO2e")
    print("pada perjalanan persentil ke-75:")
    print(f"  bahan bakar : {d_p75['liter']['bawah']:.3f} sampai "
          f"{d_p75['liter']['atas']:.3f} L")
    print(f"  emisi       : {d_p75['kg_co2e']['bawah']:.3f} sampai "
          f"{d_p75['kg_co2e']['atas']:.3f} kg CO2e")

    with db.koneksi() as kon:
        panjang_km = db.RepositoriRuas(kon).panjang_total_km()

    BERKAS.write_text(json.dumps({
        "_catatan": ("Tautan rantai dampak yang dihitung dari sistem sendiri. "
                     "Tautan yang butuh sumber luar TIDAK ada di sini dan "
                     "wajib ditandai TODO(sumber) di proposal."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "moda": a.moda,
        "jam_puncak_utc": puncak.isoformat(),
        "ruas_tergenang_saat_puncak": len(peta[puncak]),
        "pasangan_diuji": n,
        "jarak_minimum_km": JARAK_MIN_KM,
        "proporsi_rute_berubah": round(p_berubah, 4),
        "selisih_waktu_menit": kuartil(m),
        "selisih_jarak_km": kuartil(k),
        "hemat_geser_jam_menit": (
            kuartil(np.array(hemat_geser)) if hemat_geser else None),
        "hemat_geser_jam_p90": (
            round(float(np.percentile(hemat_geser, 90)), 3)
            if hemat_geser else None),
        "hemat_geser_jam_maks": (
            round(float(max(hemat_geser)), 3) if hemat_geser else None),
        "perjalanan_diuji_geser": len(hemat_geser),
        "dampak_perjalanan_median": d_median,
        "dampak_perjalanan_p75": d_p75,
        "panjang_jaringan_aoi_km": round(panjang_km, 1),
        "_yang_tetap_kosong": {
            "panjang_jaringan_kota_semarang_km": None,
            "perjalanan_terdampak_per_hari": None,
            "tingkat_adopsi": None,
            "_catatan": ("Ketiganya butuh sumber luar atau asumsi yang harus "
                         "dinyatakan sebagai asumsi. Jangan diisi dari sini."),
        },
        "_peringatan": [
            "Dihitung pada JAM PASUT TERTINGGI, yaitu keadaan terburuk. Bukan "
            "rata-rata harian, dan tidak boleh disajikan sebagai rata-rata.",
            "Median dilaporkan, bukan rata-rata, karena sebarannya menceng: "
            "sebagian besar perjalanan tidak terpengaruh sama sekali.",
            "Bahan bakar dan emisi memakai faktor di tabel ambang_moda yang "
            "konsumsinya masih asumsi tanpa sitasi.",
            "Genangan yang mendasarinya berasal dari indeks kerentanan, bukan "
            "model tervalidasi. Angka di sini mewarisi seluruh batasan itu.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
