"""Koneksi database dan repository sederhana.

Pola yang dipakai: **repository**. Setiap tabel punya satu kelas yang memuat
seluruh SQL untuk tabel itu. Skrip pipeline dan lapisan API memanggil metode
kelas ini, tidak pernah menulis SQL sendiri.

Alasannya bukan kerapian semata. Tabel `prediksi_genangan` adalah kontrak
antara orang yang melatih model dan orang yang membangun routing. Kalau SQL
tersebar di banyak berkas, satu perubahan kolom berarti perburuan di seluruh
repo. Dengan repository, perubahan itu berhenti di satu kelas.

Tidak ada ORM. psycopg2 langsung sudah cukup dan tidak menambah dependency.
"""

from __future__ import annotations

import atexit
import threading
import time
from contextlib import contextmanager
from typing import Iterable, Iterator, Sequence

import psycopg2
import psycopg2.extras
import psycopg2.pool

from app import config

# ══════════════════════════════════════════════════════════════════════════
# KOLAM KONEKSI
# ══════════════════════════════════════════════════════════════════════════
# KENAPA ADA KOLAM, PADAHAL SEBELUMNYA TANPA KOLAM SUDAH JALAN.
#
# Selama database berjalan di Docker pada mesin yang sama, membuka koneksi
# baru tiap permintaan hanya memakan sepersekian milidetik dan tidak
# terlihat. Begitu database pindah ke Supabase, dua hal berubah sekaligus:
#
#   1. Tiap koneksi baru menempuh jabat tangan TLS lintas benua. Yang tadinya
#      tak terasa menjadi ratusan milidetik.
#   2. Paket gratis membatasi jumlah koneksi. Beberapa juri yang membuka
#      aplikasi bersamaan di babak final bisa menghabiskannya.
#
# Lebih buruk lagi, lapisan API dulu membuka koneksi DUA KALI per permintaan:
# sekali oleh database_tersedia() untuk memeriksa keadaan, sekali lagi oleh
# endpoint-nya. Keduanya diperbaiki di sini.
#
# CATATAN PENTING TENTANG PGBOUNCER. Supabase menyarankan connection pooler
# di port 6543 yang berjalan dalam mode transaksi. Dalam mode itu satu
# koneksi server dipakai bergantian antar transaksi, sehingga apa pun yang
# menempel pada sesi — prepared statement bernama, kursor sisi server, hasil
# SET — tidak bertahan. Kode di berkas ini sengaja tidak memakai satu pun
# dari hal itu.

_UKURAN_KOLAM_MIN = 1
_UKURAN_KOLAM_MAKS = 5      # sengaja kecil: batas paket gratis, bukan performa

_kolam: psycopg2.pool.ThreadedConnectionPool | None = None
_kunci = threading.Lock()


class DatabaseBelumDikonfigurasi(RuntimeError):
    """DATABASE_URL belum diisi di .env."""


def _url_database() -> str:
    if not config.DATABASE_URL:
        raise DatabaseBelumDikonfigurasi(
            "DATABASE_URL belum diisi. Salin .env.example menjadi .env, "
            "lalu isi URL koneksi PostgreSQL. Berkas .env tidak masuk git."
        )
    return config.DATABASE_URL


def _dapatkan_kolam() -> psycopg2.pool.ThreadedConnectionPool:
    """Buat kolam sekali, aman dipanggil dari banyak utas sekaligus."""
    global _kolam
    if _kolam is None:
        with _kunci:
            if _kolam is None:      # diperiksa dua kali, di dalam kunci
                _kolam = psycopg2.pool.ThreadedConnectionPool(
                    _UKURAN_KOLAM_MIN, _UKURAN_KOLAM_MAKS, _url_database(),
                    # Tanpa ini, koneksi yang mati diam-diam karena jaringan
                    # putus baru ketahuan saat kueri berikutnya gagal.
                    keepalives=1,
                    keepalives_idle=30,
                    keepalives_interval=10,
                    keepalives_count=3,
                    connect_timeout=10,
                    application_name="pasang-surut",
                )
    return _kolam


def tutup_kolam() -> None:
    """Tutup seluruh koneksi. Dipanggil saat proses berakhir."""
    global _kolam
    with _kunci:
        if _kolam is not None:
            try:
                _kolam.closeall()
            except Exception:
                pass
            _kolam = None


atexit.register(tutup_kolam)


@contextmanager
def koneksi() -> Iterator[psycopg2.extensions.connection]:
    """Pinjam koneksi dari kolam, commit bila sukses, rollback bila galat.

    Dipakai sama seperti sebelumnya:

        with koneksi() as kon:
            repo = RepositoriRuas(kon)

    Bedanya, koneksinya DIKEMBALIKAN ke kolam, bukan ditutup. Koneksi yang
    transaksinya gagal dikembalikan dengan tanda buang supaya kolam tidak
    menyimpan koneksi yang keadaannya sudah kotor.
    """
    kolam = _dapatkan_kolam()
    kon = kolam.getconn()
    rusak = False
    try:
        yield kon
        kon.commit()
    except Exception:
        rusak = True
        try:
            kon.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            kolam.putconn(kon, close=rusak)
        except Exception:
            pass


# ── keadaan database, di-cache sebentar ───────────────────────────────────
# database_tersedia() dipanggil hampir tiap endpoint. Tanpa cache, ia
# menambah satu perjalanan bolak-balik ke Supabase pada tiap permintaan
# hanya untuk menjawab pertanyaan yang jawabannya nyaris tidak pernah
# berubah. Cache pendek membuat pemeriksaannya tetap jujur — kalau database
# benar-benar mati, paling lama beberapa detik kemudian ketahuan — tanpa
# membayar ongkos itu berulang kali.
_TTL_KESEHATAN_DETIK = 5.0
_kesehatan: tuple[float, bool] | None = None


def database_tersedia(paksa: bool = False) -> bool:
    """Cek apakah database bisa dihubungi. Tidak pernah melempar galat."""
    global _kesehatan
    sekarang = time.monotonic()
    if not paksa and _kesehatan is not None:
        dicek, hasil = _kesehatan
        if sekarang - dicek < _TTL_KESEHATAN_DETIK:
            return hasil
    try:
        with koneksi() as kon:
            with kon.cursor() as kur:
                kur.execute("SELECT 1")
        hasil = True
    except Exception:
        hasil = False
    _kesehatan = (time.monotonic(), hasil)
    return hasil


class RepositoriRuas:
    """Akses tabel `ruas_jalan`."""

    def __init__(self, kon: psycopg2.extensions.connection) -> None:
        self._kon = kon

    def kosongkan(self) -> None:
        """Hapus seluruh isi ruas_jalan.

        TRUNCATE ... CASCADE ikut mengosongkan prediksi_genangan dan
        sampel_latih karena keduanya punya foreign key ke edge_id. Ini
        disengaja: edge_id dibuat ulang oleh BIGSERIAL setiap kali graf
        dimuat ulang, jadi prediksi lama akan menunjuk ke ruas yang salah.
        """
        with self._kon.cursor() as kur:
            kur.execute("TRUNCATE ruas_jalan RESTART IDENTITY CASCADE")

    def sisipkan_banyak(self, baris: Iterable[Sequence]) -> int:
        """Sisipkan banyak ruas sekaligus.

        Urutan kolom tiap baris:
            (osm_u, osm_v, nama, jenis, panjang_m, kecepatan_kmh,
             satu_arah, geom_ewkt)

        geom_ewkt adalah teks EWKT, contoh:
            'SRID=4326;LINESTRING(110.42 -6.96, 110.43 -6.95)'

        ST_GeomFromEWKT mengubah teks itu jadi geometri PostGIS. Dipakai
        EWKT dan bukan WKT biasa karena EWKT membawa kode SRID di dalam
        teksnya, sehingga tidak ada kemungkinan geometri masuk tanpa sistem
        koordinat yang jelas.
        """
        baris = list(baris)
        if not baris:
            return 0
        with self._kon.cursor() as kur:
            psycopg2.extras.execute_values(
                kur,
                """
                INSERT INTO ruas_jalan
                    (osm_u, osm_v, nama, jenis, panjang_m, kecepatan_kmh,
                     satu_arah, geom)
                VALUES %s
                """,
                baris,
                template="(%s, %s, %s, %s, %s, %s, %s, ST_GeomFromEWKT(%s))",
                page_size=500,
            )
        return len(baris)

    def hitung(self) -> int:
        with self._kon.cursor() as kur:
            kur.execute("SELECT COUNT(*) FROM ruas_jalan")
            return kur.fetchone()[0]

    def panjang_total_km(self) -> float:
        with self._kon.cursor() as kur:
            kur.execute("SELECT COALESCE(SUM(panjang_m), 0) / 1000.0 FROM ruas_jalan")
            return float(kur.fetchone()[0])

    def id_dan_titik_tengah(self) -> list[tuple[int, float, float]]:
        """Ambil (edge_id, bujur, lintang) titik tengah tiap ruas.

        ST_LineInterpolatePoint(geom, 0.5) mengambil titik di tengah panjang
        garis. Dipakai skrip data contoh sebagai wakil posisi satu ruas.
        Perhitungannya di EPSG:4326, dan itu tidak apa-apa di sini karena
        yang dicari hanya posisi relatif, bukan jarak dalam meter.
        """
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT edge_id,
                       ST_X(ST_LineInterpolatePoint(geom, 0.5)) AS bujur,
                       ST_Y(ST_LineInterpolatePoint(geom, 0.5)) AS lintang
                FROM ruas_jalan
                ORDER BY edge_id
                """
            )
            return [(int(a), float(b), float(c)) for a, b, c in kur.fetchall()]

    def perbarui_fitur(self, baris: Iterable[Sequence]) -> int:
        """Isi kolom fitur model. Urutan tiap baris:

            (elevasi_m, jarak_pantai_m, laju_subsidensi_cm_thn, edge_id)

        Diperbarui sekaligus lewat VALUES dan bukan satu UPDATE per ruas,
        karena dua ribu perjalanan bolak-balik ke database untuk pekerjaan
        yang sama adalah pemborosan yang terlihat jelas saat skrip dijalankan
        ulang.

        NULL diperbolehkan dan bermakna: piksel DEM tanpa data tetap NULL,
        bukan nol. Nol adalah elevasi yang sah di kawasan pesisir, jadi
        memakainya sebagai penanda "tidak ada data" akan mencemari fitur
        model dengan ruas yang seolah-olah berada tepat di muka air.
        """
        baris = list(baris)
        if not baris:
            return 0
        with self._kon.cursor() as kur:
            psycopg2.extras.execute_values(
                kur,
                """
                UPDATE ruas_jalan r SET
                    elevasi_m              = v.elevasi,
                    jarak_pantai_m         = v.jarak,
                    laju_subsidensi_cm_thn = v.subsidensi
                FROM (VALUES %s)
                     AS v(elevasi, jarak, subsidensi, edge_id)
                WHERE r.edge_id = v.edge_id
                """,
                baris,
                template=(
                    "(%s::double precision, %s::double precision,"
                    " %s::double precision, %s::bigint)"
                ),
                page_size=500,
            )
        return len(baris)

    def ringkasan_fitur(self) -> dict:
        """Berapa ruas yang fiturnya sudah terisi. Dipakai untuk melapor."""
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT COUNT(*),
                       COUNT(elevasi_m),
                       COUNT(jarak_pantai_m),
                       COUNT(laju_subsidensi_cm_thn),
                       MIN(elevasi_m), MAX(elevasi_m),
                       MIN(jarak_pantai_m), MAX(jarak_pantai_m)
                FROM ruas_jalan
                """
            )
            b = kur.fetchone()
        return {
            "ruas": int(b[0]),
            "elevasi_terisi": int(b[1]),
            "jarak_pantai_terisi": int(b[2]),
            "subsidensi_terisi": int(b[3]),
            "elevasi_min_m": None if b[4] is None else float(b[4]),
            "elevasi_maks_m": None if b[5] is None else float(b[5]),
            "jarak_pantai_min_m": None if b[6] is None else float(b[6]),
            "jarak_pantai_maks_m": None if b[7] is None else float(b[7]),
        }

    def geojson(self, waktu=None) -> dict:
        """Seluruh ruas sebagai FeatureCollection GeoJSON.

        Bila `waktu` diisi, kedalaman genangan pada jam itu ikut dilampirkan
        lewat LEFT JOIN. LEFT dan bukan INNER supaya ruas yang tidak punya
        baris prediksi tetap muncul di peta sebagai ruas kering, bukan hilang.

        ST_AsGeoJSON mengeluarkan geometri dalam EPSG:4326 apa adanya, yaitu
        format yang langsung dimengerti MapLibre di frontend. Tidak ada
        proyeksi di sini — proyeksi ke meter hanya dipakai saat menghitung
        panjang, dan itu sudah selesai sejak ruas disisipkan.
        """
        sql = """
            SELECT r.edge_id, r.nama, r.jenis, r.panjang_m, r.kecepatan_kmh,
                   r.satu_arah,
                   COALESCE(p.kedalaman_cm, 0)  AS kedalaman_cm,
                   COALESCE(p.probabilitas, 0)  AS probabilitas,
                   p.sumber,
                   ST_AsGeoJSON(r.geom, 5) AS geom
            FROM ruas_jalan r
            LEFT JOIN prediksi_genangan p
                   ON p.edge_id = r.edge_id AND p.waktu = %s
            ORDER BY r.edge_id
        """
        import json

        with self._kon.cursor() as kur:
            kur.execute(sql, (waktu,))
            fitur = []
            for (
                edge_id, nama, jenis, panjang_m, kecepatan_kmh, satu_arah,
                kedalaman_cm, probabilitas, sumber, geom,
            ) in kur.fetchall():
                fitur.append({
                    "type": "Feature",
                    "id": edge_id,
                    "properties": {
                        "edge_id": edge_id,
                        "nama": nama,
                        "jenis": jenis,
                        "panjang_m": round(float(panjang_m), 1),
                        "kecepatan_kmh": float(kecepatan_kmh) if kecepatan_kmh else None,
                        "satu_arah": bool(satu_arah),
                        "kedalaman_cm": round(float(kedalaman_cm), 1),
                        "probabilitas": round(float(probabilitas), 3),
                        "sumber": sumber,
                    },
                    "geometry": json.loads(geom),
                })
        return {"type": "FeatureCollection", "features": fitur}

    def semua_untuk_routing(self) -> list[dict]:
        """Seluruh ruas dalam bentuk yang siap dijadikan graf routing.

        KENAPA GRAF DIBANGUN DARI TABEL, BUKAN DARI GraphML. Tabel ruas_jalan
        sudah memuat seluruh yang dibutuhkan: simpul ujung, panjang dalam
        meter, kecepatan, arah, dan geometri. Jumlah simpul uniknya juga
        persis sama dengan graf OSMnx aslinya, jadi tidak ada konektivitas
        yang hilang.

        Keuntungannya dua. Pertama, edge_id yang dipakai tabel prediksi
        genangan menempel langsung pada sisi graf, sehingga tidak perlu
        mencocokkan pasangan simpul dan tidak ada kemungkinan salah pasang
        pada ruas paralel. Kedua, API tidak lagi memerlukan berkas GraphML
        saat berjalan, sehingga server yang di-deploy cukup membawa database.

        Titik ujung diambil dari geometri: koordinat pertama adalah posisi
        osm_u, koordinat terakhir adalah posisi osm_v. Ini dipakai untuk
        mencari simpul terdekat dari titik yang diketuk pengguna di peta.
        """
        import json

        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT edge_id, osm_u, osm_v, nama, jenis, panjang_m,
                       kecepatan_kmh, satu_arah, ST_AsGeoJSON(geom, 5)
                FROM ruas_jalan
                ORDER BY edge_id
                """
            )
            hasil = []
            for (edge_id, u, v, nama, jenis, panjang, kecepatan,
                 satu_arah, geom) in kur.fetchall():
                koordinat = json.loads(geom)["coordinates"]
                hasil.append({
                    "edge_id": int(edge_id),
                    "osm_u": int(u),
                    "osm_v": int(v),
                    "nama": nama,
                    "jenis": jenis,
                    "panjang_m": float(panjang),
                    "kecepatan_kmh": float(kecepatan) if kecepatan else 30.0,
                    "satu_arah": bool(satu_arah),
                    "koordinat": koordinat,
                })
            return hasil

    def ambang_moda(self) -> dict[str, dict]:
        """Baca tabel ambang_moda apa adanya.

        Aturan sesi ini: ambang TIDAK BOLEH ditulis tetap di dalam kode.
        Angka di tabel itu sendiri masih berstatus asumsi menurut komentar
        di schema.sql, jadi ia harus bisa dikoreksi tanpa menyentuh kode.
        """
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT moda, lambat_cm, berisiko_cm, tidak_bisa_lewat_cm,
                       konsumsi_l_per_km, faktor_emisi_kg_per_l
                FROM ambang_moda
                ORDER BY moda
                """
            )
            return {
                baris[0]: {
                    "lambat_cm": float(baris[1]),
                    "berisiko_cm": float(baris[2]),
                    "tidak_bisa_lewat_cm": float(baris[3]),
                    "konsumsi_l_per_km": float(baris[4]),
                    "faktor_emisi_kg_per_l": float(baris[5]),
                }
                for baris in kur.fetchall()
            }


class RepositoriGenangan:
    """Akses tabel `prediksi_genangan` — kontrak antara model dan routing."""

    def __init__(self, kon: psycopg2.extensions.connection) -> None:
        self._kon = kon

    def kosongkan_sumber(self, sumber: str) -> int:
        """Hapus hanya baris dengan sumber tertentu.

        Penting: menghapus per sumber, bukan seluruh tabel. Saat model asli
        siap, baris 'dummy' dibuang tanpa menyentuh baris 'model_v1', dan
        sebaliknya. Inilah yang membuat pergantian dari data contoh ke model
        asli tidak memerlukan perubahan kode di sisi routing dan frontend.
        """
        with self._kon.cursor() as kur:
            kur.execute("DELETE FROM prediksi_genangan WHERE sumber = %s", (sumber,))
            return kur.rowcount

    def sisipkan_banyak(self, baris: Iterable[Sequence]) -> int:
        """Urutan kolom: (edge_id, waktu, kedalaman_cm, probabilitas, sumber).

        ON CONFLICT memakai kunci primer (edge_id, waktu) supaya skrip bisa
        dijalankan ulang tanpa menabrak baris yang sudah ada.
        """
        baris = list(baris)
        if not baris:
            return 0
        with self._kon.cursor() as kur:
            psycopg2.extras.execute_values(
                kur,
                """
                INSERT INTO prediksi_genangan
                    (edge_id, waktu, kedalaman_cm, probabilitas, sumber)
                VALUES %s
                ON CONFLICT (edge_id, waktu) DO UPDATE SET
                    kedalaman_cm = EXCLUDED.kedalaman_cm,
                    probabilitas = EXCLUDED.probabilitas,
                    sumber       = EXCLUDED.sumber
                """,
                baris,
                page_size=1000,
            )
        return len(baris)

    def hitung(self) -> int:
        with self._kon.cursor() as kur:
            kur.execute("SELECT COUNT(*) FROM prediksi_genangan")
            return kur.fetchone()[0]

    def sumber_yang_ada(self) -> list[str]:
        """Daftar nilai `sumber` yang sedang mengisi tabel.

        Dipakai lapisan API untuk memutuskan apakah lencana DATA CONTOH
        ditampilkan. Selama masih ada 'dummy', lencana wajib tampil.
        """
        with self._kon.cursor() as kur:
            kur.execute("SELECT DISTINCT sumber FROM prediksi_genangan ORDER BY sumber")
            return [b[0] for b in kur.fetchall()]

    def rentang_waktu(self) -> tuple[object | None, object | None]:
        with self._kon.cursor() as kur:
            kur.execute("SELECT MIN(waktu), MAX(waktu) FROM prediksi_genangan")
            awal, akhir = kur.fetchone()
            return awal, akhir

    def peta_kedalaman(self, mulai, selesai) -> dict:
        """Seluruh prediksi pada rentang waktu, disusun per jam.

        Bentuk hasilnya: { waktu: { edge_id: (kedalaman_cm, probabilitas) } }

        Dimuat sekaligus, bukan satu kueri per jam, karena mesin routing
        yang sadar waktu berpindah jam sepanjang penelusuran. Menanyakan
        database di tengah Dijkstra akan membuat satu permintaan rute
        memicu ribuan kueri.

        Ingat: ruas kering TIDAK punya baris. Ruas yang tidak muncul di sini
        berarti kering, bukan berarti datanya hilang.
        """
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT waktu, edge_id, kedalaman_cm, probabilitas
                FROM prediksi_genangan
                WHERE waktu BETWEEN %s AND %s
                """,
                (mulai, selesai),
            )
            hasil: dict = {}
            for waktu, edge_id, kedalaman, probabilitas in kur.fetchall():
                hasil.setdefault(waktu, {})[int(edge_id)] = (
                    float(kedalaman), float(probabilitas)
                )
            return hasil

    def ringkasan_per_jam(self) -> list[tuple]:
        """(waktu, jumlah ruas tergenang, kedalaman maksimum) untuk tiap jam.

        Dipakai Pita Pasut di frontend untuk mengarsir jam berisiko.
        """
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT waktu, COUNT(*), COALESCE(MAX(kedalaman_cm), 0)
                FROM prediksi_genangan
                GROUP BY waktu
                ORDER BY waktu
                """
            )
            return [(w, int(n), float(m)) for w, n, m in kur.fetchall()]


class RepositoriPemicu:
    """Akses tabel `pemicu` — variabel pendorong genangan, satu baris per jam.

    Isinya tinggi pasut hasil rekonstruksi harmonik dan hujan terakumulasi
    24 dan 72 jam. Dua-duanya dihitung sekali lalu disimpan, tidak pernah
    diambil saat permintaan rute datang. Aturan repo nomor 6 melarang
    panggilan API eksternal saat runtime, dan hujan Open-Meteo adalah contoh
    paling jelas dari hal yang menggoda untuk dipanggil langsung.
    """

    def __init__(self, kon: psycopg2.extensions.connection) -> None:
        self._kon = kon

    def sisipkan_banyak(self, baris: Iterable[Sequence]) -> int:
        """Urutan kolom:
        (waktu, tinggi_pasut_m, hujan_24j_mm, hujan_72j_mm, sumber_hujan).

        ON CONFLICT dipakai supaya pengambilan ulang rentang tanggal yang
        sama memperbarui, bukan menabrak kunci primer.
        """
        baris = list(baris)
        if not baris:
            return 0
        with self._kon.cursor() as kur:
            psycopg2.extras.execute_values(
                kur,
                """
                INSERT INTO pemicu
                    (waktu, tinggi_pasut_m, hujan_24j_mm, hujan_72j_mm,
                     sumber_hujan)
                VALUES %s
                ON CONFLICT (waktu) DO UPDATE SET
                    tinggi_pasut_m = EXCLUDED.tinggi_pasut_m,
                    hujan_24j_mm   = EXCLUDED.hujan_24j_mm,
                    hujan_72j_mm   = EXCLUDED.hujan_72j_mm,
                    sumber_hujan   = EXCLUDED.sumber_hujan
                """,
                baris,
                page_size=1000,
            )
        return len(baris)

    def hitung(self) -> int:
        with self._kon.cursor() as kur:
            kur.execute("SELECT COUNT(*) FROM pemicu")
            return kur.fetchone()[0]

    def rentang_waktu(self) -> tuple[object | None, object | None]:
        with self._kon.cursor() as kur:
            kur.execute("SELECT MIN(waktu), MAX(waktu) FROM pemicu")
            return kur.fetchone()

    def ringkasan(self) -> dict:
        """Statistik ringkas untuk dilaporkan setelah pengisian."""
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT COUNT(*),
                       MIN(waktu), MAX(waktu),
                       MIN(tinggi_pasut_m), MAX(tinggi_pasut_m),
                       MAX(hujan_24j_mm), MAX(hujan_72j_mm),
                       COUNT(*) FILTER (WHERE hujan_24j_mm > 0)
                FROM pemicu
                """
            )
            b = kur.fetchone()
        return {
            "baris": int(b[0]),
            "awal": b[1],
            "akhir": b[2],
            "pasut_min_m": None if b[3] is None else float(b[3]),
            "pasut_maks_m": None if b[4] is None else float(b[4]),
            "hujan_24j_maks_mm": None if b[5] is None else float(b[5]),
            "hujan_72j_maks_mm": None if b[6] is None else float(b[6]),
            "jam_berhujan": int(b[7] or 0),
        }

    def pada(self, waktu) -> dict | None:
        """Satu baris pemicu pada jam tertentu, atau None bila tidak ada."""
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT waktu, tinggi_pasut_m, hujan_24j_mm, hujan_72j_mm,
                       sumber_hujan
                FROM pemicu WHERE waktu = %s
                """,
                (waktu,),
            )
            b = kur.fetchone()
        if b is None:
            return None
        return {
            "waktu": b[0],
            "tinggi_pasut_m": float(b[1]),
            "hujan_24j_mm": float(b[2] or 0.0),
            "hujan_72j_mm": float(b[3] or 0.0),
            "sumber_hujan": b[4],
        }


class RepositoriSampelLatih:
    """Akses tabel `sampel_latih` — satu baris per ruas per waktu akuisisi.

    Ingat aturan PLAN.md bagian 8: SETIAP citra menjadi sampel, bukan hanya
    citra pada tanggal rob. Sebagian besar baris di tabel ini karena itu
    berlabel kering, dan memang seharusnya begitu. Ketidakseimbangan kelas
    ditangani di sisi model, bukan dengan membuang baris kering.
    """

    def __init__(self, kon: psycopg2.extensions.connection) -> None:
        self._kon = kon

    def kosongkan(self) -> int:
        with self._kon.cursor() as kur:
            kur.execute("DELETE FROM sampel_latih")
            return kur.rowcount

    def sisipkan_banyak(self, baris: Iterable[Sequence]) -> int:
        """Urutan kolom: (edge_id, waktu_akuisisi, s1_scene_id, basah,
        tinggi_pasut_m, hujan_24j_mm, hujan_72j_mm)."""
        baris = list(baris)
        if not baris:
            return 0
        with self._kon.cursor() as kur:
            psycopg2.extras.execute_values(
                kur,
                """
                INSERT INTO sampel_latih
                    (edge_id, waktu_akuisisi, s1_scene_id, basah,
                     tinggi_pasut_m, hujan_24j_mm, hujan_72j_mm)
                VALUES %s
                """,
                baris,
                page_size=2000,
            )
        return len(baris)

    def ringkasan(self) -> dict:
        with self._kon.cursor() as kur:
            kur.execute(
                """
                SELECT COUNT(*),
                       COUNT(*) FILTER (WHERE basah),
                       COUNT(DISTINCT edge_id),
                       COUNT(DISTINCT waktu_akuisisi),
                       MIN(waktu_akuisisi), MAX(waktu_akuisisi)
                FROM sampel_latih
                """
            )
            b = kur.fetchone()
        return {
            "baris": int(b[0]),
            "basah": int(b[1] or 0),
            "ruas": int(b[2] or 0),
            "citra": int(b[3] or 0),
            "awal": b[4],
            "akhir": b[5],
        }
