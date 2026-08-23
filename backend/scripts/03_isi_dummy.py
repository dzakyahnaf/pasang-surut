"""Isi `prediksi_genangan` dengan DATA CONTOH untuk 72 jam ke depan.

    python -m scripts.03_isi_dummy               # dijalankan dari backend/

╔══════════════════════════════════════════════════════════════════════════╗
║  INI BUKAN PREDIKSI. INI ANGKA KARANGAN YANG SENGAJA DIBUAT DAN DIBERI   ║
║  TANDA sumber = 'dummy'.                                                 ║
║                                                                          ║
║  Tujuannya satu: supaya mesin routing, API, dan frontend bisa dibangun   ║
║  dan diuji hari ini, tanpa menunggu model asli selesai di M4. Saat model ║
║  siap, baris 'dummy' dihapus dan diganti 'model_v1'. Nol perubahan kode. ║
║                                                                          ║
║  Selama tabel masih berisi 'dummy', antarmuka WAJIB menampilkan lencana  ║
║  DATA CONTOH. Lencana itu hilang sendiri saat sumber berganti.           ║
╚══════════════════════════════════════════════════════════════════════════╝

Fungsi sintetisnya sengaja sederhana dan bisa dijelaskan dalam satu kalimat:
kedalaman naik saat pasut tinggi, dan ruas yang lebih dekat pantai lebih
cepat tergenang. Tidak ada klaim ketelitian apa pun di baliknya.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

from app import config, db

SUMBER = "dummy"
JUMLAH_JAM = 72

# ── Pasut contoh ──────────────────────────────────────────────────────────
# Satu sinusoid saja, periode 24,8 jam. Angka 24,8 dipilih karena itu
# panjang satu hari bulan, yaitu ritme dasar pasang surut harian.
#
# Pasut ASLI adalah jumlah dari banyak komponen harmonik (M2, S2, K1, O1,
# dan seterusnya) dengan amplitudo dan fase yang harus diambil dari konstanta
# terpublikasi. Itu pekerjaan modul domain/pasut.py, bukan di sini. Satu
# sinusoid ini hanya memberi bentuk naik-turun supaya Pita Pasut di frontend
# punya sesuatu untuk digambar.
PERIODE_PASUT_JAM = 24.8
AMPLITUDO_PASUT_M = 0.5

# Titik acuan fase. Dipatok pada waktu tetap, bukan waktu jalan, supaya
# skrip ini menghasilkan kurva yang sama setiap kali dijalankan.
EPOCH_PASUT = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)

# ── Parameter kedalaman contoh ────────────────────────────────────────────
# AMBANG_MAKS_CM sengaja jauh lebih besar daripada puncak muka air (50 cm).
# Kalau tidak, ruas paling jauh dari pantai pun ikut tergenang saat pasut
# puncak, seluruh peta jadi satu warna, dan tangga kedalaman tidak ada
# gunanya.
#
# Angka 112 bukan tebakan. Sebaran kerentanan ruas di AOI ini diukur lebih
# dulu, dan ternyata condong ke selatan — persentil ke-50 hanya 0,274 —
# karena jalan permukiman jauh lebih rapat di darat daripada di kawasan
# pelabuhan. Dengan ambang 112 cm, sekitar 12 persen ruas tergenang saat
# pasut puncak, dan keempat kelas tangga kedalaman muncul di peta.
AMBANG_MAKS_CM = 112.0  # ambang ruas paling jauh dari pantai
BIAS_CM = 4.0           # geser sedikit supaya pantai tetap tergenang saat puncak

# Pengali kedalaman. Tanpa ini kedalaman maksimum berhenti di sekitar 48 cm
# dan kelas terdalam (di atas 50 cm) tidak pernah muncul, sehingga pola
# titik halftone yang diwajibkan DESIGN.md Bagian 3.4 tidak bisa diuji.
FAKTOR_KEDALAMAN = 1.4
KEDALAMAN_MAKS_CM = 80.0
SEBARAN_JITTER = 0.12   # keragaman antar ruas, lihat kerentanan()


def tinggi_pasut_m(waktu: np.ndarray | datetime) -> np.ndarray | float:
    """Tinggi muka air contoh dalam meter, relatif terhadap rata-rata.

    Satu kosinus tunggal. Sekali lagi: ini bukan rekonstruksi harmonik.
    """
    if isinstance(waktu, datetime):
        jam = (waktu - EPOCH_PASUT).total_seconds() / 3600.0
    else:
        jam = waktu
    return AMPLITUDO_PASUT_M * np.sin(2 * np.pi * jam / PERIODE_PASUT_JAM)


def kerentanan(lintang: np.ndarray) -> np.ndarray:
    """Seberapa mudah satu ruas tergenang, skala 0 sampai 1.

    PENGGANTI SEMENTARA UNTUK ELEVASI. Elevasi sungguhan datang dari DEMNAS
    dan itu pekerjaan M4. Di sini dipakai satu pengganti kasar: jarak ke
    pantai, didekati lewat lintang.

    Dasarnya geografi Semarang — Laut Jawa ada di UTARA kota. Di EPSG:4326
    lintang belahan selatan bernilai negatif, jadi makin ke utara berarti
    lintang makin BESAR (makin mendekati nol). Tepi utara AOI adalah sisi
    yang paling dekat laut.

    Jadi: ruas dengan lintang mendekati tepi utara AOI diberi kerentanan
    mendekati 1, ruas di tepi selatan mendekati 0.

    Ini jelas menyederhanakan. Kenyataannya genangan rob mengikuti elevasi,
    laju penurunan tanah, dan jaringan drainase, bukan garis lintang. Karena
    itulah datanya ditandai 'dummy'.
    """
    _, lintang_min, _, lintang_maks = config.bbox_aoi()
    rentang = lintang_maks - lintang_min
    dasar = (lintang - lintang_min) / rentang     # 0 di selatan, 1 di utara
    return np.clip(dasar, 0.0, 1.0)


def jitter_per_ruas(edge_id: np.ndarray) -> np.ndarray:
    """Keragaman tetap per ruas, supaya peta tidak tampak seperti gradien rapi.

    Genangan sungguhan tidak rata mengikuti garis. Ada jalan yang tergenang
    sementara tetangganya kering, karena drainase dan ketinggian aspal
    berbeda. Nilai ini diturunkan dari edge_id lewat aritmetika sederhana,
    jadi hasilnya SELALU SAMA untuk ruas yang sama — bukan angka acak yang
    berubah tiap kali skrip dijalankan.
    """
    # Kalikan dengan bilangan prima besar lalu ambil sisa bagi. Cara murah
    # untuk menyebar nilai secara merata tanpa generator acak.
    sebar = (edge_id.astype(np.int64) * 2_654_435_761) % 1000 / 1000.0
    return (sebar - 0.5) * 2 * SEBARAN_JITTER


def hitung_kedalaman(
    muka_air_cm: float, kerentanan_ruas: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Kedalaman contoh dalam cm dan probabilitas contoh, untuk satu jam.

    Modelnya, kalau boleh disebut model:

        ambang   = AMBANG_MAKS * (1 - kerentanan)
        kedalaman = muka_air - ambang + bias

    Ruas di pantai punya ambang mendekati nol, jadi ia mengikuti muka air
    hampir langsung. Ruas jauh di darat punya ambang tinggi, jadi ia tetap
    kering kecuali muka air naik sangat tinggi.
    """
    ambang_cm = AMBANG_MAKS_CM * (1.0 - kerentanan_ruas)
    lebih_cm = muka_air_cm - ambang_cm + BIAS_CM

    kedalaman = np.clip(lebih_cm * FAKTOR_KEDALAMAN, 0.0, KEDALAMAN_MAKS_CM)

    # Probabilitas contoh: kurva logistik terhadap selisih yang sama.
    # Dibuat mulus supaya frontend punya nilai yang berubah halus saat
    # Pita Pasut digeser.
    probabilitas = 1.0 / (1.0 + np.exp(-lebih_cm / 8.0))
    probabilitas = np.clip(probabilitas, 0.0, 1.0)

    return kedalaman, probabilitas


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument(
        "--jam", type=int, default=JUMLAH_JAM,
        help=f"berapa jam ke depan diisi (bawaan {JUMLAH_JAM})",
    )
    argumen = pengurai.parse_args()

    with db.koneksi() as kon:
        ruas = db.RepositoriRuas(kon).id_dan_titik_tengah()

    if not ruas:
        print("Tabel ruas_jalan masih kosong. Jalankan dulu:")
        print("  python -m scripts.02_isi_ruas_jalan")
        return 1

    edge_id = np.array([r[0] for r in ruas], dtype=np.int64)
    lintang = np.array([r[2] for r in ruas], dtype=np.float64)

    # Kerentanan tetap sepanjang waktu, jadi dihitung sekali di luar loop jam.
    kerentanan_ruas = np.clip(kerentanan(lintang) + jitter_per_ruas(edge_id), 0.0, 1.0)

    # Waktu disimpan dalam UTC. Antarmuka yang mengubahnya ke WIB saat
    # menampilkan. Aturan repo: simpan UTC, tampilkan WIB.
    mulai = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    print(f"ruas          : {len(edge_id):,}")
    print(f"jam diisi     : {argumen.jam}")
    print(f"mulai (UTC)   : {mulai.isoformat()}")
    print(f"mulai (WIB)   : {mulai.astimezone(config.ZONA_WAKTU_LOKAL).isoformat()}")
    print(f"sumber        : {SUMBER}")
    print()

    with db.koneksi() as kon:
        db.RepositoriGenangan(kon).kosongkan_sumber(SUMBER)

    total_baris = 0
    total_tergenang = 0
    ringkasan_jam = []

    for indeks_jam in range(argumen.jam):
        waktu = mulai + timedelta(hours=indeks_jam)
        jam_sejak_epoch = (waktu - EPOCH_PASUT).total_seconds() / 3600.0
        pasut_m = float(tinggi_pasut_m(jam_sejak_epoch))
        muka_air_cm = pasut_m * 100.0

        kedalaman, probabilitas = hitung_kedalaman(muka_air_cm, kerentanan_ruas)

        # HANYA ruas yang tergenang yang disimpan.
        #
        # Ruas kering tidak perlu satu baris pun. Skema sudah dirancang untuk
        # ini: kolom kedalaman_cm bawaannya 0, dan view v_bobot_ruas memakai
        # LEFT JOIN dengan COALESCE, jadi ruas tanpa baris prediksi otomatis
        # terbaca sebagai kering.
        #
        # Bedanya besar. Menyimpan semua ruas untuk semua jam berarti
        # 19.394 x 72 = sekitar 1,4 juta baris. Menyimpan yang tergenang saja
        # memangkasnya jauh, dan itu penting karena Supabase paket gratis
        # hanya menyediakan 500 MB.
        basah = kedalaman > 0.0
        jumlah_basah = int(basah.sum())
        total_tergenang += jumlah_basah

        if jumlah_basah:
            baris = [
                (int(e), waktu, float(k), float(p), SUMBER)
                for e, k, p in zip(
                    edge_id[basah], kedalaman[basah], probabilitas[basah]
                )
            ]
            with db.koneksi() as kon:
                total_baris += db.RepositoriGenangan(kon).sisipkan_banyak(baris)

        ringkasan_jam.append((waktu, pasut_m, jumlah_basah, float(kedalaman.max())))

    print(f"baris tersimpan: {total_baris:,}")
    print(f"(tanpa penyaringan ruas kering akan menjadi {len(edge_id) * argumen.jam:,} baris)")
    print()
    print("contoh 12 jam pertama, waktu ditampilkan WIB:")
    print("  jam WIB        pasut(m)   ruas tergenang   kedalaman maks(cm)")
    for waktu, pasut, jumlah, maks in ringkasan_jam[:12]:
        lokal = waktu.astimezone(config.ZONA_WAKTU_LOKAL)
        print(f"  {lokal:%a %d %H:%M}   {pasut:+6.2f}   {jumlah:>10,}   {maks:>14.1f}")

    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        awal, akhir = repo.rentang_waktu()
        print()
        print(f"prediksi_genangan berisi: {repo.hitung():,} baris")
        print(f"sumber yang ada         : {repo.sumber_yang_ada()}")
        print(f"rentang waktu (UTC)     : {awal} sampai {akhir}")

    print()
    print("Ingat: seluruh angka di atas adalah data contoh, bukan prediksi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
