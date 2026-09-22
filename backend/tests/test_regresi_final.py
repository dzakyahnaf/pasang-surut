"""Kasus audit final: data rusak, input besar, dan makna hasil routing."""
import json
import asyncio
from copy import deepcopy
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from app import main, runtime, db
from app.batas_isi import BatasIsi
from app.domain import routing
from tests.test_runtime_api import data, client


def ubah_potret(data, ubah):
    _, _, path = data
    isi = json.loads(path.read_text())
    ubah(isi)
    path.write_text(json.dumps(isi))


@pytest.mark.parametrize("nilai", [[float('nan'), .5], [-1, .5], [5, 1.2], [5], [5, float('inf')]])
def test_prediksi_rusak_tidak_dianggap_kering(client, data, nilai):
    _, jam, _ = data
    ubah_potret(data, lambda d: d['genangan'][jam[0].isoformat()].update({'1': nilai}))
    r = client.get('/api/kondisi', params={'waktu': jam[0].isoformat()})
    assert r.status_code == 503
    assert r.json()['detail']['kode'] == 'data_tidak_tersedia'


def test_prediksi_ruas_tak_dikenal_ditolak(client, data):
    _, jam, _ = data
    ubah_potret(data, lambda d: d['genangan'][jam[0].isoformat()].update({'999': [20, .9]}))
    assert client.get('/api/kondisi', params={'waktu': jam[0].isoformat()}).status_code == 503


def test_jaringan_terputus_bukan_seluruh_jalur_tergenang(client, data):
    _, jam, _ = data
    def putus(d):
        f = deepcopy(d['ruas']['features'][0])
        f['properties'].update(edge_id=2, osm_u=3, osm_v=4)
        f['geometry']['coordinates'] = [[110.403, -6.95], [110.404, -6.95]]
        d['ruas']['features'].append(f)
    ubah_potret(data, putus)
    r = client.post('/api/rute', json={'asal': [110.4, -6.95], 'tujuan': [110.404, -6.95],
                                     'waktu': jam[1].isoformat()})
    assert r.status_code == 200
    hasil = r.json()
    assert hasil['rute']['features'][1]['properties']['alasan'] == 'tidak_terhubung'
    assert hasil['dampak'] is None


def test_rute_membawa_versi_jaringan(client, data):
    _, jam, _ = data
    r = client.post('/api/rute', json={'asal': [110.4, -6.95], 'tujuan': [110.401, -6.95],
                                     'waktu': jam[1].isoformat()})
    assert r.json()['versi_jaringan'] == client.get('/api/jaringan').json()['versi_jaringan']


def test_isi_permintaan_besar_ditolak_sebelum_parse(client, data, monkeypatch):
    def tidak_boleh():
        pytest.fail('Permintaan terlalu besar tidak boleh memuat dataset')
    monkeypatch.setattr(main.penyimpan, 'ambil', tidak_boleh)
    r = client.post('/api/rute', content=b'{"padding":"' + b'x' * 20000 + b'"}')
    assert r.status_code == 413


def test_saran_jam_dibulatkan_ke_jam_data(data):
    simpan, jam, _ = data
    permintaan = main.PermintaanRute(asal=[110.4, -6.95], tujuan=[110.401, -6.95])
    d = simpan.ambil()
    saran = main._jam_lebih_aman(d, permintaan, jam[0] + timedelta(minutes=23), d.ambang['motor'])
    assert saran['waktu_utc'] == jam[1].isoformat()


def test_publikasi_baru_memeriksa_perubahan_jaringan(data, monkeypatch):
    simpan, jam, path = data
    isi = json.loads(path.read_text())
    fitur = isi['ruas']['features'][0]
    ruas = MagicMock()
    ruas.versi_jaringan.return_value = 'graf-1'
    ruas.semua_untuk_routing.return_value = [{**fitur['properties'], 'koordinat': fitur['geometry']['coordinates']}]
    ruas.ambang_moda.return_value = isi['ambang_moda']
    prediksi = MagicMock()
    meta = {'versi': 'v1', 'jam': jam, 'sumber': 'kerentanan_v1', 'akhir': jam[-1] + timedelta(hours=1)}
    prediksi.cakupan.return_value = meta
    prediksi.peta_kedalaman.return_value = {}
    @contextmanager
    def koneksi():
        yield MagicMock()
    monkeypatch.setattr(db, 'koneksi', koneksi)
    monkeypatch.setattr(db, 'RepositoriRuas', lambda _: ruas)
    monkeypatch.setattr(db, 'RepositoriGenangan', lambda _: prediksi)
    pertama = simpan._dari_database()
    simpan._dataset = pertama
    meta['versi'] = 'v2'
    kedua = simpan._dari_database()
    assert kedua.jaringan is pertama.jaringan
    assert ruas.semua_untuk_routing.call_count == 1
    simpan._dataset = kedua
    meta['versi'] = 'v3'
    ruas.versi_jaringan.return_value = 'graf-2'
    ruas.semua_untuk_routing.return_value[0]['nama'] = 'Jalan diperbarui'
    ketiga = simpan._dari_database()
    assert ketiga.jaringan.versi != pertama.jaringan.versi
    assert ketiga.jaringan.per_id[1]['properties']['nama'] == 'Jalan diperbarui'


@pytest.mark.parametrize('headers', [[], [(b'content-length', b'1')]])
def test_body_streaming_tetap_dibatasi_walau_header_hilang_atau_palsu(headers):
    async def skenario():
        def tidak_dipanggil(*_):
            pytest.fail('Parser tidak boleh berjalan')
        app = BatasIsi(tidak_dipanggil, maksimum=16)
        keluaran = []
        async def receive():
            return {'type': 'http.request', 'body': b'x' * 9, 'more_body': True}
        async def send(pesan):
            keluaran.append(pesan)
        await app({'type': 'http', 'path': '/api/rute', 'method': 'POST', 'headers': headers}, receive, send)
        assert keluaran[0]['status'] == 413
    asyncio.run(skenario())


def test_body_terlalu_lambat_tidak_menahan_slot_selamanya():
    async def skenario():
        keluaran = []
        async def receive():
            await asyncio.Event().wait()
        async def send(pesan):
            keluaran.append(pesan)
        await BatasIsi(None, detik=.01)({'type': 'http', 'path': '/api/rute', 'method': 'POST'}, receive, send)
        assert keluaran[0]['status'] == 408
    asyncio.run(skenario())
