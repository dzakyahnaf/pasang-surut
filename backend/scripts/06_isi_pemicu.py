"""Isi tabel `pemicu`: tinggi pasut dan curah hujan per jam, sekali di muka.

    python -m scripts.06_isi_pemicu                    # 2015 sampai kemarin
    python -m scripts.06_isi_pemicu --mulai 2024-01-01 # rentang tertentu

Tabel `pemicu` adalah pasangan waktu untuk `sampel_latih`. Model genangan
membaca keduanya lewat kolom `waktu`, jadi tabel ini harus mencakup seluruh
periode latih dan uji: latih 2015 sampai 2023, uji 2024 sampai 2026.

KENAPA DIAMBIL SEKARANG DAN DISIMPAN.

Aturan repo nomor 6 melarang panggilan API eksternal saat runtime, dan hujan
adalah godaan terbesar untuk melanggarnya karena API-nya mudah dipanggil.
Skrip ini menariknya sekali, menghitung akumulasinya, lalu menyimpannya.
Setelah ini berjalan, demo tidak lagi memerlukan internet.

KENAPA AKUMULASI, BUKAN HUJAN SESAAT.

Genangan rob tidak ditentukan oleh hujan pada jam itu juga. Tanah yang sudah
jenuh dan saluran yang sudah penuh membuat hujan beberapa hari sebelumnya
lebih menentukan daripada gerimis saat air pasang. Karena itu yang disimpan
adalah jumlah 24 jam dan 72 jam terakhir, sesuai kolom yang sudah disediakan
schema.sql.

BATASAN YANG WAJIB DISEBUT.

Open-Meteo Archive menyajikan reanalisis ERA5, bukan pengamatan stasiun.
Petaknya berukuran puluhan kilometer, sedangkan AOI hanya sekitar 13 kali 8
kilometer. Jadi seluruh AOI berbagi satu deret hujan yang sama. Hujan
konvektif di Semarang kerap sangat setempat, dan perbedaan antara Tanjungmas
yang deras dengan Genuk yang kering tidak akan tertangkap. Dicatat di
docs/batasan.md.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

import numpy as np

from app import config, db
from app.domain import pasut

LAYANAN = "https://archive-api.open-meteo.com/v1/archive"
AGEN = "PasangSurut-ANFORCOM2026/0.1 (riset akademik; dzakyahnf@gmail.com)"

MULAI_BAWAAN = "2015-01-01"      # awal periode latih, sejalan aturan repo 5
SUMBER_HUJAN = "open-meteo-era5"

BERKAS_CADANGAN = config.DIR_DATA_REFERENSI / "hujan_open_meteo.json"


def titik_ambil() -> tuple[float, float]:
    """Titik tengah AOI. Satu titik untuk seluruh AOI, lihat catatan batasan."""
    lon0, lat0, lon1, lat1 = config.bbox_aoi()
    return (lat0 + lat1) / 2.0, (lon0 + lon1) / 2.0


def ambil_hujan(lintang: float, bujur: float,
                mulai: str, selesai: str) -> tuple[list[str], np.ndarray]:
    """Unduh curah hujan per jam. Kembalikan (waktu ISO UTC, mm)."""
    kueri = urllib.parse.urlencode({
        "latitude": f"{lintang:.4f}",
        "longitude": f"{bujur:.4f}",
        "start_date": mulai,
        "end_date": selesai,
        "hourly": "precipitation",
        "timezone": "UTC",
    })
    url = f"{LAYANAN}?{kueri}"
    print(f"  {mulai} .. {selesai}", end="", flush=True)
    permintaan = urllib.request.Request(url, headers={"User-Agent": AGEN})
    try:
        with urllib.request.urlopen(permintaan, timeout=300) as r:
            isi = json.load(r)
    except urllib.error.HTTPError as e:
        badan = e.read().decode("utf-8", "replace")[:300]
        raise SystemExit(f"\nOpen-Meteo menolak: HTTP {e.code}. {badan}")

    jam = isi["hourly"]["time"]
    mm = np.array(
        [0.0 if x is None else float(x) for x in isi["hourly"]["precipitation"]],
        dtype=np.float64,
    )
    print(f"   -> {len(jam):,} jam")
    return jam, mm


def akumulasi(mm: np.ndarray, jendela: int) -> np.ndarray:
    """Jumlah hujan pada `jendela` jam terakhir, termasuk jam berjalan.

    Jam-jam paling awal deret tidak punya riwayat selengkap itu, jadi
    jumlahnya dihitung dari data yang ada saja. Beberapa baris pertama karena
    itu bernilai lebih rendah daripada seharusnya; karena deret dimulai 2015
    dan periode latih juga mulai 2015, pengaruhnya hanya di hari pertama.
    """
    kumulatif = np.concatenate(([0.0], np.cumsum(mm)))
    indeks = np.arange(len(mm)) + 1
    awal = np.maximum(indeks - jendela, 0)
    return kumulatif[indeks] - kumulatif[awal]


def per_potongan(mulai: date, selesai: date, tahun_per_potong: int = 3):
    """Bagi rentang jadi potongan supaya satu permintaan tidak terlalu besar."""
    a = mulai
    while a <= selesai:
        b = min(date(a.year + tahun_per_potong, 1, 1) - timedelta(days=1), selesai)
        yield a, b
        a = b + timedelta(days=1)


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--mulai", default=MULAI_BAWAAN)
    pengurai.add_argument(
        "--selesai", default=None,
        help="bawaan: kemarin, karena ERA5 tertinggal beberapa hari",
    )
    argumen = pengurai.parse_args()

    mulai = date.fromisoformat(argumen.mulai)
    selesai = (date.fromisoformat(argumen.selesai) if argumen.selesai
               else date.today() - timedelta(days=1))
    lintang, bujur = titik_ambil()

    print(f"titik ambil : {lintang:.4f}, {bujur:.4f}  (tengah AOI)")
    print(f"rentang     : {mulai} sampai {selesai}")
    print("sumber      : Open-Meteo Archive, reanalisis ERA5\n")

    print("mengunduh hujan per jam ...")
    waktu_semua: list[str] = []
    mm_semua: list[np.ndarray] = []
    for a, b in per_potongan(mulai, selesai):
        jam, mm_potong = ambil_hujan(lintang, bujur, a.isoformat(), b.isoformat())
        waktu_semua.extend(jam)
        mm_semua.append(mm_potong)
    mm = np.concatenate(mm_semua)
    print(f"total       : {len(waktu_semua):,} jam\n")

    if len(waktu_semua) != len(set(waktu_semua)):
        raise SystemExit("Ada jam ganda di hasil unduhan. Potongan tumpang tindih.")

    h24 = akumulasi(mm, 24)
    h72 = akumulasi(mm, 72)
    tahun = len(mm) / 8766.0
    print("curah hujan")
    print(f"  jam berhujan          : {int((mm > 0).sum()):,} dari {len(mm):,} "
          f"({100.0 * (mm > 0).mean():.1f} persen)")
    print(f"  total                 : {mm.sum():,.0f} mm selama {tahun:.1f} tahun")
    print(f"  rerata tahunan        : {mm.sum() / tahun:,.0f} mm")
    print(f"  hujan sejam maksimum  : {mm.max():.1f} mm")
    print(f"  hujan 24 jam maksimum : {h24.max():.1f} mm")
    print(f"  hujan 72 jam maksimum : {h72.max():.1f} mm\n")

    print("tinggi pasut rekonstruksi harmonik")
    waktu_utc = [
        datetime.strptime(t, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        for t in waktu_semua
    ]
    # Dihitung sekali sebagai deret, bukan seratus ribu panggilan terpisah.
    jam_sejak = np.array(
        [(t - pasut.EPOCH_HARMONIK).total_seconds() / 3600.0 for t in waktu_utc]
    )
    tinggi = pasut.tinggi_pasut_harmonik(
        jam_sejak, offset_jam=pasut.OFFSET_FASE_JAM
    )
    print(f"  sumber  : {pasut.SUMBER}, offset fase {pasut.OFFSET_FASE_JAM:+.1f} jam")
    print(f"  rentang : {tinggi.min():+.3f} sampai {tinggi.max():+.3f} m "
          "terhadap muka air rata-rata\n")

    BERKAS_CADANGAN.write_text(
        json.dumps({
            "_catatan": ("Cadangan mentah curah hujan Open-Meteo, supaya tabel "
                         "pemicu bisa dibangun ulang tanpa internet."),
            "diunduh": datetime.now(timezone.utc).isoformat(),
            "sumber": LAYANAN,
            "model": "ERA5 reanalysis",
            "lintang": round(lintang, 4),
            "bujur": round(bujur, 4),
            "satuan": "mm per jam",
            "mulai": waktu_semua[0],
            "selesai": waktu_semua[-1],
            "jam": len(waktu_semua),
            "hujan_mm": [round(float(x), 2) for x in mm],
        }, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"cadangan mentah tersimpan: {BERKAS_CADANGAN.name}")

    print("menulis ke database ...")
    baris = [
        (w, float(t), float(a), float(b), SUMBER_HUJAN)
        for w, t, a, b in zip(waktu_utc, tinggi, h24, h72)
    ]
    with db.koneksi() as kon:
        n = db.RepositoriPemicu(kon).sisipkan_banyak(baris)
    print(f"  {n:,} baris dikirim")

    with db.koneksi() as kon:
        r = db.RepositoriPemicu(kon).ringkasan()
    print(f"  di tabel  : {r['baris']:,} baris")
    print(f"  periode   : {r['awal']} sampai {r['akhir']}")
    print(f"  pasut     : {r['pasut_min_m']:+.3f} sampai {r['pasut_maks_m']:+.3f} m")
    print(f"  hujan 24j : maksimum {r['hujan_24j_maks_mm']:.1f} mm")
    print(f"  hujan 72j : maksimum {r['hujan_72j_maks_mm']:.1f} mm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
