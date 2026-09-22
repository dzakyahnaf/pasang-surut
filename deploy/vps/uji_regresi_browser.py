import json,sys,io
from PIL import Image
from pathlib import Path
from playwright.sync_api import sync_playwright

URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:5181'
OUT=Path('docs/final/bukti')
label='lokal' if '127.0.0.1' in URL else 'publik'
checks=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='msedge',headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.set_default_timeout(30000)
    errors=[]; warnings=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:warnings.append(m.text) if m.type=='error' else None)
    page.goto(URL,wait_until='networkidle',timeout=60000)
    page.locator('.pesan--muat').wait_for(state='detached')
    if ':5181' in URL:
        page.wait_for_function("window.__peta?.loaded() && window.__peta.queryRenderedFeatures({layers:['nama-jalan-utama','nama-wilayah','nama-tempat']}).length > 0",timeout=40000)
        checks.append('label_dan_jalan_benar_benar_dirender')
    page.get_by_role('button',name='Stasiun Semarang Tawang',exact=True).click()
    with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200) as response:
        page.get_by_role('button',name='Kawasan Industri Terboyo',exact=True).click()
    data=response.value.json()
    assert data['versi_jaringan']
    page.locator('.hasil__angka').first.wait_for()
    page.wait_for_timeout(1500)
    kanvas=Image.open(io.BytesIO(page.locator('canvas.maplibregl-canvas').screenshot())).convert('RGB')
    assert len(kanvas.getcolors(kanvas.width*kanvas.height))>20, 'Canvas peta kosong'
    checks.append('canvas_peta_berisi_gambar')
    assert page.locator('.pesan--galat').count()==0
    checks.append('peta_label_dan_rute_satu_versi')
    page.screenshot(path=str(OUT/f'audit_22_{label}_desktop.png'))
    for key in ['End','Home','PageUp','PageDown']:
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200):
            page.get_by_role('slider').press(key)
        page.locator('.hasil__angka').first.wait_for()
    checks.append('navigasi_jam_dan_rute')
    with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200):
        page.get_by_role('radio',name='Mobil',exact=True).click()
    page.locator('.hasil__angka').first.wait_for()
    page.get_by_role('button',name='Sembunyikan rute biasa',exact=True).click()
    page.get_by_role('button',name='Tampilkan rute biasa',exact=True).click()
    checks.append('ganti_moda_toggle_rute')
    page.get_by_role('button',name='Validasi',exact=True).click()
    page.get_by_role('heading',name='Validasi model',exact=True).wait_for()
    page.get_by_role('button',name='Kembali ke peta',exact=True).click()
    page.locator('.hasil__angka').first.wait_for()
    checks.append('validasi_kembali')
    for width in (360,768):
        page.set_viewport_size({'width':width,'height':900})
        page.wait_for_timeout(500)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT/f'audit_22_{label}_{width}.png'))
    checks.append('responsif_360_768')
    assert not errors, errors
    assert not warnings, warnings
    browser.close()
    no_gl=pw.chromium.launch(channel='msedge',headless=True,args=['--disable-webgl'])
    page=no_gl.new_page()
    page.goto(URL,wait_until='networkidle',timeout=60000)
    page.get_by_text('Peta tidak dapat digambar',exact=False).wait_for()
    assert page.get_by_role('button',name='Stasiun Semarang Tawang',exact=True).is_visible()
    checks.append('webgl_gagal_tujuan_cepat_tetap_tersedia')
    no_gl.close()
report={'url':URL,'checks':checks,'errors':errors,'console_errors':warnings}
(OUT/f'audit_22_browser_{label}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
