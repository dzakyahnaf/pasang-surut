# Naskah demo PASANG SURUT

Untuk video 3–7 menit dan untuk babak final. Waktunya dihitung dari
menjalankan skenarionya sungguhan, bukan diperkirakan.

**Aturan utama: jangan pernah menjelaskan apa yang sedang dimuat.** Kalau ada
yang perlu dijelaskan sambil menunggu, itu tanda ada yang harus diperbaiki,
bukan tanda perlu kalimat pengisi.

---

## Sebelum mulai — daftar periksa 10 menit

Dikerjakan sebelum kamera menyala atau sebelum masuk ruang final.

```bash
# 1. Prakiraan hujan dan prediksi diperbarui.
cd backend
python -m scripts.06_isi_pemicu --prakiraan
python -m scripts.11_indeks_kerentanan

# 2. Potret tahan banting dibekukan ulang. WAJIB — potret lama ditolak API.
python -m scripts.18_seed_demo
python -m scripts.18_seed_demo --periksa    # pastikan masih berlaku
```

Lalu:

- [ ] Buka URL API, pastikan `/api/kesehatan` membalas `200`
- [ ] Buka aplikasi dan **biarkan terbuka** — layanan paket gratis tidur saat
      menganggur, dan permintaan pertama setelah tidur memakan puluhan detik
- [ ] Jalankan skenario di bawah **satu kali penuh** supaya cache graf panas
- [ ] Siapkan laptop cadangan yang menjalankan versi lokal, dengan
      `VITE_API_URL` menunjuk ke `127.0.0.1:8000`
- [ ] Matikan notifikasi

**Kalau jaringan acara mati di tengah demo:** jangan panik dan jangan minta
maaf. Aplikasi tetap jalan dari potret beku. Yang berhenti hanya pemuatan
ulang halaman, dan itu pun hanya kalau service worker belum sempat menyimpan
cangkangnya.

---

## Naskah, 4 menit 30 detik

### 0.00 — 0.35 · Masalah, dengan satu angka

> "Sepuluh persen jaringan jalan Semarang berpotensi terdampak rob. Kerugian
> gangguan transportasinya sekitar Rp848 miliar setahun, menurut WRI
> Indonesia. Tanggulnya belum selesai, tapi orang tetap harus berangkat kerja
> besok pagi."

Layar: peta penuh, belum ada interaksi.

> "PASANG SURUT tidak mencoba menghentikan robnya. Ia menjawab satu
> pertanyaan yang lebih sempit: jalan mana yang berisiko pada jam Anda
> berangkat."

### 0.35 — 1.10 · Tunjukkan bahwa waktu itu penting

Geser Pita Pasut ke jam surut. Diam sejenak — biarkan peta terlihat bersih.

> "Ini jam surut. Jaringan jalannya kering."

Geser ke jam pasut puncak. Ruas terisi selama 180 milidetik.

> "Ini enam jam kemudian. Ruas yang sama."

**Jangan buru-buru.** Pergeseran inilah seluruh argumen produk. Kalau juri
hanya mengingat satu hal, ini yang harus diingat.

### 1.10 — 2.00 · Rutekan sesuatu

Tekan **Pelabuhan Tanjung Emas**, lalu **Kawasan Industri Terboyo**.

> "Dua tujuan yang paling sering dituju truk logistik."

Dua rute muncul. Tunjuk yang putus-putus.

> "Yang putus-putus adalah rute biasa — yang akan diberikan aplikasi peta mana
> pun, karena ia tidak tahu soal rob. Yang tebal menghindari genangan pada jam
> tiba di tiap ruas, bukan pada jam berangkat. Itu bedanya."

### 2.00 — 2.40 · Panel dampak

Tunjuk empat angka.

> "Menghindar itu ada harganya, dan kami menghitungnya: selisih waktu, jarak,
> bahan bakar, dan emisi terhadap rute biasa."

> "Bahan bakar dan emisi ditulis sebagai rentang, bukan angka tunggal, karena
> konsumsi bergantung kendaraan dan lalu lintas. Menyajikan satu angka sampai
> tiga desimal akan menyesatkan."

### 2.40 — 3.10 · Peringatan paparan

Geser ke jam yang membuat rute tetap menembus genangan.

> "Kadang semua jalur tergenang. Sistem tidak berpura-pura ada jalan keluar —
> ia memperingatkan, menjelaskan risiko leptospirasis, dan menyarankan jam
> berangkat lain."

Tekan sarannya. Pita Pasut melompat ke jam itu.

### 3.10 — 4.10 · Halaman validasi — bagian yang menentukan

Buka halaman Validasi.

> "Ini bagian yang biasanya tidak ditunjukkan orang."

> "Kami melatih model genangan dari 725 citra Sentinel-1, 1,8 juta nilai
> backscatter. ROC-AUC 0,66. Lalu kami menolaknya sendiri."

Tunjuk tiga batang merah.

> "Ini alasannya. Ketiga fitur yang bergantung waktu — pasut dan dua hujan —
> menyumbang nol. Model itu belajar ruas mana yang sering beranomali, bukan
> kapan ruas tergenang. Untuk sistem perutean, itu tidak berguna."

> "Kami mencoba menyelamatkannya empat kali: cuplikan areal, kriteria dua
> arah untuk pantulan ganda, luas air kawasan terbuka, dan muka air terukur.
> Keempatnya gagal, dan angkanya semua ada di sini."

> "Yang dipakai sekarang: waktu dari rekonstruksi pasut yang tervalidasi
> terhadap stasiun BIG — korelasi 0,78 sampai 0,91 — dan peringkat ruas dari
> indeks kerentanan. Indeks itu tidak punya angka akurasi, dan kami menulis
> itu di aplikasinya sendiri."

### 4.10 — 4.30 · Tutup

> "Kami tidak bisa menghentikan rob. Kami bisa membuat orang tahu jam berapa
> jalannya lewat, dan berapa harga menghindarinya."

---

## Pertanyaan yang hampir pasti muncul, dan jawabannya

**"Kenapa AUC-nya cuma 0,66?"**
Karena labelnya yang bermasalah, bukan modelnya. Aturan "pasut saja"
menghasilkan 0,4935 — setara lemparan koin. Itu sebabnya modelnya ditolak,
bukan disajikan.

**"Sentinel-1 kan lewat pada jam tetap. Bukankah itu bias?"**
Bias, tapi ke arah yang menguntungkan. Persentil ke-95 pasut saat akuisisi
+0,338 m berbanding +0,302 m pada seluruh jam — arsipnya justru memuat lebih
banyak pengamatan pasang tinggi daripada pencuplikan acak. Penyebabnya
komponen S2 berperiode tepat 12 jam sehingga fasenya terkunci pada waktu
matahari, dan kedua jam lintasan jatuh dekat fase tingginya. Gambarnya ada di
`docs/pasut_saat_akuisisi.png`.

**"Angka kedalaman sentimeternya dari mana?"**
Estimasi turunan, dan kami menulisnya begitu di antarmuka. Sentinel-1 hanya
memberi label basah atau kering. Batas 10 sampai 50 cm berasal dari rentang
rob yang kami tetapkan di awal, bukan dari pengukuran kami.

**"Kenapa tidak pakai model bathtub saja, elevasi di bawah muka air?"**
DEMNAS punya RMSE vertikal 2,79 meter sementara rob yang dimodelkan 10 sampai
50 sentimeter. Galat alat ukurnya lima kali lebih besar daripada hal yang
diukur. Yang kami pakai elevasi **relatif** terhadap tetangga radius 500
meter, yang meniadakan galat berkorelasi spasial — terukur, simpangan bakunya
turun dari 5,86 ke 2,99 meter.

**"Bagaimana kalau internetnya mati saat dinilai?"**
Aplikasinya tetap jalan. Ada potret beku 72 jam, dan peruteannya tetap
menghitung sungguhan dari potret itu — silakan ketuk titik mana pun, bukan
hanya yang kami siapkan.

**"Subsidensi Semarang kan 13 cm per tahun?"**
Sumber yang kami baca sampai ke tabelnya — Jurnal Geodesi Undip 2020 — memberi
maksimum 9,4 cm per tahun pada varian yang RMSE-nya terkecil, yaitu varian
yang dipilih penulisnya sendiri. Angka belasan muncul pada varian terkoreksi
atmosfer yang RMSE-nya dua sampai lima kali lebih besar. Kami memakai yang
dipilih penulisnya.

---

## Yang TIDAK boleh dilakukan saat demo

- Jangan memuat ulang halaman. Service worker menyimpan cangkangnya, tetapi
  permintaan API pertama setelah layanan tidur tetap lambat.
- Jangan mengetuk peta untuk memilih titik kalau tombol tujuan cepat cukup.
  Ketukan peta bisa jatuh di tempat yang jauh dari jalan.
- Jangan menjanjikan angka akurasi untuk indeks kerentanan. Tidak ada.
- Jangan menyebut kedalaman tanpa kata "estimasi".
