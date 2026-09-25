# Peta OSM dipilih untuk final, 26 September 2026

Dzaky menyampaikan persetujuan tim untuk memakai tampilan OSM/CARTO dari
branch `preview/peta-dasar-osm`, menggabungkannya ke main dan menghapus branch.
Peta tersedia di [aplikasi publik](https://pasang-surut.vercel.app/app).
Landing Daffa tetap pada `/`; konfigurasi Vercel khusus pratinjau tidak
dibawa ke produksi. Kata "Pratinjau" pada status peta dihapus.

## Apa yang berubah

Basemap CARTO Voyager berbasis OSM menampilkan daratan, perairan, hierarki
jalan, nama kawasan dan tempat. Genangan dan rute masih menggunakan API
PASANG SURUT. Empat tujuan cepat, pola kedalaman, pilihan moda dan Pita
Pasut tetap bekerja. Atribusi OSM/CARTO terlihat dan dapat diklik.

Garis dasar serta sebagian label lokal disembunyikan saat CARTO aktif agar
tidak bertumpuk. Jika pemuatan awal penyedia belum selesai dalam 10 detik,
peta lokal menjadi cadangan. Gambar cadangan memerlukan waktu render setelah
status berganti; pengujian menunggu sampai label dan rute terlihat.

## Hasil pemeriksaan

- 26 tes frontend lulus, build VPS dan build proxy landing berhasil.
- Build produksi diperiksa di browser: rute Tawang-Terboyo pada 26 September
  08.00/13.00, motor/mobil, Cari ulang, atribusi, serta viewport 390×844.
  Tidak ada galat JavaScript atau overflow horizontal ponsel.
- Hasil lokal, geometri rute, dampak dan versi data sama dengan potret deck.
  Data produksi memakai versi berbeda, sehingga tidak diklaim identik dengan
  potret. Alur yang sama juga berhasil pada URL publik.
- CARTO diblokir pada browser lokal: peta cadangan, label dan rute berhasil
  dirender. Tidak dilakukan uji beban produksi tambahan untuk perubahan ini.
- Aset terbit sebagai `osm26-5f46ace4929e`: backup sebelum perubahan,
  aset lama dipertahankan, index diganti atomik. Tidak ada restart container;
  identitas/waktu mulai/jumlah restart keenam container tetap sama.
  Maknaprice HTTP 200 sebelum dan sesudah, tanpa perubahan layanan tersebut.
- Service worker menjadi `pasang-surut-v4-osm`; cache API tetap dilarang.
  HTML dan bundle publik dicocokkan dengan build. Isi landing cocok dengan
  sumber setelah normalisasi akhir baris Windows/Linux.

Bukti: [browser lokal](bukti/osm_final_26_lokal.json),
[browser publik](bukti/osm_final_26_publik.json),
[deployment](bukti/osm_final_26_deployment.json),
[hash publik](bukti/osm_final_26_http.json),
[desktop publik](bukti/osm_final_26_publik_desktop.png),
[ponsel publik](bukti/osm_final_26_publik_mobile.png), dan
[cadangan lokal](bukti/osm_final_26_lokal_cadangan.png).

## Catatan untuk tim

Jika tab lama masih memperlihatkan peta sebelumnya, muat ulang dengan
`Ctrl+Shift+R`. Basemap perlu internet; demo potret beserta peta cadangan
tetap tersedia. Nama kawasan dari basemap tidak menambah cakupan analisis
genangan atau membuktikan kedalaman ruas. Label tempat juga bukan tambahan
fitur pencarian alamat.

Screenshot PPT 25 September dan video pameran tetap memakai peta sebelumnya.
Angka skenario dan catatan metode tetap berlaku; screenshot dapat dipakai
sebagai cadangan lokal. Berkas PPT/video tidak diganti pada pekerjaan merge
ini. Keputusan basemap sudah selesai, bukan lagi butir yang menunggu tim.

[Dokumentasi CARTO](https://docs.carto.com/faqs/carto-basemaps) diperiksa pada
26 September: vector tetap tidak terdampak watermark raster; penyedia
merekomendasikan API key untuk kesiapan perubahan layanan di masa depan.
Tidak ada akun atau langganan baru dibuat. Atribusi tetap ditampilkan.

Rollback frontend menggunakan backup
`/opt/pasang-surut/backups/frontend-before-osm26-5f46ace4929e.tar.gz` pada
direktori PASANG SURUT, dengan aset lama dipertahankan dan pergantian index
atomik. Tidak perlu mengubah database, API, atau layanan lain.
