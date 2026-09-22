"""Masukan ekstrem ditolak sebelum menyentuh dataset atau mesin routing."""
import json

import pytest
from fastapi.testclient import TestClient

from fastapi import HTTPException
from app.main import app, penyimpan, _urai_waktu


@pytest.mark.parametrize('slot', ['asal', 'tujuan'])
@pytest.mark.parametrize('coords', [
    ['NaN', -6.95], [110.4, 'Infinity'], [float('nan'), -6.95],
    [110.4, float('inf')], [float('-inf'), -6.95], [1e200, 1e200],
    [181, -6.95], [110.4, -91], [110.4], ['x', -6.95],
])
def test_koordinat_buruk_selalu_422(monkeypatch, slot, coords):
    def tidak_boleh_memuat():
        pytest.fail('Masukan buruk masuk ke pemuatan dataset')
    monkeypatch.setattr(penyimpan, 'ambil', tidak_boleh_memuat)
    body = {'asal':[110.41853, -6.94959], 'tujuan':[110.46934, -6.94825], slot:coords}
    response = TestClient(app).post('/api/rute', content=json.dumps(body),
                                    headers={'content-type':'application/json'})
    assert response.status_code == 422
    detail = response.json()['detail']
    assert any(e['loc'][:2] == ['body', slot] for e in detail)
    assert all('input' not in e and 'ctx' not in e for e in detail)


def test_json_cacat_tetap_galat_validasi():
    response = TestClient(app).post('/api/rute', content='{"asal":',
                                   headers={'content-type':'application/json'})
    assert response.status_code == 422
    assert response.json()['detail'][0]['type'] == 'json_invalid'


@pytest.mark.parametrize('waktu', [
    '0001-01-01T00:00:00+14:00', '9999-12-31T23:59:59-14:00',
])
def test_konversi_zona_waktu_melampaui_kalender(waktu):
    with pytest.raises(HTTPException) as err:
        _urai_waktu(waktu)
    assert err.value.status_code == 400
