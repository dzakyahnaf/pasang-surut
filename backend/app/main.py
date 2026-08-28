"""API PASANG SURUT.

    cd backend && uvicorn app.main:app --reload

Endpoint yang tersedia:

    GET  /api/kesehatan   keadaan sistem, sumber data, rentang waktu prediksi
    GET  /api/ruas        jaringan jalan sebagai GeoJSON, dengan kedalaman
                          genangan pada jam yang diminta
    GET  /api/genangan    ruas tergenang saja pada satu jam
    GET  /api/jam         ringkasan per jam untuk Pita Pasut
    POST /api/rute        dua rute sekaligus: pembanding dan sadar rob

Panel dampak, tujuan cepat, dan halaman validasi menyusul di milestone
berikutnya.

Catatan penting soal jalur offline: API ini TIDAK PERNAH memanggil layanan
luar. Jaringan jalan dibaca dari database, atau dari berkas GeoJSON di
data/processed/ bila database belum tersedia. Overpass hanya disentuh sekali
oleh skrip 01, jauh sebelum aplikasi dijalankan.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config, db
from app.domain import pasut, routing

app = FastAPI(
    title="PASANG SURUT",
    description="Perutean sadar rob untuk Semarang pesisir",
    version="0.3.0",
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
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

BERKAS_GEOJSON = config.DIR_DATA_OLAHAN / "ruas_jalan.geojson"


# ══════════════════════════════════════════════════════════════════════════
# PEMANASAN SAAT START
# ══════════════════════════════════════════════════════════════════════════
@app.on_event("startup")
async def panaskan_cache() -> None:
    """Bangun graf routing dan baca ambang moda sebelum permintaan pertama.

    KENAPA INI PENTING, DAN KENAPA BARU TERASA SETELAH PINDAH KE SUPABASE.

    Graf routing dibangun dari 19.394 baris tabel `ruas_jalan` dan disimpan
    di cache. Selama database berjalan di mesin yang sama, pembangunan itu
    memakan waktu yang tidak terasa. Lewat jaringan ke Supabase, permintaan
    rute PERTAMA terukur 11,9 detik sementara permintaan berikutnya hanya
    1,3 detik.

    Sebelas detik itu jatuh tepat pada klik pertama pengguna, dan di babak
    final pengguna pertamanya adalah juri. Kriteria Keberhasilan Implementasi
    berbobot 25 persen dan dinilai dari memakai aplikasi langsung.

    Dijalankan di latar lewat utas terpisah supaya server tetap menerima
    permintaan selagi memanaskan. Kegagalan sengaja ditelan: database yang
    belum siap saat start bukan alasan untuk menolak menyalakan server, dan
    endpoint-nya sendiri sudah menangani keadaan itu dengan galat yang jelas.
    """
    import asyncio

    def kerjakan() -> None:
        try:
            _graf_routing()
            _ambang_moda()
        except Exception:
            pass

    asyncio.get_running_loop().run_in_executor(None, kerjakan)


@app.on_event("shutdown")
async def tutup_koneksi() -> None:
    """Kembalikan seluruh koneksi ke Supabase saat server berhenti."""
    db.tutup_kolam()


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
    waktu_utc = _jam_bulat(_urai_waktu(waktu))

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


# ══════════════════════════════════════════════════════════════════════════
# GRAF ROUTING — dimuat sekali, disimpan di memori
# ══════════════════════════════════════════════════════════════════════════
def _urai_waktu(waktu: str | None) -> datetime:
    """Ubah teks ISO 8601 menjadi datetime UTC. Kosong berarti jam berjalan."""
    if waktu is None:
        return datetime.now(timezone.utc)
    try:
        # fromisoformat pada Python 3.11 sudah menerima akhiran Z.
        return datetime.fromisoformat(waktu)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Format waktu tidak dikenali: {waktu}. "
                "Pakai ISO 8601, contoh 2026-08-24T09:00:00Z."
            ),
        )


@lru_cache(maxsize=1)
def _graf_routing() -> routing.GrafJalan:
    """Bangun graf jalan dari tabel ruas_jalan, sekali saja.

    Membangunnya ulang tiap permintaan berarti membaca 19 ribu baris setiap
    kali pengguna menggeser Pita Pasut satu jam. Cache ini yang membuat
    pergeseran terasa seketika.

    Kalau isi tabel ruas_jalan berubah, proses API harus dijalankan ulang.
    Itu wajar: ruas jalan hanya berubah saat skrip 02 dijalankan ulang.
    """
    if not db.database_tersedia():
        raise HTTPException(
            status_code=503,
            detail=(
                "Routing memerlukan database. Isi DATABASE_URL di .env, "
                "jalankan db/schema.sql, lalu jalankan skrip 01 sampai 03."
            ),
        )
    with db.koneksi() as kon:
        ruas_semua = db.RepositoriRuas(kon).semua_untuk_routing()
    return routing.GrafJalan(ruas_semua)


@lru_cache(maxsize=1)
def _ambang_moda() -> dict:
    """Ambang kelayakan per moda, dibaca dari tabel ambang_moda.

    Aturan sesi ini: ambang tidak boleh ditulis tetap di dalam kode. Angka
    di tabel itu masih berstatus asumsi menurut komentar di schema.sql, jadi
    tim harus bisa mengoreksinya tanpa menyentuh kode.
    """
    with db.koneksi() as kon:
        return db.RepositoriRuas(kon).ambang_moda()


def _peta_kedalaman_penuh() -> dict:
    """Seluruh prediksi genangan pada rentang yang tersedia.

    Tidak di-cache karena isi tabel prediksi berubah tiap kali skrip data
    contoh dijalankan ulang, dan berubah lagi saat model asli masuk.
    Ukurannya hanya puluhan ribu baris, jadi memuatnya murah.
    """
    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        awal, akhir = repo.rentang_waktu()
        if awal is None:
            return {}
        return repo.peta_kedalaman(awal, akhir)


# ══════════════════════════════════════════════════════════════════════════
# GENANGAN
# ══════════════════════════════════════════════════════════════════════════
@app.get("/api/genangan")
def genangan(
    waktu: str | None = Query(
        default=None,
        description="Jam ISO 8601. Kosongkan untuk jam berjalan.",
    ),
) -> dict:
    """Ruas yang TERGENANG pada satu jam, sebagai GeoJSON.

    Berbeda dari /api/ruas yang mengirim seluruh jaringan. Endpoint ini
    hanya mengirim ruas yang berair, sehingga jauh lebih ringan dan cocok
    dipanggil berulang saat Pita Pasut digeser.
    """
    waktu_utc = _jam_bulat(_urai_waktu(waktu))

    if not db.database_tersedia():
        raise HTTPException(
            status_code=503,
            detail="Prediksi genangan memerlukan database.",
        )

    with db.koneksi() as kon:
        isi = db.RepositoriRuas(kon).geojson(waktu_utc)
        sumber = db.RepositoriGenangan(kon).sumber_yang_ada()

    basah = [f for f in isi["features"] if f["properties"]["kedalaman_cm"] > 0]
    return {
        "type": "FeatureCollection",
        "features": basah,
        "waktu_utc": waktu_utc.isoformat(),
        "waktu_wib": waktu_utc.astimezone(config.ZONA_WAKTU_LOKAL).isoformat(),
        "sumber_data": sumber,
        "jumlah_tergenang": len(basah),
    }


JAM_PITA_PASUT = 72


@app.get("/api/jam")
def jam_tersedia() -> dict:
    """Sumbu waktu Pita Pasut: 72 jam ke depan sejak jam berjalan.

    KENAPA JENDELANYA DIHITUNG DARI JAM BERJALAN, BUKAN DARI ISI TABEL.
    Tabel prediksi hanya menyimpan baris untuk ruas yang tergenang, jadi
    jam yang seluruh kotanya kering tidak punya baris sama sekali. Kalau
    rentang diambil dari nilai terkecil dan terbesar di tabel, jam kering di
    ujung jendela akan hilang dan Pita Pasut jadi lebih pendek dari 72 jam.

    Jadi jendelanya ditetapkan di sini, lalu diisi dengan apa pun yang ada.
    Jam tanpa baris berarti kering, bukan berarti data hilang.
    """
    if not db.database_tersedia():
        raise HTTPException(status_code=503, detail="Memerlukan database.")

    mulai = _jam_bulat(datetime.now(timezone.utc))

    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        ringkasan = repo.ringkasan_per_jam()
        sumber = repo.sumber_yang_ada()
        awal_tabel, akhir_tabel = repo.rentang_waktu()

    per_jam = {w: (n, m) for w, n, m in ringkasan}

    jam = []
    for i in range(JAM_PITA_PASUT):
        kursor = mulai + timedelta(hours=i)
        n, m = per_jam.get(kursor, (0, 0.0))
        jam.append({
            "waktu_utc": kursor.isoformat(),
            "ruas_tergenang": n,
            "kedalaman_maks_cm": round(m, 1),
            # Tinggi pasut dihitung dengan fungsi yang SAMA dengan yang
            # dipakai membuat data contoh, sehingga kurva Pita Pasut selalu
            # sejalan dengan genangan yang digambar di peta.
            "tinggi_pasut_m": round(float(pasut.tinggi_pasut_m(kursor)), 4),
        })

    selesai = mulai + timedelta(hours=JAM_PITA_PASUT - 1)
    # Kalau prediksi sudah kedaluwarsa, jangan diam-diam menampilkan pita
    # yang seluruhnya kering. Frontend perlu tahu bedanya antara benar-benar
    # kering dan datanya sudah lewat.
    tercakup = bool(
        awal_tabel and akhir_tabel
        and akhir_tabel >= mulai and awal_tabel <= selesai
    )

    return {
        "jam": jam,
        "sumber_data": sumber,
        "sumber_pasut": pasut.SUMBER,
        "mulai_utc": mulai.isoformat(),
        "selesai_utc": selesai.isoformat(),
        "prediksi_mencakup_jendela": tercakup,
        "prediksi_mulai_utc": awal_tabel.isoformat() if awal_tabel else None,
        "prediksi_selesai_utc": akhir_tabel.isoformat() if akhir_tabel else None,
    }


# ══════════════════════════════════════════════════════════════════════════
# RUTE
# ══════════════════════════════════════════════════════════════════════════
class PermintaanRute(BaseModel):
    asal: list[float] = Field(..., min_length=2, max_length=2,
                              description="[bujur, lintang]")
    tujuan: list[float] = Field(..., min_length=2, max_length=2,
                                description="[bujur, lintang]")
    waktu: str | None = Field(default=None, description="ISO 8601, jam berangkat")
    moda: str = Field(default="motor", description="motor atau mobil")


def _rute_ke_geojson(hasil: routing.HasilRute, jenis: str) -> dict:
    """Ubah satu hasil rute menjadi Feature GeoJSON."""
    return {
        "type": "Feature",
        "properties": {
            "jenis": jenis,
            "ditemukan": hasil.ditemukan,
            "alasan": hasil.alasan,
            "detik": round(hasil.detik, 1),
            "menit": round(hasil.detik / 60, 1),
            "jarak_m": round(hasil.jarak_m, 1),
            "jarak_km": round(hasil.jarak_m / 1000, 2),
            "jumlah_ruas": len(hasil.edge_ids),
            "ruas_tergenang": hasil.ruas_tergenang,
            "kedalaman_maks_cm": round(hasil.kedalaman_maks_cm, 1),
            "waktu_tiba_utc": (
                hasil.waktu_tiba.isoformat() if hasil.waktu_tiba else None
            ),
            "waktu_tiba_wib": (
                hasil.waktu_tiba.astimezone(config.ZONA_WAKTU_LOKAL).isoformat()
                if hasil.waktu_tiba else None
            ),
            "nama_jalan": hasil.nama_jalan[:12],
        },
        "geometry": (
            {"type": "LineString", "coordinates": hasil.koordinat}
            if hasil.koordinat else None
        ),
    }


@app.post("/api/rute")
def rute(permintaan: PermintaanRute) -> dict:
    """Hitung DUA rute: pembanding yang mengabaikan rob, dan yang sadar rob.

    Keduanya dikembalikan bersamaan dengan sengaja. Selisih antara keduanya
    adalah satu-satunya pijakan yang sah untuk angka dampak di M5.
    Menampilkan hanya rute sadar rob berarti mengklaim penghematan tanpa
    pembanding.
    """
    graf = _graf_routing()
    ambang_semua = _ambang_moda()

    if permintaan.moda not in ambang_semua:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Moda {permintaan.moda} tidak ada di tabel ambang_moda. "
                f"Yang tersedia: {', '.join(sorted(ambang_semua))}."
            ),
        )

    waktu_berangkat = _jam_bulat(_urai_waktu(permintaan.waktu))
    ambang = ambang_semua[permintaan.moda]
    peta_kedalaman = _peta_kedalaman_penuh()

    hasil = routing.dua_rute(
        graf,
        (permintaan.asal[0], permintaan.asal[1]),
        (permintaan.tujuan[0], permintaan.tujuan[1]),
        waktu_berangkat,
        ambang,
        peta_kedalaman,
    )

    if "galat" in hasil:
        raise HTTPException(
            status_code=422,
            detail={
                "kode": hasil["galat"],
                "jarak_m": round(hasil["jarak_m"], 1),
                "batas_m": routing.JARAK_MAKS_KE_JALAN_M,
            },
        )

    with db.koneksi() as kon:
        sumber = db.RepositoriGenangan(kon).sumber_yang_ada()

    abai: routing.HasilRute = hasil["rute_abai_rob"]
    sadar: routing.HasilRute = hasil["rute_sadar_rob"]
    keduanya_ada = abai.ditemukan and sadar.ditemukan

    return {
        "waktu_berangkat_utc": waktu_berangkat.isoformat(),
        "waktu_berangkat_wib": waktu_berangkat.astimezone(
            config.ZONA_WAKTU_LOKAL).isoformat(),
        "moda": permintaan.moda,
        "ambang_moda": ambang,
        # Selama nilainya masih memuat dummy, antarmuka WAJIB menampilkan
        # lencana DATA CONTOH. Tidak ada saklar manual yang bisa lupa
        # dimatikan sebelum demo.
        "sumber_data": sumber[0] if len(sumber) == 1 else sumber,
        "rute": {
            "type": "FeatureCollection",
            "features": [
                _rute_ke_geojson(abai, "rute_abai_rob"),
                _rute_ke_geojson(sadar, "rute_sadar_rob"),
            ],
        },
        "selisih": {
            "_catatan": (
                "Selisih rute sadar rob terhadap rute pembanding. Ini bahan "
                "mentah panel dampak di M5, bukan panel dampak itu sendiri."
            ),
            "tersedia": keduanya_ada,
            "menit": (
                round((sadar.detik - abai.detik) / 60, 1) if keduanya_ada else None
            ),
            "km": (
                round((sadar.jarak_m - abai.jarak_m) / 1000, 2)
                if keduanya_ada else None
            ),
            "sama_persis": keduanya_ada and abai.edge_ids == sadar.edge_ids,
        },
    }
