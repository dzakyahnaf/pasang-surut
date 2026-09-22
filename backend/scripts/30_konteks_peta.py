"""Bangun konteks peta ringan dari data OSM tersimpan, tanpa unduhan baru.

Jalankan dari akar repo: python backend/scripts/30_konteks_peta.py.
Tidak mengubah AOI, jaringan routing, atau database.
"""
import hashlib
import json
from pathlib import Path

from shapely.geometry import shape, mapping

ROOT = Path(__file__).resolve().parents[2]


def main():
    sources = [ROOT/'data/aoi/aoi_semarang_pilot.geojson'] + [
        ROOT/'data/processed'/name for name in
        ('kecamatan.geojson', 'garis_pantai.geojson', 'tujuan_cepat.geojson')]
    aoi, districts, coast, places = [json.loads(p.read_text(encoding='utf-8')) for p in sources]
    area = shape(aoi['features'][0]['geometry'])
    features = []

    def add(geometry, **properties):
        if not geometry.is_empty:
            features.append({'type': 'Feature', 'properties': properties,
                             'geometry': mapping(geometry)})

    for f in districts['features']:
        polygon = shape(f['geometry'])
        clipped = polygon.intersection(area)
        if clipped.is_empty:
            continue
        name = f['properties']['kecamatan']
        # Potong batas ASLI; tepi AOI bukan batas administrasi kecamatan.
        add(polygon.boundary.intersection(area).simplify(0.00005), jenis='batas', nama=name)
        add(clipped.representative_point(), jenis='wilayah', nama=name)
    for f in coast['features']:
        add(shape(f['geometry']).intersection(area).simplify(0.00005), jenis='pantai')
    for f in places['features']:
        props = f['properties']
        # Label berada di lokasi tempat, bukan simpul jalan yang bisa berjarak ratusan meter.
        add(shape({'type': 'Point', 'coordinates': [props['lon_asli'], props['lat_asli']]}),
            jenis='tempat', nama=props['label'], kunci=props['kunci'],
            lon_rute=f['geometry']['coordinates'][0], lat_rute=f['geometry']['coordinates'][1])
    data = {'type': 'FeatureCollection', 'features': features,
            '_sumber': {'lisensi': 'OpenStreetMap contributors, ODbL',
                'catatan': 'Turunan data tersimpan; titik label wilayah bukan batas resmi. Tidak mengubah AOI.',
                'berkas': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sources}}}
    output = ROOT/'frontend/src/data/konteks-peta.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
    print(f'{len(features)} fitur konteks; {output.stat().st_size} byte')


if __name__ == '__main__':
    main()
