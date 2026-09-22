# Pratinjau peta dasar OSM

Branch `preview/peta-dasar-osm` khusus perbandingan visual, **jangan merge
ke main tanpa keputusan Dzaky**. Main mempertahankan peta lokal berlabel.

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

Di direktori `frontend` pada branch ini:

```powershell
npm ci
npm run preview:osm
```

Buka `http://127.0.0.1:5175`. API diproksi ke VPS yang sama dengan main.
Bandingkan dengan `https://pasang-surut.vercel.app` pada lokasi/jam yang sama.
Basemap diambil langsung browser dari CARTO; tidak disimpan di API/VPS.
Tidak ada unduhan massal atau prefetch wilayah. Bila pemuatan awal basemap
gagal selama 10 detik, peta lokal aktif dengan status yang terlihat.

Vercel pada branch ini membangun frontend asli dan hanya memproksi `/api`.
Konfigurasi produksi main tetap memproksi seluruh frontend ke VPS.
Preview Vercel dapat meminta login sesuai perlindungan proyek yang berlaku.

## Penyedia dan batas pratinjau

[Dokumentasi CARTO](https://docs.carto.com/faqs/carto-basemaps) yang diperiksa
22 September 2026 menyebut vector basemap belum mewajibkan key, tetapi
merekomendasikan key untuk penggunaan selanjutnya. Raster sudah memerlukan
key. Pratinjau ini menggunakan vector, bukan menghindari watermark raster.
Atribusi OpenStreetMap dan CARTO ditampilkan sebagai tautan. Internet tetap
dibutuhkan untuk basemap serta API produksi. Tidak ada langganan berbayar
atau pendaftaran akun yang dibuat.

Renderer pada main maupun branch ini masih MapLibre 5.24.0. Audit npm
mencatat GHSA-jrc7-96c5-q579 pada HTML attribution. `AttributionControl`
dimatikan; atribusi ditulis sebagai tautan React statis, bukan HTML dari
style penyedia. Jangan mengaktifkan jalur HTML tersebut sebelum upgrade
ke versi patched dan uji kompatibilitas. Ini pratinjau visual, bukan
pernyataan bahwa seluruh audit dependensi telah bersih.
