"""Tarik muka air TERUKUR pada tiap waktu akuisisi Sentinel-1, lalu uji ulang.

    python -m scripts.16_muka_air_terukur          # tarik lalu uji
    python -m scripts.16_muka_air_terukur --uji    # uji saja, dari cache

CELAH YANG DITUTUP SKRIP INI.

Seluruh pengujian sebelumnya membandingkan label Sentinel-1 terhadap
rekonstruksi harmonik, dan rekonstruksi itu hanya memuat komponen ASTRONOMIS.
Rob sesungguhnya terjadi saat pasang astronomis bertemu kenaikan muka air
akibat angin, tekanan udara, dan gelombang badai — dan tidak satu pun dari itu
ada di dalam rekonstruksi kami.

Artinya ada dua kemungkinan yang belum terpisah:

    A. Label Sentinel-1 memang tidak menangkap genangan.
    B. Label menangkapnya, tetapi PEMBANDINGNYA yang kurang lengkap.

Stasiun pasut IOC 'sema' milik BIG mengukur muka air yang sesungguhnya,
lengkap dengan komponen non-astronomisnya, dan rekamannya tersedia sampai
2015. Skrip ini mengambil bacaan terdekat dengan tiap waktu akuisisi lalu
mengulang uji korelasi memakai angka terukur itu.

KALAU KORELASINYA MELONJAK, kemungkinan B yang benar dan model layak
dihidupkan kembali dengan muka air terukur sebagai fitur.

KALAU TETAP DATAR, kemungkinan A yang benar dan pembahasan ditutup.

CATATAN PENTING TENTANG APA YANG BISA DIKLAIM SETELAHNYA.

Sekalipun hasilnya positif, muka air terukur TIDAK bisa dipakai untuk
memprediksi 72 jam ke depan — mengukur bukan meramal, dan kami tidak punya
prakiraan gelombang badai. Nilainya ada pada pembuktian bahwa label Sentinel-1
bermakna, bukan pada pemakaiannya sebagai fitur operasional.

CATATAN DATUM. Alat ukur IOC memakai titik nol sendiri yang berbeda dari nol
palem 2014. Yang dibandingkan karena itu hanya SIMPANGAN terhadap rata-rata,
sama seperti di skrip 04.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import numpy as np

from app import config
from app.domain import pasut

STASIUN = "sema"
# SATU SENSOR SAJA, TIDAK PERNAH JATUH KE SENSOR LAIN.
#
# Versi pertama mencoba prs, lalu rad, lalu pr2 bila yang sebelumnya kosong.
# Itu keliru dan merusak seluruh uji: ketiga sensor punya titik nol sendiri,
# sehingga deret yang tersusun dari campuran ketiganya memuat lompatan datum
# yang tidak ada hubungannya dengan air. Buktinya terukur — korelasi antara
# pasut astronomis dan deret campuran itu hanya +0,24, padahal skrip 04
# memperoleh 0,78 sampai 0,91 pada rekaman satu sensor yang bersih.
#
# Citra yang sensornya tidak merekam sekarang dibiarkan kosong. Kehilangan
# sebagian citra jauh lebih baik daripada deret yang datumnya bergeser
# diam-diam di tengah jalan.
SENSOR = "prs"
LAYANAN = "https://www.ioc-sealevelmonitoring.org/service.php"
AGEN = "PasangSurut-ANFORCOM2026/0.1 (riset akademik; dzakyahnf@gmail.com)"

JENDELA_MENIT = 60
JEDA_DETIK = 0.4                       # sopan terhadap layanan publik

BERKAS_CITRA = config.DIR_DATA_OLAHAN / "s1_daftar_citra.json"
BERKAS_CACHE = config.DIR_DATA_REFERENSI / "muka_air_terukur_akuisisi.json"
BERKAS_VV = config.DIR_DATA_OLAHAN / "s1_vv_ruas.jsonl"
BERKAS_HASIL = config.DIR_DATA_REFERENSI / "uji_muka_air_terukur.json"


def ambil_satu(waktu: datetime) -> float | None:
    """Bacaan muka air terdekat dengan `waktu`, dalam meter. None bila kosong."""
    a = waktu - timedelta(minutes=JENDELA_MENIT)
    b = waktu + timedelta(minutes=JENDELA_MENIT)
    url = (f"{LAYANAN}?query=data&code={STASIUN}"
           f"&timestart={a:%Y-%m-%dT%H:%M:%S}"
           f"&timestop={b:%Y-%m-%dT%H:%M:%S}&format=json")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": AGEN})
        with urllib.request.urlopen(req, timeout=60) as r:
            isi = json.load(r)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    if not isinstance(isi, list):
        return None

    calon = []
    for x in isi:
        if x.get("sensor") != SENSOR:
            continue
        try:
            t = datetime.strptime(x["stime"], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc)
            calon.append((abs((t - waktu).total_seconds()), float(x["slevel"])))
        except (KeyError, ValueError, TypeError):
            continue
    return min(calon)[1] if calon else None


def tarik(citra: list[dict]) -> dict[str, float]:
    cache: dict[str, float] = {}
    if BERKAS_CACHE.exists():
        cache = json.loads(BERKAS_CACHE.read_text(encoding="utf-8"))["nilai"]
        print(f"  cache berisi {len(cache):,} dari {len(citra):,}")

    gagal = 0
    for i, c in enumerate(citra):
        if c["indeks"] in cache:
            continue
        w = datetime.fromisoformat(c["waktu"]).astimezone(timezone.utc)
        nilai = ambil_satu(w)
        if nilai is None:
            gagal += 1
        else:
            cache[c["indeks"]] = nilai
        time.sleep(JEDA_DETIK)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1:>4}/{len(citra)}  terisi {len(cache):,}  "
                  f"kosong {gagal}", flush=True)
            BERKAS_CACHE.write_text(json.dumps({
                "_catatan": ("Muka air terukur stasiun IOC 'sema' pada waktu "
                             "akuisisi Sentinel-1. Datum alat ukur, bukan nol "
                             "palem 2014."),
                "stasiun": STASIUN, "sensor": SENSOR,
                "jendela_menit": JENDELA_MENIT, "nilai": cache,
            }, ensure_ascii=False), encoding="utf-8")

    BERKAS_CACHE.write_text(json.dumps({
        "_catatan": ("Muka air terukur stasiun IOC 'sema' pada waktu akuisisi "
                     "Sentinel-1. Datum alat ukur, bukan nol palem 2014."),
        "stasiun": STASIUN, "sensor": SENSOR,
        "jendela_menit": JENDELA_MENIT, "nilai": cache,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"  selesai: {len(cache):,} terisi, {len(citra) - len(cache):,} kosong")
    return cache


def uji(citra: list[dict], cache: dict[str, float]) -> int:
    """Ulangi uji korelasi memakai muka air TERUKUR sebagai pembanding."""
    if not BERKAS_VV.exists():
        raise SystemExit(f"{BERKAS_VV.name} tidak ada. Jalankan skrip 08.")

    urutan = {c["indeks"]: i for i, c in enumerate(citra)}
    edge, idx, vv = [], [], []
    with BERKAS_VV.open(encoding="utf-8") as f:
        for garis in f:
            b = json.loads(garis)
            i = urutan.get(b["pita"].rsplit("_VV", 1)[0])
            if i is None:
                continue
            edge.append(b["edge_id"]); idx.append(i); vv.append(b["vv_db"])
    edge = np.array(edge, np.int64); idx = np.array(idx, np.int32)
    vv = np.array(vv, np.float64)

    orbit = np.array([citra[i]["orbit_relatif"] for i in idx], np.int32)
    kunci = edge * 1000 + orbit
    u = np.argsort(kunci, kind="stable")
    ku, vu = kunci[u], vv[u]
    au = np.empty(len(vu))
    for k in np.split(np.arange(len(ku)), np.flatnonzero(np.diff(ku)) + 1):
        au[k] = vu[k] - np.median(vu[k])
    anom = np.empty_like(au); anom[u] = au

    waktu = [datetime.fromisoformat(c["waktu"]).astimezone(timezone.utc)
             for c in citra]
    astro = np.array([float(pasut.tinggi_pasut_m(w)) for w in waktu])
    terukur = np.array([cache.get(c["indeks"], np.nan) for c in citra])
    ada = np.isfinite(terukur)

    # ── PENYARINGAN PENCILAN, DAN KENAPA WAJIB ─────────────────────────
    #
    # Tarikan pertama menghasilkan rentang -9,437 sampai +1,807 meter.
    # Pasut Semarang rentangnya sekitar satu meter, jadi angka sebelas meter
    # itu mustahil secara fisik. Penyebabnya khas rekaman pasut jangka
    # panjang: alat diganti, datum digeser, atau sensor melonjak sesaat.
    #
    # Pemeriksaan silang yang membuktikannya: korelasi antara pasut
    # astronomis dan bacaan mentah hanya +0,081, padahal skrip 04 sudah
    # menunjukkan 0,78 sampai 0,91 pada rekaman sepuluh hari yang bersih.
    # Kalau bacaan itu benar, korelasinya tidak mungkin runtuh sedemikian.
    #
    # Disaring dengan MAD, bukan simpangan baku, karena simpangan baku
    # sendiri sudah dirusak oleh pencilan yang hendak dibuang.
    nilai = terukur[ada]
    tengah = float(np.median(nilai))
    mad = float(np.median(np.abs(nilai - tengah)))
    batas = max(6.0 * 1.4826 * mad, 1.5)      # minimal 1,5 m, longgar
    waras = ada & (np.abs(terukur - tengah) <= batas)
    dibuang = int(ada.sum() - waras.sum())
    print(f"penyaringan pencilan: nilai tengah {tengah:+.3f} m, "
          f"batas +/- {batas:.3f} m")
    print(f"  dibuang {dibuang} bacaan mustahil dari {int(ada.sum())}")
    ada = waras
    print(f"\ncitra dengan bacaan terukur: {int(ada.sum())} dari {len(citra)}")
    if ada.sum() < 100:
        raise SystemExit("Terlalu sedikit bacaan terukur untuk diuji.")

    # Simpangan terhadap rata-rata; datum alat ukur bukan nol palem.
    terukur_rel = terukur - np.nanmean(terukur[ada])
    print(f"rentang terukur : {np.nanmin(terukur_rel[ada]):+.3f} sampai "
          f"{np.nanmax(terukur_rel[ada]):+.3f} m")
    print(f"rentang astronomis: {astro[ada].min():+.3f} sampai "
          f"{astro[ada].max():+.3f} m")
    k_astro_terukur = float(np.corrcoef(astro[ada], terukur_rel[ada])[0, 1])
    print(f"korelasi astronomis vs terukur: {k_astro_terukur:+.4f}")
    print("  (di bawah 1 berarti ada komponen non-astronomis yang nyata)\n")

    print(f"{'kriteria':<10} {'ambang':>7} {'vs astronomis':>14} "
          f"{'vs TERUKUR':>12}")
    print("-" * 48)
    hasil = {}
    for nama, fn in (("turun", lambda a, x: a < -x),
                     ("naik", lambda a, x: a > x)):
        for x in (2.0, 3.0, 4.0):
            label = fn(anom, x)
            frak = np.full(len(citra), np.nan)
            for i in range(len(citra)):
                m = idx == i
                if m.sum() >= 100:
                    frak[i] = label[m].mean()
            ok = np.isfinite(frak) & ada
            if ok.sum() < 100:
                continue
            k_a = float(np.corrcoef(frak[ok], astro[ok])[0, 1])
            k_t = float(np.corrcoef(frak[ok], terukur_rel[ok])[0, 1])
            hasil[f"{nama}_{x:g}"] = {"vs_astronomis": round(k_a, 4),
                                      "vs_terukur": round(k_t, 4)}
            print(f"{nama:<10} {x:>7.1f} {k_a:>+14.4f} {k_t:>+12.4f}")
        print()

    terbaik = max((abs(v["vs_terukur"]) for v in hasil.values()), default=0.0)
    print("=" * 48)
    print(f"korelasi mutlak tertinggi terhadap muka air TERUKUR: {terbaik:.4f}")
    if terbaik >= 0.3:
        putusan = "LABEL BERMAKNA"
        kalimat = ("Label Sentinel-1 berkorelasi dengan muka air yang "
                   "sebenarnya. Kegagalan sebelumnya berasal dari pembanding "
                   "astronomis yang tidak lengkap, bukan dari labelnya. Model "
                   "layak dihidupkan kembali.")
    elif terbaik >= 0.15:
        putusan = "LEMAH TAPI ADA"
        kalimat = ("Ada kaitan tipis dengan muka air terukur yang tidak "
                   "terlihat pada pasut astronomis. Layak disebut di proposal "
                   "sebagai arah lanjutan, belum cukup untuk melatih model.")
    else:
        putusan = "TETAP DATAR"
        kalimat = ("Memakai muka air yang sebenarnya pun tidak memunculkan "
                   "kaitan. Pembanding bukan penyebabnya, dan pembahasan "
                   "label Sentinel-1 untuk AOI ini ditutup.")
    print(f"PUTUSAN: {putusan}")
    print(kalimat)

    BERKAS_HASIL.write_text(json.dumps({
        "_catatan": ("Uji ulang label Sentinel-1 memakai muka air TERUKUR "
                     "stasiun IOC 'sema', bukan rekonstruksi astronomis."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "citra_dengan_bacaan": int(ada.sum()),
        "citra_total": len(citra),
        "korelasi_astronomis_vs_terukur": round(k_astro_terukur, 4),
        "putusan": putusan,
        "kesimpulan": kalimat,
        "korelasi_mutlak_tertinggi": round(terbaik, 4),
        "per_kriteria": hasil,
        "_peringatan": [
            "Muka air TERUKUR tidak bisa dipakai memprediksi 72 jam ke depan. "
            "Mengukur bukan meramal, dan kami tidak punya prakiraan gelombang "
            "badai.",
            "Datum alat ukur IOC berbeda dari nol palem 2014, jadi yang "
            "dibandingkan hanya simpangan terhadap rata-rata.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--uji", action="store_true", help="lewati penarikan")
    a = p.parse_args()

    citra = json.loads(BERKAS_CITRA.read_text(encoding="utf-8"))["citra"]
    print(f"citra: {len(citra):,}")
    if a.uji:
        if not BERKAS_CACHE.exists():
            raise SystemExit("Cache belum ada. Jalankan tanpa --uji dulu.")
        cache = json.loads(BERKAS_CACHE.read_text(encoding="utf-8"))["nilai"]
    else:
        print("menarik muka air terukur stasiun IOC ...")
        cache = tarik(citra)
    return uji(citra, cache)


if __name__ == "__main__":
    sys.exit(main())
