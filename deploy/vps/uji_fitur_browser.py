"""Alur tambahan browser produksi; galat kondisi sengaja disimulasikan."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = 'https://pasang-surut.vercel.app'
OUT = Path(__file__).resolve().parents[2]/'docs/final/bukti'


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='msedge', headless=True,
            args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page = browser.new_page(viewport={'width':1440,'height':1000})
        page.set_default_timeout(20000)
        errors, requests, checks = [], [], []
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:requests.append(r.url))
        page.goto(URL,wait_until='networkidle',timeout=60000)
        page.get_by_role('button',name='Pelabuhan Tanjung Emas',exact=True).click()
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200) as response:
            page.get_by_role('button',name='Kawasan Industri Terboyo',exact=True).click()
        assert response.value.json()['moda']=='motor'
        page.locator('.hasil__angka').first.wait_for()
        checks.append('pelabuhan_ke_terboyo_motor')
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200) as response:
            page.get_by_role('radio',name='Mobil',exact=True).click()
        assert response.value.json()['moda']=='mobil'
        page.locator('.hasil__angka').first.wait_for()
        checks.append('ganti_mobil_menghitung_ulang')
        before = sum('/api/rute' in u for u in requests)
        page.get_by_role('button',name='Sembunyikan rute biasa',exact=True).click()
        page.get_by_role('button',name='Tampilkan rute biasa',exact=True).click()
        assert sum('/api/rute' in u for u in requests)==before
        checks.append('toggle_pembanding_tanpa_request_baru')
        with page.expect_response(lambda r:'/api/validasi' in r.url and r.status==200) as response:
            page.get_by_role('button',name='Validasi',exact=True).click()
        assert response.value.json()['dipakai'] is False
        page.get_by_role('heading',name='Validasi model',exact=True).wait_for()
        page.get_by_role('button',name='Kembali ke peta',exact=True).click()
        page.locator('.hasil__angka').first.wait_for()
        checks.append('validasi_dan_kembali_mempertahankan_hasil')
        page.get_by_role('button',name='Hapus titik berangkat',exact=True).click()
        assert page.locator('.hasil__angka').count()==0
        assert page.locator('.rail > .tombol-utama').is_disabled()
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200):
            page.get_by_role('button',name='Stasiun Semarang Tawang',exact=True).click()
        page.locator('.hasil__angka').first.wait_for()
        page.get_by_role('button',name='Hapus tujuan',exact=True).click()
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200):
            page.get_by_role('button',name='RSI Sultan Agung Semarang',exact=True).click()
        page.locator('.hasil__angka').first.wait_for()
        checks.append('hapus_dan_ganti_kedua_titik_semua_tujuan_cepat')
        slider = page.get_by_role('slider')
        for key, expected in (('End',71),('Home',0),('PageUp',6),('PageDown',0)):
            with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200):
                slider.focus();page.keyboard.press(key)
            assert int(slider.get_attribute('aria-valuenow'))==expected
            page.locator('.hasil__angka').first.wait_for()
        checks.append('batas_slider_home_end_pageup_pagedown')
        before = sum('/api/rute' in u for u in requests)
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200):
            slider.focus()
            # event cepat dalam satu putaran: uji batching React dan debounce.
            slider.evaluate("e => {for(let i=0;i<40;i++) e.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));}")
        page.locator('.hasil__angka').first.wait_for()
        assert int(slider.get_attribute('aria-valuenow'))==40
        assert sum('/api/rute' in u for u in requests)-before==1
        checks.append('40_pergeseran_cepat_satu_request_rute')
        failed=[False]
        def fail_once(route):
            if not failed[0]:
                failed[0]=True
                route.fulfill(status=503,content_type='application/json',
                              body='{"detail":{"kode":"server_sibuk"}}')
            else:
                route.continue_()
        page.route('**/api/kondisi?*',fail_once)
        slider.focus();page.keyboard.press('ArrowRight')
        page.locator('.pesan--galat').wait_for()
        page.locator('.pesan--galat').get_by_role('button',name='Cari ulang').click()
        page.locator('.pesan--galat').wait_for(state='detached')
        page.locator('.hasil__angka').first.wait_for()
        checks.append('retry_data_setelah_503_simulasi')
        page.screenshot(path=str(OUT/'fitur_browser_22_desktop.png'))
        for width in (360,768):
            page.set_viewport_size({'width':width,'height':900})
            page.wait_for_timeout(400)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert page.locator('.atribusi').is_visible()
            page.screenshot(path=str(OUT/f'fitur_browser_22_{width}.png'))
        checks.append('layar_360_dan_768_tanpa_overflow_atribusi_terlihat')
        assert not errors,errors
        report={'url':URL,'checks':checks,'errors':errors,
                'simulated_failures':['satu respons kondisi 503'],
                'route_requests':sum('/api/rute' in u for u in requests)}
        (OUT/'fitur_browser_22.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report),flush=True)
        browser.close()


if __name__=='__main__':
    main()
