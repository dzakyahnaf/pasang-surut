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

## 6. Model genangan Sentinel-1 — DILATIH, LALU DITOLAK

Bagian ini melaporkan hasil negatif. Modelnya ada, angkanya ada, dan
kesimpulannya adalah **model itu tidak dipakai**. Ini keputusan sadar, bukan
pekerjaan yang belum selesai.

### 6.1 Apa yang dikerjakan

Seluruh arsip ditarik, bukan sebagian: **725 citra Sentinel-1 GRD IW VV**,
2015 sampai 2026, dicuplik pada **2.502 ruas berstrata** menurut elevasi dan
jarak pantai — **1.813.950 nilai backscatter**. Skala 30 m, dengan median
fokal 30 m sebagai peredam speckle.

Label basah dibuat dengan **deteksi perubahan**, bukan ambang mutlak. Ambang
mutlak dikesampingkan setelah datanya sendiri menunjukkan sebabnya: pada
jalan di dalam kota, nilai VV terendah hanya sekitar −13 dB, sedangkan ambang
air terbuka yang lazim −15 sampai −18 dB. Ambang mutlak akan menyatakan
seluruh kota kering sepanjang masa.

Garis dasar dihitung per pasangan **(ruas, orbit relatif)** — dipisah per
orbit karena backscatter bergantung geometri sudut pandang, dan mencampur
ascending dengan descending memunculkan "perubahan" yang sebenarnya hanya
beda arah lihat satelit.

Pada ambang −3 dB, 33.858 dari 1.813.950 sampel berlabel basah (1,87 persen).

### 6.2 Angka model

`HistGradientBoostingClassifier`, pemisahan **berdasarkan waktu**: latih
2015–2023 (1.366.092 baris), uji 2024–2026 (447.858 baris).

| Metrik | Nilai |
|---|---:|
| ROC-AUC | 0,6579 |
| PR-AUC | 0,0371 (proporsi dasar 0,0160) |
| F1 | 0,0894 pada ambang 0,665 |

Matriks konfusi pada data uji: TN 422.350 · FP 18.352 · FN 5.962 · TP 1.194.

### 6.3 Kenapa angka itu ditolak

**Label basahnya tidak berhubungan dengan pasut sama sekali.** Ini terdeteksi
oleh pemeriksaan kewarasan yang sengaja dipasang sebelum pelatihan, bukan
ditemukan belakangan:

| Pemeriksaan | Hasil | Yang diharapkan |
|---|---:|---|
| Pasut rata-rata saat label basah | +0,092 m | jelas lebih tinggi |
| Pasut rata-rata saat label kering | +0,095 m | — |
| **Selisih** | **−0,003 m** | positif dan jelas |
| ROC-AUC aturan "pasut saja" | 0,4935 | jauh di atas 0,5 |

Diagnosis dilanjutkan pada agregat **per citra**, yang meratakan speckle atas
2.502 titik sekaligus:

| Uji | Korelasi terhadap pasut saat akuisisi |
|---|---:|
| Rata-rata anomali, seluruh sampel | +0,040 |
| Idem, ruas < 1.000 m dari pantai | +0,054 |
| Idem, ruas < 500 m dari pantai | +0,072 |

Dan terhadap kejadian rob terdokumentasi — 12 citra jatuh pada atau
berdekatan dengan tanggal kejadian:

| Kelompok ruas | Saat kejadian | Di luar kejadian | Selisih |
|---|---:|---:|---:|
| Seluruh sampel | +0,217 dB | +0,070 dB | **+0,148 dB** |
| < 1.000 m dari pantai | +0,186 dB | +0,074 dB | +0,112 dB |
| < 500 m dari pantai | +0,213 dB | +0,054 dB | +0,159 dB |

**Tandanya terbalik.** Genangan seharusnya MENURUNKAN backscatter, tetapi
pada tanggal kejadian nilainya justru sedikit lebih tinggi — dan besarnya
hanya 0,34 sampai 0,46 simpangan baku antar citra, jadi ini tidak signifikan
ke arah mana pun.

Yang tersisa: ROC-AUC 0,658 itu hampir seluruhnya berasal dari fitur STATIS.
Kepentingan permutasi memperlihatkannya terang-terangan:

| Fitur | Penurunan ROC-AUC saat diacak |
|---|---:|
| Jarak ke pantai | +0,1417 ± 0,0039 |
| Elevasi DEMNAS | +0,0619 ± 0,0016 |
| Laju subsidensi | +0,0342 ± 0,0014 |
| **Tinggi pasut saat akuisisi** | **+0,0010 ± 0,0014** |
| **Hujan 24 jam** | **+0,0004 ± 0,0010** |
| **Hujan 72 jam** | **−0,0026 ± 0,0011** |

Ketiga fitur waktu tidak menyumbang apa pun — dua di antaranya di dalam
simpangan bakunya sendiri, satu bahkan negatif. Model ini mempelajari **ruas
mana yang sering beranomali**, bukan **kapan ruas tergenang**. Untuk sistem
perutean yang seluruh gunanya terletak pada kata "kapan", itu tidak berguna.

Model tetap mengalahkan ketiga pembanding naif (pasut saja 0,4935, elevasi
saja 0,5503, jarak pantai saja 0,6096), tetapi mengalahkan pembanding naif
pada tugas yang salah bukan alasan untuk memakainya.

### 6.4 Kemungkinan sebabnya

Tiga dugaan, tidak satu pun sudah dibuktikan:

1. **Pantulan ganda di kawasan terbangun.** Air dangkal di antara bangunan
   memantul dua kali antara permukaan air dan dinding, dan itu MENAIKKAN
   backscatter. Kriteria penurunan buta terhadap genangan semacam itu. Tanda
   positif yang konsisten pada tanggal kejadian di 6.3 sejalan dengan dugaan
   ini, tetapi 0,34 simpangan baku terlalu lemah untuk diklaim.
2. **Waktu lintas satelit.** Akuisisi hanya terjadi pada 10.57–10.58 dan
   22.16–22.17 UTC, yaitu 17.58 dan 05.16 WIB. Pasut saat akuisisi tetap
   bervariasi penuh (−0,249 sampai +0,435 m, simpangan baku 0,147 m)
   sehingga ini bukan pencuplikan yang beraliasi — tetapi puncak rob yang
   berlangsung beberapa jam bisa saja terlewat.
3. **Jalan terlalu sempit terhadap piksel 30 m.** Satu piksel di atas jalan
   ikut memuat trotoar, kendaraan, pohon, dan bangunan.

### 6.5 Lima upaya penyelamatan, semuanya gagal

Model tidak ditinggalkan setelah satu kegagalan. Lima dugaan penyebab diuji
satu per satu, dan kelimanya terbantah. Yang kelima sempat menjanjikan dan
karena itu diuji paling dalam. Ini dicatat lengkap supaya tidak ada
yang mengulang percobaan yang sama.

**Upaya 1 — mencuplik lingkungan, bukan satu piksel.**
Dugaan: jalan selebar belasan meter berada di dalam piksel 30 meter yang
isinya juga trotoar, kendaraan, dan dinding bangunan, sehingga yang terukur
lebih banyak bangunan daripada permukaan jalan. Genangan bersifat areal, jadi
seharusnya dicuplik areal juga.

Seluruh arsip ditarik ULANG dengan rata-rata dalam radius 100 meter —
1.813.950 nilai kedua kalinya. Hasilnya lebih buruk, bukan lebih baik.

| | Cuplikan titik | Radius 100 m |
|---|---:|---:|
| ROC-AUC data uji | 0,6579 | **0,5982** |
| ROC-AUC "pasut saja" | 0,4935 | 0,4793 |
| Pasut saat basah − saat kering | −0,003 m | −0,006 m |

Perbandingannya dibuat adil: ambang tidak dipertahankan di −3 dB, melainkan
diturunkan ke −1,4 dB supaya laju labelnya setara (1,48 persen berbanding
1,87 persen). Tanpa penyesuaian itu perataan radius menekan ragam sampai
label basah nyaris lenyap — pada −3 dB hanya tersisa 838 label dari 1,8 juta.

**Upaya 2 — kriteria dua arah, dugaan pantulan ganda.**
Dugaan: di kawasan terbangun, air dangkal di antara bangunan membentuk
pemantul sudut yang justru MENAIKKAN backscatter. Kalau begitu, kriteria
penurunan melihat ke arah yang salah.

Tiga kriteria dibandingkan pada empat ambang, seluruhnya dari data yang sudah
ditarik sehingga tidak memakai kuota sama sekali:

| Kriteria | Korelasi terhadap pasut | Selisih pada tanggal kejadian |
|---|---:|---:|
| turun (anomali < −X) | −0,028 sampai −0,041 | −0,25 sampai −0,38 σ |
| **naik (anomali > +X)** | +0,015 sampai +0,041 | **+0,39 sampai +0,47 σ** |
| dua arah (\|anomali\| > X) | +0,003 sampai +0,014 | +0,21 sampai +0,29 σ |

Arahnya konsisten dan sesuai dugaan — kriteria "naik" selalu positif pada
tanggal kejadian, kriteria "turun" selalu negatif. Jadi fisika pantulan ganda
kemungkinan memang benar. Tetapi besarnya hanya 0,47 simpangan baku pada 12
citra, jauh dari cukup untuk dijadikan label.

**Upaya 3 — melihat kawasan terbuka, bukan jalan.**
Dugaan: air pasang membentuk permukaan halus yang terlihat radar di tambak,
lahan kosong, dan muara — bukan di jalan perkotaan.

Proporsi luas AOI di bawah ambang air terbuka memang besar dan berubah-ubah
(9,8 sampai 25,9 persen luas, simpangan baku 6,6 persen), jadi Sentinel-1
jelas melihat air. Tetapi korelasinya terhadap pasut **negatif**: −0,10
sampai −0,27 tergantung ambang dan orbit.

Tanda negatif itu bukan kejanggalan. Luas gelap didominasi tambak dan muara,
dan air dangkal yang tenang saat surut justru lebih halus, lebih gelap, dan
lebih luas terlihat daripada air dalam yang beriak saat pasang. Isyarat yang
dicari — daratan berubah menjadi air — hanya beberapa persen luas dan
tenggelam di bawah ragam itu.

**Upaya 4 — memakai muka air TERUKUR, bukan pasut astronomis.**
Dugaan yang paling menjanjikan, dan yang paling lama bertahan. Rekonstruksi
harmonik hanya memuat komponen ASTRONOMIS, sementara rob sesungguhnya terjadi
saat pasang astronomis bertemu kenaikan muka air akibat angin, tekanan udara,
dan gelombang badai. Bisa jadi labelnya benar dan pembandingnya yang kurang.

Muka air terukur stasiun IOC `sema` ditarik untuk 725 waktu akuisisi, satu
sensor `prs` saja, 699 di antaranya berhasil. Hasil pertamanya tampak
meyakinkan:

| Pembanding | Korelasi label basah |
|---|---:|
| Pasut astronomis | −0,03 |
| Muka air terukur, MENTAH | **−0,29** |

Sepuluh kali lipat. **Dan seluruhnya semu.**

Rekaman stasiun itu MELAYANG NAIK sepanjang arsip: nilai tengahnya +0,861 m
pada 2015 dan +1,781 m pada 2025, naik **0,92 meter dalam sepuluh tahun**.
Besarannya sepadan dengan laju penurunan muka tanah — masuk akal untuk alat
yang terpasang di tanah yang turun — tetapi sebabnya bisa juga penggantian
alat atau penggeseran datum.

Arsip Sentinel-1 juga berubah sepanjang dekade yang sama: satelitnya berganti
dari 1A ke 1B lalu 1C, dan baseline pengolahannya diperbarui. Dua besaran
yang sama-sama melayang akan berkorelasi kuat tanpa ada hubungan sebab.

Setelah layangan diluruskan per tahun:

| Kriteria | Sebelum diluruskan | Setelah diluruskan |
|---|---:|---:|
| turun | −0,290 | **+0,052** |
| naik | +0,291 | **−0,111** |

Petunjuk bahwa angka mentah itu semu sudah terlihat sebelum diluruskan:
kriteria "turun" dan "naik" berkorelasi hampir sama besar dengan tanda
berlawanan. Kalau genangan yang menjadi penyebabnya, salah satu arah
seharusnya jauh lebih kuat. Simetri seperti itu adalah tanda khas pergeseran
radiometrik SELURUH citra, bukan genangan di ruas tertentu — dan memang
begitu: rata-rata anomali seluruh citra ikut berkorelasi, dan setelah
pergeseran itu dibuang sisanya tinggal −0,06.

**Kesimpulan upaya 4: pembanding BUKAN penyebabnya.** Memakai muka air yang
sebenarnya pun tidak memunculkan kaitan. Yang tersisa untuk diuji tinggal
satu: cara labelnya dibuat, bukan pembandingnya.

Temuan sampingan yang layak disebut sendiri: **stasiun pasut Semarang
merekam kenaikan muka air relatif sekitar 9 sentimeter per tahun** sepanjang
2015–2025. Angka itu bukan kenaikan muka laut absolut — ia campuran kenaikan
muka laut, penurunan tanah tempat alat berdiri, dan kemungkinan perubahan
datum. Sebagai pengamatan mentah ia tetap berguna dan sejalan dengan besaran
subsidensi di literatur.

**Upaya 5 — membuang topeng air permanen, lalu turun ke tingkat ruas.**
Dugaan: Upaya 3 gagal karena luas gelap didominasi tubuh air yang MEMANG
selalu ada. Kalau tambak, sungai, dan laut dibuang lebih dulu, yang
tersisa adalah daratan — dan perubahan di daratan itulah rob.

**Hasilnya tidak nol.** Piksel yang gelap pada lebih dari 40 persen akuisisi dibuang
sebagai tubuh air tetap, lalu proporsi piksel DARAT yang tampak berair
dikorelasikan terhadap pasut, 2019 sampai 2026:

| Orbit | Jam lintas | Citra | Korelasi vs pasut |
|---|---|---:|---:|
| **76, descending** | 05.16 WIB | 195 | **+0,362** |
| 76, ambang −17 dB | | 195 | +0,285 |
| 127, ascending | 17.58 WIB | 316 | +0,032 |
| 127, ambang −17 dB | | 316 | +0,050 |

Tandanya POSITIF — makin tinggi pasut, makin luas daratan tampak berair. Itu
arah yang benar secara fisika, berbeda dari empat upaya sebelumnya.

**Dua keberatan itu kemudian DIUJI, bukan dibiarkan sebagai keberatan.**

Sebelumnya dua hal disebut sebagai alasan tidak mencabut penolakan: rancu
musiman belum disingkirkan, dan yang diukur luas bukan ruas. Keduanya kini
sudah diuji, dan keduanya terbukti menjadi masalah.

### Rancu musiman: benar, dan besar

Sentinel-1 sinkron matahari sehingga melintas pada jam lokal yang hampir
tetap. Pada jam tetap itu, komponen K1 (23,93 jam) dan P1 (24,07 jam)
bergeser fasenya dengan periode sekitar SATU TAHUN, bukan sebulan. Akibatnya
rekonstruksi pasut yang dicuplik pada waktu akuisisi punya siklus tahunan
semu. Kebasahan lahan juga bersiklus tahunan kuat mengikuti musim hujan.

Diuji dengan mengendalikan hari-dalam-tahun pada KEDUA deret — dua harmonik
tahunan, lalu sisanya dikorelasikan. Hasilnya membenarkan kekhawatiran itu:

| Deret | Mentah | Parsial | Susut |
|---|---:|---:|---:|
| Luas AOI, orbit 76, −15 dB | +0,362 | **+0,140** | 62 persen |
| Luas AOI, orbit 76, −17 dB | +0,285 | +0,098 | 66 persen |
| Luas AOI, orbit 127 | +0,032 | +0,041 | — |

**Musim menjelaskan 38,6 persen ragam tinggi pasut** pada waktu akuisisi, dan
32,8 persen ragam proporsi basah. Dua deret yang sama-sama bersiklus tahunan,
persis mekanisme yang dikhawatirkan. Lebih dari separuh korelasi +0,36 itu
ternyata musim, bukan pasut.

### Dari luas ke ruas: melemah lagi, dan buktinya berbalik

Langkah inferensi yang berulang kali disebut "belum tervalidasi" kini
dikerjakan. Topeng air permanen dibangun per orbit, lalu tiap ruas dinilai
dari proporsi piksel darat yang basah dalam radius 100 meter — 487.890 nilai
atas 2.502 ruas dan 195 citra.

| Ambang proporsi | Laju basah | Korelasi pasut | Parsial | Tanggal rob |
|---:|---:|---:|---:|---:|
| 0,05 | 0,92 persen | +0,230 | +0,107 | **−0,77 σ** |
| 0,10 | 0,29 persen | +0,185 | +0,123 | −0,41 σ |
| 0,20 | 0,02 persen | +0,013 | — | −0,52 σ |

Dua hal terbaca dari tabel itu. Isyaratnya **melemah dua kali**: dari 0,362 di
tingkat luas menjadi 0,230 di tingkat ruas, lalu menjadi 0,107 setelah musim
dikendalikan. Dan bukti yang sepenuhnya bebas — tanggal kejadian rob
terdokumentasi — **berbalik arah di seluruh ambang**: label basah justru
lebih JARANG muncul pada hari kejadian.

### Kesimpulan, kini di atas dasar yang jauh lebih kokoh

Yang tersisa setelah kedua keberatan diuji adalah korelasi sekitar +0,11
terhadap pasut, dengan bukti tanggal kejadian yang menunjuk arah berlawanan.
Itu bukan dasar untuk melabeli 19.394 ruas jalan dan menghidupkan kembali
model genangan.

**Penolakan model tetap berdiri**, dan sekarang berdiri karena diuji sampai
tuntas, bukan karena satu keberatan yang dibiarkan menggantung.

Yang tetap patut dicatat sebagai arah lanjutan: tandanya positif dan
konsisten pada orbit 76, dan orbit itu melintas pukul 05.16 WIB. Kalau suatu
saat ada pengamatan genangan per ruas untuk diuji, lintasan pagi itulah yang
paling layak diperiksa lebih dulu.

Skripnya: `12_uji_isyarat_s1.py --darat-saja` untuk tingkat luas,
`20_label_luas_ke_ruas.py` untuk tingkat ruas, dan
`21_uji_rancu_musiman.py` untuk kedua uji musiman. Hasilnya di
`data/referensi/uji_isyarat_s1_darat.json`,
`uji_label_luas_ke_ruas.json`, `uji_rancu_musiman.json`, dan
`uji_rancu_musiman_ruas.json`.

---

### 6.6 Kesimpulan

`PLAN.md` bagian 9.A menyiapkan jalur cadangan untuk keadaan ini, dan
kalimatnya dipatuhi apa adanya: *"Jangan panik dan jangan memaksakan model."*
Sistem beralih ke **indeks kerentanan**, dan klaimnya diturunkan dari
prediksi menjadi kerentanan. Lihat bagian 7.

Model, metriknya, dan grafik kepentingan fiturnya **tetap disimpan** di
`data/processed/model_genangan_v1.joblib`,
`data/referensi/metrik_model.json`, dan `docs/kepentingan_fitur.svg`. Hasil
negatif yang terdokumentasi adalah hasil, dan menyembunyikannya justru
menghilangkan bagian paling informatif dari pekerjaan ini.

---

## 7. Indeks kerentanan rob — yang benar-benar dipakai

Dasar pemikiran lengkap ada di `backend/app/domain/kerentanan.py`.

Tiga komponen berbobot **sama rata**, masing-masing sepertiga:

| Komponen | Arah | Sumber |
|---|---|---|
| Elevasi relatif terhadap tetangga radius 500 m | makin rendah makin rentan | DEMNAS |
| Jarak ke garis pantai | makin dekat makin rentan | OSM `natural=coastline` |
| Laju penurunan muka tanah | makin cepat makin rentan | Rahmawati dkk (2020) |

**Elevasi RELATIF, bukan mutlak.** Aturan repo nomor 4: DEMNAS punya RMSE
vertikal 2,79 m sementara rob yang dimodelkan 10–50 cm, jadi elevasi mutlak
terlalu kasar untuk membedakan ruas dari tetangganya. Galat DEM sebagian
besar berkorelasi spasial, sehingga pengurangan terhadap nilai tengah
tetangga meniadakan sebagian besarnya. Terukur: simpangan baku turun dari
**5,86 m (mutlak) menjadi 2,99 m (relatif)**.

Ini tetap **bukan** ambang elevasi absolut. Tidak ada satu baris pun yang
berbunyi `if elevasi < muka_air: tergenang`.

Sebaran indeks atas 19.394 ruas: p5 0,269 · p25 0,446 · p50 0,572 ·
p75 0,691 · p95 0,773 · p99 0,817.

### 7.1 Pemeriksaan kewarasan, dan kenapa ia BUKAN akurasi

| Jalan yang dilaporkan tergenang | Ruas | Persentil median indeks |
|---|---:|---:|
| Bandarharjo | 18 | 97,7 |
| Kaligawe | 50 | 90,5 |
| Genuk | 9 | 86,0 |
| Terboyo | 9 | 68,7 |
| *Seluruh ruas* | *19.394* | *50,0* |

Keempatnya jauh di atas dasar 50. **Itu tidak boleh disebut akurasi.**
Kawasan yang dilaporkan tergenang seluruhnya pesisir, sedangkan jarak ke
pantai adalah salah satu komponen indeks — jadi indeks ini memang sudah
seharusnya menempatkannya di atas. Kalau tidak, justru ada bug. Melaporkan
angka ini sebagai akurasi berarti mengukur diri sendiri dengan penggaris
buatan sendiri.

**Tidak ada satu pun angka ROC-AUC, F1, atau akurasi yang dilaporkan untuk
indeks ini,** karena tidak ada pengamatan genangan per ruas untuk mengujinya.

### 7.2 Dari indeks menjadi genangan per jam

Indeks bersifat statis; yang berubah tiap jam adalah pasut.

- **Ruas MANA** yang terdampak ditentukan peringkat indeks
- **BERAPA BANYAK** ditentukan pasut: nol saat pasut di atau di bawah nilai
  tengahnya, naik hingga puncaknya saat pasut menyentuh persentil ke-99,9
- Skala puncaknya **10 persen jaringan**, diikat ke perkiraan WRI Indonesia
  bahwa sekitar 10 persen jaringan jalan Kota Semarang berpotensi terdampak
  rob. Angka itu berlaku se-kota sementara AOI ini bagian terparahnya,
  sehingga memakainya apa adanya bersifat konservatif
- **Kedalaman** dari `app/domain/genangan.py`, dibatasi 10–50 cm sesuai
  aturan repo nomor 4, monoton terhadap indeks dan terhadap pasut

Hasil pada 72 jam mulai 28 Agustus 2026: **33 dari 72 jam tanpa genangan
sama sekali**, puncak 1.028 ruas (5,3 persen), 21.778 baris prediksi.

### 7.3 Yang wajib tampil di antarmuka

Sumber `kerentanan_v1` memunculkan lencana **INDEKS KERENTANAN — bukan
prediksi genangan**. Lencana ini tidak punya saklar manual, sama seperti
lencana DATA CONTOH. Hanya sumber `model_v1` yang membuat peta tampil tanpa
lencana, dan itu baru sah bila bagian 6 memuat angka akurasi yang
benar-benar lolos.

---

## 8. Validasi rute

**Sebagian.** Mesin routing diuji lewat `pytest` untuk perilaku algoritmanya:
biaya dihitung pada waktu TIBA bukan waktu berangkat, ruas dengan kedalaman
di atas ambang moda dibuang dari graf, dan dua rute dikembalikan tiap
permintaan. 13 uji.

Diuji juga ujung ke ujung di atas data kerentanan nyata: permintaan mobil
dari Tanjungmas ke Genuk pada jam pasut tinggi mengembalikan dua rute yang
berbeda 1,0 menit dan 0,44 km.

**Yang belum ada:** apakah rute yang disarankan memang bisa dilalui saat rob.
Itu memerlukan pengamatan lapangan, bukan hanya data yang lebih baik.

---

## 9. Validasi estimasi dampak

**Belum tersedia.** Menunggu faktor emisi yang masih `null` di
`data/referensi/faktor_emisi.json`.
