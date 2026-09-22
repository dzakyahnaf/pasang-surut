# Panduan demo dan latihan final

Tim tampil **pertama**. Selesaikan persiapan sebelum sesi dimulai. Target
latihan 9 menit; batas presentasi/demo 10 menit, tanya jawab 15 menit.
Pertahankan kebiasaan H−30 menit: buka aplikasi, lakukan satu pencarian,
periksa kesehatan layanan dari laptop, dan biarkan tab serta demo lokal siap.

## Sebelum latihan

Pembagian yang disarankan: Dzaky memeriksa angka/metode dan menjawab teknis;
Daffa mengoperasikan demo; Naufal membawa dampak/roadmap dan mengurus berkas
pengumpulan. Semua anggota perlu memahami label sumber dan batas model.

1. Buka PPTX dengan Presenter View; catatan sudah ada di tiap slide.
2. Siapkan `https://pasang-surut.vercel.app/app` dan demo lokal pada tab
   terpisah, kemudian jalankan skenario sekali untuk memanaskan cache.
3. Periksa tanggal/sumber. Dataset produksi dan potret berbeda. Screenshot
   dan angka deck memakai **potret 26 September 2026**, moda motor.
4. Pastikan slide 9/10 dapat dibuka dengan nomor slide + Enter. Kedua
   gambar tertanam; PDF juga tersimpan lokal. MP4 belum dibuat dalam paket ini.
5. Matikan notifikasi, pasang charger, uji adaptor/proyektor, resolusi, zoom
   browser dan font. Lakukan uji cabut koneksi jaringan pada laptop demo lokal.

## Menyalakan potret lokal

Persiapan dependency dilakukan **sebelum hari final**. Laptop ini sudah
memiliki `.venv` dan `frontend/node_modules`; laptop cadangan perlu disiapkan
lebih dulu. Dua terminal dari akar repo:

```powershell
# Terminal 1: API potret, tanpa database.
.\.venv\Scripts\python.exe deploy/demo_lokal.py
```

```powershell
# Terminal 2: aplikasi lokal, proxy ke API potret.
Set-Location frontend
npm run dev -- --config ../deploy/demo.vite.mjs
```

Buka `http://127.0.0.1:5182`. API menggunakan `127.0.0.1:8012` dan sengaja
mengabaikan `DATABASE_URL` dari `.env`. Skrip tidak menulis database atau
membuat data baru. Bila port sudah dipakai, gunakan server demo yang telah
menyala atau hentikan terminal milik demo itu; jangan mematikan proses lain.
`Ctrl+C` menghentikan masing-masing server saat latihan selesai.

Potret mencakup 26 September 00.00 hingga 28 September 23.00 WIB dan berakhir
eksklusif **29 September 00.00 WIB**. Jangan jalankan ulang seed/pipeline
menjelang tampil tanpa memeriksa ulang hasil dan angka presentasi.
Service worker bukan pengganti API lokal: halaman yang pernah dibuka di
Vercel belum menjamin pencarian rute tetap berfungsi saat internet putus.

## Skenario tiga menit pada slide 3

| Alokasi | Aksi | Pesan yang dibawakan |
|---|---|---|
| 0–30 detik | Pilih Tawang → Terboyo, motor; orientasikan peta | Akses jaringan jalan di pesisir Semarang; tanggal/sumber terlihat. |
| 30–90 detik | Pada 26 Sep 08.00, tunjukkan hasil dan peringatan | 13,9 menit, 10,58 km; masih ada paparan model. Pembanding mengabaikan genangan. |
| 90–135 detik | Geser ke 13.00 dan tunggu hasil selesai | 7,0 menit, 6,32 km; rute model sama dengan pembanding. Ini tidak membuktikan jalan kering. |
| 135–165 detik | Jelaskan pilihan | Jam lain bisa dipertimbangkan jika jadwal fleksibel; biaya menunggu belum dihitung. |
| 165–180 detik | Kembali ke slide 4 | Jelaskan metode dan batas kondisi jam keberangkatan. |

Potret dimulai pada 00.00 WIB. Fokus Pita Pasut lalu tekan panah kanan
delapan kali untuk 08.00, tambah lima kali untuk 13.00. Tombol `Home`
mengembalikan awal pita. Nama tempat menunjuk akses yang dilekatkan ke
jaringan jalan, bukan pintu bangunan terverifikasi.

Bila produksi tertahan sekitar 10 detik, pindah ke lokal yang sudah aktif.
Jika lokal juga gagal, tampilkan slide 9 lalu 10 dan lanjutkan narasi.
Kembali ke slide 4. Jangan menghabiskan waktu mengulang permintaan.
Produksi hanya dipakai bila cakupan jam dan hasilnya sudah diperiksa;
dataset produksinya dapat menghasilkan angka berbeda dari potret deck.

## Sisa pekerjaan tim sampai 24 September

- **Dzaky:** baca slide 4–6 dan lampiran 11–14; latih jawaban akurasi pasut,
  genangan per ruas, model jam keberangkatan, dan asumsi emisi.
- **Daffa:** latih demo 3 menit dan perpindahan produksi/lokal/slide;
  periksa QR di HP nyata serta keterbacaan peta di proyektor.
- **Naufal:** latih slide 6–8, konfirmasi deadline PDF kepada panitia,
  simpan PPTX/PDF di dua laptop dan media cadangan.
- **Bersama:** tetapkan pembagian final, lakukan dua latihan penuh dengan
  stopwatch, satu simulasi gangguan jaringan, lalu bekukan versi materi.
- Jika perlu video cadangan atau poster, buat sebagai pekerjaan berikutnya.
  Belum ada bukti uji pengguna; jangan menambahkan testimoni atau persentase
  keberhasilan yang belum dikumpulkan.

Rencana kerja ideal 24 September: 2 jam latihan individu/pemeriksaan materi,
2 jam latihan gabungan dan perbaikan, 1 jam simulasi Q&A, 1 jam pengemasan
berkas/perangkat. Ini usulan 6 jam fokus per orang, bukan komitmen waktu
yang telah dikonfirmasi. Sisakan istirahat; hindari perubahan fitur baru
setelah materi dibekukan kecuali ada bug yang memblokir demo.
