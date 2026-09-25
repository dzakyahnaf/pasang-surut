"""Verifikasi materi ekspor PowerPoint; tidak menjalankan layanan produksi."""
import hashlib, json, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'.deploy-local/presentation-tools'))
import pymupdf
import zxingcpp
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
REVIEW=ROOT/'.deploy-local/ppt-final-25/review';REVIEW.mkdir(exist_ok=True,parents=True)
NAME='Pasang_Surut_Final_2026_25Sep'
APP='https://pasang-surut.vercel.app/app'
report=json.loads((OUT/'verifikasi_powerpoint.json').read_text(encoding='utf-8-sig'))
assert report['slides']==18 and not report['overflow'] and not report['offSlide'],report
report['pdf']=NAME+'_lengkap.pdf'
(OUT/'verifikasi_powerpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
native_text=[];note_count=0;internal_links=0;external_links=set()
with zipfile.ZipFile(OUT/(NAME+'.pptx')) as z:
    for i in range(1,19):
        e=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        assert (e.get('show')=='0')==(i>9)
        strings=[t.text or '' for t in e.findall('.//a:t',ns)];native_text.extend(strings)
        n=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        nt=' '.join(t.text or '' for t in n.findall('.//a:t',ns))
        assert 'WAKTU:' in nt and 'SUMBER:' in nt and 'AKSI:' in nt
        note_count+=1
    for name in z.namelist():
        if name.startswith('ppt/slides/_rels/'):
            for e in ET.fromstring(z.read(name)):
                if e.get('Type','').endswith('/slide'):internal_links+=1
                if e.get('TargetMode')=='External':external_links.add(e.get('Target'))
    assert internal_links>=18
assert not any(c in ''.join(native_text) for c in ['\u2013','\u2014'])
bad=['tidak hanya','bukan sekadar','transformasi digital','holistik','di era modern','sebagai kesimpulan']
assert not any(b in ' '.join(native_text).lower() for b in bad)
pdf=pymupdf.open(OUT/(NAME+'_lengkap.pdf'));assert len(pdf)==18
text='\n'.join(p.get_text() for p in pdf)
for needle in ['13,9','10,58','0,834','12,44','95','26','0,6579','2014','2015','Belum']:
    assert needle.lower() in text.lower(),needle
assert 'smart low-carbon urban mobility' in text.lower()
assert all(abs(p.rect.width/p.rect.height-16/9)<.001 for p in pdf)
for i,p in enumerate(pdf):p.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(REVIEW/f'slide_{i+1:02}.png')
qr=zxingcpp.read_barcode(Image.open(REVIEW/'slide_09.png'))
assert qr and qr.text==APP
assert any(l.get('uri')==APP for l in pdf[8].get_links())
assert any(l.get('page')==10 for l in pdf[3].get_links()),'Tombol cadangan 08.00 hilang pada PDF lengkap'
short=pymupdf.open();short.insert_pdf(pdf,from_page=0,to_page=8)
# PDF utama tidak membawa tautan lampiran di luar dokumen; gunakan PDF lengkap untuk navigasi itu.
short.save(OUT/(NAME+'_utama.pdf'));short.close()
for group in range(3):
    canvas=Image.new('RGB',(1440,3*425),(218,228,232));draw=ImageDraw.Draw(canvas)
    for k in range(6):
        i=group*6+k
        im=Image.open(REVIEW/f'slide_{i+1:02}.png');im.thumbnail((710,400))
        x=(k%2)*720;y=(k//2)*425
        canvas.paste(im,(x,y+21));draw.text((x+10,y+4),f'Slide {i+1}',fill=(11,31,42))
    canvas.save(REVIEW/f'lembar_{group+1}.png')
(REVIEW/'text_pdf.txt').write_text(text,encoding='utf-8')
manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
assert sum(s['seconds'] for s in manifest['slides_summary'])==540
result={'pdf_main_pages':9,'pdf_full_pages':18,'notes':note_count,'hidden_appendices':9,
        'overflow':0,'objects_off_slide':0,'internal_slide_relationships':internal_links,
        'qr_from_pdf':qr.text,'pdf_backup_link':True,'target_seconds':540,
        'external_links':sorted(external_links),'native_text_characters':sum(map(len,native_text)),
        'style_check':{'em_en_dash_in_native_text':0,'banned_boilerplate':0},
        'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/(NAME+'.pptx'),OUT/(NAME+'_utama.pdf'),OUT/(NAME+'_lengkap.pdf')]}}
(OUT/'verifikasi_berkas.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['external_links','sha256']},ensure_ascii=True,indent=2))
