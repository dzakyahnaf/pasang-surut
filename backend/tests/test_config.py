"""Uji fondasi: AOI benar-benar termuat dan kotak pembatasnya masuk akal.

Uji ini adalah pengaman paling murah di repo. Kalau berkas AOI hilang,
tertukar, atau tanda lintangnya terbalik, uji ini gagal sebelum ada satu
ruas jalan pun yang dibangun di atasnya.
"""

from app import config


def test_aoi_termuat_dan_bbox_masuk_akal():
    # ── AOI termuat sebagai GeoJSON yang sah ────────────────────────────
    aoi = config.muat_aoi()
    assert aoi["type"] == "FeatureCollection"
    assert len(aoi["features"]) >= 1, "AOI tidak berisi satu fitur pun"

    geometri = config.geometri_aoi()
    assert geometri["type"] in ("Polygon", "MultiPolygon"), (
        f"AOI harus berupa poligon, bukan {geometri['type']}"
    )

    # ── Kotak pembatas ──────────────────────────────────────────────────
    bujur_min, lintang_min, bujur_maks, lintang_maks = config.bbox_aoi()

    # Tidak boleh terbalik atau berupa titik.
    assert bujur_min < bujur_maks, "bujur minimum tidak lebih kecil dari maksimum"
    assert lintang_min < lintang_maks, "lintang minimum tidak lebih kecil dari maksimum"

    # Semarang berada di sekitar 110,4 derajat bujur timur dan 6,96 derajat
    # lintang SELATAN. Lintang selatan bernilai negatif di EPSG:4326.
    # Lintang positif berarti tanda terbalik dan AOI melompat ke Laut Cina
    # Selatan — kesalahan yang sunyi dan mahal kalau lolos ke tahap graf.
    assert 110.0 < bujur_min and bujur_maks < 111.0, (
        f"bujur AOI {bujur_min}..{bujur_maks} berada di luar Jawa Tengah"
    )
    assert -7.5 < lintang_min and lintang_maks < -6.5, (
        f"lintang AOI {lintang_min}..{lintang_maks} berada di luar Semarang; "
        "periksa apakah tandanya terbalik"
    )

    # Ini AOI wilayah pilot, bukan satu kota penuh. Lebar 0,5 derajat sudah
    # sekitar 55 km, jauh lebih besar dari yang seharusnya, jadi ambang ini
    # menangkap AOI yang tanpa sengaja melebar.
    lebar = bujur_maks - bujur_min
    tinggi = lintang_maks - lintang_min
    assert 0 < lebar < 0.5, f"lebar AOI {lebar} derajat tidak wajar"
    assert 0 < tinggi < 0.5, f"tinggi AOI {tinggi} derajat tidak wajar"
