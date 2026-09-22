"""Bandingkan 2.400 pencarian dengan Bellman-Ford pada graf acak kecil."""
import math
import random
from datetime import datetime, timezone

import pytest

from app.domain.routing import GrafJalan, cari_rute, penalti_genangan


def test_dijkstra_sesuai_bellman_ford_dengan_arah_paralel_dan_jam_berganti():
    ambang = {'lambat_cm': 10, 'berisiko_cm': 20, 'tidak_bisa_lewat_cm': 30}
    waktu = datetime(2026, 9, 26, 10, 59, 59, tzinfo=timezone.utc)
    for seed in range(40):
        acak = random.Random(seed)
        ruas, biaya, dalam = [], [], {}
        for e in range(24):
            u, v = acak.sample(range(6), 2)
            panjang, kecepatan, k = acak.randint(1, 10000), acak.choice([10, 30, 60]), acak.choice([0, 10, 20, 29, 30, 50])
            satu_arah = acak.choice([True, False])
            ruas.append({'edge_id': e, 'osm_u': u, 'osm_v': v, 'panjang_m': panjang,
                'kecepatan_kmh': kecepatan, 'satu_arah': satu_arah,
                'koordinat': [[110.4 + u*.001, -6.95], [110.4 + v*.001, -6.95]]})
            dalam[e] = (k, .5)
            biaya.append((u, v, panjang / (kecepatan / 3.6), k))
            if not satu_arah:
                biaya.append((v, u, panjang / (kecepatan / 3.6), k))
        graf = GrafJalan(ruas)
        prediksi = {waktu.replace(minute=0, second=0): dalam,
                    waktu.replace(hour=11, minute=0, second=0): {e: (0, 0) for e in dalam}}
        for sadar in [False, True]:
            for asal in range(6):
                acuan = [math.inf] * 6
                acuan[asal] = 0
                for _ in range(5):
                    for u, v, detik, k in biaya:
                        bobot = detik * (penalti_genangan(k, ambang) if sadar else 1)
                        acuan[v] = min(acuan[v], acuan[u] + bobot)
                for tujuan in range(6):
                    if asal == tujuan:
                        continue
                    r = cari_rute(graf, asal, tujuan, waktu, ambang, prediksi, sadar_rob=sadar)
                    assert r.ditemukan == math.isfinite(acuan[tujuan]), (seed, asal, tujuan, sadar)
                    if r.ditemukan:
                        assert r.detik == pytest.approx(acuan[tujuan]), (seed, asal, tujuan, sadar)
