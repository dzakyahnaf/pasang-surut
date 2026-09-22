"""Indeks kerentanan rob per ruas — jalur cadangan PLAN.md bagian 9.A.

KENAPA MODUL INI ADA, PADAHAL SUDAH ADA MODEL.

Model genangan berbasis Sentinel-1 SUDAH dilatih dan hasilnya DITOLAK sendiri
oleh tim ini. Alasannya tercatat lengkap di docs/validasi.md: label basah yang
dibuat dari penurunan backscatter VV tidak berkorelasi sama sekali dengan
tinggi pasut, dan pada tanggal kejadian rob terdokumentasi tandanya justru
terbalik. Menyajikan model itu sebagai prediksi genangan akan menjadi
overclaim, dan aturan repo nomor 1 melarangnya.

PLAN.md bagian 9.A menyiapkan jalur ini persis untuk keadaan tersebut:

    "Ganti pendekatan jadi model susceptibility berbasis aturan ... skor
    kerentanan per ruas dari elevasi relatif, jarak ke pantai, dan laju
    subsidensi ... Turunkan klaim dari prediksi jadi indeks kerentanan, dan
    katakan terus terang di proposal."

APA YANG DIKLAIM DAN TIDAK DIKLAIM INDEKS INI.

Diklaim: ruas berindeks tinggi lebih rentan tergenang rob daripada ruas
berindeks rendah, menurut tiga besaran fisik yang sumbernya bisa ditelusuri.

TIDAK diklaim: bahwa ruas tertentu AKAN tergenang, sedalam sekian sentimeter,
pada jam sekian. Indeks ini tidak punya akurasi yang bisa dilaporkan karena
tidak ada satu pun pengamatan genangan per ruas untuk mengujinya.

KENAPA BOBOTNYA SAMA RATA.

Karena tidak ada dasar untuk membuatnya tidak sama. Membobot dengan angka
hasil "penyetelan" tanpa data uji hanyalah menyembunyikan tebakan di balik
desimal. Sepertiga untuk masing-masing adalah tebakan juga, tetapi tebakan
yang jujur dan mudah diperiksa orang lain.

KENAPA ELEVASI RELATIF, BUKAN ELEVASI MUTLAK.

Aturan repo nomor 4: DEMNAS punya RMSE vertikal 2,79 m sementara rob yang
dimodelkan 10 sampai 50 cm. Elevasi mutlak karena itu terlalu kasar untuk
membedakan ruas satu dengan tetangganya.

Galat DEM sebagian besar BERKORELASI SPASIAL: bila satu petak terangkat
sekian meter, tetangganya ikut terangkat kira-kira sama. Dengan mengurangkan
nilai tengah tetangga dalam radius beberapa ratus meter, sebagian besar galat
sistematis itu saling meniadakan, dan yang tersisa adalah beda tinggi SETEMPAT
antar ruas — yang justru menentukan ke mana air mengalir.

Ini tetap BUKAN ambang elevasi absolut. Tidak ada satu baris pun di sini yang
berbunyi "kalau elevasi kurang dari muka air maka tergenang".
"""

from __future__ import annotations

import numpy as np

# Bobot ketiga komponen. Sama rata, dan itu keputusan sadar; lihat catatan
# modul. Kalau nanti ada data genangan per ruas, di sinilah tempat
# mengoreksinya, dan hanya di sini.
BOBOT = {
    "elevasi_relatif": 1.0 / 3.0,
    "jarak_pantai": 1.0 / 3.0,
    "subsidensi": 1.0 / 3.0,
}

# Persentil pemotong. Dipakai supaya satu ruas ekstrem tidak menentukan skala
# seluruh kota, dan supaya indeksnya tetap tersebar di seluruh rentang 0..1.
PERSENTIL_BAWAH = 5.0
PERSENTIL_ATAS = 95.0


def _skala_terbalik(nilai: np.ndarray) -> np.ndarray:
    """Petakan ke 0..1 dengan MAKIN KECIL nilainya MAKIN TINGGI skornya.

    Dipakai untuk elevasi dan jarak pantai: makin rendah dan makin dekat laut,
    makin rentan. NaN menghasilkan NaN, tidak diam-diam dijadikan nol.
    """
    sah = np.isfinite(nilai)
    if not sah.any():
        return np.full_like(nilai, np.nan, dtype=float)
    bawah = np.percentile(nilai[sah], PERSENTIL_BAWAH)
    atas = np.percentile(nilai[sah], PERSENTIL_ATAS)
    if atas <= bawah:
        return np.where(sah, 0.5, np.nan)
    skor = (atas - nilai) / (atas - bawah)
    return np.where(sah, np.clip(skor, 0.0, 1.0), np.nan)


def _skala_searah(nilai: np.ndarray) -> np.ndarray:
    """Petakan ke 0..1 dengan MAKIN BESAR nilainya MAKIN TINGGI skornya.

    Dipakai untuk laju subsidensi: makin cepat tanah turun, makin rentan.
    """
    sah = np.isfinite(nilai)
    if not sah.any():
        return np.full_like(nilai, np.nan, dtype=float)
    bawah = np.percentile(nilai[sah], PERSENTIL_BAWAH)
    atas = np.percentile(nilai[sah], PERSENTIL_ATAS)
    if atas <= bawah:
        return np.where(sah, 0.5, np.nan)
    return np.where(sah, np.clip((nilai - bawah) / (atas - bawah), 0.0, 1.0),
                    np.nan)


def elevasi_relatif(elevasi: np.ndarray, x_m: np.ndarray, y_m: np.ndarray,
                    radius_m: float = 500.0) -> np.ndarray:
    """Elevasi tiap ruas dikurangi median pada kumpulan sel 3 x 3.

    Koordinat WAJIB dalam meter, bukan derajat. Dihitung lewat petak dengan
    sisi sepanjang radius, bukan dengan membandingkan tiap ruas terhadap
    seluruh ruas lain, karena yang terakhir berarti 19.394 kuadrat perbandingan.

    Nama parameter radius_m dipertahankan untuk kompatibilitas: nilainya
    adalah sisi sel, bukan radius pencarian melingkar. Satu ruas memakai
    selnya sendiri dan delapan sel tetangga (jendela 1.500 x 1.500 m bila
    sisi sel 500 m). Tidak ada penyaringan jarak Euclidean 500 m.
    """
    petak_x = np.floor(x_m / radius_m).astype(np.int64)
    petak_y = np.floor(y_m / radius_m).astype(np.int64)

    isi: dict[tuple[int, int], list[int]] = {}
    for i, (a, b) in enumerate(zip(petak_x, petak_y)):
        isi.setdefault((int(a), int(b)), []).append(i)

    hasil = np.full(len(elevasi), np.nan)
    for (a, b), anggota in isi.items():
        tetangga: list[int] = []
        for da in (-1, 0, 1):
            for dbb in (-1, 0, 1):
                tetangga.extend(isi.get((a + da, b + dbb), ()))
        nilai = elevasi[tetangga]
        nilai = nilai[np.isfinite(nilai)]
        if nilai.size == 0:
            continue
        acuan = float(np.median(nilai))
        for i in anggota:
            hasil[i] = elevasi[i] - acuan
    return hasil


def indeks(elevasi_rel: np.ndarray, jarak_pantai: np.ndarray,
           subsidensi: np.ndarray) -> tuple[np.ndarray, dict]:
    """Gabungkan tiga komponen menjadi indeks kerentanan 0 sampai 1.

    Komponen yang NaN diabaikan dan bobotnya dibagi ulang ke komponen yang
    ada, sehingga ruas tanpa data subsidensi tetap mendapat indeks dari dua
    komponen sisanya. Itu lebih jujur daripada mengisi NaN dengan nol, yang
    akan menyatakan "tidak ada subsidensi" padahal yang benar "tidak tahu".
    """
    komponen = {
        "elevasi_relatif": _skala_terbalik(np.asarray(elevasi_rel, dtype=float)),
        "jarak_pantai": _skala_terbalik(np.asarray(jarak_pantai, dtype=float)),
        "subsidensi": _skala_searah(np.asarray(subsidensi, dtype=float)),
    }
    n = len(next(iter(komponen.values())))
    jumlah = np.zeros(n)
    bobot_terpakai = np.zeros(n)
    for nama, nilai in komponen.items():
        sah = np.isfinite(nilai)
        jumlah[sah] += BOBOT[nama] * nilai[sah]
        bobot_terpakai[sah] += BOBOT[nama]

    hasil = np.where(bobot_terpakai > 0, jumlah / np.maximum(bobot_terpakai, 1e-9),
                     np.nan)
    return hasil, komponen
