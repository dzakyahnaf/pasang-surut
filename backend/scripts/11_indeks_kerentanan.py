"""Hitung indeks kerentanan per ruas, lalu isi prediksi_genangan 72 jam.

    python -m scripts.11_indeks_kerentanan            # 72 jam sejak jam ini
    python -m scripts.11_indeks_kerentanan --mulai 2026-05-18
    python -m scripts.11_indeks_kerentanan --hanya-indeks

INI JALUR CADANGAN PLAN.md BAGIAN 9.A, dipakai karena jalur utama gagal dan
kegagalannya sudah dibuktikan, bukan karena jalur utama belum dicoba.

Dasar pemikirannya ada di app/domain/kerentanan.py. Skrip ini hanya
menjalankannya di atas data nyata, memeriksa kewarasannya terhadap lokasi
kejadian yang dilaporkan, lalu menuliskan hasilnya.

PEMERIKSAAN KEWARASAN, BUKAN PENGUKURAN AKURASI.

Lokasi rob yang dilaporkan media dipakai untuk memeriksa apakah indeks ini
menempatkan kawasan itu di peringkat atas. Itu pemeriksaan kewarasan, BUKAN
pengukuran akurasi, dan bedanya penting:

Kawasan yang dilaporkan tergenang seluruhnya berada di pesisir, sedangkan
jarak ke pantai adalah salah satu komponen indeks. Jadi indeks ini memang
SUDAH SEHARUSNYA menempatkan kawasan itu di atas — kalau tidak, justru ada
yang salah dengan kodenya. Melaporkan angka itu sebagai akurasi berarti
mengukur diri sendiri dengan penggaris buatan sendiri.

Karena itu yang dicetak hanyalah peringkat persentil, tanpa satu pun angka
AUC atau F1. Aturan repo nomor 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pyproj

from app import config, db
from app.domain import genangan, kerentanan

SUMBER = "kerentanan_v1"
JAM_KE_DEPAN = 72

# Kawasan yang berulang kali disebut tergenang di data/referensi/
# kejadian_rob_semarang.json. Dipakai HANYA untuk memeriksa kewarasan.
JALAN_DILAPORKAN = ("Kaligawe", "Terboyo", "Bandarharjo", "Genuk")

BERKAS_INDEKS = config.DIR_DATA_OLAHAN / "indeks_kerentanan.json"


def muat_ruas():
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT edge_id, nama, elevasi_m, jarak_pantai_m,
                       laju_subsidensi_cm_thn,
                       ST_X(ST_LineInterpolatePoint(geom, 0.5)),
                       ST_Y(ST_LineInterpolatePoint(geom, 0.5))
                FROM ruas_jalan ORDER BY edge_id
                """
            )
            return kur.fetchall()


def acuan_pasut() -> tuple[float, float]:
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT percentile_cont(0.5)   WITHIN GROUP (ORDER BY tinggi_pasut_m),
                       percentile_cont(0.999) WITHIN GROUP (ORDER BY tinggi_pasut_m)
                FROM pemicu
                """
            )
            a, b = kur.fetchone()
    return float(a), float(b)


def pemicu_jendela(mulai: datetime, jam: int):
    selesai = mulai + timedelta(hours=jam - 1)
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                "SELECT waktu, tinggi_pasut_m FROM pemicu "
                "WHERE waktu BETWEEN %s AND %s ORDER BY waktu",
                (mulai, selesai),
            )
            baris = kur.fetchall()
    if len(baris) < jam:
        raise SystemExit(
            f"Tabel pemicu hanya punya {len(baris)} dari {jam} jam yang diminta.\n"
            "Jalankan `python -m scripts.06_isi_pemicu --prakiraan` lebih dulu."
        )
    return baris


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--mulai", default=None)
    pengurai.add_argument("--jam", type=int, default=JAM_KE_DEPAN)
    pengurai.add_argument("--hanya-indeks", action="store_true")
    pengurai.add_argument("--puncak-terdampak", type=float, default=0.10,
                          help="proporsi ruas terdampak saat pasut tertinggi")
    pengurai.add_argument("--pertahankan-dummy", action="store_true")
    argumen = pengurai.parse_args()

    baris = muat_ruas()
    edge = np.array([b[0] for b in baris], dtype=np.int64)
    nama = [b[1] for b in baris]
    elev = np.array([np.nan if b[2] is None else float(b[2]) for b in baris])
    jarak = np.array([np.nan if b[3] is None else float(b[3]) for b in baris])
    subs = np.array([np.nan if b[4] is None else float(b[4]) for b in baris])
    lon = np.array([float(b[5]) for b in baris])
    lat = np.array([float(b[6]) for b in baris])

    print(f"ruas: {len(edge):,}\n")

    # Elevasi relatif wajib dihitung di meter. Derajat bukan meter, dan
    # radius 500 dalam derajat berarti setengah keliling Jawa.
    ke_metrik = pyproj.Transformer.from_crs(
        config.CRS_SIMPAN, config.CRS_METRIK, always_xy=True)
    x_m, y_m = ke_metrik.transform(lon, lat)

    print("menghitung elevasi relatif terhadap tetangga radius 500 m ...")
    elev_rel = kerentanan.elevasi_relatif(elev, np.asarray(x_m), np.asarray(y_m))
    sah = np.isfinite(elev_rel)
    print(f"  terhitung {int(sah.sum()):,} ruas")
    print(f"  rentang  : {np.nanmin(elev_rel):+.2f} sampai "
          f"{np.nanmax(elev_rel):+.2f} m terhadap tetangga")
    print(f"  simpangan: {np.nanstd(elev_rel):.2f} m "
          f"(bandingkan elevasi mutlak {np.nanstd(elev):.2f} m)\n")

    skor, komponen = kerentanan.indeks(elev_rel, jarak, subs)
    print("indeks kerentanan")
    print(f"  terhitung: {int(np.isfinite(skor).sum()):,} ruas")
    for p in (5, 25, 50, 75, 95, 99):
        print(f"  persentil {p:>2}: {np.nanpercentile(skor, p):.3f}")
    print()

    # ── PEMERIKSAAN KEWARASAN ──────────────────────────────────────────
    print("pemeriksaan kewarasan terhadap jalan yang dilaporkan tergenang")
    print("  (BUKAN pengukuran akurasi; alasannya di docstring skrip ini)")
    peringkat = np.full(len(skor), np.nan)
    ok = np.isfinite(skor)
    peringkat[ok] = 100.0 * (
        np.argsort(np.argsort(skor[ok])) / max(int(ok.sum()) - 1, 1))
    for kata in JALAN_DILAPORKAN:
        m = np.array([bool(n) and n != "nan" and kata.lower() in n.lower()
                      for n in nama])
        m &= ok
        if not m.any():
            print(f"  {kata:<14} tidak ada ruas bernama itu")
            continue
        print(f"  {kata:<14} {int(m.sum()):>4} ruas, "
              f"persentil median {np.median(peringkat[m]):5.1f}, "
              f"indeks median {np.median(skor[m]):.3f}")
    print(f"  {'seluruh ruas':<14} {int(ok.sum()):>4} ruas, "
          f"persentil median  50.0, indeks median {np.nanmedian(skor):.3f}")
    print()

    BERKAS_INDEKS.write_text(json.dumps({
        "_catatan": ("Indeks kerentanan rob per ruas, jalur cadangan PLAN.md "
                     "bagian 9.A. BUKAN prediksi genangan dan tidak punya "
                     "metrik akurasi. Dasar pemikiran di "
                     "backend/app/domain/kerentanan.py."),
        "dihitung": datetime.now(timezone.utc).isoformat(),
        "bobot": kerentanan.BOBOT,
        "radius_elevasi_relatif_m": 500,
        "ruas": int(ok.sum()),
        "sebaran": {f"p{p}": round(float(np.nanpercentile(skor, p)), 4)
                    for p in (1, 5, 25, 50, 75, 95, 99)},
        "_peringatan": [
            "Indeks ini TIDAK punya akurasi yang bisa dilaporkan. Tidak ada "
            "pengamatan genangan per ruas untuk mengujinya.",
            "Pemeriksaan terhadap jalan yang dilaporkan tergenang bersifat "
            "MELINGKAR: kawasan itu pesisir, dan jarak pantai adalah salah "
            "satu komponen indeks.",
            "Bobot sepertiga untuk tiap komponen adalah asumsi, bukan hasil "
            "penyetelan terhadap data.",
        ],
        "indeks": {int(edge[i]): round(float(skor[i]), 4)
                   for i in range(len(edge)) if np.isfinite(skor[i])},
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"tersimpan: {BERKAS_INDEKS.name}")
    if argumen.hanya_indeks:
        return 0

    # ── PREDIKSI PER JAM ───────────────────────────────────────────────
    mulai = (datetime.fromisoformat(argumen.mulai).replace(tzinfo=timezone.utc)
             if argumen.mulai else
             datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0))
    jam_pemicu = pemicu_jendela(mulai, argumen.jam)
    bawah, puncak = acuan_pasut()

    print(f"\njendela: {mulai:%Y-%m-%d %H:%M} UTC, {argumen.jam} jam")
    print(f"acuan pasut: bawah {bawah:+.3f} m, puncak {puncak:+.3f} m")
    print(f"proporsi terdampak saat pasut tertinggi: "
          f"{100 * argumen.puncak_terdampak:.0f} persen\n")

    # BERAPA BANYAK RUAS YANG TERDAMPAK, DAN DARI MANA ANGKANYA.
    #
    # Ambang indeks yang TETAP tidak masuk akal: ia menyatakan proporsi
    # jaringan yang sama tergenang saat surut terendah dan saat pasang
    # tertinggi. Yang dipakai di sini adalah proporsi yang MENGIKUTI PASUT:
    # nol saat pasut di atau di bawah acuan bawah, dan mencapai puncaknya saat
    # pasut menyentuh acuan atas.
    #
    # Skalanya diikat ke angka yang sudah menjadi jangkar proposal: riset WRI
    # Indonesia memperkirakan sekitar 10 persen jaringan jalan Kota Semarang
    # berpotensi terdampak rob. Angka itu berlaku untuk SELURUH kota,
    # sedangkan AOI ini justru bagian yang paling terdampak, sehingga
    # memakainya apa adanya bersifat konservatif. Itu memang yang dipilih.
    #
    # Yang menentukan ruas MANA adalah indeks kerentanan; yang menentukan
    # BERAPA BANYAK adalah pasut. Keduanya terpisah dan bisa diperiksa
    # sendiri-sendiri. Indeks menggantikan peran probabilitas pada fungsi
    # kedalaman, dan sifat yang dituntut fungsi itu sama saja sehingga seluruh
    # ujinya tetap berlaku.
    skor_isi = np.nan_to_num(skor, nan=0.0)
    hasil, ringkas = [], []
    for waktu, tinggi in jam_pemicu:
        s_pasut = float(np.clip(
            (float(tinggi) - bawah) / max(puncak - bawah, 1e-9), 0.0, 1.0))
        proporsi = argumen.puncak_terdampak * s_pasut
        if proporsi <= 0.0:
            ringkas.append((waktu, float(tinggi), 0, 0.0))
            continue
        potong = float(np.quantile(skor_isi, 1.0 - proporsi))
        dalam = genangan.kedalaman_cm(skor_isi, float(tinggi), potong,
                                      bawah, puncak)
        pilih = np.flatnonzero(dalam > 0)
        for i in pilih:
            hasil.append((int(edge[i]), waktu, round(float(dalam[i]), 1),
                          round(float(skor[i]), 4), SUMBER))
        ringkas.append((waktu, float(tinggi), len(pilih),
                        float(dalam.max()) if len(pilih) else 0.0))

    print(f"{'waktu WIB':<17} {'pasut':>8} {'tergenang':>10} {'maks cm':>8}")
    for waktu, tinggi, n, maks in ringkas[::6]:
        wib = waktu.astimezone(config.ZONA_WAKTU_LOKAL)
        print(f"{wib:%Y-%m-%d %H:%M}  {tinggi:+7.3f} {n:>10,} {maks:>8.1f}")

    puncak_n = max(n for _, _, n, _ in ringkas)
    jam_kering = sum(1 for _, _, n, _ in ringkas if n == 0)
    print(f"\njam tanpa genangan: {jam_kering} dari {len(ringkas)}")
    print(f"\nbaris          : {len(hasil):,}")
    print(f"puncak tergenang: {puncak_n:,} dari {len(edge):,} "
          f"({100.0 * puncak_n / len(edge):.1f} persen)")

    print("\nmenulis ke database ...")
    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        repo.publikasikan(hasil, [w for w, *_ in ringkas], SUMBER)
        if not argumen.pertahankan_dummy:
            print(f"  {repo.kosongkan_sumber('dummy'):,} baris dummy dihapus")
    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        print(f"  total baris    : {repo.hitung():,}")
        print(f"  sumber di tabel: {repo.sumber_yang_ada()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
