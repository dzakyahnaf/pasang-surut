"""Tarik deret waktu backscatter Sentinel-1 per ruas dari Earth Engine.

    python -m scripts.08_ekstrak_s1                  # seluruh arsip
    python -m scripts.08_ekstrak_s1 --tahun 2024     # satu tahun saja
    python -m scripts.08_ekstrak_s1 --contoh         # uji cepat, 1 tahun 200 ruas

YANG DIAMBIL SKRIP INI, DAN YANG TIDAK.

Skrip ini HANYA menarik nilai backscatter VV mentah dalam desibel untuk tiap
ruas pada tiap tanggal akuisisi. Ia TIDAK memutuskan mana yang basah dan mana
yang kering.

Itu keputusan sengaja. Klasifikasi basah/kering adalah bagian yang paling
perlu disetel berulang kali: ambangnya, cara menormalkan terhadap keadaan
biasa, perlakuan terhadap arah orbit. Kalau klasifikasi dikerjakan di dalam
Earth Engine, tiap kali ambangnya diubah seluruh arsip harus ditarik ulang
dan kuota bulanan habis untuk percobaan. Dengan menarik nilai mentahnya
sekali, seluruh penyetelan bisa dilakukan di laptop tanpa biaya, dan tanpa
internet.

KENAPA HANYA SEBAGIAN RUAS.

Arsipnya 725 citra dan ruasnya 19.394. Menarik semuanya berarti 14 juta
nilai, dan itu memboroskan kuota bulanan yang tidak bisa ditambah sebelum
tenggat. Yang ditarik adalah sampel ruas BERSTRATA menurut elevasi dan jarak
pantai, supaya ruang fitur tetap terwakili. Model dilatih pada sampel itu
lalu MEMPREDIKSI seluruh 19.394 ruas — memang begitu cara model dipakai.

Daftar ruas terpilih disimpan supaya bisa dijalankan ulang persis sama.

KENAPA ARAH ORBIT IKUT DICATAT.

Backscatter radar bergantung pada geometri sudut pandang. Citra ascending
dan descending atas titik yang sama menghasilkan nilai berbeda meski
permukaannya identik. Membandingkan keduanya tanpa memisahkan orbit akan
memunculkan "perubahan" yang sebenarnya hanya perbedaan sudut pandang.
Nomor orbit relatif dan arah lintasan karena itu ikut disimpan, dan
normalisasi di skrip berikutnya dilakukan PER ORBIT.

CATATAN SPECKLE. Radar SAR selalu berbintik. Sebelum dicuplik, tiap citra
dihaluskan dengan median fokal beradius 30 meter. Tanpa itu, nilai satu
piksel lebih banyak memuat derau daripada isyarat.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np

from app import config, db

PROYEK = "pasang-surut-anforcom"
KOLEKSI = "COPERNICUS/S1_GRD"

SKALA_M = 30            # aturan repo: jangan 10, kuota tidak akan cukup
RADIUS_HALUS_M = 30     # median fokal peredam speckle
TAHUN_AWAL = 2015
TAHUN_AKHIR = 2026

# Dinaikkan sampai batas yang masih aman untuk satu permintaan interaktif.
# Terlalu besar berarti permintaan kehabisan waktu; terlalu kecil berarti
# jumlah permintaannya membengkak.
RUAS_PER_PERMINTAAN = 500
TARGET_RUAS = 2500

BERKAS_SAMPEL_RUAS = config.DIR_DATA_OLAHAN / "ruas_sampel_latih.json"
BERKAS_KELUARAN = config.DIR_DATA_OLAHAN / "s1_vv_ruas.jsonl"
BERKAS_CITRA = config.DIR_DATA_OLAHAN / "s1_daftar_citra.json"


# ══════════════════════════════════════════════════════════════════════════
# PEMILIHAN RUAS BERSTRATA
# ══════════════════════════════════════════════════════════════════════════
def pilih_ruas(target: int) -> list[dict]:
    """Pilih ruas berstrata menurut elevasi dan jarak pantai.

    Pengambilan acak sederhana akan didominasi jalan kampung di tengah kota
    yang jumlahnya paling banyak, sementara ruas pesisir berelevasi rendah —
    justru yang paling menentukan — hanya kebagian sedikit. Strata lima kali
    lima memastikan tiap sudut ruang fitur terwakili.
    """
    if BERKAS_SAMPEL_RUAS.exists():
        tersimpan = json.loads(BERKAS_SAMPEL_RUAS.read_text(encoding="utf-8"))
        print(f"memakai daftar ruas tersimpan: {len(tersimpan['ruas']):,} ruas")
        return tersimpan["ruas"]

    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT edge_id, elevasi_m, jarak_pantai_m,
                       ST_X(ST_LineInterpolatePoint(geom, 0.5)),
                       ST_Y(ST_LineInterpolatePoint(geom, 0.5))
                FROM ruas_jalan
                WHERE elevasi_m IS NOT NULL AND jarak_pantai_m IS NOT NULL
                ORDER BY edge_id
                """
            )
            baris = kur.fetchall()

    edge = np.array([b[0] for b in baris], dtype=np.int64)
    elev = np.array([float(b[1]) for b in baris])
    jarak = np.array([float(b[2]) for b in baris])
    lon = np.array([float(b[3]) for b in baris])
    lat = np.array([float(b[4]) for b in baris])

    def kelompok(nilai: np.ndarray, n: int = 5) -> np.ndarray:
        tepi = np.percentile(nilai, np.linspace(0, 100, n + 1)[1:-1])
        return np.digitize(nilai, tepi)

    strata = kelompok(elev) * 5 + kelompok(jarak)
    acak = np.random.default_rng(2026)          # tetap, supaya bisa diulang
    terpilih: list[int] = []
    for s in np.unique(strata):
        anggota = np.flatnonzero(strata == s)
        jatah = min(len(anggota), max(1, round(target * len(anggota) / len(edge))))
        terpilih.extend(acak.choice(anggota, size=jatah, replace=False).tolist())

    terpilih = sorted(set(terpilih))
    ruas = [
        {"edge_id": int(edge[i]), "lon": round(float(lon[i]), 6),
         "lat": round(float(lat[i]), 6), "strata": int(strata[i])}
        for i in terpilih
    ]
    BERKAS_SAMPEL_RUAS.write_text(json.dumps({
        "_catatan": ("Ruas terpilih untuk penarikan Sentinel-1. Berstrata "
                     "menurut elevasi dan jarak pantai, benih acak 2026, "
                     "supaya penarikan bisa diulang persis sama."),
        "dibuat": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "jumlah": len(ruas),
        "ruas": ruas,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"ruas terpilih: {len(ruas):,} dari {len(edge):,} "
          f"({len(np.unique(strata))} strata)")
    return ruas


# ══════════════════════════════════════════════════════════════════════════
# EARTH ENGINE
# ══════════════════════════════════════════════════════════════════════════
def koleksi_s1(ee, geom, awal: str, akhir: str):
    return (ee.ImageCollection(KOLEKSI)
            .filterBounds(geom)
            .filterDate(awal, akhir)
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VV"))
            .select("VV")
            .sort("system:time_start"))


def daftar_citra(ee, geom) -> list[dict]:
    """Metadata tiap citra: indeks, waktu, arah orbit, nomor orbit relatif."""
    if BERKAS_CITRA.exists():
        d = json.loads(BERKAS_CITRA.read_text(encoding="utf-8"))
        print(f"memakai daftar citra tersimpan: {len(d['citra']):,} citra")
        return d["citra"]

    kol = koleksi_s1(ee, geom, f"{TAHUN_AWAL}-01-01", f"{TAHUN_AKHIR + 1}-01-01")
    print("mengambil metadata seluruh citra ...")
    mentah = kol.reduceColumns(
        ee.Reducer.toList(4),
        ["system:index", "system:time_start",
         "orbitProperties_pass", "relativeOrbitNumber_start"],
    ).getInfo()["list"]

    citra = [{
        "indeks": a,
        "waktu": datetime.fromtimestamp(b / 1000.0, timezone.utc).isoformat(),
        "orbit_arah": c,
        "orbit_relatif": int(d),
    } for a, b, c, d in mentah]

    BERKAS_CITRA.write_text(json.dumps({
        "_catatan": "Metadata citra Sentinel-1 GRD IW VV di atas AOI.",
        "diambil": datetime.now(timezone.utc).isoformat(),
        "koleksi": KOLEKSI,
        "jumlah": len(citra),
        "citra": citra,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"citra: {len(citra):,}")
    return citra


def tarik_setahun(ee, ruas: list[dict], tahun: int) -> list[dict]:
    """Tarik VV dB tiap ruas untuk seluruh citra pada satu tahun.

    Seluruh citra setahun digabung jadi satu gambar bermultipita lewat
    toBands(), lalu dicuplik SEKALI per kelompok titik. Satu permintaan
    menghasilkan seluruh deret waktu setahun untuk lima ratus ruas, jauh
    lebih hemat daripada satu permintaan per citra.
    """
    aoi = json.load(config.BERKAS_AOI.open(encoding="utf-8"))
    geom = ee.Geometry(aoi["features"][0]["geometry"])
    kol = koleksi_s1(ee, geom, f"{tahun}-01-01", f"{tahun + 1}-01-01")

    n = kol.size().getInfo()
    if n == 0:
        print(f"  {tahun}: tidak ada citra")
        return []

    # toBands() sendiri yang memberi nama pita, berbentuk "<system:index>_VV",
    # jadi tidak perlu rename manual. Nama itulah yang dicocokkan ke daftar
    # citra untuk mendapatkan waktu akuisisi dan orbitnya.
    halus = kol.map(
        lambda img: img.focal_median(RADIUS_HALUS_M, "circle", "meters")
    )
    gabungan = halus.toBands()

    hasil: list[dict] = []
    for i in range(0, len(ruas), RUAS_PER_PERMINTAAN):
        potongan = ruas[i:i + RUAS_PER_PERMINTAAN]
        titik = ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([r["lon"], r["lat"]]),
                       {"edge_id": r["edge_id"]})
            for r in potongan
        ])
        mulai = time.time()
        balasan = gabungan.reduceRegions(
            collection=titik,
            reducer=ee.Reducer.first(),
            scale=SKALA_M,
        ).getInfo()
        lama = time.time() - mulai
        for f in balasan["features"]:
            sifat = dict(f["properties"])
            edge_id = int(sifat.pop("edge_id"))
            for pita, nilai in sifat.items():
                if nilai is None:
                    continue
                hasil.append({"edge_id": edge_id, "pita": pita,
                              "vv_db": round(float(nilai), 3)})
        print(f"  {tahun}: ruas {i + 1}-{i + len(potongan)} dari {len(ruas)}, "
              f"{n} citra, {lama:.0f} detik")
    return hasil


# ══════════════════════════════════════════════════════════════════════════
def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--tahun", type=int, default=None)
    pengurai.add_argument("--contoh", action="store_true",
                          help="uji cepat: 2024 saja, 200 ruas")
    pengurai.add_argument("--target-ruas", type=int, default=TARGET_RUAS)
    argumen = pengurai.parse_args()

    try:
        import ee
    except ImportError:
        raise SystemExit("earthengine-api belum terpasang.")

    ee.Initialize(project=PROYEK)
    print(f"terhubung ke proyek Earth Engine {PROYEK}\n")

    ruas = pilih_ruas(argumen.target_ruas)
    if argumen.contoh:
        ruas = ruas[:200]
        tahun_dipakai = [2024]
        print("MODE CONTOH: 200 ruas, tahun 2024 saja\n")
    elif argumen.tahun:
        tahun_dipakai = [argumen.tahun]
    else:
        tahun_dipakai = list(range(TAHUN_AWAL, TAHUN_AKHIR + 1))

    aoi = json.load(config.BERKAS_AOI.open(encoding="utf-8"))
    geom = ee.Geometry(aoi["features"][0]["geometry"])
    daftar_citra(ee, geom)

    sudah = set()
    if BERKAS_KELUARAN.exists() and not argumen.contoh:
        with BERKAS_KELUARAN.open(encoding="utf-8") as f:
            for garis in f:
                try:
                    sudah.add(json.loads(garis)["tahun"])
                except (json.JSONDecodeError, KeyError):
                    continue
        if sudah:
            print(f"tahun yang sudah ada di berkas: {sorted(sudah)}\n")

    mode = "w" if argumen.contoh else "a"
    berkas = (config.DIR_DATA_OLAHAN / "s1_vv_contoh.jsonl" if argumen.contoh
              else BERKAS_KELUARAN)
    total = 0
    with berkas.open(mode, encoding="utf-8") as keluar:
        for tahun in tahun_dipakai:
            if tahun in sudah:
                print(f"  {tahun}: dilewati, sudah ada")
                continue
            baris = tarik_setahun(ee, ruas, tahun)
            for b in baris:
                b["tahun"] = tahun
                keluar.write(json.dumps(b, separators=(",", ":")) + "\n")
            keluar.flush()
            total += len(baris)
            print(f"  {tahun}: {len(baris):,} nilai tersimpan\n")

    print(f"selesai. {total:,} nilai ditulis ke {berkas.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
