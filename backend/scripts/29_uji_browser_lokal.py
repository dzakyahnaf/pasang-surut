"""Uji interaksi browser localhost memakai Edge dan paket playwright lokal."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True,
            args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width":1440,"height":1000})
        errors, requests = [], []
        attempts = [0]
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "[peta]" in m.text else None)
        page.on("request", lambda r: requests.append(r.url.split("8018")[-1]) if "8018" in r.url else None)
        def route(r):
            attempts[0] += 1
            if attempts[0] == 1:
                r.fulfill(status=503, content_type="application/json",
                          body='{"detail":{"kode":"server_sibuk"}}')
            else:
                r.continue_()
        page.route("**/api/rute", route)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle", timeout=40000)
        page.wait_for_function("window.__peta && window.__peta.loaded()", timeout=30000)
        page.get_by_role("button",name="Stasiun Semarang Tawang",exact=True).click()
        page.get_by_role("button",name="Kawasan Industri Terboyo",exact=True).click()
        page.locator(".rail__blok.galat").wait_for()
        page.locator(".rail > .tombol-utama").click()
        page.locator(".hasil__angka").first.wait_for(timeout=15000)
        before = sum(r == "/api/jaringan" for r in requests)
        page.locator("[role=slider]").focus()
        for _ in range(8):
            page.keyboard.press("ArrowRight")
        page.wait_for_function("document.querySelector('[role=slider]').getAttribute('aria-valuenow') === '8'")
        page.wait_for_function("document.querySelector('.plat__jam')?.textContent.includes('08.00')")
        page.wait_for_function('async () => (await window.__peta.getSource("rute").getData()).features.some(f => f.properties.waktu_tiba_wib?.startsWith("2026-09-26T08:"))', timeout=15000)
        try:
            page.locator(".hasil__angka").first.wait_for(timeout=15000)
        except Exception:
            print(json.dumps({"errors":errors,"requests":requests,
                              "body":page.locator('body').inner_text()}))
            raise
        assert not errors, errors
        assert page.locator(".hasil__angka").count() >= 1
        wet = page.evaluate('async () => (await window.__peta.getSource("ruas").getData()).features.filter(f => window.__peta.getFeatureState({source:"ruas",id:f.id}).kedalaman_cm > 0).length')
        assert wet > 0
        assert sum(r == "/api/jaringan" for r in requests) == before
        out = Path(__file__).resolve().parents[2] / "docs/final/bukti"
        out.mkdir(exist_ok=True)
        page.screenshot(path=str(out / "ui_perbaikan_21_september.png"))
        hasil = {"browser":"Edge headless, localhost", "errors":errors,
            "route_requests_including_failed_retry":attempts[0],
            "geometry_requests_bootstrap_including_dev_strictmode":before,
            "geometry_extra_requests_on_slider":0,
            "wet_feature_states":wet, "api_requests":requests, "final_slider":8}
        (out / "browser_21_september.json").write_text(json.dumps(hasil,indent=2),encoding="utf-8")
        print(json.dumps(hasil))
        browser.close()


if __name__ == "__main__":
    main()
