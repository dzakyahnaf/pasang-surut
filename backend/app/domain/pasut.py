"""Pasang surut — rekonstruksi harmonik.

Tinggi muka air dihitung sebagai jumlah komponen harmonik M2, S2, N2, K2,
K1, O1, dan P1, dengan amplitudo dan fase dari
data/referensi/konstanta_pasut_semarang.json. Sepenuhnya luring; tidak ada
panggilan jaringan saat aplikasi berjalan.

ACUAN WAKTU FASE SUDAH DIPASTIKAN, 28 Agustus 2026.

Sumber konstanta tidak menyatakan zona waktu acuan fasenya. Pertanyaan itu
diselesaikan secara empiris oleh scripts/04_kalibrasi_pasut.py: rekonstruksi
disisir pada seluruh offset dari -12 sampai +12 jam, lalu dibandingkan
dengan muka air terukur di stasiun pasut IOC 'sema' milik Badan Informasi
Geospasial, yang berjarak sekitar 120 meter dari stasiun tempat konstanta
itu diukur.

Hasilnya tegas dan stabil pada jendela 2, 4, 7, dan 10 hari:

    acuan UTC  : korelasi -0,29 sampai -0,46   <- BERKEBALIKAN
    acuan WIB  : korelasi +0,78 sampai +0,91

Memakai UTC bukan sekadar kurang tepat, melainkan membalik pasang menjadi
surut. Acuan yang benar adalah WAKTU LOKAL WIB.

Fungsi sinusoid data contoh yang lama sudah dibuang. Riwayatnya ada di git.
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache

import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# ACUAN WAKTU FASE
# ══════════════════════════════════════════════════════════════════════════
# Fase konstanta mengacu waktu lokal WIB, yaitu UTC+7. Dibuktikan lewat
# kalibrasi terhadap data terukur; lihat kepala modul dan
# data/referensi/kalibrasi_pasut.json.
#
# KENAPA DIPAKAI +7,0 DAN BUKAN ANGKA HASIL PENCOCOKAN TERBAIK.
# Pencocokan terbaik jatuh di sekitar +7,9 jam, bukan tepat +7,0. Selisih
# sekitar 0,9 jam itu punya penjelasan fisik: rekonstruksi ini belum
# menerapkan koreksi nodal siklus 18,6 tahun, sementara konstantanya diukur
# 2014 dan dipakai untuk 2026. Sumbernya pun hanya rekaman 15 hari.
#
# Memakai +7,9 memang menurunkan RMSE sekitar 1,4 sentimeter, tetapi angka
# itu hasil pencocokan terhadap sepuluh hari data pada satu musim saja dan
# sulit dipertanggungjawabkan di depan penguji. Yang dipakai adalah nilai
# yang berdasar, yaitu +7,0, dan sisa galatnya dilaporkan apa adanya di
# docs/validasi.md. Begitu tim menghitung konstanta sendiri dari rekaman
# setahun stasiun 'sema', pertanyaan ini hilang seluruhnya.
OFFSET_FASE_JAM = 7.0

SUMBER = "harmonik_v1"


def jam_sejak_epoch(waktu: datetime) -> float:
    """Berapa jam sejak titik acuan fase. Waktu tanpa zona dianggap UTC."""
    return _jam_sejak(waktu, EPOCH_HARMONIK)


def tinggi_pasut_m(waktu):
    """Tinggi muka air dalam meter, relatif terhadap muka air rata-rata.

    Inilah fungsi yang dipakai seluruh sistem. Menerima satu datetime, atau
    larik jam sejak EPOCH_HARMONIK untuk perhitungan borongan.
    """
    return tinggi_pasut_harmonik(waktu, offset_jam=OFFSET_FASE_JAM)


def deret_pasut(mulai: datetime, jumlah_jam: int, langkah_jam: int = 1) -> list[dict]:
    """Deret tinggi pasut per jam, siap dikirim ke frontend.

    Dipakai Pita Pasut untuk menggambar kurvanya. Bentuk kembaliannya
    sengaja sederhana supaya tidak berubah saat isi modul ini diganti
    rekonstruksi harmonik yang sebenarnya di M4.
    """
    from datetime import timedelta

    hasil = []
    for i in range(0, jumlah_jam, langkah_jam):
        waktu = mulai + timedelta(hours=i)
        hasil.append({
            "waktu_utc": waktu.isoformat(),
            "tinggi_m": round(float(tinggi_pasut_m(waktu)), 4),
        })
    return hasil


# ══════════════════════════════════════════════════════════════════════════
# REKONSTRUKSI HARMONIK — pasut yang sebenarnya
# ══════════════════════════════════════════════════════════════════════════
# Kecepatan sudut tiap komponen dalam DERAJAT PER JAM. Angka-angka ini
# konstanta astronomi baku, sama di seluruh dunia, dan tidak ada kaitannya
# dengan lokasi. Yang bersifat lokal hanya amplitudo dan fase, dan itu
# dibaca dari data/referensi/konstanta_pasut_semarang.json.
KECEPATAN_SUDUT = {
    "M2": 28.9841042,   # bulan utama, ganda
    "S2": 30.0000000,   # matahari utama, ganda
    "N2": 28.4397295,   # bulan eliptik besar, ganda
    "K2": 30.0821373,   # deklinasi bulan-matahari, ganda
    "K1": 15.0410686,   # deklinasi bulan-matahari, tunggal
    "O1": 13.9430356,   # bulan utama, tunggal
    "P1": 14.9589314,   # matahari utama, tunggal
    "M4": 57.9682084,   # perairan dangkal, seperempat harian
    "MS4": 58.9841042,  # perairan dangkal gabungan
}

# Komponen yang dipakai rekonstruksi, sesuai PLAN.md bagian 10.2.
KOMPONEN_DIPAKAI = ("M2", "S2", "N2", "K2", "K1", "O1", "P1")

# Titik acuan fase. Rekonstruksi menghitung t sebagai jam sejak saat ini.
EPOCH_HARMONIK = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)


@lru_cache(maxsize=1)
def muat_konstanta() -> dict:
    """Baca konstanta harmonik dari data/referensi/."""
    import json

    from app import config

    berkas = config.DIR_DATA_REFERENSI / "konstanta_pasut_semarang.json"
    with berkas.open(encoding="utf-8") as f:
        return json.load(f)


def tinggi_pasut_harmonik(waktu, offset_jam: float = 0.0,
                          komponen=KOMPONEN_DIPAKAI):
    """Tinggi muka air dari penjumlahan komponen harmonik, dalam meter.

    h(t) = SUM A_i * cos(sigma_i * t - g_i)

    dengan t dalam jam sejak EPOCH_HARMONIK, sigma dalam derajat per jam,
    dan g fase lokal tiap komponen.

    KENAPA ADA PARAMETER offset_jam. Sumber konstanta tidak menyatakan zona
    waktu acuan fasenya. Selisih tujuh jam antara UTC dan WIB cukup untuk
    membalik pasang menjadi surut pada komponen M2 yang periodenya 12,4 jam.
    Parameter ini dipakai skrip kalibrasi untuk menyisir seluruh kemungkinan
    offset dan menemukan mana yang benar-benar cocok dengan data terukur.

    Nilai S0 sengaja TIDAK ditambahkan. S0 adalah muka air rata-rata terhadap
    nol palem pasut di stasiun tahun 2014, dan datum itu tidak sama dengan
    datum alat ukur mana pun yang dipakai sekarang. Yang bermakna lintas
    datum hanya simpangan terhadap rata-rata, bukan nilai mutlaknya.
    """
    k = muat_konstanta()["konstituen"]

    if isinstance(waktu, datetime):
        jam = _jam_sejak(waktu, EPOCH_HARMONIK) + offset_jam
    else:
        jam = np.asarray(waktu, dtype=float) + offset_jam

    total = np.zeros_like(np.asarray(jam, dtype=float))
    for nama in komponen:
        c = k.get(nama)
        if not c or c.get("amplitudo") is None or c.get("fase") is None:
            continue
        amplitudo_m = c["amplitudo"] / 100.0          # cm menjadi meter
        sudut = np.deg2rad(KECEPATAN_SUDUT[nama] * jam - c["fase"])
        total = total + amplitudo_m * np.cos(sudut)
    return total


def _jam_sejak(waktu: datetime, epoch: datetime) -> float:
    if waktu.tzinfo is None:
        waktu = waktu.replace(tzinfo=timezone.utc)
    return (waktu.astimezone(timezone.utc) - epoch).total_seconds() / 3600.0
