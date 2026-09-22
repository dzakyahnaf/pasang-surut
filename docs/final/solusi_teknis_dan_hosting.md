# Solusi teknis dan pilihan hosting — 20 September 2026

**Pembaruan 21 September:** empat perbaikan sudah diterapkan dan diuji lokal;
lihat [hasil dan bukti pengujian](hasil_21_september.md). Dzaky menolak Render
berbayar. VPS Maknaprice sudah dapat diakses dan diperiksa; API + frontend
statis menjadi opsi uji berikutnya. Belum ada deploy atau migrasi.

Bagian di bawah adalah rancangan historis 20 September. Rekomendasi Render
berbayar dan keterangan “belum memiliki VPS” telah digantikan pembaruan ini.

## 1. Insiden memori dan rekomendasi keputusan

Dzaky melaporkan email Render pukul **17.09 WIB, 20 September**: instance
`pasang-surut-api` melewati batas memori dan otomatis restart. Ini memastikan
insiden kehabisan memori terjadi dan dapat menjelaskan API sementara tidak
menjawab. Belum membuktikan memory leak atau bahwa semua galat sebelumnya
berasal dari insiden yang sama.

Audit sebelumnya menjalankan satu pengujian enam request serentak: tiga
peta dan tiga rute. Pengujian itu mungkin ikut memicu puncak memori; cocokkan
timestamp request/restart dan grafik RAM sebelum menetapkan hubungan sebab.
Pengujian beban produksi dihentikan. Profil berikutnya memakai lokal atau
staging dengan batas sumber daya; smoke test produksi setelah perbaikan
dilakukan secara bertahap.

**Rekomendasi untuk final:** optimasi tetap wajib. Bila anggaran memungkinkan,
naikkan compute layanan Render yang sama ke **1 CPU / 2 GB RAM** untuk masa
persiapan dan final. Ini mengurangi pekerjaan operasional dibanding VPS baru.
RAM 2 GB adalah kapasitas awal yang disarankan, bukan kebutuhan minimum
terukur atau jaminan bebas OOM. Tetap siapkan demo lokal.

Starter/`0.5c-512mb` masih memiliki RAM 512 MB, sama dengan Free; peningkatan
CPU tidak menambah batas memori. Yang dinilai adalah **compute web service**,
bukan upgrade workspace Pro. [Spesifikasi resmi Render](https://render.com/docs/compute-plans).

## 2. Pilihan biaya yang dapat dibandingkan

Harga diperiksa 20 September 2026, menggunakan halaman resmi. Angka tabel
adalah harga tertera, bukan penawaran final dengan pajak, kurs kartu, domain,
backup, dan pemakaian tambahan. Konfirmasi checkout sebelum transaksi.

| Pilihan | CPU / RAM / disk | Harga tertera | Penilaian untuk tim |
|---|---|---|---|
| Render Free sekarang | 0,1 CPU / 512 MB | US$0 | Tetap mungkin untuk prototipe setelah optimasi, tetapi belum layak diasumsikan stabil untuk demo publik setelah insiden ini |
| Render `0.5c-512mb` / Starter | 0,5 CPU / 512 MB | US$7/bulan | Tidak direkomendasikan sebagai solusi penambahan RAM |
| Render `1c-2g` / Standard | 1 CPU / 2 GB | US$25/bulan | Pilihan utama menjelang final: deployment yang sama, kapasitas RAM lebih besar |
| Biznet GIO NEO Lite SS 2.1 | 1 vCPU / 2 GB / SSD 60 GB | Rp80.000/bulan | Opsi VPS ekonomis untuk API saja; perlu pengelolaan server |
| Biznet GIO NEO Lite MS 4.2 | 2 vCPU / 4 GB / SSD 60 GB | Rp139.000/bulan | Pilihan VPS yang saya sarankan jika ingin melanjutkan pengembangan setelah final; ruang RAM lebih longgar |
| DigitalOcean Basic Regular | 1 vCPU / 2 GiB / SSD 50 GiB | US$12/bulan | Alternatif VPS; pilih region Singapore yang tersedia dan periksa ketersediaan paket |

Sumber tabel: [harga Render](https://render.com/pricing),
[NEO Lite](https://www.biznetgio.com/product/neo-lite),
[DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets).
Lokasi DigitalOcean: [daftar region resmi](https://docs.digitalocean.com/platform/regional-availability/).
Harga NEO Lite merupakan angka promosi yang ditampilkan; periksa masa promo,
harga perpanjangan, lokasi, dan pajak pada checkout.

Compute Render ditagih prorata per detik menurut
[FAQ resminya](https://render.com/docs/faq). Sebagai ilustrasi, tepat tujuh
hari pada tarif US$25 per 30 hari sekitar **US$5,83 untuk compute**. Ini
bukan plafon tagihan; durasi nyata dan komponen lain memengaruhi total.
Layanan berbayar yang tetap aktif setelah final terus ditagih. Evaluasi
ulang kapasitas pada 27 September; jangan menganggap akhir lomba otomatis
menghentikan biaya. Tidak perlu berlangganan workspace Pro untuk sekadar
membandingkan opsi compute ini.

Karena belum ada VPS siap pakai, pilihan awal yang paling efisien terhadap
waktu tim adalah **Render 2 GB sementara + optimasi + demo lokal**. Bila
tujuannya biaya bulanan jangka panjang dalam rupiah dan tim siap mengelola
server, **NEO Lite 4 GB** layak menjadi kandidat utama. Jangan memindahkan
backend dan database sekaligus menjelang final.

### Spesifikasi dan pekerjaan bila memilih VPS

- API saja: titik awal 1 vCPU, RAM 2 GB, SSD 25–60 GB; lebih longgar 2 vCPU,
  RAM 4 GB. Tidak perlu GPU. Database tetap Supabase dan frontend tetap Vercel.
- Gunakan arsitektur x86-64 dan OS yang cocok dengan deployment Docker yang
  diuji. Mulai dari satu worker aplikasi agar graf/cache tidak diduplikasi
  ke banyak proses. Ubah jumlah worker hanya setelah pengukuran.
- Penyiapan mencakup image/container, environment rahasia, auto-restart,
  HTTPS, firewall, pembaruan OS, log/monitoring, dan pemulihan versi lama.
- Alamat API harus HTTPS agar dapat dipanggil dari Vercel. Perubahan URL
  memerlukan konfigurasi frontend dan CORS, kemudian pengujian ulang.
- Singapore/Indonesia adalah kandidat region; latensi nyata ke Supabase
  Sydney dan pengguna harus diukur. VPS lebih dekat pengguna belum tentu
  mempercepat query database yang jauh.
- Anggarkan satu blok 4–6 jam kerja untuk setup dan pemeriksaan awal; ini
  estimasi perencanaan, bukan jaminan selesai. Deadline internal keputusan
  21 September, integrasi 22, verifikasi 23. Jika terganggu, pakai jalur
  Render/lokal yang telah diuji.

## 3. T0/T3 — menghentikan lonjakan RAM dan mempercepat interaksi

Temuan kode: perubahan slider dapat memicu peta dan rute berulang; peta
mengirim ulang sekitar 6,6 MB JSON; pembacaan prediksi dan pembuatan objek
respons bertumpuk ketika request serentak. Objek Python, graf, cache potret,
hasil query, dan serialisasi dapat memakai RAM jauh di atas ukuran berkas.
Ini penjelasan yang masuk akal, belum profil alokasi memori yang selesai.

Urutan implementasi:

1. **Kurangi pekerjaan masuk — Daffa.** Gerakan slider memperbarui pratinjau
   jam; commit pilihan pada pelepasan pointer atau debounce sekitar 300 ms
   untuk keyboard/interaksi lain. Peta dan rute memakai satu waktu committed.
   Batalkan fetch lama dengan AbortController dan gunakan ID request agar
   respons lama tidak menimpa pilihan terbaru. Galat dibersihkan setelah
   sukses. Pembatalan browser tidak menjamin tugas server ikut berhenti.
2. **Batasi pekerjaan berat — Dzaky.** Antrean terbatas untuk pembangunan
   peta/rute; mulai satu atau dua pekerjaan berat serentak, kemudian ukur.
   Tolak kelebihan secara terkendali dengan 429/503 dan pesan sibuk yang
   bisa dicoba ulang. Jangan otomatis mengulang berkali-kali dari semua tab.
3. **Pisahkan geometri dan nilai — Daffa + Dzaky.** Muat geometri jalan satu
   kali per versi sebagai aset statis lokal/CDN. Pergantian waktu mengirim
   ID ruas dan kedalaman/status yang berubah. Jangan membentuk ulang seluruh
   geometri pada setiap jam atau menyimpan 72 GeoJSON penuh di RAM.
4. **Bagikan data runtime — Dzaky.** Satu graf dan snapshot prediksi ringkas
   per versi, dibaca sekali dengan penguncian saat pemuatan. Publikasikan
   versi baru secara utuh, batasi cache, dan lepaskan referensi versi lama.
   Hindari penggandaan startup/request pertama dan pembacaan seluruh prediksi
   dari database pada setiap pencarian. Versi/cakupan T2 tetap diperiksa.
5. **Ukur dan putuskan kapasitas — Dzaky.** Catat RAM saat startup, idle,
   pemuatan pertama, pencarian hangat, serta interaksi berulang. Bandingkan
   lokal/staging 512 MB, kemudian 2 GB bila tersedia. Puncak sesaat berbeda
   dari penggunaan yang terus meningkat setelah sejumlah siklus selesai.

Kompresi membantu jaringan, tetapi bukan pengganti pengurangan objek dan
request. Menambah RAM juga tidak mengoreksi bug cakupan waktu atau algoritme.

Kriteria penerimaan yang diusulkan: tidak ada restart dalam uji staging
representatif; puncak RAM di bawah 70% batas instance sebagai ruang cadangan;
tidak ada tren kenaikan RAM yang terus berlangsung setelah pemanasan pada
pengulangan set skenario yang sama; rute hangat p95 ≤2 detik dan perubahan
peta ≤1 detik setelah geometri dimuat. Catat jumlah sampel, perangkat,
jaringan, sumber data, serta concurrency; target ini belum tercapai/terukur.
Gunakan setidaknya 30 interaksi per skenario untuk ringkasan awal, bukan
klaim SLA. Validasi dengan batas RAM Linux/container bila memungkinkan;
RSS Python Windows lokal tidak identik dengan metrik container Render.

Pemanasan H-30 menit dan ping laptop tetap membantu kesiapan, tetapi tidak
mencegah OOM saat request berat. Gunakan endpoint kesehatan untuk penjagaan,
bukan menghitung rute berulang sebagai ping.

## 4. T1 — tombol Cari ulang

`setIndeksJam(i => i)` tidak mengubah state sehingga efek pencarian tidak
berjalan lagi. Ganti dengan fungsi pencarian bersama atau token retry
eksplisit yang menggunakan asal, tujuan, moda, dan jam committed saat ini.
Atur status memuat/sukses/galat melalui jalur yang sama, cegah klik berulang
selama permintaan aktif, dan tangani respons terlambat.

Uji perilaku: permintaan pertama gagal; tanpa mengubah input, klik Cari
ulang menghasilkan request baru dan hasil sukses. Uji juga perubahan titik
saat request berjalan dan galat lama hilang setelah pulih. Tes harus
mengamati permintaan/hasil UI, bukan sekadar perubahan sebuah variabel.

## 5. T2 — tidak ada data bukan berarti kering

Tambahkan metadata dataset yang dipublikasikan bersama hasil: versi,
awal cakupan inklusif, akhir eksklusif, interval waktu, dan jam lengkap
termasuk jam tanpa ruas tergenang. Tabel prediksi bersifat sparse; min/max
baris basah tidak dapat membuktikan seluruh jam tersedia.

Validasi jam permintaan, cakupan evaluasi perjalanan, serta saran waktu
terhadap metadata yang sama. Periksa masa berlaku setiap request walaupun
cache masih tersimpan. Jam di luar rentang mendapat respons terstruktur
(misalnya 422); dataset hilang/basi mendapat 503. UI menampilkan data tidak
tersedia dan menonaktifkan pilihan yang tidak sah. Nilai kedalaman nol
hanya boleh berarti kering setelah jam dinyatakan tercakup dan lengkap.

Uji batas: sebelum jam pertama; tepat jam pertama; menit terakhir dari jam
terakhir; tepat akhir eksklusif; tahun 2099; jam kering lengkap; dataset
kosong; potret kedaluwarsa setelah cache terisi; perjalanan/saran melewati
horizon. Selaraskan skrip HTTP yang sebelumnya menganggap 2099 dengan
respons 200 sebagai keberhasilan.

## 6. T4 — routing saat pergantian jam

Contoh lawan yang sudah direproduksi: hasil 4.046 detik, padahal jalur lain
sah dengan 3.661 detik. Kedatangan lebih awal di simpul antara tidak selalu
memberi kedatangan lebih awal di tujuan bila biaya ruas jatuh mendadak pada
batas jam. Algoritme sekarang menutup simpul setelah label pertama.

**Rekomendasi scope final:** gunakan kondisi pada **jam keberangkatan yang
dipilih** sebagai biaya tetap selama satu pencarian Dijkstra. Saat pengguna
mengganti jam, hitung kembali dengan kondisi jam tersebut. Bobot harus
nonnegatif dan aturan ruas tertutup konsisten. Produk tetap membandingkan
rute dan jam, dengan klaim: “rute terbaik menurut biaya model pada kondisi
jam yang dipilih.”

Ini perubahan model dan batas kemampuan, bukan perbaikan solver dinamis
dengan hasil yang setara. Hasil numerik demo harus dihitung ulang. UI,
slide, dokumentasi, dan estimasi durasi harus menyatakan bahwa perubahan
kondisi di tengah perjalanan belum dimodelkan. Jangan menyebutnya optimal
untuk semua perubahan kondisi sepanjang perjalanan atau menjamin keamanan.
Keputusan ini disetujui Dzaky dan diterapkan 21 September. Bukti dan batas
model akhir ada dalam [hasil implementasi](hasil_21_september.md).

Jika kemampuan sepanjang perjalanan harus dipertahankan, diperlukan pekerjaan
lebih besar: model waktu tempuh yang terbukti FIFO, atau pencarian dengan
state waktu yang mampu mempertahankan alternatif kedatangan. Diskretisasi
waktu membatasi jaminan pada resolusinya; menambah state dapat meningkatkan
RAM. Menunggu di suatu simpul juga harus menjadi asumsi produk eksplisit,
bukan disisipkan seolah pengguna pasti dapat berhenti di ruas tergenang.
Jangan hanya menghapus visited atau menyimpan satu label per simpul-jam lalu
mengklaim persoalan selesai. Dasar algoritmik:
[Dean, Shortest Paths in FIFO Time-Dependent Networks](https://people.computing.clemson.edu/~bcdean/tdsp.pdf).

Uji penerimaan dipisahkan sesuai model:

- Model dinamis lama: pertahankan contoh 4.046 vs 3.661 sebagai bukti cacat;
  bila memperbaiki solver dengan asumsi sama, kasus ini harus menghasilkan
  hasil ≤3.661 detik tanpa memperkenalkan asumsi menunggu diam-diam.
- Model jam keberangkatan tetap: bandingkan hasil dengan enumerasi jalur
  pada graf kecil, dua sisi pergantian jam, ruas tertutup, moda, dan graf
  tak terhubung. Jangan menuntut angka 3.661 dari model yang berbeda.
- Keduanya: uji cakupan data dan hitung ulang skenario demo; hapus klaim
  optimalitas yang lebih luas daripada hasil pengujian dan asumsi model.

## 7. Peta dan metode untuk juri

Daffa menambah nama jalan utama menurut zoom, nama/batas wilayah, garis
pantai, dan penanda tujuan. Gunakan data lokal yang sudah tersedia; 6.518
ruas belum bernama sehingga jangan mengarang nama. Font/glyph dan label harus
tetap tersedia saat demo tanpa jaringan. Uji label tidak bertabrakan dengan
rute/legenda pada layar laptop dan proyektor.

Dzaky dan Naufal menyelaraskan materi dengan implementasi: **median lingkungan
3 × 3 sel grid, tiap sel bersisi 500 m**, bukan radius lingkaran 500 m.
Untuk final, koreksi penjelasan lebih terukur daripada meregenerasi semua
data dengan metode baru. Arsip proposal submission tetap disimpan; buat
lembar koreksi yang jelas. Penurunan simpangan baku elevasi bukan penurunan
RMSE terhadap lapangan. Evaluasi pasut tidak boleh diberi label akurasi
genangan ruas, dan angka dampak simulasi tidak disebut penghematan terukur.
