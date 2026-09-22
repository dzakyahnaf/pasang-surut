"""API PASANG SURUT: data lengkap bertanggal dan routing kondisi jam berangkat."""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timedelta, timezone

# Harus sebelum impor domain pasut/NumPy. API hanya menghitung deret kecil;
# pool BLAS per inti host memboroskan memori pada VPS bersama. Pipeline
# pelatihan yang tidak mengimpor app.main tetap memakai konfigurasinya sendiri.
for _variabel_thread in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_variabel_thread, "1")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, field_validator

from app import config, db
from app.domain import dampak, pasut, routing
from app.runtime import penyimpan, utc, jam_bulat
from app.batas_beban import BatasBeban
from app.batas_isi import BatasIsi

app = FastAPI(title="PASANG SURUT", version="0.4.0")
app.add_middleware(BatasIsi)
app.add_middleware(BatasBeban, maksimum=2)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:4173", "http://127.0.0.1:4173"] + [
        a.strip() for a in os.getenv("ASAL_DIIZINKAN", "").split(",") if a.strip()],
    allow_origin_regex=os.getenv("ASAL_POLA") or None,
    allow_methods=["GET", "POST"], allow_headers=["*"],
    expose_headers=["ETag", "Retry-After"])

BERKAS_TUJUAN = config.DIR_DATA_OLAHAN / "tujuan_cepat.geojson"
BERKAS_METRIK = config.DIR_DATA_REFERENSI / "metrik_model.json"
BERKAS_INDEKS = config.DIR_DATA_OLAHAN / "indeks_kerentanan.json"


@app.exception_handler(RequestValidationError)
async def masukan_tidak_sah(request, exc):
    # Decoder JSON juga menerima konstanta NaN/Infinity nonstandar. Jangan
    # pantulkan input tersebut ke JSON galat: serialisasinya bisa menjadi 500.
    # Lokasi, jenis, dan pesan cukup untuk menjelaskan validasi kepada klien.
    return JSONResponse(status_code=422, content={"detail": [
        {k: e[k] for k in ("type", "loc", "msg") if k in e}
        for e in exc.errors()
    ]})

@app.on_event("shutdown")
async def tutup_koneksi():
    db.tutup_kolam()


def _urai_waktu(waktu):
    if waktu is None:
        return datetime.now(timezone.utc)
    try:
        return utc(datetime.fromisoformat(waktu))
    except (ValueError, OverflowError):
        raise HTTPException(400, detail="Gunakan waktu ISO 8601.") from None


@app.get("/api/kesehatan")
def kesehatan():
    hasil = {"status": "hidup", "versi": app.version,
             "commit": os.getenv("RENDER_GIT_COMMIT") or os.getenv("APP_COMMIT"),
             "waktu_server_utc": datetime.now(timezone.utc).isoformat(),
             "zona_waktu_tampilan": str(config.ZONA_WAKTU_LOKAL),
             "database": False, "data_tersedia": False,
             "aoi": {"bbox": list(config.bbox_aoi())}}
    try:
        data = penyimpan.ambil()
    except HTTPException:
        return hasil
    hasil.update({"database": data.asal == "database", "data_tersedia": True,
        "asal_jaringan": data.asal, "jumlah_ruas": len(data.jaringan.fitur),
        "jumlah_prediksi": sum(len(x) for x in data.prediksi.values()),
        "sumber_data": list(data.cakupan.sumber), "versi_data": data.cakupan.versi,
        "prediksi_mulai_utc": data.cakupan.mulai.isoformat(),
        "prediksi_selesai_utc": data.cakupan.jam[-1].isoformat(),
        "akhir_eksklusif_utc": data.cakupan.akhir.isoformat(),
        "potret_berlaku_sampai_utc": (data.cakupan.berlaku_sampai.isoformat()
                                        if data.asal == "potret" else None)})
    return hasil


@app.get("/api/jaringan")
def jaringan(request: Request):
    data = penyimpan.ambil()
    etag = '"' + data.jaringan.versi + '"'
    headers = {"ETag": etag, "Cache-Control": "public, max-age=0, must-revalidate"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(data.jaringan.json, media_type="application/geo+json", headers=headers)


@app.get("/api/kondisi")
def kondisi(waktu: str | None = None):
    data = penyimpan.ambil()
    waktu = jam_bulat(_urai_waktu(waktu))
    nilai = data.kondisi(waktu)
    return {**data.cakupan.metadata(), "waktu_utc": waktu.isoformat(),
            "versi_jaringan": data.jaringan.versi, "asal_jaringan": data.asal,
            "ruas": [[e, v[0], v[1]] for e, v in nilai.items() if v[0] > 0]}


def _geojson(waktu, hanya_basah=False):
    data = penyimpan.ambil()
    waktu = jam_bulat(_urai_waktu(waktu))
    nilai = data.kondisi(waktu)
    fitur = []
    for e, f in data.jaringan.per_id.items():
        k, p = nilai.get(e, (0.0, 0.0))
        if hanya_basah and k <= 0:
            continue
        fitur.append({"type": "Feature", "id": e, "geometry": f["geometry"],
            "properties": {**f["properties"], "kedalaman_cm": k,
                           "probabilitas": p, "sumber": data.cakupan.sumber[0]}})
    # Jalur kompatibilitas klien lama; klien baru tidak mengunduh ini per jam.
    return Response(json.dumps({"type": "FeatureCollection", "features": fitur,
        "waktu_utc": waktu.isoformat(), "asal_jaringan": data.asal,
        "sumber_data": list(data.cakupan.sumber),
        "jumlah_tergenang": sum(v[0] > 0 for v in nilai.values())},
        ensure_ascii=False, separators=(",", ":")), media_type="application/geo+json")


@app.get("/api/ruas")
def ruas(waktu: str | None = None):
    return _geojson(waktu)


@app.get("/api/genangan")
def genangan(waktu: str | None = None):
    return _geojson(waktu, hanya_basah=True)


@app.get("/api/jam")
def jam_tersedia():
    data = penyimpan.ambil()
    awal = (data.cakupan.mulai if data.asal == "potret"
            else jam_bulat(datetime.now(timezone.utc)))
    jam = []
    for i in range(72):
        w = awal + timedelta(hours=i)
        tersedia = w in data.cakupan.jam
        nilai = data.prediksi.get(w, {})
        jam.append({"waktu_utc": w.isoformat(), "tersedia": tersedia,
            "ruas_tergenang": sum(v[0] > 0 for v in nilai.values()) if tersedia else None,
            "kedalaman_maks_cm": max((v[0] for v in nilai.values()), default=0.0) if tersedia else None,
            "tinggi_pasut_m": round(float(pasut.tinggi_pasut_m(w)), 4) if tersedia else None})
    return {"jam": jam, **data.cakupan.metadata(), "asal_jaringan": data.asal,
            "prediksi_mencakup_jendela": all(j["tersedia"] for j in jam),
            "mulai_utc": awal.isoformat(), "selesai_utc": jam[-1]["waktu_utc"],
            "prediksi_mulai_utc": data.cakupan.mulai.isoformat(),
            "prediksi_selesai_utc": data.cakupan.jam[-1].isoformat()}


class PermintaanRute(BaseModel):
    asal: list[float] = Field(..., min_length=2, max_length=2)
    tujuan: list[float] = Field(..., min_length=2, max_length=2)
    waktu: str | None = None
    moda: str = "motor"

    @field_validator("asal", "tujuan")
    @classmethod
    def koordinat_sah(cls, nilai):
        if (not all(math.isfinite(x) for x in nilai)
                or not -180 <= nilai[0] <= 180 or not -90 <= nilai[1] <= 90):
            raise ValueError("Koordinat harus berhingga; bujur -180..180 dan lintang -90..90.")
        return nilai


def _jam_lebih_aman(data, permintaan, mulai, ambang):
    # Hanya ke depan, dalam horizon, dan rutenya dihitung ulang sesuai model.
    # Maksimal 24 kandidat; memakai snapshot/graf bersama tanpa query per jam.
    for langkah in range(1, 25):
        w = jam_bulat(mulai) + timedelta(hours=langkah)
        if jam_bulat(w) not in data.cakupan.jam:
            continue
        hasil = routing.dua_rute(data.jaringan.graf, tuple(permintaan.asal),
            tuple(permintaan.tujuan), w, ambang, data.prediksi)
        if "galat" in hasil:
            continue
        r = hasil["rute_sadar_rob"]
        if r.ditemukan and r.kedalaman_maks_cm < float(ambang["berisiko_cm"]):
            try:
                data.cakupan.periksa_perjalanan(w, r.waktu_tiba)
            except HTTPException:
                continue
            return {"waktu_utc": w.isoformat(),
                    "waktu_wib": w.astimezone(config.ZONA_WAKTU_LOKAL).isoformat(),
                    "geser_jam": langkah, "kedalaman_maks_cm": round(r.kedalaman_maks_cm, 1)}
    return None


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
    try:
        sumber = list(penyimpan.ambil().cakupan.sumber)
    except HTTPException:
        sumber = []
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
    data = penyimpan.ambil()
    graf = data.jaringan.graf
    ambang_semua = data.ambang

    if permintaan.moda not in ambang_semua:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Moda {permintaan.moda} tidak ada di tabel ambang_moda. "
                f"Yang tersedia: {', '.join(sorted(ambang_semua))}."
            ),
        )

    waktu_berangkat = utc(_urai_waktu(permintaan.waktu))
    data.periksa(waktu_berangkat)
    ambang = ambang_semua[permintaan.moda]
    peta_kedalaman = data.prediksi

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

    sumber = list(data.cakupan.sumber)

    abai: routing.HasilRute = hasil["rute_abai_rob"]
    sadar: routing.HasilRute = hasil["rute_sadar_rob"]
    for perjalanan in (abai, sadar):
        if perjalanan.ditemukan and perjalanan.waktu_tiba:
            data.cakupan.periksa_perjalanan(waktu_berangkat, perjalanan.waktu_tiba)
    keduanya_ada = abai.ditemukan and sadar.ditemukan

    # Rute sadar rob menghindari genangan sebisanya, tetapi tidak selalu bisa.
    # Kalau ia tetap menembus, pengguna berhak tahu SEBELUM berangkat, bukan
    # setelah rodanya masuk air.
    paparan = dampak.paparan(sadar.kedalaman_per_ruas_cm, ambang)
    jam_aman = (
        _jam_lebih_aman(data, permintaan, waktu_berangkat, ambang)
        if paparan["menembus"] else None
    )

    return {
        "waktu_berangkat_utc": waktu_berangkat.isoformat(),
        "waktu_berangkat_wib": waktu_berangkat.astimezone(
            config.ZONA_WAKTU_LOKAL).isoformat(),
        "moda": permintaan.moda,
        "versi_data": data.cakupan.versi,
        "versi_jaringan": data.jaringan.versi,
        "asal_jaringan": data.asal,
        "model_routing": "kondisi_jam_keberangkatan",
        "batas_model": "Kondisi jam keberangkatan dipakai sepanjang rute; perubahan selama perjalanan belum dimodelkan.",
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
            if keduanya_ada else None
        ),
        "paparan": paparan,
        "jam_lebih_aman": jam_aman,
    }
