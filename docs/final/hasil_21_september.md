# Hasil perbaikan dan pemeriksaan VPS — 21 September 2026

> Catatan historis. Uji Linux, migrasi database, dan penerapan VPS privat
> berikutnya tercatat pada [laporan 22 September](migrasi_vps_22_september.md).
> Rekomendasi menambahkan situs pada Caddy lama di bawah tidak dipakai:
> instruksi terbaru mempertahankan seluruh layanan Maknaprice.

Empat perbaikan yang disetujui Dzaky sudah diterapkan dan diuji **di workspace
lokal**. Belum ada commit/push, deploy, migrasi Supabase, pembelian hosting,
atau perubahan layanan Maknaprice. Versi publik belum mendapat perubahan ini.
Dokumen ini menggantikan rekomendasi hosting dan status implementasi pada
catatan 20 September. Dzaky menolak Render berbayar; opsi utama berikutnya
adalah memakai VPS yang sudah dimiliki, dengan demo lokal tetap disiapkan.

## Perubahan yang selesai

| Temuan | Perubahan dan bukti |
|---|---|
| Cari ulang tidak bekerja | Tombol sekarang mengirim request baru walaupun asal, tujuan, moda, dan jam sama. Galat hilang setelah pulih. Diuji di React dan browser Edge dengan request pertama sengaja dijawab 503 |
| Waktu tanpa data dianggap kering | Dataset membawa versi dan daftar jam lengkap. Jam tanpa baris basah hanya dianggap kering jika metadata menyatakan jam itu lengkap. Tahun 2099, perjalanan melewati akhir cakupan, dan lubang antarkala ditolak 422; data hilang/kedaluwarsa ditolak 503. Jam yang tidak tersedia ditandai di pita |
| Lambat dan kehabisan memori | Geometri statis dikirim terpisah dari perubahan kedalaman; graf/prediksi dipakai bersama, dimuat satu kali secara terkunci, lalu diperiksa per versi. Slider ditunda 300 ms, request lama dibatalkan dan respons terlambat diabaikan. Maksimum dua request berat dilayani bersamaan; sisanya mendapat 503 `server_sibuk` tanpa antrean. BLAS/OMP/MKL dibatasi satu thread di API dan Docker |
| Routing saat pergantian jam | Kondisi **jam keberangkatan tetap sepanjang satu pencarian**. Mengubah jam menghitung ulang biaya. Kasus lawan pergantian jam mendapat uji regresi terhadap model baru. Batas model tampil di panel dan respons API |

Perubahan routing membatasi model secara eksplisit. Ini tidak menyelesaikan
optimasi jaringan dinamis yang kondisinya berubah ketika kendaraan sedang
berjalan. Klaim optimalitas hanya berlaku pada graf biaya tetap tersebut,
dengan asumsi waktu tempuh dan penalti yang digunakan. Rute bukan jaminan
keselamatan di lapangan.

Metadata dan prediksi dari database kini diterbitkan dalam transaksi yang
sama oleh skrip 03/10/11. Publikasi yang seluruh jamnya kering tetap sah;
menghapus data sumber atau jaringan juga membatalkan metadata kelengkapannya.
Pembacaan runtime menggunakan satu snapshot transaksi. Graf database disimpan
selama proses hidup: setelah mengganti jaringan jalan, restart API diperlukan.

Potret demo dihitung ulang untuk **26 September 00.00 sampai 28 September
23.00 WIB**, bukan sekadar diberi cap lengkap pada data lama. Penghitungan
memakai indeks tersimpan dengan presisi empat desimal dan acuan pasut dari
pipeline: bawah `0.0138329530994234`, puncak `0.418352523203923`, asumsi
proporsi puncak 0,10. Provenans tersimpan dalam `rekonstruksi_potret`.
Pembulatan indeks dapat membuat hasil berbeda dari pipeline presisi penuh.
Potret berakhir pada **29 September 00.00 WIB** dan sesudah itu ditolak.

README dan outline slide diselaraskan: elevasi relatif memakai median
lingkungan **3 × 3 sel grid, sisi sel 500 m**. Evaluasi rekonstruksi pasut
tetap harus dibedakan dari akurasi genangan per ruas yang belum tervalidasi.
Label nama jalan/wilayah pada peta masih menjadi pekerjaan UI tersendiri.

## Hasil pengujian

- Backend: **57 tes lulus**; termasuk retry data, cakupan, kedaluwarsa setelah
  cache, pergantian versi, pemuatan serentak, fallback saat query gagal,
  pembatasan beban, dan regresi routing.
- Antarmuka: **7 tes lulus**; retry, debounce, pembatalan, respons terlambat,
  jam tidak tersedia, pemulihan galat, serta perbedaan versi geometri.
- HTTP nyata melalui Uvicorn lokal: **35 lulus, 0 gagal**.
- Build frontend produksi berhasil. Peringatan bundel besar masih ada:
  JavaScript sekitar 1,27 MB sebelum gzip, 349 kB setelah gzip.
- Browser Edge lokal: request rute pertama sengaja gagal lalu retry berhasil;
  slider 00.00 → 08.00 menghasilkan rute baru dan 1.043 ruas basah;
  **nol unduhan geometri tambahan** ketika slider bergeser; tidak ada galat
  JavaScript/MapLibre. Dua request geometri saat bootstrap berasal dari
  React StrictMode development, termasuk request pertama yang dibatalkan.

Laporan mentah: [benchmark](bukti/kinerja_21_september.json),
[browser](bukti/browser_21_september.json),
[tangkapan layar](bukti/ui_perbaikan_21_september.png).

Benchmark: Windows localhost, potret, satu worker, tiga putaran berisi
masing-masing 30 request per endpoint; lima pilihan jam. Ini **bukan** hasil
VPS/Linux/Render dan tidak dapat dibandingkan langsung dengan latensi
produksi 5,8–6,8 detik yang melibatkan jaringan dan database.

| Ukuran | Hasil lokal |
|---|---:|
| Rute p95, 90 sampel | 317,20 ms |
| Kondisi peta p95, 90 sampel | 6,19 ms |
| Geometri statis, sekali muat | 4.464.414 byte |
| Kondisi per jam pada sampel | 290–20.442 byte |
| RSS akhir tiga putaran | 121,3 / 120,1 / 121,3 MiB |
| Puncak RSS tersampel | 126,2 MiB |
| Alokasi privat Windows setelah uji | 108,1 MiB |
| Puncak working set Windows | 130,8 MiB |
| Enam rute serentak, hanya localhost | 2 berhasil, 4 ditolak 503 secara terkendali |

Sebelum pembatasan BLAS, laporan lokal mencatat alokasi privat Windows
783,6 MiB. Pemeriksaan proses baru menunjukkan OpenBLAS membuka 22 thread;
setelah dibatasi satu thread, alokasi turun tajam. RSS yang rendah pada
proses lama tidak cukup untuk menilai tekanan memori karena paging Windows.
[Laporan sebelum pembatasan](bukti/kinerja_sebelum_batas_blas.json) disimpan
agar angka tersebut tidak tertukar. Ini faktor pemborosan yang terbukti
lokal, belum bukti penyebab tunggal OOM Render pukul 17.09.

Batas verifikasi: Docker Desktop daemon tidak aktif, sehingga image Linux,
migrasi SQL, dan integrasi dataset database baru belum diuji di container
nyata. Tidak ada uji beban produksi tambahan. HP, proyektor, dan laptop
dengan Wi-Fi dimatikan tetap perlu gladi langsung.

## VPS yang sudah dimiliki

SSH berhasil menggunakan kunci yang ditunjuk Dzaky; fingerprint host cocok.
Pemeriksaan hanya membaca keadaan layanan dan metrik, tanpa mengubah
container, database, Caddy, DNS, firewall, atau berkas aplikasi Maknaprice.
Kredensial dan isi private key tidak disimpan dalam laporan/repo.

| Komponen | Hasil pemeriksaan |
|---|---|
| Sistem | Rocky Linux 8.10, x86-64, waktu Asia/Jakarta tersinkron |
| CPU | 2 vCPU; load 0,06 / 0,03 / 0,00 saat sampel |
| RAM fisik | 1.723 MiB, sekitar 1,68 GiB |
| RAM tersedia | Sekitar 879 MiB saat sampel |
| Swap | 2 GiB; 169 MiB terpakai, tidak ada aktivitas swap masuk/keluar pada sampel lanjutan |
| Disk | 39 GiB total, sekitar 29 GiB tersisa |
| Maknaprice Next.js | Sekitar 183 MiB, healthy |
| Caddy | Sekitar 38 MiB; sudah memiliki port publik 80/443 |
| PostgreSQL 17 Alpine | Sekitar 47 MiB, healthy; database aplikasi sekitar 8,4 MiB |
| PostGIS | Tidak tersedia pada daftar extension image PostgreSQL saat ini |
| Batas container lama | Belum ada batas RAM/CPU per container; tidak diubah |

Tidak terlihat OOM pada log kernel tujuh hari yang tersedia maupun status
container saat diperiksa. Metrik ini merupakan sampel saat relatif sepi;
belum menunjukkan puncak trafik Maknaprice.

**Keputusan yang disarankan: gunakan VPS ini dahulu untuk API PASANG SURUT
yang sudah dioptimalkan. Frontend statis juga dapat disajikan di VPS yang
sama melalui Caddy.** Tidak perlu membeli VPS baru sebelum uji bertahap.

Makna “seluruhnya” perlu dibedakan:

| Bentuk layanan | Penilaian |
|---|---|
| Frontend + API + potret bertanggal | Kandidat utama untuk final. Semua kebutuhan runtime PASANG SURUT ada di VPS; tidak membutuhkan Supabase saat melayani |
| Frontend + API di VPS, data terbaru tetap Supabase | Kandidat untuk layanan dengan pembaruan berkala setelah migrasi metadata dan publikasi data diuji |
| Frontend + API + PostgreSQL/PostGIS baru di VPS | Belum disarankan menjelang final pada RAM fisik 1,68 GiB bersama Maknaprice. Memerlukan container database terpisah, pengukuran tambahan, backup, dan rencana pemindahan data |

Pipeline ekstraksi/pelatihan/pembentukan data tetap dijalankan di laptop
atau runner terpisah. API hanya membaca hasilnya. Memindahkan runtime ke
VPS tidak berarti menjalankan Earth Engine/training di VPS kecil tersebut.

## Rancangan penerapan berikutnya

1. Build image API dan frontend di laptop/runner, supaya proses build tidak
   memperebutkan RAM dengan Maknaprice. Gunakan `VITE_API_URL=""` jika Caddy
   menyajikan frontend dan `/api/*` pada domain yang sama.
2. Jalankan API dalam container dan direktori terpisah. Titik awal uji:
   **satu worker, batas RAM 384 MiB, CPU maksimum 1 vCPU**, batas dua request
   berat dan satu thread BLAS. Batas ini usulan awal berdasarkan pengukuran
   lokal, belum konfigurasi VPS yang teruji. Jangan mengandalkan swap sebagai
   tambahan RAM untuk latensi demo.
3. Untuk final, pilih `DATABASE_URL` kosong secara eksplisit sehingga
   runtime memakai potret. Tanggal dan label potret harus tetap terlihat.
   Siapkan ulang data jika periode demo berubah atau potret kedaluwarsa.
4. Tambahkan satu situs pada Caddy yang ada, dengan domain/subdomain yang
   dipilih Dzaky. Caddy menyajikan hasil `frontend/dist` dan meneruskan
   `/api/*` ke container API melalui jaringan internal. Jangan berebut port
   80/443 atau mengganti image PostgreSQL Maknaprice menjadi PostGIS.
5. Uji bertahap: kesehatan kedua aplikasi; buka dashboard; satu pencarian;
   ubah jam; retry; lalu beberapa sesi terbatas. Pantau RAM container,
   `MemAvailable`, swap, restart, latensi, dan galat Maknaprice selama
   30–60 menit. Target cadangan praktis: pertahankan setidaknya sekitar
   400 MiB `MemAvailable`; hentikan container baru bila layanan lama
   terpengaruh, OOM, atau terjadi swap terus-menerus.
6. Alihkan URL pengguna setelah pengujian lulus. Pemulihan dilakukan dengan
   melepas situs/container PASANG SURUT dan mengembalikan URL sebelumnya;
   data dan layanan Maknaprice tetap terpisah. Demo laptop dipertahankan.

Jika memilih data Supabase terbaru, terapkan
[`001_cakupan_prediksi.sql`](../../db/migrations/001_cakupan_prediksi.sql)
lalu terbitkan ulang prediksi melalui pipeline yang sudah diperbarui.
Mengandalkan `MIN/MAX(waktu)` dari baris lama tidak membuktikan jam kering
sudah dihitung. Jalankan uji integrasi database sebelum mengarahkan API ke
dataset tersebut. Hingga metadata tersedia, API memakai potret cadangan
yang valid dan menyatakan sumbernya kepada klien.

## Menjalankan pemeriksaan ulang

Dari akar repo, aktifkan `.venv`; perintah backend dijalankan dari
`backend/`, perintah npm dari `frontend/`:

```text
python -m pytest -q
npm test
npm run build
python -m scripts.23_uji_menyeluruh --alamat http://127.0.0.1:8018
python -m scripts.28_uji_kinerja_lokal --pid PID_UVICORN --alamat http://127.0.0.1:8018
python -m scripts.29_uji_browser_lokal
```

Benchmark membutuhkan `psutil`; uji browser membutuhkan paket `playwright`
dan Edge, frontend development pada port 5173 dengan
`VITE_API_URL=http://127.0.0.1:8018`, serta API potret lokal pada port 8018.
Alat ukur itu tidak masuk dependency runtime image. Script 28 membatasi
alamat tujuan ke localhost; jangan mengubahnya untuk menguji beban layanan
publik tanpa rencana terpisah.
