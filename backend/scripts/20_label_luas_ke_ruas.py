"""Ubah ukuran LUAS air kawasan terbuka menjadi label per RUAS, lalu uji.

    python -m scripts.20_label_luas_ke_ruas
    python -m scripts.20_label_luas_ke_ruas --uji     # uji saja, dari cache

LANGKAH INFERENSI YANG SELAMA INI DISEBUT "BELUM TERVALIDASI".

Skrip 12 menemukan sesuatu: setelah air permanen dibuang, proporsi DARATAN
yang tampak berair berkorelasi +0,36 terhadap pasut pada orbit 76. Itu ukuran
LUAS untuk seluruh AOI — satu angka per citra.

Sistem ini merutekan per ruas jalan, bukan per AOI. Untuk memakai temuan itu,
angka luas harus diubah menjadi label per ruas, dan perubahan itulah yang
berulang kali kami sebut "satu langkah inferensi lagi yang belum tervalidasi".

Skrip ini mengerjakan langkah tersebut, lalu mengujinya. Kalau labelnya
bertahan, model layak dihidupkan. Kalau runtuh saat turun ke tingkat ruas,
kita tahu persis di mana ia runtuh — dan itu keterangan yang lebih berguna
daripada "belum divalidasi".

BEDANYA DENGAN SKRIP 08 DAN 09.

Skrip 08 menarik nilai backscatter mentah, dan skrip 09 memberi label lewat
penurunan terhadap garis dasar tiap ruas. Kriteria itu gagal.

Di sini kriterianya berbeda dan mengikuti temuan skrip 12:

    1. Bangun topeng AIR PERMANEN per orbit: piksel yang gelap pada lebih
       dari 40 persen akuisisi. Tambak, muara, dan laut dibuang.
    2. Sebuah piksel DARAT disebut basah bila nilainya di bawah ambang air
       terbuka MUTLAK, bukan relatif terhadap dirinya sendiri.
    3. Sebuah RUAS disebut basah bila cukup banyak piksel darat di
       sekelilingnya basah.

Butir ketiga adalah inferensinya. Radius dan ambang proporsinya adalah
pilihan kami, dan keduanya dinyatakan sebagai pilihan.

KENAPA ORBIT 76 SAJA.

Isyarat pada skrip 12 hanya muncul di orbit 76; orbit 127 memberi +0,03.
Menarik keduanya berarti membayar dua kali untuk satu yang sudah diketahui
kosong. Kalau orbit 76 bertahan di tingkat ruas, orbit 127 layak ditarik
sebagai uji tandingan — bukan sebaliknya.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, datetime, timedelta, timezone

import numpy as np

from app import config
from app.domain import pasut

PROYEK = "pasang-surut-anforcom"
KOLEKSI = "COPERNICUS/S1_GRD"

ORBIT = 76                # satu-satunya orbit yang menunjukkan isyarat
AMBANG_AIR_DB = -15.0     # ambang air terbuka mutlak, sama seperti skrip 12
AMBANG_PERMANEN = 0.4     # gelap pada >40 persen akuisisi = tubuh air tetap
RADIUS_M = 100.0          # lingkungan ruas; PILIHAN kami, bukan pengukuran
SKALA_M = 30
TAHUN = (2019, 2026)
RUAS_PER_PERMINTAAN = 400

BERKAS_RUAS = config.DIR_DATA_OLAHAN / "ruas_sampel_latih.json"
BERKAS_CACHE = config.DIR_DATA_OLAHAN / "s1_basah_luas_ruas.jsonl"
BERKAS_HASIL = config.DIR_DATA_REFERENSI / "uji_label_luas_ke_ruas.json"


def koleksi(ee, geom):
    return (ee.ImageCollection(KOLEKSI)
            .filterBounds(geom)
            .filterDate(f"{TAHUN[0]}-01-01", f"{TAHUN[1] + 1}-01-01")
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.eq("relativeOrbitNumber_start", ORBIT))
            .select("VV")
            .sort("system:time_start"))


def tarik(ee, ruas: list[dict]) -> int:
    aoi = json.loads(config.BERKAS_AOI.read_text(encoding="utf-8"))
    geom = ee.Geometry(aoi["features"][0]["geometry"])
    kol = koleksi(ee, geom)
    n = kol.size().getInfo()
    print(f"citra orbit {ORBIT}: {n}")
    if n < 20:
        raise SystemExit("Citra terlalu sedikit.")

    halus = kol.map(
        lambda img: img.focal_median(30, "circle", "meters").rename("VV"))
    gelap = halus.map(lambda img: img.lt(AMBANG_AIR_DB))
    darat = gelap.mean().lt(AMBANG_PERMANEN)
    print(f"topeng air permanen: piksel gelap >{AMBANG_PERMANEN:.0%} akuisisi\n")

    # Basah = gelap DAN darat. toBands() menyusun seluruh citra jadi satu
    # gambar bermultipita supaya satu permintaan mengembalikan deret penuh.
    basah = halus.map(
        lambda img: img.lt(AMBANG_AIR_DB).And(darat).rename(
            img.get("system:index")))
    gabungan = basah.toBands()

    ditulis = 0
    with BERKAS_CACHE.open("w", encoding="utf-8") as keluar:
        for i in range(0, len(ruas), RUAS_PER_PERMINTAAN):
            potong = ruas[i:i + RUAS_PER_PERMINTAAN]
            titik = ee.FeatureCollection([
                ee.Feature(
                    ee.Geometry.Point([r["lon"], r["lat"]]).buffer(RADIUS_M),
                    {"edge_id": r["edge_id"]})
                for r in potong
            ])
            mulai = time.time()
            balasan = gabungan.reduceRegions(
                collection=titik, reducer=ee.Reducer.mean(), scale=SKALA_M
            ).getInfo()
            for f in balasan["features"]:
                sifat = dict(f["properties"])
                edge_id = int(sifat.pop("edge_id"))
                for pita, nilai in sifat.items():
                    if nilai is None:
                        continue
                    keluar.write(json.dumps(
                        {"edge_id": edge_id, "pita": pita,
                         "basah": round(float(nilai), 4)},
                        separators=(",", ":")) + "\n")
                    ditulis += 1
            keluar.flush()
            print(f"  ruas {i + 1}-{i + len(potong)} dari {len(ruas)}, "
                  f"{time.time() - mulai:.0f} detik", flush=True)
    print(f"\n{ditulis:,} nilai ditulis ke {BERKAS_CACHE.name}")
    return ditulis


def hari_kejadian() -> set[date]:
    kej = json.loads(
        (config.DIR_DATA_REFERENSI / "kejadian_rob_semarang.json")
        .read_text(encoding="utf-8"))["kejadian"]
    hari: set[date] = set()
    for k in kej:
        t = k.get("tanggal")
        if not t:
            continue
        p = t.split("/")
        try:
            if len(p) == 2:
                a, b = date.fromisoformat(p[0]), date.fromisoformat(p[1])
                if b >= a and (b - a).days <= 30:
                    d = a
                    while d <= b:
                        hari.add(d)
                        d += timedelta(days=1)
            else:
                hari.add(date.fromisoformat(p[0]))
        except ValueError:
            continue
    return hari


def uji() -> int:
    if not BERKAS_CACHE.exists():
        raise SystemExit(f"{BERKAS_CACHE.name} belum ada. Jalankan tanpa --uji.")

    citra = json.loads(
        (config.DIR_DATA_OLAHAN / "s1_daftar_citra.json")
        .read_text(encoding="utf-8"))["citra"]
    urutan = {c["indeks"]: i for i, c in enumerate(citra)}

    edge, idx, basah = [], [], []
    with BERKAS_CACHE.open(encoding="utf-8") as f:
        for garis in f:
            b = json.loads(garis)
            nama = b["pita"].rsplit("_", 1)[0] if b["pita"].endswith("_VV") \
                else b["pita"]
            i = urutan.get(nama) or urutan.get(b["pita"])
            if i is None:
                continue
            edge.append(b["edge_id"]); idx.append(i); basah.append(b["basah"])
    edge = np.array(edge, np.int64); idx = np.array(idx, np.int32)
    basah = np.array(basah, np.float64)
    print(f"nilai: {len(basah):,}  ruas: {len(np.unique(edge)):,}  "
          f"citra: {len(np.unique(idx)):,}\n")
    if len(basah) < 1000:
        raise SystemExit("Data terlalu sedikit.")

    waktu = [datetime.fromisoformat(citra[i]["waktu"]).astimezone(timezone.utc)
             for i in range(len(citra))]
    astro = np.array([float(pasut.tinggi_pasut_m(w)) for w in waktu])
    hari = hari_kejadian()
    tgl = np.array([w.date() for w in waktu])
    dekat = np.array([any((t + timedelta(days=o)) in hari for o in (-1, 0, 1))
                      for t in tgl])

    print(f"{'ambang proporsi':>16} {'laju basah':>12} {'korelasi pasut':>16} "
          f"{'kejadian (sigma)':>18}")
    print("-" * 66)
    hasil = {}
    for ambang in (0.05, 0.10, 0.20, 0.30):
        label = basah >= ambang
        frak = np.full(len(citra), np.nan)
        for i in range(len(citra)):
            m = idx == i
            if m.sum() >= 100:
                frak[i] = label[m].mean()
        ok = np.isfinite(frak)
        if ok.sum() < 50 or frak[ok].std() < 1e-12:
            continue
        k = float(np.corrcoef(frak[ok], astro[ok])[0, 1])
        a_, b_ = frak[ok & dekat], frak[ok & ~dekat]
        sig = (float((a_.mean() - b_.mean()) / b_.std())
               if len(a_) >= 3 and b_.std() > 0 else float("nan"))
        hasil[f"{ambang:.2f}"] = {
            "laju_basah": round(float(label.mean()), 4),
            "korelasi_pasut": round(k, 4),
            "selisih_kejadian_sigma": None if not np.isfinite(sig) else round(sig, 3),
            "citra_dipakai": int(ok.sum()),
        }
        print(f"{ambang:>16.2f} {100 * label.mean():>11.2f}% {k:>+16.4f} "
              f"{sig:>+18.2f}")

    terbaik = max((abs(v["korelasi_pasut"]) for v in hasil.values()), default=0.0)
    print()
    print("=" * 66)
    print(f"korelasi mutlak tertinggi di tingkat RUAS: {terbaik:.4f}")
    print("pembanding: di tingkat LUAS seluruh AOI, skrip 12 memperoleh 0,3624")
    if terbaik >= 0.30:
        putusan = "BERTAHAN"
        kalimat = ("Isyarat bertahan saat turun ke tingkat ruas. Langkah "
                   "inferensi dari luas ke ruas TIDAK meruntuhkannya, dan "
                   "model layak dihidupkan dengan kriteria ini.")
    elif terbaik >= 0.15:
        putusan = "MELEMAH"
        kalimat = ("Isyarat melemah tetapi tidak hilang saat turun ke tingkat "
                   "ruas. Layak disebut sebagai arah lanjutan yang lebih "
                   "konkret, belum cukup untuk melatih model.")
    else:
        putusan = "RUNTUH"
        kalimat = ("Isyarat RUNTUH saat turun ke tingkat ruas. Yang terlihat "
                   "di tingkat luas tidak dapat dialamatkan ke ruas jalan "
                   "tertentu, dan itu persis yang dibutuhkan sistem perutean.")
    print(f"PUTUSAN: {putusan}")
    print(kalimat)

    BERKAS_HASIL.write_text(json.dumps({
        "_catatan": ("Uji apakah isyarat luas air kawasan terbuka bertahan "
                     "saat diubah menjadi label per ruas jalan."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "orbit": ORBIT,
        "ambang_air_db": AMBANG_AIR_DB,
        "ambang_permanen": AMBANG_PERMANEN,
        "radius_m": RADIUS_M,
        "tahun": list(TAHUN),
        "pembanding_tingkat_luas": 0.3624,
        "korelasi_mutlak_tertinggi": round(terbaik, 4),
        "putusan": putusan,
        "kesimpulan": kalimat,
        "per_ambang_proporsi": hasil,
        "_peringatan": [
            "Radius 100 m dan ambang proporsi adalah PILIHAN tim, bukan hasil "
            "pengukuran. Keduanya dinyatakan sebagai pilihan.",
            "Hanya orbit 76 yang ditarik, karena hanya orbit itu yang "
            "menunjukkan isyarat di tingkat luas.",
            "Rancu musiman yang berlaku pada uji tingkat luas berlaku juga di "
            "sini; lihat skrip 21.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--uji", action="store_true")
    a = p.parse_args()
    if a.uji:
        return uji()

    import ee
    ee.Initialize(project=PROYEK)
    ruas = json.loads(BERKAS_RUAS.read_text(encoding="utf-8"))["ruas"]
    print(f"ruas sampel: {len(ruas):,}\n")
    tarik(ee, ruas)
    print()
    return uji()


if __name__ == "__main__":
    sys.exit(main())
