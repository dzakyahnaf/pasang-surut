"""Ubah probabilitas model menjadi estimasi kedalaman genangan.

MODUL INI ADALAH TITIK TERLEMAH SELURUH METODOLOGI, dan PLAN.md bagian 10.3
menyuruh mengakuinya sendiri sebelum juri menemukannya. Berkas ini karena itu
dibuat terpisah, kecil, dan bisa diuji, bukan diselipkan di dalam skrip.

MASALAHNYA.

Model genangan mengeluarkan PROBABILITAS ruas tergenang, bukan kedalaman.
Sentinel-1 tidak pernah mengukur kedalaman: ia hanya menunjukkan permukaan
menjadi lebih halus. Sementara itu antarmuka perlu angka sentimeter, karena
ambang kelayakan tiap moda dinyatakan dalam sentimeter di tabel `ambang_moda`.

Jadi ada jurang antara yang bisa diukur dan yang perlu ditampilkan. Jurang
itu diseberangi dengan ASUMSI, dan asumsi itu ditulis di sini secara terbuka,
bukan disembunyikan di dalam angka ajaib.

ASUMSI YANG DIPAKAI.

1. Rentang kedalaman rob 10 sampai 50 sentimeter. Ini berasal dari aturan
   repo nomor 4, dan dipakai sebagai batas bawah dan batas atas keluaran.
   Sistem TIDAK PERNAH melaporkan kedalaman di luar rentang itu.

2. Kedalaman naik monoton terhadap dua hal: keyakinan model, dan tinggi
   pasut. Keduanya diberi bobot sama, 50 berbanding 50.

   Kenapa keduanya, bukan pasut saja: model bisa menyatakan ruas tergenang
   pada pasut sedang karena hujan, dan memaksa kedalaman mengikuti pasut
   akan menihilkan genangan akibat hujan.

   Kenapa keduanya, bukan probabilitas saja: probabilitas 0,9 pada surut
   terendah tidak sepatutnya menghasilkan angka yang sama dengan
   probabilitas 0,9 pada pasang tertinggi tahun itu.

3. Bobot 50 berbanding 50 itu SENDIRI adalah asumsi. Tidak ada satu pun
   pengukuran kedalaman genangan di repo ini yang bisa dipakai mengalibrasi
   bobotnya. Kalau nanti ada data kedalaman lapangan, di sinilah tempat
   mengoreksinya, dan hanya di sini.

YANG DILARANG DILAKUKAN DENGAN KELUARAN MODUL INI.

Menyebutnya "kedalaman terukur", menampilkannya tanpa kata estimasi, atau
memakainya sebagai dasar keputusan keselamatan jiwa. Aturan repo nomor 3
berlaku penuh di sini.
"""

from __future__ import annotations

import numpy as np

# Rentang rob menurut aturan repo nomor 4. Bukan hasil pengukuran kita.
KEDALAMAN_MIN_CM = 10.0
KEDALAMAN_MAKS_CM = 50.0

# Bobot antara keyakinan model dan tinggi pasut. Asumsi, lihat catatan modul.
BOBOT_PROBABILITAS = 0.5
BOBOT_PASUT = 0.5


def _normalkan(nilai, bawah: float, atas: float):
    """Petakan nilai ke rentang 0 sampai 1, dipotong di kedua ujungnya."""
    if atas <= bawah:
        return np.zeros_like(np.asarray(nilai, dtype=float))
    return np.clip((np.asarray(nilai, dtype=float) - bawah) / (atas - bawah),
                   0.0, 1.0)


def kedalaman_cm(probabilitas, tinggi_pasut_m, ambang_probabilitas: float,
                 pasut_acuan_m: float, pasut_puncak_m: float):
    """Estimasi kedalaman genangan dalam sentimeter.

    Argumen:
        probabilitas        keluaran model, 0 sampai 1
        tinggi_pasut_m      tinggi pasut pada jam yang sama
        ambang_probabilitas ambang tempat ruas mulai disebut tergenang
        pasut_acuan_m       tinggi pasut yang dianggap tidak menambah apa-apa
        pasut_puncak_m      tinggi pasut yang dianggap menyumbang penuh

    Kedua acuan pasut diambil dari sebaran rekonstruksi itu sendiri, bukan
    ditetapkan dengan tangan, supaya tidak ada angka yang tidak bisa
    ditelusuri asalnya.

    Ruas dengan probabilitas di bawah ambang menghasilkan 0, bukan
    KEDALAMAN_MIN_CM. Nol berarti "tidak diprediksi tergenang"; angka 10
    berarti "tergenang, dan ini estimasi paling dangkal yang kami laporkan".
    """
    p = np.asarray(probabilitas, dtype=float)
    s_prob = _normalkan(p, ambang_probabilitas, 1.0)
    s_pasut = _normalkan(tinggi_pasut_m, pasut_acuan_m, pasut_puncak_m)

    s = BOBOT_PROBABILITAS * s_prob + BOBOT_PASUT * s_pasut
    hasil = KEDALAMAN_MIN_CM + (KEDALAMAN_MAKS_CM - KEDALAMAN_MIN_CM) * s
    return np.where(p >= ambang_probabilitas, hasil, 0.0)
