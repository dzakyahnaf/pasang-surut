# Sisa pekerjaan proposal

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

**Masih harus dikerjakan:** perbarui lagi pada 31 Agustus bila M4 selesai.
Bila model tetap belum jadi, turunkan klaim menjadi indeks kerentanan
sesuai rencana 9.A di PLAN.md.

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

**Menunggu M4.**

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
| Batas rulebook | 30 |

Diukur dengan Word, bukan diperkirakan. Penanda `[[ISI]]` tersisa **20**,
turun dari 21.

Tersisa **4 halaman** untuk Bagian 10 yang seluruhnya berisi tangkapan
layar. Enam gambar dengan keterangan kira-kira menghabiskan 3 sampai 4
halaman, jadi anggarannya pas tetapi tidak longgar. Kalau kurang, yang
paling aman dipangkas adalah Bagian 3 yang saat ini paling panjang.
