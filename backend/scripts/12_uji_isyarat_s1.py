"""Uji menentukan: apakah Sentinel-1 melihat pasang surut di AOI ini sama sekali?

    python -m scripts.12_uji_isyarat_s1
    python -m scripts.12_uji_isyarat_s1 --tahun 2024

PERTANYAAN YANG DIJAWAB SKRIP INI.

Skrip 09 menyimpulkan label basah dari backscatter tidak berkorelasi dengan
pasut. Tetapi kesimpulan itu diambil dari cuplikan SATU PIKSEL di titik tengah
tiap ruas jalan. Ada dua kemungkinan yang belum dipisahkan:

    A. Sentinel-1 memang tidak melihat rob di wilayah ini.
    B. Sentinel-1 melihatnya, tetapi tidak di atas jalan — dan cara
       pencuplikan kamilah yang salah.

Bedanya menentukan nasib seluruh jalur model. Kalau B yang benar, modelnya
bisa diselamatkan dengan mencuplik ulang di tempat yang benar. Kalau A yang
benar, tidak ada penyetelan ambang yang akan menolong.

CARA MEMISAHKANNYA.

Berhenti melihat jalan. Untuk tiap citra, hitung PROPORSI LUAS di dalam AOI
yang backscatter-nya di bawah ambang air terbuka, lalu lihat apakah proporsi
itu naik-turun mengikuti pasut.

Uji ini jauh lebih peka daripada uji di skrip 09 karena dua hal. Pertama, ia
memakai seluruh piksel AOI, bukan 2.502 titik. Kedua, dan ini yang penting,
ia melihat KAWASAN TERBUKA — tambak, lahan kosong, muara — tempat air pasang
memang membentuk permukaan halus yang bisa dilihat radar. Jalan perkotaan
selebar belasan meter di dalam piksel 30 meter yang penuh bangunan adalah
tempat paling sulit untuk melihat air, dan seharusnya bukan tempat pertama
yang dicoba.

Ambang mutlak DIPAKAI di sini, berbeda dari skrip 09. Di kawasan terbuka
ambang mutlak memang cara yang benar: air terbuka betul-betul memantulkan
gelombang menjauh dari satelit, dan nilainya jatuh jauh di bawah daratan.

KALAU HASILNYA POSITIF, apa artinya. Berarti isyarat pasang surut ADA di
citra, dan label genangan bisa dibangun dari luas air di kawasan terbuka lalu
dikaitkan ke ruas jalan terdekat. Itu jalan keluar yang sah dan model bisa
dihidupkan lagi.

KALAU HASILNYA NEGATIF, tidak ada gunanya menyetel ambang lebih lanjut.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import numpy as np

from app import config
from app.domain import pasut

PROYEK = "pasang-surut-anforcom"
KOLEKSI = "COPERNICUS/S1_GRD"
SKALA_M = 50            # diagnosis, bukan produksi: lebih kasar, lebih murah
AMBANG_AIR_DB = (-15.0, -17.0, -19.0)

BERKAS_HASIL = config.DIR_DATA_REFERENSI / "uji_isyarat_s1.json"


def koleksi(ee, geom, tahun: int):
    return (ee.ImageCollection(KOLEKSI)
            .filterBounds(geom)
            .filterDate(f"{tahun}-01-01", f"{tahun + 1}-01-01")
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VV"))
            .select("VV")
            .sort("system:time_start"))


def proporsi_air(ee, geom, tahun: int, ambang: float) -> list[dict]:
    """Proporsi luas AOI di bawah ambang, untuk tiap citra pada satu tahun."""
    kol = koleksi(ee, geom, tahun)
    if kol.size().getInfo() == 0:
        return []

    def satu(img):
        halus = img.focal_median(30, "circle", "meters")
        basah = halus.lt(ambang)
        rata = basah.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=geom,
            scale=SKALA_M, maxPixels=int(1e9), bestEffort=True)
        return ee.Feature(None, {
            "waktu": img.get("system:time_start"),
            "orbit": img.get("relativeOrbitNumber_start"),
            "arah": img.get("orbitProperties_pass"),
            "proporsi": rata.get("VV"),
        })

    fitur = ee.FeatureCollection(kol.map(satu)).getInfo()["features"]
    hasil = []
    for f in fitur:
        s = f["properties"]
        if s.get("proporsi") is None:
            continue
        hasil.append({
            "waktu": datetime.fromtimestamp(
                s["waktu"] / 1000.0, timezone.utc).isoformat(),
            "orbit": int(s["orbit"]),
            "arah": s["arah"],
            "proporsi": float(s["proporsi"]),
        })
    return hasil


def proporsi_air_di_darat(ee, geom, tahun: list[int], orbit: int,
                          ambang: float) -> list[dict]:
    """Proporsi piksel DARAT yang tampak berair, per citra, untuk satu orbit.

    KENAPA AIR PERMANEN HARUS DIBUANG LEBIH DULU.

    Uji sebelumnya mengukur seluruh luas gelap di dalam AOI dan mendapat
    korelasi NEGATIF terhadap pasut. Penyebabnya bukan misteri: sebagian besar
    luas gelap itu tambak, muara, dan laut — bukan genangan. Luas tampaknya
    berubah mengikuti kekasaran permukaan, dan air dangkal yang tenang saat
    surut justru lebih halus, lebih gelap, dan lebih luas terlihat daripada
    air dalam yang beriak saat pasang.

    Isyarat yang dicari — daratan yang berubah menjadi air — hanya beberapa
    persen luas dan tenggelam di bawah ragam itu.

    Karena itu di sini dibangun topeng AIR PERMANEN: piksel yang gelap pada
    lebih dari 40 persen seluruh akuisisi dianggap tubuh air tetap dan
    dikeluarkan. Yang dihitung setelahnya adalah proporsi piksel DARAT yang
    tampak berair, dan itulah ukuran genangan yang sebenarnya.

    Dihitung PER ORBIT karena topeng air permanen pun bergantung geometri
    sudut pandang.
    """
    kol = (ee.ImageCollection(KOLEKSI)
           .filterBounds(geom)
           .filterDate(f"{min(tahun)}-01-01", f"{max(tahun) + 1}-01-01")
           .filter(ee.Filter.eq("instrumentMode", "IW"))
           .filter(ee.Filter.listContains(
               "transmitterReceiverPolarisation", "VV"))
           .filter(ee.Filter.eq("relativeOrbitNumber_start", orbit))
           .select("VV")
           .sort("system:time_start"))
    n = kol.size().getInfo()
    if n < 20:
        return []

    gelap = kol.map(
        lambda img: img.focal_median(30, "circle", "meters").lt(ambang))
    frekuensi = gelap.mean()
    darat = frekuensi.lt(0.4)

    def satu(img):
        basah = (img.focal_median(30, "circle", "meters").lt(ambang)
                 .updateMask(darat))
        rata = basah.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=geom,
            scale=SKALA_M, maxPixels=int(1e9), bestEffort=True)
        return ee.Feature(None, {
            "waktu": img.get("system:time_start"),
            "proporsi": rata.get("VV"),
        })

    fitur = ee.FeatureCollection(kol.map(satu)).getInfo()["features"]
    hasil = []
    for f in fitur:
        d = f["properties"]
        if d.get("proporsi") is None:
            continue
        hasil.append({
            "waktu": datetime.fromtimestamp(
                d["waktu"] / 1000.0, timezone.utc).isoformat(),
            "orbit": orbit,
            "arah": "",
            "proporsi": float(d["proporsi"]),
        })
    return hasil


def korelasi_per_orbit(baris: list[dict]) -> dict:
    """Korelasi proporsi air terhadap pasut, dihitung PER ORBIT RELATIF.

    Wajib dipisah per orbit. Geometri sudut pandang yang berbeda menggeser
    seluruh nilai backscatter, sehingga mencampur orbit menyuntikkan ragam
    yang tidak ada hubungannya dengan air.
    """
    per = {}
    for b in baris:
        per.setdefault(b["orbit"], []).append(b)

    hasil = {}
    for orbit, kelompok in sorted(per.items()):
        if len(kelompok) < 20:
            continue
        p = np.array([k["proporsi"] for k in kelompok])
        t = np.array([
            float(pasut.tinggi_pasut_m(datetime.fromisoformat(k["waktu"])))
            for k in kelompok
        ])
        if p.std() < 1e-12:
            continue
        hasil[orbit] = {
            "citra": len(kelompok),
            "arah": kelompok[0]["arah"],
            "korelasi": round(float(np.corrcoef(p, t)[0, 1]), 4),
            "proporsi_rata": round(float(p.mean()), 5),
            "proporsi_simpangan": round(float(p.std()), 5),
            "pasut_simpangan": round(float(t.std()), 4),
        }
    return hasil


def uji_darat(ee, geom, tahun: list[int]) -> int:
    """Uji lanjutan: proporsi DARAT yang berair, setelah air permanen dibuang."""
    print("UJI LANJUTAN: air permanen dibuang lebih dulu")
    print("piksel yang gelap pada lebih dari 40 persen akuisisi dianggap")
    print("tubuh air tetap dan dikeluarkan dari perhitungan.\n")

    terbaik = 0.0
    laporan = {}
    for orbit in (76, 127):
        for ambang in (-15.0, -17.0):
            baris = proporsi_air_di_darat(ee, geom, tahun, orbit, ambang)
            if not baris:
                print(f"orbit {orbit} ambang {ambang:+.0f} dB: citra kurang")
                continue
            p = np.array([b["proporsi"] for b in baris])
            t = np.array([
                float(pasut.tinggi_pasut_m(datetime.fromisoformat(b["waktu"])))
                for b in baris
            ])
            if p.std() < 1e-12:
                continue
            k = float(np.corrcoef(p, t)[0, 1])
            terbaik = max(terbaik, abs(k))
            print(f"orbit {orbit:>3}  ambang {ambang:+.0f} dB  {len(baris):>3} citra")
            print(f"  darat tampak berair : {100 * p.mean():.2f} persen "
                  f"(simpangan {100 * p.std():.2f})")
            print(f"  korelasi vs pasut   : {k:+.4f}")
            print()
            laporan[f"orbit{orbit}_{ambang:+.0f}dB"] = {
                "citra": len(baris),
                "darat_berair_rata_persen": round(100 * float(p.mean()), 3),
                "darat_berair_simpangan_persen": round(100 * float(p.std()), 3),
                "korelasi": round(k, 4),
            }

    print("=" * 66)
    if terbaik >= 0.35:
        putusan = "ADA ISYARAT"
    elif terbaik >= 0.2:
        putusan = "ISYARAT LEMAH"
    else:
        putusan = "TIDAK ADA ISYARAT"
    print(f"PUTUSAN setelah air permanen dibuang: {putusan}")
    print(f"korelasi mutlak tertinggi: {terbaik:.4f}")

    berkas = config.DIR_DATA_REFERENSI / "uji_isyarat_s1_darat.json"
    berkas.write_text(json.dumps({
        "_catatan": ("Uji isyarat Sentinel-1 SETELAH air permanen dibuang. "
                     "Piksel gelap pada lebih dari 40 persen akuisisi "
                     "dianggap tubuh air tetap."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "tahun": tahun,
        "putusan": putusan,
        "korelasi_mutlak_tertinggi": round(terbaik, 4),
        "per_kombinasi": laporan,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"tersimpan: {berkas.name}")
    return 0


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--tahun", type=int, action="append", default=None)
    pengurai.add_argument("--darat-saja", action="store_true",
                          help="buang air permanen lebih dulu")
    argumen = pengurai.parse_args()

    import ee
    ee.Initialize(project=PROYEK)
    aoi = json.loads(config.BERKAS_AOI.read_text(encoding="utf-8"))
    geom = ee.Geometry(aoi["features"][0]["geometry"])

    tahun_dipakai = argumen.tahun or list(range(2015, 2027))
    print(f"AOI luas   : {geom.area(1).getInfo() / 1e6:.1f} km2")
    print(f"skala      : {SKALA_M} m")
    print(f"tahun      : {tahun_dipakai[0]} sampai {tahun_dipakai[-1]}\n")

    if argumen.darat_saja:
        return uji_darat(ee, geom, tahun_dipakai)

    laporan = {}
    for ambang in AMBANG_AIR_DB:
        print(f"ambang air {ambang:+.0f} dB")
        semua: list[dict] = []
        for tahun in tahun_dipakai:
            baris = proporsi_air(ee, geom, tahun, ambang)
            semua.extend(baris)
            print(f"  {tahun}: {len(baris):>3} citra", flush=True)

        if not semua:
            print("  tidak ada data\n")
            continue

        p = np.array([b["proporsi"] for b in semua])
        t = np.array([
            float(pasut.tinggi_pasut_m(datetime.fromisoformat(b["waktu"])))
            for b in semua
        ])
        gabungan = float(np.corrcoef(p, t)[0, 1])
        per_orbit = korelasi_per_orbit(semua)

        print(f"  luas air rata-rata : {100 * p.mean():.2f} persen AOI")
        print(f"  simpangan bakunya  : {100 * p.std():.2f} persen")
        print(f"  korelasi gabungan  : {gabungan:+.4f}")
        print("  korelasi per orbit:")
        for orbit, d in per_orbit.items():
            print(f"    orbit {orbit:>3} {d['arah'][:4]:<5} "
                  f"{d['citra']:>3} citra  korelasi {d['korelasi']:+.4f}  "
                  f"luas rata {100 * d['proporsi_rata']:.2f} persen")
        print()

        laporan[f"{ambang:+.0f}dB"] = {
            "citra": len(semua),
            "luas_air_rata_persen": round(100 * float(p.mean()), 3),
            "luas_air_simpangan_persen": round(100 * float(p.std()), 3),
            "korelasi_gabungan": round(gabungan, 4),
            "per_orbit": per_orbit,
        }

    # ── PUTUSAN ────────────────────────────────────────────────────────
    terbaik = 0.0
    for d in laporan.values():
        for o in d["per_orbit"].values():
            terbaik = max(terbaik, abs(o["korelasi"]))
    print("=" * 66)
    if terbaik >= 0.35:
        putusan = "ADA ISYARAT"
        kalimat = (
            "Sentinel-1 MELIHAT pasang surut di AOI ini. Berarti kegagalan di "
            "skrip 09 berasal dari cara pencuplikan, bukan dari citranya. "
            "Label genangan bisa dibangun ulang dari luas air kawasan terbuka "
            "lalu dikaitkan ke ruas terdekat, dan jalur model layak dihidupkan.")
    elif terbaik >= 0.2:
        putusan = "ISYARAT LEMAH"
        kalimat = (
            "Ada kaitan tetapi tipis. Membangun model prediksi di atasnya "
            "berisiko, dan hasilnya harus dilaporkan dengan ketidakpastian "
            "yang jujur.")
    else:
        putusan = "TIDAK ADA ISYARAT"
        kalimat = (
            "Sentinel-1 tidak melihat pasang surut di AOI ini, bahkan di "
            "kawasan terbuka sekalipun. Tidak ada penyetelan ambang yang akan "
            "menolong, dan indeks kerentanan adalah pilihan yang benar.")
    print(f"PUTUSAN: {putusan}")
    print(f"korelasi mutlak tertinggi antar orbit: {terbaik:.4f}")
    print(kalimat)

    BERKAS_HASIL.write_text(json.dumps({
        "_catatan": ("Uji apakah Sentinel-1 melihat pasang surut di AOI, "
                     "diukur lewat proporsi luas AOI di bawah ambang air "
                     "terbuka. Dihasilkan oleh "
                     "backend/scripts/12_uji_isyarat_s1.py."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "skala_m": SKALA_M,
        "putusan": putusan,
        "korelasi_mutlak_tertinggi": round(terbaik, 4),
        "kesimpulan": kalimat,
        "per_ambang": laporan,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
