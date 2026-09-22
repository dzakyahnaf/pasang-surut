# Migrasi VPS — 22 September 2026

**API, frontend produksi, dan database PostGIS PASANG SURUT sudah berjalan
di VPS untuk pengujian privat.** Alamat masuk tetap
`https://pasang-surut.vercel.app`, tetapi pengalihan layanan publik **belum
dilakukan**. Port origin masih `127.0.0.1:18080`, hanya dapat diakses di VPS
atau melalui SSH tunnel. Render dan Supabase lama tetap tersedia.

Hasil saat ini mendukung memakai VPS lama untuk runtime demo final, dengan
pembatasan beban dan cadangan laptop. Pengujian jalur publik Vercel–VPS
masih diperlukan sebelum keputusan pengalihan produksi. Hasil ini
menggantikan penilaian awal bahwa database belum layak dicoba pada
[catatan 21 September](hasil_21_september.md).

## Yang selesai dan batasnya

| Bagian | Hasil |
|---|---|
| Empat temuan aplikasi | Perbaikan retry, cakupan waktu, memori/kinerja, dan model routing diterapkan pada image VPS; versi publik lama belum mendapatkannya |
| Linux | 57 tes backend lulus pada image Linux final; 4 peringatan deprecation dependency/lifecycle |
| Frontend | 7 tes React lulus; build produksi dan browser Edge melalui SSH tunnel lulus |
| HTTP | 35 pemeriksaan endpoint melalui tunnel lulus |
| Database | Lima tabel PASANG SURUT disalin dari Supabase dan seluruh isi diverifikasi; metadata cakupan baru diuji; prediksi diterbitkan ulang |
| Pemulihan | Backup berhasil dipulihkan ke database uji terpisah; penghentian sementara database PASANG SURUT memicu fallback potret, lalu API kembali ke database setelah pulih |
| Maknaprice | Tidak ada perubahan layanan, image, konfigurasi Caddy, jaringan aplikasi, atau database Maknaprice; identitas dan waktu mulai container tetap sama |
| Akses publik | Belum dialihkan; pembukaan origin dan perubahan routing Vercel tertahan tinjauan persetujuan otomatis |

Routing menggunakan **kondisi pada jam keberangkatan sepanjang satu
pencarian**. Mengubah jam menghitung ulang rute. Ini membatasi klaim
optimalitas pada graf biaya tetap, bukan menyelesaikan routing dinamis
ketika kondisi berubah selama perjalanan. Batas tersebut tampil di UI.

Insiden Render dari log Dzaky konsisten dengan kehabisan RAM: request
`/api/ruas` mendapat 500 pada 20 September 17.09.07 WIB, kemudian proses baru
mulai pada 17.09.18 WIB. Email menyatakan penggunaan melebihi 512 MB. Log ini
tidak mengidentifikasi alokasi atau kebocoran tertentu. Pembatasan thread
BLAS, penggunaan ulang graf, pemisahan geometri, dan pembatasan request
mengatasi pemborosan yang direproduksi; belum membuktikan penyebab tunggal
insiden lama.

## Kinerja dan kapasitas

Pengukuran VPS dilakukan pada loopback Linux dengan satu worker dan CPU API
maksimum 0,8 vCPU. Tiap mode memakai 30 pencarian berurutan, bergantian pada
lima jam, dengan asal Tawang dan tujuan Terboyo. Angka geometri adalah
respons pertama setelah pemeriksaan kesehatan, bukan waktu cold start proses.

| Pengukuran | VPS potret | VPS database, image final |
|---|---:|---:|
| Rute p95 | 686,49 ms | **724,39 ms** |
| Kondisi jalan p95 | 14,61 ms | **17,59 ms** |
| Geometri sekali muat | 183,32 ms | 170,19 ms |
| Ukuran geometri sebelum kompresi | 4.464.414 byte | 4.464.454 byte |
| Respons kondisi per jam | 290–20.442 byte | 292–20.444 byte |

Selisih kecil ukuran geometri berasal dari penambahan versi jaringan di
payload pada image final. Hasil rute lima skenario konsisten antara mode
potret dan database. Benchmark ini berbeda jalur dari audit produksi lama
(ruas sekitar 10,9 detik, rute 5,8–6,8 detik); **jangan menyebutnya rasio
percepatan Vercel yang sudah terukur**.

Saat enam pencarian berat dikirim serentak melalui tunnel, dua selesai 200
dan empat ditolak 503 `server_sibuk`. API tetap sehat. Ini perilaku batas
kapasitas yang disengaja, bukan bukti mampu melayani enam pencarian
bersamaan. Tombol Cari ulang sudah diuji setelah galat.

VPS mempunyai 2 vCPU, RAM fisik 1.723 MiB, swap 2 GiB, dan disk tersedia
sekitar 29 GiB. Konfigurasi runtime terisolasi:

| Container PASANG SURUT | Batas RAM | Batas CPU | Sampel setelah benchmark final |
|---|---:|---:|---:|
| API, satu worker | **320 MiB** | 0,80 | 149,4 MiB |
| PostgreSQL 17 + PostGIS 3.5 | 192 MiB | 0,35 | 38,8 MiB |
| Caddy frontend/proxy sendiri | 48 MiB | 0,15 | 25,6 MiB |

API semula dibatasi 256 MiB. Setelah fallback dan pemulihan database,
graf potret dan graf database sama-sama berada di cache: sampel 221,5 MiB
dan puncak cgroup 250,7 MiB, tanpa kegagalan alokasi/OOM. Batas dinaikkan ke
320 MiB untuk ruang permintaan berikutnya. Ini perubahan hanya pada
container PASANG SURUT. Jumlah batas RAM ketiganya 560 MiB; layanan lama
tetap berbagi RAM host sehingga pemantauan masih diperlukan.

Sampel setelah benchmark mencatat RAM tersedia 652 MiB dan swap terpakai
194 MiB. Dua interval `vmstat` berikutnya tidak menunjukkan swap masuk atau
keluar. Pengamatan awal 45 menit mencatat minimum RAM tersedia 641,3 MiB,
seluruh pemeriksaan Maknaprice HTTP 200, tanpa pemicu penghentian otomatis.
Pengamatan kedua selama 45 menit (122 sampel) mencakup uji pemulihan database
dan penyesuaian batas RAM: RAM tersedia minimum **533,4 MiB**, seluruh
pemeriksaan Maknaprice HTTP 200, identitas container tetap sama, dan guard
tidak terpicu. Pemeriksaan ulang sekitar 22 September 10.16 WIB mencatat
RAM tersedia 660 MiB, API 165,6 MiB, dan tidak ada OOM/restart otomatis pada
container PASANG SURUT. Ini pemeriksaan ulang sesaat, bukan pemantauan
kontinu sepanjang malam. Pengamatan terbatas ini belum mewakili
puncak trafik Maknaprice atau penggunaan berhari-hari.

Build Linux menggunakan builder khusus PASANG SURUT dengan batas 384 MiB
dan 0,8 CPU; builder dihentikan setelah build. Builder, container, volume,
network, dan Caddy Maknaprice tidak diubah. Ekstraksi Earth Engine,
pelatihan, dan pipeline besar tetap dikerjakan di luar VPS ini.

## Data, backup, dan masa berlaku

Ekspor sumber memakai transaksi read-only konsisten, hanya lima tabel
aplikasi: 19.394 ruas, 103.080 pemicu, 67.442 prediksi, 0 sampel latih,
dan 3 ambang moda. Jumlah baris dan SHA-256 CSV seluruh kolom cocok setelah
impor. Tidak ada perubahan pada Supabase sumber. PostGIS dibuat dalam
container baru karena image database Maknaprice tidak menyediakan PostGIS.

Pengujian SQL mencakup migrasi berulang, geometri valid, publikasi jam yang
seluruhnya kering, pembatalan metadata saat sumber berubah, rollback
publikasi gagal, dan penolakan DELETE oleh akun API read-only. Data kemudian
diterbitkan ulang melalui pipeline indeks kerentanan; hasilnya **87.427
prediksi dan 317 jam lengkap**, dengan versi dataset tersendiri.

- Cakupan database: **22 September 02.00 WIB–5 Oktober 06.00 WIB**;
  akhir eksklusif **5 Oktober 07.00 WIB**.
- Potret cadangan: **26 September 00.00 WIB–28 September 23.00 WIB**;
  kedaluwarsa **29 September 00.00 WIB**. Potret hanya melayani jam dalam
  cakupannya; fallback pada 22 September tidak membuat data hari itu tersedia.
- Jadwal pembaruan prediksi otomatis belum dipasang. Cakupan sekarang cukup
  untuk tanggal final yang diketahui; sumber pemicu dan publikasi perlu
  diperbarui sebelum masa berlaku habis. Jangan mengubah cap waktu saja.

Backup setelah publikasi berukuran 3.735.909 byte, SHA-256
`1a7b15174ac19e7e473f261b930c7fa4849bcfbe0e90868a986fce373054ec96`.
Restore ke database uji PASANG SURUT berhasil dengan 19.394 ruas, 87.427
prediksi, dan 317 jam lengkap; database uji kemudian dihapus. Backup lokal
tersimpan di `.deploy-local/backups/` dan tidak masuk Git.

Backup harian khusus PASANG SURUT dijadwalkan pukul **03.20 WIB** melalui
`/etc/cron.d/pasang-surut-backup`. Script memeriksa identitas project,
menunda bila RAM tersedia kurang dari 450.000 KiB, dan memvalidasi arsip
sebelum menyelesaikan file. Backup manual dan **run terjadwal 22 September
03.20 WIB** sudah berhasil, masing-masing 3.735.909 byte. Backup harian di
disk VPS belum menjadi backup di luar server secara otomatis; salin secara
berkala ke laptop. Tidak ada penghapusan backup otomatis.

## Temuan khusus saat uji browser produksi

Caddy menambahkan akhiran kompresi pada ETag. Klien sebelumnya memakai ETag
sebagai versi logis jaringan, sehingga geometri dianggap berbeda dari
respons kondisi dan bisa diunduh berulang. Versi jaringan sekarang berada
di payload JSON; salt versi membatalkan cache payload lama. ETag tetap
berfungsi sebagai validator HTTP.

Uji ulang build produksi melewati Caddy terkompresi: satu unduhan geometri,
**nol unduhan tambahan saat slider digeser**, retry berhasil setelah request
pertama dibuat gagal, waktu terpilih dan rute mengikuti respons terbaru,
tanpa galat JavaScript/MapLibre. Uji itu memakai Edge pada laptop melalui
SSH; belum merupakan gladi HP, proyektor, atau internet venue.

## Langkah publik yang masih tertahan

Alamat pengguna tetap `pasang-surut.vercel.app`. Usulan yang sudah
disiapkan adalah Vercel sebagai pintu masuk HTTPS yang meneruskan semua
request ke Caddy PASANG SURUT pada port 18080. Frontend dan API sama-sama
berasal dari VPS; browser menggunakan `/api` pada origin yang sama.

**Usulan ini belum diterapkan.** Peninjau persetujuan otomatis menolak
pembukaan `PASANG_BIND=0.0.0.0` dan pengalihan routing karena akan membuka
origin HTTP tanpa autentikasi secara menetap. Otorisasi umum migrasi
bersyarat dinilai belum mencakup paparan publik tersebut secara spesifik.
`frontend/vercel.json` tetap pada konfigurasi produksi sebelumnya.

Opsi sementara memerlukan persetujuan spesifik untuk membuka HTTP 18080
dan mengalihkan Vercel setelah pengujian publik lulus. HTTPS hanya berlaku
di sisi pengguna–Vercel; jalur Vercel–VPS pada opsi ini belum terenkripsi.
Jika origin juga harus HTTPS, siapkan alamat origin dan sertifikat pada
layanan PASANG SURUT sendiri terlebih dahulu. Caddy Maknaprice tidak boleh
diubah untuk salah satu opsi.

Setelah jalur origin disetujui: uji endpoint publik satu per satu, uji
preview Vercel (halaman, aset, API, slider, retry, cache/service worker),
ukur latensi dari laptop, lalu alihkan produksi hanya jika hasilnya
memenuhi kebutuhan demo dan Maknaprice tetap sehat. Simpan deployment
Vercel sebelumnya untuk rollback. Jangan menghapus Render/Supabase sampai
pengalihan dan gladi final selesai.

## Pengingat ide dan peta untuk juri

**PASANG SURUT membantu warga dan logistik membandingkan rute serta waktu
berangkat berdasarkan indikasi risiko rob di Semarang.** Waktu risiko
menggunakan rekonstruksi pasut; kerentanan ruas berasal dari indeks elevasi,
jarak pantai, dan penurunan tanah. Sistem bukan sensor genangan langsung.

Peta masih menampilkan jaringan/rute tanpa konteks nama yang memadai.
Sebelum merekam demo atau menyusun slide final, prioritaskan nama jalan,
wilayah, landmark/POI, serta nama asal–tujuan di samping koordinat. Gunakan
nama yang tersedia di data dan label fallback yang jujur untuk ruas tanpa
nama; jangan mengarang. Pastikan keterbacaan pada proyektor dan cadangan
lokal. Judul “Semarang Utara dan Timur” saja belum cukup untuk orientasi.

Penjelasan elevasi tetap **median lingkungan 3 × 3 sel grid, sisi sel
500 m**, bukan radius 500 m. Angka validasi pasut bukan akurasi prediksi
genangan per ruas. Perbaikan label peta belum dikerjakan pada migrasi ini.

## Bukti dan operasi

- [Benchmark database final](bukti/vps_database_22_september.json) dan
  [potret](bukti/vps_potret_22_september.json).
- [Migrasi SQL](bukti/migration_test_22_september.json),
  [tes Linux](bukti/linux_tests_22_september.txt), dan
  [restore](bukti/vps_restore_22_september.txt).
- [Browser](bukti/vps_browser_22_september.json),
  [tangkapan layar](bukti/vps_browser_22_september.png), dan
  [uji beban terbatas](bukti/vps_beban_22_september.json).
- [Pengamatan awal](bukti/vps_observasi_awal.json),
  [pengamatan kedua](bukti/vps_observasi_22_september.json),
  [verifikasi layanan dan backup terakhir](bukti/vps_verifikasi_22_september.json),
  [fallback](bukti/vps_failover_22_september.json), dan
  [database pulih](bukti/vps_recovered_22_september.json).
- [Panduan operasi dan rollback](../../deploy/vps/README.md).

Ekspor data, backup, kredensial, private key, dan log host mentah tidak
disertakan dalam Git. Pengembangan berada pada branch
`deploy/vps-uji-20260922`; image aktif `21sep-d76a27388461`, dengan konfigurasi
batas API 320 MiB diterapkan setelah image tersebut dibangun.
