"""Uji fungsi murni di skrip penyiapan pemicu dan uji silang rob.

Skrip pipeline diberi nama berawalan angka supaya urutan jalannya terbaca dari
daftar berkas. Konsekuensinya nama modulnya bukan pengenal Python yang sah,
sehingga tidak bisa diimpor dengan `import`. importlib dipakai untuk itu.

Yang diuji di sini hanya fungsi yang tidak menyentuh jaringan atau database.
Bagian yang mengunduh diuji dengan menjalankan skripnya, bukan dengan pytest.
"""

from __future__ import annotations

import importlib.util
from datetime import date

import numpy as np
import pytest

from app import config


def _muat(nama: str):
    """Impor modul skrip yang namanya diawali angka."""
    berkas = config.DIR_SCRIPTS / f"{nama}.py"
    spesifikasi = importlib.util.spec_from_file_location(
        nama.replace(".", "_"), berkas
    )
    modul = importlib.util.module_from_spec(spesifikasi)
    spesifikasi.loader.exec_module(modul)
    return modul


pemicu = _muat("06_isi_pemicu")
uji_rob = _muat("07_uji_silang_rob")


# ══════════════════════════════════════════════════════════════════════════
# AKUMULASI HUJAN
# ══════════════════════════════════════════════════════════════════════════
def test_akumulasi_menjumlah_jendela_yang_benar():
    mm = np.arange(1.0, 11.0)          # 1, 2, ... 10

    h3 = pemicu.akumulasi(mm, 3)
    # Jam ke-5 (indeks 4) meliputi jam 3, 4, 5 yaitu 3 + 4 + 5.
    assert h3[4] == pytest.approx(12.0)
    # Jam terakhir meliputi 8 + 9 + 10.
    assert h3[-1] == pytest.approx(27.0)


def test_akumulasi_termasuk_jam_berjalan():
    """Jam berjalan ikut dijumlah. Jendela 1 jam sama dengan hujan itu sendiri."""
    mm = np.array([0.0, 5.0, 0.0, 2.5])
    assert pemicu.akumulasi(mm, 1) == pytest.approx(mm)


def test_akumulasi_awal_deret_tidak_meminjam_dari_masa_depan():
    """Baris paling awal hanya menjumlah data yang ada, tidak melingkar balik."""
    mm = np.array([4.0, 1.0, 1.0])
    h24 = pemicu.akumulasi(mm, 24)
    assert h24[0] == pytest.approx(4.0)
    assert h24[1] == pytest.approx(5.0)
    assert h24[2] == pytest.approx(6.0)


def test_akumulasi_72_jam_tidak_pernah_kurang_dari_24_jam():
    acak = np.random.default_rng(7).random(500) * 12.0
    assert np.all(pemicu.akumulasi(acak, 72) >= pemicu.akumulasi(acak, 24) - 1e-9)


# ══════════════════════════════════════════════════════════════════════════
# TITIK PENGAMBILAN
# ══════════════════════════════════════════════════════════════════════════
def test_titik_ambil_ada_di_dalam_aoi():
    lintang, bujur = pemicu.titik_ambil()
    lon0, lat0, lon1, lat1 = config.bbox_aoi()
    assert lat0 <= lintang <= lat1
    assert lon0 <= bujur <= lon1


# ══════════════════════════════════════════════════════════════════════════
# PENGURAIAN TANGGAL KEJADIAN
# ══════════════════════════════════════════════════════════════════════════
def test_tanggal_pasti_membuang_presisi_bulan_dan_tahun():
    hasil = uji_rob.tanggal_pasti([
        {"tanggal": "2016-07"},
        {"tanggal": "2022"},
        {"tanggal": None},
        {"tanggal": "2022-05-23"},
    ])
    assert [t for t, _ in hasil] == [date(2022, 5, 23)]


def test_tanggal_pasti_membentangkan_rentang():
    hasil = uji_rob.tanggal_pasti([{"tanggal": "2022-12-01/2022-12-04"}])
    assert [t for t, _ in hasil] == [
        date(2022, 12, 1), date(2022, 12, 2),
        date(2022, 12, 3), date(2022, 12, 4),
    ]


def test_tanggal_pasti_menolak_rentang_terbalik_dan_kepanjangan():
    """Rentang terbalik dan rentang berbulan-bulan bukan kejadian tunggal."""
    assert uji_rob.tanggal_pasti([{"tanggal": "2022-12-04/2022-12-01"}]) == []
    assert uji_rob.tanggal_pasti([{"tanggal": "2025-05-01/2025-07-31"}]) == []


# ══════════════════════════════════════════════════════════════════════════
# PASUT MAKSIMUM HARIAN
# ══════════════════════════════════════════════════════════════════════════
def test_pasut_maks_harian_satu_nilai_per_hari():
    hasil = uji_rob.pasut_maks_harian(date(2026, 1, 1), date(2026, 1, 10))
    assert len(hasil) == 10
    assert set(hasil) == {date(2026, 1, d) for d in range(1, 11)}


def test_pasut_maks_harian_lebih_tinggi_daripada_nilai_jam_bulat():
    """Cuplikan 15 menit tidak boleh melewatkan puncak yang ditangkap per jam.

    Ini pengaman terhadap kesalahan pembentukan ulang larik: kalau reshape-nya
    salah, nilai harian akan tercampur antar hari dan uji ini gagal.
    """
    from datetime import datetime, timezone

    from app.domain import pasut

    hari = date(2026, 3, 15)
    maks = uji_rob.pasut_maks_harian(hari, hari)[hari]
    per_jam = [
        float(pasut.tinggi_pasut_m(
            datetime(2026, 3, 15, j, tzinfo=timezone.utc)
        ))
        for j in range(24)
    ]
    assert maks >= max(per_jam) - 1e-9
