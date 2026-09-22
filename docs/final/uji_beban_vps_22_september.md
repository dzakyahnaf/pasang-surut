# Uji beban VPS dan masukan ekstrem — 22 September 2026

**VPS lulus skenario terukur setelah dua perbaikan validasi dan tambahan
16 MiB untuk container web PASANG SURUT.** Tampilan main, data produksi,
serta layanan Maknaprice dipertahankan. API aktif `22sep-89cc5e755a12`.

## Temuan yang diperbaiki

1. Koordinat string `NaN` menghasilkan rute yang tidak sah; `Infinity`
   menghasilkan HTTP 500. Koordinat sekarang harus berhingga dan berada
   pada rentang geografis. Galat validasi tidak memantulkan input NaN/Inf
   ke JSON, sehingga konstanta JSON nonstandar juga ditolak rapi dengan 422.
2. Konversi `0001-01-01T00:00:00+14:00` melampaui batas kalender Python
   dan menghasilkan 500. Konversi zona waktu yang overflow sekarang 400.
   Batas tahun 9999 dan kedua endpoint GET/POST ikut diperiksa.
3. Uji pertama dihentikan guard saat memori container web mencapai 45,66
   MiB dari 48 MiB. Nilai mencakup cache, bukan hanya heap/RSS; **belum OOM**.
   Batas web dinaikkan menjadi 64 MiB, tanpa restart web. Batas API tetap
   320 MiB, database tetap 192 MiB. Compose VPS ikut diperbarui.

API dibuat ulang secara sengaja untuk kedua rilis perbaikan; probe selama
pergantian sempat mendapat 502 lalu pulih dalam hitungan detik. Klaim
tanpa restart di bawah berlaku **selama uji akhir**, sesudah deployment.

## Skenario dan hasil akhir

Jendela utama **16.17.21–16.25.02 WIB**, 460,91 detik; 913 sampel memori
setengah detik. Pengirim request berjalan di laptop, melalui origin HTTP
publik, dengan satu fase tambahan melalui HTTPS Vercel. Tidak ada load
generator yang berjalan di VPS atau menyasar Maknaprice.

| Pemeriksaan | Hasil |
|---|---|
| Request lengkap pada harness akhir | **1.596**, tidak ada respons tak terduga |
| Respons sibuk terkendali | **112** HTTP 503, kode `server_sibuk`, `Retry-After: 1` |
| Lonjakan kondisi peta | Hingga **32 serentak**, semuanya 200 |
| Lonjakan rute 32 serentak | **2 berhasil, 30 ditolak sibuk**; bukan kapasitas melayani 32 perhitungan bersamaan |
| Pola ruas besar berulang, 45 detik | **90 request**, 89 berhasil, 1 sibuk |
| Campuran slider/rute/jam, 300 detik | **1.160 request**, seluruhnya 200; p95 campuran **1.015 ms** |
| Pembatalan unduhan | 12 unduhan dihentikan klien, lalu 3 pencarian rute berhasil |
| Puncak memori API dari cgroup | **233,51 / 320 MiB**; peak sampel 230,49 MiB |
| Puncak sampel DB / web | **97,05 / 192 MiB** dan **49,13 / 64 MiB** |
| RAM host tersedia minimum | **583,85 MiB** |
| OOM / restart / penambahan failcnt | **Tidak ada** selama uji akhir |
| Maknaprice | **46/46 HTTP 200**, p95 139,44 ms; identitas container dan hash konfigurasi tetap |

Puncak cgroup merupakan puncak sepanjang umur container. API baru dibuat
sebelum uji; puncak DB 103,46 MiB berasal dari riwayat sebelum uji, sehingga
tabel memakai peak sampel DB. Swap host maksimum 228 MiB; selama jendela
uji ada 439 page masuk dan 700 page keluar. Tidak diklaim bebas swap.

85 request kasus tepi mencakup semua 12 pasangan berarah dari empat tujuan
cepat, dua moda, jam paling basah/kering, awal/akhir cakupan, waktu 2099,
titik jauh dari jalan, koordinat salah, moda tak dikenal, overflow waktu,
keberangkatan ±1 detik di pergantian jam, serta perjalanan melampaui akhir
data. 400/422 pada masukan yang memang salah adalah hasil yang diharapkan.

Enam GET ruas pada log Render diuji dengan tanggal aslinya: lima sekarang
di luar cakupan dan ditolak 422, satu masih berada dalam cakupan dan 200.
Reproduksi beban alokasi menggunakan pola yang sama pada jam valid saat ini.
Log Render tidak menyimpan badan POST rute atau seluruh request in-flight;
ini **reproduksi pola**, bukan rekonstruksi persis penyebab OOM Render.

## Pemeriksaan fungsi dan browser

- **80 tes backend** lulus di Windows dan container Linux, termasuk 23 tes
  tambahan masukan ekstrem; **12 tes frontend** lulus.
- **35 pemeriksaan HTTP** melalui Vercel lulus, tanpa catatan gagal.
- Browser Edge produksi: retry rute setelah 503 simulasi; retry data
  setelah 503 simulasi; motor/mobil; seluruh tombol tujuan cepat; hapus dan
  ganti titik; tampil/sembunyikan pembanding; validasi dan kembali; Home,
  End, Page Up/Down pada slider. **40 perpindahan cepat menghasilkan satu
  request rute**. Pergeseran jam tidak mengunduh ulang geometri.
- Layar 360, 768, dan 1440 piksel diperiksa; tidak ada overflow horizontal
  atau galat JavaScript, atribusi terlihat. Ini emulasi browser desktop,
  bukan pengganti gladi di telepon/proyektor venue.

Guard menghentikan beban bila RAM tersedia <400 MiB, pemakaian salah satu
container mencapai 95% batas, failcnt bertambah, identitas/state berubah,
probe Maknaprice gagal dua kali, atau telemetri putus. Hanya PASANG SURUT
yang dituju. Pengujian ini bukan uji DDoS, kapasitas tanpa batas, atau bukti
tidak ada memory leak untuk semua durasi/pola trafik. Beban ditolak dengan
503 saat kapasitas penuh; tombol Cari ulang tetap dibutuhkan.

## Peta dan dependensi

OSM menyediakan data nama jalan, kawasan, dan tempat. MapLibre adalah
renderer; label tidak muncul otomatis dari GeoJSON jalan tanpa layer teks
atau basemap. Layanan siap pakai sah digunakan. Keputusan lokal sebelumnya
adalah pilihan implementasi mengikuti jalur demo offline, bukan keterbatasan
OSM atau larangan pengguna memakai layanan luar.

Main mempertahankan label jalan, tujuh kecamatan dan empat tujuan utama.
Atas permintaan Dzaky, branch `preview/peta-dasar-osm` menyediakan perbandingan
basemap OSM/CARTO dan **tidak digabung ke main**. Label lokal main sudah aktif,
tetapi bukan katalog lengkap semua tempat OSM.

`npm audit` menemukan advisory MapLibre 5.24.0
[GHSA-jrc7-96c5-q579](https://github.com/maplibre/maplibre-gl-js/security/advisories/GHSA-jrc7-96c5-q579).
Jalur yang terdampak ialah HTML attribution tidak tepercaya. Aplikasi saat
ini menonaktifkan `AttributionControl` dan merender atribusi statis melalui
React; tidak ada `Popup.setHTML`. Jalur tersebut tidak dipakai dalam dua
tampilan ini. Temuan dependensi tetap dicatat terbuka; upgrade mayor ke
versi patched memerlukan uji kompatibilitas terpisah. Jangan mengaktifkan
HTML attribution dari penyedia pada versi ini. Uji beban bukan audit
keamanan menyeluruh.

## Bukti

- [Ringkasan mesin](bukti/vps_stress_22_ringkasan.json),
  [seluruh request](bukti/vps_stress_22_lulus_requests.json),
  [telemetri](bukti/vps_stress_22_lulus_monitor.jsonl).
- [Verifikasi isolasi dan source API](bukti/vps_stress_22_verifikasi.json).
- [Bug NaN sebelum perbaikan](bukti/vps_stress_22_awal_requests.json) dan
  [uji yang dihentikan oleh batas web 48 MiB](bukti/vps_stress_22_final_requests.json).
- [Tes Linux](bukti/linux_stress_tests_22.txt),
  [HTTP publik](bukti/http_fitur_22_stress.txt),
  [fitur browser](bukti/fitur_browser_22.json),
  [retry dan geometri browser](bukti/vercel_browser_stress_22.json).

Script `deploy/vps/pantau_beban.py` hanya membaca metrik host.
`deploy/vps/uji_beban.py` memerlukan stop event yang dihubungkan ke output
monitor; jangan menjalankannya tanpa pengawasan telemetri. SSH/key lokal
dan skrip penghubung sesi tidak dipublikasikan.
