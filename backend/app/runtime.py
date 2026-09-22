"""Snapshot runtime terbatas: geometri sekali, prediksi sekali per versi.

Metadata cakupan adalah bagian dari publikasi data. Jam tanpa baris basah
hanya berarti kering bila jam tersebut dinyatakan lengkap oleh pembuat data.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from fastapi import HTTPException

from app import config, db
from app.domain import routing

BERKAS_POTRET = config.DIR_DATA_OLAHAN / "potret_demo.json"
TTL_DETIK = 60


def utc(waktu: datetime) -> datetime:
    return waktu.replace(tzinfo=timezone.utc) if waktu.tzinfo is None else waktu.astimezone(timezone.utc)


def jam_bulat(waktu: datetime) -> datetime:
    return utc(waktu).replace(minute=0, second=0, microsecond=0)


def tidak_tersedia() -> HTTPException:
    return HTTPException(503, detail={"kode": "data_tidak_tersedia",
        "pesan": "Data lengkap yang masih berlaku belum tersedia."})


@dataclass(frozen=True)
class Cakupan:
    versi: str
    jam: tuple[datetime, ...]
    sumber: tuple[str, ...]
    berlaku_sampai: datetime

    def __post_init__(self):
        if (not self.versi or not self.jam or not self.sumber
                or tuple(sorted(set(self.jam))) != self.jam
                or any(jam_bulat(j) != j for j in self.jam)
                or self.berlaku_sampai < self.akhir):
            raise ValueError("Metadata cakupan tidak lengkap atau tidak sah")

    @property
    def mulai(self):
        return self.jam[0]

    @property
    def akhir(self):
        return self.jam[-1] + timedelta(hours=1)

    def masih_berlaku(self, sekarang=None):
        return utc(sekarang or datetime.now(timezone.utc)) < self.berlaku_sampai

    def periksa(self, waktu, sekarang=None):
        if not self.masih_berlaku(sekarang):
            raise tidak_tersedia()
        if jam_bulat(waktu) not in self.jam:
            raise HTTPException(422, detail={"kode": "waktu_di_luar_cakupan",
                "pesan": "Waktu ini berada di luar cakupan data lengkap.",
                "mulai_utc": self.mulai.isoformat(),
                "akhir_eksklusif_utc": self.akhir.isoformat()})

    def metadata(self):
        return {"versi_data": self.versi, "sumber_data": list(self.sumber),
                "mulai_utc": self.mulai.isoformat(),
                "akhir_eksklusif_utc": self.akhir.isoformat()}

    def periksa_perjalanan(self, mulai, selesai):
        self.periksa(mulai)
        self.periksa(selesai)
        kursor = jam_bulat(mulai)
        while kursor < selesai:
            self.periksa(kursor)
            kursor += timedelta(hours=1)


class Jaringan:
    def __init__(self, fitur):
        if not fitur:
            raise ValueError("Jaringan jalan kosong")
        ids = set()
        for f in fitur:
            p, g = f['properties'], f['geometry']
            edge_id = int(p['edge_id'])
            if edge_id in ids or g['type'] != 'LineString' or len(g['coordinates']) < 2:
                raise ValueError("Identitas atau geometri ruas tidak sah")
            ids.add(edge_id)
            for nilai in (p['panjang_m'], p.get('kecepatan_kmh') if p.get('kecepatan_kmh') is not None else 30):
                if not math.isfinite(float(nilai)) or float(nilai) <= 0:
                    raise ValueError("Panjang/kecepatan ruas tidak sah")
            for lon, lat in g['coordinates']:
                if not math.isfinite(lon) or not math.isfinite(lat) or not -180 <= lon <= 180 or not -90 <= lat <= 90:
                    raise ValueError("Koordinat ruas tidak sah")
        self.fitur = fitur
        self.per_id = {int(f["properties"]["edge_id"]): f for f in fitur}
        self.graf = routing.GrafJalan({
            **f["properties"], "koordinat": f["geometry"]["coordinates"]
        } for f in fitur)
        # Hanya atribut yang dibutuhkan browser. Byte siap kirim tidak
        # diserialisasi ulang oleh FastAPI untuk setiap pengunjung.
        publik = [{"type": "Feature", "id": int(f["properties"]["edge_id"]),
                   "properties": {k: f["properties"].get(k)
                                  for k in ("edge_id", "nama", "jenis")},
                   "geometry": f["geometry"]} for f in fitur]
        self.json = json.dumps({"type": "FeatureCollection", "features": publik},
                               ensure_ascii=False, separators=(",", ":")).encode()
        # Format v2 menambah identitas ke payload; ETag lama harus gugur
        # agar browser tidak memakai respons 304 dengan payload format lama.
        self.versi = hashlib.sha256(b"jaringan-v2:" + self.json).hexdigest()[:20]
        # Identitas dataset harus berada di payload. Proxy kompresi boleh
        # mengubah ETag (misalnya menambah -gzip) untuk representasi HTTP.
        self.json = self.json[:-1] + b',"versi_jaringan":"' + self.versi.encode() + b'"}'


@dataclass(frozen=True)
class Dataset:
    cakupan: Cakupan
    jaringan: Jaringan
    prediksi: dict
    ambang: dict
    asal: str

    def __post_init__(self):
        jam = set(self.cakupan.jam)
        for w, nilai in self.prediksi.items():
            if w not in jam:
                raise ValueError("Prediksi di luar metadata")
            for edge_id, (kedalaman, peluang) in nilai.items():
                if (edge_id not in self.jaringan.per_id
                        or not math.isfinite(kedalaman) or kedalaman < 0
                        or not math.isfinite(peluang) or not 0 <= peluang <= 1):
                    raise ValueError("Nilai prediksi tidak sah")
        if not self.ambang:
            raise ValueError("Ambang moda kosong")
        for a in self.ambang.values():
            nilai = [float(a[k]) for k in ('lambat_cm', 'berisiko_cm',
                'tidak_bisa_lewat_cm', 'konsumsi_l_per_km', 'faktor_emisi_kg_per_l')]
            if (not all(math.isfinite(v) for v in nilai)
                    or not 0 <= nilai[0] <= nilai[1] < nilai[2]
                    or nilai[3] <= 0 or nilai[4] <= 0):
                raise ValueError("Ambang moda tidak sah")

    def periksa(self, waktu):
        self.cakupan.periksa(waktu)

    def kondisi(self, waktu):
        self.periksa(waktu)
        return self.prediksi.get(jam_bulat(waktu), {})


class PenyimpanRuntime:
    def __init__(self, berkas: Path = BERKAS_POTRET):
        self.berkas = berkas
        self._kunci = threading.Lock()
        self._dataset = None
        self._diperiksa = 0.0
        self._jaringan_db = None
        self._versi_jaringan_db = None
        self._potret = None
        self._cap_berkas = None

    def ambil(self):
        with self._kunci:
            # Lock juga menahan pemuatan pertama agar tidak ada duplikasi
            # graf ketika startup dan beberapa request tiba bersamaan.
            if self._dataset and time.monotonic() - self._diperiksa < TTL_DETIK:
                if not self._dataset.cakupan.masih_berlaku():
                    raise tidak_tersedia()
                return self._dataset
            data = None
            if config.DATABASE_URL:
                try:
                    data = self._dari_database()
                except (psycopg2.Error, db.DatabaseBelumDikonfigurasi, ValueError, KeyError, TypeError, OverflowError):
                    # Kegagalan di tengah query juga beralih ke potret.
                    pass
            if data is None:
                data = self._dari_potret()
            if not data.cakupan.masih_berlaku():
                raise tidak_tersedia()
            self._dataset = data
            self._diperiksa = time.monotonic()
            return data

    def _dari_database(self):
        with db.koneksi() as kon:
            # Metadata dan prediksi berasal dari satu snapshot transaksi,
            # termasuk ketika pipeline menerbitkan versi baru bersamaan.
            with kon.cursor() as kur:
                kur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            repo = db.RepositoriGenangan(kon)
            meta = repo.cakupan()
            if meta is None:
                return None
            cakupan = Cakupan(meta["versi"], tuple(meta["jam"]),
                              (meta["sumber"],), meta["akhir"])
            if not cakupan.masih_berlaku():
                return None
            if (self._dataset and self._dataset.asal == "database"
                    and self._dataset.cakupan.versi == cakupan.versi):
                return self._dataset
            versi_jaringan = db.RepositoriRuas(kon).versi_jaringan()
            jaringan = self._jaringan_db
            if jaringan is None or versi_jaringan != self._versi_jaringan_db:
                baris = db.RepositoriRuas(kon).semua_untuk_routing()
                fitur = [{"type": "Feature", "properties": {k: v for k, v in r.items()
                          if k != "koordinat"},
                          "geometry": {"type": "LineString", "coordinates": r["koordinat"]}}
                         for r in baris]
                jaringan = Jaringan(fitur)
            prediksi = repo.peta_kedalaman(cakupan.mulai, cakupan.akhir,
                                          sumber=meta["sumber"])
            ambang = db.RepositoriRuas(kon).ambang_moda()
            data = Dataset(cakupan, jaringan, prediksi, ambang, "database")
            self._jaringan_db, self._versi_jaringan_db = jaringan, versi_jaringan
            return data

    def _dari_potret(self):
        try:
            cap = (self.berkas.stat().st_mtime_ns, self.berkas.stat().st_size)
            if self._potret is not None and cap == self._cap_berkas:
                return self._potret
            d = json.loads(self.berkas.read_text(encoding="utf-8"))
            meta = d["cakupan"]
            jam = tuple(utc(datetime.fromisoformat(j)) for j in meta["jam_lengkap"])
            cakupan = Cakupan(meta["versi"], jam, tuple(d["sumber_data"]),
                              utc(datetime.fromisoformat(d["berlaku_sampai"])))
            prediksi = {utc(datetime.fromisoformat(w)): {
                int(e): (float(v[0]), float(v[1])) for e, v in nilai.items()
            } for w, nilai in d["genangan"].items()}
            if any(w not in jam for w in prediksi):
                raise ValueError("Prediksi di luar metadata")
            jaringan = Jaringan(d["ruas"]["features"])
            self._potret = Dataset(cakupan, jaringan, prediksi, d["ambang_moda"], "potret")
            self._cap_berkas = cap
            return self._potret
        except (OSError, KeyError, TypeError, ValueError, IndexError, OverflowError):
            raise tidak_tersedia() from None


penyimpan = PenyimpanRuntime()
