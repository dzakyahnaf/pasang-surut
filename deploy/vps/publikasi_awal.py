"""Terbitkan prediksi lengkap pada database VPS setelah impor tervalidasi."""
import os
import runpy
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

assert os.environ['POSTGRES_DB'] == 'pasang_surut'
os.environ['DATABASE_URL'] = ('postgresql://'+quote(os.environ['POSTGRES_USER'],safe='')+
    ':'+quote(os.environ['POSTGRES_PASSWORD'],safe='')+'@db:5432/pasang_surut')
sys.path.insert(0,'/app/backend')
from app import db

mulai = datetime.now(timezone.utc).replace(minute=0,second=0,microsecond=0)
with db.koneksi() as c:
    with c.cursor() as q:
        q.execute('SELECT max(waktu) FROM pemicu')
        akhir = min(q.fetchone()[0], mulai+timedelta(hours=24*14-1))
jam = int((akhir-mulai).total_seconds()/3600)+1
assert jam >= 72
assert akhir >= datetime(2026,9,29,tzinfo=timezone.utc)
sys.argv = ['11_indeks_kerentanan.py','--mulai',mulai.isoformat(),'--jam',str(jam)]
runpy.run_path('/pipeline/11_indeks_kerentanan.py',run_name='__main__')
