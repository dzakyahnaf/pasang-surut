"""API PASANG SURUT.

    cd backend && uvicorn app.main:app --reload

Dua endpoint di milestone ini:

    GET /api/kesehatan   keadaan sistem, sumber data, rentang waktu prediksi
    GET /api/ruas        jaringan jalan sebagai GeoJSON, dengan kedalaman
                         genangan pada jam yang diminta

Pita Pasut, routing, rute, dan validasi menyusul di milestone berikutnya.

Catatan penting soal jalur offline: API ini TIDAK PERNAH memanggil layanan
luar. Jaringan jalan dibaca dari database, atau dari berkas GeoJSON di
data/processed/ bila database belum tersedia. Overpass hanya disentuh sekali
oleh skrip 01, jauh sebelum aplikasi dijalankan.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import config, db

app = FastAPI(
    title="PASANG SURUT",
    description="Perutean sadar rob untuk Semarang pesisir",
    version="0.2.0",
)

# Frontend berjalan di port lain saat pengembangan, jadi peramban
# memperlakukannya sebagai asal yang berbeda dan memblokir permintaan tanpa
# izin CORS. Daftar ini hanya berisi alamat pengembangan lokal.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

BERKAS_GEOJSON = config.DIR_DATA_OLAHAN / "ruas_jalan.geojson"


# ══════════════════════════════════════════════════════════════════════════
# SUMBER DATA
# ══════════════════════════════════════════════════════════════════════════
@lru_cache(maxsize=1)
def _ruas_dari_berkas() -> dict:
    """Baca jaringan jalan dari berkas cadangan, lalu simpan di memori.

    Dipakai kalau database belum siap. Berkas ini dihasilkan skrip 02 dan
    isinya sama dengan tabel ruas_jalan, hanya tanpa kolom prediksi.
    """
    if not BERKAS_GEOJSON.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Jaringan jalan belum tersedia. Jalankan dari backend/: "
                "python -m scripts.01_bangun_graf lalu "
                "python -m scripts.02_isi_ruas_jalan"
            ),
        )
    return json.loads(BERKAS_GEOJSON.read_text(encoding="utf-8"))


def _jam_bulat(waktu: datetime) -> datetime:
    """Bulatkan ke jam penuh dalam UTC.

    Prediksi disimpan per jam penuh. Permintaan dengan menit dan detik
    dibulatkan ke bawah supaya cocok dengan kunci di database.
    """
    if waktu.tzinfo is None:
        # Waktu tanpa zona dianggap UTC, bukan waktu lokal mesin. Kalau
        # dianggap lokal, hasilnya berbeda di laptop tiap anggota tim.
        waktu = waktu.replace(tzinfo=timezone.utc)
    return waktu.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


# ══════════════════════════════════════════════════════════════════════════
# ENDPOINT
# ══════════════════════════════════════════════════════════════════════════
@app.get("/api/kesehatan")
def kesehatan() -> dict:
    """Keadaan sistem. Dipakai frontend untuk tahu apa yang sedang dilihat.

    Bagian terpenting di sini adalah `sumber_data`. Selama nilainya masih
    memuat 'dummy', frontend WAJIB menampilkan lencana DATA CONTOH. Lencana
    itu hilang dengan sendirinya begitu tabel diisi 'model_v1' — tidak ada
    saklar manual yang bisa lupa dimatikan.
    """
    sekarang = datetime.now(timezone.utc)
    jawaban = {
        "status": "hidup",
        "versi": app.version,
        "waktu_server_utc": sekarang.isoformat(),
        "zona_waktu_tampilan": str(config.ZONA_WAKTU_LOKAL),
        "aoi": {
            "berkas": config.BERKAS_AOI.name,
            "bbox": list(config.bbox_aoi()),
            "crs_simpan": config.CRS_SIMPAN,
            "crs_metrik": config.CRS_METRIK,
        },
        "database": False,
        "jumlah_ruas": 0,
        "sumber_data": [],
        "prediksi_mulai_utc": None,
        "prediksi_selesai_utc": None,
        "asal_jaringan": "berkas",
    }

    if db.database_tersedia():
        with db.koneksi() as kon:
            repo_ruas = db.RepositoriRuas(kon)
            repo_gen = db.RepositoriGenangan(kon)
            awal, akhir = repo_gen.rentang_waktu()
            jawaban.update({
                "database": True,
                "asal_jaringan": "database",
                "jumlah_ruas": repo_ruas.hitung(),
                "panjang_jaringan_km": round(repo_ruas.panjang_total_km(), 1),
                "jumlah_prediksi": repo_gen.hitung(),
                "sumber_data": repo_gen.sumber_yang_ada(),
                "prediksi_mulai_utc": awal.isoformat() if awal else None,
                "prediksi_selesai_utc": akhir.isoformat() if akhir else None,
            })
    else:
        isi = _ruas_dari_berkas()
        jawaban["jumlah_ruas"] = len(isi.get("features", []))

    return jawaban


@app.get("/api/ruas")
def ruas(
    waktu: str | None = Query(
        default=None,
        description=(
            "Jam yang ingin dilihat, format ISO 8601, contoh "
            "2026-08-24T09:00:00Z. Dibulatkan ke jam penuh. "
            "Kosongkan untuk memakai jam berjalan."
        ),
    ),
) -> dict:
    """Jaringan jalan sebagai GeoJSON, lengkap dengan kedalaman pada satu jam.

    Geometri keluar dalam EPSG:4326 karena itu yang dimengerti MapLibre di
    frontend. Tidak ada proyeksi di sini: panjang ruas dalam meter sudah
    dihitung sekali di skrip 02 dan tersimpan sebagai kolom biasa.
    """
    if waktu is None:
        waktu_utc = _jam_bulat(datetime.now(timezone.utc))
    else:
        try:
            # fromisoformat pada Python 3.11 sudah menerima akhiran Z.
            waktu_utc = _jam_bulat(datetime.fromisoformat(waktu))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Format waktu tidak dikenali: {waktu}. "
                    "Pakai ISO 8601, contoh 2026-08-24T09:00:00Z."
                ),
            )

    if db.database_tersedia():
        with db.koneksi() as kon:
            isi = db.RepositoriRuas(kon).geojson(waktu_utc)
            sumber = db.RepositoriGenangan(kon).sumber_yang_ada()
        asal = "database"
    else:
        # Jalur cadangan: berkas tidak memuat prediksi sama sekali, jadi
        # seluruh ruas dilaporkan kering. Peta tetap tampil, hanya tanpa
        # lapisan genangan.
        berkas = _ruas_dari_berkas()
        fitur = []
        for indeks, f in enumerate(berkas.get("features", [])):
            sifat = dict(f.get("properties", {}))
            sifat.update({"edge_id": indeks + 1, "kedalaman_cm": 0.0,
                          "probabilitas": 0.0, "sumber": None})
            fitur.append({
                "type": "Feature",
                "id": indeks + 1,
                "properties": sifat,
                "geometry": f["geometry"],
            })
        isi = {"type": "FeatureCollection", "features": fitur}
        sumber = []
        asal = "berkas"

    # GeoJSON mengizinkan anggota tambahan di tingkat teratas. MapLibre
    # mengabaikannya, sementara frontend kita memakainya untuk tahu jam mana
    # yang sedang tampil dan apakah lencana DATA CONTOH perlu muncul.
    isi["waktu_utc"] = waktu_utc.isoformat()
    isi["waktu_wib"] = waktu_utc.astimezone(config.ZONA_WAKTU_LOKAL).isoformat()
    isi["sumber_data"] = sumber
    isi["asal_jaringan"] = asal
    return isi
