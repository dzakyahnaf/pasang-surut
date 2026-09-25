# Presentasi final PASANG SURUT, 25 September 2026

Gunakan paket ini untuk final 26 September. **9 slide utama, target 9 menit
termasuk demo 2 menit 25 detik**, ditambah 9 lampiran untuk tanya jawab dan
cadangan demo. Satu menit tersisa untuk transisi atau gangguan. Durasi ini
target latihan; belum hasil pengukuran presentasi tim.

## Berkas siap dipakai

- [PowerPoint yang dapat diedit](Pasang_Surut_Final_2026_25Sep.pptx).
- [PDF utama, 9 halaman](Pasang_Surut_Final_2026_25Sep_utama.pdf).
- [PDF lengkap, 18 halaman](Pasang_Surut_Final_2026_25Sep_lengkap.pdf).
- [Panduan tim: jadwal, demo, latihan dan jawaban juri](panduan_tim.md).
- [Naskah dan aksi operator per slide](catatan_pembicara.md).
- [Acuan lomba, keputusan alur dan sumber bukti](acuan_dan_sumber.md).

PPTX memuat catatan pembicara pada seluruh slide. Teks, angka, diagram,
dan peta konteks dapat diedit; screenshot, grafik pengujian dan QR tertanam.
Rasio 16:9, font Arial/Arial Narrow, tanpa animasi atau video tertaut yang
harus diunduh ketika presentasi. Gunakan Presenter View agar catatan tidak
terlihat juri. Nama pembicara merupakan usulan pembagian latihan.

## Alur dan waktu

| Slide | Inti pembicaraan | Waktu kumulatif | Usulan pembicara |
|---|---|---|---|
| 1 | Berangkat kapan, lewat mana? | 00:00-00:30 | Dzaky |
| 2 | Kebutuhan perjalanan Tawang ke Terboyo | 00:30-01:20 | Dzaky |
| 3 | Memilih tujuan, menggeser jam, membaca hasil | 01:20-02:05 | Daffa |
| 4 | Demo motor pada 08.00 dan 13.00 | 02:05-04:30 | Daffa |
| 5 | Cara indeks, pasut dan routing membentuk hasil | 04:30-05:30 | Dzaky |
| 6 | Bukti pengujian dan batas yang belum terjawab | 05:30-06:40 | Dzaky |
| 7 | Konsekuensi memutar: waktu, jarak, BBM, CO₂ | 06:40-07:40 | Naufal |
| 8 | Rencana uji pengguna, validasi ruas dan pembaruan | 07:40-08:35 | Naufal |
| 9 | Penutup, QR aplikasi dan akses bukti | 08:35-09:00 | Naufal |

Pembuka memakai satu perjalanan agar juri punya konteks ketika demo dimulai.
Metode dan hasil pengujian menjelaskan keluaran yang baru mereka lihat.
Manfaat dibahas bersama biaya memutar, lalu ditutup dengan pekerjaan yang
memang belum selesai. Uji pengguna **belum dilakukan**, sesuai konfirmasi
Dzaky pada 25 September; target 5-8 peserta ditulis sebagai rencana.

## Navigasi saat tampil

`F5` menjalankan slide 1-9. Lampiran 10-18 disembunyikan dari urutan biasa.
Tombol pada slide 4 membuka cadangan demo; pada slide 9 membuka menu lampiran.
Saat slideshow, nomor slide lalu `Enter` juga bisa dipakai:

| Nomor | Isi |
|---|---|
| 10 | Menu tanya jawab |
| 11, 12 | Cadangan demo 08.00 dan 13.00; kembali ke metode dengan `5` + Enter |
| 13 | Sumber, umur dan masa berlaku data |
| 14 | Grafik pengujian pasut September |
| 15 | Indeks, asumsi genangan, routing dan eksperimen ML |
| 16 | Hosting, penanganan galat dan uji beban |
| 17 | Struktur kode serta reproduksi |
| 18 | Asumsi perhitungan BBM dan CO₂ |

PDF lengkap membawa lampiran dan tautan navigasinya. PDF utama hanya memuat
sembilan halaman, sehingga tidak bisa membuka lampiran yang tidak ada di
berkas itu. Simpan keduanya di laptop dan media cadangan. Ketentuan PDF
berasal dari jawaban panitia kepada Dzaky; deadline belum diumumkan dalam
informasi yang diberikan. Jangan menganggap salah satu versi PDF diwajibkan
panitia tanpa arahan tambahan.

## Bukti pemeriksaan

- Dibuka dan diekspor di Microsoft PowerPoint: 18 slide, **0 overflow teks,
  0 objek di luar slide**. Seluruh halaman hasil render diperiksa visual.
- Ada 18 catatan pembicara dan 9 lampiran tersembunyi. Tautan cadangan pada
  PDF lengkap dan QR hasil render menuju `/app` berhasil diperiksa.
- Alur aplikasi lokal diuji melalui browser dengan request HTTP ke luar
  laptop diblokir. Pilihan Tawang-Terboyo, jam 08.00/13.00, geometri rute,
  angka, versi data, serta tombol Cari ulang cocok dengan sumber deck;
  tidak muncul galat JavaScript. Ini tidak menggantikan uji perangkat acara.
- [Laporan PowerPoint](verifikasi_powerpoint.json), [verifikasi berkas dan
  hash](verifikasi_berkas.json), [verifikasi demo](verifikasi_demo_lokal.json).

Screenshot memakai potret 26 September dari paket 23 September, diuji ulang
pada 25 September. Pengujian 95 backend/26 frontend dan beban VPS adalah
hasil audit 22-23 September, bukan tes kapasitas baru pada sesi materi ini.
Evaluasi pasut memakai data 18-25 September. Runtime, database dan layanan
produksi tidak diubah oleh pembuatan materi.

## Membuat ulang

Dependency khusus materi mengikuti [requirements-materi.txt](../presentasi/requirements-materi.txt),
terpisah dari runtime. Di laptop kerja ini dependency tersedia di
`.deploy-local/presentation-tools`. Jalankan dari akar repo:

```powershell
.\.venv\Scripts\python.exe docs/final/presentasi_25_september/buat_presentasi.py
& docs/final/presentasi_25_september/ekspor_presentasi.ps1
.\.venv\Scripts\python.exe docs/final/presentasi_25_september/verifikasi_presentasi.py
```

Ekspor memerlukan Microsoft PowerPoint desktop. Generator membaca angka
skenario, audit dan geometri repo. Hasil render pemeriksaan berada di
`.deploy-local/ppt-final-25/review`, tidak ikut paket publik. Menjalankan
generator menimpa PPTX; jika tim menyunting secara manual, simpan salinan
bernama lain dahulu dan periksa ulang PDF serta catatan pembicaranya.
