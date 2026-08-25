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

from contextlib import contextmanager
from typing import Iterable, Iterator, Sequence

import psycopg2
import psycopg2.extras

from app import config


class DatabaseBelumDikonfigurasi(RuntimeError):
    """DATABASE_URL belum diisi di .env."""


def _url_database() -> str:
    if not config.DATABASE_URL:
        raise DatabaseBelumDikonfigurasi(
            "DATABASE_URL belum diisi. Salin .env.example menjadi .env, "
            "lalu isi URL koneksi PostgreSQL. Berkas .env tidak masuk git."
        )
    return config.DATABASE_URL


@contextmanager
def koneksi() -> Iterator[psycopg2.extensions.connection]:
    """Buka koneksi, commit bila sukses, rollback bila ada galat, lalu tutup.

    Dipakai sebagai:

        with koneksi() as kon:
            repo = RepositoriRuas(kon)
    """
    kon = psycopg2.connect(_url_database())
    try:
        yield kon
        kon.commit()
    except Exception:
        kon.rollback()
        raise
    finally:
        kon.close()


def database_tersedia() -> bool:
    """Cek apakah database bisa dihubungi. Tidak pernah melempar galat.

    Dipakai lapisan API untuk memutuskan membaca dari database atau dari
    berkas cadangan di data/processed/.
    """
    try:
        with koneksi() as kon:
            with kon.cursor() as kur:
                kur.execute("SELECT 1")
        return True
    except Exception:
        return False


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
