"""Inventaris audit sumber dan validasi potret tanpa menulis database.

Ini pemeriksaan mekanis pendamping review, bukan pembuktian bebas bug.
Hasil hanya menyebut lokasi kandidat secret, tidak menyalin nilainya.
"""
import ast
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from app.runtime import PenyimpanRuntime


def main():
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    ext, parsed, invalid, suspects, manifests = Counter(), Counter(), [], [], []
    patterns = [r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
                r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{40,}',
                r'postgres(?:ql)?://[^\s/:]+:[^\s/@]{6,}@[^\s]+']
    for rel in filter(None, paths):
        p = ROOT / rel
        if not p.is_file():
            continue
        ext[p.suffix.lower()] += 1
        if p.suffix.lower() not in {'.py', '.js', '.jsx', '.mjs', '.json', '.geojson', '.yml', '.yaml', '.sql', '.md', '.html', '.css', '.txt'}:
            continue
        raw = p.read_bytes()
        text = raw.decode('utf-8-sig')
        for i, pattern in enumerate(patterns):
            if re.search(pattern, text):
                suspects.append({'path': rel, 'pattern': i})
        try:
            if p.suffix == '.py':
                ast.parse(text); parsed['python'] += 1
            if p.suffix in {'.json', '.geojson'}:
                json.loads(text, parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
                parsed['json_geojson'] += 1
        except (ValueError, SyntaxError) as e:
            invalid.append({'path': rel, 'error_type': type(e).__name__})
        if rel.startswith(('backend/app/', 'backend/scripts/', 'frontend/src/', 'dashboard/', 'db/', 'deploy/', '.github/')):
            manifests.append({'path': rel, 'sha256': hashlib.sha256(raw).hexdigest()})
    # Potret divalidasi seluruh nilai, referensi edge, geometri, dan ambangnya.
    data = PenyimpanRuntime()._dari_potret()
    output = {'utc': datetime.now(timezone.utc).isoformat(), 'tracked_extensions': dict(ext),
        'parsed': dict(parsed), 'parse_failures': invalid, 'secret_candidates': suspects,
        'snapshot': {'roads': len(data.jaringan.fitur), 'hours': len(data.cakupan.jam),
                     'wet_records': sum(len(v) for v in data.prediksi.values()),
                     'valid_until': data.cakupan.berlaku_sampai.isoformat(), 'all_values_validated': True},
        'source_manifest': manifests}
    (ROOT / 'docs/final/bukti/audit_statis_22.json').write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='source_manifest'}, indent=2))


if __name__ == '__main__':
    main()
