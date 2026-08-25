"""Pasang surut.

╔══════════════════════════════════════════════════════════════════════════╗
║  ISI MODUL INI MASIH DATA CONTOH.                                        ║
║                                                                          ║
║  Yang ada di sini hanya SATU sinusoid berperiode 24,8 jam. Itu bukan     ║
║  rekonstruksi pasut, hanya bentuk naik-turun supaya Pita Pasut punya     ║
║  sesuatu untuk digambar dan supaya mesin routing punya pemicu yang       ║
║  berubah tiap jam.                                                       ║
║                                                                          ║
║  Pasut SUNGGUHAN adalah jumlah banyak komponen harmonik — M2, S2, N2,    ║
║  K2, K1, O1, P1 — dengan amplitudo dan fase dari                         ║
║  data/referensi/konstanta_pasut_semarang.json. Berkas itu SUDAH TERISI   ║
║  sejak 24 Agustus 2026, tetapi belum bisa dipakai karena zona waktu      ║
║  acuan fasenya belum dipastikan. Selama itu belum selesai, memakainya    ║
║  berisiko menggeser seluruh kurva sampai tujuh jam.                      ║
║                                                                          ║
║  Rincian dan cara menyelesaikannya ada di berkas konstanta itu sendiri   ║
║  dan di docs/batasan.md bagian 1.4.                                      ║
╚══════════════════════════════════════════════════════════════════════════╝

Modul ini sengaja dibuat supaya rumus pasut contoh hanya hidup di SATU
tempat. Sebelumnya ia tertulis di dalam scripts/03_isi_dummy.py, sehingga
Pita Pasut di frontend tidak punya cara membaca kurva yang sama dengan yang
dipakai saat data contoh dibuat. Kalau keduanya berbeda, kurva di layar
tidak akan cocok dengan genangan yang digambar di peta.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

# Periode 24,8 jam adalah panjang satu hari bulan, yaitu ritme dasar pasang
# surut harian. Dipilih karena sederhana dan bisa dijelaskan, bukan karena
# hasil analisis.
PERIODE_PASUT_JAM = 24.8

# Setengah amplitudo dalam meter. Rentangnya jadi sekitar -0,5 sampai +0,5 m.
# Sebagai pembanding, BMKG mencatat pasang tertinggi 0,95 m pada peringatan
# rob 18 Mei 2026 di Semarang, jadi besaran ini berada di kisaran yang masuk
# akal walau bukan hasil perhitungan.
AMPLITUDO_PASUT_M = 0.5

# Titik acuan fase. Dipatok pada waktu tetap, bukan waktu jalan, supaya
# kurva yang dihasilkan sama persis setiap kali dihitung.
EPOCH_PASUT = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)

SUMBER = "dummy"


def jam_sejak_epoch(waktu: datetime) -> float:
    """Berapa jam sejak titik acuan fase. Waktu tanpa zona dianggap UTC."""
    if waktu.tzinfo is None:
        waktu = waktu.replace(tzinfo=timezone.utc)
    return (waktu.astimezone(timezone.utc) - EPOCH_PASUT).total_seconds() / 3600.0


def tinggi_pasut_m(waktu):
    """Tinggi muka air contoh dalam meter, relatif terhadap rata-rata.

    Menerima satu datetime, atau larik jam sejak epoch untuk perhitungan
    borongan.

    SEKALI LAGI: ini bukan rekonstruksi harmonik.
    """
    if isinstance(waktu, datetime):
        jam = jam_sejak_epoch(waktu)
    else:
        jam = waktu
    return AMPLITUDO_PASUT_M * np.sin(2 * np.pi * jam / PERIODE_PASUT_JAM)


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
