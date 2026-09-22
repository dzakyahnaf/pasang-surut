"""Periksa artefak materi dan buat PDF utama 8 halaman dari ekspor PowerPoint."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'.deploy-local/presentation-tools'))
import pymupdf
import zxingcpp
from PIL import Image

OUT=Path(__file__).resolve().parent
CHECK=ROOT/'.deploy-local/presentation-review'
CHECK.mkdir(parents=True,exist_ok=True)
NAME='Pasang_Surut_Final_ANFORCOM_2026'
APP='https://pasang-surut.vercel.app/app'
powerpoint=json.loads((OUT/'verifikasi_powerpoint.json').read_text(encoding='utf-8-sig'))
assert powerpoint['slides']==14 and not powerpoint['overflow'],powerpoint
with zipfile.ZipFile(OUT/f'{NAME}.pptx') as z:
    note_files=[p for p in z.namelist() if p.startswith('ppt/notesSlides/notesSlide') and p.endswith('.xml')]
    assert len(note_files)==14
    for i in range(1,15):
        root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        assert (root.get('show')=='0')==(i>8)
        notes=z.read(f'ppt/notesSlides/notesSlide{i}.xml').decode('utf-8')
        assert 'WAKTU' in notes and 'SUMBER' in notes
d=pymupdf.open(OUT/f'{NAME}.pdf')
assert len(d)==14
for i,p in enumerate(d):
    p.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(CHECK/f'slide_{i+1:02d}.png')
source_qr=zxingcpp.read_barcode(Image.open(OUT/'aset/qr_aplikasi.png'))
pdf_qr=zxingcpp.read_barcode(Image.open(CHECK/'slide_08.png'))
assert source_qr and pdf_qr and source_qr.text==pdf_qr.text==APP
assert any(link.get('uri')==APP for link in d[7].get_links())
texts='\n'.join(p.get_text() for p in d)
for value in ['13,9','10,58','0,1155','0,6579','±30%','26']:
    assert value in texts,value
short=pymupdf.open();short.insert_pdf(d,from_page=0,to_page=7)
short.save(OUT/f'{NAME}_utama.pdf');short.close()
# Normalisasi JSON COM agar portabel dan tidak membawa path laptop.
powerpoint['pdf']=NAME+'.pdf'
(OUT/'verifikasi_powerpoint.json').write_text(json.dumps(powerpoint,indent=2)+'\n',encoding='utf-8')
report={'pdf_pages':14,'pdf_main_pages':8,'notes_slides':14,'hidden_appendices':6,
        'powerpoint_overflow':0,'qr_source':source_qr.text,'qr_pdf_render':pdf_qr.text,
        'pdf_app_link':True,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in [OUT/f'{NAME}.pptx',OUT/f'{NAME}.pdf',OUT/f'{NAME}_utama.pdf']}}
(OUT/'verifikasi_berkas.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
