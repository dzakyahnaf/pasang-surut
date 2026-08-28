"""Uji kriteria dua arah: apakah genangan kota MENAIKKAN backscatter?

    python -m scripts.14_uji_dua_arah

DUGAAN YANG DIUJI.

Skrip 09 memakai kriteria satu arah: ruas disebut basah bila backscatter
TURUN di bawah garis dasarnya. Itu benar untuk air terbuka, yang memantulkan
gelombang radar menjauh dari satelit.

Di kawasan terbangun, fisikanya bisa berlawanan. Air dangkal di antara
bangunan membentuk pemantul sudut: gelombang memantul dari permukaan air ke
dinding lalu kembali lurus ke satelit. Efek pantulan ganda ini MENAIKKAN
backscatter, kadang beberapa desibel.

Kalau itu yang terjadi di Semarang, kriteria penurunan bukan sekadar lemah —
ia melihat ke arah yang salah, dan seluruh label yang dihasilkannya terbalik.

Petunjuk yang memicu uji ini nyata: pada 12 citra yang jatuh di tanggal
kejadian rob terdokumentasi, anomali rata-rata justru POSITIF (+0,148 dB)
secara konsisten di tiga lapisan kerawanan yang berbeda. Besarnya hanya 0,34
simpangan baku sehingga tidak bisa diklaim, tetapi arahnya cukup untuk
menuntut pemeriksaan.

TIGA KRITERIA YANG DIBANDINGKAN.

    turun     anomali < -X        air terbuka menelan gelombang
    naik      anomali > +X        pantulan ganda air dan dinding
    dua arah  |anomali| > X       perubahan permukaan, arah apa pun

Semuanya diuji terhadap dua bukti bebas: tinggi pasut saat akuisisi, dan
tanggal kejadian rob yang terdokumentasi.

Uji ini TIDAK memakai kuota Earth Engine sama sekali. Nilai mentahnya sudah
ditarik sekali oleh skrip 08 dan disimpan, dan itu memang alasan
rancangannya dibuat begitu.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone

import numpy as np

from app import config
from app.domain import pasut

BERKAS_VV = config.DIR_DATA_OLAHAN / "s1_vv_ruas.jsonl"
BERKAS_CITRA = config.DIR_DATA_OLAHAN / "s1_daftar_citra.json"
BERKAS_KEJADIAN = config.DIR_DATA_REFERENSI / "kejadian_rob_semarang.json"
BERKAS_HASIL = config.DIR_DATA_REFERENSI / "uji_dua_arah.json"

AMBANG = (2.0, 2.5, 3.0, 4.0)


def muat():
    citra = json.loads(BERKAS_CITRA.read_text(encoding="utf-8"))["citra"]
    urutan = {c["indeks"]: i for i, c in enumerate(citra)}
    edge, idx, vv = [], [], []
    with BERKAS_VV.open(encoding="utf-8") as f:
        for garis in f:
            b = json.loads(garis)
            i = urutan.get(b["pita"].rsplit("_VV", 1)[0])
            if i is None:
                continue
            edge.append(b["edge_id"])
            idx.append(i)
            vv.append(b["vv_db"])
    return (np.array(edge, np.int64), np.array(idx, np.int32),
            np.array(vv, np.float64), citra)


def anomali_per_orbit(edge, idx, vv, citra) -> np.ndarray:
    orbit = np.array([citra[i]["orbit_relatif"] for i in idx], np.int32)
    kunci = edge * 1000 + orbit
    u = np.argsort(kunci, kind="stable")
    ku, vu = kunci[u], vv[u]
    au = np.empty(len(vu))
    for k in np.split(np.arange(len(ku)), np.flatnonzero(np.diff(ku)) + 1):
        au[k] = vu[k] - np.median(vu[k])
    a = np.empty_like(au)
    a[u] = au
    return a


def hari_kejadian() -> set[date]:
    kej = json.loads(BERKAS_KEJADIAN.read_text(encoding="utf-8"))["kejadian"]
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


def nilai_uji(frak: np.ndarray, pasut_citra: np.ndarray,
              dekat: np.ndarray) -> dict:
    """Korelasi terhadap pasut, dan selisih antara hari kejadian dan lainnya."""
    ok = np.isfinite(frak)
    if ok.sum() < 50 or frak[ok].std() < 1e-12:
        return {"korelasi": float("nan"), "selisih_sigma": float("nan")}
    korelasi = float(np.corrcoef(frak[ok], pasut_citra[ok])[0, 1])
    a, b = frak[ok & dekat], frak[ok & ~dekat]
    if len(a) < 3 or b.std() < 1e-12:
        sigma = float("nan")
    else:
        # Positif berarti label lebih sering muncul saat kejadian rob, yaitu
        # arah yang diharapkan apa pun kriterianya.
        sigma = float((a.mean() - b.mean()) / b.std())
    return {"korelasi": korelasi, "selisih_sigma": sigma,
            "laju_label": float(np.nanmean(frak))}


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    if not BERKAS_VV.exists():
        raise SystemExit(
            f"{BERKAS_VV.name} tidak ada. Jalankan skrip 08 lebih dulu.\n"
            "Berkas itu tidak masuk git karena 219 MB; lihat .gitignore.")

    print("memuat backscatter ...")
    edge, idx, vv, citra = muat()
    print(f"  {len(vv):,} nilai, {len(np.unique(edge)):,} ruas, "
          f"{len(citra):,} citra\n")

    anom = anomali_per_orbit(edge, idx, vv, citra)
    waktu = [datetime.fromisoformat(c["waktu"]).astimezone(timezone.utc)
             for c in citra]
    pasut_citra = np.array([float(pasut.tinggi_pasut_m(w)) for w in waktu])
    hari = hari_kejadian()
    tgl = np.array([w.date() for w in waktu])
    dekat = np.array([any((t + timedelta(days=o)) in hari for o in (-1, 0, 1))
                      for t in tgl])
    print(f"citra pada atau berdekatan tanggal kejadian: {int(dekat.sum())} "
          f"dari {len(citra)}\n")

    # Proporsi ruas berlabel basah per citra, untuk tiap kriteria dan ambang.
    print(f"{'kriteria':<10} {'ambang':>7} {'laju label':>11} "
          f"{'korelasi pasut':>15} {'kejadian (sigma)':>17}")
    print("-" * 66)

    hasil = {}
    for nama, uji in (
        ("turun", lambda a, x: a < -x),
        ("naik", lambda a, x: a > x),
        ("dua arah", lambda a, x: np.abs(a) > x),
    ):
        for x in AMBANG:
            label = uji(anom, x)
            frak = np.full(len(citra), np.nan)
            for i in range(len(citra)):
                m = idx == i
                if m.sum() >= 100:
                    frak[i] = label[m].mean()
            d = nilai_uji(frak, pasut_citra, dekat)
            hasil[f"{nama}_{x:g}"] = {k: (None if not np.isfinite(v) else round(v, 4))
                                      for k, v in d.items()}
            print(f"{nama:<10} {x:>7.1f} {100 * d['laju_label']:>10.2f}% "
                  f"{d['korelasi']:>+15.4f} {d['selisih_sigma']:>+17.2f}")
        print()

    # ── PUTUSAN ────────────────────────────────────────────────────────
    terbaik_k = max(
        (abs(v["korelasi"]) for v in hasil.values() if v["korelasi"] is not None),
        default=0.0)
    terbaik_s = max(
        (v["selisih_sigma"] for v in hasil.values()
         if v["selisih_sigma"] is not None), default=0.0)

    print("=" * 66)
    print(f"korelasi mutlak tertinggi terhadap pasut : {terbaik_k:.4f}")
    print(f"selisih terbesar pada tanggal kejadian   : {terbaik_s:+.2f} sigma")
    print()
    if terbaik_k >= 0.3 or terbaik_s >= 1.0:
        putusan = "ADA KRITERIA YANG MENJANJIKAN"
        kalimat = ("Salah satu kriteria menunjukkan kaitan yang cukup untuk "
                   "ditindaklanjuti. Bangun ulang label memakai kriteria itu, "
                   "lalu latih ulang.")
    else:
        putusan = "TIDAK ADA"
        kalimat = ("Tidak satu pun dari tiga kriteria pada empat ambang "
                   "menunjukkan kaitan dengan pasut maupun dengan tanggal "
                   "kejadian. Dugaan pantulan ganda TIDAK terbukti. Arah "
                   "kriteria bukan penyebab kegagalan.")
    print(f"PUTUSAN: {putusan}")
    print(kalimat)

    BERKAS_HASIL.write_text(json.dumps({
        "_catatan": ("Perbandingan kriteria label satu arah turun, satu arah "
                     "naik, dan dua arah. Tidak memakai kuota Earth Engine; "
                     "seluruhnya dari nilai mentah yang sudah ditarik skrip 08."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "citra": len(citra),
        "citra_pada_kejadian": int(dekat.sum()),
        "putusan": putusan,
        "kesimpulan": kalimat,
        "korelasi_mutlak_tertinggi": round(terbaik_k, 4),
        "selisih_sigma_tertinggi": round(terbaik_s, 4),
        "per_kriteria": hasil,
        "_peringatan": [
            "Hanya 12 citra jatuh pada atau berdekatan tanggal kejadian, jadi "
            "kolom sigma berdasar sampel yang sangat kecil.",
            "Daftar kejadian sebagian besar berstatus perlu_verifikasi.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
