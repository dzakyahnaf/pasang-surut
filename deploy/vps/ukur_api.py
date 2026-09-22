"""Benchmark berurutan pada loopback VPS; tidak menerima alamat produksi."""
import argparse
import json
import math
import time
import urllib.request
from datetime import datetime, timezone

def request(path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request('http://127.0.0.1:18080'+path, data=body,
        headers={'Content-Type':'application/json'})
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    return json.loads(raw), (time.monotonic()-start)*1000, len(raw)

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['potret','database'],required=True)
    p.add_argument('--sampel',type=int,default=30);a=p.parse_args()
    health,cold,_ = request('/api/kesehatan')
    assert health['asal_jaringan']==a.mode
    pois=request('/api/tujuan-cepat')[0]['tujuan']
    coords=lambda i:[pois[i]['lon'],pois[i]['lat']]
    _,geometri_ms,geometri_bytes=request('/api/jaringan')
    hours=['2026-09-25T17:00:00+00:00','2026-09-26T01:00:00+00:00',
           '2026-09-26T06:00:00+00:00','2026-09-27T02:00:00+00:00','2026-09-27T06:00:00+00:00']
    routes,conditions,sizes=[],[],[]
    route_results={}
    for i in range(a.sampel):
        w=hours[i%len(hours)]
        kondisi,ms,n=request('/api/kondisi?waktu='+urllib.parse.quote(w))
        conditions.append(ms);sizes.append(n)
        result,ms,_=request('/api/rute',{'asal':coords(1),'tujuan':coords(2),'moda':'motor','waktu':w})
        routes.append(ms)
        route_results[w]=[{k:f['properties'][k] for k in ('jenis','menit','jarak_km','ruas_tergenang')}
                          for f in result['rute']['features']]
        time.sleep(.15)
    p95=lambda x:round(sorted(x)[math.ceil(.95*len(x))-1],2)
    result={'utc':datetime.now(timezone.utc).isoformat(),'lingkungan':'VPS Linux loopback, satu worker, CPU 0.8',
        'mode':a.mode,'samples':a.sampel,'health_ms':round(cold,2),
        'route_p95_ms':p95(routes),'condition_p95_ms':p95(conditions),
        'route_min_max_ms':[round(min(routes),2),round(max(routes),2)],
        'geometry_ms':round(geometri_ms,2),'geometry_bytes':geometri_bytes,
        'condition_bytes_min_max':[min(sizes),max(sizes)],'route_results':route_results}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
