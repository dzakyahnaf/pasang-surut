# Publikasi VPS dan label peta — 22 September 2026

Dzaky mengizinkan pembukaan origin HTTP 18080 sementara selama final,
pengujian publik, lalu pengalihan Vercel bila lulus. Commit perbaikan
`3cf1a37` sudah dipush ke branch `deploy/vps-uji-20260922`; CI lulus.
Alamat masuk yang dipertahankan: `https://pasang-surut.vercel.app`.

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

Konfigurasi Vercel pada branch ini menjadi proxy semua request ke origin
VPS. Cache API dinonaktifkan. Jalur pengguna–Vercel memakai HTTPS; jalur
Vercel–VPS memakai HTTP sesuai izin sementara. Pengalihan produksi dilakukan
sesudah preview diuji; hasil tahap itu dicatat setelah selesai.

## Sumber dan bukti

- [Label dan klik tempat](bukti/label_peta_22_september.json),
  [desktop](bukti/label_peta_desktop.png),
  [detail jalan](bukti/label_peta_detail.png).
- [Browser origin publik](bukti/origin_label_browser_22_september.json),
  [tampilan 360px](bukti/origin_label_browser_22_september_mobile.png),
  [respons origin](bukti/origin_publik_22_september.json).
- [Panduan glyph MapLibre](https://maplibre.org/maplibre-style-spec/glyphs/)
  dan [rewrite Vercel](https://vercel.com/docs/routing/rewrites).

Tetap ingat batas produk: indeks kerentanan ruas belum mempunyai validasi
akurasi genangan per ruas, dan routing memakai kondisi jam keberangkatan
sepanjang satu pencarian. Label lokasi tidak mengubah batas klaim tersebut.
