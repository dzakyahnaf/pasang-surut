"""Isi kolom fitur di tabel `ruas_jalan`: elevasi, jarak pantai, subsidensi.

    python -m scripts.05_isi_fitur_ruas          # dijalankan dari backend/

Ketiganya adalah fitur masukan model genangan di M4. Skrip ini menyiapkannya
lebih dulu supaya pelatihan model tinggal membaca tabel.

TIGA HAL YANG PATUT DIPERHATIKAN.

1. Berkas DEMNAS TIDAK membawa CRS. rasterio melaporkan CRS None walau
   koordinatnya jelas derajat WGS84. CRS ditetapkan eksplisit di sini.
   Kalau dilewatkan, pengambilan sampel gagal atau diam-diam salah.

2. Jarak pantai dihitung di EPSG:32749, bukan di derajat. Alasannya sama
   seperti panjang ruas: derajat bukan meter.

3. Laju subsidensi tersedia hanya per KECAMATAN, bukan per ruas. Nilainya
   dipetakan lewat kecamatan tempat titik tengah ruas berada. Daya pisahnya
   kasar dan itu wajib disebut di docs/batasan.md.
"""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import rasterio
from rasterio.errors import RasterioIOError

from app import config, db

BERKAS_DEM = config.DIR_DATA_MENTAH / "DEMNAS_1409-22_v1.0.tif"
BERKAS_SUBSIDENSI = config.DIR_DATA_REFERENSI / "laju_subsidensi.json"
BERKAS_GARIS_PANTAI = config.DIR_DATA_OLAHAN / "garis_pantai.geojson"

# DEMNAS memakai koordinat geografis WGS84 tetapi tidak menuliskannya di
# dalam berkas. Ditetapkan di sini, sekali, dan tidak ditebak di tempat lain.
CRS_DEM = "EPSG:4326"


# ══════════════════════════════════════════════════════════════════════════
# ELEVASI
# ══════════════════════════════════════════════════════════════════════════
def ambil_elevasi(titik: list[tuple[float, float]]) -> np.ndarray:
    """Sampling DEMNAS pada titik tengah tiap ruas. Kembalikan meter."""
    if not BERKAS_DEM.exists():
        raise SystemExit(
            f"Berkas DEM tidak ada di {BERKAS_DEM}.\n"
            "Unduh tile 1409-22 sesuai docs/panduan_akun_dan_data.md bagian C."
        )
    try:
        r = rasterio.open(BERKAS_DEM)
    except RasterioIOError as e:
        raise SystemExit(f"Gagal membuka DEM: {e}")

    with r:
        if r.crs is None:
            print(f"  DEM tidak membawa CRS, ditetapkan {CRS_DEM}")
        b = r.bounds
        print(f"  cakupan DEM: bujur {b.left:.4f}..{b.right:.4f} "
              f"lintang {b.bottom:.4f}..{b.top:.4f}")
        nilai = np.array(
            [v[0] for v in r.sample(titik)], dtype=np.float64
        )
    # NaN adalah nodata pada berkas ini.
    return nilai


# ══════════════════════════════════════════════════════════════════════════
# JARAK KE GARIS PANTAI
# ══════════════════════════════════════════════════════════════════════════
def muat_garis_pantai():
    """Muat garis pantai dari berkas yang sudah diunduh sekali.

    Garis pantai diambil dari OpenStreetMap lewat OSMnx SATU KALI oleh
    fungsi unduh_garis_pantai(), lalu disimpan. Aturan repo melarang
    memanggil Overpass saat runtime; penyiapan data bukan runtime, dan
    hasilnya disimpan supaya tidak diambil dua kali.
    """
    import shapely.geometry

    if not BERKAS_GARIS_PANTAI.exists():
        unduh_garis_pantai()
    isi = json.loads(BERKAS_GARIS_PANTAI.read_text(encoding="utf-8"))
    geometri = [shapely.geometry.shape(f["geometry"]) for f in isi["features"]]
    if not geometri:
        raise SystemExit("Berkas garis pantai kosong.")
    return geometri


def unduh_garis_pantai() -> None:
    """Ambil garis pantai OSM di sekitar AOI, sekali saja, lalu simpan."""
    import osmnx as ox
    import shapely.geometry

    # Kotak diperlebar dari AOI supaya garis pantai tidak terpotong tepat di
    # tepi wilayah kerja. Ruas di tepi utara butuh garis pantai yang menerus.
    lon0, lat0, lon1, lat1 = config.bbox_aoi()
    lebar = 0.15
    kotak = shapely.geometry.box(
        lon0 - lebar, lat0 - lebar, lon1 + lebar, lat1 + lebar
    )
    print("  mengunduh garis pantai dari OpenStreetMap, sekali saja ...")
    gdf = ox.features.features_from_polygon(kotak, tags={"natural": "coastline"})
    if gdf.empty:
        raise SystemExit("OSM tidak mengembalikan garis pantai di sekitar AOI.")

    fitur = [
        {"type": "Feature", "properties": {},
         "geometry": shapely.geometry.mapping(g)}
        for g in gdf.geometry if g is not None and not g.is_empty
    ]
    BERKAS_GARIS_PANTAI.write_text(
        json.dumps({"type": "FeatureCollection", "features": fitur},
                   ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"  tersimpan: {BERKAS_GARIS_PANTAI.name} ({len(fitur)} garis)")


def hitung_jarak_pantai(titik: list[tuple[float, float]]) -> np.ndarray:
    """Jarak tiap titik ke garis pantai terdekat, dalam METER.

    Diproyeksikan ke EPSG:32749 lebih dulu. Menghitung jarak di derajat
    akan menghasilkan angka tanpa arti fisik, karena satu derajat bujur dan
    satu derajat lintang tidak sama panjang.
    """
    import pyproj
    import shapely.ops
    from shapely.geometry import MultiLineString, Point

    garis = muat_garis_pantai()
    ke_metrik = pyproj.Transformer.from_crs(
        config.CRS_SIMPAN, config.CRS_METRIK, always_xy=True
    ).transform
    print(f"  proyeksi {config.CRS_SIMPAN} -> {config.CRS_METRIK} untuk jarak")

    # MultiLineString hanya menerima LineString, jadi yang bersarang dibongkar.
    bagian = []
    for g in garis:
        bagian.extend(g.geoms if g.geom_type == "MultiLineString" else [g])
    pantai = MultiLineString([shapely.ops.transform(ke_metrik, g) for g in bagian])

    jarak = np.empty(len(titik), dtype=np.float64)
    for i, (lon, lat) in enumerate(titik):
        jarak[i] = pantai.distance(
            shapely.ops.transform(ke_metrik, Point(lon, lat))
        )
    return jarak


# ══════════════════════════════════════════════════════════════════════════
# LAJU SUBSIDENSI
# ══════════════════════════════════════════════════════════════════════════
def hitung_subsidensi(titik: list[tuple[float, float]]) -> np.ndarray:
    """Laju subsidensi per ruas, dipetakan dari kecamatan.

    Sumbernya melaporkan per kecamatan. Batas kecamatan tidak tersedia di
    repo, jadi pemetaan dilakukan lewat kotak pembatas kecamatan yang
    diambil dari OpenStreetMap sekali, sama seperti garis pantai.
    """
    d = json.loads(BERKAS_SUBSIDENSI.read_text(encoding="utf-8"))
    tabel = d["kecamatan"]
    berkas_batas = config.DIR_DATA_OLAHAN / "kecamatan.geojson"

    if not berkas_batas.exists():
        import osmnx as ox
        import shapely.geometry

        print("  mengunduh batas kecamatan dari OpenStreetMap, sekali saja ...")
        fitur = []
        for nama in tabel:
            try:
                g = ox.geocode_to_gdf(f"Kecamatan {nama}, Kota Semarang, Indonesia")
            except Exception as e:
                print(f"    {nama}: gagal ({type(e).__name__})")
                continue
            fitur.append({
                "type": "Feature",
                "properties": {"kecamatan": nama},
                "geometry": shapely.geometry.mapping(g.geometry.iloc[0]),
            })
            print(f"    {nama}: ok")
        berkas_batas.write_text(
            json.dumps({"type": "FeatureCollection", "features": fitur},
                       ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    import shapely.geometry
    from shapely.strtree import STRtree

    isi = json.loads(berkas_batas.read_text(encoding="utf-8"))
    poligon, nama_poligon = [], []
    for f in isi["features"]:
        poligon.append(shapely.geometry.shape(f["geometry"]))
        nama_poligon.append(f["properties"]["kecamatan"])
    pohon = STRtree(poligon)

    hasil = np.full(len(titik), np.nan, dtype=np.float64)
    for i, (lon, lat) in enumerate(titik):
        p = shapely.geometry.Point(lon, lat)
        for idx in pohon.query(p):
            if poligon[idx].contains(p):
                hasil[i] = tabel[nama_poligon[idx]]["rata_rata"]
                break
    return hasil


# ══════════════════════════════════════════════════════════════════════════
def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--lewati-subsidensi", action="store_true")
    argumen = pengurai.parse_args()

    with db.koneksi() as kon:
        baris = db.RepositoriRuas(kon).id_dan_titik_tengah()
    if not baris:
        print("Tabel ruas_jalan kosong. Jalankan skrip 02 lebih dulu.")
        return 1

    edge_id = [b[0] for b in baris]
    titik = [(b[1], b[2]) for b in baris]
    print(f"ruas: {len(titik):,}\n")

    print("elevasi dari DEMNAS")
    elevasi = ambil_elevasi(titik)
    sah = np.isfinite(elevasi)
    print(f"  valid {int(sah.sum()):,} dari {len(elevasi):,}")
    print(f"  min {np.nanmin(elevasi):.2f} m, median {np.nanmedian(elevasi):.2f} m, "
          f"maks {np.nanmax(elevasi):.2f} m\n")

    print("jarak ke garis pantai")
    jarak = hitung_jarak_pantai(titik)
    print(f"  min {jarak.min():,.0f} m, median {np.median(jarak):,.0f} m, "
          f"maks {jarak.max():,.0f} m\n")

    subsidensi = np.full(len(titik), np.nan)
    if not argumen.lewati_subsidensi:
        print("laju subsidensi per kecamatan")
        subsidensi = hitung_subsidensi(titik)
        cocok = np.isfinite(subsidensi)
        print(f"  ruas dalam kecamatan yang punya data: {int(cocok.sum()):,}")
        if cocok.any():
            print(f"  min {np.nanmin(subsidensi):.1f}, "
                  f"maks {np.nanmax(subsidensi):.1f} cm/tahun\n")

    print("menulis ke database ...")
    with db.koneksi() as kon:
        db.RepositoriRuas(kon).perbarui_fitur(
            list(zip(
                [None if not np.isfinite(x) else float(x) for x in elevasi],
                [float(x) for x in jarak],
                [None if not np.isfinite(x) else float(x) for x in subsidensi],
                edge_id,
            ))
        )

    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                "SELECT COUNT(*) FILTER (WHERE elevasi_m IS NOT NULL),"
                "       COUNT(*) FILTER (WHERE jarak_pantai_m IS NOT NULL),"
                "       COUNT(*) FILTER (WHERE laju_subsidensi_cm_thn IS NOT NULL)"
                " FROM ruas_jalan"
            )
            a, b, c = kur.fetchone()
    print(f"  elevasi terisi     : {a:,}")
    print(f"  jarak pantai terisi: {b:,}")
    print(f"  subsidensi terisi  : {c:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
