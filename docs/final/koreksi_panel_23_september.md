# Koreksi panel paparan — 23 September 2026

Saat mengambil screenshot presentasi, dua peringatan dalam aplikasi ternyata
belum konsisten. `PeringatanPaparan` sudah menyebut maksimum pada rute,
sedangkan `PanelRute` masih menempatkan maksimum itu pada `nama_jalan[0]`.
Data respons tidak membuktikan bahwa ruas pertama adalah ruas terdalam.

Panel sekarang memakai kalimat estimasi maksimum **pada rute**, disertai
tanggal/jam WIB yang sama dengan keberangkatan. Algoritme, dataset, dan
kontrak API tidak berubah. Screenshot materi diambil ulang dari aplikasi
setelah koreksi, bukan disunting untuk menyembunyikan pesan lama.

Tes regresi integrasi baru mengisi rute dengan nama jalan pertama dan
kedalaman maksimum, lalu memeriksa kedua panel: keduanya menyebut estimasi
pada rute dan WIB, tanpa mengaitkan kedalaman dengan nama jalan pertama.
Seluruh **26 tes frontend** serta build produksi VPS lulus. Angka 25 pada
laporan 22 September tetap merupakan catatan historis audit saat itu.

Batas cakupan: perubahan ini memperbaiki makna pesan yang telah ditemukan;
tidak berarti audit membuktikan tidak ada bug lain.

**Pemasangan dan pemeriksaan publik:** frontend `panel23-d5f8b721c34c`
dipasang dengan pergantian index atomik dan aset lama dipertahankan untuk
browser yang masih terbuka. Tidak ada restart container atau perubahan
konfigurasi Maknaprice. Identitas/waktu mulai/restart enam container sebelum
dan sesudah pemasangan sama. Browser baru pada `/app` menampilkan kedua
peringatan dengan kalimat, kedalaman, dan WIB identik; canvas peta berisi
gambar dan tidak ada galat JavaScript. Bukti:
[deployment](bukti/panel_23_deployment.json) dan [browser](bukti/panel_23_publik.json).
Branch OSM juga menerima koreksi yang sama, tanpa digabung ke main.
