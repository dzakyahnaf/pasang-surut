# Presentasi final PASANG SURUT

Paket 23 September 2026: **8 slide utama, target 9 menit termasuk demo
3 menit**, dan 6 lampiran untuk tanya jawab. Rasio 16:9. Pembagian pembicara
merupakan usulan, belum keputusan pembagian tugas tim.

## Berkas untuk digunakan

- [PPTX yang dapat diedit](Pasang_Surut_Final_ANFORCOM_2026.pptx): teks,
  diagram, peta konteks, dan angka berupa objek PowerPoint. Catatan pembicara
  tertanam di setiap slide. Gambar aplikasi dan QR tertanam sebagai PNG.
- [PDF utama, 8 halaman](Pasang_Surut_Final_ANFORCOM_2026_utama.pdf).
- [PDF lengkap, 14 halaman](Pasang_Surut_Final_ANFORCOM_2026.pdf), termasuk
  cadangan demo serta rincian metode/pengujian.
- [Catatan pembicara](catatan_pembicara.md), termasuk jawaban untuk lampiran.
- [Panduan demo dan latihan](panduan_demo.md).
- [Sumber angka dan batas klaim](sumber_angka.md).

Di PowerPoint, F5 menjalankan delapan slide utama. Enam lampiran
**disembunyikan dari urutan biasa**, tetapi tetap ada dalam berkas. Ketik
`9` lalu Enter untuk cadangan demo 08.00, `10` lalu Enter untuk 13.00,
dan `4` lalu Enter untuk kembali ke metode. Pada PDF, halaman lampiran
terletak setelah halaman 8.

| Slide | Pokok | Waktu kumulatif | Usulan pembicara |
|---|---|---|---|
| 1 | Masalah pengguna dan lokasi | 00.00–00.45 | Dzaky |
| 2 | Keputusan yang dibantu produk | 00.45–01.30 | Dzaky |
| 3 | Demo Tawang–Terboyo | 01.30–04.30 | Daffa |
| 4 | Metode dan runtime | 04.30–05.30 | Dzaky |
| 5 | Bukti pengujian dan batasan | 05.30–06.30 | Dzaky |
| 6 | Biaya adaptasi perjalanan | 06.30–07.30 | Naufal |
| 7 | Rencana pengembangan | 07.30–08.30 | Naufal |
| 8 | Penutup, QR dan tautan | 08.30–09.00 | Naufal |

TM selesai; tim tampil pertama. Batas tetap **10 menit presentasi/demo dan
15 menit tanya jawab**. PDF diwajibkan melalui jawaban panitia kepada Dzaky;
deadline belum diumumkan. Pilih versi PDF utama/lengkap mengikuti arahan
panitia saat pengumpulan, bukan mengasumsikan lampiran dilarang atau wajib.

## Pemeriksaan berkas

PPTX dibuka dan PDF diekspor memakai Microsoft PowerPoint. Pemeriksaan
`BoundHeight`/`BoundWidth` tidak menemukan teks melampaui kotaknya. Seluruh
14 halaman hasil render ditinjau; 14 catatan pembicara tersedia. QR asli
dan QR pada hasil render PDF didekode ke `/app`. Tautan PDF juga diperiksa.
Font memakai Arial dan Arial Narrow agar tidak memerlukan pemasangan font
web aplikasi pada laptop presentasi. Tetap uji pada perangkat/proyektor acara.

Skenario diambil ulang dari API potret lokal pada 23 September; screenshot
diambil setelah koreksi pesan panel. Di publik, koreksi itu juga sudah
diverifikasi pada kedua panel. Artefak uji kapasitas tetap berasal dari
audit 22 September, bukan pengujian kapasitas baru untuk PPT ini.

## Membuat ulang (opsional)

Paket Python berikut khusus membuat/verifikasi materi, tidak ditambahkan
ke runtime aplikasi. Alasannya: PPTX yang dapat diedit, ekspor/render PDF,
dan pemeriksaan QR.

```powershell
# Dari akar repo, memakai venv yang sudah ada.
.\.venv\Scripts\python.exe -m pip install --target .deploy-local/presentation-tools -r docs/final/presentasi/requirements-materi.txt
.\.venv\Scripts\python.exe docs/final/presentasi/buat_presentasi.py
& docs/final/presentasi/ekspor_presentasi.ps1
.\.venv\Scripts\python.exe docs/final/presentasi/verifikasi_presentasi.py
```

Ekspor membutuhkan Microsoft PowerPoint pada Windows. Generator memakai
`aset/skenario.json` dan screenshot tersimpan, sehingga tidak menarik angka
baru dari produksi diam-diam. Membuat ulang akan menimpa PPTX/PDF hasil
generator; simpan salinan jika PPTX sudah diedit manual. Target sembilan
menit adalah susunan waktu, belum hasil latihan tim menggunakan stopwatch.
