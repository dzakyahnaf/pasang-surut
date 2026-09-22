"""Buat paket runtime tanpa .env, kredensial, model latihan, atau data mentah."""
import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.deploy-local'

def main():
    paths = [p for p in (ROOT/'backend/app').rglob('*.py')]
    paths += [ROOT/'backend/Dockerfile', ROOT/'backend/requirements-runtime.txt', ROOT/'.dockerignore']
    paths += list((ROOT/'data/aoi').glob('*.geojson'))
    paths += [ROOT/'data/processed'/f for f in
              ('potret_demo.json', 'indeks_kerentanan.json', 'tujuan_cepat.geojson')]
    paths += [ROOT/'data/referensi'/f for f in
              ('konstanta_pasut_semarang.json', 'metrik_model.json', 'faktor_emisi.json')]
    files = {p.relative_to(ROOT).as_posix(): p for p in paths}
    files.update({'frontend/'+p.relative_to(ROOT/'frontend/dist').as_posix(): p
                  for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()})
    assert 'frontend/index.html' in files, 'Jalankan npm run build:vps dahulu'
    files.update({f: ROOT/'deploy/vps'/f for f in ('compose.yml','Caddyfile')})
    hashes = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name,p in sorted(files.items())}
    release = '21sep-' + hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()[:12]
    OUT.mkdir(exist_ok=True)
    (OUT/'release.json').write_text(json.dumps({'release':release,'sha256':hashes},indent=2),encoding='utf-8')
    with tarfile.open(OUT/'runtime.tar.gz','w:gz') as archive:
        for name,path in files.items():
            archive.add(path,arcname=name,recursive=False)
    print(json.dumps({'release':release,'files':len(files),'bytes':(OUT/'runtime.tar.gz').stat().st_size}))

if __name__ == '__main__':
    main()
