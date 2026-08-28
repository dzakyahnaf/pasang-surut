# Validasi

Angka di berkas ini apa adanya. Kalau sebuah angka belum ada, tertulis
"Belum tersedia" — tidak diisi perkiraan.

---

## 1. Cakupan arsip Sentinel-1

**Dijalankan:** 23 Agustus 2026
**Diverifikasi ulang:** 28 Agustus 2026, dari Code Editor DAN dari Python
lewat `earthengine-api`, memakai proyek `pasang-surut-anforcom`. Kedua belas
angka per tahun, kedua arah orbit, dan totalnya **cocok seluruhnya**. Tabel
di bawah karena itu berstatus terverifikasi dari sumber, bukan dilaporkan.
**Skrip:** `gee/cek_cakupan_s1.js` di code.earthengine.google.com
**Koleksi:** Sentinel-1 GRD, mode IW
**Wilayah:** `data/aoi/aoi_semarang_pilot.geojson`

**Total citra tersedia di atas AOI: 723**

### Sebaran per tahun

| Tahun | Jumlah citra |
|---:|---:|
| 2015 | 26 |
| 2016 | 29 |
| 2017 | 69 |
| 2018 | 90 |
| 2019 | 92 |
| 2020 | 89 |
| 2021 | 76 |
| 2022 | 33 |
| 2023 | 42 |
| 2024 | 53 |
| 2025 | 69 |
| 2026 | 55 |
| **Total** | **723** |

### Sebaran per arah orbit

| Arah orbit | Jumlah citra |
|---|---:|
| Ascending | 442 |
| Descending | 281 |
| **Total** | **723** |

### Bacaan atas angka ini

**Ambang keputusan terpenuhi.** PLAN.md bagian 3 menetapkan lebih dari 150
citra berarti rencana berjalan penuh tanpa pemangkasan fitur model. 723 jauh
di atas ambang itu, jadi rencana 9.A tidak dipakai.

**Lubang arsip yang diperingatkan PLAN.md bagian 8 memang terlihat, dan
besarnya terukur.** Sentinel-1B berhenti beroperasi 23 Desember 2021 dan
Sentinel-1C baru reguler sejak 26 Maret 2025. Jejaknya ada di tabel: 2022
sampai 2024 berada di kisaran 33 sampai 53 citra per tahun, sementara 2018
sampai 2021 di kisaran 76 sampai 92. Tahun 2025 kembali ke 69.

Konsekuensinya untuk split latih/uji berbasis waktu — latih 2015–2023, uji
2024–2026 — jendela uji berisi 177 citra dari 723, atau sekitar 24 persen.
Cukup untuk diuji, tetapi kepadatan sampel di jendela uji lebih rendah
daripada di jendela latih. Ini wajib disebut saat membahas hasil model.

**Yang belum diperiksa dan masih bisa memangkas angka ini:**

- Berapa dari 723 citra yang benar-benar menutup AOI penuh, bukan sekadar
  bersinggungan dengan tepinya
- Berapa yang jatuh pada jam pasut tinggi — nilai sesungguhnya dataset latih
  ada di sebaran tinggi muka air pada detik akuisisi, bukan pada jumlah citra
- Apakah ascending dan descending perlu dimodelkan terpisah; keduanya punya
  geometri sudut pandang berbeda sehingga hamburan baliknya tidak setara

---

## 2. Data elevasi

**DEMNAS tile `1409-22` sudah diunduh dan diverifikasi**, 28 Agustus 2026.
Berkas di `data/raw/DEMNAS_1409-22_v1.0.tif`, 43 MB, tidak masuk git.

| | |
|---|---|
| Ukuran | 3.333 × 3.333 piksel, satu band, float32 |
| Cakupan | bujur 110,2500–110,5000 · lintang −7,0000 sampai −6,7500 |
| Menutupi seluruh AOI | ya |
| Resolusi | 0,00007501 derajat, sekitar 8,35 m |
| Piksel valid di dalam AOI | 1.430.289 dari 1.430.289, 100 persen |

Sebaran elevasi **di dalam AOI**:

| Ukuran | Nilai |
|---|---:|
| Minimum | −1,15 m |
| Persentil ke-1 | −1,14 m |
| Persentil ke-5 | −0,01 m |
| Persentil ke-25 | **0,16 m** |
| Median | **2,60 m** |
| Persentil ke-75 | 4,99 m |
| Persentil ke-95 | 12,34 m |
| Maksimum | 55,95 m |

**Seperempat wilayah pilot berada di bawah 0,16 meter.** Itu alasan fisik
kenapa rob melumpuhkan kawasan ini.

Sekaligus penegasan kenapa ambang elevasi absolut tidak sah: RMSE vertikal
DEMNAS 2,79 m jauh lebih besar daripada sebaran elevasi yang sedang
dibedakan. Selisih antara persentil ke-25 dan median hanya 2,44 m, masih di
bawah ketidakpastian alat ukurnya sendiri.

**Jebakan:** berkas ini tidak membawa CRS. `rasterio` melaporkan
`CRS: None`. CRS harus ditetapkan eksplisit setiap kali dibuka.

---

## 3. Akurasi model genangan

**Belum tersedia.** Model belum dilatih.

Akan diisi setelah `backend/scripts/03_latih_model.py` berjalan. Yang akan
dicatat di sini: metrik pada jendela uji 2024–2026, matriks konfusi,
feature importance, dan perbandingan terhadap baseline naif.

Split berbasis waktu, tidak pernah acak: latih 2015–2023, uji 2024–2026.

---

## 4. Validasi rute

**Belum tersedia.** Mesin routing belum dibangun.

---

## 5. Validasi estimasi dampak

**Belum tersedia.**
