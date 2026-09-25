# Peta dasar OSM pilihan final

Pada **26 September 2026**, Dzaky menyampaikan persetujuan tim untuk memakai
tampilan OSM/CARTO dan meminta branch digabung ke main lalu dihapus.
Peta ini menjadi tampilan aplikasi di `/app`; landing tetap di `/`.
Riwayat perbandingan dan screenshot 22-23 September dipertahankan di bawah.

Basemap siap pakai: [CARTO Voyager](https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json),
berbasis OpenStreetMap. Gambar jalan, perairan, bangunan, nama kawasan dan
POI berasal dari penyedia. Lebih banyak label muncul saat diperbesar;
kelengkapan tetap tergantung pemetaan OSM dan pemilihan label oleh gaya.
Tidak semua objek OSM dijamin tampil.

Contoh: [tampilan kota](bukti/osm_pratinjau_desktop_final.png),
[detail jalan/tempat](bukti/osm_pratinjau_detail_final.png),
[ponsel](bukti/osm_pratinjau_mobile_final.png),
dan [rute pada jam basah](bukti/osm_pratinjau_rute.png).

Overlay genangan, pola kedalaman, rute, titik berangkat/tujuan, API, dan
database tetap milik PASANG SURUT. Empat penanda akses tujuan cepat tetap
interaktif. Nama akses pada panel tetap merujuk data routing tersimpan.
Basemap tidak menambah cakupan prediksi atau validasi model genangan.

## Melihat dari laptop

Di direktori `frontend` pada main:

```powershell
npm ci
npm run preview:osm
```

Buka `http://127.0.0.1:5175`. API diproksi ke VPS yang sama dengan main.
Bandingkan dengan `https://pasang-surut.vercel.app/app` pada lokasi/jam yang sama.
Basemap diambil langsung browser dari CARTO; tidak disimpan di API/VPS.
Tidak ada unduhan massal atau prefetch wilayah. Bila pemuatan awal basemap
gagal selama 10 detik, peta lokal aktif dengan status yang terlihat.

Konfigurasi Vercel khusus pratinjau telah dikembalikan ke konfigurasi main:
landing di `/`, aplikasi dan API dari VPS di `/app` serta `/api`.
Perubahan UI dibangun dengan `npm run build:vps` dan aset dipasang ke VPS;
push Git saja tidak mengganti frontend yang disajikan VPS.

## Penyedia dan batas pratinjau

[Dokumentasi CARTO](https://docs.carto.com/faqs/carto-basemaps) yang diperiksa
22 September 2026 menyebut vector basemap belum mewajibkan key, tetapi
merekomendasikan key untuk penggunaan selanjutnya. Raster sudah memerlukan
key. Pratinjau ini menggunakan vector, bukan menghindari watermark raster.
Atribusi OpenStreetMap dan CARTO ditampilkan sebagai tautan. Internet tetap
dibutuhkan untuk basemap serta API produksi. Tidak ada langganan berbayar
atau pendaftaran akun yang dibuat.

Renderer pada main maupun branch ini sudah MapLibre 6.4.1, dengan worker
modul dibundel oleh Vite. `npm audit` pada 22 September tidak menemukan
advisory yang diketahui. Atribusi OpenStreetMap dan CARTO tetap berupa
tautan React statis. Perbaikan regresi dari main disertakan pada branch
ini; pilihan basemap sudah disetujui untuk main. Jika internet ke penyedia
terputus sebelum peta selesai dimuat, tampilan lokal cadangan tetap tersedia.
