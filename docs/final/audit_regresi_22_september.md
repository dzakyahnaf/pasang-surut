# Audit regresi final — 22 September 2026

Audit ini melanjutkan uji beban 1.596 request. Fokus tambahan: makna hasil,
data rusak, pergantian versi, jaringan gagal, dependency, dan alur browser.
Pengujian tidak membuktikan bahwa seluruh kemungkinan bug sudah hilang.

## Temuan dan perbaikan

| Temuan | Perbaikan dan bukti |
|---|---|
| NaN/negatif dalam data tersimpan dapat terlihat kering; tuple rusak dapat menjadi 500 | Validasi seluruh nilai, probabilitas, referensi ruas, geometri, dan ambang saat snapshot dimuat. Dataset rusak tidak dilayani sebagai kondisi kering. Fixture lima jenis kerusakan diuji. |
| Graf terputus disebut seluruh jalur tergenang; biaya disebut tidak ada selisih | Bedakan kegagalan konektivitas dari hambatan genangan; `dampak: null` bila dua rute tidak tersedia. |
| Peta, pita waktu, dan hasil rute dapat berasal dari versi berbeda | Rute membawa versi jaringan; frontend menyembunyikan hasil campuran dan menyediakan pemuatan ulang. |
| Permintaan menggantung membuat pencarian tidak selesai | Batas 20 detik mencakup fetch dan pembacaan JSON, dengan pembatalan pengguna tetap dibedakan. Query runtime dibatasi 10 detik dan menunggu lock 3 detik. |
| Body JSON belum dibatasi sebelum parsing | Maksimum 16 KiB, termasuk streaming tanpa Content-Length/ukuran header palsu; pengiriman body maksimum 10 detik. Ini hardening, bukan klaim telah mereproduksi OOM baru. |
| Cache graf abadi meskipun jaringan diganti saat publikasi | Sidik isi tabel diperiksa ketika versi publikasi berubah. Graf tetap dibagi bila isinya sama. Pembaruan besar graf tetap sebaiknya dilakukan dalam jadwal pemeliharaan. |
| Saran jam tidak cocok dengan jam pita atau berada di luar pita | API membulatkan ke jam data; saran di luar pita menjadi informasi tanpa tombol mati. Teks 72 jam dikoreksi menjadi cakupan yang diperiksa, maksimal 24 jam. |
| Peringatan kedalaman maksimum melekat pada nama jalan pertama dan waktu kosong | Sebut maksimum pada rute dan waktu keberangkatan yang sebenarnya; tidak menebak ruas terparah. |
| Tujuan cepat hilang setelah fetch gagal | Galat dan tombol muat ulang tersendiri. |
| Dependency MapLibre memiliki advisory XSS | Naik 5.24.0 → 6.4.1; konfigurasi worker ESM dibundel; pengujian memastikan canvas berisi jalan/label, termasuk build produksi. |
| Browser tanpa WebGL dapat menjatuhkan aplikasi | Pesan kegagalan grafis; tujuan cepat dan panel tetap berfungsi. Diuji pada Edge dengan WebGL dinonaktifkan. |
| Parameter landing dapat menjadi URL `javascript:`/`data:` pada CTA | Batasi HTTP/HTTPS; default `/app` pada origin yang sama. Parameter kosong tidak memutar kembali ke landing. Lima regresi URL. |

Koreksi penjelasan: estimasi emisi memakai faktor pembakaran CO₂, bukan
inventaris CO₂e/daur hidup. API menambah `kg_co2`; `kg_co2e` tetap alias lama
untuk kompatibilitas dan diberi keterangan satuan. Konsumsi/faktor masih
asumsi, bukan pengukuran kendaraan. Elevasi relatif menggunakan median
pada 3 × 3 sel dengan sisi 500 m; bukan radius melingkar 500 m. Log dan
metadata keluaran pipeline baru diselaraskan tanpa menghitung ulang indeks.

Rujukan upgrade: [advisory resmi MapLibre](https://github.com/maplibre/maplibre-gl-js/security/advisories/GHSA-jrc7-96c5-q579)
dan [panduan migrasi v6](https://maplibre.org/maplibre-gl-js/docs/guides/v5-to-v6-migration-guide/).
Jalur attribution HTML yang terdampak tidak dipakai aplikasi ini; pembaruan
dependency tetap dilakukan, bukan klaim ada eksploitasi produksi.

## Cakupan verifikasi

- 95 tes backend Windows dan container Linux; termasuk 2.400 pencarian
  pada 40 graf acak kecil dibanding Bellman-Ford, untuk model kondisi
  tetap pada jam keberangkatan. Ini bukan pembuktian optimalitas dinamis.
- 25 tes frontend, build Vite produksi dan build proxy/landing.
- Uji browser Edge: render jalan/label, dua moda, perubahan jam, pembanding,
  validasi/kembali, layar 360/768/1440, dan keadaan tanpa WebGL.
- Potret: seluruh 19.394 geometri, 72 jam, dan 14.400 baris kondisi diperiksa.
  Preflight image Linux pada DB VPS: 19.394 ruas, 317 jam, 87.427 baris valid;
  transaksi baca saja. Database tidak diubah oleh audit.
- Inventaris sumber, parsing Python/JSON/GeoJSON, pemeriksaan SQL/publikasi,
  deployment, cache, abort/retry, dan kandidat secret pada teks tracked.
  Bukan audit seluruh riwayat Git atau pentest pihak ketiga.
- `npm audit`: nol advisory setelah upgrade. `pip-audit`: nol kerentanan
  dikenal pada resolusi requirements runtime maupun pipeline saat audit.
  Ini bukan jaminan tidak ada kerentanan yang belum dipublikasikan.
- Uji VPS tambahan memakai guard RAM host/container dan probe Maknaprice;
  hasil serta telemetri disimpan terpisah dari uji beban sebelumnya.

Bukti berada di [folder bukti](bukti/): `audit_*22*`, `audit_22_*`, dan
`linux_audit_tests_22.txt`. Skrip audit dapat dijalankan ulang di
`deploy/vps/audit_statis.py`, `uji_regresi_vps.py`, serta `uji_regresi_browser.py`.

## Email Vercel

Preview commit `8d74b2f` gagal. Script build menyalin `dashboard/`, sementara
folder tersebut belum ada di tree commit. Commit `97d8408` menambah folder;
PR #4 digabung menjadi `4336afe`, dan status deployment produksi berhasil.
Ini diagnosis dari tree/diff dan status deployment; log rinci Vercel tidak
diakses karena CLI belum login. Landing `/` dan aplikasi `/app` dipertahankan.

## Hasil publik setelah pemasangan

API `audit22-11c58776b1ca` dan frontend `audit-c3c753c59f8d` dipasang pada
22 September sekitar 23.26 WIB. Uji 412 request selama 94,47 detik menghasilkan
316 HTTP 200, 58 HTTP 413, empat HTTP 422, dua HTTP 400, dan 32 HTTP 503 sibuk
yang memang diharapkan. Tidak ada galat tak terduga, OOM, peningkatan failcnt,
atau restart selama pengujian. Recreate API saat deployment dilakukan sebelum
baseline pengujian, bukan dihitung sebagai restart akibat beban.

Puncak sampel memori API 186,89/320 MiB, DB 93,20/192 MiB, web 51,71/64 MiB;
RAM host tersedia minimum 645,92 MiB. Sampel ini tidak menggantikan hasil
soak panjang sebelumnya. Sepuluh probe Maknaprice seluruhnya HTTP 200;
identitas container dan hash konfigurasi tetap sama. Browser pada
`https://pasang-surut.vercel.app/app` lulus termasuk pemeriksaan canvas,
responsif dan kegagalan WebGL. Backend tetap memakai versi data yang sama.

## Batas yang tetap harus dijelaskan kepada juri

Indeks kerentanan bukan model genangan tervalidasi per ruas. Akurasi pasut
bukan akurasi genangan. Kondisi selama perjalanan belum dimodelkan.
Biaya BBM/CO₂ merupakan ilustrasi asumsi, bukan dampak lapangan terukur.
Data produksi berakhir 5 Oktober 07.00 WIB; potret berakhir 29 September
00.00 WIB. Tidak ada scheduler publikasi data otomatis.

Origin sementara masih HTTP 18080 sesuai izin pengguna. Uji kapasitas ini
dibatasi agar Maknaprice tetap aman, bukan uji DDoS atau kapasitas maksimum.
Peringatan ukuran bundle Vite dan deprecation API testing masih ada; tidak
menggagalkan build/tes. Belum diuji pada seluruh perangkat/browser pengguna.

## Lanjut materi final

TM 22 September selesai; durasi tetap 10 menit presentasi dan 15 menit
tanya jawab. Tim tampil **pertama**. Deadline PDF belum diumumkan, bukan
berarti PDF boleh diserahkan kapan saja. Konfirmasi deadline tetap tugas tim.

Setelah pemeriksaan publik lulus, bekukan perubahan fitur dan gunakan
[outline delapan slide](outline_slide.md). Siapkan PPTX, PDF, MP4 lokal,
tiga screenshot cadangan, serta latihan 9 menit. Perangkat/proyektor,
audio bila dipakai, dan pergantian ke demo lokal tetap harus diuji tim.

Proposal submission dipertahankan. Koreksi audit dibuat sebagai
[addendum terpisah](Addendum_audit_22_september.docx), satu halaman menurut
`ComputeStatistics` Microsoft Word pada 22 September 2026.
