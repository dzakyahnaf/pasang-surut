"""Konfigurasi terpusat PASANG SURUT.

Semua path proyek, konstanta sistem koordinat, zona waktu, dan pemuatan AOI
berkumpul di berkas ini. Tujuannya satu: tidak ada modul lain yang boleh
menebak lokasi berkas atau menuliskan kode EPSG sendiri. Kalau AOI atau CRS
berubah, hanya berkas ini yang disunting.

Tidak ada logika bisnis di sini. Hanya konstanta dan pemuatan berkas.
"""

from __future__ import annotations

import json
import os
from datetime import timezone
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════════════════
# PATH PROYEK
# ══════════════════════════════════════════════════════════════════════════
# Berkas ini ada di <akar>/backend/app/config.py.
# parents[0] = backend/app, parents[1] = backend, parents[2] = akar repo.
# Path dihitung relatif terhadap berkas, bukan terhadap direktori kerja,
# supaya skrip tetap menemukan datanya dari mana pun ia dijalankan.
AKAR_REPO = Path(__file__).resolve().parents[2]

DIR_BACKEND = AKAR_REPO / "backend"
DIR_APP = DIR_BACKEND / "app"
DIR_SCRIPTS = DIR_BACKEND / "scripts"
DIR_TESTS = DIR_BACKEND / "tests"

DIR_DATA = AKAR_REPO / "data"
DIR_DATA_AOI = DIR_DATA / "aoi"
DIR_DATA_MENTAH = DIR_DATA / "raw"          # tidak masuk git, lihat .gitignore
DIR_DATA_OLAHAN = DIR_DATA / "processed"    # hasil kecil, boleh di-commit
DIR_DATA_REFERENSI = DIR_DATA / "referensi"

DIR_DB = AKAR_REPO / "db"
DIR_GEE = AKAR_REPO / "gee"
DIR_DOCS = AKAR_REPO / "docs"
DIR_NOTEBOOKS = AKAR_REPO / "notebooks"
DIR_FRONTEND = AKAR_REPO / "frontend"

BERKAS_AOI = DIR_DATA_AOI / "aoi_semarang_pilot.geojson"

# ══════════════════════════════════════════════════════════════════════════
# SISTEM KOORDINAT (CRS)
# ══════════════════════════════════════════════════════════════════════════
# Dua CRS dipakai di proyek ini dan keduanya punya tugas berbeda.
#
# EPSG:4326 (WGS 84) — CRS PENYIMPANAN.
#   Satuannya derajat bujur dan lintang. Ini bahasa yang dipahami GeoJSON,
#   PostGIS, dan MapLibre, jadi semua yang disimpan di database dan semua
#   yang dikirim ke frontend memakai ini.
#   Yang tidak boleh: menghitung jarak langsung di CRS ini. Satu derajat
#   bujur di Semarang panjangnya sekitar 110 km, satu derajat lintang juga
#   sekitar 110 km, tetapi keduanya tidak sama persis dan rasionya berubah
#   mengikuti lintang. Selisih koordinat derajat bukan meter.
EPSG_SIMPAN = 4326
CRS_SIMPAN = f"EPSG:{EPSG_SIMPAN}"

# EPSG:32749 (WGS 84 / UTM zone 49S) — CRS PERHITUNGAN.
#   Satuannya meter. Zona UTM 49 membentang pada bujur 108 sampai 114 derajat
#   timur, dan Semarang di 110,4 derajat berada tepat di dalamnya. Akhiran S
#   berarti belahan bumi selatan: sumbu utara diberi offset 10.000.000 meter
#   supaya koordinat Semarang tetap positif meski berada di lintang negatif.
#   Setiap kali panjang ruas jalan, luas genangan, atau buffer dalam meter
#   dihitung, geometri diproyeksikan dulu ke CRS ini. Hasilnya diproyeksikan
#   balik ke CRS_SIMPAN sebelum disimpan atau dikirim ke frontend.
EPSG_METRIK = 32749
CRS_METRIK = f"EPSG:{EPSG_METRIK}"

# ══════════════════════════════════════════════════════════════════════════
# ZONA WAKTU
# ══════════════════════════════════════════════════════════════════════════
# Aturan repo: database menyimpan UTC, antarmuka menampilkan WIB.
# Alasannya, waktu akuisisi Sentinel-1 dan hasil hitungan pasut keduanya
# lahir dalam UTC. Mengubahnya ke waktu lokal sedini mungkin akan membuat
# selisih jam menyelinap masuk ke data latih tanpa terlihat.
# Konversi ke WIB hanya terjadi di lapisan tampilan.
ZONA_WAKTU_SIMPAN = timezone.utc
ZONA_WAKTU_LOKAL = ZoneInfo("Asia/Jakarta")   # WIB, UTC+7, tanpa DST
LABEL_ZONA_WAKTU_LOKAL = "WIB"

# ══════════════════════════════════════════════════════════════════════════
# VARIABEL LINGKUNGAN
# ══════════════════════════════════════════════════════════════════════════
# .env tidak pernah masuk git. Bila belum ada, nilainya None dan modul yang
# membutuhkannya yang bertanggung jawab memberi galat yang jelas.
load_dotenv(AKAR_REPO / ".env")

DATABASE_URL: str | None = os.getenv("DATABASE_URL")

# ══════════════════════════════════════════════════════════════════════════
# AOI — WILAYAH PILOT
# ══════════════════════════════════════════════════════════════════════════
# AOI dibekukan bersama tim. Jangan ubah berkas GeoJSON-nya tanpa memberi
# tahu seluruh tim: batas ini menentukan graf jalan, sampel latih, dan
# tampilan peta sekaligus.


@lru_cache(maxsize=1)
def muat_aoi() -> dict:
    """Baca AOI apa adanya sebagai FeatureCollection GeoJSON.

    Hasilnya di-cache karena berkasnya statis sepanjang proses berjalan.
    Encoding ditulis eksplisit supaya perilakunya sama di Windows dan Linux.
    """
    if not BERKAS_AOI.exists():
        raise FileNotFoundError(
            f"Berkas AOI tidak ditemukan di {BERKAS_AOI}. "
            "Berkas ini wajib ada di repo; ambil kembali dari riwayat git."
        )
    with BERKAS_AOI.open(encoding="utf-8") as f:
        return json.load(f)


def fitur_aoi() -> dict:
    """Ambil Feature pertama AOI, satu-satunya poligon wilayah pilot."""
    fitur = muat_aoi()["features"]
    if not fitur:
        raise ValueError(f"AOI di {BERKAS_AOI} tidak berisi satu fitur pun.")
    return fitur[0]


def geometri_aoi() -> dict:
    """Ambil geometri AOI dalam bentuk dict GeoJSON.

    Dikembalikan sebagai dict, bukan objek Shapely, supaya modul yang hanya
    perlu meneruskannya ke peta atau ke OSMnx tidak wajib mengimpor Shapely.
    """
    return fitur_aoi()["geometry"]


def _koordinat_datar(koordinat) -> list[tuple[float, float]]:
    """Ratakan sarang koordinat GeoJSON jadi daftar pasangan (bujur, lintang).

    GeoJSON menyarangkan koordinat berbeda-beda kedalaman: Polygon punya
    daftar cincin, MultiPolygon punya daftar poligon berisi daftar cincin.
    Fungsi ini turun sampai menemukan pasangan angka, jadi bbox tetap benar
    apa pun tipe geometrinya.
    """
    if (
        len(koordinat) >= 2
        and isinstance(koordinat[0], (int, float))
        and isinstance(koordinat[1], (int, float))
    ):
        return [(float(koordinat[0]), float(koordinat[1]))]
    titik: list[tuple[float, float]] = []
    for bagian in koordinat:
        titik.extend(_koordinat_datar(bagian))
    return titik


def bbox_aoi() -> tuple[float, float, float, float]:
    """Kotak pembatas AOI sebagai (bujur_min, lintang_min, bujur_maks, lintang_maks).

    Urutannya mengikuti konvensi GeoJSON, yaitu bujur lebih dulu baru lintang.
    Satuannya derajat karena AOI disimpan dalam CRS_SIMPAN.
    """
    titik = _koordinat_datar(geometri_aoi()["coordinates"])
    bujur = [t[0] for t in titik]
    lintang = [t[1] for t in titik]
    return (min(bujur), min(lintang), max(bujur), max(lintang))
