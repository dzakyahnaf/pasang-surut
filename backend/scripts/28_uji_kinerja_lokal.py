"""Benchmark terbatas localhost; sengaja menolak URL produksi.

    python -m scripts.28_uji_kinerja_lokal --pid PID_UVICORN --alamat http://127.0.0.1:8018

Memerlukan psutil (alat pengukuran lokal, bukan dependency runtime).
"""
import argparse
import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
import psutil


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pid", required=True, type=int)
    p.add_argument("--alamat", default="http://127.0.0.1:8018")
    a = p.parse_args()
    if urlparse(a.alamat).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Pengujian hanya diizinkan ke localhost")
    proses = psutil.Process(a.pid)
    samples, stop = [], threading.Event()
    def ukur():
        while not stop.wait(.02):
            samples.append(proses.memory_info().rss / 2**20)
    thread = threading.Thread(target=ukur, daemon=True)
    thread.start()
    try:
        with httpx.Client(base_url=a.alamat, timeout=30) as c:
            health = c.get("/api/kesehatan").json()
            assert health["asal_jaringan"] == "potret" and not health["database"]
            jam = c.get("/api/jam").json()["jam"]
            tujuan = c.get("/api/tujuan-cepat").json()["tujuan"]
            koordinat = lambda i: [tujuan[i]["lon"], tujuan[i]["lat"]]
            geometri = c.get("/api/jaringan")
            data = {"asal":koordinat(1), "tujuan":koordinat(2), "moda":"motor"}
            rute_ms, kondisi_ms, ukuran = [], [], []
            awal = proses.memory_info().rss / 2**20
            per_putaran = []
            for putaran in range(3):
                for i in range(30):
                    waktu = jam[[0,8,13,33,37][i % 5]]["waktu_utc"]
                    t = time.perf_counter()
                    r = c.get("/api/kondisi", params={"waktu":waktu})
                    r.raise_for_status()
                    kondisi_ms.append((time.perf_counter()-t)*1000)
                    ukuran.append(len(r.content))
                    t = time.perf_counter()
                    r = c.post("/api/rute", json={**data,"waktu":waktu})
                    r.raise_for_status()
                    rute_ms.append((time.perf_counter()-t)*1000)
                per_putaran.append(proses.memory_info().rss / 2**20)
            # Sejumlah request serentak hanya di localhost: boleh menolak
            # beban lebih dengan 503, tidak boleh menjadi 500/tidak respons.
            with ThreadPoolExecutor(max_workers=6) as pool:
                status = list(pool.map(lambda _: c.post("/api/rute", json={
                    **data,"waktu":jam[8]["waktu_utc"]}).status_code, range(6)))
            assert set(status) <= {200,503} and 200 in status
            p95 = lambda x: round(sorted(x)[math.ceil(.95*len(x))-1],2)
            hasil = {"tanggal_utc":datetime.now(timezone.utc).isoformat(),
                "lingkungan":"Windows localhost, potret, satu worker; bukan container Linux/VPS",
                "sampel_per_endpoint":len(rute_ms), "putaran":3,
                "rute_p95_ms":p95(rute_ms), "kondisi_p95_ms":p95(kondisi_ms),
                "geometri_sekali_bytes":len(geometri.content),
                "kondisi_min_maks_bytes":[min(ukuran),max(ukuran)],
                "rss_awal_mib":round(awal,1),
                "rss_per_putaran_mib":[round(x,1) for x in per_putaran],
                "rss_puncak_sampel_mib":round(max(samples),1),
                "enam_request_lokal_status":status}
            info = proses.memory_info()
            for key in ("private", "peak_wset", "peak_pagefile"):
                if hasattr(info, key):
                    hasil[f"windows_{key}_mib"] = round(getattr(info,key)/2**20,1)
            out=Path(__file__).resolve().parents[2]/"docs/final/bukti/kinerja_21_september.json"
            out.parent.mkdir(exist_ok=True)
            out.write_text(json.dumps(hasil,indent=2),encoding="utf-8")
            print(json.dumps(hasil,indent=2))
    finally:
        stop.set()
        thread.join()


if __name__ == "__main__":
    main()
