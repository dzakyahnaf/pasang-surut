"""Uji bundle produksi: retry, pindah jam, respons terbaru, geometri sekali."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

def main():
    p=argparse.ArgumentParser();p.add_argument('--alamat',default='http://127.0.0.1:18080')
    p.add_argument('--nama',default='vps_browser');a=p.parse_args()
    host = urlparse(a.alamat).hostname or ''
    assert host in ('127.0.0.1','localhost','38.103.171.82') or host.endswith('.vercel.app')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge',headless=True,
            args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1440,'height':1000})
        requests,errors=[],[];attempts=[0]
        external=[]
        page.on('request',lambda r:requests.append(urlparse(r.url).path) if '/api/' in r.url else None)
        page.on('request',lambda r:external.append(r.url) if urlparse(r.url).scheme in ('http','https')
                and urlparse(r.url).netloc != urlparse(a.alamat).netloc else None)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' and '[peta]' in m.text else None)
        def route(r):
            attempts[0]+=1
            if attempts[0]==1:r.fulfill(status=503,content_type='application/json',body='{"detail":{"kode":"server_sibuk"}}')
            else:r.continue_()
        page.route('**/api/rute',route)
        with page.expect_response(lambda r:'/api/jam' in r.url and r.status==200) as jam:
            page.goto(a.alamat,wait_until='networkidle',timeout=60000)
        hours=jam.value.json()['jam']
        index=max((i for i,h in enumerate(hours) if h['tersedia']),key=lambda i:hours[i]['ruas_tergenang'])
        assert index>0
        page.get_by_role('button',name='Stasiun Semarang Tawang',exact=True).click()
        page.get_by_role('button',name='Kawasan Industri Terboyo',exact=True).click()
        page.get_by_text('Akses Stasiun Semarang Tawang',exact=True).wait_for()
        page.get_by_text('Akses Kawasan Industri Terboyo',exact=True).wait_for()
        page.locator('.rail__blok.galat').wait_for()
        page.locator('.rail > .tombol-utama').click()
        page.locator('.hasil__angka').first.wait_for(timeout=20000)
        before=requests.count('/api/jaringan')
        target=hours[index]['waktu_utc']
        with page.expect_response(lambda r:'/api/rute' in r.url and r.status==200 and r.request.post_data_json['waktu']==target,timeout=20000) as reply:
            page.locator('[role=slider]').focus()
            for _ in range(index):page.keyboard.press('ArrowRight')
        result=reply.value.json()
        page.locator('.hasil__angka').first.wait_for(timeout=20000)
        assert result['waktu_berangkat_utc']==target
        assert requests.count('/api/jaringan')==before==1
        assert '/api/ruas' not in requests and not errors and not external, (errors,external)
        output=Path(__file__).resolve().parents[2]/'docs/final/bukti'
        page.screenshot(path=str(output/(a.nama+'.png')))
        report={'alamat':a.alamat,'errors':errors,'mode':result['asal_jaringan'],
            'geometry_requests':before,'extra_geometry_on_slider':0,'route_requests_including_retry':attempts[0],
            'selected_index':index,'selected_time':target,'wet_roads':hours[index]['ruas_tergenang'],
            'route_model':result['model_routing'],'external_browser_requests':external}
        page.set_viewport_size({'width':360,'height':800})
        page.wait_for_timeout(500)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        assert page.locator('.atribusi').is_visible()
        page.screenshot(path=str(output/(a.nama+'_mobile.png')))
        report['mobile_360px_no_horizontal_overflow']=True
        (output/(a.nama+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report));browser.close()

if __name__=='__main__':main()
