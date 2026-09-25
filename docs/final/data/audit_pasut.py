"""Audit data publik; tidak mengubah model, kalibrasi lama, atau database."""
from pathlib import Path
import sys, json, csv, hashlib, urllib.request
from datetime import datetime, timezone, timedelta
import numpy as np

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / 'backend'))
from app.domain import pasut

out = root / 'docs/final/data'
out.mkdir(exist_ok=True)
(root / '.deploy-local').mkdir(exist_ok=True)
end = datetime(2026, 9, 25, 6, tzinfo=timezone.utc)
start = end - timedelta(days=7)
url = ('https://www.ioc-sealevelmonitoring.org/service.php?query=data&code=sema'
       f'&timestart={start:%Y-%m-%dT%H:%M:%S}&timestop={end:%Y-%m-%dT%H:%M:%S}&format=json')
req = urllib.request.Request(url, headers={'User-Agent': 'PasangSurut-ANFORCOM2026/data-audit'})
with urllib.request.urlopen(req, timeout=90) as response:
    raw = response.read()
(root / '.deploy-local/ioc-sema-september-raw.json').write_bytes(raw)
records = json.loads(raw)
if not isinstance(records, list):
    raise ValueError('Balasan IOC bukan daftar pengamatan: ' + str(records)[:200])
selected = []
rejected = 0
seen = set()
for row in records:
    if row.get('sensor') != 'prs':
        continue
    try:
        t = datetime.strptime(row['stime'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        h = float(row['slevel'])
        if not np.isfinite(h) or not start <= t <= end or t in seen:
            rejected += 1
            continue
        seen.add(t)
        selected.append((t, h))
    except (KeyError, ValueError, TypeError):
        rejected += 1
selected.sort()
if len(selected) < 2:
    raise ValueError('Pengamatan sensor prs tidak cukup')
times = [t for t, _ in selected]
observed = np.array([h for _, h in selected])
hours = np.array([pasut.jam_sejak_epoch(t) for t in times])
predicted = pasut.tinggi_pasut_m(hours)
y = observed - observed.mean()
p = predicted - predicted.mean()
def metrics(a, b):
    a = a - a.mean(); b = b - b.mean()
    return {'n': len(a), 'korelasi': float(np.corrcoef(a, b)[0, 1]),
            'rmse_simpangan_m': float(np.sqrt(np.mean((a-b)**2))),
            'mae_simpangan_m': float(np.mean(np.abs(a-b)))}
daily = {}
for day in sorted({t.date().isoformat() for t in times}):
    ix = np.array([t.date().isoformat() == day for t in times])
    daily[day] = metrics(predicted[ix], observed[ix])
with (out / 'ioc_sema_18_25_september_2026.csv').open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['waktu_utc', 'sensor', 'muka_air_sensor_m', 'harmonik_v1_m',
                'simpangan_sensor_m', 'simpangan_model_m', 'galat_simpangan_m'])
    for i, t in enumerate(times):
        w.writerow([t.isoformat(), 'prs', observed[i], round(float(predicted[i]), 6),
                    round(float(y[i]), 6), round(float(p[i]), 6), round(float(p[i]-y[i]), 6)])
gaps = np.diff([t.timestamp() for t in times])
summary = {
    'dijalankan_utc': datetime.now(timezone.utc).isoformat(), 'sumber': url,
    'station': 'sema', 'sensor': 'prs', 'raw_sha256': hashlib.sha256(raw).hexdigest(),
    'raw_records_semua_sensor': len(records), 'rekaman_ditolak': rejected,
    'rentang_utc': [times[0].isoformat(), times[-1].isoformat()],
    'nilai_sensor_min_m': float(observed.min()), 'nilai_sensor_max_m': float(observed.max()),
    'interval_median_detik': float(np.median(gaps)), 'jeda_maksimum_menit': float(gaps.max()/60),
    'model': 'harmonik_v1', 'offset_jam': pasut.OFFSET_FASE_JAM,
    'epoch_utc': pasut.EPOCH_HARMONIK.isoformat(),
    'evaluasi': metrics(predicted, observed), 'per_hari_utc_demean_per_hari': daily,
    'batasan': ['Model dan offset +7 dibekukan; tidak ada pelatihan atau pemilihan offset baru.',
                'Data sensor publik belum diaudit mutu oleh tim; hanya filter tidak hingga/duplikat/rentang waktu.',
                'Datum berbeda: statistik hanya terhadap simpangan, bukan tinggi absolut.',
                'Jendela baru tujuh hari; tidak membuktikan akurasi sepanjang musim atau genangan per ruas.',
                'Sampel rapat berkorelasi; jumlah baris bukan jumlah observasi independen.']
}
(out / 'uji_pasut_independen_25_september.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps(summary, ensure_ascii=True, indent=2))
