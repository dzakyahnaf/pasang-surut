"""Impor lima tabel PASANG SURUT ke database BARU, lalu uji transaksi SQL.

Hanya untuk container alat pada jaringan pasang-surut_default. Tidak
membaca kredensial sumber dan tidak menghubungi database Maknaprice.
"""
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from psycopg2 import sql
sys.path.insert(0, '/app/backend')
from app import db

ROOT = Path('/migration')
TABLES = ('ruas_jalan','pemicu','prediksi_genangan','sampel_latih','ambang_moda')

class Digest:
    def __init__(self):
        self.hash = hashlib.sha256()
    def write(self, value):
        self.hash.update(value)
        return len(value)

def main():
    assert os.environ['POSTGRES_DB'] == 'pasang_surut'
    connection = psycopg2.connect(host='db', dbname='pasang_surut',
        user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'])
    manifest = json.loads((ROOT/'manifest.json').read_text())
    report = {'tables': {}, 'tests': {}}
    with connection:
        with connection.cursor() as q:
            q.execute("SELECT to_regclass('public.ruas_jalan')")
            assert q.fetchone()[0] is None, 'Impor hanya diizinkan pada database baru'
            q.execute((ROOT/'schema.sql').read_text())
            q.execute('TRUNCATE ambang_moda')
            for table in TABLES:
                entry = manifest[table]
                path = ROOT/(table+'.csv.gz')
                assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256_gzip']
                q.execute(sql.SQL('SELECT * FROM {} LIMIT 0').format(sql.Identifier(table)))
                assert [c.name for c in q.description] == entry['columns']
                with gzip.open(path,'rb') as data:
                    q.copy_expert(f"COPY public.{table} FROM STDIN WITH (FORMAT CSV, HEADER, ENCODING 'UTF8')",data)
                q.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(table)))
                count = q.fetchone()[0]
                assert count == entry['rows']
                digest = Digest()
                q.copy_expert(f"COPY (SELECT * FROM public.{table} ORDER BY {entry['order']}) TO STDOUT WITH (FORMAT CSV, HEADER, ENCODING 'UTF8')",digest)
                with gzip.open(path,'rb') as data:
                    expected = hashlib.file_digest(data,'sha256').hexdigest()
                assert digest.hash.hexdigest() == expected, 'Isi tabel berbeda: '+table
                report['tables'][table] = {'rows':count,'sha256_csv':expected}
            q.execute("SELECT setval(pg_get_serial_sequence('ruas_jalan','edge_id'), (SELECT max(edge_id) FROM ruas_jalan))")
            q.execute("SELECT setval(pg_get_serial_sequence('sampel_latih','id'), 1, false)")
            # Migrasi terpisah harus aman dijalankan lagi setelah skema baru.
            q.execute((ROOT/'001_cakupan_prediksi.sql').read_text())
            q.execute((ROOT/'001_cakupan_prediksi.sql').read_text())
            q.execute('SELECT count(*) FROM ruas_jalan WHERE NOT ST_IsValid(geom) OR ST_SRID(geom) != 4326')
            assert q.fetchone()[0] == 0
            q.execute('CREATE ROLE pasang_api LOGIN PASSWORD %s', (os.environ['PASANG_API_PASSWORD'],))
            q.execute('GRANT CONNECT ON DATABASE pasang_surut TO pasang_api')
            q.execute('GRANT USAGE ON SCHEMA public TO pasang_api')
            q.execute('GRANT SELECT ON ALL TABLES IN SCHEMA public TO pasang_api')
            q.execute('ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO pasang_api')
            q.execute('ALTER ROLE pasang_api SET default_transaction_read_only = on')
    report['tests']['copy_identik_semua_tabel'] = True
    report['tests']['migrasi_idempoten'] = True
    report['tests']['geometri_valid'] = True

    # Dataset kering diterbitkan sebagai lengkap, kemudian di-rollback.
    hours = [datetime(2026,9,26,tzinfo=timezone.utc)+timedelta(hours=i) for i in range(3)]
    repo = db.RepositoriGenangan(connection)
    assert repo.publikasikan([], hours, 'kerentanan_v1') == 0
    assert repo.cakupan()['jam'] == hours
    assert repo.peta_kedalaman(hours[0],hours[-1],sumber='kerentanan_v1') == {}
    repo.kosongkan_sumber('kerentanan_v1')
    assert repo.cakupan() is None
    connection.rollback()
    report['tests']['jam_kering_dan_pembatalan_metadata'] = True

    # Gagal insert tidak boleh menghapus publikasi lama secara parsial.
    try:
        repo.publikasikan([(-999, hours[0], 5, .5, 'kerentanan_v1')], hours, 'kerentanan_v1')
        raise AssertionError('Foreign key seharusnya menolak ruas yang tidak ada')
    except psycopg2.IntegrityError:
        connection.rollback()
    with connection.cursor() as q:
        q.execute('SELECT count(*) FROM prediksi_genangan')
        assert q.fetchone()[0] == manifest['prediksi_genangan']['rows']
        q.execute('SELECT count(*) FROM cakupan_prediksi')
        assert q.fetchone()[0] == 0
    connection.rollback()
    report['tests']['rollback_publikasi_gagal'] = True

    readonly = psycopg2.connect(host='db', dbname='pasang_surut', user='pasang_api',
        password=os.environ['PASANG_API_PASSWORD'])
    try:
        with readonly.cursor() as q:
            q.execute('DELETE FROM prediksi_genangan WHERE false')
        raise AssertionError('Akun API seharusnya tidak bisa menulis')
    except (psycopg2.errors.InsufficientPrivilege, psycopg2.errors.ReadOnlySqlTransaction):
        readonly.rollback()
    finally:
        readonly.close()
    report['tests']['akun_api_hanya_baca'] = True
    connection.close()
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
