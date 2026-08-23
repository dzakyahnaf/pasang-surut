"""Unduh jaringan jalan AOI dari OpenStreetMap, simpan sebagai GraphML.

    python -m scripts.01_bangun_graf            # dijalankan dari backend/
    python -m scripts.01_bangun_graf --paksa    # timpa graf yang sudah ada

SKRIP INI DIJALANKAN SEKALI. Hasilnya dipakai selamanya.

Kenapa sekali saja: OSMnx mengambil data lewat Overpass API, server publik
gratis yang membatasi laju permintaan dan kadang tidak merespons. Kalau
aplikasi memanggil Overpass saat runtime, demo di depan juri bergantung pada
server yang tidak kita kendalikan. Karena itu graf diunduh sekali, disimpan ke
berkas, dan seluruh proses berikutnya hanya membaca berkas itu.

Aturan repo: Overpass TIDAK PERNAH dipanggil saat runtime.
"""

from __future__ import annotations

import argparse
import sys
import time

import networkx as nx
import osmnx as ox
from shapely.geometry import shape

from app import config

# Nama berkas keluaran. Modul lain mengacu ke sini, jangan menulis ulang path.
BERKAS_GRAF = config.DIR_DATA_OLAHAN / "graph.graphml"

# Tipe jaringan "drive" berarti hanya jalan yang bisa dilalui kendaraan
# bermotor. Jalan setapak, jalur sepeda, dan tangga tidak ikut. MVP hanya
# melayani moda motor dan mobil, jadi mengambil selain "drive" hanya
# memperbesar graf tanpa dipakai.
TIPE_JARINGAN = "drive"


def bangun_graf() -> nx.MultiDiGraph:
    """Ambil jaringan jalan di dalam poligon AOI dari OpenStreetMap."""
    # Poligon AOI disimpan sebagai dict GeoJSON di data/aoi/. Shapely
    # mengubahnya jadi objek geometri yang dimengerti OSMnx.
    #
    # Koordinatnya dalam EPSG:4326, yaitu derajat bujur dan lintang. Ini
    # memang yang diminta OSMnx: Overpass API bekerja dalam bujur-lintang,
    # bukan meter. Jadi di tahap ini TIDAK ADA proyeksi sama sekali.
    # Proyeksi ke meter baru dibutuhkan saat menghitung panjang ruas, dan
    # itu terjadi di skrip 02.
    poligon = shape(config.geometri_aoi())

    print(f"AOI    : {config.BERKAS_AOI.name}")
    print(f"bbox   : {config.bbox_aoi()}  (bujur_min, lintang_min, bujur_maks, lintang_maks)")
    print(f"CRS    : {config.CRS_SIMPAN} — derajat, bukan meter")
    print(f"jaringan: {TIPE_JARINGAN}")
    print("mengunduh dari Overpass, ini bisa memakan waktu satu sampai beberapa menit...")

    mulai = time.perf_counter()
    # graph_from_polygon mengembalikan MultiDiGraph:
    #   - Di = berarah. Jalan satu arah hanya punya sisi ke satu jurusan.
    #   - Multi = boleh ada lebih dari satu sisi antara pasangan simpul yang
    #     sama, misalnya dua jalan sejajar yang menghubungkan persimpangan
    #     yang sama.
    # truncate_by_edge=True mempertahankan ruas yang salah satu ujungnya
    # sedikit di luar AOI. Tanpa ini, jalan yang menyentuh tepi AOI akan
    # terpotong dan graf jadi terputus di pinggir wilayah.
    graf = ox.graph_from_polygon(
        poligon,
        network_type=TIPE_JARINGAN,
        simplify=True,
        truncate_by_edge=True,
        retain_all=False,
    )
    durasi = time.perf_counter() - mulai

    print(f"selesai dalam {durasi:.1f} detik")
    return graf


def ringkas(graf: nx.MultiDiGraph) -> None:
    """Cetak ringkasan graf supaya hasil unduhan bisa diperiksa sekilas."""
    jumlah_simpul = graf.number_of_nodes()
    jumlah_sisi = graf.number_of_edges()

    print()
    print(f"simpul (persimpangan) : {jumlah_simpul:,}")
    print(f"sisi (ruas jalan)     : {jumlah_sisi:,}")

    # graph_from_polygon menandai CRS graf di atribut grafnya. Nilainya harus
    # EPSG:4326 karena belum ada proyeksi apa pun di tahap ini.
    print(f"CRS graf              : {graf.graph.get('crs')}")

    jenis: dict[str, int] = {}
    for _, _, data in graf.edges(data=True):
        nilai = data.get("highway", "tidak diketahui")
        # OSM kadang menaruh lebih dari satu nilai highway pada satu ruas.
        # Ambil yang pertama supaya ringkasannya tetap terbaca.
        if isinstance(nilai, list):
            nilai = nilai[0] if nilai else "tidak diketahui"
        jenis[nilai] = jenis.get(nilai, 0) + 1

    print("\njenis jalan terbanyak:")
    for nama, jumlah in sorted(jenis.items(), key=lambda x: -x[1])[:10]:
        print(f"  {nama:20s} {jumlah:6,}")


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument(
        "--paksa",
        action="store_true",
        help="timpa graf yang sudah ada",
    )
    argumen = pengurai.parse_args()

    if BERKAS_GRAF.exists() and not argumen.paksa:
        print(f"Graf sudah ada di {BERKAS_GRAF}")
        print("Skrip ini dirancang dijalankan sekali. Pakai --paksa untuk menimpa.")
        return 0

    config.DIR_DATA_OLAHAN.mkdir(parents=True, exist_ok=True)

    graf = bangun_graf()
    ringkas(graf)

    # GraphML adalah XML, jadi berkasnya besar tetapi bisa dibaca manusia dan
    # dimuat ulang tanpa menyentuh jaringan sama sekali. Inilah berkas yang
    # membuat jalur demo bisa offline penuh.
    ox.save_graphml(graf, BERKAS_GRAF)
    ukuran_mb = BERKAS_GRAF.stat().st_size / 1_048_576
    print(f"\ntersimpan: {BERKAS_GRAF}  ({ukuran_mb:.1f} MB)")
    print("Mulai sekarang tidak ada lagi panggilan ke Overpass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
