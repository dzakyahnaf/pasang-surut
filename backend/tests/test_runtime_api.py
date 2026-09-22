"""Regresi cakupan, cache dan pembatasan beban tanpa database/jaringan luar."""
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import httpx
import psycopg2
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import config, main, runtime
from app.batas_beban import BatasBeban


@pytest.fixture
def data(tmp_path, monkeypatch):
    awal = runtime.jam_bulat(datetime.now(timezone.utc)) + timedelta(hours=1)
    jam = [awal + timedelta(hours=i) for i in range(3)]
    feature = {"type": "Feature", "properties": {
        "edge_id": 1, "osm_u": 1, "osm_v": 2, "panjang_m": 100,
        "nama": "Jalan Uji", "jenis": "residential", "kecepatan_kmh": 36,
        "satu_arah": False},
        "geometry": {"type": "LineString", "coordinates": [[110.4,-6.95],[110.401,-6.95]]}}
    d = {"cakupan": {"versi": "uji-1", "jam_lengkap": [w.isoformat() for w in jam]},
         "berlaku_sampai": (jam[-1]+timedelta(hours=1)).isoformat(),
         "sumber_data": ["kerentanan_v1"],
         "ruas": {"type": "FeatureCollection", "features": [feature]},
         "genangan": {jam[0].isoformat(): {"1": [5, .5]}},
         "ambang_moda": {"motor": {"lambat_cm": 10, "berisiko_cm": 20,
             "tidak_bisa_lewat_cm": 30, "konsumsi_l_per_km": .02,
             "faktor_emisi_kg_per_l": 2.31}}}
    path = tmp_path / "potret.json"
    path.write_text(json.dumps(d), encoding="utf-8")
    monkeypatch.setattr(config, "DATABASE_URL", "")
    simpan = runtime.PenyimpanRuntime(path)
    monkeypatch.setattr(main, "penyimpan", simpan)
    return simpan, jam, path


@pytest.fixture
def client(data):
    with TestClient(main.app) as c:
        yield c


@pytest.mark.parametrize("jalur", ["/api/ruas", "/api/genangan", "/api/kondisi"])
def test_waktu_di_luar_cakupan_bukan_kering(client, data, jalur):
    _, jam, _ = data
    for w in [jam[0]-timedelta(seconds=1), jam[-1]+timedelta(hours=1),
              datetime(2099,1,1,tzinfo=timezone.utc)]:
        r = client.get(jalur, params={"waktu": w.isoformat()})
        assert r.status_code == 422
        assert r.json()["detail"]["kode"] == "waktu_di_luar_cakupan"


def test_jam_kering_lengkap_dan_batas_akhir(client, data):
    _, jam, _ = data
    for w in [jam[0], jam[1], jam[-1]+timedelta(minutes=59,seconds=59)]:
        assert client.get("/api/kondisi", params={"waktu": w.isoformat()}).status_code == 200
    assert client.get("/api/kondisi", params={"waktu": jam[1].isoformat()}).json()["ruas"] == []
    info = client.get("/api/jam").json()
    assert info["jam"][1]["tersedia"] and info["jam"][1]["ruas_tergenang"] == 0
    assert not info["jam"][3]["tersedia"] and info["jam"][3]["ruas_tergenang"] is None
    assert not info["prediksi_mencakup_jendela"]


def test_perjalanan_tidak_melompati_jam_yang_hilang(data):
    simpan, jam, _ = data
    cakupan = replace(simpan.ambil().cakupan, jam=(jam[0],jam[2]))
    with pytest.raises(HTTPException) as galat:
        cakupan.periksa_perjalanan(jam[0],jam[2])
    assert galat.value.status_code == 422


def test_cache_tidak_membuat_potret_kedaluwarsa_terus_berlaku(client, data, monkeypatch):
    simpan, jam, _ = data
    assert client.get("/api/kondisi", params={"waktu": jam[0].isoformat()}).status_code == 200
    monkeypatch.setattr(runtime.Cakupan, "masih_berlaku", lambda *a, **k: False)
    r = client.get("/api/kondisi", params={"waktu": jam[0].isoformat()})
    assert r.status_code == 503
    assert r.json()["detail"]["kode"] == "data_tidak_tersedia"


def test_tidak_ada_metadata_tidak_boleh_dianggap_kering(client, data):
    _, jam, path = data
    d = json.loads(path.read_text())
    del d["cakupan"]
    path.write_text(json.dumps(d))
    assert client.get("/api/kondisi", params={"waktu": jam[0].isoformat()}).status_code == 503


def test_rute_memeriksa_keberangkatan_dan_tiba(client, data):
    _, jam, _ = data
    body = {"asal": [110.4,-6.95], "tujuan": [110.401,-6.95], "moda": "motor"}
    for w in [datetime(2099,1,1,tzinfo=timezone.utc), jam[-1]+timedelta(minutes=59,seconds=55)]:
        assert client.post("/api/rute", json={**body,"waktu":w.isoformat()}).status_code == 422
    r = client.post("/api/rute", json={**body,"waktu":jam[1].isoformat()})
    assert r.status_code == 200
    assert r.json()["model_routing"] == "kondisi_jam_keberangkatan"
    assert r.json()["rute"]["features"][1]["properties"]["ditemukan"]


def test_geometri_statis_dan_kondisi_ringkas(client, data):
    _, jam, _ = data
    r = client.get("/api/jaringan")
    assert r.status_code == 200
    assert client.get("/api/jaringan", headers={"If-None-Match":r.headers["etag"]}).status_code == 304
    perubahan = client.get("/api/kondisi", params={"waktu":jam[0].isoformat()}).json()
    assert r.json()["versi_jaringan"] == perubahan["versi_jaringan"]
    assert perubahan["ruas"] == [[1,5,.5]]
    assert "geometry" not in json.dumps(perubahan)


def test_pemuatan_serentak_hanya_membangun_satu_snapshot(data, monkeypatch):
    simpan, _, _ = data
    asli = runtime.Jaringan
    spy = Mock(side_effect=asli)
    monkeypatch.setattr(runtime, "Jaringan", spy)
    with ThreadPoolExecutor(max_workers=6) as pool:
        hasil = list(pool.map(lambda _: simpan.ambil(), range(6)))
    assert len({id(d) for d in hasil}) == 1
    assert spy.call_count == 1


def test_database_putus_di_tengah_query_memakai_potret(data, monkeypatch):
    simpan, _, _ = data
    monkeypatch.setattr(config, "DATABASE_URL", "dummy-not-a-real-connection")
    monkeypatch.setattr(simpan, "_dari_database", Mock(side_effect=psycopg2.OperationalError("putus")))
    assert simpan.ambil().asal == "potret"


def test_data_versi_baru_menggantikan_cache_setelah_ttl(data, monkeypatch):
    simpan, jam, path = data
    lama = simpan.ambil()
    d = json.loads(path.read_text())
    d["cakupan"]["versi"] = "uji-2"
    d["genangan"][jam[1].isoformat()] = {"1": [20, .8]}
    path.write_text(json.dumps(d))
    monkeypatch.setattr(runtime, "TTL_DETIK", 0)
    baru = simpan.ambil()
    assert baru.cakupan.versi == "uji-2"
    assert baru.kondisi(jam[1])[1][0] == 20
    assert lama.kondisi(jam[1]) == {}


def test_beban_berlebih_ditolak_tanpa_antrean_dan_slot_pulih():
    async def scenario():
        mulai, selesai = asyncio.Event(), asyncio.Event()
        async def lambat(scope, receive, send):
            mulai.set()
            await selesai.wait()
            from starlette.responses import JSONResponse
            await JSONResponse({"ok":True})(scope,receive,send)
        app = BatasBeban(lambat, maksimum=1)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
            satu = asyncio.create_task(c.get("/api/rute"))
            await mulai.wait()
            dua = await c.get("/api/rute")
            assert dua.status_code == 503
            assert dua.json()["detail"]["kode"] == "server_sibuk"
            selesai.set()
            assert (await satu).status_code == 200
            assert (await c.get("/api/rute")).status_code == 200
    asyncio.run(scenario())
