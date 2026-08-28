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

## 3. Rekonstruksi pasut

Dua uji dijalankan, keduanya terhadap bukti di luar konstanta itu sendiri.

### 3.1 Acuan waktu fase — diselesaikan 28 Agustus 2026

Rachman dkk (2015) tidak menyatakan zona waktu acuan fase konstantanya.
Taruhannya besar: selisih tujuh jam setara 203 derajat pada M2 yang
periodenya 12,42 jam, lebih dari setengah siklus. Salah acuan berarti pasang
tertukar surut, dan fitur pasut yang jadi masukan terpenting model akan
salah tanda.

Alih-alih menguji dua tebakan, seluruh offset −12 sampai +12 jam disisir
dengan langkah 0,25 jam, lalu dibandingkan terhadap muka air terukur stasiun
pasut IOC `sema` milik BIG, sekitar 120 m dari stasiun sumber konstanta.
Skrip: `backend/scripts/04_kalibrasi_pasut.py`.

Waktu pada layanan IOC lebih dulu dibuktikan UTC secara empiris: rekaman
terbaru hanya berselang menit dari waktu UTC berjalan, sedangkan bila dibaca
sebagai waktu lokal ia akan tertinggal tujuh jam padahal stasiunnya melapor
hampir seketika.

| Jendela | Offset terbaik | Korelasi terbaik | Fase = UTC (0 j) | Fase = WIB (+7 j) |
|---|---:|---:|---:|---:|
| 2 hari | +7,50 j | +0,914 | **−0,289** | +0,907 |
| 4 hari | +7,75 j | +0,933 | **−0,362** | +0,909 |
| 7 hari | +8,25 j | +0,925 | **−0,427** | +0,858 |
| 10 hari | +8,00 j | +0,847 | **−0,465** | +0,782 |

**Memakai UTC bukan sekadar kurang tepat, melainkan berkebalikan.**
Korelasinya negatif di seluruh jendela uji. Acuan yang benar adalah WIB.
RMSE pada WIB 0,097–0,116 m terhadap rentang terukur 0,920 m.

Sistem memakai **+7,0 jam**, bukan +7,9 jam yang merupakan pencocokan
terbaik. Alasannya: +7,0 adalah nilai berdasar, +7,9 adalah hasil pencocokan
terhadap sepuluh hari data. Sisa selisih ~0,9 jam diperkirakan berasal dari
koreksi nodal siklus 18,6 tahun yang belum diterapkan, ditambah rekaman
sumber yang hanya 15 hari.

### 3.2 Uji silang terhadap kejadian rob terdokumentasi

Bukti yang sama sekali terpisah: 21 entri kejadian rob dari pemberitaan dan
dokumen resmi. Yang tanggalnya pasti sampai hari menghasilkan 37 hari dari
16 kejadian di dalam 2020–2026. Untuk tiap hari diambil pasut maksimum
(cuplikan 15 menit), lalu dicari persentilnya di antara 2.431 hari pada
periode yang sama. Skrip: `backend/scripts/07_uji_silang_rob.py`.

Persentil dipakai supaya hasilnya tidak bergantung pada datum, dan supaya
pembandingnya hari rob melawan hari biasa, bukan melawan ambang yang kita
tentukan sendiri.

| Ukuran | Median persentil | ≥ p75 | ≥ p90 |
|---|---:|---:|---:|
| Per hari (37 hari) | 71,5 | 16 (43%) | 7 (19%) |
| Per kejadian (16 kejadian) | 80,2 | 9 (56%) | 5 (31%) |

Bila tanggal kejadian tidak berhubungan dengan pasut, medianya akan mendekati
50. **Putusan yang dicatat adalah "sedang", diambil dari ukuran per hari yang
angkanya lebih rendah.** Ukuran per kejadian diperkenalkan setelah ukuran per
hari dihitung, jadi memakainya sebagai dasar putusan akan terlihat seperti
memilih ukuran yang hasilnya paling enak.

**Enam dari 16 kejadian justru terjadi pada pasut yang tidak tinggi**
(persentil di bawah 60), dan hujan 24 jam pada hari-hari itu juga sedang saja
(2,5–20,4 mm):

| Kejadian | Persentil pasut | Hujan 24 jam |
|---|---:|---:|
| 2020-12-10 | 47,5 | 7,3 mm |
| 2022-12-19 | 23,5 | 11,8 mm |
| 2024-04-07 | 37,1 | 3,9 mm |
| 2024-11-18 | 53,8 | 20,4 mm |
| 2026-05-04 | 11,9 | 9,2 mm |
| 2026-05-18 | 29,2 | 2,5 mm |

Ini temuan yang berguna, bukan kegagalan. Ia menunjukkan pasut saja tidak
menjelaskan rob, dan dua pemicu yang kita punya pun belum menjelaskan
seluruhnya. Angin, penurunan tanah, kondisi tanggul, dan kapasitas pompa
ikut menentukan. **Itulah alasan sistem ini memakai model, bukan ambang.**

Perlu jujur juga: `2026-05-18` berstatus verifikasi `primer` — kejadian yang
sumbernya paling kuat — dan persentil pasutnya hanya 29,2.

### 3.3 Yang belum diuji

- Koreksi nodal 18,6 tahun belum diterapkan sama sekali
- Sumber lain (Az Zahro dkk, 29 piantan data Pushidrosal 2018) memperoleh
  Formzahl 3,94, yaitu tipe harian tunggal, bukan campuran seperti sumber
  utama. Rekamannya lebih panjang. Perbedaan ini belum diselesaikan
- Konstanta belum dihitung ulang dari rekaman IOC multi-tahun

---

## 4. Fitur ruas jalan

Diisi 28 Agustus 2026 oleh `backend/scripts/05_isi_fitur_ruas.py`, atas
**19.394 ruas** di dalam AOI.

| Fitur | Terisi | Minimum | Median | Maksimum |
|---|---:|---:|---:|---:|
| Elevasi DEMNAS | 19.368 (99,87%) | −0,13 m | 4,07 m | 57,31 m |
| Jarak ke garis pantai | 19.394 (100%) | 7 m | 3.565 m | 7.909 m |
| Laju subsidensi | 18.404 (94,9%) | 2,1 cm/th | — | 5,8 cm/th |

Catatan tiap fitur:

- **Elevasi** dicuplik di titik tengah ruas. 26 ruas jatuh di piksel tanpa
  data dan tetap `NULL`, bukan nol — nol adalah elevasi yang sah di pesisir,
  jadi memakainya sebagai penanda "tidak ada data" akan mencemari fitur.
  Median 4,07 m di sini lebih tinggi daripada median 2,60 m untuk seluruh
  piksel AOI di bagian 2. Dugaan penjelasannya jalan cenderung dibangun dan
  ditinggikan di atas lahan sekitarnya, tetapi itu belum diuji dan sebaiknya
  tidak disajikan sebagai temuan.
- **Jarak pantai** dihitung di EPSG:32749, bukan di derajat. Garis pantai
  dari OpenStreetMap `natural=coastline`, 21 garis, diunduh sekali ke
  `data/processed/garis_pantai.geojson`.
- **Laju subsidensi** hanya tersedia per kecamatan, dipetakan lewat batas
  kecamatan OSM ke `data/processed/kecamatan.geojson`. 990 ruas berada di
  kecamatan yang tidak dilaporkan sumbernya dan tetap `NULL`. Delapan
  poligon kecamatan diperiksa tidak saling tumpang tindih dan sentroidnya
  jatuh di posisi yang benar. Luasnya belum dibandingkan terhadap angka resmi
  BPS; itu pemeriksaan yang masih terbuka.

---

## 5. Variabel pemicu

Diisi 28 Agustus 2026 oleh `backend/scripts/06_isi_pemicu.py`.
**102.168 baris jam**, 2015-01-01 sampai 2026-08-27, mencakup seluruh
periode latih (2015–2023) dan uji (2024–2026).

| | |
|---|---|
| Sumber hujan | Open-Meteo Archive, reanalisis ERA5 |
| Titik ambil | −6,9600 / 110,4425, tengah AOI |
| Jam berhujan | 28.375 dari 102.168 (27,8 persen) |
| Rerata tahunan | 1.830 mm |
| Hujan sejam maksimum | 42,9 mm |
| Hujan 24 jam maksimum | 181,6 mm |
| Hujan 72 jam maksimum | 204,5 mm |
| Rentang pasut rekonstruksi | −0,571 sampai +0,445 m terhadap muka air rata-rata |

**Belum diverifikasi:** rerata tahunan 1.830 mm belum dibandingkan terhadap
normal BMKG stasiun Semarang. Reanalisis diketahui cenderung meratakan hujan
konvektif setempat, jadi angka ini patut diperiksa sebelum dikutip. Dicatat
sebagai pekerjaan terbuka, bukan sebagai angka yang sudah sahih.

---

## 6. Akurasi model genangan

**Belum tersedia.** Model belum dilatih.

Akan diisi setelah skrip pelatihan berjalan. Yang akan dicatat di sini:
metrik pada jendela uji 2024–2026, matriks konfusi, feature importance, dan
perbandingan terhadap baseline naif.

Split berbasis waktu, tidak pernah acak: latih 2015–2023, uji 2024–2026.

---

## 7. Validasi rute

**Sebagian.** Mesin routing sudah dibangun di M3
(`backend/app/domain/routing.py`) dan diuji lewat `pytest` untuk perilaku
algoritmanya: biaya dihitung pada waktu TIBA bukan waktu berangkat, ruas
dengan kedalaman di atas ambang moda dibuang dari graf, dan dua rute
dikembalikan untuk tiap permintaan.

**Yang belum ada** adalah validasi terhadap dunia nyata: apakah rute yang
disarankan memang bisa dilalui saat rob. Itu memerlukan data genangan asli,
bukan data contoh, sehingga bergantung pada bagian 6.

---

## 8. Validasi estimasi dampak

**Belum tersedia.** Menunggu faktor emisi yang masih `null` di
`data/referensi/faktor_emisi.json`.
