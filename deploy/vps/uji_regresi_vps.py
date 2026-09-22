"""Regresi publik setelah audit; jalankan bersama guard pantau_beban.py."""
import asyncio
import json
import time
from collections import Counter
from itertools import permutations
from pathlib import Path

import httpx

ORIGIN = 'http://38.103.171.82:18080'
PUBLIC = 'https://pasang-surut.vercel.app'


async def jalankan(stop, out):
    rows = []
    async with httpx.AsyncClient(timeout=25, trust_env=False) as c:
        async def req(stage, path, *, body=None, content=None, expected=(200,), base=ORIGIN):
            if stop.is_set():
                raise RuntimeError('Dihentikan oleh guard')
            mulai = time.monotonic()
            r = await c.request('POST' if body is not None or content is not None else 'GET', base+path,
                                json=body, content=content)
            ok = r.status_code in expected
            if r.status_code == 503:
                ok = ok and r.json().get('detail', {}).get('kode') == 'server_sibuk'
            rows.append({'stage': stage, 'path': path, 'base': base, 'status': r.status_code,
                         'ms': round((time.monotonic()-mulai)*1000, 2), 'ok': ok})
            if not ok:
                stop.set()
                raise AssertionError(rows[-1])
            return r.json() if r.status_code == 200 else None
        jam = (await req('metadata', '/api/jam'))['jam']
        tersedia = [j for j in jam if j['tersedia']]
        waktu = [min(tersedia, key=lambda j:j['ruas_tergenang'])['waktu_utc'],
                 max(tersedia, key=lambda j:j['ruas_tergenang'])['waktu_utc']]
        tujuan = (await req('metadata', '/api/tujuan-cepat'))['tujuan']
        await req('metadata', '/api/validasi')
        body = {'asal':[tujuan[0]['lon'], tujuan[0]['lat']], 'tujuan':[tujuan[1]['lon'],tujuan[1]['lat']],
                'waktu':waktu[0], 'moda':'motor'}
        for w in waktu:
            for moda in ('motor','mobil'):
                for a,b in permutations(tujuan, 2):
                    hasil = await req('semua_tujuan_dua_moda_dua_kondisi', '/api/rute',
                        body={'asal':[a['lon'],a['lat']], 'tujuan':[b['lon'],b['lat']], 'waktu':w, 'moda':moda})
                    assert hasil['versi_jaringan'] and hasil['versi_data']
        for w in [j['waktu_utc'] for j in tersedia[:12]]:
            await req('pola_slider_legacy', '/api/ruas?waktu='+w.replace('+','%2B'))
        for base in (ORIGIN, PUBLIC):
            await req('body_besar', '/api/rute', content=b'{"padding":"'+b'x'*20000+b'"}', expected=(413,), base=base)
            await req('nan', '/api/rute', body={**body,'asal':['NaN',-6.95]}, expected=(422,), base=base)
            await req('cakupan', '/api/rute', body={**body,'waktu':'2099-01-01'}, expected=(422,), base=base)
            await req('timezone', '/api/rute', body={**body,'waktu':'0001-01-01T00:00:00+14:00'}, expected=(400,), base=base)
        for jumlah in (8,16,32):
            await asyncio.gather(*(req('burst_rute_'+str(jumlah), '/api/rute', body=body, expected=(200,503)) for _ in range(jumlah)))
            await asyncio.gather(*(req('burst_body_'+str(jumlah), '/api/rute', content=b'x'*20000, expected=(413,503)) for _ in range(jumlah)))
        # Pemulihan berulang setelah burst, termasuk satu batas TTL cache.
        awal=time.monotonic()
        i=0
        while time.monotonic()-awal < 65:
            await req('pemulihan', '/api/kondisi?waktu='+tersedia[i%len(tersedia)]['waktu_utc'].replace('+','%2B'))
            await req('pemulihan', '/api/rute', body=body)
            i+=1
            await asyncio.sleep(.5)
        await req('akhir', '/api/kesehatan', base=PUBLIC)
    report={'requests':len(rows),'statuses':dict(Counter(r['status'] for r in rows)),
            'unexpected':sum(not r['ok'] for r in rows), 'rows':rows}
    Path(out).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)
    return not stop.is_set()
