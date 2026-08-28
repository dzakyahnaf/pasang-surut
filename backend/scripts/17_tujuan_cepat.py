"""Kumpulkan titik tujuan cepat dari OpenStreetMap, sekali, lalu simpan.

    python -m scripts.17_tujuan_cepat

KENAPA DIAMBIL DARI OSM, BUKAN DITULIS TANGAN.

Empat tujuan yang diminta PLAN.md bagian 10.7 — Pelabuhan Tanjung Emas,
Stasiun Tawang, kawasan industri Terboyo, dan rumah sakit terdekat — mudah
sekali ditulis koordinatnya dari ingatan. Itu justru masalahnya: koordinat
yang ditulis dari ingatan tidak bisa diperiksa siapa pun, dan meleset
beberapa ratus meter sudah cukup untuk menempelkan tombol ke ruas jalan yang
salah.

Diambil dari OSM sekali, disimpan ke berkas, lalu dipakai luring. Pola yang
sama dengan garis pantai dan batas kecamatan.

Titik yang tersimpan sudah DILEKATKAN ke simpul jalan terdekat, sehingga
tombol tujuan cepat tidak pernah mengembalikan galat "terlalu jauh dari
jalan" yang membingungkan pengguna.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from app import config, db

BERKAS = config.DIR_DATA_OLAHAN / "tujuan_cepat.geojson"

# Nama yang dicari di OSM, beserta label yang ditampilkan di antarmuka.
# Pencarian memakai kata kunci karena penamaan OSM tidak seragam.
DICARI = [
    {"kunci": "pelabuhan", "kata": ["tanjung emas", "tanjungemas"],
     "label": "Pelabuhan Tanjung Emas", "ikon": "pelabuhan",
     "tag": {"landuse": "port", "amenity": "ferry_terminal",
             "harbour": "yes", "industrial": "port"}},
    {"kunci": "stasiun", "kata": ["tawang"],
     "label": "Stasiun Semarang Tawang", "ikon": "stasiun",
     "tag": {"railway": "station"}},
    {"kunci": "industri", "kata": ["terboyo"],
     "label": "Kawasan Industri Terboyo", "ikon": "industri",
     "tag": {"landuse": "industrial"}},
    {"kunci": "rumah_sakit", "kata": [],
     "label": None, "ikon": "rumah_sakit",
     "tag": {"amenity": "hospital"}},
]


def kumpulkan() -> list[dict]:
    import osmnx as ox
    import shapely.geometry

    lon0, lat0, lon1, lat1 = config.bbox_aoi()
    lebar = 0.02
    kotak = shapely.geometry.box(lon0 - lebar, lat0 - lebar,
                                 lon1 + lebar, lat1 + lebar)

    hasil: list[dict] = []
    for cari in DICARI:
        print(f"  mencari {cari['kunci']} ...", end="", flush=True)
        try:
            gdf = ox.features.features_from_polygon(kotak, tags=cari["tag"])
        except Exception as e:
            print(f" gagal ({type(e).__name__})")
            continue
        if gdf.empty:
            print(" tidak ada")
            continue

        kolom_nama = "name" if "name" in gdf.columns else None
        calon = []
        for _, baris in gdf.iterrows():
            nama = str(baris[kolom_nama]) if kolom_nama else ""
            if nama in ("nan", "None"):
                nama = ""
            g = baris.geometry
            if g is None or g.is_empty:
                continue
            titik = g if g.geom_type == "Point" else g.representative_point()
            if not (lon0 <= titik.x <= lon1 and lat0 <= titik.y <= lat1):
                continue        # di luar AOI, tidak berguna sebagai tujuan
            cocok = (not cari["kata"]
                     or any(k in nama.lower() for k in cari["kata"]))
            if cocok:
                calon.append((nama, titik.x, titik.y))

        if not calon:
            print(" tidak ada yang cocok di dalam AOI")
            continue
        nama, x, y = calon[0]
        hasil.append({
            "kunci": cari["kunci"],
            "label": cari["label"] or nama or cari["kunci"],
            "ikon": cari["ikon"],
            "nama_osm": nama,
            "lon": round(float(x), 6),
            "lat": round(float(y), 6),
            "kandidat": len(calon),
        })
        print(f" ok: {nama or '(tanpa nama)'} ({len(calon)} kandidat)")
    return hasil


def lekatkan_ke_jalan(titik: list[dict]) -> list[dict]:
    """Geser tiap titik ke simpul jalan terdekat, supaya rute selalu bisa."""
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            for t in titik:
                kur.execute(
                    """
                    SELECT ST_X(p.g), ST_Y(p.g),
                           ST_Distance(p.g::geography,
                                       ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
                    FROM (
                        SELECT ST_StartPoint(geom) AS g FROM ruas_jalan
                        UNION ALL
                        SELECT ST_EndPoint(geom) AS g FROM ruas_jalan
                    ) p
                    ORDER BY p.g <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    LIMIT 1
                    """,
                    (t["lon"], t["lat"], t["lon"], t["lat"]),
                )
                x, y, jarak = kur.fetchone()
                t["lon_asli"], t["lat_asli"] = t["lon"], t["lat"]
                t["lon"], t["lat"] = round(float(x), 6), round(float(y), 6)
                t["geser_m"] = round(float(jarak), 1)
                print(f"  {t['label']:<28} digeser {t['geser_m']:>6.1f} m "
                      "ke simpul jalan terdekat")
    return titik


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    print("mengumpulkan tujuan cepat dari OpenStreetMap ...")
    titik = kumpulkan()
    if not titik:
        raise SystemExit("Tidak ada satu pun tujuan yang ditemukan.")
    print()
    print("melekatkan ke simpul jalan terdekat ...")
    titik = lekatkan_ke_jalan(titik)

    BERKAS.write_text(json.dumps({
        "type": "FeatureCollection",
        "_catatan": ("Tujuan cepat, diambil sekali dari OpenStreetMap lalu "
                     "dilekatkan ke simpul jalan terdekat. Dipakai luring; "
                     "tidak ada panggilan OSM saat aplikasi berjalan."),
        "diambil": datetime.now(timezone.utc).isoformat(),
        "features": [{
            "type": "Feature",
            "properties": {k: v for k, v in t.items()
                           if k not in ("lon", "lat")},
            "geometry": {"type": "Point", "coordinates": [t["lon"], t["lat"]]},
        } for t in titik],
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS.name} ({len(titik)} tujuan)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
