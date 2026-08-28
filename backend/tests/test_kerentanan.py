"""Uji indeks kerentanan rob.

Indeks ini tidak punya kebenaran yang bisa diuji — tidak ada pengamatan
genangan per ruas. Yang diuji di sini karena itu sifat mekanisnya: arah
pengaruh tiap komponen, penanganan data yang hilang, dan bahwa elevasi
relatif benar-benar meniadakan kemiringan wilayah.

Uji arah pengaruh bukan formalitas. Membalik tanda satu komponen adalah
kesalahan yang paling mudah lolos dari pembacaan mata, dan akibatnya indeks
akan menyatakan bukit lebih rentan daripada pesisir.
"""

from __future__ import annotations

import numpy as np
import pytest

from app.domain import kerentanan


def test_elevasi_makin_rendah_makin_rentan():
    elev = np.array([-2.0, 0.0, 2.0, 5.0, 20.0])
    tetap = np.zeros(5)
    skor, _ = kerentanan.indeks(elev, tetap, tetap)
    assert np.all(np.diff(skor) <= 1e-9), "indeks harus turun saat elevasi naik"


def test_jarak_pantai_makin_dekat_makin_rentan():
    jarak = np.array([50.0, 500.0, 2000.0, 5000.0, 9000.0])
    tetap = np.zeros(5)
    skor, _ = kerentanan.indeks(tetap, jarak, tetap)
    assert np.all(np.diff(skor) <= 1e-9)


def test_subsidensi_makin_cepat_makin_rentan():
    subs = np.array([0.5, 2.0, 3.6, 4.6, 5.8])
    tetap = np.zeros(5)
    skor, _ = kerentanan.indeks(tetap, tetap, subs)
    assert np.all(np.diff(skor) >= -1e-9), "indeks harus naik saat subsidensi naik"


def test_indeks_selalu_di_antara_nol_dan_satu():
    acak = np.random.default_rng(3)
    skor, _ = kerentanan.indeks(
        acak.normal(0, 5, 500), acak.random(500) * 9000,
        acak.random(500) * 6)
    assert np.nanmin(skor) >= 0.0 - 1e-9
    assert np.nanmax(skor) <= 1.0 + 1e-9


def test_komponen_hilang_tidak_menghapus_ruas():
    """Ruas tanpa data subsidensi tetap dapat indeks dari dua komponen sisanya.

    Mengisi NaN dengan nol akan menyatakan "tidak ada subsidensi", padahal
    yang benar "tidak tahu". Bedanya besar untuk 990 ruas yang kecamatannya
    tidak dilaporkan sumber.
    """
    elev = np.array([0.0, 0.0])
    jarak = np.array([100.0, 100.0])
    subs = np.array([np.nan, np.nan])
    skor, _ = kerentanan.indeks(elev, jarak, subs)
    assert np.all(np.isfinite(skor))


def test_ruas_tanpa_data_sama_sekali_menghasilkan_nan():
    nan3 = np.array([np.nan, np.nan])
    skor, _ = kerentanan.indeks(nan3, nan3, nan3)
    assert np.all(np.isnan(skor))


def test_bobot_berjumlah_satu():
    assert sum(kerentanan.BOBOT.values()) == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════════════════
# ELEVASI RELATIF
# ══════════════════════════════════════════════════════════════════════════
def test_elevasi_relatif_meniadakan_kemiringan_wilayah():
    """Lereng seragam harus menghasilkan elevasi relatif mendekati nol.

    Inilah alasan elevasi relatif dipakai: galat vertikal DEMNAS sebagian
    besar berkorelasi spasial, dan pengurangan terhadap tetangga
    meniadakannya. Kalau uji ini gagal, manfaat itu hilang.
    """
    x = np.arange(0.0, 5000.0, 100.0)
    y = np.zeros_like(x)
    elev = 0.01 * x                      # naik 1 m tiap 100 m
    rel = kerentanan.elevasi_relatif(elev, x, y, radius_m=500.0)
    tengah = rel[5:-5]                   # abaikan tepi yang tetangganya timpang
    assert np.nanmax(np.abs(tengah)) < 8.0
    assert np.nanstd(tengah) < np.std(elev)


def test_elevasi_relatif_menonjolkan_cekungan_setempat():
    """Satu titik yang jauh lebih rendah dari tetangganya harus bernilai negatif."""
    x = np.arange(0.0, 3000.0, 100.0)
    y = np.zeros_like(x)
    elev = np.full_like(x, 5.0)
    elev[15] = 1.0
    rel = kerentanan.elevasi_relatif(elev, x, y, radius_m=500.0)
    assert rel[15] < -3.0
    assert rel[15] == np.nanmin(rel)


def test_elevasi_relatif_meneruskan_nan():
    x = np.array([0.0, 100.0, 200.0])
    y = np.zeros(3)
    elev = np.array([1.0, np.nan, 3.0])
    rel = kerentanan.elevasi_relatif(elev, x, y, radius_m=500.0)
    assert np.isnan(rel[1])
    assert np.all(np.isfinite(rel[[0, 2]]))
