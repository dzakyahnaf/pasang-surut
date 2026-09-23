"""Video pameran PASANG SURUT: motion design 60 detik, 1920x1080, 30 fps, tanpa suara.

    .venv\\Scripts\\python.exe docs/final/pameran/buat_video.py
    .venv\\Scripts\\python.exe docs/final/pameran/buat_video.py --cuplikan 3,11,22,36,48,56

Opsi `--cuplikan` hanya menyimpan PNG pada detik yang diminta, untuk
diperiksa sebelum encoding penuh.

DIGAMBAR DARI DATA, BUKAN DIANIMASIKAN TANGAN.

Peta, genangan, kurva pasut, dan kedua rute digambar langsung dari berkas
yang sama dengan yang dipakai aplikasi dan slide final:

    data/processed/potret_demo.json            19.394 ruas dan genangan per jam
    docs/final/presentasi/aset/skenario.json   dua rute Tawang-Terboyo, 08.00 dan 13.00
    frontend/src/data/konteks-peta.json        garis pantai, batas, kecamatan, tempat
    backend/app/domain/pasut.py                kurva pasut harmonik
    frontend/src/styles/token.css              seluruh warna, dibaca dari token

Angka rute dan jumlah ruas dibaca dari berkas itu saat video dibuat, bukan
diketik. Batas klaimnya sama dengan docs/final/presentasi/sumber_angka.md:
skenario potret bertanggal, kedalaman adalah estimasi, alat bantu
perencanaan, bukan peringatan dini resmi.

VISUAL. Mengikuti DESIGN.md: badan instrumen gelap, jendela peta terang,
tangga kedalaman dengan pola titik untuk kelas dalam, rute ambar bergaris
luar gelap, rute pembanding putus-putus, dan Pita Pasut sebagai satu-satunya
gradien. Gerak memakai lengkung cubic-bezier(.4,0,.2,1) milik aplikasi;
angka muncul dengan pudar, tidak berputar.

ALAT. Encoder tidak masuk runtime aplikasi:

    .venv\\Scripts\\python.exe -m pip install --target .deploy-local/video-tools -r docs/final/pameran/requirements-video.txt

Pillow, numpy, dan fontTools sudah ada di .venv. Huruf Barlow Semi Condensed
dan IBM Plex Mono diambil dari frontend/node_modules/@fontsource, lalu
dikonversi sekali ke TTF di .deploy-local/video-tools/fonts.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

AKAR = Path(__file__).resolve().parents[3]
FOLDER = Path(__file__).resolve().parent
ALAT_VIDEO = AKAR / ".deploy-local" / "video-tools"
sys.path.insert(0, str(AKAR / "backend"))
sys.path.insert(0, str(ALAT_VIDEO))

from app.domain import pasut  # noqa: E402

W, H, FPS, DURASI = 1920, 1080, 30, 60.0
SS = 2                                   # supersampling untuk garis
WIB = timezone(timedelta(hours=7))
KELUARAN = FOLDER / "Pasang_Surut_Pameran.mp4"
TAUTAN = "https://pasang-surut.vercel.app/app"

# Jendela peta dan pita pada adegan peta, meniru tata letak desktop aplikasi:
# rail gelap di kiri, peta terang mengisi sisanya, Pita Pasut di bawah.
JENDELA = (560, 64, 1296, 796)
PITA_BAWAH = (560, 876, 1296, 140)
PITA_BESAR = (96, 330, 1728, 430)
RAIL_X, RAIL_LEBAR = 72, 440
# Token --rute-lebar 5px dan --rute-abai-lebar 3px dikali 1,5 untuk layar
# pameran yang dilihat dari dua sampai tiga meter.
LEBAR_RUTE, LEBAR_ABAI = 7.5, 4.5


# ══════════════════════════════════════════════════════════════════════════
# TOKEN, HURUF, DAN GERAK
# ══════════════════════════════════════════════════════════════════════════
def _muat_token() -> dict:
    """Baca warna dari token.css, supaya video tidak punya palet sendiri."""
    css = (AKAR / "frontend/src/styles/token.css").read_text(encoding="utf-8")
    token = {}
    for nama, heks in re.findall(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", css):
        token.setdefault(nama, tuple(int(heks[i:i + 2], 16) for i in (1, 3, 5)))
    return token


WARNA = _muat_token()
for _wajib in ("lambung-1", "lambung-3", "dek-1", "tinta-2", "tinta-3", "tinta-balik",
               "air-1", "air-2", "air-3", "air-4", "bahaya", "rute", "rute-abai", "aman"):
    assert _wajib in WARNA, f"token --{_wajib} tidak ada di token.css"

_SUMBER_HURUF = {
    ("ui", 400): "barlow-semi-condensed/files/barlow-semi-condensed-latin-400-normal.woff",
    ("ui", 500): "barlow-semi-condensed/files/barlow-semi-condensed-latin-500-normal.woff",
    ("ui", 600): "barlow-semi-condensed/files/barlow-semi-condensed-latin-600-normal.woff",
    ("ui", 700): "barlow-semi-condensed/files/barlow-semi-condensed-latin-700-normal.woff",
    ("data", 400): "ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff",
    ("data", 600): "ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff",
}


def _berkas_huruf(jenis: str, tebal: int) -> Path:
    sumber = AKAR / "frontend/node_modules/@fontsource" / _SUMBER_HURUF[(jenis, tebal)]
    ttf = ALAT_VIDEO / "fonts" / (sumber.stem + ".ttf")
    if not ttf.exists():
        from fontTools.ttLib import TTFont
        ttf.parent.mkdir(parents=True, exist_ok=True)
        huruf = TTFont(str(sumber))
        huruf.flavor = None
        huruf.save(str(ttf))
    return ttf


@lru_cache(maxsize=None)
def huruf(jenis: str, tebal: int, ukuran: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(_berkas_huruf(jenis, tebal)), max(6, int(round(ukuran))))


def _bezier(p1x, p1y, p2x, p2y):
    def bx(u): return 3 * (1 - u) ** 2 * u * p1x + 3 * (1 - u) * u ** 2 * p2x + u ** 3
    def by(u): return 3 * (1 - u) ** 2 * u * p1y + 3 * (1 - u) * u ** 2 * p2y + u ** 3

    def f(t):
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(28):
            tengah = (lo + hi) / 2
            if bx(tengah) < t:
                lo = tengah
            else:
                hi = tengah
        return by((lo + hi) / 2)
    return f


LENGKUNG = _bezier(0.4, 0.0, 0.2, 1.0)      # --gerak-air-lengkung aplikasi


def maju(t: float, mulai: float, lama: float) -> float:
    if lama <= 0:
        return 1.0 if t >= mulai else 0.0
    return LENGKUNG(min(1.0, max(0.0, (t - mulai) / lama)))


def tampak(t: float, masuk: float, keluar: float | None = None, lama: float = 0.5) -> float:
    """Opasitas: pudar masuk mulai `masuk`, pudar keluar selesai tepat di `keluar`."""
    a = maju(t, masuk, lama)
    if keluar is not None:
        a *= 1.0 - maju(t, keluar - lama, lama)
    return a


def campur(a, b, f):
    return a + (b - a) * f


def angka(nilai: float, desimal: int = 1) -> str:
    """Angka gaya Indonesia: koma desimal, titik ribuan."""
    teks = f"{nilai:,.{desimal}f}"
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


# ══════════════════════════════════════════════════════════════════════════
# MENGGAMBAR TEKS DAN BENTUK
# ══════════════════════════════════════════════════════════════════════════
def rgba(nama: str, alfa: float = 1.0) -> tuple:
    return WARNA[nama] + (int(round(255 * max(0.0, min(1.0, alfa)))),)


def teks(d: ImageDraw.ImageDraw, xy, isi: str, fnt, warna: str, alfa: float = 1.0,
         jarak_huruf: float = 0.0, anchor: str = "la", halo: str | None = None) -> float:
    """Tulis teks; kembalikan lebarnya. `jarak_huruf` dalam em, untuk label gaya rambu.

    KENAPA LEWAT SPRITE. ImageDraw.text di Pillow 12 mengabaikan kanal alfa
    warna isi, walau ImageDraw bermode RGBA mencampur alfa untuk bentuk
    lain. Diuji: teks beralfa 10 persen tetap tergambar 255. Tanpa jalan
    memutar ini, teks adegan lama tetap menyala penuh sementara latarnya
    sudah memudar. Teks digambar penuh ke sprite transparan kecil, lalu
    sprite itu yang ditempel dengan opasitas.
    """
    tambah = jarak_huruf * fnt.size if jarak_huruf else 0.0
    if tambah:
        lebar = sum(fnt.getlength(c) for c in isi) + tambah * (len(isi) - 1)
    else:
        lebar = fnt.getlength(isi)
    if alfa <= 0.004 or not isi.strip():
        return lebar
    tepi = 3 if halo else 0
    x, y = xy
    if anchor[0] == "r":
        x -= lebar
    elif anchor[0] == "m":
        x -= lebar / 2
    jangkar = "l" + anchor[1]
    kiri, atas, kanan, bawah = fnt.getbbox(isi, anchor=jangkar, stroke_width=tepi)
    ruang = 2 + tepi
    ox = ruang - min(0.0, kiri)
    oy = ruang - atas
    w = int(math.ceil(ox + max(lebar, kanan) + ruang))
    h = int(math.ceil(oy + bawah + ruang))
    # Latar sprite diisi warna halo (atau warna teks) beralfa nol, supaya
    # tepi huruf yang dihaluskan tidak membawa pinggiran gelap.
    sprite = Image.new("RGBA", (w, h), WARNA[halo or warna] + (0,))
    sd = ImageDraw.Draw(sprite)
    lain = {"stroke_width": tepi, "stroke_fill": rgba(halo)} if halo else {}
    if tambah:
        cx = ox
        for c in isi:
            sd.text((cx, oy), c, font=fnt, fill=rgba(warna), anchor=jangkar, **lain)
            cx += fnt.getlength(c) + tambah
    else:
        sd.text((ox, oy), isi, font=fnt, fill=rgba(warna), anchor=jangkar, **lain)
    tempel(d._image, sprite, (x - ox, y - oy), alfa)
    return lebar


def bungkus(isi: str, fnt, lebar_maks: float) -> list[str]:
    baris, kini = [], ""
    for kata in isi.split():
        calon = f"{kini} {kata}".strip()
        if fnt.getlength(calon) <= lebar_maks or not kini:
            kini = calon
        else:
            baris.append(kini)
            kini = kata
    if kini:
        baris.append(kini)
    return baris


def paragraf(d, xy, isi: str, fnt, warna: str, lebar_maks: float, alfa: float = 1.0,
             spasi: float = 1.25) -> float:
    """Tulis paragraf terbungkus; kembalikan y di bawah baris terakhir."""
    x, y = xy
    for b in bungkus(isi, fnt, lebar_maks):
        teks(d, (x, y), b, fnt, warna, alfa)
        y += fnt.size * spasi
    return y


def tempel(dasar: Image.Image, lapis: Image.Image, xy=(0, 0), alfa: float = 1.0):
    """Tumpuk `lapis` ke `dasar` dengan opasitas tambahan.

    Bingkai video berformat RGB dan bentuknya digambar lewat ImageDraw
    bermode RGBA, karena kombinasi itu mencampur warna semi-transparan. Teks
    tidak ikut aturan itu dan ditangani lewat sprite di teks(). Lapisan peta
    tetap RGBA dan ditumpuk dengan alpha_composite.
    """
    if alfa <= 0.004:
        return
    if lapis.mode != "RGBA":
        lapis = lapis.convert("RGBA")
    a = lapis.getchannel("A")
    if alfa < 0.999:
        a = a.point(lambda v: int(v * alfa))
    pos = (int(round(xy[0])), int(round(xy[1])))
    if dasar.mode == "RGBA":
        salin = lapis.copy()
        salin.putalpha(a)
        dasar.alpha_composite(salin, dest=pos)
    else:
        dasar.paste(lapis.convert("RGB"), pos, mask=a)


def lingkaran(dasar: Image.Image, cx, cy, r, isi: str, tepi: str | None = None,
              lebar_tepi: float = 0.0, alfa: float = 1.0, isi_alfa: float = 1.0):
    """Lingkaran berhalus, digambar 4x lalu diperkecil."""
    k = 4
    tepi_total = r + lebar_tepi
    ukuran = int(math.ceil(tepi_total * 2 + 4))
    kan = Image.new("RGBA", (ukuran * k, ukuran * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(kan)
    c = ukuran * k / 2
    if tepi:
        d.ellipse([c - tepi_total * k, c - tepi_total * k, c + tepi_total * k, c + tepi_total * k],
                  fill=rgba(tepi))
    d.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], fill=rgba(isi, isi_alfa))
    kan = kan.resize((ukuran, ukuran), Image.LANCZOS)
    tempel(dasar, kan, (cx - ukuran / 2, cy - ukuran / 2), alfa)


def kotak(d, rect, warna: str, alfa: float = 1.0, radius: int = 0):
    x, y, w, h = rect
    if radius:
        d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=rgba(warna, alfa))
    else:
        d.rectangle([x, y, x + w, y + h], fill=rgba(warna, alfa))


# ══════════════════════════════════════════════════════════════════════════
# PETA
# ══════════════════════════════════════════════════════════════════════════
class Kamera:
    """Proyeksi ekuirektangular sederhana, cukup untuk AOI 13 x 8 km."""

    def __init__(self, bbox, lebar: int, tinggi: int, isi: float = 0.96):
        lon0, lat0, lon1, lat1 = bbox
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        self.skala = min(lebar * isi / ((lon1 - lon0) * self.k), tinggi * isi / (lat1 - lat0))
        self.cx, self.cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
        self.lebar, self.tinggi = lebar, tinggi

    def px(self, lon, lat):
        x = (np.asarray(lon) - self.cx) * self.k * self.skala + self.lebar / 2
        y = (self.cy - np.asarray(lat)) * self.skala + self.tinggi / 2
        return x, y

    def zoom_maplibre(self) -> float:
        meter_per_px = 111_320.0 / self.skala
        return math.log2(78_271.517 * self.k / meter_per_px)


def _bertumpuk(a, b) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def lebar_jalan(jenis: str, z: float) -> float:
    """Salinan ekspresi lebar lapisan ruas-dasar di Peta.jsx."""
    f = min(1.0, max(0.0, (z - 11) / 5))
    if jenis in ("trunk", "primary"):
        a, b = 1.6, 4.5
    elif jenis in ("secondary", "tertiary"):
        a, b = 1.1, 3.2
    else:
        a, b = 0.6, 1.8
    return a + (b - a) * f


def kelas_kedalaman(cm: float) -> int:
    if cm < 1:
        return 0
    if cm < 10:
        return 1
    if cm < 25:
        return 2
    if cm < 50:
        return 3
    return 4


def pola_titik(lebar: int, tinggi: int, sisi: float, jari: float) -> Image.Image:
    """Kisi halftone Peta.jsx: dua titik berselang per ubin, tepinya dihaluskan."""
    y, x = np.mgrid[0:tinggi, 0:lebar].astype(np.float32) + 0.5
    u, v = np.mod(x, sisi), np.mod(y, sisi)
    alfa = np.zeros((tinggi, lebar), np.float32)
    for pusat in (0.25 * sisi, 0.75 * sisi):
        du = np.minimum(np.abs(u - pusat), sisi - np.abs(u - pusat))
        dv = np.minimum(np.abs(v - pusat), sisi - np.abs(v - pusat))
        alfa = np.maximum(alfa, np.clip(jari + 0.5 - np.hypot(du, dv), 0, 1))
    return Image.fromarray((alfa * 255).astype(np.uint8), "L")


def topeng_baru(lebar, tinggi):
    im = Image.new("L", (lebar * SS, tinggi * SS), 0)
    return im, ImageDraw.Draw(im)


def perkecil(topeng: Image.Image, lebar: int, tinggi: int) -> Image.Image:
    return topeng.resize((lebar, tinggi), Image.LANCZOS)


def warnai(topeng: Image.Image, warna: str, alfa: float = 1.0) -> Image.Image:
    lapis = Image.new("RGBA", topeng.size, WARNA[warna] + (0,))
    lapis.putalpha(topeng if alfa >= 0.999 else topeng.point(lambda v: int(v * alfa)))
    return lapis


def garis_putus(titik: np.ndarray, panjang_isi: float, panjang_sela: float):
    """Pecah polyline menjadi potongan putus-putus, mengikuti panjang lintasan."""
    potongan, kini, sisa, isi = [], [tuple(titik[0])], panjang_isi, True
    for a, b in zip(titik[:-1], titik[1:]):
        seg = float(np.hypot(*(b - a)))
        pos = 0.0
        while seg - pos > sisa:
            pos += sisa
            p = tuple(a + (b - a) * (pos / seg))
            if isi:
                kini.append(p)
                potongan.append(kini)
            kini = [p]
            isi = not isi
            sisa = panjang_isi if isi else panjang_sela
        sisa -= seg - pos
        if isi:
            kini.append(tuple(b))
    if isi and len(kini) > 1:
        potongan.append(kini)
    return potongan


def potong_lintasan(titik: np.ndarray, fraksi: float) -> np.ndarray:
    """Bagian awal polyline sepanjang `fraksi` dari panjang totalnya."""
    if fraksi >= 1:
        return titik
    seg = np.hypot(*np.diff(titik, axis=0).T)
    kum = np.concatenate([[0], np.cumsum(seg)])
    target = kum[-1] * max(0.0, fraksi)
    i = int(np.searchsorted(kum, target, side="right"))
    if i <= 0:
        return titik[:1]
    if i >= len(titik):
        return titik
    f = (target - kum[i - 1]) / max(seg[i - 1], 1e-9)
    ujung = titik[i - 1] + (titik[i] - titik[i - 1]) * f
    return np.vstack([titik[:i], ujung])


class Peta:
    """Semua lapisan peta untuk satu kamera, digambar sekali lalu dipakai ulang."""

    def __init__(self, data, kamera: Kamera, jam_genangan: list[str]):
        self.kam = kamera
        self._rute_jadi = {}
        w, h = kamera.lebar, kamera.tinggi
        z = kamera.zoom_maplibre()
        self.ruas = {}
        for f in data["potret"]["ruas"]["features"]:
            lon, lat = np.array(f["geometry"]["coordinates"]).T
            x, y = kamera.px(lon, lat)
            self.ruas[str(f["properties"]["edge_id"])] = (np.stack([x, y], 1), f["properties"]["jenis"])

        # Dasar: permukaan dek, garis pantai, batas kecamatan, jaringan jalan.
        dasar = Image.new("RGBA", (w, h), rgba("dek-1"))
        pantai, dp = topeng_baru(w, h)
        batas, db = topeng_baru(w, h)
        for f in data["konteks"]["features"]:
            jenis = f["properties"]["jenis"]
            geo = f["geometry"]
            garis = [geo["coordinates"]] if geo["type"] == "LineString" else (
                geo["coordinates"] if geo["type"] == "MultiLineString" else [])
            for g in garis:
                lon, lat = np.array(g).T
                x, y = kamera.px(lon, lat)
                pts = np.stack([x, y], 1) * SS
                if jenis == "pantai":
                    dp.line([tuple(p) for p in pts], fill=255, width=2 * SS, joint="curve")
                elif jenis == "batas":
                    for pot in garis_putus(pts, 4 * SS, 4 * SS):
                        db.line(pot, fill=255, width=SS)
        jalan, dj = topeng_baru(w, h)
        for pts, jenis in self.ruas.values():
            dj.line([tuple(p) for p in pts * SS], fill=255,
                    width=max(1, int(round(lebar_jalan(jenis, z) * SS))))
        for topeng, warna, alfa in ((batas, "tinta-2", 0.35), (pantai, "air-3", 1.0),
                                    (jalan, "tinta-2", 1.0)):
            dasar = Image.alpha_composite(dasar, warnai(perkecil(topeng, w, h), warna, alfa))
        self.dasar = dasar

        jarang = pola_titik(w, h, 10, 1.4)
        rapat = pola_titik(w, h, 6, 1.3)
        self.genangan = {}
        for kunci in jam_genangan:
            per_ruas = data["potret"]["genangan"].get(kunci, {})
            topeng = {c: topeng_baru(w, h) for c in (1, 2, 3, 4)}
            for eid, nilai in per_ruas.items():
                cm = float(nilai[0] if isinstance(nilai, list) else nilai)
                c = kelas_kedalaman(cm)
                if not c or eid not in self.ruas:
                    continue
                lebar = (3 + 3 * min(cm, 50) / 50) * SS
                topeng[c][1].line([tuple(p) for p in self.ruas[eid][0] * SS], fill=255,
                                  width=int(round(lebar)), joint="curve")
            lapis = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            kecil = {c: perkecil(topeng[c][0], w, h) for c in topeng}
            for c, nama in ((1, "air-1"), (2, "air-2"), (3, "air-3"), (4, "air-4")):
                lapis = Image.alpha_composite(lapis, warnai(kecil[c], nama))
            for c, pola in ((3, jarang), (4, rapat)):
                lapis = Image.alpha_composite(
                    lapis, warnai(ImageChops.multiply(kecil[c], pola), "dek-1"))
            self.genangan[kunci] = lapis

    def rute(self, koordinat, lebar: float, fraksi: float, putus: bool = False,
             garis_luar: str | None = None, warna: str = "rute") -> Image.Image:
        kunci = (id(koordinat), lebar, putus, garis_luar, warna)
        if fraksi >= 1 and kunci in self._rute_jadi:
            return self._rute_jadi[kunci]
        hasil = self._rute(koordinat, lebar, fraksi, putus, garis_luar, warna)
        if fraksi >= 1:
            self._rute_jadi[kunci] = hasil
        return hasil

    def _rute(self, koordinat, lebar, fraksi, putus, garis_luar, warna) -> Image.Image:
        w, h = self.kam.lebar, self.kam.tinggi
        lon, lat = np.array(koordinat).T
        x, y = self.kam.px(lon, lat)
        pts = potong_lintasan(np.stack([x, y], 1), fraksi) * SS
        lapis = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if len(pts) < 2:
            return lapis
        if garis_luar:
            luar, dl = topeng_baru(w, h)
            dl.line([tuple(p) for p in pts], fill=255, width=int((lebar + 2) * SS), joint="curve")
            lapis = Image.alpha_composite(lapis, warnai(perkecil(luar, w, h), garis_luar))
        inti, di = topeng_baru(w, h)
        if putus:
            # Garis luar gelap per potongan, prinsip yang sama dengan rute ambar
            # di DESIGN.md: tanpa itu abu-abu terang hilang di atas jalan abu-abu gelap.
            luar, dl = topeng_baru(w, h)
            potongan = garis_putus(pts, 2 * lebar * SS, 2 * lebar * SS)
            for pot in potongan:
                dl.line(pot, fill=255, width=int((lebar + 2.5) * SS))
            lapis = Image.alpha_composite(lapis, warnai(perkecil(luar, w, h), "lambung-1"))
            for pot in potongan:
                di.line(pot, fill=255, width=int(lebar * SS))
        else:
            di.line([tuple(p) for p in pts], fill=255, width=int(lebar * SS), joint="curve")
        return Image.alpha_composite(lapis, warnai(perkecil(inti, w, h), warna))


# ══════════════════════════════════════════════════════════════════════════
# PITA PASUT
# ══════════════════════════════════════════════════════════════════════════
HARI = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]


def label_jam(waktu_utc: str) -> str:
    w = datetime.fromisoformat(waktu_utc).astimezone(WIB)
    return f"{HARI[w.weekday()]} {w.day} · {w:%H.%M}"


def gambar_pita(bingkai: Image.Image, rect, data, indeks: float, f_kurva: float = 1.0,
                f_tanda: float = 1.0, alfa: float = 1.0, skala: float = 1.0):
    """Pita Pasut seperti PitaPasut.jsx, diperbesar `skala` kali untuk layar pameran."""
    if alfa <= 0.004:
        return
    x0, y0, w, h = rect
    jam = data["potret"]["jam"]
    n = len(jam)
    s = skala
    kan = Image.new("RGB", (int(w * SS), int(h * SS)), WARNA["lambung-1"])
    d = ImageDraw.Draw(kan, "RGBA")

    def S(v):
        return v * SS

    kepala, kaki, tepi = 30 * s, 26 * s, 14 * s
    puncak, dasar = kepala + 8 * s, h - kaki
    lebar_g = w - 2 * tepi
    X = lambda i: tepi + i * lebar_g / (n - 1)          # noqa: E731
    maks = max(0.1, max(abs(j["tinggi_pasut_m"]) for j in jam))
    tengah = (dasar + puncak) / 2
    Y = lambda m: tengah - (m / maks) * ((dasar - puncak) / 2) * 0.86  # noqa: E731

    # garis atas penanda panel, seperti garis rambut --lambung-3
    d.line([(0, 0), (S(w), 0)], fill=rgba("lambung-3"), width=max(1, int(S(1))))

    # arsiran jam berisiko dan penanda jam aman
    langkah = lebar_g / (n - 1)
    for i, j in enumerate(jam):
        if j["ruas_tergenang"] > 0:
            d.rectangle([S(X(i) - langkah / 2), S(dasar - 7 * s), S(X(i) + langkah / 2), S(dasar)],
                        fill=rgba("bahaya", 0.85 * f_tanda))
        else:
            d.rectangle([S(X(i) - 0.9 * s), S(dasar - 2.4 * s), S(X(i) + 0.9 * s), S(dasar)],
                        fill=rgba("aman", f_tanda))

    # kurva halus dari fungsi pasut yang sama dengan backend
    halus = data["pasut_halus"]              # (jam_desimal, meter)
    batas = f_kurva * (n - 1)
    pilih = halus[halus[:, 0] <= batas + 1e-9]
    if len(pilih) >= 2:
        titik = [(S(X(a)), S(Y(b))) for a, b in pilih]
        dasar_kolom = S(dasar - 8 * s)
        # kolom air: satu-satunya gradien, --air-2 55% ke --air-4 15%
        topeng = Image.new("L", kan.size, 0)
        ImageDraw.Draw(topeng).polygon(titik + [(titik[-1][0], dasar_kolom), (titik[0][0], dasar_kolom)],
                                       fill=255)
        gy = np.linspace(0, 1, kan.size[1], dtype=np.float32)[:, None]
        atas, bawah = np.array(WARNA["air-2"], np.float32), np.array(WARNA["air-4"], np.float32)
        warna_g = atas + (bawah - atas) * gy[..., None]
        alfa_g = (0.55 + (0.15 - 0.55) * gy) * (np.asarray(topeng, np.float32) / 255)
        latar = np.asarray(kan, np.float32)
        hasil = latar * (1 - alfa_g[..., None]) + warna_g * alfa_g[..., None]
        kan = Image.fromarray(np.clip(hasil, 0, 255).astype(np.uint8), "RGB")
        d = ImageDraw.Draw(kan, "RGBA")
        d.line([(S(tepi), S(Y(0))), (S(w - tepi), S(Y(0)))], fill=rgba("lambung-3"), width=int(S(1)))
        d.line(titik, fill=rgba("tinta-balik"), width=max(1, int(S(1.5 * s))), joint="curve")

    # guratan jam bergradasi: panjang tiap 6 jam, pendek tiap jam
    f_label = huruf("data", 400, 11 * s * SS)
    for i, j in enumerate(jam):
        wib = datetime.fromisoformat(j["waktu_utc"]).astimezone(WIB)
        panjang = wib.hour % 6 == 0
        d.line([(S(X(i)), S(dasar)), (S(X(i)), S(dasar + (6 if panjang else 3) * s))],
               fill=rgba("tinta-3", 0.9 if panjang else 0.45), width=max(1, int(S((1 if panjang else 0.75) * s))))
        if panjang:
            isi = f"{HARI[wib.weekday()]} {wib.day}" if wib.hour == 0 else f"{wib:%H}"
            d.text((S(X(i) - (2 * s if i == 0 else 0)), S(dasar + 8 * s)), isi, font=f_label,
                   fill=rgba("tinta-3"), anchor="la" if i == 0 else "ma")

    # kepala: judul dan jam terpilih
    teks(d, (S(tepi), S(9 * s)), "PITA PASUT · 72 JAM", huruf("ui", 700, 13 * s * SS), "tinta-3",
         jarak_huruf=0.08)
    i_bulat = int(round(min(max(indeks, 0), n - 1)))
    aktif = jam[i_bulat]
    tinggi_aktif = float(np.interp(indeks, halus[:, 0], halus[:, 1]))
    kanan = f"{label_jam(aktif['waktu_utc'])} WIB   {'+' if tinggi_aktif >= 0 else '−'}{angka(abs(tinggi_aktif), 2)} m"
    d.text((S(w - tepi), S(8 * s)), kanan, font=huruf("data", 600, 13 * s * SS),
           fill=rgba("tinta-balik"), anchor="ra")

    # pegangan geser
    if f_kurva >= 0.999:
        px = S(X(indeks))
        d.line([(px, S(puncak - 2 * s)), (px, S(dasar + 6 * s))], fill=rgba("rute"), width=int(S(2 * s)))
        r, rt = S(4.5 * s), S(1.5 * s)
        cy = S(Y(tinggi_aktif))
        d.ellipse([px - r - rt, cy - r - rt, px + r + rt, cy + r + rt], fill=rgba("lambung-1"))
        d.ellipse([px - r, cy - r, px + r, cy + r], fill=rgba("rute"))

    kan = kan.resize((int(w), int(h)), Image.LANCZOS)
    tempel(bingkai, kan, (x0, y0), alfa)


# ══════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════
def muat_data() -> dict:
    baca = lambda p: json.loads((AKAR / p).read_text(encoding="utf-8"))  # noqa: E731
    potret = baca("data/processed/potret_demo.json")
    skenario = baca("docs/final/presentasi/aset/skenario.json")
    konteks = baca("frontend/src/data/konteks-peta.json")

    mulai = datetime.fromisoformat(potret["jam"][0]["waktu_utc"])
    langkah = np.arange(0, len(potret["jam"]) - 1 + 1e-9, 1 / 6)          # tiap 10 menit
    tinggi = [float(pasut.tinggi_pasut_m(mulai + timedelta(hours=float(a)))) for a in langkah]
    # Kurva halus harus melewati nilai per jam yang ada di potret; bila fungsi
    # backend berubah dan tidak lagi cocok, video jangan dibuat diam-diam.
    for i, j in enumerate(potret["jam"]):
        assert abs(tinggi[i * 6] - j["tinggi_pasut_m"]) < 0.002, "kurva pasut tidak cocok dengan potret"

    rute = {}
    for jam_wib in ("8", "13"):
        for f in skenario[jam_wib]["rute"]["features"]:
            rute[(jam_wib, f["properties"]["jenis"])] = f
    tempat = {f["properties"]["kunci"]: f for f in konteks["features"]
              if f["properties"]["jenis"] == "tempat"}
    return {"potret": potret, "skenario": skenario, "konteks": konteks,
            "pasut_halus": np.stack([langkah, tinggi], 1), "rute": rute, "tempat": tempat}


def kunci_jam(data, indeks: int) -> str:
    return data["potret"]["jam"][indeks]["waktu_utc"]


# ══════════════════════════════════════════════════════════════════════════
# ADEGAN
# ══════════════════════════════════════════════════════════════════════════
class Video:
    def __init__(self):
        mulai = time.perf_counter()
        self.d = data = muat_data()
        w, h = JENDELA[2], JENDELA[3]
        from app import config
        self.kam_penuh = Kamera(tuple(config.bbox_aoi()), w, h, isi=0.97)

        # Kamera dekat: kotak kedua rute pukul 08.00 ditambah ruang, disesuaikan ke rasio jendela.
        pts = np.array([c for k, f in data["rute"].items() for c in f["geometry"]["coordinates"]])
        lon0, lat0 = pts.min(0)
        lon1, lat1 = pts.max(0)
        lebar_lon, tinggi_lat = lon1 - lon0, lat1 - lat0
        # Kiri lebih longgar: label "Stasiun Semarang Tawang" diletakkan di kiri
        # penanda supaya tidak menutupi rute, dan harus tetap di dalam jendela.
        self.kam_dekat = Kamera((lon0 - lebar_lon * 0.34, lat0 - tinggi_lat * 0.20,
                                 lon1 + lebar_lon * 0.10, lat1 + tinggi_lat * 0.24), w, h, isi=1.0)

        jam_penuh = [kunci_jam(data, i) for i in range(0, 14)]      # Sab 26, 00.00 sampai 13.00
        print("menggambar lapisan peta penuh ...", flush=True)
        self.peta_penuh = Peta(data, self.kam_penuh, jam_penuh)
        print("menggambar lapisan peta dekat ...", flush=True)
        self.peta_dekat = Peta(data, self.kam_dekat, jam_penuh[8:])

        # Topeng sudut jendela, radius 6px sesuai --r-2.
        topeng = Image.new("L", (w * 4, h * 4), 0)
        ImageDraw.Draw(topeng).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=6 * 4, fill=255)
        self.topeng_jendela = topeng.resize((w, h), Image.LANCZOS)

        # Kotak kamera dekat di dalam koordinat kamera penuh, untuk animasi perbesaran.
        kd = self.kam_dekat
        lon_a = kd.cx - (kd.lebar / 2) / (kd.k * kd.skala)
        lon_b = kd.cx + (kd.lebar / 2) / (kd.k * kd.skala)
        lat_a = kd.cy + (kd.tinggi / 2) / kd.skala
        lat_b = kd.cy - (kd.tinggi / 2) / kd.skala
        xa, ya = self.kam_penuh.px(lon_a, lat_a)
        xb, yb = self.kam_penuh.px(lon_b, lat_b)
        self.kotak_dekat = (float(xa), float(ya), float(xb), float(yb))

        self.jumlah = {i: data["potret"]["jam"][i]["ruas_tergenang"] for i in range(14)}
        self.qr = self._qr()
        print(f"persiapan selesai dalam {time.perf_counter() - mulai:.1f} detik", flush=True)

    def _qr(self) -> Image.Image:
        """QR ke /app. Dibuat ulang dengan qrcode bila tersedia, jatuh ke PNG tim bila tidak."""
        try:
            sys.path.append(str(AKAR / ".deploy-local" / "presentation-tools"))
            import qrcode
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=1, border=2)
            qr.add_data(TAUTAN)
            qr.make(fit=True)
            modul = np.array(qr.get_matrix(), bool)
            kecil = Image.fromarray(np.where(modul, 0, 255).astype(np.uint8), "L")
        except ImportError:
            kecil = Image.open(AKAR / "docs/final/presentasi/aset/qr_aplikasi.png").convert("L")
        kali = max(1, 300 // kecil.size[0])
        besar = kecil.resize((kecil.size[0] * kali, kecil.size[1] * kali), Image.NEAREST)
        warna = Image.new("RGBA", besar.size, rgba("dek-1"))
        gelap = Image.new("RGBA", besar.size, rgba("lambung-1"))
        warna.paste(gelap, mask=ImageChops.invert(besar))
        return warna

    # ── komposisi peta per bingkai ──────────────────────────────────────
    def peta(self, bingkai: Image.Image, t: float, alfa: float, jam_a: int, jam_b: int, f_jam: float,
             f_zoom: float, lapis_atas: list):
        if alfa <= 0.004:
            return
        w, h = JENDELA[2], JENDELA[3]
        if f_zoom < 0.999:
            penuh = self.peta_penuh.dasar.copy()
            self._genangan(penuh, self.peta_penuh, jam_a, jam_b, f_jam)
            if f_zoom > 0.001:
                xa, ya, xb, yb = self.kotak_dekat
                # perbesaran geometrik: skala berubah eksponensial, pusat bergeser linear
                s = (w / (xb - xa)) ** f_zoom
                cx = campur(w / 2, (xa + xb) / 2, f_zoom)
                cy = campur(h / 2, (ya + yb) / 2, f_zoom)
                kotak_potong = (cx - w / 2 / s, cy - h / 2 / s, cx + w / 2 / s, cy + h / 2 / s)
                penuh = penuh.transform((w, h), Image.EXTENT, kotak_potong, Image.BICUBIC)
            gambar = penuh
        else:
            gambar = None
        if f_zoom > 0.55:
            dekat = self.peta_dekat.dasar.copy()
            self._genangan(dekat, self.peta_dekat, jam_a, jam_b, f_jam)
            f = maju(f_zoom, 0.55, 0.45) if f_zoom < 0.999 else 1.0
            gambar = dekat if gambar is None else Image.blend(gambar, dekat, f)
        for lapis, a in lapis_atas:
            tempel(gambar, lapis, (0, 0), a)
        gambar.putalpha(ImageChops.multiply(gambar.getchannel("A"), self.topeng_jendela))
        tempel(bingkai, gambar, JENDELA[:2], alfa)

    def _genangan(self, dasar, peta: Peta, jam_a: int, jam_b: int, f: float):
        kunci_a, kunci_b = kunci_jam(self.d, jam_a), kunci_jam(self.d, jam_b)
        if kunci_a in peta.genangan:
            tempel(dasar, peta.genangan[kunci_a], (0, 0), 1 - f if jam_a != jam_b else 1)
        if jam_b != jam_a and kunci_b in peta.genangan:
            tempel(dasar, peta.genangan[kunci_b], (0, 0), f)

    # ── elemen tetap di jendela peta ────────────────────────────────────
    def legenda(self, d, alfa: float):
        if alfa <= 0.004:
            return
        x, y, w, h = self._rect_legenda()
        kotak(d, (x, y, w, h), "lambung-1", alfa, radius=6)
        teks(d, (x + 20, y + 18), "KEDALAMAN GENANGAN", huruf("ui", 700, 18), "tinta-balik", alfa, 0.08)
        baris = [("tinta-2", "Kering", ""), ("air-1", "Tipis", "1–10 cm"), ("air-2", "Sedang", "10–25 cm"),
                 ("air-3", "Dalam", "25–50 cm"), ("air-4", "Sangat dalam", "di atas 50 cm")]
        for k, (warna, nama, rentang) in enumerate(baris):
            yy = y + 56 + k * 34
            if warna == "tinta-2":
                d.line([(x + 20, yy + 11), (x + 60, yy + 11)], fill=rgba(warna, alfa), width=3)
            else:
                kotak(d, (x + 20, yy + 4, 40, 14), warna, alfa, radius=3)
            if warna in ("air-3", "air-4"):
                sisi = 10 if warna == "air-3" else 6
                for tx in np.arange(x + 20 + sisi * 0.25, x + 60, sisi):
                    for ty in np.arange(yy + 4 + sisi * 0.25, yy + 18, sisi):
                        for dx, dy in ((0, 0), (sisi / 2, sisi / 2)):
                            if tx + dx < x + 59 and ty + dy < yy + 17:
                                d.ellipse([tx + dx - 1.3, ty + dy - 1.3, tx + dx + 1.3, ty + dy + 1.3],
                                          fill=rgba("dek-1", alfa))
            teks(d, (x + 76, yy), nama, huruf("ui", 600, 21), "tinta-balik", alfa)
            teks(d, (x + w - 20, yy + 2), rentang, huruf("data", 400, 17), "tinta-3", alfa, anchor="ra")
        paragraf(d, (x + 20, y + 228), "Kedalaman adalah estimasi, bukan hasil pengukuran langsung",
                 huruf("ui", 400, 16), "tinta-3", w - 40, alfa, 1.2)

    def lencana(self, d, alfa: float):
        if alfa <= 0.004:
            return
        isi = "INDEKS KERENTANAN — BUKAN PREDIKSI GENANGAN"
        fnt = huruf("ui", 700, 20)
        lebar = sum(fnt.getlength(c) for c in isi) + 0.06 * fnt.size * (len(isi) - 1) + 36
        x = JENDELA[0] + JENDELA[2] - 20 - lebar
        y = JENDELA[1] + 20
        kotak(d, (x, y, lebar, 42), "bahaya", alfa, radius=3)
        teks(d, (x + 18, y + 21), isi, fnt, "tinta-balik", alfa, 0.06, anchor="lm")

    def atribusi(self, d, alfa: float):
        if alfa <= 0.004:
            return
        isi = "© OpenStreetMap contributors"
        fnt = huruf("ui", 500, 16)
        lebar = fnt.getlength(isi) + 16
        x = JENDELA[0] + JENDELA[2] - lebar - 6
        y = JENDELA[1] + JENDELA[3] - 30
        kotak(d, (x, y, lebar, 24), "dek-1", 0.85 * alfa, radius=3)
        teks(d, (x + 8, y + 12), isi, fnt, "tinta-2", alfa, anchor="lm")

    def label_kecamatan(self, d, alfa: float, alfa_legenda: float = 0.0):
        """Nama kecamatan. Seperti renderer aplikasi, label yang bertabrakan dilewati."""
        if alfa <= 0.004:
            return
        fnt = huruf("ui", 500, 24)
        terpasang = []
        kotak_legenda = self._kotak_legenda()
        for f in self.d["konteks"]["features"]:
            if f["properties"]["jenis"] != "wilayah":
                continue
            nama = f["properties"]["nama"]
            x, y = self.kam_penuh.px(*f["geometry"]["coordinates"])
            x, y = float(x) + JENDELA[0], float(y) + JENDELA[1]
            lebar = fnt.getlength(nama)
            kotak_label = (x - lebar / 2 - 8, y - 16, x + lebar / 2 + 8, y + 16)
            if not (JENDELA[0] + 60 < x < JENDELA[0] + JENDELA[2] - 60
                    and JENDELA[1] + 80 < y < JENDELA[1] + JENDELA[3] - 40):
                continue
            if any(_bertumpuk(kotak_label, k) for k in terpasang):
                continue
            terpasang.append(kotak_label)
            a = alfa * (1 - alfa_legenda if _bertumpuk(kotak_label, kotak_legenda) else 1)
            teks(d, (x, y), nama, fnt, "tinta-2", a, anchor="mm", halo="dek-1")

    def _kotak_legenda(self):
        x, y, w, h = self._rect_legenda()
        return (x, y, x + w, y + h)

    def _rect_legenda(self):
        return (JENDELA[0] + 20, JENDELA[1] + JENDELA[3] - 20 - 270, 400, 270)

    def titik_perjalanan(self, bingkai, d, alfa: float):
        if alfa <= 0.004:
            return
        # Penanda diletakkan di ujung rute yang benar-benar dihitung API, bukan di
        # koordinat tempat pada data konteks: keduanya bisa berselisih ratusan
        # meter karena rute memakai simpul akses jalan terdekat.
        garis = self.d["rute"][("8", "rute_sadar_rob")]["geometry"]["coordinates"]
        for ujung, peran, label, arah in ((garis[0], "asal", "Stasiun Semarang Tawang", "kiri"),
                                          (garis[-1], "tujuan", "Kawasan Industri Terboyo", "kiri")):
            x, y = self.kam_dekat.px(*ujung)
            x, y = float(x) + JENDELA[0], float(y) + JENDELA[1]
            lingkaran(bingkai, x, y, 9 * 1.4, "lambung-1", tepi="rute", lebar_tepi=2 * 1.4, alfa=alfa)
            lingkaran(bingkai, x, y, 3.5 * 1.4, "rute" if peran == "asal" else "aman", alfa=alfa)
            if arah == "kiri":
                teks(d, (x - 26, y), label, huruf("ui", 600, 26), "tinta-1", alfa, anchor="rm", halo="dek-1")
            else:
                teks(d, (x, y - 34), label, huruf("ui", 600, 26), "tinta-1", alfa, anchor="mm", halo="dek-1")

    # ── rail kiri ───────────────────────────────────────────────────────
    def label_rail(self, d, y, isi, alfa):
        teks(d, (RAIL_X, y), isi, huruf("ui", 700, 22), "tinta-3", alfa, 0.08)

    def judul_rail(self, d, y, isi, alfa, ukuran=56):
        return paragraf(d, (RAIL_X, y), isi, huruf("ui", 600, ukuran), "tinta-balik", RAIL_LEBAR, alfa, 1.12)

    def angka_satuan(self, d, xy, pasangan, alfa, ukuran=40):
        """Pasangan (angka, satuan): angka mono besar, satuan lebih kecil dan redup."""
        x, y = xy
        for nilai, satuan in pasangan:
            x += teks(d, (x, y), nilai, huruf("data", 600, ukuran), "tinta-balik", alfa, anchor="ls")
            x += 6
            x += teks(d, (x, y), satuan, huruf("ui", 500, ukuran * 0.55), "tinta-3", alfa, anchor="ls")
            x += 22
        return x

    # ── tiap adegan ─────────────────────────────────────────────────────
    def bingkai(self, t: float) -> Image.Image:
        im = Image.new("RGB", (W, H), WARNA["lambung-1"])
        d = ImageDraw.Draw(im, "RGBA")
        if t < 6.6:
            self.adegan_pembuka(im, d, t)
        if 6.3 <= t < 16.2:
            self.adegan_pita(im, d, t)
        if 14.9 <= t < 44.6:
            self.adegan_peta(im, d, t)
        if 44.4 <= t < 52.6:
            self.adegan_cara_kerja(im, d, t)
        if t >= 52.4:
            self.adegan_penutup(im, d, t)
        return im

    def adegan_pembuka(self, im, d, t):
        a = tampak(t, 0.2, 6.5, 0.6)
        naik = (1 - maju(t, 0.2, 0.8)) * 14
        self.label_rail(d, 150, "PASANG SURUT · SEMARANG UTARA DAN TIMUR", a)
        fnt = huruf("ui", 600, 132)
        teks(d, (RAIL_X, 230 + naik), "Berangkat kapan,", fnt, "tinta-balik", a)
        teks(d, (RAIL_X, 380 + naik), "lewat mana?", fnt, "tinta-balik", a)
        paragraf(d, (RAIL_X, 580), "Rob mengikuti pasang laut. Jalan yang kering siang ini bisa "
                 "tergenang besok pagi.", huruf("ui", 400, 44), "tinta-3", 1000,
                 tampak(t, 1.8, 6.5, 0.6), 1.3)

        # papan duga air: guratan bergradasi, air naik ke tinggi pasut Sab 26 pukul 08.00
        a2 = tampak(t, 1.0, 6.5, 0.6)
        x, atas, bawah = 1560, 150, 930
        meter_ke_y = lambda m: bawah - (m + 0.4) / 0.8 * (bawah - atas)  # noqa: E731
        target = self.d["potret"]["jam"][8]["tinggi_pasut_m"]
        muka = campur(-0.25, target, maju(t, 1.4, 3.6))
        ya = meter_ke_y(muka)
        kotak(d, (x - 4, ya, 208, bawah - ya), "air-2", 0.30 * a2)
        for k in range(0, 81):
            m = -0.4 + k * 0.01
            y = meter_ke_y(m)
            panjang = k % 10 == 0
            d.line([(x, y), (x + (60 if panjang else 26 if k % 5 == 0 else 14), y)],
                   fill=rgba("tinta-3", (0.9 if panjang else 0.45) * a2), width=2 if panjang else 1)
            if panjang:
                teks(d, (x + 76, y), ("+" if m > 0.001 else "−" if m < -0.001 else "") + angka(abs(m), 1),
                     huruf("data", 400, 24), "tinta-3", a2, anchor="lm")
        d.line([(x - 4, ya), (x + 204, ya)], fill=rgba("tinta-balik", a2), width=3)
        teks(d, (x - 16, ya), f"{'+' if muka >= 0 else '−'}{angka(abs(muka), 2)} m",
             huruf("data", 600, 30), "tinta-balik", a2, anchor="rm")
        teks(d, (x - 16, ya + 34), "Sab 26 Sep · 08.00", huruf("data", 400, 20), "tinta-3",
             a2 * maju(t, 4.4, 0.6), anchor="rm")

    def adegan_pita(self, im, d, t):
        a_teks = tampak(t, 6.6, 14.9, 0.6)
        teks(d, (RAIL_X + 24, 120), "Pasang surut bisa dihitung jauh hari.", huruf("ui", 600, 76),
             "tinta-balik", a_teks)
        paragraf(d, (RAIL_X + 24, 218), "Kurva ini dihitung dari rumus pasang surut harmonik untuk "
                 "perairan Semarang, tanpa sensor dan tanpa internet.", huruf("ui", 400, 36), "tinta-3",
                 1740, tampak(t, 7.2, 14.9, 0.6))
        if t < 15.0:
            f_kurva = maju(t, 7.0, 2.8)
            f_tanda = maju(t, 9.8, 0.6)
            gambar_pita(im, PITA_BESAR, self.d, 0.0, f_kurva, f_tanda, tampak(t, 6.4, None, 0.6), 2.6)
        a_chip = tampak(t, 10.2, 14.9, 0.5)
        y = PITA_BESAR[1] + PITA_BESAR[3] + 40
        x = RAIL_X + 24
        kotak(d, (x, y + 6, 36, 16), "bahaya", 0.85 * a_chip)
        x += 50 + teks(d, (x + 50, y), "Jam berisiko genangan", huruf("ui", 500, 30), "tinta-balik", a_chip)
        x += 60
        kotak(d, (x, y + 4, 6, 20), "aman", a_chip)
        teks(d, (x + 20, y), "Jam aman", huruf("ui", 500, 30), "tinta-balik", a_chip)
        paragraf(d, (RAIL_X + 24, y + 70), "Selama 10 hari, kurva ini cocok dengan muka air terukur "
                 "stasiun pasut Semarang (r 0,78; RMSE 0,12 m). Itu kecocokan pasut, bukan akurasi genangan.",
                 huruf("ui", 400, 26), "tinta-3", 1740, tampak(t, 11.0, 14.9, 0.5))

    def adegan_peta(self, im, d, t):
        dt = self.d
        # 1) Pita pindah dari tengah ke bawah peta
        f_pindah = maju(t, 15.0, 1.1)
        rect = tuple(campur(a, b, f_pindah) for a, b in zip(PITA_BESAR, PITA_BAWAH))
        skala = campur(2.6, 1.55, f_pindah)

        # 2) Jam aktif pada Pita dan lapisan genangan
        indeks, jam_a, jam_b, f_jam = 0.0, 0, 0, 0.0
        if t >= 17.6:                                   # 00.00 -> 08.00, satu jam tiap 0,6875 detik
            k = min(8.0, (t - 17.6) / 0.6875)
            ke = min(8, int(math.floor(k)) + 1) if k < 8 else 8
            dari = ke - 1 if k < 8 else 8
            f_langkah = maju(k - dari, 0.0, 0.55) if k < 8 else 1.0
            indeks = dari + f_langkah if k < 8 else 8.0
            jam_a, jam_b, f_jam = dari, ke, f_langkah
        if t >= 37.3:                                   # 08.00 -> 13.00
            k = min(5.0, (t - 37.3) / 0.6)
            dari = 8 + min(4, int(math.floor(k)))
            ke = min(13, dari + 1)
            f_langkah = maju(k - (dari - 8), 0.0, 0.5) if k < 5 else 1.0
            if k >= 5:
                dari = ke = 13
            indeks = dari + f_langkah if k < 5 else 13.0
            jam_a, jam_b, f_jam = dari, ke, f_langkah

        # 3) Perbesaran ke kawasan Tawang-Terboyo
        f_zoom = maju(t, 28.0, 1.5)
        a_peta = tampak(t, 15.7, 44.5, 0.6)

        lapis = []
        if t >= 30.0:
            rute_abai = dt["rute"][("8", "rute_abai_rob")]["geometry"]["coordinates"]
            f = maju(t, 30.0, 1.6)
            lapis.append((self.peta_dekat.rute(rute_abai, LEBAR_ABAI, f, putus=True, warna="rute-abai"), 1.0))
        if 31.8 <= t:
            rute_08 = dt["rute"][("8", "rute_sadar_rob")]["geometry"]["coordinates"]
            f = maju(t, 31.8, 2.0)
            lapis.append((self.peta_dekat.rute(rute_08, LEBAR_RUTE, f, garis_luar="lambung-1"),
                          1.0 - maju(t, 37.3, 0.5)))
        if t >= 40.1:
            rute_13 = dt["rute"][("13", "rute_sadar_rob")]["geometry"]["coordinates"]
            lapis.append((self.peta_dekat.rute(rute_13, LEBAR_RUTE, 1.0, garis_luar="lambung-1"),
                          maju(t, 40.1, 0.5)))
        self.peta(im, t, a_peta, jam_a, jam_b, f_jam, f_zoom, lapis)

        a_kec = a_peta * tampak(t, 16.6, 28.4, 0.5)
        a_leg = a_peta * tampak(t, 22.6, 28.3, 0.5)
        self.label_kecamatan(d, a_kec, a_leg)
        self.titik_perjalanan(im, d, a_peta * tampak(t, 29.3, 44.5, 0.5))
        self.lencana(d, a_peta * tampak(t, 17.4, 44.5, 0.5))
        self.legenda(d, a_leg)
        self.atribusi(d, a_peta)
        gambar_pita(im, rect, dt, indeks, 1.0, 1.0, 1.0 - maju(t, 44.0, 0.5), skala)

        # 4) Rail kiri
        a = tampak(t, 16.0, 27.9, 0.6)
        self.label_rail(d, 88, "SEMARANG UTARA DAN TIMUR", a)
        y = self.judul_rail(d, 132, "Setiap ruas jalan, setiap jam.", a, 60)
        paragraf(d, (RAIL_X, y + 18), "19.394 ruas jalan, masing-masing dengan indeks kerentanan rob.",
                 huruf("ui", 400, 30), "tinta-3", RAIL_LEBAR, a, 1.25)
        a_baca = a * tampak(t, 17.5, None, 0.4)
        j = int(round(indeks)) if t < 37 else 8
        waktu = dt["potret"]["jam"][j]["waktu_utc"]
        self.label_rail(d, 470, "PADA PITA PASUT", a_baca)
        teks(d, (RAIL_X, 540), label_jam(waktu) + " WIB", huruf("data", 600, 40), "tinta-balik",
             a_baca, anchor="ls")
        teks(d, (RAIL_X, 640), angka(self.jumlah[j], 0), huruf("data", 600, 76), "tinta-balik",
             a_baca, anchor="ls")
        teks(d, (RAIL_X, 680), "ruas tergenang dalam model", huruf("ui", 500, 28), "tinta-3", a_baca)
        paragraf(d, (RAIL_X, 740), "Pukul 08.00 adalah pasang tertinggi hari itu. Pukul 13.00, "
                 "tidak ada ruas tergenang dalam model.", huruf("ui", 400, 28), "tinta-3", RAIL_LEBAR, a * tampak(t, 23.4, None, 0.5))

        self.rail_perjalanan(d, t)

    def rail_perjalanan(self, d, t):
        dt = self.d
        s8 = dt["skenario"]["8"]
        p_abai = dt["rute"][("8", "rute_abai_rob")]["properties"]
        p_sadar = dt["rute"][("8", "rute_sadar_rob")]["properties"]
        p_13 = dt["rute"][("13", "rute_sadar_rob")]["properties"]

        a = tampak(t, 29.0, 44.5, 0.6)
        self.label_rail(d, 88, "CONTOH PERJALANAN · MOTOR", a)
        a_08 = a * (1 - maju(t, 36.9, 0.4))
        a_geser = a * maju(t, 37.3, 0.4) * (1 - maju(t, 39.8, 0.4))
        a_13 = a * maju(t, 40.3, 0.4) * (1 - maju(t, 42.0, 0.4))
        self.judul_rail(d, 132, "Tawang ke Terboyo, pukul 08.00", a_08, 52)
        # copy.id.json pitaPasut.petunjuk, kalimat yang sama dengan aplikasi
        self.judul_rail(d, 132, "Geser untuk melihat kondisi jalan pada jam lain.", a_geser, 36)
        self.judul_rail(d, 132, "Tawang ke Terboyo, pukul 13.00", a_13, 52)

        # 08.00: dua rute, biaya menghindar, peringatan
        y = 300
        a1 = a_08 * maju(t, 30.3, 0.5)
        self._contoh_garis(d, (RAIL_X, y + 14), putus=True, alfa=a1)
        teks(d, (RAIL_X + 70, y), "Rute biasa", huruf("ui", 600, 30), "tinta-balik", a1)
        self.angka_satuan(d, (RAIL_X, y + 82), [(angka(p_abai["menit"]), "menit"),
                                                (angka(p_abai["jarak_km"], 2), "km")], a1, 38)
        teks(d, (RAIL_X, y + 96), f"{p_abai['ruas_tergenang']} ruas tergenang di jalur ini",
             huruf("ui", 400, 26), "tinta-3", a1)

        y = 460
        a2 = a_08 * maju(t, 32.1, 0.5)
        self._contoh_garis(d, (RAIL_X, y + 14), putus=False, alfa=a2)
        teks(d, (RAIL_X + 70, y), "Rute disarankan", huruf("ui", 600, 30), "tinta-balik", a2)
        self.angka_satuan(d, (RAIL_X, y + 82), [(angka(p_sadar["menit"]), "menit"),
                                                (angka(p_sadar["jarak_km"], 2), "km")], a2, 38)
        teks(d, (RAIL_X, y + 96), f"{p_sadar['ruas_tergenang']} ruas tergenang di jalur ini",
             huruf("ui", 400, 26), "tinta-3", a2)

        y = 640
        a3 = a_08 * maju(t, 34.0, 0.5)
        self.label_rail(d, y, "BIAYA MENGHINDAR", a3)
        self.angka_satuan(d, (RAIL_X, y + 70), [("+" + angka(s8["selisih"]["menit"]), "menit"),
                                                ("+" + angka(s8["selisih"]["km"], 2), "km")], a3, 44)
        a4 = a_08 * maju(t, 34.8, 0.5)
        isi = (f"Estimasi kedalaman maksimum {angka(s8['paparan']['kedalaman_maks_cm'])} cm "
               "pada rute ini, untuk keberangkatan 08.00.")
        fnt = huruf("ui", 500, 25)
        n_baris = len(bungkus(isi, fnt, RAIL_LEBAR - 36))
        kotak(d, (RAIL_X, 736, RAIL_LEBAR, n_baris * fnt.size * 1.2 + 28), "bahaya", a4, radius=3)
        paragraf(d, (RAIL_X + 18, 750), isi, fnt, "tinta-balik", RAIL_LEBAR - 36, a4, 1.2)

        # 13.00: rute sama dengan rute biasa
        y = 300
        a5 = a_13 * maju(t, 40.4, 0.5)
        self._contoh_garis(d, (RAIL_X, y + 14), putus=False, alfa=a5)
        teks(d, (RAIL_X + 70, y), "Rute disarankan", huruf("ui", 600, 30), "tinta-balik", a5)
        self.angka_satuan(d, (RAIL_X, y + 82), [(angka(p_13["menit"]), "menit"),
                                                (angka(p_13["jarak_km"], 2), "km")], a5, 38)
        paragraf(d, (RAIL_X, y + 104), "Tidak ada genangan di jalur ini pada jam tersebut. Rute "
                 "disarankan sama dengan rute biasa. Tidak perlu memutar.", huruf("ui", 400, 28),
                 "tinta-3", RAIL_LEBAR, a5, 1.25)

        # pesan penutup adegan
        a6 = a * maju(t, 42.3, 0.5)
        y = self.judul_rail(d, 132, "Dua pilihan, terlihat sebelum berangkat.", a6, 52)
        pilihan = (("08.00", f"Rute disarankan, +{angka(s8['selisih']['menit'])} menit"),
                   ("13.00", f"Rute biasa, {p_13['ruas_tergenang']} ruas tergenang"))
        for k, (jam, isi) in enumerate(pilihan):
            yy = y + 40 + k * 128
            teks(d, (RAIL_X, yy), jam, huruf("data", 600, 40), "tinta-balik", a6)
            paragraf(d, (RAIL_X, yy + 52), isi, huruf("ui", 500, 30), "tinta-balik", RAIL_LEBAR, a6, 1.2)

        paragraf(d, (RAIL_X, 880), "Skenario potret 26 September 2026. Waktu dan kedalaman dari "
                 "model, bukan pengamatan.", huruf("ui", 400, 22), "tinta-3", RAIL_LEBAR, a * 0.95, 1.25)

    def _contoh_garis(self, d, xy, putus: bool, alfa: float):
        x, y = xy
        if putus:
            for k in range(0, 54, 12):
                d.line([(x + k, y), (x + k + 6, y)], fill=rgba("rute-abai", alfa), width=3)
        else:
            d.line([(x, y), (x + 54, y)], fill=rgba("lambung-1", alfa), width=9)
            d.line([(x, y), (x + 54, y)], fill=rgba("rute", alfa), width=6)

    def adegan_cara_kerja(self, im, d, t):
        a = tampak(t, 44.6, 52.5, 0.5)
        self.label_rail(d, 110, "CARA KERJANYA", a)
        baris = [
            ("KAPAN", "Pasut harmonik memberi tinggi air tiap jam, 72 jam ke depan.", 45.0),
            ("DI MANA", "Indeks kerentanan tiap ruas dari elevasi relatif, jarak ke pantai, dan "
                        "penurunan tanah.", 46.2),
            ("LEWAT MANA", "Perutean di graf jalan OpenStreetMap, dengan ambang aman tiap moda.", 47.4),
        ]
        for k, (label, isi, masuk) in enumerate(baris):
            y = 200 + k * 190
            ab = a * maju(t, masuk, 0.6)
            self._ikon(d, k, (RAIL_X, y + 10), ab)
            teks(d, (RAIL_X + 330, y + 6), label, huruf("ui", 700, 26), "rute", ab, 0.08)
            paragraf(d, (RAIL_X + 330, y + 48), isi, huruf("ui", 500, 44), "tinta-balik", 1340, ab, 1.18)
        ah = a * maju(t, 48.9, 0.6)
        d.line([(RAIL_X, 800), (W - RAIL_X, 800)], fill=rgba("lambung-3", ah), width=2)
        paragraf(d, (RAIL_X, 836), "Model satelit Sentinel-1 sudah kami latih, lalu tidak kami pakai. "
                 "Angka dan alasannya terbuka di halaman Validasi.", huruf("ui", 400, 36), "tinta-3",
                 W - 2 * RAIL_X, ah, 1.25)

    def _ikon(self, d, jenis: int, xy, alfa: float):
        """Gambar kecil dari bahasa visual yang sama: kurva, ruas berair, dua rute."""
        x, y = xy
        if alfa <= 0.004:
            return
        if jenis == 0:
            halus = self.d["pasut_halus"]
            maks = np.abs(halus[:, 1]).max()
            pts = [(x + a / 71 * 280, y + 60 - b / maks * 44) for a, b in halus[::2]]
            d.line([(x, y + 60), (x + 280, y + 60)], fill=rgba("lambung-3", alfa), width=1)
            d.line(pts, fill=rgba("tinta-balik", alfa), width=3, joint="curve")
            d.line([(x + 8 / 71 * 280, y + 4), (x + 8 / 71 * 280, y + 116)], fill=rgba("rute", alfa), width=3)
        elif jenis == 1:
            for k, (warna, tebal) in enumerate((("tinta-2", 3), ("air-2", 7), ("air-3", 10))):
                yy = y + 22 + k * 36
                d.line([(x, yy), (x + 280, yy)], fill=rgba(warna, alfa), width=tebal)
                if warna == "air-3":
                    for tx in range(int(x) + 3, int(x) + 280, 10):
                        d.ellipse([tx - 1.4, yy - 3.4, tx + 1.4, yy - 0.6], fill=rgba("dek-1", alfa))
                        d.ellipse([tx + 5 - 1.4, yy + 0.6, tx + 5 + 1.4, yy + 3.4], fill=rgba("dek-1", alfa))
        else:
            for k in range(0, 280, 14):
                d.line([(x + k, y + 80), (x + k + 7, y + 80)], fill=rgba("rute-abai", alfa), width=4)
            pts = [(x, y + 80), (x + 60, y + 80), (x + 100, y + 24), (x + 180, y + 24), (x + 220, y + 80),
                   (x + 280, y + 80)]
            d.line(pts, fill=rgba("lambung-1", alfa), width=11, joint="curve")
            d.line(pts, fill=rgba("rute", alfa), width=7, joint="curve")
            for px, warna in ((x, "rute"), (x + 280, "aman")):
                d.ellipse([px - 12, y + 68, px + 12, y + 92], fill=rgba("lambung-1", alfa),
                          outline=rgba("rute", alfa), width=3)
                d.ellipse([px - 5, y + 75, px + 5, y + 85], fill=rgba(warna, alfa))

    def adegan_penutup(self, im, d, t):
        a = tampak(t, 52.6, 60.0, 0.9)
        naik = (1 - maju(t, 52.6, 0.9)) * 14
        teks(d, (RAIL_X, 250 + naik), "PASANG SURUT", huruf("ui", 700, 150), "tinta-balik", a, 0.02)
        a2 = a * maju(t, 53.2, 0.6)
        teks(d, (RAIL_X, 440), "Tahu jalan mana yang terendam, sebelum berangkat.", huruf("ui", 500, 50),
             "tinta-balik", a2)
        teks(d, (RAIL_X, 510), "Perutean sadar rob untuk Semarang pesisir.", huruf("ui", 400, 36),
             "tinta-3", a2)

        a3 = a * maju(t, 53.9, 0.6)
        qw, qh = self.qr.size
        x, y = W - RAIL_X - qw - 48 - 56, 230
        kotak(d, (x, y, qw + 48, qh + 48), "dek-1", a3, radius=6)
        tempel(im, self.qr, (x + 24, y + 24), a3)
        teks(d, (x + (qw + 48) / 2, y + qh + 92), "Coba di ponsel", huruf("ui", 600, 34), "tinta-balik",
             a3, anchor="ma")
        teks(d, (x + (qw + 48) / 2, y + qh + 142), "pasang-surut.vercel.app/app", huruf("data", 400, 26),
             "tinta-3", a3, anchor="ma")

        a4 = a * maju(t, 54.6, 0.6)
        d.line([(RAIL_X, 760), (RAIL_X + 1000, 760)], fill=rgba("lambung-3", a4), width=2)
        teks(d, (RAIL_X, 790), "trio la albiceleste · Institut Teknologi Sepuluh Nopember",
             huruf("ui", 600, 32), "tinta-balik", a4)
        teks(d, (RAIL_X, 840), "Diponegoro Software Development Competition · ANFORCOM 2026",
             huruf("ui", 400, 28), "tinta-3", a4)
        teks(d, (RAIL_X, 930), "Alat bantu perencanaan perjalanan, bukan peringatan dini resmi.",
             huruf("ui", 400, 24), "tinta-3", a * maju(t, 55.2, 0.6))


# ══════════════════════════════════════════════════════════════════════════
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--cuplikan", default=None, help="detik dipisah koma; simpan PNG saja")
    a = p.parse_args()

    video = Video()
    if a.cuplikan:
        for s in a.cuplikan.split(","):
            t = float(s)
            berkas = FOLDER / f"cuplikan_{t:05.1f}.png"
            video.bingkai(t).save(berkas)
            print("tersimpan:", berkas.relative_to(AKAR))
        return 0

    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    perintah = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
                "-preset", "slow", "-crf", "18", "-tune", "animation", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", str(KELUARAN)]
    proses = subprocess.Popen(perintah, stdin=subprocess.PIPE)
    total = int(DURASI * FPS)
    mulai = time.perf_counter()
    for i in range(total):
        proses.stdin.write(video.bingkai(i / FPS).tobytes())
        if i % 150 == 0:
            lewat = time.perf_counter() - mulai
            print(f"bingkai {i}/{total}  {lewat:.0f} s", flush=True)
    proses.stdin.close()
    if proses.wait() != 0:
        raise SystemExit("ffmpeg gagal")
    print(f"selesai: {KELUARAN.relative_to(AKAR)}  "
          f"{KELUARAN.stat().st_size / 1e6:.1f} MB  {time.perf_counter() - mulai:.0f} detik")
    return 0


if __name__ == "__main__":
    sys.exit(main())
