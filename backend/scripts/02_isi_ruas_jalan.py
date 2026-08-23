"""Ubah graf jalan jadi baris tabel `ruas_jalan`.

    python -m scripts.02_isi_ruas_jalan          # dijalankan dari backend/

Membaca data/processed/graph.graphml. TIDAK menyentuh jaringan sama sekali.
Jalankan skrip 01 lebih dulu kalau berkas graf belum ada.

Dua hal penting yang terjadi di sini, dan keduanya sering salah dipahami:

1. PANJANG DIHITUNG DI EPSG:32749, GEOMETRI DISIMPAN DI EPSG:4326.
   Ini bukan pemborosan, ini keharusan. Penjelasannya ada di komentar
   fungsi hitung_panjang_meter().

2. RUAS DUA ARAH DISIMPAN SATU BARIS, BUKAN DUA.
   Penjelasannya ada di komentar fungsi ke_ruas_tunggal().
"""

from __future__ import annotations

import argparse
import json
import sys

import geopandas as gpd
import osmnx as ox

from app import config, db

BERKAS_GRAF = config.DIR_DATA_OLAHAN / "graph.graphml"
BERKAS_GEOJSON = config.DIR_DATA_OLAHAN / "ruas_jalan.geojson"

# Koordinat dibulatkan ke 5 angka desimal sebelum diekspor ke GeoJSON.
# Satu derajat bujur di Semarang sekitar 110 km, jadi 5 desimal setara
# sekitar 1,1 meter. Jauh lebih teliti daripada yang bisa dibedakan mata di
# layar peta, tetapi memangkas ukuran berkas secara drastis.
DESIMAL_KOORDINAT = 5


def muat_graf():
    """Baca graf dari berkas. Tidak ada panggilan Overpass di sini."""
    if not BERKAS_GRAF.exists():
        raise FileNotFoundError(
            f"Graf belum ada di {BERKAS_GRAF}. "
            "Jalankan dulu: python -m scripts.01_bangun_graf"
        )
    print(f"membaca {BERKAS_GRAF.name} ...")
    return ox.load_graphml(BERKAS_GRAF)


def ke_ruas_tunggal(graf):
    """Ubah graf berarah jadi satu baris per ruas jalan fisik.

    KENAPA INI PERLU. OSMnx mengembalikan graf BERARAH. Jalan dua arah
    muncul dua kali di graf: sekali sebagai (u -> v) dan sekali sebagai
    (v -> u). Keduanya menggambarkan aspal yang sama persis.

    Kalau keduanya dimasukkan ke tabel, akibatnya tiga hal, semuanya buruk:
      - Panjang jaringan terhitung dua kali lipat
      - Peta menggambar dua garis bertumpuk di atas aspal yang sama,
        sehingga warna kedalaman terlihat lebih pekat dari seharusnya
      - Tabel prediksi_genangan ikut membengkak dua kali lipat, padahal
        satu jam sudah berisi satu baris untuk setiap ruas

    to_undirected() menggabungkan pasangan bolak-balik itu jadi satu sisi.
    Jalan satu arah tidak punya pasangan, jadi ia lolos apa adanya dan
    ditandai lewat kolom satu_arah. Mesin routing nanti membaca kolom itu
    untuk tahu arah mana yang boleh dilalui.
    """
    graf_tak_berarah = ox.convert.to_undirected(graf)
    print(
        f"sisi berarah {graf.number_of_edges():,} "
        f"-> ruas fisik {graf_tak_berarah.number_of_edges():,}"
    )
    return graf_tak_berarah


def hitung_panjang_meter(gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Hitung panjang tiap ruas dalam meter.

    KENAPA HARUS DIPROYEKSIKAN DULU. Geometri jalan tersimpan di EPSG:4326,
    yang satuannya DERAJAT bujur dan lintang, bukan meter. Menghitung
    panjang garis langsung di derajat menghasilkan angka tanpa arti fisik,
    karena satu derajat bujur dan satu derajat lintang tidak sama panjang,
    dan rasionya berubah mengikuti lintang.

    EPSG:32749 adalah UTM zona 49 belahan selatan. Satuannya METER. Semarang
    di bujur 110,4 derajat berada di dalam zona 49, yang membentang dari 108
    sampai 114 derajat bujur timur, jadi distorsinya kecil di wilayah kita.

    Jadi urutannya: proyeksikan ke 32749, ukur panjangnya, ambil angkanya
    saja. Geometri yang DISIMPAN tetap yang asli di 4326, karena itu yang
    dimengerti PostGIS, GeoJSON, dan MapLibre.
    """
    gdf_metrik = gdf.to_crs(config.EPSG_METRIK)
    print(f"proyeksi {config.CRS_SIMPAN} -> {config.CRS_METRIK} untuk mengukur panjang")
    return gdf_metrik.length


def _teks_pertama(nilai, bawaan=None):
    """OSM kadang menaruh beberapa nilai pada satu tag. Ambil yang pertama.

    Contoh nyata: satu ruas hasil penyederhanaan bisa membawa
    name = ['Jl. Kaligawe Raya', 'Jl. Raya Kaligawe'] karena dua ruas OSM
    dengan nama berbeda digabung jadi satu.

    Nilai kosong dikembalikan sebagai None, BUKAN sebagai teks. Sebagian
    besar ruas jalan kampung di OSM memang tidak punya tag name, dan pandas
    mewakili itu sebagai NaN. Kalau NaN diubah jadi teks apa adanya, yang
    tersimpan di database adalah string "nan" dan itulah yang akan terbaca
    juri sebagai nama jalan di peta.
    """
    if nilai is None:
        return bawaan
    if isinstance(nilai, list):
        nilai = nilai[0] if nilai else None
        if nilai is None:
            return bawaan
    # NaN adalah satu-satunya nilai yang tidak sama dengan dirinya sendiri.
    if isinstance(nilai, float) and nilai != nilai:
        return bawaan
    teks = str(nilai).strip()
    return teks if teks and teks.lower() != "nan" else bawaan


def _ke_boolean(nilai) -> bool:
    if isinstance(nilai, list):
        nilai = nilai[0] if nilai else False
    if isinstance(nilai, bool):
        return nilai
    return str(nilai).strip().lower() in {"true", "yes", "1"}


def siapkan_baris(gdf: gpd.GeoDataFrame) -> list[tuple]:
    """Susun baris siap sisip sesuai urutan kolom RepositoriRuas."""
    baris = []
    for (u, v, _kunci), data in gdf.iterrows():
        geometri = data.geometry
        if geometri is None or geometri.is_empty:
            continue

        # EWKT membawa kode SRID di dalam teksnya, jadi tidak mungkin
        # geometri masuk ke database tanpa sistem koordinat yang jelas.
        ewkt = f"SRID={config.EPSG_SIMPAN};{geometri.wkt}"

        baris.append((
            int(u),
            int(v),
            _teks_pertama(data.get("name")),
            _teks_pertama(data.get("highway"), "tidak diketahui"),
            float(data["panjang_m"]),
            float(data["kecepatan_kmh"]),
            _ke_boolean(data.get("oneway")),
            ewkt,
        ))
    return baris


def tulis_geojson(gdf: gpd.GeoDataFrame) -> None:
    """Ekspor jaringan jalan ke GeoJSON sebagai jalur cadangan offline.

    Berkas ini dipakai lapisan API kalau database belum tersedia, misalnya
    di laptop anggota tim yang belum menyiapkan Supabase. Dengan begitu peta
    tetap bisa dibuka tanpa database sama sekali.
    """
    fitur = []
    for (u, v, _kunci), data in gdf.iterrows():
        geometri = data.geometry
        if geometri is None or geometri.is_empty:
            continue
        koordinat = [
            [round(x, DESIMAL_KOORDINAT), round(y, DESIMAL_KOORDINAT)]
            for x, y in geometri.coords
        ]
        fitur.append({
            "type": "Feature",
            "properties": {
                "osm_u": int(u),
                "osm_v": int(v),
                "nama": _teks_pertama(data.get("name")),
                "jenis": _teks_pertama(data.get("highway"), "tidak diketahui"),
                "panjang_m": round(float(data["panjang_m"]), 1),
                "kecepatan_kmh": round(float(data["kecepatan_kmh"]), 1),
                "satu_arah": _ke_boolean(data.get("oneway")),
            },
            "geometry": {"type": "LineString", "coordinates": koordinat},
        })

    isi = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": fitur,
    }
    BERKAS_GEOJSON.write_text(
        json.dumps(isi, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    ukuran_mb = BERKAS_GEOJSON.stat().st_size / 1_048_576
    print(f"cadangan offline: {BERKAS_GEOJSON.name}  ({ukuran_mb:.1f} MB, {len(fitur):,} ruas)")


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument(
        "--tanpa-database",
        action="store_true",
        help="hanya tulis GeoJSON, lewati penyisipan ke database",
    )
    argumen = pengurai.parse_args()

    graf = muat_graf()
    graf = ke_ruas_tunggal(graf)

    # Kecepatan bebas hambatan. OSMnx membaca tag maxspeed dari OSM bila ada.
    # Ruas tanpa tag maxspeed diisi rata-rata jenis jalan yang sama DI DALAM
    # AOI INI, bukan angka karangan dari luar. Ini imputasi, bukan pengukuran,
    # dan wajib disebut sebagai asumsi di docs/batasan.md.
    graf = ox.routing.add_edge_speeds(graf)

    gdf = ox.convert.graph_to_gdfs(graf, nodes=False, edges=True)
    print(f"CRS geometri dari graf: {gdf.crs}")

    gdf["panjang_m"] = hitung_panjang_meter(gdf)
    gdf["kecepatan_kmh"] = gdf["speed_kph"].astype(float)

    # Pemeriksaan kewarasan. OSMnx sendiri sudah menghitung kolom `length`
    # memakai jarak lingkaran besar di atas bola bumi. Angka kita lewat
    # proyeksi UTM seharusnya sangat dekat. Selisih besar berarti ada yang
    # keliru pada pemilihan zona UTM.
    if "length" in gdf.columns:
        selisih = (gdf["panjang_m"] - gdf["length"].astype(float)).abs()
        relatif = (selisih / gdf["length"].astype(float).clip(lower=0.01)).median()
        print(f"beda median terhadap perhitungan OSMnx: {relatif * 100:.3f} persen")

    total_km = gdf["panjang_m"].sum() / 1000
    print(f"panjang jaringan: {total_km:,.1f} km")

    tulis_geojson(gdf)

    if argumen.tanpa_database:
        print("dilewati: penyisipan ke database (--tanpa-database)")
        return 0

    baris = siapkan_baris(gdf)
    print(f"menyisipkan {len(baris):,} ruas ke database ...")

    with db.koneksi() as kon:
        repo = db.RepositoriRuas(kon)
        repo.kosongkan()
        repo.sisipkan_banyak(baris)

    with db.koneksi() as kon:
        repo = db.RepositoriRuas(kon)
        print(f"\nruas_jalan berisi   : {repo.hitung():,} baris")
        print(f"panjang total       : {repo.panjang_total_km():,.1f} km")
    return 0


if __name__ == "__main__":
    sys.exit(main())
