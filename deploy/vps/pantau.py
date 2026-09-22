"""Pantau host bersama; hanya container PASANG SURUT boleh dihentikan."""
import argparse
import json
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWN = ('pasang-surut-api-1','pasang-surut-web-1','pasang-surut-db-1')
OLD = ('bermakna-app-1','bermakna-db-1','bermakna-caddy-1')

def run(*cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, timeout=20)

def snapshot():
    mem = dict((line.split(':')[0],int(line.split()[1]))
               for line in Path('/proc/meminfo').read_text().splitlines())
    fmt = '{{json .Name}} {{json .State.Status}} {{json .State.OOMKilled}} {{.RestartCount}} {{json .Id}} {{json .State.StartedAt}}'
    state = run('docker','inspect',*OLD,*OWN,'--format',fmt).stdout.splitlines()
    start = time.monotonic()
    try:
        response = urllib.request.urlopen('https://maknaprice.my.id/', timeout=8)
        status = response.status
        response.close()
    except Exception:
        status = 0
    elapsed = (time.monotonic()-start)*1000
    stats = run('docker','stats','--no-stream','--format','{{json .}}').stdout
    return {'utc':datetime.now(timezone.utc).isoformat(),
            'available_mib':round(mem['MemAvailable']/1024,1),
            'swap_used_mib':round((mem['SwapTotal']-mem['SwapFree'])/1024,1),
            'maknaprice_status':status,'maknaprice_ms':round(elapsed,1),
            'states':state,'containers':[json.loads(x) for x in stats.splitlines()]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--menit',type=int,default=40)
    p.add_argument('--out',default='/opt/pasang-surut/monitor.jsonl')
    a=p.parse_args(); end=time.monotonic()+a.menit*60
    rendah=galat=0
    with open(a.out,'a',buffering=1) as output:
        while time.monotonic()<end:
            s=snapshot()
            rendah=rendah+1 if s['available_mib']<350 else 0
            galat=galat+1 if s['maknaprice_status']!=200 else 0
            s['stop_guard']=rendah>=2 or galat>=3
            output.write(json.dumps(s)+'\n')
            if s['stop_guard']:
                run('docker','stop',*OWN)
                break
            time.sleep(20)

if __name__=='__main__': main()
