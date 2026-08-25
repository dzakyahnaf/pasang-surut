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

    HATI-HATI DI SINI, DAN INI PERNAH SALAH. to_undirected() TIDAK menjamin
    sisi hasil gabungan mempertahankan orientasi aslinya. Untuk jalan dua
    arah itu tidak masalah, tetapi untuk jalan satu arah artinya pasangan
    (osm_u, osm_v) yang tersimpan belum tentu searah dengan arah jalan yang
    sebenarnya.

    Akibatnya terukur: ketika mesin routing menghormati kolom satu_arah apa
    adanya, hanya 13,6 persen simpul yang terjangkau dari Pelabuhan Tanjung
    Emas. Jalan satu arah yang arahnya terbalik bekerja seperti tembok.

    Karena itu arah TIDAK diambil dari atribut oneway hasil penggabungan,
    melainkan diperiksa ulang terhadap graf berarah aslinya. Lihat
    arah_sebenarnya().
    """
    graf_tak_berarah = ox.convert.to_undirected(graf)
    print(
        f"sisi berarah {graf.number_of_edges():,} "
        f"-> ruas fisik {graf_tak_berarah.number_of_edges():,}"
    )
    return graf_tak_berarah


def arah_sebenarnya(u, v, koordinat, pasangan_berarah):
    """Tentukan arah jalan yang benar dengan melihat graf berarah aslinya.

    Aturannya sederhana dan tidak menebak sama sekali:

      - Kalau (u, v) DAN (v, u) sama-sama ada di graf berarah, jalan itu dua
        arah. Simpan apa adanya, satu_arah bernilai salah.
      - Kalau hanya (u, v) yang ada, jalan itu satu arah dari u ke v.
      - Kalau hanya (v, u) yang ada, jalan itu satu arah dari v ke u, jadi
        pasangan simpulnya DITUKAR dan geometrinya dibalik supaya
        osm_u -> osm_v selalu berarti arah yang boleh dilalui.

    Dengan begitu mesin routing cukup membaca osm_u dan osm_v tanpa perlu
    tahu apa pun soal cara graf ini dibangun.

    Mengembalikan (u, v, koordinat, satu_arah).
    """
    maju = (u, v) in pasangan_berarah
    mundur = (v, u) in pasangan_berarah

    if maju and mundur:
        return u, v, koordinat, False
    if maju:
        return u, v, koordinat, True
    if mundur:
        return v, u, list(reversed(koordinat)), True

    # Tidak ditemukan di graf berarah. Seharusnya mustahil, karena graf tak
    # berarah diturunkan dari graf berarah itu sendiri. Diperlakukan sebagai
    # dua arah supaya tidak diam-diam memutus jaringan, dan dihitung sebagai
    # anomali di ringkasan.
    return u, v, koordinat, False


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


def susun_daftar_ruas(gdf: gpd.GeoDataFrame, pasangan_berarah: set) -> list[dict]:
    """Ubah GeoDataFrame jadi daftar ruas dengan arah yang sudah dibetulkan.

    Satu tempat ini menjadi sumber untuk dua keluaran sekaligus, yaitu baris
    database dan berkas GeoJSON cadangan, supaya keduanya tidak mungkin
    berbeda isi.
    """
    daftar: list[dict] = []
    ditukar = 0
    anomali = 0

    for (u, v, _kunci), data in gdf.iterrows():
        geometri = data.geometry
        if geometri is None or geometri.is_empty:
            continue

        koordinat = [
            [round(x, DESIMAL_KOORDINAT), round(y, DESIMAL_KOORDINAT)]
            for x, y in geometri.coords
        ]

        u_asli, v_asli = int(u), int(v)
        if (u_asli, v_asli) not in pasangan_berarah and (v_asli, u_asli) not in pasangan_berarah:
            anomali += 1

        u_baru, v_baru, koordinat, satu_arah = arah_sebenarnya(
            u_asli, v_asli, koordinat, pasangan_berarah
        )
        if (u_baru, v_baru) != (u_asli, v_asli):
            ditukar += 1

        daftar.append({
            "osm_u": u_baru,
            "osm_v": v_baru,
            "nama": _teks_pertama(data.get("name")),
            "jenis": _teks_pertama(data.get("highway"), "tidak diketahui"),
            "panjang_m": float(data["panjang_m"]),
            "kecepatan_kmh": float(data["kecepatan_kmh"]),
            "satu_arah": satu_arah,
            "koordinat": koordinat,
        })

    satu_arah_total = sum(1 for r in daftar if r["satu_arah"])
    print(f"ruas satu arah        : {satu_arah_total:,}")
    print(f"arah dibalik agar benar: {ditukar:,}")
    if anomali:
        print(f"PERINGATAN: {anomali:,} ruas tidak ditemukan di graf berarah")
    return daftar


def siapkan_baris(daftar: list[dict]) -> list[tuple]:
    """Susun baris siap sisip sesuai urutan kolom RepositoriRuas."""
    baris = []
    for r in daftar:
        titik = ", ".join(f"{x} {y}" for x, y in r["koordinat"])
        # EWKT membawa kode SRID di dalam teksnya, jadi tidak mungkin
        # geometri masuk ke database tanpa sistem koordinat yang jelas.
        ewkt = f"SRID={config.EPSG_SIMPAN};LINESTRING({titik})"
        baris.append((
            r["osm_u"], r["osm_v"], r["nama"], r["jenis"],
            r["panjang_m"], r["kecepatan_kmh"], r["satu_arah"], ewkt,
        ))
    return baris


def tulis_geojson(daftar: list[dict]) -> None:
    """Ekspor jaringan jalan ke GeoJSON sebagai jalur cadangan offline.

    Berkas ini dipakai lapisan API kalau database belum tersedia, misalnya
    di laptop anggota tim yang belum menyiapkan Supabase. Dengan begitu peta
    tetap bisa dibuka tanpa database sama sekali.
    """
    fitur = [
        {
            "type": "Feature",
            "properties": {
                "osm_u": r["osm_u"],
                "osm_v": r["osm_v"],
                "nama": r["nama"],
                "jenis": r["jenis"],
                "panjang_m": round(r["panjang_m"], 1),
                "kecepatan_kmh": round(r["kecepatan_kmh"], 1),
                "satu_arah": r["satu_arah"],
            },
            "geometry": {"type": "LineString", "coordinates": r["koordinat"]},
        }
        for r in daftar
    ]

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

    graf_berarah = muat_graf()

    # Rekam seluruh pasangan simpul yang benar-benar ada sebagai sisi
    # BERARAH, sebelum graf disederhanakan. Inilah satu-satunya sumber yang
    # sah untuk menentukan arah jalan satu arah. Lihat arah_sebenarnya().
    pasangan_berarah = {(int(u), int(v)) for u, v in graf_berarah.edges()}
    print(f"pasangan berarah unik : {len(pasangan_berarah):,}")

    graf = ke_ruas_tunggal(graf_berarah)

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

    daftar = susun_daftar_ruas(gdf, pasangan_berarah)
    tulis_geojson(daftar)

    if argumen.tanpa_database:
        print("dilewati: penyisipan ke database (--tanpa-database)")
        return 0

    baris = siapkan_baris(daftar)
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
