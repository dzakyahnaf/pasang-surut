"""Telemetri baca-saja saat uji beban; JSONL stdout, tidak mengubah layanan.

Jalankan pada host Docker cgroup v1. Pengirim beban WAJIB berhenti bila
stop_guard terisi atau telemetri terputus. Hanya menginspeksi nama di bawah.
"""
import argparse
import json
import subprocess
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWN = ('pasang-surut-api-1', 'pasang-surut-db-1', 'pasang-surut-web-1')
OLD = ('bermakna-app-1', 'bermakna-db-1', 'bermakna-caddy-1')


def inspect():
    fmt = '{"name":{{json .Name}},"id":{{json .Id}},"started":{{json .State.StartedAt}},"restarts":{{.RestartCount}},"oom":{{.State.OOMKilled}},"running":{{.State.Running}},"limit":{{.HostConfig.Memory}}}'
    raw = subprocess.check_output(['docker', 'inspect', *OWN, *OLD, '--format', fmt], timeout=10)
    return [json.loads(line) for line in raw.decode().splitlines()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=int, default=1200)
    args = parser.parse_args()
    assert 10 <= args.seconds <= 1800
    baseline = inspect()
    macro = {'status': None, 'errors': 0, 'ms': None, 'checked_utc': None}
    done = threading.Event()

    def probe():
        while not done.is_set():
            start = time.monotonic()
            try:
                with urllib.request.urlopen('https://maknaprice.my.id/', timeout=4) as response:
                    status = response.status
            except Exception:
                status = 0
            macro.update(status=status, errors=0 if status == 200 else macro['errors']+1,
                         ms=round((time.monotonic()-start)*1000, 2),
                         checked_utc=datetime.now(timezone.utc).isoformat())
            done.wait(10)

    threading.Thread(target=probe, daemon=True).start()
    start = time.monotonic()
    checked = -100
    states = baseline
    initial_fail = {}
    while time.monotonic()-start < args.seconds:
        mem = {line.split(':')[0]: int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()}
        vm = dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
        if time.monotonic()-checked >= 10:
            states = inspect()
            checked = time.monotonic()
        containers = {}
        reasons = []
        for state in baseline[:3]:
            root = Path('/sys/fs/cgroup/memory/docker')/state['id']
            stat = dict(line.split() for line in (root/'memory.stat').read_text().splitlines())
            usage, peak, fail = [int((root/('memory.'+key)).read_text()) for key in ('usage_in_bytes', 'max_usage_in_bytes', 'failcnt')]
            initial_fail.setdefault(state['name'], fail)
            containers[state['name']] = {'usage_mib':round(usage/1048576, 2),
                'rss_mib':round(int(stat['total_rss'])/1048576, 2),
                'lifetime_peak_mib':round(peak/1048576, 2), 'failcnt':fail,
                'limit_mib':state['limit']/1048576}
            if usage > state['limit']*.95 or fail > initial_fail[state['name']]:
                reasons.append('memory_limit_approached:'+state['name'])
        if mem['MemAvailable']/1024 < 400:
            reasons.append('host_available_below_400_mib')
        if macro['errors'] >= 2:
            reasons.append('maknaprice_probe_failed_twice')
        if states != baseline:
            reasons.append('container_identity_or_state_changed')
        row = {'utc':datetime.now(timezone.utc).isoformat(),
               'elapsed_s':round(time.monotonic()-start, 2),
               'available_mib':round(mem['MemAvailable']/1024, 2),
               'swap_used_mib':round((mem['SwapTotal']-mem['SwapFree'])/1024, 2),
               'pswpin':int(vm['pswpin']), 'pswpout':int(vm['pswpout']),
               'load':Path('/proc/loadavg').read_text().split()[:3],
               'containers':containers, 'maknaprice':dict(macro),
               'states':states if time.monotonic()-start < 1 or reasons else None,
               'stop_guard':reasons}
        print(json.dumps(row), flush=True)
        if reasons:
            break
        time.sleep(.5)
    done.set()


if __name__ == '__main__':
    main()
