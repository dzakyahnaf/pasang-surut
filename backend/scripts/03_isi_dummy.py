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
from app.domain import pasut

SUMBER = "dummy"
JUMLAH_JAM = 72

# ── Pasut ─────────────────────────────────────────────────────────────────
# Sejak 28 Agustus 2026 pasut yang dipakai BUKAN lagi sinusoid contoh,
# melainkan rekonstruksi harmonik sungguhan dari app/domain/pasut.py, dengan
# acuan fase WIB yang sudah dikalibrasi terhadap data terukur stasiun IOC.
#
# Jadi status berkas ini berubah: PEMICUNYA sudah nyata, yang masih karangan
# hanya cara pemicu itu diterjemahkan menjadi kedalaman genangan per ruas.
tinggi_pasut_m = pasut.tinggi_pasut_m

# ── Parameter kedalaman contoh ────────────────────────────────────────────
# Berapa persen ruas yang diharapkan tergenang pada jam pasut tertinggi di
# dalam jendela. Ambangnya DIHITUNG dari angka ini, bukan ditulis tetap.
#
# KENAPA MENYESUAIKAN SENDIRI. Versi sebelumnya memakai ambang tetap 112 cm
# yang ditala untuk sinusoid contoh beramplitudo 0,5 m. Begitu pasut diganti
# rekonstruksi harmonik, tinggi puncaknya berubah mengikuti siklus purnama
# dan perbani — jendela 72 jam saat perbani hanya mencapai sekitar 0,23 m,
# sehingga ambang tetap itu membuat seluruh kota kering dan peta kehilangan
# isinya. Dengan ambang yang diturunkan dari puncak pasut di jendela yang
# sedang diisi, skrip ini tidak perlu ditala ulang setiap kali dijalankan.
TARGET_TERGENANG_SAAT_PUNCAK = 0.12

BIAS_CM = 4.0           # geser sedikit supaya pantai tetap tergenang saat puncak

# Kedalaman yang ingin dicapai ruas paling rentan pada jam pasut tertinggi.
# Pengalinya diturunkan dari angka ini, dengan alasan yang sama seperti
# ambang: tinggi puncak pasut berubah mengikuti purnama dan perbani, jadi
# pengali tetap akan membuat kelas terdalam kadang muncul kadang tidak.
# DESIGN.md Bagian 3.4 mewajibkan dua kelas terdalam ditumpuk pola titik
# halftone, dan itu hanya bisa diuji kalau kelasnya benar-benar terisi.
TARGET_KEDALAMAN_MAKS_CM = 65.0
KEDALAMAN_MAKS_CM = 80.0
SEBARAN_JITTER = 0.12   # keragaman antar ruas, lihat kerentanan()


def ambang_maks_cm(puncak_muka_air_cm: float, kerentanan_ruas) -> float:
    """Ambang ruas terjauh dari pantai, diturunkan dari puncak pasut.

    Ruas tergenang bila  muka_air + BIAS > AMBANG_MAKS * (1 - kerentanan).
    Supaya tepat sebagian ruas yang tergenang saat puncak, ambangnya dipilih
    sehingga persamaan itu terpenuhi persis pada persentil kerentanan yang
    sesuai dengan TARGET_TERGENANG_SAAT_PUNCAK.
    """
    k_ambang = float(np.percentile(
        kerentanan_ruas, 100.0 * (1.0 - TARGET_TERGENANG_SAAT_PUNCAK)
    ))
    sisa = max(1.0 - k_ambang, 1e-3)
    return (puncak_muka_air_cm + BIAS_CM) / sisa


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


def faktor_kedalaman(puncak_muka_air_cm: float, kerentanan_ruas,
                     ambang_maks: float) -> float:
    """Pengali yang membuat ruas paling rentan mencapai TARGET saat puncak."""
    k_maks = float(np.max(kerentanan_ruas))
    lebih_maks = puncak_muka_air_cm - ambang_maks * (1.0 - k_maks) + BIAS_CM
    if lebih_maks <= 0:
        return 1.0
    return TARGET_KEDALAMAN_MAKS_CM / lebih_maks


def hitung_kedalaman(
    muka_air_cm: float, kerentanan_ruas: np.ndarray, ambang_maks: float,
    faktor: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Kedalaman contoh dalam cm dan probabilitas contoh, untuk satu jam.

    Modelnya, kalau boleh disebut model:

        ambang   = ambang_maks * (1 - kerentanan)
        kedalaman = muka_air - ambang + bias

    Ruas di pantai punya ambang mendekati nol, jadi ia mengikuti muka air
    hampir langsung. Ruas jauh di darat punya ambang tinggi, jadi ia tetap
    kering kecuali muka air naik sangat tinggi.
    """
    ambang_cm = ambang_maks * (1.0 - kerentanan_ruas)
    lebih_cm = muka_air_cm - ambang_cm + BIAS_CM

    kedalaman = np.clip(lebih_cm * faktor, 0.0, KEDALAMAN_MAKS_CM)

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

    # Puncak pasut di dalam jendela dihitung LEBIH DULU, karena ambang
    # kedalaman diturunkan darinya. Lihat ambang_maks_cm().
    jam_jendela = np.array([
        pasut.jam_sejak_epoch(mulai + timedelta(hours=i))
        for i in range(argumen.jam)
    ])
    muka_air_jendela_cm = np.asarray(tinggi_pasut_m(jam_jendela)) * 100.0
    puncak_cm = float(muka_air_jendela_cm.max())
    ambang = ambang_maks_cm(puncak_cm, kerentanan_ruas)
    faktor = faktor_kedalaman(puncak_cm, kerentanan_ruas, ambang)

    print(f"ruas          : {len(edge_id):,}")
    print(f"jam diisi     : {argumen.jam}")
    print(f"mulai (UTC)   : {mulai.isoformat()}")
    print(f"mulai (WIB)   : {mulai.astimezone(config.ZONA_WAKTU_LOKAL).isoformat()}")
    print(f"sumber        : {SUMBER}")
    print(f"pemicu pasut  : {pasut.SUMBER}, acuan fase WIB +{pasut.OFFSET_FASE_JAM:.0f} jam")
    print(f"puncak pasut  : {puncak_cm:+.1f} cm di dalam jendela")
    print(f"ambang maks   : {ambang:.1f} cm (dihitung, bukan ditulis tetap)")
    print(f"pengali dalam : {faktor:.2f} (dihitung)")
    print()

    with db.koneksi() as kon:
        db.RepositoriGenangan(kon).kosongkan_sumber(SUMBER)

    total_baris = 0
    total_tergenang = 0
    ringkasan_jam = []

    for indeks_jam in range(argumen.jam):
        waktu = mulai + timedelta(hours=indeks_jam)
        pasut_m = float(tinggi_pasut_m(pasut.jam_sejak_epoch(waktu)))
        muka_air_cm = pasut_m * 100.0

        kedalaman, probabilitas = hitung_kedalaman(
            muka_air_cm, kerentanan_ruas, ambang, faktor)

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
    for waktu, tinggi_m, jumlah, maks in ringkasan_jam[:12]:
        lokal = waktu.astimezone(config.ZONA_WAKTU_LOKAL)
        print(f"  {lokal:%a %d %H:%M}   {tinggi_m:+6.2f}   {jumlah:>10,}   {maks:>14.1f}")

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
