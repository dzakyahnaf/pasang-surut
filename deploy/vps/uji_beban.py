"""Uji baca API dari laptop, dengan callback penghenti dari telemetri host.

Bukan benchmark kapasitas maksimum. Maksimal 32 request bersamaan; fase
soak dibatasi 4 request/detik. Tidak menyimpan badan GeoJSON besar ke bukti.
Panggil jalankan(stop_event, out) hanya bersama pantau_beban.py.
"""
import asyncio
import json
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx

ORIGIN = 'http://38.103.171.82:18080'
PUBLIC = 'https://pasang-surut.vercel.app'


async def jalankan(stop, out):
    rows, stages = [], []
    async with httpx.AsyncClient(timeout=25, limits=httpx.Limits(max_connections=32),
                                 headers={'User-Agent':'PasangSurut-Authorized-Final-Test/1.0'},
                                 trust_env=False) as client:
        async def call(stage, path, body=None, expected=(200,), base=ORIGIN, check=None):
            if stop.is_set():
                raise RuntimeError('Beban dihentikan oleh telemetri atau respons tak terduga')
            start = time.monotonic()
            data = None
            try:
                r = await client.request('POST' if body is not None else 'GET', base+path, json=body)
                code = r.status_code
                size = len(r.content)
                detail = None
                if code != 200 or check or size < 100000:
                    try:
                        data = r.json()
                        detail = data.get('detail') if isinstance(data, dict) else None
                    except ValueError:
                        detail = r.text[:200]
                ok = code in expected
                if code == 503:
                    ok = ok and isinstance(detail, dict) and detail.get('kode') == 'server_sibuk' and r.headers.get('retry-after') == '1'
                if ok and check:
                    ok = bool(check(data))
                error = None
            except httpx.HTTPError as exc:
                code, size, detail, ok, error = 0, 0, None, False, type(exc).__name__
            row = {'stage':stage, 'utc':datetime.now(timezone.utc).isoformat(),
                   'base':base, 'path':path, 'body':body, 'status':code,
                   'ms':round((time.monotonic()-start)*1000, 2), 'bytes':size,
                   'ok':ok, 'detail':detail, 'error':error}
            rows.append(row)
            if not ok:
                print('UNEXPECTED '+json.dumps(row), flush=True)
                stop.set()
            return data

        def summary(stage, began):
            subset = [r for r in rows if r['stage'] == stage]
            times = sorted(r['ms'] for r in subset if r['status'] == 200)
            result = {'stage':stage, 'seconds':round(time.monotonic()-began, 2),
                      'requests':len(subset), 'statuses':dict(Counter(r['status'] for r in subset)),
                      'unexpected':sum(not r['ok'] for r in subset),
                      'p95_success_ms':times[min(len(times)-1, int(len(times)*.95))] if times else None,
                      'max_success_ms':max(times) if times else None}
            stages.append(result)
            print(json.dumps(result), flush=True)

        try:
            stage = 'metadata'
            began = time.monotonic()
            health = await call(stage, '/api/kesehatan', check=lambda d:d['database'] and d['data_tersedia'])
            hours = (await call(stage, '/api/jam'))['jam']
            points = (await call(stage, '/api/tujuan-cepat'))['tujuan']
            await call(stage, '/api/validasi', check=lambda d:d['dipakai'] is False and d['tersedia'])
            wet = max(hours, key=lambda h:h['ruas_tergenang'] or 0)['waktu_utc']
            dry = min(hours, key=lambda h:h['ruas_tergenang'] if h['tersedia'] else float('inf'))['waktu_utc']
            def body(i=0, j=2, when=wet, mode='motor'):
                return {'asal':[points[i]['lon'],points[i]['lat']],
                        'tujuan':[points[j]['lon'],points[j]['lat']], 'waktu':when, 'moda':mode}
            def timed(path, when):
                return path+'?'+urlencode({'waktu':when})
            summary(stage, began)

            stage = 'functional_edges'
            began = time.monotonic()
            for i in range(4):
                for j in range(4):
                    if i == j:
                        continue
                    for mode in ('motor', 'mobil'):
                        for when in (wet, dry):
                            await call(stage, '/api/rute', body(i,j,when,mode),
                                       check=lambda d:d['model_routing']=='kondisi_jam_keberangkatan' and bool(d['rute']['features']))
            for when in ('2026-09-21T11:00:00+00:00','2026-09-21T09:00:00+00:00',
                         '2026-09-21T13:00:00+00:00','2026-09-21T20:00:00+00:00',
                         '2026-09-20T10:00:00+00:00','2026-09-20T11:00:00+00:00'):
                expected = 200 if datetime.fromisoformat(health['prediksi_mulai_utc']) <= datetime.fromisoformat(when) < datetime.fromisoformat(health['akhir_eksklusif_utc']) else 422
                await call(stage, timed('/api/ruas', when), expected=(expected,))
            for path in ('/api/kondisi','/api/ruas','/api/genangan'):
                for when, code in ((health['prediksi_mulai_utc'],200),
                                   (health['akhir_eksklusif_utc'],422),
                                   ('2099-01-01T00:00:00Z',422),('bukan-tanggal',400),
                                   ('0001-01-01T00:00:00+14:00',400),
                                   ('9999-12-31T23:59:59-14:00',400)):
                    await call(stage,timed(path,when),expected=(code,))
            for patch in ({'asal':[0,0]}, {'asal':[110.4]}, {'moda':'pesawat'},
                          {'waktu':'2099-01-01T00:00:00Z'}, {'asal':['NaN',-6.95]},
                          {'asal':[110.4,'Infinity']}, {'asal':[1e200,1e200]}):
                await call(stage,'/api/rute',{**body(),**patch},expected=(400,422))
            for when in ('0001-01-01T00:00:00+14:00','9999-12-31T23:59:59-14:00'):
                await call(stage,'/api/rute',body(0,2,when),expected=(400,))
            last = datetime.fromisoformat(health['akhir_eksklusif_utc'])-timedelta(seconds=1)
            await call(stage,'/api/rute',body(0,2,last.isoformat()),expected=(422,))
            for delta in (-1,0,1):
                when=(datetime.fromisoformat(wet)+timedelta(seconds=delta)).isoformat()
                await call(stage,'/api/rute',body(1,2,when),check=lambda d:d['waktu_berangkat_utc']==when)
            summary(stage,began)

            async def burst(stage, specs, count, base=ORIGIN):
                began = time.monotonic()
                await asyncio.gather(*(call(stage,*specs[i%len(specs)],expected=(200,503),base=base) for i in range(count)))
                summary(stage,began)
                await asyncio.sleep(2)

            legacy = [(timed('/api/ruas', h['waktu_utc']),None) for h in hours[:24]]
            routes = [('/api/rute',body(i,(i+2)%4,wet,mode)) for i in range(4) for mode in ('motor','mobil')]
            conditions = [(timed('/api/kondisi',h['waktu_utc']),None) for h in hours]
            for n in (2,4,8,16,32):
                await burst('legacy_burst_'+str(n),legacy,n)
                await burst('route_burst_'+str(n),routes,n)
                await burst('condition_burst_'+str(n),conditions,n)
            await burst('metadata_burst_32',[('/api/jam',None),('/api/validasi',None),('/api/kesehatan',None),('/api/tujuan-cepat',None)],32)
            await burst('vercel_mixed_burst_32',routes+conditions[:8],32,PUBLIC)

            async def paced(stage, specs, seconds, rate):
                began = time.monotonic()
                pending = set()
                i = 0
                while time.monotonic()-began < seconds and not stop.is_set():
                    if len(pending) < 32:
                        task = asyncio.create_task(call(stage,*specs[i%len(specs)],expected=(200,503)))
                        pending.add(task)
                        task.add_done_callback(pending.discard)
                        i += 1
                    await asyncio.sleep(1/rate)
                if pending:
                    await asyncio.gather(*pending)
                summary(stage,began)
                if stop.is_set():
                    raise RuntimeError('Batas penghentian tercapai; tidak meneruskan fase berikutnya')
            await paced('legacy_render_pattern_45s',legacy+routes[:2],45,2)
            await paced('modern_slider_route_soak_300s',conditions[:3]+routes[:2]+[('/api/jam',None)],300,4)

            stage='abort_recovery'
            began=time.monotonic()
            for i in range(12):
                async with client.stream('GET',ORIGIN+legacy[i][0]) as r:
                    assert r.status_code in (200,503)
                    async for chunk in r.aiter_bytes(1024):
                        break
                await asyncio.sleep(.15)
            await asyncio.sleep(3)
            for _ in range(3):
                await call(stage,'/api/rute',body(1,2))
            summary(stage,began)
            print('Cooldown 30s',flush=True)
            await asyncio.sleep(30)
            for base in (ORIGIN,PUBLIC):
                await call('recovery','/api/kesehatan',base=base,check=lambda d:d['database'] and d['data_tersedia'])
                await call('recovery','/api/rute',body(1,2),base=base)
        except Exception as exc:
            print('STOP '+str(exc),flush=True)
            stop.set()
        finally:
            Path(out).write_text(json.dumps({'origin':ORIGIN,'public':PUBLIC,
                'stopped':stop.is_set(),'stages':stages,'requests':rows},indent=2)+'\n',encoding='utf-8')
    return not stop.is_set()
