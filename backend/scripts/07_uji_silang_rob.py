"""Uji silang: apakah tanggal rob yang terdokumentasi jatuh pada pasut tinggi?

    python -m scripts.07_uji_silang_rob          # dijalankan dari backend/

APA YANG DIUJI.

Rekonstruksi harmonik sudah dikalibrasi acuan waktunya lewat skrip 04, tetapi
kalibrasi itu memakai data terukur sepuluh hari terakhir. Uji ini berbeda dan
saling melengkapi: ia memakai bukti yang sama sekali terpisah, yaitu tanggal
kejadian rob yang dikumpulkan dari pemberitaan dan dokumen resmi sepanjang
2020 sampai 2026, lalu bertanya satu hal sederhana.

    Pada hari-hari itu, apakah pasut hasil rekonstruksi memang tinggi?

Kalau ya, rekonstruksi punya daya jelas terhadap kejadian nyata. Kalau tidak,
ada yang salah dan lebih baik ketahuan sekarang daripada di depan juri.

CARA MENGUKURNYA: PERSENTIL, BUKAN NILAI MUTLAK.

Untuk tiap tanggal kejadian diambil pasut maksimum hari itu, lalu dicari
letaknya di antara pasut maksimum SELURUH hari pada periode yang sama.
Persentil 90 berarti hari itu lebih tinggi daripada 90 persen hari lainnya.

Persentil dipakai supaya hasilnya tidak bergantung pada datum, dan supaya
pembandingnya adil: yang dibandingkan hari rob dengan hari biasa, bukan
dengan angka ambang yang kita tentukan sendiri.

YANG TIDAK DIKLAIM UJI INI.

Ini BUKAN pengukuran akurasi model genangan. Tidak ada model di sini, hanya
pasut. Rob juga tidak selalu disebabkan pasut tinggi semata — hujan, angin,
dan penurunan tanah ikut berperan, dan jebolnya tanggul bisa membuat rob
terjadi pada pasut sedang. Karena itu persentil yang tidak selalu ekstrem
adalah hasil yang wajar, bukan kegagalan.

Daftar kejadiannya sendiri berstatus 'perlu_verifikasi' untuk sebagian besar
entri, dan ketelitian tanggalnya beragam. Yang dipakai di sini hanya entri
yang tanggalnya pasti sampai hari.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone

import numpy as np

from app import config
from app.domain import pasut

BERKAS_KEJADIAN = config.DIR_DATA_REFERENSI / "kejadian_rob_semarang.json"
BERKAS_HASIL = config.DIR_DATA_REFERENSI / "uji_silang_rob.json"

# Persentil pembanding dihitung atas periode ini, bukan atas seluruh sejarah,
# supaya musim dan tahun kejadian terwakili seimbang.
PERIODE_AWAL = date(2020, 1, 1)
PERIODE_AKHIR = date(2026, 8, 27)


def hujan_harian() -> dict[date, float]:
    """Hujan 24 jam maksimum tiap hari, dibaca dari tabel pemicu.

    Dipakai untuk menjawab pertanyaan lanjutan: kejadian yang pasutnya justru
    rendah, apakah hari itu hujan deras? Kalau ya, itu bukan kelemahan
    rekonstruksi melainkan bukti bahwa rob berkepala dua dan satu variabel
    saja tidak cukup — persis alasan proyek ini memakai model, bukan ambang.
    """
    from app import db

    try:
        with db.koneksi() as kon:
            with kon.cursor() as kur:
                kur.execute(
                    """
                    SELECT (waktu AT TIME ZONE 'UTC')::date AS hari,
                           MAX(hujan_24j_mm)
                    FROM pemicu GROUP BY hari
                    """
                )
                return {h: float(m or 0.0) for h, m in kur.fetchall()}
    except Exception as e:
        print(f"  (tabel pemicu tidak terbaca: {type(e).__name__}, "
              "kolom hujan dilewati)")
        return {}


def tanggal_pasti(kejadian: list[dict]) -> list[tuple[date, dict]]:
    """Ambil hanya entri yang tanggalnya pasti sampai hari.

    Entri berformat 'YYYY-MM' atau 'YYYY' dilewati, begitu pula rentang
    'YYYY-MM-DD/YYYY-MM-DD' yang diperlakukan sebagai kejadian berhari-hari
    dan diambil SELURUH harinya.
    """
    hasil: list[tuple[date, dict]] = []
    for k in kejadian:
        t = k.get("tanggal")
        if not t:
            continue
        bagian = t.split("/")
        try:
            if len(bagian) == 2:
                a = date.fromisoformat(bagian[0])
                b = date.fromisoformat(bagian[1])
                if b < a or (b - a).days > 30:
                    continue
                hari = a
                while hari <= b:
                    hasil.append((hari, k))
                    hari += timedelta(days=1)
            else:
                hasil.append((date.fromisoformat(bagian[0]), k))
        except ValueError:
            continue        # presisi bulan atau tahun, tidak dipakai
    return hasil


def pasut_maks_harian(awal: date, akhir: date) -> dict[date, float]:
    """Pasut maksimum tiap hari pada rentang, dari rekonstruksi harmonik.

    Dicuplik tiap 15 menit, bukan tiap jam. Puncak pasut bisa jatuh di antara
    dua jam bulat, dan mencuplik per jam akan meleset sampai beberapa
    sentimeter secara sistematis pada semua hari sekaligus.
    """
    mulai = datetime(awal.year, awal.month, awal.day, tzinfo=timezone.utc)
    jumlah_hari = (akhir - awal).days + 1
    per_hari = 96                                  # 24 jam / 15 menit
    langkah = 0.25

    jam0 = (mulai - pasut.EPOCH_HARMONIK).total_seconds() / 3600.0
    jam = jam0 + np.arange(jumlah_hari * per_hari) * langkah
    tinggi = pasut.tinggi_pasut_harmonik(jam, offset_jam=pasut.OFFSET_FASE_JAM)

    maks = tinggi.reshape(jumlah_hari, per_hari).max(axis=1)
    return {awal + timedelta(days=i): float(maks[i]) for i in range(jumlah_hari)}


def main() -> int:
    kejadian = json.loads(BERKAS_KEJADIAN.read_text(encoding="utf-8"))["kejadian"]
    harian = pasut_maks_harian(PERIODE_AWAL, PERIODE_AKHIR)
    semua = np.array(sorted(harian.values()))

    print(f"periode pembanding : {PERIODE_AWAL} sampai {PERIODE_AKHIR} "
          f"({len(harian):,} hari)")
    print(f"pasut maksimum harian: {semua.min():+.3f} sampai {semua.max():+.3f} m")
    print(f"median               : {np.median(semua):+.3f} m\n")

    dipakai = [
        (t, k) for t, k in tanggal_pasti(kejadian)
        if PERIODE_AWAL <= t <= PERIODE_AKHIR
    ]
    print(f"kejadian bertanggal pasti di dalam periode: {len(dipakai)} hari")
    print(f"dari {len(kejadian)} entri di berkas kejadian\n")

    if not dipakai:
        print("Tidak ada tanggal yang bisa diuji.")
        return 1

    hujan = hujan_harian()
    baris = []
    for t, k in sorted(dipakai, key=lambda x: x[0]):
        nilai = harian[t]
        persentil = 100.0 * float((semua < nilai).mean())
        baris.append({
            "tanggal": t.isoformat(),
            "kejadian": k.get("tanggal"),
            "pasut_maks_m": round(nilai, 3),
            "persentil": round(persentil, 1),
            "hujan_24j_mm": (None if t not in hujan
                             else round(hujan[t], 1)),
            "verifikasi": k.get("verifikasi", "tidak_disebut"),
        })

    print(f"{'tanggal':<12} {'pasut maks':>11} {'persentil':>10} "
          f"{'hujan 24j':>10}   verifikasi")
    for b in baris:
        h = "-" if b["hujan_24j_mm"] is None else f"{b['hujan_24j_mm']:.1f} mm"
        print(f"{b['tanggal']:<12} {b['pasut_maks_m']:+10.3f} m "
              f"{b['persentil']:9.1f} {h:>10}   {b['verifikasi']}")

    p = np.array([b["persentil"] for b in baris])
    print()
    print("ringkasan persentil hari kejadian")
    print(f"  median            : {np.median(p):.1f}")
    print(f"  rata-rata         : {p.mean():.1f}")
    print(f"  di atas persentil 75 : {int((p >= 75).sum())} dari {len(p)} "
          f"({100.0 * (p >= 75).mean():.0f} persen)")
    print(f"  di atas persentil 90 : {int((p >= 90).sum())} dari {len(p)} "
          f"({100.0 * (p >= 90).mean():.0f} persen)")
    print()

    # UKURAN KEDUA: PER KEJADIAN, BUKAN PER HARI.
    #
    # Pemberitaan sering menulis rentang, misalnya "rob melanda 1 sampai 13
    # November". Menghitung tiap hari di rentang itu sebagai satu pengamatan
    # membuat satu kejadian panjang menenggelamkan kejadian lain, sekaligus
    # menghukum rekonstruksi atas hari-hari di tepi rentang yang belum tentu
    # tergenang. Yang adil untuk sebuah rentang adalah bertanya apakah DI
    # DALAMNYA ada hari berpasut tinggi.
    per_kejadian: dict[str, dict] = {}
    for b in baris:
        k = per_kejadian.setdefault(
            b["kejadian"], {"persentil": -1.0, "hujan_24j_mm": None, "hari": 0}
        )
        k["hari"] += 1
        if b["persentil"] > k["persentil"]:
            k["persentil"] = b["persentil"]
            k["tanggal_puncak"] = b["tanggal"]
            k["pasut_maks_m"] = b["pasut_maks_m"]
            k["verifikasi"] = b["verifikasi"]
        if b["hujan_24j_mm"] is not None:
            k["hujan_24j_mm"] = max(k["hujan_24j_mm"] or 0.0, b["hujan_24j_mm"])

    pk = np.array([v["persentil"] for v in per_kejadian.values()])
    print("ringkasan per KEJADIAN "
          f"({len(per_kejadian)} kejadian, persentil tertinggi di rentangnya)")
    print(f"  median               : {np.median(pk):.1f}")
    print(f"  di atas persentil 75 : {int((pk >= 75).sum())} dari {len(pk)} "
          f"({100.0 * (pk >= 75).mean():.0f} persen)")
    print(f"  di atas persentil 90 : {int((pk >= 90).sum())} dari {len(pk)} "
          f"({100.0 * (pk >= 90).mean():.0f} persen)")
    print()

    # Kejadian yang pasutnya rendah adalah yang paling menarik, karena di
    # situlah terlihat bahwa pasut saja tidak menjelaskan rob.
    rendah = {n: v for n, v in per_kejadian.items() if v["persentil"] < 60}
    if rendah:
        print("kejadian dengan pasut TIDAK tinggi (persentil di bawah 60):")
        for n, v in sorted(rendah.items()):
            h = ("tidak terbaca" if v["hujan_24j_mm"] is None
                 else f"{v['hujan_24j_mm']:.1f} mm")
            print(f"  {n:<24} persentil {v['persentil']:5.1f}   "
                  f"hujan 24 jam {h}")
        print("  Inilah alasan sistem ini memakai model, bukan ambang pasut.")
        print()

    # PUTUSAN DIAMBIL DARI UKURAN PER HARI, yang angkanya lebih rendah.
    # Ukuran per kejadian diperkenalkan setelah ukuran per hari dihitung, jadi
    # memakainya sebagai dasar putusan akan terlihat seperti memilih ukuran
    # yang hasilnya paling enak. Keduanya dilaporkan, yang menentukan yang
    # lebih konservatif.
    #
    # Kalau tanggal kejadian tidak berhubungan dengan pasut, persentilnya akan
    # tersebar merata dan medianya mendekati 50.
    if np.median(p) >= 75:
        putusan = "kuat"
        kalimat = ("Hari kejadian rob memang jatuh pada pasut yang tinggi. "
                   "Rekonstruksi harmonik punya daya jelas terhadap kejadian "
                   "nyata, terpisah dari kalibrasi skrip 04.")
    elif np.median(p) >= 60:
        putusan = "sedang"
        kalimat = ("Hari kejadian condong ke pasut tinggi, tetapi tidak "
                   "seluruhnya. Wajar: rob juga dipicu hujan, angin, dan "
                   "tanggul yang jebol.")
    else:
        putusan = "lemah"
        kalimat = ("Tanggal kejadian TIDAK condong ke pasut tinggi. Ini harus "
                   "ditelusuri sebelum rekonstruksi dipakai sebagai fitur "
                   "utama model.")
    kalimat = (f"{kalimat} Median persentil per hari {np.median(p):.1f}, "
               f"per kejadian {np.median(pk):.1f}, terhadap 50 bila tanggal "
               "kejadian tidak berhubungan sama sekali dengan pasut.")
    print(f"PUTUSAN: {putusan}. {kalimat}")

    BERKAS_HASIL.write_text(json.dumps({
        "_catatan": ("Uji silang rekonstruksi pasut terhadap tanggal kejadian "
                     "rob terdokumentasi. Dihasilkan oleh "
                     "backend/scripts/07_uji_silang_rob.py."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "periode_pembanding": [PERIODE_AWAL.isoformat(), PERIODE_AKHIR.isoformat()],
        "hari_pembanding": len(harian),
        "sumber_pasut": pasut.SUMBER,
        "offset_fase_jam": pasut.OFFSET_FASE_JAM,
        "cuplikan_menit": 15,
        "hari_kejadian_diuji": len(baris),
        "entri_di_berkas_kejadian": len(kejadian),
        "ukuran": "dua: per hari dan per kejadian",
        "kejadian_diuji": len(per_kejadian),
        "persentil_median_per_kejadian": round(float(np.median(pk)), 1),
        "per_kejadian_di_atas_p75": int((pk >= 75).sum()),
        "per_kejadian_di_atas_p90": int((pk >= 90).sum()),
        "persentil_median": round(float(np.median(p)), 1),
        "persentil_rata_rata": round(float(p.mean()), 1),
        "di_atas_p75": int((p >= 75).sum()),
        "di_atas_p90": int((p >= 90).sum()),
        "putusan": putusan,
        "kesimpulan": kalimat,
        "per_tanggal": baris,
        "_peringatan": [
            "Uji ini menilai PASUT, bukan model genangan. Tidak ada metrik "
            "model di sini dan angka apa pun dari berkas ini tidak boleh "
            "disajikan sebagai akurasi model.",
            "Sebagian besar entri kejadian berstatus perlu_verifikasi. "
            "Sumbernya pemberitaan, bukan pengukuran lapangan.",
            "Entri yang presisinya bulan atau tahun dibuang, jadi cakupan uji "
            "lebih sempit daripada daftar kejadian seutuhnya.",
            "Koreksi nodal 18,6 tahun belum diterapkan pada rekonstruksi.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
