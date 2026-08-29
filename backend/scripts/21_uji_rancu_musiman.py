"""Uji apakah korelasi +0,36 itu nyata atau hanya rancu musiman.

    python -m scripts.21_uji_rancu_musiman

DUGAAN YANG DIUJI, DAN KENAPA IA SERIUS.

Skrip 12 menemukan proporsi daratan yang tampak berair berkorelasi +0,362
terhadap pasut pada orbit 76. Tandanya positif, arah yang benar secara fisika.
Tetapi ada penjelasan tandingan yang harus disingkirkan lebih dulu.

Sentinel-1 sinkron matahari, sehingga melintas pada jam lokal yang hampir
tetap. Pada jam yang tetap itu, komponen pasut K1 (23,93 jam) dan P1 (24,07
jam) bergeser fasenya dengan periode SEKITAR SATU TAHUN — bukan sebulan.
Akibatnya rekonstruksi pasut yang dicuplik pada waktu akuisisi memiliki
siklus tahunan semu.

Kebasahan lahan di Semarang juga bersiklus tahunan, dan siklusnya kuat:
musim hujan November sampai April, kemarau Mei sampai Oktober.

Dua besaran yang sama-sama bersiklus tahunan akan berkorelasi tanpa ada
hubungan sebab sama sekali. Persis seperti korelasi semu -0,29 pada uji muka
air terukur, yang ternyata seluruhnya berasal dari layangan sepuluh tahun.

CARANYA MENGUJI.

Bukan dengan membuang data, melainkan dengan MENGENDALIKAN hari-dalam-tahun.
Untuk kedua deret — proporsi basah dan tinggi pasut — dibuang dulu bagian
yang dapat dijelaskan oleh musim, lalu sisanya dikorelasikan. Yang tersisa
disebut korelasi parsial.

Musim dimodelkan dengan dua harmonik tahunan:

    sin(2 pi d/365,25), cos(2 pi d/365,25)      siklus tahunan
    sin(4 pi d/365,25), cos(4 pi d/365,25)      siklus setengah tahunan

Harmonik kedua ikut dipakai karena musim di Indonesia tidak berbentuk
sinusoid tunggal: ada dua peralihan dalam setahun, bukan satu.

CARA MEMBACA HASILNYA.

    korelasi parsial masih sekitar 0,36   isyaratnya nyata, bukan musiman
    korelasi parsial runtuh ke sekitar 0  seluruhnya rancu musiman
    di antaranya                          sebagian nyata, sebagian musiman

Uji ini TIDAK memakai kuota Earth Engine. Deret per-citra sudah disimpan.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import numpy as np

from app import config
from app.domain import pasut

BERKAS = config.DIR_DATA_REFERENSI / "uji_isyarat_s1_darat.json"
BERKAS_HASIL = config.DIR_DATA_REFERENSI / "uji_rancu_musiman.json"


def rancangan_musim(waktu: list[datetime]) -> np.ndarray:
    """Matriks rancangan: konstanta + dua harmonik tahunan."""
    hari = np.array([w.timetuple().tm_yday for w in waktu], dtype=float)
    sudut = 2.0 * np.pi * hari / 365.25
    return np.column_stack([
        np.ones(len(hari)),
        np.sin(sudut), np.cos(sudut),
        np.sin(2 * sudut), np.cos(2 * sudut),
    ])


def sisa_setelah_musim(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Buang bagian y yang dapat dijelaskan musim; kembalikan sisanya."""
    koef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ koef


def r2_musim(y: np.ndarray, X: np.ndarray) -> float:
    """Berapa besar ragam y yang dijelaskan musim saja."""
    sisa = sisa_setelah_musim(y, X)
    total = np.var(y)
    return float(1.0 - np.var(sisa) / total) if total > 0 else 0.0


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    if not BERKAS.exists():
        raise SystemExit(f"{BERKAS.name} belum ada. Jalankan skrip 12 dulu.")
    d = json.loads(BERKAS.read_text(encoding="utf-8"))
    deret = d.get("deret_per_citra")
    if not deret:
        raise SystemExit(
            "Deret per-citra tidak ada di berkas hasil. Jalankan ulang\n"
            "`python -m scripts.12_uji_isyarat_s1 --darat-saja` dengan versi\n"
            "skrip yang sudah menyimpan deret.")

    print(f"{'kombinasi':<22}{'n':>5}{'mentah':>10}{'parsial':>10}"
          f"{'musim jelaskan':>16}")
    print("-" * 64)

    hasil = {}
    for nama, baris in deret.items():
        if len(baris) < 40:
            continue
        waktu = [datetime.fromisoformat(b["waktu"]).astimezone(timezone.utc)
                 for b in baris]
        p = np.array([b["proporsi"] for b in baris], dtype=float)
        t = np.array([float(pasut.tinggi_pasut_m(w)) for w in waktu])
        if p.std() < 1e-12 or t.std() < 1e-12:
            continue

        mentah = float(np.corrcoef(p, t)[0, 1])
        X = rancangan_musim(waktu)
        p_sisa = sisa_setelah_musim(p, X)
        t_sisa = sisa_setelah_musim(t, X)
        parsial = (float(np.corrcoef(p_sisa, t_sisa)[0, 1])
                   if p_sisa.std() > 1e-12 and t_sisa.std() > 1e-12 else 0.0)
        # Seberapa besar musim menjelaskan masing-masing deret.
        r2_p, r2_t = r2_musim(p, X), r2_musim(t, X)

        hasil[nama] = {
            "citra": len(baris),
            "korelasi_mentah": round(mentah, 4),
            "korelasi_parsial": round(parsial, 4),
            "musim_jelaskan_proporsi_basah": round(r2_p, 4),
            "musim_jelaskan_pasut": round(r2_t, 4),
            "susut": round(abs(mentah) - abs(parsial), 4),
        }
        print(f"{nama:<22}{len(baris):>5}{mentah:>+10.4f}{parsial:>+10.4f}"
              f"{100 * r2_p:>13.1f}% basah")
        print(f"{'':<22}{'':>5}{'':>10}{'':>10}{100 * r2_t:>13.1f}% pasut")

    if not hasil:
        raise SystemExit("Tidak ada deret yang cukup panjang untuk diuji.")

    terbaik_mentah = max(abs(v["korelasi_mentah"]) for v in hasil.values())
    terbaik_parsial = max(abs(v["korelasi_parsial"]) for v in hasil.values())
    susut = terbaik_mentah - terbaik_parsial

    print()
    print("=" * 64)
    print(f"korelasi mutlak tertinggi MENTAH  : {terbaik_mentah:.4f}")
    print(f"korelasi mutlak tertinggi PARSIAL : {terbaik_parsial:.4f}")
    print(f"susut karena musim                : {susut:.4f} "
          f"({100 * susut / max(terbaik_mentah, 1e-9):.0f} persen)")
    print()

    if terbaik_parsial >= 0.25:
        putusan = "ISYARAT NYATA"
        kalimat = ("Korelasi bertahan setelah musim dikendalikan. Rancu "
                   "musiman BUKAN penjelasannya, dan isyarat ini layak "
                   "ditindaklanjuti.")
    elif terbaik_parsial >= 0.15:
        putusan = "SEBAGIAN NYATA"
        kalimat = ("Sebagian korelasi bertahan setelah musim dikendalikan, "
                   "sebagian lagi memang musiman. Arah lanjutan yang layak, "
                   "belum cukup untuk melatih model.")
    else:
        putusan = "RANCU MUSIMAN"
        kalimat = ("Korelasi runtuh setelah musim dikendalikan. Yang terlihat "
                   "sebagai kaitan dengan pasut sesungguhnya kaitan dengan "
                   "musim hujan, dan penolakan model tetap berdiri.")
    print(f"PUTUSAN: {putusan}")
    print(kalimat)

    BERKAS_HASIL.write_text(json.dumps({
        "_catatan": ("Uji rancu musiman atas korelasi luas air terhadap pasut. "
                     "Musim dimodelkan dua harmonik tahunan; yang dilaporkan "
                     "korelasi parsial setelah musim dikendalikan pada KEDUA "
                     "deret."),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "cara": "regresi hari-dalam-tahun, dua harmonik, lalu korelasi sisa",
        "korelasi_mutlak_mentah": round(terbaik_mentah, 4),
        "korelasi_mutlak_parsial": round(terbaik_parsial, 4),
        "susut_karena_musim": round(susut, 4),
        "putusan": putusan,
        "kesimpulan": kalimat,
        "per_kombinasi": hasil,
        "_peringatan": [
            "Regresi musiman hanya menyingkirkan rancu yang BERBENTUK siklus "
            "tahunan. Rancu lain yang tidak berpola tahunan tidak tersentuh.",
            "Kalau musim menjelaskan sebagian besar ragam kedua deret, sisa "
            "yang dikorelasikan menjadi kecil dan korelasi parsialnya lebih "
            "berderau daripada korelasi mentahnya.",
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
