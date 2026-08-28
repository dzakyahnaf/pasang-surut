"""Uji konversi probabilitas menjadi estimasi kedalaman.

Modul yang diuji di sini adalah titik terlemah metodologi menurut PLAN.md
bagian 10.3. Justru karena itu ia perlu uji: asumsinya boleh diperdebatkan,
tetapi perilakunya tidak boleh mengejutkan. Yang dijaga uji ini bukan
kebenaran angkanya — tidak ada data kedalaman untuk membuktikannya — melainkan
sifat-sifat yang sudah dijanjikan docstring-nya.
"""

from __future__ import annotations

import numpy as np
import pytest

from app.domain import genangan

AMBANG = 0.4
BAWAH, PUNCAK = 0.0, 0.45


def kedalaman(p, pasut):
    return genangan.kedalaman_cm(p, pasut, AMBANG, BAWAH, PUNCAK)


def test_di_bawah_ambang_selalu_nol():
    """Nol berarti tidak diprediksi tergenang, bukan tergenang paling dangkal."""
    hasil = kedalaman(np.array([0.0, 0.1, 0.39]), 0.45)
    assert np.all(hasil == 0.0)


def test_tepat_di_ambang_sudah_tergenang():
    assert kedalaman(np.array([AMBANG]), 0.0)[0] > 0.0


def test_tidak_pernah_keluar_rentang_rob():
    """Aturan repo nomor 4: rob 10 sampai 50 cm. Keluaran tidak boleh melewati."""
    acak = np.random.default_rng(1)
    p = acak.random(2000)
    for pasut in (-1.0, -0.3, 0.0, 0.2, 0.45, 2.0):
        h = kedalaman(p, pasut)
        bergenang = h[h > 0]
        if bergenang.size:
            assert bergenang.min() >= genangan.KEDALAMAN_MIN_CM - 1e-9
            assert bergenang.max() <= genangan.KEDALAMAN_MAKS_CM + 1e-9


def test_naik_monoton_terhadap_probabilitas():
    p = np.linspace(AMBANG, 1.0, 50)
    h = kedalaman(p, 0.2)
    assert np.all(np.diff(h) >= -1e-9)


def test_naik_monoton_terhadap_pasut():
    pasut = np.linspace(-0.5, 0.6, 40)
    h = np.array([kedalaman(np.array([0.8]), t)[0] for t in pasut])
    assert np.all(np.diff(h) >= -1e-9)


def test_pasut_di_luar_acuan_dipotong_bukan_diekstrapolasi():
    """Pasut jauh di atas puncak acuan tidak boleh melewati batas atas."""
    tinggi = kedalaman(np.array([1.0]), 5.0)[0]
    di_puncak = kedalaman(np.array([1.0]), PUNCAK)[0]
    assert tinggi == pytest.approx(di_puncak)
    assert tinggi == pytest.approx(genangan.KEDALAMAN_MAKS_CM)


def test_probabilitas_sama_pasut_berbeda_menghasilkan_kedalaman_berbeda():
    """Kalau tidak, bobot pasut tidak berpengaruh dan modulnya sia-sia."""
    surut = kedalaman(np.array([0.9]), BAWAH)[0]
    pasang = kedalaman(np.array([0.9]), PUNCAK)[0]
    assert pasang > surut


def test_pasut_sama_probabilitas_berbeda_menghasilkan_kedalaman_berbeda():
    ragu = kedalaman(np.array([AMBANG]), 0.2)[0]
    yakin = kedalaman(np.array([1.0]), 0.2)[0]
    assert yakin > ragu


def test_acuan_terbalik_tidak_membuat_galat_pembagian_nol():
    """Kalau acuan bawah dan puncak sama, sumbangan pasut jadi nol, bukan NaN."""
    h = genangan.kedalaman_cm(np.array([1.0]), 0.3, AMBANG, 0.2, 0.2)[0]
    assert np.isfinite(h)
    assert h == pytest.approx(
        genangan.KEDALAMAN_MIN_CM
        + (genangan.KEDALAMAN_MAKS_CM - genangan.KEDALAMAN_MIN_CM)
        * genangan.BOBOT_PROBABILITAS
    )
