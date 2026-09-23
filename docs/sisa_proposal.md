# Sisa pekerjaan proposal

**Pembaruan 24 September:** [video branding pameran 105 detik](final/pameran/branding/README.md)
dengan musik, narasi Indonesia dan subtitle tersedia. Materi ini dilengkapi
[addendum pameran](final/Addendum_pameran_24_september.docx), diperiksa dengan
Microsoft Word: satu halaman. Proposal yang sudah disubmit tetap diarsipkan.
Uji volume/loop di perangkat acara, poster lomba, latihan tim, dan deadline
PDF tetap perlu ditangani. Catatan MP4 belum selesai di bawah adalah historis.

**Pembaruan 23 September:** [paket PPTX/PDF final](final/presentasi/README.md)
sudah selesai dan diverifikasi, dilengkapi catatan pembicara dan dua gambar
demo. [Addendum materi](final/Addendum_presentasi_23_september.docx) mencatat
skenario terverifikasi, 26 tes frontend, dan tugas manual tersisa. Proposal yang
telah disubmit tidak ditimpa. MP4, latihan tim/proyektor, dan deadline PDF
masih perlu ditangani tim.
Addendum 23 September diperiksa dengan Microsoft Word: satu halaman.

**Pembaruan final 22 September 2026:** proposal yang telah disubmit tetap
diarsipkan. Koreksi metode, status runtime, audit regresi, dan konfirmasi TM
ditulis pada [addendum audit](final/Addendum_audit_22_september.docx).
Dokumen addendum diperiksa dengan Microsoft Word: satu halaman. PPTX/PDF
presentasi final dan video cadangan masih menjadi pekerjaan materi; jangan
menyalin klaim radius 500 m atau CO₂e dari naskah lama tanpa koreksi.

Bagian di bawah adalah riwayat penyusunan proposal babak penyisihan.

Berkas ini memindahkan tujuh kotak `[ ISI MANUAL ]` yang semula tertanam di
dalam `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.docx`.

**Kenapa dipindahkan.** Kotak-kotak itu instruksi untuk penulis, bukan isi
proposal, dan wajib hilang sebelum dikumpulkan. Selama masih di dalam
dokumen, ia memakan sekitar satu halaman penuh dan berisiko ikut tercetak ke
PDF yang dibaca juri. Isinya tidak dibuang, hanya pindah ke tempat yang
memang dibaca tim.

Status per 28 Agustus 2026. Sisa waktu **3 hari**.

---

## 1. Bagian 9 — status implementasi

> Seluruh isi Bagian 9 wajib diperbarui sebelum pengumpulan. Angka progres,
> status modul, dan metrik model masih berupa kerangka. Isi dengan kondisi
> sebenarnya per 31 Agustus 2026. **JANGAN mengarang angka akurasi.** Bila
> model belum selesai dilatih, nyatakan terus terang dan turunkan klaim dari
> prediksi menjadi indeks kerentanan. Kriteria penilaian secara eksplisit
> menghargai penilaian yang realistis dan tidak overclaim.

**Sudah dikerjakan 28 Agustus.** Tabel 7 (status modul) terisi seluruhnya
dari keadaan repo yang sebenarnya. Tabel 8 (metrik model) diisi
"Belum tersedia" pada seluruh baris, karena model memang belum dilatih.

**Diperbarui lagi 28 Agustus, sesi kelima.** Baris "Rekonstruksi harmonik
pasang surut" berubah dari Belum menjadi Selesai setelah acuan fase
terkalibrasi. Ditambahkan satu baris "Fitur ruas dan variabel pemicu"
(19.394 ruas, 102.168 jam). Di bawah Tabel 8 ditambahkan satu paragraf yang
menyatakan terus terang bahwa metrik model belum ada, sekaligus melaporkan
apa yang SUDAH tervalidasi, yaitu komponen pasang surut. Tabel 8 sendiri
tetap "Belum tersedia" seluruhnya.

**Diperbarui 28 Agustus, M4 — dan ini perubahan besar.** Model Sentinel-1
dilatih lalu DITOLAK sendiri karena labelnya tidak berkorelasi dengan pasut.
Rencana 9.A dipakai: klaim diturunkan dari "memprediksi genangan" menjadi
"indeks kerentanan". Yang sudah disunting di dokumen:

- Abstrak: klaim prediksi diganti indeks kerentanan, dengan penolakan model
  disebut terbuka dan dirujuk ke Bagian 9.2
- Bagian 6.2: elevasi kini dijelaskan sebagai elevasi RELATIF terhadap
  tetangga radius 500 m, bukan sebagai fitur mentah
- Tabel 7: baris ekstraksi label dan pelatihan model diperbarui
- Tabel 8: seluruh baris TERISI angka sebenarnya, dengan keterangan tabel
  menyatakan model itu ditolak
- Paragraf di bawah Tabel 8: ditulis ulang menjelaskan kenapa ditolak

**Masih harus dikerjakan:** keputusan tim apakah penurunan klaim ini
diterima. Saya menurunkannya karena aturan repo nomor 1, tetapi ini
keputusan strategis. Tercatat sebagai C16 di Papan Blokade.

## 2. Bagian 10 — tangkapan layar

> **SELURUH BAGIAN 10 WAJIB DIISI GAMBAR.** Tidak ada satu pun gambar yang
> dapat disiapkan sebelumnya. Sisipkan minimal enam tangkapan layar sesuai
> daftar, masing-masing dengan keterangan gambar. Gunakan tangkapan dari
> aplikasi nyata, bukan dari Figma, kecuali pada butir keenam.

Aplikasi sudah berjalan, jadi tangkapan layar sudah bisa diambil sekarang:
peta penuh layar, Pita Pasut pada jam pasut tinggi, dua rute tergambar
bersamaan, dan lencana DATA CONTOH.

**Saran penyajian:** sandingkan dua tangkapan untuk pasangan asal-tujuan
yang sama pada jam surut dan jam pasut puncak. Contoh yang sudah terbukti
menghasilkan perbedaan rute ada di `docs/PROGRESS.md` bagian M3.

## 3. Bagian 11 — angka Impact Projection

> Setiap `[[ISI]]` pada Bagian 11.2 hingga 11.4 harus diisi angka hasil
> perhitungan sistem, bukan perkiraan kasar. Sumbernya adalah selisih rute
> sadar genangan dan rute pembanding pada modul akuntansi dampak.
> **Cantumkan rentang bawah dan atas, bukan satu angka tunggal.** Bila belum
> sempat menghitung, lebih baik menyatakan metode perhitungannya saja
> daripada mengisi angka karangan.

**Belum bisa diisi.** Penghalangnya bukan mesin routing — selisih dua rute
sudah dikembalikan API di field `selisih`. Yang belum ada adalah faktor
emisi dan konsumsi bahan bakar: `data/referensi/faktor_emisi.json` masih
bernilai `null` seluruhnya karena sumbernya belum ditemukan.

## 4. Bagian 13 — daftar pustaka

> Lengkapi seluruh `[[ISI]]`, verifikasi setiap tautan masih dapat diakses,
> seragamkan gaya sitasi (disarankan APA edisi ketujuh), dan urutkan menurut
> abjad. Tambahkan rujukan untuk konstanta harmonik pasang surut dan laju
> penurunan muka tanah begitu sumbernya ditemukan.

**Sudah dikerjakan 28 Agustus,** lima entri, seluruh tautannya dibuka dan
dipastikan berisi:

- Badan Informasi Geospasial — DEMNAS, Ina-Geoportal
- European Space Agency — Sentinel-1, SentiWiki Copernicus
- Google Earth Engine — Sentinel-1 SAR GRD
- Rachman, Ismunarti, dan Handoyo (2015) — konstanta harmonik pasut Semarang
- Rahmawati, Prasetyo, dan Sasmito (2020) — laju penurunan muka tanah,
  *Jurnal Geodesi Undip* 9(1):29–36. **Ditambahkan sesi kelima.** PDF-nya
  dibaca sampai ke tabelnya, bukan dikutip dari ringkasan pencarian

**Masih kosong, dan sengaja dibiarkan kosong sampai sumbernya ada:**

- Data kasus leptospirosis Dinas Kesehatan Kota Semarang
- Tautan riset WRI Indonesia April 2026

## 5. Lampiran A — tautan wajib

> Judul video di YouTube wajib berformat
> `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut` dan visibilitasnya wajib
> publik. Repositori GitHub wajib dapat diakses penguji. Nama berkas
> proposal wajib `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.pdf`.
> Rulebook poin 7.9 mewajibkan penggunaan Figma, sehingga tautan Figma tidak
> boleh kosong.

**Belum satu pun terisi.** Keempatnya bergantung pada pekerjaan manual:
repo publik, deploy, video, dan Figma.

## 6. Grafik tingkat kepentingan fitur

> Sisipkan gambar keluaran skrip pelatihan model. Grafik ini termasuk visual
> paling meyakinkan bagi penguji karena memperlihatkan bahwa model
> mempelajari pola yang masuk akal secara fisik, misalnya tinggi pasut dan
> elevasi terkoreksi menempati peringkat teratas.

**DUA gambar siap sisip, keduanya PNG dan SVG di `docs/`:**

`pasut_saat_akuisisi` — bukti bahwa jam lintasan tetap Sentinel-1 justru
MENGUNTUNGKAN pemantauan rob. Persentil ke-95 pasut saat akuisisi +0,338 m
berbanding +0,302 m pada seluruh jam, jadi arsip memuat lebih banyak
pengamatan pasang tinggi daripada pencuplikan acak. Gambar ini menjawab di
muka keberatan yang hampir pasti muncul di sesi tanya jawab.

`kepentingan_fitur` — **sudah ada, tetapi untuk model yang DITOLAK.**
`docs/kepentingan_fitur.svg` memuat kepentingan permutasi enam fitur.
Grafik itu justru berguna: ia memperlihatkan dengan telak bahwa tiga fitur
waktu — pasut dan dua hujan — tidak menyumbang apa pun, dan itulah alasan
modelnya ditolak. Sisipkan dengan keterangan yang menyebut hal itu, jangan
sebagai bukti model bekerja.

## 7. Logo tools — opsional

> Sisipkan baris logo Python, FastAPI, PostgreSQL, React, MapLibre, dan
> Figma di bawah Tabel 5. Unduh dari situs resmi masing-masing.

Boleh dilewati tanpa mengurangi kelengkapan proposal.

---

## Anggaran halaman

| Keadaan | Halaman |
|---|---:|
| Draf awal, sebelum diisi | 26 |
| Setelah penanda terisi, kotak scaffolding masih ada | 27 |
| **Setelah kotak scaffolding dipindah ke berkas ini** | **26** |
| **Setelah pembaruan sesi kelima (+131 kata)** | **26** |
| **Setelah pembaruan M4 (+86 kata)** | **26** |
| **Setelah paragraf perbandingan Sentinel-1 vs pasut (M5)** | **27** |
| Batas rulebook | 30 |

Diukur dengan Word, bukan diperkirakan. Penanda `[[ISI]]` tersisa **20**.

Naik ke 27 halaman disengaja: paragraf perbandingan kedua pendekatan
menjawab langsung pertanyaan yang paling mungkin muncul di sesi tanya
jawab, dan batas rulebook 30 masih longgar.

Tersisa **4 halaman** untuk Bagian 10 yang seluruhnya berisi tangkapan
layar. Enam gambar dengan keterangan kira-kira menghabiskan 3 sampai 4
halaman, jadi anggarannya pas tetapi tidak longgar. Kalau kurang, yang
paling aman dipangkas adalah Bagian 3 yang saat ini paling panjang.
