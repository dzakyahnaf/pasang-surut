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
import os
from datetime import datetime, timedelta, timezone
import threading
import time
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config, db
from app.domain import dampak, pasut, routing

app = FastAPI(
    title="PASANG SURUT",
    description="Perutean sadar rob untuk Semarang pesisir",
    version="0.3.0",
)

# Frontend berjalan di port lain saat pengembangan, jadi peramban
# memperlakukannya sebagai asal yang berbeda dan memblokir permintaan tanpa
# izin CORS. Daftar ini hanya berisi alamat pengembangan lokal.
# Asal yang diizinkan dibaca dari lingkungan, dipisah koma, supaya alamat
# frontend produksi tidak perlu masuk ke dalam kode. Dua alamat pengembangan
# selalu ikut karena keduanya tidak berbahaya dan menghemat satu langkah
# konfigurasi tiap kali orang baru menjalankan repo ini.
#
# Daftar putih dipakai, BUKAN "*". Endpoint /api/rute menerima POST, dan
# mengizinkan semua asal berarti situs mana pun bisa memakainya sebagai
# mesin routing gratis atas biaya kuota Supabase kita.
_ASAL_PENGEMBANGAN = ["http://localhost:5173", "http://127.0.0.1:5173"]
_ASAL_PRODUKSI = [
    a.strip() for a in os.getenv("ASAL_DIIZINKAN", "").split(",") if a.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ASAL_PENGEMBANGAN + _ASAL_PRODUKSI,
    # Pratinjau Vercel memakai subdomain yang berubah tiap penerapan, jadi
    # polanya diizinkan sekalian. Hanya subdomain vercel.app, bukan mana pun.
    allow_origin_regex=os.getenv("ASAL_POLA") or None,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

BERKAS_GEOJSON = config.DIR_DATA_OLAHAN / "ruas_jalan.geojson"
BERKAS_TUJUAN = config.DIR_DATA_OLAHAN / "tujuan_cepat.geojson"
BERKAS_METRIK = config.DIR_DATA_REFERENSI / "metrik_model.json"
BERKAS_INDEKS = config.DIR_DATA_OLAHAN / "indeks_kerentanan.json"
BERKAS_POTRET = config.DIR_DATA_OLAHAN / "potret_demo.json"


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
def _potret() -> dict | None:
    """Potret beku dari skrip 18, dipakai HANYA bila database tidak terjangkau.

    KENAPA ADA, DAN KENAPA BERTANGGAL.

    Aplikasi ini dinilai di ruangan yang jaringannya bukan milik kita, sambil
    menghubungi database di Sydney. Dua hal bisa gagal bersamaan tepat saat
    juri memakainya. Potret ini membuat peta, sumbu waktu, genangan, dan
    perutean tetap hidup tanpa satu pun kueri.

    Tanggal kedaluwarsanya BUKAN kehati-hatian berlebihan. Sistem ini
    menyarankan kapan orang boleh menembus air; menampilkan prediksi minggu
    lalu seolah-olah berlaku hari ini lebih berbahaya daripada layar kosong.
    Lewat `berlaku_sampai`, potret ditolak dan API mengembalikan galat yang
    menjelaskan apa yang harus dijalankan.
    """
    if not BERKAS_POTRET.exists():
        return None
    try:
        d = json.loads(BERKAS_POTRET.read_text(encoding="utf-8"))
        sampai = datetime.fromisoformat(d["berlaku_sampai"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return None
    if datetime.now(timezone.utc) > sampai:
        return None
    return d


def _potret_kedaluwarsa() -> bool:
    """True bila potret ada tetapi sudah lewat masa berlakunya."""
    if not BERKAS_POTRET.exists():
        return False
    try:
        d = json.loads(BERKAS_POTRET.read_text(encoding="utf-8"))
        return datetime.now(timezone.utc) > datetime.fromisoformat(
            d["berlaku_sampai"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return False


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
        "asal_jaringan": "potret" if _potret() is not None else "berkas",
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
    elif _potret() is not None:
        # Jalur cadangan UTAMA: potret beku memuat ruas DAN genangannya, jadi
        # peta tampil lengkap tanpa database. Ini yang dipakai saat demo.
        potret = _potret()
        per_ruas = potret["genangan"].get(waktu_utc.isoformat(), {})
        fitur = []
        for f in potret["ruas"]["features"]:
            sifat = dict(f["properties"])
            nilai = per_ruas.get(str(sifat["edge_id"]))
            sifat["kedalaman_cm"] = nilai[0] if nilai else 0.0
            sifat["probabilitas"] = nilai[1] if nilai else 0.0
            sifat["sumber"] = potret["sumber_data"][0] if nilai else None
            fitur.append({"type": "Feature", "id": sifat["edge_id"],
                          "properties": sifat, "geometry": f["geometry"]})
        isi = {"type": "FeatureCollection", "features": fitur}
        sumber = potret["sumber_data"]
        asal = "potret"
    else:
        # Jalur cadangan TERAKHIR: hanya geometri jalan, tanpa prediksi sama
        # sekali, jadi seluruh ruas dilaporkan kering. Peta tetap tampil.
        # Dipakai kalau potret pun tidak ada atau sudah kedaluwarsa.
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
    if db.database_tersedia():
        with db.koneksi() as kon:
            ruas_semua = db.RepositoriRuas(kon).semua_untuk_routing()
        return routing.GrafJalan(ruas_semua)

    # Database tidak terjangkau. Graf dibangun dari potret beku, sehingga
    # perutean tetap MENGHITUNG SUNGGUHAN — bukan mengembalikan rute yang
    # sudah disiapkan untuk pasangan titik pilihan kita sendiri. Juri boleh
    # mengetuk titik mana pun.
    potret = _potret()
    if potret is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Routing memerlukan database atau potret demo yang masih "
                "berlaku. Jalankan `python -m scripts.18_seed_demo` dari "
                "backend/, atau perbaiki DATABASE_URL."
                + (" Potret yang ada sudah kedaluwarsa."
                   if _potret_kedaluwarsa() else "")
            ),
        )
    ruas_semua = []
    for f in potret["ruas"]["features"]:
        sifat = f["properties"]
        ruas_semua.append({
            "edge_id": int(sifat["edge_id"]),
            "osm_u": int(sifat.get("osm_u", 0)),
            "osm_v": int(sifat.get("osm_v", 0)),
            "nama": sifat.get("nama"),
            "jenis": sifat.get("jenis"),
            "panjang_m": float(sifat["panjang_m"]),
            "kecepatan_kmh": float(sifat.get("kecepatan_kmh") or 30.0),
            "satu_arah": bool(sifat.get("satu_arah")),
            "koordinat": f["geometry"]["coordinates"],
        })
    return routing.GrafJalan(ruas_semua)


@lru_cache(maxsize=1)
def _ambang_moda() -> dict:
    """Ambang kelayakan per moda, dibaca dari tabel ambang_moda.

    Aturan sesi ini: ambang tidak boleh ditulis tetap di dalam kode. Angka
    di tabel itu masih berstatus asumsi menurut komentar di schema.sql, jadi
    tim harus bisa mengoreksinya tanpa menyentuh kode.
    """
    if db.database_tersedia():
        with db.koneksi() as kon:
            return db.RepositoriRuas(kon).ambang_moda()
    potret = _potret()
    if potret is None:
        raise HTTPException(
            status_code=503,
            detail="Ambang moda memerlukan database atau potret demo.",
        )
    return potret["ambang_moda"]


def _peta_kedalaman_penuh() -> dict:
    """Seluruh prediksi genangan pada rentang yang tersedia.

    Tidak di-cache karena isi tabel prediksi berubah tiap kali skrip data
    contoh dijalankan ulang, dan berubah lagi saat model asli masuk.
    Ukurannya hanya puluhan ribu baris, jadi memuatnya murah.
    """
    if db.database_tersedia():
        with db.koneksi() as kon:
            repo = db.RepositoriGenangan(kon)
            awal, akhir = repo.rentang_waktu()
            if awal is None:
                return {}
            return repo.peta_kedalaman(awal, akhir)

    # Bentuknya disamakan persis dengan yang dikembalikan repositori, yaitu
    # { datetime: { edge_id: (kedalaman, probabilitas) } }, supaya mesin
    # routing tidak perlu tahu dari mana angkanya datang.
    potret = _potret()
    if potret is None:
        return {}
    return {
        datetime.fromisoformat(w): {
            int(e): (v[0], v[1]) for e, v in per_ruas.items()
        }
        for w, per_ruas in potret["genangan"].items()
    }


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

    if db.database_tersedia():
        with db.koneksi() as kon:
            isi = db.RepositoriRuas(kon).geojson(waktu_utc)
            sumber = db.RepositoriGenangan(kon).sumber_yang_ada()
    else:
        potret = _potret()
        if potret is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Prediksi genangan memerlukan database atau potret demo "
                    "yang masih berlaku."
                    + (" Potret yang ada sudah kedaluwarsa."
                       if _potret_kedaluwarsa() else "")
                ),
            )
        per_ruas = potret["genangan"].get(waktu_utc.isoformat(), {})
        fitur = []
        for f in potret["ruas"]["features"]:
            sifat = dict(f["properties"])
            nilai = per_ruas.get(str(sifat["edge_id"]))
            sifat["kedalaman_cm"] = nilai[0] if nilai else 0.0
            sifat["probabilitas"] = nilai[1] if nilai else 0.0
            sifat["sumber"] = potret["sumber_data"][0] if nilai else None
            fitur.append({"type": "Feature", "id": sifat["edge_id"],
                          "properties": sifat, "geometry": f["geometry"]})
        isi = {"type": "FeatureCollection", "features": fitur}
        sumber = potret["sumber_data"]

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


# Cache sumbu waktu. Umurnya pendek dengan sengaja.
#
# `/api/jam` adalah panggilan PERTAMA setiap pengunjung, dan isinya hanya
# berubah saat skrip data dijalankan ulang. Tanpa cache, setiap pemuatan
# halaman menembus database — dan saat beberapa orang membuka aplikasi
# bersamaan, kelima koneksi kolam terpakai untuk menjawab pertanyaan yang
# jawabannya sama persis.
#
# Diukur: 20 permintaan serentak menghasilkan sebagian HTTP 500 sebelum
# cache ini ada. TTL 60 detik dipilih karena jendela 72 jam hanya bergeser
# saat jamnya berganti, jadi data basi paling lama satu menit dan itu tidak
# pernah mengubah apa yang dilihat pengguna.
_CACHE_JAM_DETIK = 60.0
_cache_jam: tuple[float, dict] | None = None
_kunci_jam = threading.Lock()


@app.get("/api/jam")
def jam_tersedia() -> dict:
    """Pembungkus ber-cache. Perhitungan sesungguhnya ada di `_hitung_jam()`."""
    global _cache_jam
    sekarang = time.monotonic()
    tersimpan = _cache_jam
    if tersimpan is not None and sekarang - tersimpan[0] < _CACHE_JAM_DETIK:
        return tersimpan[1]
    with _kunci_jam:
        # Diperiksa ulang: utas lain bisa sudah mengisinya sementara menunggu.
        tersimpan = _cache_jam
        if tersimpan is not None and time.monotonic() - tersimpan[0] < _CACHE_JAM_DETIK:
            return tersimpan[1]
        hasil = _hitung_jam()
        _cache_jam = (time.monotonic(), hasil)
        return hasil


def _hitung_jam() -> dict:
    """Sumbu waktu Pita Pasut: 72 jam ke depan sejak jam berjalan.

    KENAPA JENDELANYA DIHITUNG DARI JAM BERJALAN, BUKAN DARI ISI TABEL.
    Tabel prediksi hanya menyimpan baris untuk ruas yang tergenang, jadi
    jam yang seluruh kotanya kering tidak punya baris sama sekali. Kalau
    rentang diambil dari nilai terkecil dan terbesar di tabel, jam kering di
    ujung jendela akan hilang dan Pita Pasut jadi lebih pendek dari 72 jam.

    Jadi jendelanya ditetapkan di sini, lalu diisi dengan apa pun yang ada.
    Jam tanpa baris berarti kering, bukan berarti data hilang.
    """
    mulai = _jam_bulat(datetime.now(timezone.utc))
    asal = "database"

    if db.database_tersedia():
        with db.koneksi() as kon:
            repo = db.RepositoriGenangan(kon)
            ringkasan = repo.ringkasan_per_jam()
            sumber = repo.sumber_yang_ada()
            awal_tabel, akhir_tabel = repo.rentang_waktu()
        per_jam = {w: (n, m) for w, n, m in ringkasan}
    else:
        potret = _potret()
        if potret is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Memerlukan database atau potret demo yang masih berlaku."
                    + (" Potret yang ada sudah kedaluwarsa; jalankan "
                       "`python -m scripts.18_seed_demo`."
                       if _potret_kedaluwarsa() else "")
                ),
            )
        asal = "potret"
        sumber = potret["sumber_data"]
        # Potret dibekukan pada jam tertentu. Sumbu waktu mengikuti potret,
        # bukan jam berjalan, supaya jam yang ditampilkan benar-benar punya
        # prediksi di belakangnya.
        mulai = datetime.fromisoformat(potret["mulai"])
        awal_tabel = mulai
        akhir_tabel = datetime.fromisoformat(potret["selesai"])
        per_jam = {
            datetime.fromisoformat(j["waktu_utc"]):
                (j["ruas_tergenang"], j["kedalaman_maks_cm"])
            for j in potret["jam"]
        }

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


def _jam_lebih_aman(edge_ids: list[int], mulai, ambang: dict,
                    peta_kedalaman: dict, batas: int = 24) -> dict | None:
    """Cari jam terdekat yang genangannya di bawah ambang berisiko moda ini.

    Menyarankan "berangkat nanti saja" tanpa menyebut jam berapa adalah saran
    kosong. Fungsi ini menelusuri jam-jam yang prediksinya sudah ada, ke depan
    dan ke belakang secara berselang-seling, lalu mengembalikan yang PERTAMA
    ditemukan aman — jadi yang disarankan selalu jam terdekat, bukan sekadar
    jam mana pun yang kebetulan aman.

    Yang diperiksa hanya ruas yang benar-benar dilewati rute, bukan seluruh
    kota. Jam bisa saja buruk di tempat lain dan tetap aman di jalur ini.
    """
    berisiko = float(ambang["berisiko_cm"])
    urutan = []
    for langkah in range(1, batas + 1):
        urutan.append(timedelta(hours=langkah))
        urutan.append(timedelta(hours=-langkah))

    for geser in urutan:
        waktu = mulai + geser
        per_jam = peta_kedalaman.get(waktu)
        if per_jam is None:
            continue
        maks = 0.0
        for e in edge_ids:
            nilai = per_jam.get(e)
            if nilai:
                maks = max(maks, nilai[0])
        if maks < berisiko:
            return {
                "waktu_utc": waktu.isoformat(),
                "waktu_wib": waktu.astimezone(config.ZONA_WAKTU_LOKAL).isoformat(),
                "geser_jam": int(geser.total_seconds() // 3600),
                "kedalaman_maks_cm": round(maks, 1),
            }
    return None


@app.get("/api/tujuan-cepat")
def tujuan_cepat() -> dict:
    """Titik tujuan penting, dibaca dari berkas yang disiapkan skrip 17.

    Titiknya sudah dilekatkan ke simpul jalan terdekat saat disiapkan,
    sehingga tombol tujuan cepat tidak pernah mengembalikan galat "terlalu
    jauh dari jalan". Berkasnya luring; tidak ada panggilan OSM di sini.
    """
    if not BERKAS_TUJUAN.exists():
        return {"tersedia": False, "tujuan": [],
                "_catatan": ("Berkas tujuan cepat belum ada. Jalankan "
                             "python -m scripts.17_tujuan_cepat")}
    isi = json.loads(BERKAS_TUJUAN.read_text(encoding="utf-8"))
    return {
        "tersedia": True,
        "tujuan": [{
            "kunci": f["properties"]["kunci"],
            "label": f["properties"]["label"],
            "ikon": f["properties"]["ikon"],
            "lon": f["geometry"]["coordinates"][0],
            "lat": f["geometry"]["coordinates"][1],
            "geser_m": f["properties"].get("geser_m"),
        } for f in isi["features"]],
    }


@app.get("/api/validasi")
def validasi() -> dict:
    """Metrik model dan indeks, apa adanya.

    ATURAN REPO NOMOR 1 DITEGAKKAN DI SINI, BUKAN DI ANTARMUKA. Bila model
    belum ada, endpoint ini mengembalikan tersedia=false dan SELURUH metrik
    null. Antarmuka tidak punya kesempatan untuk menampilkan angka karangan
    karena tidak ada angka yang dikirim kepadanya.

    Model yang ada sekarang berstatus DITOLAK, dan itu dinyatakan terbuka
    lewat medan `dipakai`. Metriknya tetap dikirim justru supaya bisa
    ditampilkan beserta alasan penolakannya.
    """
    kosong = {
        "tersedia": False, "dipakai": False, "alasan_ditolak": None,
        "roc_auc": None, "pr_auc": None, "f1": None,
        "ambang_probabilitas": None, "matriks_konfusi": None,
        "baris_latih": None, "baris_uji": None,
        "periode_latih": None, "periode_uji": None,
        "kepentingan_fitur": [], "pembanding_naif": {},
        "kalibrasi": None, "sumber_label": None,
    }
    if not BERKAS_METRIK.exists():
        return kosong

    m = json.loads(BERKAS_METRIK.read_text(encoding="utf-8"))
    uji = m.get("metrik_uji", {})
    pemisahan = m.get("pemisahan", {})
    label = m.get("label_info") or m.get("label", "")

    # Halaman validasi harus tetap terbuka meski database mati; justru saat
    # demo bermasalah itulah juri paling mungkin membuka halaman ini.
    if db.database_tersedia():
        with db.koneksi() as kon:
            sumber = db.RepositoriGenangan(kon).sumber_yang_ada()
    else:
        potret = _potret()
        sumber = potret["sumber_data"] if potret else []
    dipakai = "model_v1" in sumber

    indeks = None
    if BERKAS_INDEKS.exists():
        d = json.loads(BERKAS_INDEKS.read_text(encoding="utf-8"))
        indeks = {"bobot": d.get("bobot"), "sebaran": d.get("sebaran"),
                  "ruas": d.get("ruas"), "peringatan": d.get("_peringatan", [])}

    return {
        "tersedia": True,
        "dipakai": dipakai,
        "alasan_ditolak": (None if dipakai else (
            "Label basah Sentinel-1 tidak berkorelasi dengan pasang surut. "
            "Aturan pasut saja menghasilkan ROC-AUC 0,4935 dan kepentingan "
            "permutasi ketiga fitur waktu nol dalam batas ketidakpastiannya. "
            "Rinciannya di docs/validasi.md bagian 6.")),
        "sumber_data_aktif": sumber,
        "model": m.get("model"),
        "dilatih": m.get("dilatih"),
        "roc_auc": uji.get("roc_auc"),
        "pr_auc": uji.get("pr_auc"),
        "proporsi_dasar": uji.get("proporsi_dasar_pr"),
        "f1": uji.get("f1"),
        "ambang_probabilitas": uji.get("ambang_probabilitas"),
        "matriks_konfusi": uji.get("matriks_konfusi"),
        "baris_latih": pemisahan.get("baris_latih"),
        "baris_uji": pemisahan.get("baris_uji"),
        "citra_latih": pemisahan.get("citra_latih"),
        "citra_uji": pemisahan.get("citra_uji"),
        "periode_latih": pemisahan.get("latih"),
        "periode_uji": pemisahan.get("uji"),
        "cara_pemisahan": pemisahan.get("cara"),
        "kepentingan_fitur": m.get("kepentingan_fitur", []),
        "pembanding_naif": m.get("pembanding_naif_roc_auc", {}),
        "kalibrasi": m.get("kalibrasi"),
        "sumber_label": (m.get("label") or {}).get("cara")
        if isinstance(m.get("label"), dict) else None,
        "peringatan": m.get("_peringatan", []),
        "indeks_kerentanan": indeks,
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

    # Sumber data menentukan lencana peringatan di antarmuka, jadi ia tidak
    # boleh menggagalkan permintaan rute saat database mati. Potret membawa
    # daftarnya sendiri.
    if db.database_tersedia():
        with db.koneksi() as kon:
            sumber = db.RepositoriGenangan(kon).sumber_yang_ada()
    else:
        potret = _potret()
        sumber = potret["sumber_data"] if potret else []

    abai: routing.HasilRute = hasil["rute_abai_rob"]
    sadar: routing.HasilRute = hasil["rute_sadar_rob"]
    keduanya_ada = abai.ditemukan and sadar.ditemukan

    # Rute sadar rob menghindari genangan sebisanya, tetapi tidak selalu bisa.
    # Kalau ia tetap menembus, pengguna berhak tahu SEBELUM berangkat, bukan
    # setelah rodanya masuk air.
    paparan = dampak.paparan(sadar.kedalaman_per_ruas_cm, ambang)
    jam_aman = (
        _jam_lebih_aman(sadar.edge_ids, waktu_berangkat, ambang, peta_kedalaman)
        if paparan["menembus"] else None
    )

    return {
        "waktu_berangkat_utc": waktu_berangkat.isoformat(),
        "waktu_berangkat_wib": waktu_berangkat.astimezone(
            config.ZONA_WAKTU_LOKAL).isoformat(),
        "moda": permintaan.moda,
        "ambang_moda": ambang,
        # SELALU LIST, TIDAK PERNAH STRING.
        #
        # Sebelumnya baris ini memadatkan list bersatu anggota menjadi string
        # sebagai "kemudahan". Akibatnya fatal dan tidak kentara: endpoint
        # /api/ruas mengembalikan ["kerentanan_v1"] sementara endpoint ini
        # mengembalikan "kerentanan_v1", dan LencanaContoh.jsx menolak yang
        # bukan array. Lencana peringatan karena itu HILANG tepat setelah
        # pengguna menghitung rute — di tengah alur demo, pada layar yang
        # dilihat juri.
        #
        # Aturan repo nomor 2 menuntut lencana muncul selama sumbernya belum
        # model tervalidasi. Bentuk data yang tidak konsisten antar endpoint
        # membatalkan jaminan itu tanpa satu pun galat yang terlihat.
        "sumber_data": sumber,
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
        "dampak": (
            dampak.hitung((sadar.detik - abai.detik) / 60,
                          (sadar.jarak_m - abai.jarak_m) / 1000, ambang)
            if keduanya_ada else {"berarti": False}
        ),
        "paparan": paparan,
        "jam_lebih_aman": jam_aman,
    }
