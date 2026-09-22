# Publikasi VPS dan label peta — 22 September 2026

Dzaky mengizinkan pembukaan origin HTTP 18080 sementara selama final,
pengujian publik, lalu pengalihan Vercel bila lulus. Commit perbaikan
`3cf1a37` sudah dipush, kemudian implementasi label dan pengalihan masuk
`main`. **Produksi aktif di `https://pasang-surut.vercel.app`, dengan
frontend, API, dan database dilayani VPS.** Vercel tetap menjadi pintu masuk
HTTPS. CI dan uji browser produksi lulus; Maknaprice tidak diubah.

OSM adalah sumber data, MapLibre adalah renderer. Nama jalan sudah ada pada
atribut data, tetapi gaya khusus aplikasi sebelumnya belum memiliki layer
symbol/teks. Basemap siap pakai bisa membawa label, namun aplikasi ini
mempertahankan data dan font lokal untuk demo tanpa ketergantungan ubin luar.
Implementasi memakai fitur label bawaan MapLibre, bukan renderer peta baru.

## Label yang ditambahkan

- Nama jalan mengikuti geometri. Ruas senama yang tersambung digabung hanya
  untuk menggambar label; duplikat arah dibuang. Graf routing tidak berubah.
  Jalan utama tersedia mulai zoom 10,5 bila muat; jalan lokal mulai 14,5.
- Tujuh nama kecamatan dari polygon OSM yang memotong AOI, batas indikatif
  putus-putus, dan garis pantai. Tidak ada perubahan AOI atau data sumber.
- Empat tempat penting memakai koordinat OSM asli. Mengetuk tempat memilih
  simpul akses jalan yang sama dengan tombol tujuan cepat.
- Panel menampilkan “Akses …” untuk tujuan cepat, “Dekat …” untuk jalan
  berjarak paling jauh 80 meter, dan keterangan jujur untuk ruas tanpa nama.
  Koordinat tetap tersedia; nama jalan lain tidak dipinjam untuk ruas kosong.
- Label memakai Barlow yang sudah dibundel dan renderer TinySDF MapLibre;
  tidak ada ketergantungan server font, ubin, atau geocoding eksternal.
- Atribusi OSM tetap terlihat pada layar 360px. Service worker naik ke v3
  untuk membersihkan cache cangkang lama saat migrasi.

Data konteks berukuran 22.984 byte (25 fitur), diturunkan oleh
`backend/scripts/30_konteks_peta.py` dari berkas kecamatan, pantai, tujuan
cepat, dan AOI yang sudah tersimpan. Manifest SHA-256 sumber ikut disimpan.
Script tidak mengakses layanan eksternal atau menulis database.

## Bukti sebelum pengalihan Vercel

12 tes frontend dan build produksi lulus. Browser development memverifikasi
label jalan utama, jalan lokal saat diperbesar, kecamatan, tempat, serta klik
tempat yang memilih akses jalan. Tidak ada galat atau request browser ke
domain luar. Uji produksi di origin publik juga lulus: retry setelah galat,
slider, satu unduhan geometri tanpa unduhan ulang, nama asal–tujuan, dan
layar 360px tanpa overflow horizontal. 35 pemeriksaan HTTP origin lulus.

Origin sudah terbuka pada `http://38.103.171.82:18080`. Frontend dengan label
aktif di VPS, rilis aset `label-a29a25013940`. Aset lama dipertahankan dan
backup frontend dibuat sebelum pergantian index secara atomik. API dan
database tidak dibuat ulang; tidak ada perubahan Maknaprice.

Konfigurasi Vercel menjadi proxy semua request ke origin
VPS. Cache API dinonaktifkan. Jalur pengguna–Vercel memakai HTTPS; jalur
Vercel–VPS memakai HTTP sesuai izin sementara.

## Hasil produksi

Preview berhasil dibangun, tetapi dilindungi login Vercel sehingga uji
browser preview tidak dapat dilakukan tanpa autentikasi. Sesudah uji origin
publik lulus, produksi dialihkan sesuai izin Dzaky. Pemeriksaan awal
menemukan `/` 404 meskipun `/index.html` dan API 200. Aturan root eksplisit
ke `/index.html` ditambahkan pada `e6a7348`; halaman utama kemudian 200.
Gangguan root singkat tersebut diperbaiki sebelum pengujian alur dinyatakan
lulus. Deployment produksi perbaikan tercatat sukses.

Browser pada alamat produksi HTTPS lulus: retry setelah 503 yang disimulasikan
di klien, slider menuju jam dengan 1.367 ruas basah, satu unduhan geometri,
nama akses asal–tujuan, serta tampilan 360px tanpa overflow horizontal dan
dengan atribusi OSM terlihat. Tidak ada galat JavaScript/MapLibre atau
permintaan browser ke domain lain. Uji desktop sudah memeriksa label jalan,
wilayah, tempat, dan jalan lokal saat diperbesar. Collision renderer bisa
menyembunyikan label yang tidak muat; nama jalan lebih banyak saat zoom naik.

Pengukuran dari laptop melalui **HTTPS Vercel → HTTP VPS**, tiga sampel jam
berurutan pada rute Tawang–Terboyo:

| Pengukuran | Hasil |
|---|---:|
| Rute | **266–857 ms** |
| Kondisi per jam | **209–292 ms** |
| Geometri sekali muat, tanpa gzip pada klien ukur | **2,35 detik**, 4.464.454 byte |

Ketiga sampel API HTTP 200, `Cache-Control: no-store`, cache Vercel MISS,
dan memakai database VPS. Angka ini sampel lapangan kecil, bukan p95 atau
jaminan latensi. Audit lama mencatat rute 5,8–6,8 detik dan ruas 10,9 detik;
hasil baru lebih cepat pada pengukuran ini, tetapi bukan eksperimen kontrol
dengan jaringan, endpoint, dan jam identik. Browser sekarang mengunduh
geometri sekali, lalu payload kondisi jauh lebih kecil saat waktu berubah.

Pemeriksaan host setelah publikasi: API sekitar 179 MiB dari batas 320 MiB,
DB 54 MiB, web 23 MiB, RAM tersedia sekitar 653 MiB. API/DB tanpa OOM atau
restart otomatis. Container web PASANG SURUT sengaja dibuat ulang untuk
membuka bind publik; seluruh identitas/waktu mulai container dan hash
konfigurasi Caddy Maknaprice tetap sama. Maknaprice HTTP 200.

Workflow `Jaga hidup` diarahkan ke `/api/kesehatan` pada alamat Vercel dan
memeriksa database, data tersedia, serta masa berlaku. Jadwal GitHub tetap
tidak dijamin tepat waktu; bukan pengganti pemeriksaan sebelum tampil.
[Run manual setelah migrasi berhasil](https://github.com/dzakyahnaf/pasang-surut/actions/runs/35704919417).
Render dan Supabase lama belum dihapus. Push `main` juga dapat memicu
integrasi deployment Render yang masih terpasang; jalur pengguna sekarang
sudah menuju VPS.

## Pemulihan dan tindak lanjut

Simpan demo laptop dan backup. Cakupan database berakhir 5 Oktober 07.00 WIB
(eksklusif), potret cadangan berakhir 29 September 00.00 WIB. Pembaruan data
tetap pekerjaan terpisah dan tidak boleh dilakukan hanya dengan mengganti
tanggal metadata. Sesudah final, tinjau penutupan port HTTP sementara atau
ganti origin dengan HTTPS sebelum melepas ketergantungan routing padanya.

Untuk rollback frontend label, gunakan arsip
`/opt/pasang-surut/backups/frontend-before-label-a29a25013940.tar.gz` dan
pulihkan index terakhir setelah aset tersedia. Untuk memulihkan jalur
Vercel/Render lama, pulihkan deployment sebelum `c6b7192` atau konfigurasi
Vite lama beserta frontend yang kompatibel. Mengganti rewrite saja sambil
tetap membangun `dist-proxy` tidak menghasilkan frontend lama.

Perbandingan implementasi lengkap:
[790a294 → e6a7348](https://github.com/dzakyahnaf/pasang-surut/compare/790a294...e6a7348).
Implementasi sudah berada di `main` sebelum permintaan PR lanjutan; PR
penutupan menyimpan bukti produksi dan memperbarui status operasional.

## Sumber dan bukti

- [Label dan klik tempat](bukti/label_peta_22_september.json),
  [desktop](bukti/label_peta_desktop.png),
  [detail jalan](bukti/label_peta_detail.png).
- [Browser origin publik](bukti/origin_label_browser_22_september.json),
  [tampilan 360px](bukti/origin_label_browser_22_september_mobile.png),
  [respons origin](bukti/origin_publik_22_september.json).
- [Browser Vercel produksi](bukti/vercel_browser_22_september.json),
  [desktop produksi](bukti/vercel_browser_22_september.png),
  [ponsel produksi](bukti/vercel_browser_22_september_mobile.png),
  [latensi Vercel](bukti/vercel_kinerja_22_september.json), dan
  [verifikasi isolasi setelah publikasi](bukti/vps_verifikasi_publik_22_september.json).
- [Panduan glyph MapLibre](https://maplibre.org/maplibre-style-spec/glyphs/)
  dan [rewrite Vercel](https://vercel.com/docs/routing/rewrites).

Tetap ingat batas produk: indeks kerentanan ruas belum mempunyai validasi
akurasi genangan per ruas, dan routing memakai kondisi jam keberangkatan
sepanjang satu pencarian. Label lokasi tidak mengubah batas klaim tersebut.
