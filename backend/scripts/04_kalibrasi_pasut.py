"""Tentukan acuan waktu fase konstanta pasut dengan membandingkannya ke data terukur.

    python -m scripts.04_kalibrasi_pasut          # dijalankan dari backend/

MASALAH YANG DISELESAIKAN SKRIP INI.

Konstanta harmonik di data/referensi/konstanta_pasut_semarang.json diambil
dari Rachman dkk (2015). Sumber itu TIDAK menyatakan zona waktu acuan
fasenya. Metode Admiralty di Indonesia lazim mengacu waktu lokal, tetapi
"lazim" bukan bukti.

Taruhannya besar. Selisih tujuh jam antara UTC dan WIB setara 203 derajat
pada komponen M2 yang periodenya 12,42 jam — lebih dari setengah siklus.
Salah menebak berarti pasang tertukar surut, dan fitur "tinggi pasut saat
akuisisi" yang menjadi masukan terpenting model genangan akan salah tanda.

CARA MENYELESAIKANNYA.

Tidak menguji dua tebakan, melainkan menyisir SELURUH offset dari -12 sampai
+12 jam, lalu mencari mana yang paling cocok dengan muka air yang benar-benar
terukur di stasiun pasut IOC berkode 'sema' — stasiun milik Badan Informasi
Geospasial yang berjarak sekitar 120 meter dari stasiun tempat konstanta itu
diukur.

Menyisir lebih baik daripada menguji dua tebakan karena hasilnya menunjukkan
sendiri apakah ada puncak kecocokan yang tegas. Kalau tidak ada puncak yang
menonjol, itu justru pertanda konstantanya yang bermasalah, bukan offsetnya.

CATATAN DATUM. Alat ukur IOC dan palem pasut 2014 memakai titik nol yang
berbeda, jadi nilai mutlaknya tidak bisa dibandingkan. Yang dibandingkan
adalah SIMPANGAN terhadap rata-rata masing-masing.

CATATAN KOREKSI NODAL. Rekonstruksi ini tidak menerapkan faktor nodal (f, u)
yang berubah mengikuti siklus 18,6 tahun. Konstanta berasal dari 2014 dan
dipakai untuk 2026, sehingga ada galat amplitudo dan fase yang tidak
dikoreksi. Untuk menentukan offset sebesar jam-jaman, galat itu terlalu
kecil untuk mengubah kesimpulan, tetapi wajib disebut saat melaporkan
ketelitian rekonstruksi.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

import numpy as np

from app import config
from app.domain import pasut

STASIUN = "sema"
SENSOR = "prs"          # sensor tekanan, deret paling rapat di stasiun ini
HARI = 7
LAYANAN = "https://www.ioc-sealevelmonitoring.org/service.php"

# Sopan santun terhadap layanan publik: sebutkan siapa yang memanggil.
AGEN = "PasangSurut-ANFORCOM2026/0.1 (riset akademik; dzakyahnf@gmail.com)"

BERKAS_HASIL = config.DIR_DATA_REFERENSI / "kalibrasi_pasut.json"


def ambil_data_terukur(hari: int = HARI) -> tuple[np.ndarray, np.ndarray]:
    """Unduh muka air terukur dari stasiun IOC. Kembalikan (jam_utc, meter).

    Waktu pada layanan IOC adalah UTC. Itu diperiksa secara empiris: rekaman
    paling baru hanya berselang beberapa menit dari waktu UTC berjalan,
    sedangkan bila dibaca sebagai waktu lokal ia akan tertinggal tujuh jam
    padahal stasiunnya melapor hampir seketika.
    """
    selesai = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    mulai = selesai - timedelta(days=hari)
    url = (
        f"{LAYANAN}?query=data&code={STASIUN}"
        f"&timestart={mulai:%Y-%m-%dT%H:%M:%S}"
        f"&timestop={selesai:%Y-%m-%dT%H:%M:%S}&format=json"
    )
    print(f"mengunduh {hari} hari data stasiun IOC '{STASIUN}' ...")
    permintaan = urllib.request.Request(url, headers={"User-Agent": AGEN})
    with urllib.request.urlopen(permintaan, timeout=180) as r:
        isi = json.load(r)

    baris = [x for x in isi if x.get("sensor") == SENSOR]
    if not baris:
        raise SystemExit(f"Sensor '{SENSOR}' tidak ada pada balasan layanan.")

    jam, tinggi = [], []
    for x in baris:
        t = datetime.strptime(x["stime"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        jam.append((t - pasut.EPOCH_HARMONIK).total_seconds() / 3600.0)
        tinggi.append(float(x["slevel"]))

    j = np.array(jam, dtype=float)
    m = np.array(tinggi, dtype=float)
    urut = np.argsort(j)
    return j[urut], m[urut]


def buang_rerata(x: np.ndarray) -> np.ndarray:
    """Datum alat ukur berbeda, jadi yang dibandingkan hanya simpangannya."""
    return x - np.mean(x)


def sisir_offset(jam: np.ndarray, terukur: np.ndarray,
                 langkah_jam: float = 0.25) -> list[dict]:
    """Hitung kecocokan rekonstruksi terhadap data terukur untuk tiap offset."""
    y = buang_rerata(terukur)
    hasil = []
    for offset in np.arange(-12.0, 12.0 + 1e-9, langkah_jam):
        model = buang_rerata(pasut.tinggi_pasut_harmonik(jam, offset_jam=float(offset)))
        korelasi = float(np.corrcoef(model, y)[0, 1])
        rmse = float(np.sqrt(np.mean((model - y) ** 2)))
        hasil.append({"offset_jam": round(float(offset), 2),
                      "korelasi": korelasi, "rmse_m": rmse})
    return hasil


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--hari", type=int, default=HARI)
    argumen = pengurai.parse_args()

    jam, terukur = ambil_data_terukur(argumen.hari)
    print(f"rekaman terpakai : {len(jam):,}")
    print(f"rentang terukur  : {np.ptp(terukur):.3f} m")
    print(f"panjang deret    : {(jam[-1] - jam[0]) / 24:.2f} hari")
    print()

    sisiran = sisir_offset(jam, terukur)
    terbaik = max(sisiran, key=lambda x: x["korelasi"])
    terburuk = min(sisiran, key=lambda x: x["korelasi"])

    print("offset terbaik menurut korelasi:")
    print(f"  offset   : {terbaik['offset_jam']:+.2f} jam")
    print(f"  korelasi : {terbaik['korelasi']:+.4f}")
    print(f"  RMSE     : {terbaik['rmse_m']:.4f} m")
    print()
    print(f"offset terburuk  : {terburuk['offset_jam']:+.2f} jam, "
          f"korelasi {terburuk['korelasi']:+.4f}")
    print()

    # Dua hipotesis yang menjadi pertanyaan semula.
    def pada(offset):
        return min(sisiran, key=lambda x: abs(x["offset_jam"] - offset))

    utc = pada(0.0)
    wib = pada(7.0)
    print("dua hipotesis yang dipertanyakan:")
    print(f"  fase mengacu UTC (offset  0 jam): korelasi {utc['korelasi']:+.4f}, "
          f"RMSE {utc['rmse_m']:.4f} m")
    print(f"  fase mengacu WIB (offset +7 jam): korelasi {wib['korelasi']:+.4f}, "
          f"RMSE {wib['rmse_m']:.4f} m")
    print()

    if utc["korelasi"] >= wib["korelasi"]:
        menang, kalah, nama = utc, wib, "UTC"
    else:
        menang, kalah, nama = wib, utc, "WIB"
    selisih = menang["korelasi"] - kalah["korelasi"]
    print(f"PEMENANG: acuan {nama}, unggul {selisih:+.4f} pada korelasi.")

    tegas = terbaik["korelasi"] >= 0.7 and selisih >= 0.2
    print(f"Puncak kecocokan tegas: {tegas}")
    if not tegas:
        print("  Korelasi rendah atau selisih tipis. Itu berarti konstantanya")
        print("  sendiri yang lemah, bukan sekadar offsetnya yang salah.")

    hasil = {
        "_catatan": (
            "Hasil kalibrasi acuan waktu fase konstanta pasut terhadap data "
            "terukur stasiun IOC 'sema'. Dihasilkan oleh "
            "backend/scripts/04_kalibrasi_pasut.py."
        ),
        "dijalankan": datetime.now(timezone.utc).isoformat(),
        "stasiun": STASIUN,
        "sensor": SENSOR,
        "sumber_data": f"{LAYANAN}?query=data&code={STASIUN}",
        "waktu_layanan": "UTC, diperiksa empiris",
        "rekaman": int(len(jam)),
        "panjang_hari": round(float((jam[-1] - jam[0]) / 24), 2),
        "rentang_terukur_m": round(float(np.ptp(terukur)), 3),
        "komponen_dipakai": list(pasut.KOMPONEN_DIPAKAI),
        "offset_terbaik_jam": terbaik["offset_jam"],
        "korelasi_terbaik": round(terbaik["korelasi"], 4),
        "rmse_terbaik_m": round(terbaik["rmse_m"], 4),
        "hipotesis_utc": {"korelasi": round(utc["korelasi"], 4),
                          "rmse_m": round(utc["rmse_m"], 4)},
        "hipotesis_wib": {"korelasi": round(wib["korelasi"], 4),
                          "rmse_m": round(wib["rmse_m"], 4)},
        "acuan_terpilih": nama,
        "selisih_korelasi": round(selisih, 4),
        "kesimpulan_tegas": bool(tegas),
        "_peringatan": [
            "Koreksi nodal 18,6 tahun TIDAK diterapkan. Konstanta 2014 "
            "dipakai untuk 2026.",
            "Konstanta berasal dari rekaman 15 hari; P1 dan K2 diturunkan "
            "dari K1 dan S2, bukan diukur.",
            "Datum alat ukur IOC berbeda dari palem pasut 2014, sehingga "
            "yang dibandingkan hanya simpangan terhadap rata-rata.",
        ],
    }
    BERKAS_HASIL.write_text(
        json.dumps(hasil, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\ntersimpan: {BERKAS_HASIL.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
