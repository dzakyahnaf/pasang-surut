# Outline slide final PASANG SURUT

Versi 22 September 2026 setelah TM. Delapan slide utama, target sembilan menit termasuk
demo dan perpindahan pembicara; batas rulebook sepuluh menit. Naufal pemilik
deck, Daffa pemilik visual/demo, Dzaky pemeriksa metode dan angka. Ini naskah
dan storyboard siap dipindahkan ke aplikasi slide, belum PPTX/PDF final.

**Konfirmasi TM:** durasi tetap 10 menit + 15 menit tanya jawab, urutan
tampil pertama. Deadline PDF belum diinformasikan. Siapkan semua berkas
dan aplikasi sebelum sesi dimulai; jangan mengandalkan waktu tim lain.
Alamat demo langsung: https://pasang-surut.vercel.app/app. Landing tetap
di https://pasang-surut.vercel.app/. Lencana sumber, tanggal, dan batas
model harus terlihat di screenshot maupun demo.

## Alur dan waktu

| Slide | Judul | Waktu | Pembicara |
|---|---|---|---|
| 1 | Berangkat kapan, lewat mana? | 00.00–00.45 | Dzaky |
| 2 | Satu keputusan perjalanan, tiga informasi | 00.45–01.30 | Dzaky |
| 3 | Coba perjalanan Tawang–Terboyo | 01.30–04.30 | Daffa |
| 4 | Dari pasut dan kerentanan ke pilihan rute | 04.30–05.30 | Dzaky |
| 5 | Bukti yang kami punya dan batasnya | 05.30–06.30 | Dzaky |
| 6 | Membaca biaya adaptasi perjalanan | 06.30–07.30 | Naufal |
| 7 | Langkah menuju uji lapangan | 07.30–08.30 | Naufal |
| 8 | Keputusan perjalanan yang lebih terinformasi | 08.30–09.00 | Naufal |

## Slide 1 — Berangkat kapan, lewat mana?

**Teks layar:** PASANG SURUT — perencanaan perjalanan sadar rob di pesisir
Semarang. “Saya perlu ke Terboyo. Tetap berangkat sekarang, atau mengubah
rute dan jam?” Nama tim dan anggota kecil di bawah.

**Visual:** peta konteks Semarang dengan Tawang, Terboyo, garis pantai, dan
nama wilayah. Maksimal satu ilustrasi perjalanan; jangan membuka dengan
tabel algoritme atau screenshot rute tanpa orientasi lokasi.

**Narasi:** “Perjalanan tetap perlu dilakukan ketika kondisi pesisir berubah.
Pilihan pengguna bukan hanya lewat jalan mana, tetapi juga kapan berangkat.
Kami membangun PASANG SURUT untuk membantu membandingkan pilihan itu.”

**Bahan/PIC:** Daffa membuat visual dari data lokal dan peta yang diperbaiki.
Tidak perlu memasukkan angka kerugian kota jika sumber primernya belum siap
ditunjukkan dan relevansinya terhadap pilot belum dijelaskan.

## Slide 2 — Satu keputusan perjalanan, tiga informasi

**Teks layar:** pilih asal–tujuan dan kendaraan; bandingkan jam dan rute;
baca tambahan waktu/jarak serta peringatan estimasi.

**Visual:** tiga panel sederhana dari UI. Beri label pengguna sasaran
“pengendara di pesisir Semarang”; jangan menyatakan sudah dipakai warga
jika belum ada bukti pemakaian.

**Narasi:** “Produk ini menggabungkan perkiraan pasut dengan indeks
kerentanan jalan. Hasilnya dipakai untuk membandingkan rute dan waktu,
beserta konsekuensi memutar. Estimasi ini membantu perencanaan dan tetap
memerlukan pengecekan kondisi lapangan.”

**Transisi:** “Daffa akan memperlihatkan satu perjalanan yang sama pada dua
waktu berbeda.”

## Slide 3 — Coba perjalanan Tawang–Terboyo

**Teks layar saat transisi:** asal Stasiun Semarang Tawang → tujuan Kawasan
Industri Terboyo; moda motor; tanggal/jam dan sumber data demo terlihat.

**Visual cadangan pada slide:** tiga screenshot berurutan, masing-masing
berlabel lokasi/jam: pilihan titik, perbandingan rute pada jam pasang,
perbandingan pada jam lain. Jangan menampilkan data lama seolah live.

**Urutan demo tiga menit:**

1. 30 detik: orientasi wilayah, pilih dua tujuan bernama dan motor.
2. 60 detik: tunjukkan rute pembanding, rute sadar rob, legenda, dan
   peringatan yang masih muncul. Sebut bahwa hasil bukan jaminan aman.
3. 45 detik: pindahkan jam; tunggu indikator pembaruan selesai; bandingkan
   pilihan dan biaya adaptasi, tanpa menganggap seluruh detour penghematan.
4. 30 detik: jelaskan satu keputusan yang bisa diambil pengguna.
5. 15 detik: kembali ke slide. Bila produksi tidak pulih dalam sekitar
   sepuluh detik, pindah ke lokal atau MP4 tanpa mengulang tunggu berkali-kali.

**Data skenario:** potret lokal bertanggal 26 September, bandingkan 08.00
dan 13.00 WIB; sebut terang-terangan sebagai skenario potret. Untuk produksi
dengan jendela bergerak, gunakan waktu yang masih tercakup, misalnya
27 September 09.00, setelah diverifikasi pada versi final. Angka audit lama
bukan angka final; ambil ulang setelah T2/T4 dan optimasi selesai.

**Bahan/PIC:** Daffa; backend lokal sudah menyala sebelum presentasi. Siapkan
produksi → lokal → MP4 lokal → screenshot, semuanya memakai cerita sama.

## Slide 4 — Dari pasut dan kerentanan ke pilihan rute

**Teks layar/diagram:**

`rekonstruksi pasut + fitur kerentanan ruas → estimasi kondisi per jam → pemilihan rute → perbandingan perjalanan`

Di bawahnya arsitektur ringkas: browser/peta → API → data/potret. Bedakan
pipeline pembentukan data dari komponen yang dipanggil saat klik.

**Narasi:** “Pasut memberi komponen waktu. Indeks kerentanan memberi
perbedaan antar ruas. Kami menggunakan keduanya sebagai model untuk
membandingkan perjalanan; indeks ini belum menggantikan pengamatan genangan
lapangan.”

**Catatan metode, diperbarui 21 September:** gunakan “median 3 × 3 sel grid,
sisi sel 500 m”. Model T4 sudah diterapkan: “kondisi jam keberangkatan
dipertahankan selama satu pencarian”. Perubahan kondisi ketika kendaraan
sedang berjalan belum dimodelkan. Akurasi rekonstruksi pasut tidak boleh
disebut sebagai akurasi genangan per ruas.

**Bahan/PIC:** Dzaky memeriksa `docs/arsitektur.png`; Daffa merapikan diagram.

## Slide 5 — Bukti yang kami punya dan batasnya

**Visual:** dua kolom “sudah dievaluasi” dan “perlu bukti lanjutan”.

**Isi yang boleh dipakai setelah sumber dan jendela uji dicantumkan:**

- Pasut: korelasi 0,78–0,91, RMSE sekitar 0,10–0,12 m pada evaluasi yang
  didokumentasikan. Jelaskan bila data yang sama ikut menentukan parameter.
- Aplikasi: 95 tes backend Windows/Linux dan 25 tes frontend pada audit
  22 September; 2.400 perbandingan routing termasuk dalam tes tersebut,
  jangan menjumlahkannya sebagai 2.400 unit test terpisah. Cantumkan commit
  rilis serta lingkungan. Detail uji publik dan batasnya ada di laporan audit.
- Genangan per ruas: belum ada ground truth yang memadai; kedalaman bukan
  pengukuran lapangan. Eksperimen model Sentinel-1 yang ditolak masuk
  lampiran dan cukup dijelaskan dalam satu kalimat bila relevan.

**Narasi inti:** “Evaluasi yang kami laporkan menguji pasut. Kami belum
menyebutnya akurasi genangan jalan. Pemisahan ini menentukan bagaimana
peringatan dan hasil rute disampaikan kepada pengguna.”

**Bahan/PIC:** Dzaky dari `docs/validasi.md`, metrik, dan hasil regresi baru.
Sertakan sumber kecil yang tetap terbaca pada slide/lampiran.

## Slide 6 — Membaca biaya adaptasi perjalanan

**Visual:** tabel dua pilihan pada satu asal–tujuan dan moda yang sama:
jam, durasi, jarak, tambahan BBM/CO2, serta indikator paparan menurut model.
Setiap angka dari keluaran versi final diberi tanggal dan label “simulasi”.

**Narasi:** “Menghindari ruas yang dianggap rentan dapat menambah jarak.
Kami memperlihatkan biaya adaptasinya, agar pengguna bisa menilai apakah
memutar atau memilih waktu lain lebih sesuai. Angka emisi menjelaskan
konsekuensi pilihan, belum membuktikan penurunan emisi kota.”

**Bukti pengguna:** bila uji tugas 5–8 peserta sudah dijalankan, laporkan
jumlah sebenarnya, latar peserta, keberhasilan tugas, dan satu masalah UI
yang ditemukan. Jika belum dilakukan, pindahkan sebagai rencana slide 7;
jangan mengisi angka keberhasilan perkiraan.

**Bahan/PIC:** Naufal menyusun; Dzaky memeriksa baseline, faktor dan satuan.
Jika faktor yang digunakan hanya CO2 bahan bakar, jangan melabelinya CO2e
tanpa dasar tambahan.

## Slide 7 — Langkah menuju uji lapangan

**Teks layar:** uji kegunaan → kumpulkan observasi ruas bertanggal → evaluasi
indeks pada data terpisah → perbaiki model dan perluas secara bertahap.

**Narasi:** “Tahap berikutnya adalah pilot yang mencatat apakah pengguna
memahami hasil, lalu membandingkan estimasi dengan observasi ruas. Data,
waktu pembaruan, dan batas cakupan perlu dikelola dengan jelas.”

**Visual:** tiga tahap ringkas dengan metrik: keberhasilan tugas, galat
estimasi dibanding observasi, dan kinerja aplikasi. Mitra/instansi yang
belum sepakat disebut calon pihak yang akan diajak, bukan mitra aktif.

**Bahan/PIC:** Naufal. Cantumkan rencana operasional realistis: pembaruan
dataset, pemantauan, biaya hosting, dan pemilik pemeliharaan. Hindari
roadmap panjang yang mengurangi waktu menjelaskan produk yang sudah ada.

## Slide 8 — Keputusan perjalanan yang lebih terinformasi

**Teks layar:** “Bandingkan rute. Pilih waktu. Pahami konsekuensinya.”
QR aplikasi dan repo, disertai URL tertulis yang dapat dibaca.

**Narasi:** “PASANG SURUT membantu pengguna mempertimbangkan perjalanan di
pesisir Semarang dengan informasi waktu, rute, dan biaya adaptasi yang bisa
dibandingkan. Kami siap menunjukkan cara kerja dan batas bukti kami.”

**Bahan/PIC:** Naufal; Daffa menguji QR pada HP nyata. Jangan bergantung pada
internet untuk menampilkan slide penutup.

## Lampiran untuk Q&A, di luar sembilan menit

1. Definisi indeks, fitur, bobot asumsi, grid elevasi, dan sumber data.
2. Grafik evaluasi pasut beserta periode, kalibrasi, dan keterbatasannya.
3. Eksperimen Sentinel-1 yang ditolak dan alasan teknisnya.
4. Algoritme routing, asumsi biaya/waktu, serta uji pergantian jam.
5. Rumus BBM/CO2, baseline, satuan, sumber faktor, dan rentang skenario.
6. Hasil pengujian terbaru: memori, waktu respons, retry, cakupan waktu,
   sumber dataset, commit, serta bukti demo lokal.
7. Lembar koreksi terhadap penjelasan proposal: grid/radius, pasut/genangan,
   model routing bila berubah, dan batas klaim dampak.

## Pemeriksaan sebelum ekspor PDF

- Tidak ada angka lama yang disalin sebagai hasil versi final.
- Nama lokasi dan tanggal demo terbaca dari jarak presentasi.
- Diagram dan grafik bukan paragraf kecil; detail dipindah ke lampiran.
- Screenshot terbaru sesuai aplikasi/potret yang dibawa.
- Transisi ke browser dan kembali ke slide dilatih oleh ketiga anggota.
- Durasi dua latihan berturut-turut ≤9 menit; semua anggota bisa mengambil
  alih bagian penting dan menjawab topik masing-masing.
- PDF ekspor dibuka dan diperiksa ulang pada laptop cadangan.
- Tenggat/kanal pengumpulan mengikuti jawaban panitia/TM, belum diasumsikan.
