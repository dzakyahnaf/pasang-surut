"""Gambar diagram arsitektur untuk Bagian 8 proposal.

    python -m scripts.24_gambar_arsitektur

KENAPA DIAGRAM INI ADA.

Bagian 8 adalah satu-satunya bagian proposal yang tidak punya gambar, padahal
kriteria penilaian "Metodologi Pengembangan" berbobot 10 persen dan menyebut
"kesesuaian rancangan arsitektur dan spesifikasi teknologi dengan solusi yang
dibangun". Klaim arsitektur yang hanya ditulis lebih lemah daripada klaim yang
bisa dilihat.

SATU HAL YANG DIGAMBARKAN, BUKAN SEMUANYA.

Diagram yang menggambar seluruh modul akan berubah menjadi kotak-kotak tanpa
argumen. Yang digambar di sini hanya klaim arsitektur yang paling menentukan:
**dunia penyiapan dan dunia melayani dipisah, dan pemisahannya ditegakkan.**

Penegakan itu bukan konvensi. Citra Docker yang dijalankan di server tidak
memasang pustaka pipeline sama sekali, sehingga kode yang keliru memanggilnya
gagal saat start, bukan diam-diam saat juri sedang memakai aplikasinya. Itulah
yang dinyatakan garis tebal di tengah gambar.

TERBACA SAAT DICETAK HITAM PUTIH.

DESIGN.md Bagian 11 mensyaratkannya, dan proposal ini dinilai dari PDF yang
bisa saja dicetak abu-abu. Karena itu setiap kotak dibedakan oleh luminansi
dan posisi, tidak pernah oleh rona saja.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe                       # noqa: E402
from matplotlib import font_manager                       # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
import matplotlib.pyplot as plt                           # noqa: E402

AKAR = Path(__file__).resolve().parents[2]
KELUARAN = AKAR / "docs" / "arsitektur.png"

# Palet DESIGN.md. Luminansinya menurun berurutan sehingga urutannya tetap
# terbaca setelah dikonversi ke abu-abu.
LAMBUNG_1 = "#0B1F2A"
LAMBUNG_2 = "#12303E"
LAMBUNG_3 = "#1B4356"
DEK_1 = "#F2F5F6"
DEK_2 = "#E3EAEC"
DEK_3 = "#CBD7DB"
TINTA_1 = "#0B1F2A"
TINTA_2 = "#46626F"
TINTA_3 = "#7E97A3"
BALIK = "#E8F1F4"
RUTE = "#FFB020"
BAHAYA = "#C8322B"


def _renggang(teks: str) -> str:
    """Renggangkan jarak huruf label bergaya rambu.

    matplotlib tidak mengenal properti letter-spacing, jadi jaraknya dibuat
    dengan menyisipkan spasi tipis U+2009 di antara huruf. Spasi antar kata
    dipertahankan lebih lebar supaya batas katanya tetap terbaca.
    """
    return " ".join(teks).replace("   ", "  ")


def _huruf() -> str:
    """Barlow Semi Condensed bila terpasang, kalau tidak sans bawaan."""
    tersedia = {f.name for f in font_manager.fontManager.ttflist}
    for pilihan in ("Barlow Semi Condensed", "Barlow", "DejaVu Sans"):
        if pilihan in tersedia:
            return pilihan
    return "sans-serif"


def _kotak(ax, x, y, w, h, isi, *, latar, tepi, warna_teks, ukuran=9,
           tebal="normal", radius=0.02):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=1.1, edgecolor=tepi, facecolor=latar, zorder=2))
    ax.text(x + w / 2, y + h / 2, isi, ha="center", va="center",
            fontsize=ukuran, color=warna_teks, fontweight=tebal,
            linespacing=1.45, zorder=3)


def _panah(ax, dari, ke, *, warna=TINTA_2, lebar=1.2):
    ax.add_patch(FancyArrowPatch(
        dari, ke, arrowstyle="-|>", mutation_scale=11,
        linewidth=lebar, color=warna, zorder=1,
        shrinkA=2, shrinkB=2))


def gambar() -> int:
    huruf = _huruf()
    plt.rcParams["font.family"] = huruf

    fig, ax = plt.subplots(figsize=(11.0, 5.9), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(-4, 52)
    ax.axis("off")
    fig.patch.set_facecolor(DEK_1)

    # ── Kolom 1: sumber data luar ───────────────────────────────────────
    ax.text(2, 46.8, _renggang("Sumber data"), fontsize=8.5, color=TINTA_3,
            fontweight="bold")
    sumber = [
        ("OpenStreetMap\nvia OSMnx", 36.5),
        ("DEMNAS\nBadan Informasi Geospasial", 27.5),
        ("Open-Meteo\nreanalisis ERA5", 18.5),
        ("Sentinel-1 GRD\nvia Google Earth Engine", 9.5),
    ]
    for teks, y in sumber:
        _kotak(ax, 2, y, 21, 6.6, teks, latar=DEK_2, tepi=DEK_3,
               warna_teks=TINTA_1, ukuran=8.2)

    # ── Kolom 2: dunia penyiapan ────────────────────────────────────────
    ax.add_patch(FancyBboxPatch(
        (27, 8.5), 27, 38, boxstyle="round,pad=0,rounding_size=0.02",
        linewidth=1.2, edgecolor=LAMBUNG_3, facecolor=LAMBUNG_1, zorder=0))
    ax.text(28.5, 42.4, _renggang("Penyiapan data"), fontsize=9, color=RUTE,
            fontweight="bold")
    ax.text(28.5, 39.9, "Dijalankan di laptop, sekali saja", fontsize=8,
            color=TINTA_3)

    _kotak(ax, 29, 29.5, 23, 8.4,
           "Sebelas skrip penyiapan\n01 graf jalan  ·  05 fitur ruas\n"
           "06 pemicu  ·  09 model  ·  11 kerentanan",
           latar=LAMBUNG_2, tepi=LAMBUNG_3, warna_teks=BALIK, ukuran=8.2)

    _kotak(ax, 29, 18.5, 23, 7.6,
           "PostgreSQL + PostGIS\n19.394 ruas  ·  102.552 jam pemicu",
           latar=LAMBUNG_2, tepi=RUTE, warna_teks=BALIK, ukuran=8.4,
           tebal="bold")

    _kotak(ax, 29, 9.6, 23, 6.8,
           "Salinan 72 jam yang dibekukan\nDipakai kalau basis data mati",
           latar=LAMBUNG_1, tepi=LAMBUNG_3, warna_teks=TINTA_3, ukuran=8)

    for y in (36.5 + 3.3, 27.5 + 3.3, 18.5 + 3.3, 9.5 + 3.3):
        _panah(ax, (23.4, y), (28.6, 33.7), warna=TINTA_3, lebar=0.9)
    _panah(ax, (40.5, 29.3), (40.5, 26.3), warna=RUTE, lebar=1.4)
    _panah(ax, (40.5, 18.3), (40.5, 16.8), warna=TINTA_3, lebar=0.9)

    # ── Batas yang ditegakkan ───────────────────────────────────────────
    #
    # Penjelasan penegakannya sengaja TIDAK diletakkan di tengah gambar.
    # Versi pertama menaruhnya di sana dan kotaknya menutupi teks kolom
    # kiri dan kanan — cacat yang baru terlihat setelah gambarnya dibuka.
    # Sekarang garisnya saja yang di tengah, penjelasannya di pita bawah.
    ax.plot([61, 61], [10, 46.5], color=BAHAYA, linewidth=2.4, zorder=4)
    ax.text(61, 47.6, _renggang("Batas"), fontsize=8.4, color=BAHAYA,
            fontweight="bold", ha="center")

    # ── Kolom 3: dunia melayani ─────────────────────────────────────────
    ax.add_patch(FancyBboxPatch(
        (68, 8.5), 30, 38, boxstyle="round,pad=0,rounding_size=0.02",
        linewidth=1.2, edgecolor=LAMBUNG_3, facecolor=LAMBUNG_1, zorder=0))
    ax.text(69.5, 42.4, _renggang("Melayani pengguna"), fontsize=9, color=RUTE,
            fontweight="bold")
    ax.text(69.5, 39.9, "Dijalankan di server, tanpa panggilan keluar",
            fontsize=8, color=TINTA_3)

    _kotak(ax, 70, 29.5, 26, 8.4,
           "FastAPI, tujuh endpoint\nkesehatan · ruas · genangan · jam\n"
           "tujuan-cepat · validasi · rute",
           latar=LAMBUNG_2, tepi=LAMBUNG_3, warna_teks=BALIK, ukuran=8.2)

    _kotak(ax, 70, 18.5, 26, 7.6,
           "Dijkstra bergantung waktu\nBiaya ruas dihitung pada jam tiba",
           latar=LAMBUNG_2, tepi=RUTE, warna_teks=BALIK, ukuran=8.4,
           tebal="bold")

    _kotak(ax, 70, 9.6, 26, 6.8,
           "React + MapLibre GL JS\nGaya peta ditulis inline, tanpa ubin luar",
           latar=LAMBUNG_2, tepi=LAMBUNG_3, warna_teks=BALIK, ukuran=8.2)

    _panah(ax, (83, 29.3), (83, 26.3), warna=RUTE, lebar=1.4)
    _panah(ax, (83, 18.3), (83, 16.8), warna=TINTA_3, lebar=0.9)
    # Basis data dan potret menyeberang batas HANYA sebagai data, bukan kode.
    _panah(ax, (52.4, 22.3), (69.6, 33.7), warna=TINTA_3, lebar=1.0)
    _panah(ax, (52.4, 13.0), (69.6, 32.2), warna=TINTA_3, lebar=0.9)

    # ── Pita penjelasan di bawah, selebar gambar ────────────────────────
    ax.add_patch(FancyBboxPatch(
        (2, 0.4), 96, 4.2, boxstyle="round,pad=0,rounding_size=0.02",
        linewidth=1.1, edgecolor=BAHAYA, facecolor=DEK_1, zorder=2))
    ax.text(50, 3.4,
            "Yang melewati batas hanya data yang sudah selesai dihitung. "
            "Citra Docker di server tidak memasang satu pun pustaka penyiapan:",
            fontsize=8, color=TINTA_1, ha="center", va="center", zorder=3)
    ax.text(50, 1.5,
            "earthengine-api   ·   osmnx   ·   geopandas   ·   rasterio   ·   "
            "scikit-learn   ·   pandas",
            fontsize=8.2, color=BAHAYA, ha="center", va="center",
            fontweight="bold", zorder=3)
    ax.text(50, -1.6,
            "Kalau ada kode yang keliru memanggilnya, server gagal menyala. "
            "Kegagalannya terlihat saat itu juga, bukan saat juri sedang memakai aplikasinya.",
            fontsize=7.6, color=TINTA_2, ha="center", va="center",
            style="italic")

    fig.tight_layout(pad=0.4)
    fig.savefig(KELUARAN, facecolor=DEK_1, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)

    kb = KELUARAN.stat().st_size / 1024
    print(f"tersimpan : {KELUARAN.relative_to(AKAR)}")
    print(f"ukuran    : {kb:.0f} KB")
    print(f"huruf     : {huruf}")
    return 0


if __name__ == "__main__":
    sys.exit(gambar())
