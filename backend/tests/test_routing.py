"""Uji mesin perutean sadar genangan.

Uji ini memakai graf buatan kecil, bukan database. Alasannya dua: uji harus
bisa jalan di laptop anggota tim yang belum menyiapkan Supabase, dan graf
buatan membuat jawaban yang benar bisa dihitung dengan tangan.

Bentuk graf yang dipakai hampir di seluruh berkas ini:

        (jalur utara — pendek, tetapi bisa tergenang)
    A ────────────── B ────────────── C
     \\                              /
      \\____________ D _____________/
        (jalur selatan — lebih panjang, selalu kering)

Saat kering, jalur utara menang karena lebih pendek. Saat utara tergenang
melewati ambang, jalur selatan harus menang. Itulah seluruh isi produk ini
dalam satu gambar.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.domain import routing


# ── Bahan uji ──────────────────────────────────────────────────────────────
WAKTU_AWAL = datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc)

# Ambang moda ditiru dari isi tabel ambang_moda untuk motor.
AMBANG_MOTOR = {
    "lambat_cm": 10.0,
    "berisiko_cm": 20.0,
    "tidak_bisa_lewat_cm": 30.0,
    "konsumsi_l_per_km": 0.020,
    "faktor_emisi_kg_per_l": 2.31,
}


def _ruas(edge_id, u, v, panjang_m, koordinat, satu_arah=False, kecepatan=36.0):
    return {
        "edge_id": edge_id, "osm_u": u, "osm_v": v, "nama": f"Jalan {edge_id}",
        "jenis": "residential", "panjang_m": panjang_m,
        "kecepatan_kmh": kecepatan, "satu_arah": satu_arah,
        "koordinat": koordinat,
    }


@pytest.fixture
def graf_uji():
    """Graf empat simpul dengan dua jalur alternatif dari A ke C.

    Koordinat dipilih di sekitar AOI Semarang supaya perhitungan jarak ke
    simpul terdekat berada pada lintang yang wajar.
    """
    A, B, C, D = 1, 2, 3, 4
    ruas = [
        # Jalur utara: A-B-C, total 2.000 m
        _ruas(101, A, B, 1000.0, [[110.40, -6.95], [110.41, -6.95]]),
        _ruas(102, B, C, 1000.0, [[110.41, -6.95], [110.42, -6.95]]),
        # Jalur selatan: A-D-C, total 3.000 m
        _ruas(201, A, D, 1500.0, [[110.40, -6.95], [110.41, -6.97]]),
        _ruas(202, D, C, 1500.0, [[110.41, -6.97], [110.42, -6.95]]),
    ]
    return routing.GrafJalan(ruas), A, B, C, D


def _kedalaman(jam_ke_kedalaman: dict[int, dict[int, float]]) -> dict:
    """Susun peta kedalaman: {jam_offset: {edge_id: kedalaman_cm}}."""
    peta = {}
    for offset, per_edge in jam_ke_kedalaman.items():
        waktu = WAKTU_AWAL + timedelta(hours=offset)
        peta[waktu] = {e: (k, 0.9) for e, k in per_edge.items()}
    return peta


# ══════════════════════════════════════════════════════════════════════════
# 1. Rute ke diri sendiri berjarak nol
# ══════════════════════════════════════════════════════════════════════════
def test_rute_ke_diri_sendiri_berjarak_nol(graf_uji):
    graf, A, _, _, _ = graf_uji

    hasil = routing.cari_rute(
        graf, A, A, WAKTU_AWAL, AMBANG_MOTOR, peta_kedalaman={},
    )

    assert hasil.ditemukan
    assert hasil.jarak_m == 0.0
    assert hasil.detik == 0.0
    assert hasil.edge_ids == []
    # Berangkat dan tiba pada detik yang sama.
    assert hasil.waktu_tiba == WAKTU_AWAL


# ══════════════════════════════════════════════════════════════════════════
# 2. Ruas tidak bisa dilewati benar-benar dihindari
# ══════════════════════════════════════════════════════════════════════════
def test_ruas_tak_terlewati_benar_benar_dihindari(graf_uji):
    graf, A, _, C, _ = graf_uji

    # Saat kering, jalur utara yang lebih pendek harus menang.
    kering = routing.cari_rute(
        graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, peta_kedalaman={},
    )
    assert kering.ditemukan
    assert kering.edge_ids == [101, 102]
    assert kering.jarak_m == pytest.approx(2000.0)

    # Sekarang ruas 102 tergenang 40 cm. Ambang tidak bisa lewat untuk motor
    # adalah 30 cm, jadi ruas itu harus dibuang dari graf.
    tergenang = _kedalaman({0: {102: 40.0}})
    hasil = routing.cari_rute(
        graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, tergenang,
    )

    assert hasil.ditemukan
    assert 102 not in hasil.edge_ids, "ruas di atas ambang masih dilewati"
    assert hasil.edge_ids == [201, 202]
    assert hasil.jarak_m == pytest.approx(3000.0)

    # Rute pembanding TIDAK boleh menghindar — itu memang gunanya.
    pembanding = routing.cari_rute(
        graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, tergenang, sadar_rob=False,
    )
    assert pembanding.edge_ids == [101, 102]


def test_seluruh_jalur_tergenang_dilaporkan_bukan_ditebak(graf_uji):
    """Kalau tidak ada jalur yang bisa dilewati, jawabannya bukan rute asal-asalan."""
    graf, A, _, C, _ = graf_uji

    buntu = _kedalaman({0: {102: 40.0, 202: 40.0}})
    hasil = routing.cari_rute(graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, buntu)

    assert not hasil.ditemukan
    assert hasil.alasan == "seluruh_jalur_tergenang"
    assert hasil.edge_ids == []


# ══════════════════════════════════════════════════════════════════════════
# 3. Rute berubah saat waktu diubah
# ══════════════════════════════════════════════════════════════════════════
def test_rute_berubah_saat_waktu_diubah(graf_uji):
    """Ini kriteria terima sesi ini, diuji tanpa peramban.

    Ruas 102 hanya tergenang pada jam ke-3. Berangkat jam 0 harus lewat
    utara, berangkat jam 3 harus memutar lewat selatan.
    """
    graf, A, _, C, _ = graf_uji
    peta = _kedalaman({3: {102: 40.0}})

    jam_kering = routing.cari_rute(graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, peta)
    jam_rob = routing.cari_rute(
        graf, A, C, WAKTU_AWAL + timedelta(hours=3), AMBANG_MOTOR, peta,
    )

    assert jam_kering.edge_ids == [101, 102]
    assert jam_rob.edge_ids == [201, 202]
    assert jam_kering.edge_ids != jam_rob.edge_ids


def test_kondisi_berangkat_tetap_meski_perjalanan_melewati_jam():
    graf = routing.GrafJalan([
        _ruas(301, 1, 2, 9000.0, [[110.40,-6.95],[110.41,-6.95]], kecepatan=9.0),
        _ruas(302, 2, 3, 1000.0, [[110.41,-6.95],[110.42,-6.95]]),
    ])
    peta = _kedalaman({0: {}, 1: {302: 40.0}})
    awal = routing.cari_rute(graf, 1, 3, WAKTU_AWAL, AMBANG_MOTOR, peta)
    assert awal.detik == pytest.approx(3700)
    assert awal.ruas_tergenang == 0
    assert awal.kedalaman_per_ruas_cm == [0, 0]
    sesudah = routing.cari_rute(graf, 1, 3, WAKTU_AWAL+timedelta(hours=1), AMBANG_MOTOR, peta)
    assert not sesudah.ditemukan


def test_kasus_non_fifo_dibandingkan_dengan_enumerasi_model_biaya_tetap():
    # Kasus audit: solver dinamis lama melewatkan jalur 3661 detik.
    # Model yang disetujui berubah: biaya tetap selama satu pencarian.
    # Hitung semua jalur sederhana pada graf ini sebagai pembanding independen.
    edges = [(1,0,1,3599),(2,0,2,1800),(3,2,1,1801),(4,1,3,60)]
    graf = routing.GrafJalan([
        _ruas(e,u,v,float(d),[[110.4+u*.001,-6.95],[110.4+v*.001,-6.95]],
              satu_arah=True,kecepatan=3.6) for e,u,v,d in edges
    ])
    peta = _kedalaman({0:{4:29.0},1:{}})
    for berangkat, biaya4 in [(WAKTU_AWAL,447),
            (WAKTU_AWAL+timedelta(seconds=3599),447),
            (WAKTU_AWAL+timedelta(hours=1),60)]:
        semua_jalur = [3599+biaya4,1800+1801+biaya4]
        hasil = routing.cari_rute(graf,0,3,berangkat,AMBANG_MOTOR,peta)
        assert hasil.detik == pytest.approx(min(semua_jalur))
        assert hasil.edge_ids == [1,4]
        assert hasil.kedalaman_maks_cm == (29 if biaya4 == 447 else 0)


def test_penalti_naik_monoton_lalu_tak_terhingga():
    a = AMBANG_MOTOR
    assert routing.penalti_genangan(0.0, a) == 1.0
    assert routing.penalti_genangan(5.0, a) == 1.0        # di bawah ambang lambat
    p15 = routing.penalti_genangan(15.0, a)
    p25 = routing.penalti_genangan(25.0, a)
    assert 1.0 < p15 < p25
    assert routing.penalti_genangan(30.0, a) == float("inf")
    assert routing.penalti_genangan(99.0, a) == float("inf")


AMBANG_MOBIL = {
    "lambat_cm": 15.0, "berisiko_cm": 30.0, "tidak_bisa_lewat_cm": 50.0,
    "konsumsi_l_per_km": 0.090, "faktor_emisi_kg_per_l": 2.31,
}


def test_ambang_moda_menentukan_ruas_masih_bisa_dilewati_atau_tidak():
    """Genangan 40 cm: motor terhenti sama sekali, mobil masih bisa lewat.

    Sengaja dipakai graf tanpa jalur alternatif, supaya yang diuji murni
    soal AMBANG dan bukan soal mana yang lebih cepat. Kalau ada jalur
    memutar, hasilnya bisa berubah karena panjang jalan memutar, bukan
    karena ambang moda.

    Ambang motor untuk tidak bisa lewat adalah 30 cm, ambang mobil 50 cm.
    Pada 40 cm ruas ini harus hilang dari graf motor, dan tetap ada di graf
    mobil meski dengan penalti besar.
    """
    A, B, C = 1, 2, 3
    graf = routing.GrafJalan([
        _ruas(101, A, B, 1000.0, [[110.40, -6.95], [110.41, -6.95]]),
        _ruas(102, B, C, 1000.0, [[110.41, -6.95], [110.42, -6.95]]),
    ])
    peta = _kedalaman({0: {102: 40.0}})

    motor = routing.cari_rute(graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, peta)
    mobil = routing.cari_rute(graf, A, C, WAKTU_AWAL, AMBANG_MOBIL, peta)

    assert not motor.ditemukan, "motor seharusnya terhenti pada 40 cm"
    assert motor.alasan == "seluruh_jalur_tergenang"

    assert mobil.ditemukan, "mobil seharusnya masih bisa lewat pada 40 cm"
    assert mobil.edge_ids == [101, 102]
    assert mobil.ruas_tergenang == 1


def test_penalti_besar_bisa_membuat_memutar_lebih_murah(graf_uji):
    """Ruas yang masih bisa dilewati pun bisa kalah oleh jalur memutar.

    Untuk mobil, genangan 40 cm memberi penalti 5,25 kali. Jalur utara yang
    2.000 m berubah menjadi setara 625 detik, sementara jalur selatan yang
    3.000 m dan kering hanya 300 detik. Mesin harus memilih memutar meski
    ruasnya sebenarnya masih bisa dilewati.

    Ini perilaku yang benar dan perlu dikunci: menghindari genangan bukan
    hanya soal bisa atau tidak bisa lewat, tetapi juga soal ongkos waktu.
    """
    graf, A, _, C, _ = graf_uji
    peta = _kedalaman({0: {102: 40.0}})

    mobil = routing.cari_rute(graf, A, C, WAKTU_AWAL, AMBANG_MOBIL, peta)

    assert mobil.ditemukan
    assert mobil.edge_ids == [201, 202], "mobil seharusnya memutar karena lebih murah"
    assert mobil.ruas_tergenang == 0

    # Pembanding tetap menembus, dan itu yang membuat selisihnya bermakna.
    pembanding = routing.cari_rute(
        graf, A, C, WAKTU_AWAL, AMBANG_MOBIL, peta, sadar_rob=False,
    )
    assert pembanding.edge_ids == [101, 102]


# ══════════════════════════════════════════════════════════════════════════
# Graf dan penjepretan titik
# ══════════════════════════════════════════════════════════════════════════
def test_ruas_dua_arah_bisa_dilalui_bolak_balik(graf_uji):
    graf, A, _, C, _ = graf_uji
    maju = routing.cari_rute(graf, A, C, WAKTU_AWAL, AMBANG_MOTOR, {})
    mundur = routing.cari_rute(graf, C, A, WAKTU_AWAL, AMBANG_MOTOR, {})
    assert maju.ditemukan and mundur.ditemukan
    assert maju.jarak_m == pytest.approx(mundur.jarak_m)


def test_ruas_satu_arah_tidak_bisa_dilawan():
    A, B = 1, 2
    graf = routing.GrafJalan([
        _ruas(401, A, B, 500.0, [[110.40, -6.95], [110.41, -6.95]], satu_arah=True),
    ])
    assert routing.cari_rute(graf, A, B, WAKTU_AWAL, AMBANG_MOTOR, {}).ditemukan
    assert not routing.cari_rute(graf, B, A, WAKTU_AWAL, AMBANG_MOTOR, {}).ditemukan


def test_gelang_dibuang_dari_graf():
    """Ruas yang berawal dan berakhir di simpul sama tidak berguna untuk routing."""
    graf = routing.GrafJalan([
        _ruas(501, 1, 1, 100.0, [[110.40, -6.95], [110.40, -6.95]]),
        _ruas(502, 1, 2, 500.0, [[110.40, -6.95], [110.41, -6.95]]),
    ])
    assert graf.jumlah_simpul == 2
    assert 501 not in graf.sisi_per_id


def test_titik_jauh_dari_jalan_ditolak_bukan_dijepret_paksa(graf_uji):
    graf, *_ = graf_uji
    # Titik di tengah Laut Jawa, jauh di utara AOI.
    hasil = routing.dua_rute(
        graf, (110.41, -6.60), (110.42, -6.95),
        WAKTU_AWAL, AMBANG_MOTOR, {},
    )
    assert hasil.get("galat") == "asal_jauh_dari_jalan"
    assert hasil["jarak_m"] > routing.JARAK_MAKS_KE_JALAN_M


def test_dua_rute_mengembalikan_pembanding_dan_sadar_rob(graf_uji):
    graf, *_ = graf_uji
    peta = _kedalaman({0: {102: 40.0}})

    hasil = routing.dua_rute(
        graf, (110.40, -6.95), (110.42, -6.95),
        WAKTU_AWAL, AMBANG_MOTOR, peta,
    )

    abai = hasil["rute_abai_rob"]
    sadar = hasil["rute_sadar_rob"]
    assert abai.ditemukan and sadar.ditemukan
    # Pembanding menembus genangan, yang sadar rob memutar.
    assert abai.edge_ids == [101, 102]
    assert sadar.edge_ids == [201, 202]
    # Dan memutar memang lebih jauh. Selisih inilah dasar angka dampak M5.
    assert sadar.jarak_m > abai.jarak_m
