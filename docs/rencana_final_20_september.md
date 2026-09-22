# Rencana final PASANG SURUT — audit 20 September 2026

Dokumen kerja untuk final 26 September. Disusun dari pemeriksaan repositori,
rulebook, proposal yang ditunjuk tim, layanan produksi, dan klarifikasi Dzaky.
**Pembaruan 21 September:** empat perbaikan telah diterapkan dan diuji lokal.
Lihat [hasil implementasi dan pemeriksaan VPS](final/hasil_21_september.md)
untuk status terkini; detail audit 20 September di bawah adalah dasar rencana.
Versi publik belum diperbarui.

Paket kerja hari pertama sudah diuraikan menjadi
[pembagian tugas dan inventaris](final/paket_20_september.md),
[rancangan perbaikan dan hosting](final/solusi_teknis_dan_hosting.md), serta
[outline slide sembilan menit](final/outline_slide.md). Pembaruan terbaru
memasukkan notifikasi OOM Render pukul 17.09 WIB yang dilaporkan Dzaky.

## 1. Keputusan dan ketentuan yang sudah pasti

- **Kehadiran sudah dikonfirmasi dan diterima panitia; ketiga anggota hadir.**
  Dikonfirmasi Dzaky pada sesi ini. Administrasi kehadiran bukan blocker lagi.
- Technical Meeting wajib **22 September**, final offline di Undip
  **26 September**. Belum ada pengumuman terbaru menurut Dzaky.
- **PDF wajib dikumpulkan ke panitia**, berdasarkan jawaban langsung panitia
  atas pertanyaan Dzaky. Ini informasi tambahan panitia, bukan pasal rulebook.
  Tenggat, kanal pengiriman, penamaan, dan batas revisinya belum diketahui.
- Hosting aktif **Vercel + Render + Supabase**. Tim tetap memprioritaskan
  optimasi aplikasi, demo lokal, membuka produksi 30 menit sebelum tampil,
  dan ping dari laptop. **Keputusan terbaru: Render berbayar ditolak.**
  VPS Maknaprice sudah diperiksa; API yang dioptimalkan dan frontend statis
  layak diuji di sana, dengan potret sebagai kandidat runtime final.
  Belum ada pembelian, deploy, atau migrasi database. Rancangan penerapan dan
  batas kapasitas ada dalam hasil pemeriksaan 21 September.
- Dzaky menyatakan tugas belum dibagi dan meminta rencana ideal dengan
  pemanfaatan waktu sampai 24 September. Rencana memakai 6 jam efektif per
  anggota per hari; ini asumsi kapasitas, bukan jadwal pribadi yang sudah
  dikonfirmasi. Inventaris repo dan referensi sudah dibuat; aset final di
  penyimpanan luar repo masih perlu dicocokkan oleh anggota.

Sumber resmi: [halaman DSDC](https://app.anforcom.com/competition/dsdc) dan
[rulebook daring](https://app.anforcom.com/Rulebook-dsdc-final.pdf), halaman
9–11. PDF daring identik byte demi byte dengan PDF Downloads yang diberikan
tim (647.808 byte; SHA-256
`de50d148b0841184aea9adaca40f26d6d5a2b2f7e4153adb6d3b70fb8180f0f9`).

| Bagian final | Ketentuan | Persiapan yang diperlukan |
|---|---|---|
| Pameran | Rotasi juri 30 menit untuk lima tim; maksimal 5 menit/tim | Pitch singkat, interaksi mandiri, QR, satu skenario yang cepat dipahami |
| Persiapan presentasi | 5 menit | Latihan menyambung layar, membuka aplikasi dan slide |
| Presentasi | Maksimal 10 menit | Target 9 menit, termasuk demo dan perpindahan pembicara |
| Tanya jawab | Maksimal 15 menit | Bank jawaban, pembagian pemilik topik, bukti cadangan |
| Kehadiran | Minimal 2; ketidakhadiran anggota harus dikonfirmasi maksimal H-3 | Tim menyatakan hadir lengkap; simpan bukti konfirmasi |

| Penilaian | Bobot | Fokus persiapan |
|---|---:|---|
| Presentasi | 30% | Cerita produk, waktu, kekompakan |
| Keberhasilan implementasi | 25% | Juri dapat memakai aplikasi langsung |
| Tanya jawab | 20% | Jawaban kritis, logis, cepat, dan sopan |
| Pameran | 15% | Interaksi dan persuasi pengunjung |
| Code project | 10% | Struktur, keterbacaan, dokumentasi, praktik pengembangan |

Implikasi: jangan menghabiskan enam hari tersisa untuk eksperimen model baru.
Perbaiki masalah yang mengganggu pemakaian, siapkan bukti manfaat, dan mulai
latihan presentasi bersamaan dengan perbaikan teknis.

## 2. Cakupan audit dan kondisi sekarang

Inventaris seluruh **161 berkas tracked**: root 16, backend 49, frontend 33,
data 30, docs 29, workflow 2, SQL 1, dan GEE 1. Pemindaian struktur/teks
mencakup 131 berkas teks dengan sekitar 30.098 baris, termasuk data JSON.
Pembacaan mendalam dipusatkan pada jalur runtime, routing, indeks, pasut,
dampak, alur React, kontrak database, pipeline aktif, tes, deploy, dan
dokumentasi final. Skrip riset serta artefak metrik dipetakan untuk memahami
asal hasil. Inventaris ini bukan klaim semua eksperimen direproduksi ulang.

Proposal acuan adalah **PDF 29 halaman dalam Downloads yang ditunjuk Dzaky**.
Proposal di root repo juga 29 halaman, tetapi tidak otomatis dianggap sebagai
berkas submission yang sama. PDF Downloads sudah mencantumkan video dan Figma;
placeholder README tidak berarti kedua deliverable belum dibuat.

| Area | Hasil pemeriksaan sesi ini |
|---|---|
| Git | Working tree awal bersih; HEAD lokal dan remote `790a2946301d8977a90bcb3d687922f79f8f3873` |
| Repo publik | Dapat diakses melalui GitHub API; bukan private |
| Frontend produksi | HTTP 200; shell Vercel tersedia |
| API produksi | HTTP 200, `database: true`, commit sama dengan HEAD |
| Data | 19.394 ruas, panjang terlapor 1.289,4 km; 67.442 baris prediksi; sumber `kerentanan_v1` |
| Rentang baris prediksi produksi | 19 September 20.00 UTC–30 September 23.00 UTC, mencakup final; min/max ini bukan metadata seluruh jam kering |
| Potret | 26 September 00.00 WIB–28 September 23.00 WIB |
| Unit test | **43 lulus**, dijalankan ulang |
| Build frontend | Berhasil; peringatan JS chunk 1,27 MB, gzip sekitar 348 KB |
| Uji HTTP produksi | **35 lulus, 0 gagal, 1 catatan** dari skrip yang tersedia |
| Uji HTTP lokal dari potret | **35 lulus, 0 gagal**, dikonfirmasi `database: false`, `asal_jaringan: potret` |
| Salinan teks UI | `copy.id.json` dan `frontend/src/copy.id.json` identik saat audit |
| CI | Workflow Uji pada HEAD sukses |
| Jaga hidup | Run terjadwal sudah berjalan; interval teramati sekitar 2–5 jam, bukan tiap 10 menit |

Pengukuran satu rangkaian HTTP produksi: `/api/ruas` **10,9 detik**, sekitar
6,3 MiB JSON; rute motor **6,8 detik**, mobil **5,8 detik**. Di localhost
dengan potret, ruas sekitar **0,1 detik**, rute **kurang dari 0,1 detik**.
Ini pengukuran sampel, bukan p95 dan bukan waktu render layar ponsel.

Batas audit: belum mengoperasikan browser interaktif produksi pada sesi ini,
belum menguji HP fisik/proyektor, belum mematikan Wi-Fi perangkat, belum
menonton video atau membuka isi Figma. Satu screenshot repo diperiksa sebagai
referensi visual historis, bukan bukti tampilan produksi hari ini. Dataset
mentah besar dan model tidak dilatih ulang. Situs lomba diperiksa melalui HTML,
bundle publik, dan PDF resminya karena pembaca web tidak merender halamannya.

## 3. Pekerjaan teknis berdasarkan temuan

### Klarifikasi setelah audit: galat saat interaksi dan konteks lokasi

Dzaky mengonfirmasi pesan “Server tidak merespons” paling sering muncul saat
menggeser waktu atau menghitung rute. Ini mengarahkan diagnosis ke jalur
permintaan interaktif; cold start belum dapat menjelaskan semua kejadian.

Uji tambahan terbatas pada 20 September: tiga pasang permintaan peta+rute
untuk tiga jam berbeda, enam permintaan berjalan serentak. Semua HTTP 200;
rute membutuhkan 16,39–19,52 detik, peta 20,00–32,50 detik. Uji ini membuktikan
latensi tinggi ketika permintaan bertumpuk, tetapi belum mereproduksi galat
spesifik yang dilihat pengguna atau menetapkan penyebab tunggal tanpa log.

**Pembaruan setelah pengujian:** Dzaky menerima notifikasi Render pukul
17.09 WIB bahwa instance melewati batas memori dan restart. Insiden OOM
terkonfirmasi melalui laporan email ini; uji serentak tadi mungkin ikut
memicu lonjakan. Hubungan tepatnya perlu dicocokkan dengan timestamp log
dan metrik. Pengujian beban produksi dihentikan. Profil memori dilanjutkan
di lokal/staging; ping atau pemanasan tidak mencegah OOM. T0/T3 naik menjadi
prioritas kestabilan, bersama T1/T2/T4. Rincian batas concurrency, cache,
geometri statis, pilihan compute dan biaya ada di
[rancangan teknis](final/solusi_teknis_dan_hosting.md).

Kode slider mengubah waktu selama pointer bergerak. Tiap perubahan dapat
memicu permintaan peta dan rute sekaligus. Flag `dibatalkan` pada efek React
hanya mengabaikan hasil lama; fetch-nya tetap berjalan. Prioritaskan pembatasan
frekuensi atau pengiriman setelah pilihan waktu stabil, pembatalan fetch lama,
cache backend, dan geometri statis yang dimuat sekali. Membatalkan fetch di
browser tidak menjamin pekerjaan server yang sudah dimulai ikut berhenti.

Keterbacaan lokasi juga menjadi kebutuhan sebelum demo: tampilkan nama jalan
utama menurut zoom, penanda tujuan cepat bernama, nama/batas wilayah, serta
garis pantai. Data lokal sudah memuat nama pada 12.876 ruas, delapan fitur
kecamatan, 21 garis pantai, dan empat tujuan cepat. Periksa cakupan/kualitas
geometrinya sebelum dipakai. Enam ribu lima ratus delapan ruas belum bernama;
jangan mengarang nama. Implementasi sekarang belum merender lapisan label
tersebut. Daffa memegang pekerjaan ini bersama perbaikan UI T1/T3.

### P0 — sebelum pembekuan versi demo

| ID | Temuan dan bukti | Pekerjaan | Syarat selesai |
|---|---|---|---|
| T1 | Tombol Cari/Cari ulang memakai `setIndeksJam(i => i)` di `frontend/src/App.jsx:262`; nilainya tidak berubah sehingga efek fetch tidak berjalan ulang | Hubungkan tombol ke pemicu pencarian nyata dan jalur retry | Setelah kegagalan sementara, tombol berhasil meminta rute lagi tanpa mengganti titik/jam |
| T2 | Data di luar waktu tersedia diperlakukan sebagai kering. Reproduksi lokal: rute tahun 2099 tetap ditemukan dan kedalaman nol. `/api/jam` hanya memeriksa overlap jendela dan frontend mengabaikan flag cakupannya | Simpan/nyatakan cakupan data eksplisit termasuk jam kering; validasi waktu berangkat, waktu tiba dan saran alternatif; tampilkan tidak tersedia | Sebelum/sesudah cakupan tidak menghasilkan rekomendasi seolah kering. Potret basi dan prediksi kosong ditolak konsisten |
| T3 | `_peta_kedalaman_penuh()` menarik semua prediksi per permintaan; perubahan jam mengunduh seluruh geometri ruas lagi | Cache data runtime dengan versi/masa berlaku; muat geometri sekali; perbarui nilai per ruas atau layer genangan; batasi query sesuai kebutuhan | Ukur ulang pada perangkat dan koneksi yang sama; target rute hangat p95 ≤2 detik dan perubahan peta ≤1 detik setelah geometri dimuat |
| T4 | Dijkstra menutup simpul sekali, sedangkan biaya per jam dapat turun mendadak. Contoh buatan menghasilkan 4.046 detik padahal ada jalur sah 3.661 detik | Tambahkan uji regresi perubahan jam, tentukan metode routing yang benar untuk model waktu yang dipilih; batasi lingkup implementasi | Kasus lawan dan kasus jalan membuka/menutup lulus. Klaim optimalitas hanya dipakai bila algoritme dan asumsi mendukungnya |

Target kinerja T3 adalah sasaran tim yang diusulkan, bukan persyaratan rulebook.
Jangan mengorbankan validitas waktu agar cache cepat. Masa berlaku data harus
tetap diperiksa setelah cache dimuat; perubahan data harus membatalkan cache.
GeoJSON besar juga perlu penanganan kompresi/ukuran, tetapi hentikan unduhan
ulang geometri lebih dahulu. Optimasi bundle bukan prioritas pertama.

T4 adalah cacat yang direproduksi pada graf kecil, **belum bukti semua rute
Semarang salah**. Contohnya: jalur langsung mencapai simpul antara pada detik
3.599, jalur lain pada 3.601; ruas berikutnya menjadi kering saat detik 3.600.
Menyimpan hanya kedatangan pertama menghilangkan jalur yang tiba lebih cepat
di tujuan. Resolusi satu jam tidak dengan sendirinya menjamin sifat FIFO.
Sebelum 22 September, tetapkan apakah memperbaiki pencarian waktu atau
mengubah model biaya dengan asumsi yang sah. Jika belum selesai, nyatakan
perutean sebagai pendekatan dengan keterbatasan optimalitas dan jangan
menjadikan hasilnya navigasi keselamatan atau angka dampak yang tervalidasi.

Rekomendasi scope final terbaru dijabarkan pada T4 di dokumen teknis:
biaya tetap menurut jam keberangkatan selama satu pencarian, lalu hitung
ulang ketika pilihan jam berubah. Ini perubahan model yang perlu ditinjau
sebelum implementasi dan disampaikan dalam UI/materi, bukan perbaikan
setara atas solver dinamis. Hasil demo harus dihitung ulang. Bila tim
mempertahankan dinamika sepanjang perjalanan, gunakan algoritme/model yang
sesuai dan verifikasi kasus lawan sebelum menyebut optimalitas.

### P1 — konsistensi demo, informasi dan pemulihan

- **Saran jam alternatif:** `_jam_lebih_aman()` dapat mencari ke masa lalu,
  tidak mengevaluasi ulang perjalanan berdasarkan waktu tiba, dan melewati
  jam kering yang tidak punya baris database. Dalam contoh Pelabuhan→Tawang
  pukul 08.00, saran yang muncul 05.00. Untuk keberangkatan mendatang,
  batasi ke waktu yang masih bisa dipilih, dalam horizon, dan hitung ulang
  rute. Bedakan pencarian skenario historis dari rekomendasi berangkat.
- **Saat menggeser waktu:** batalkan request lama atau batasi frekuensinya;
  tampilkan status pembaruan agar label jam baru tidak tampak mewakili peta
  dan rute lama. Bersihkan galat setelah pemulihan berhasil. Uji slider cepat,
  pergantian moda, penghapusan titik saat request berjalan, dan retry.
- **Failover saat sedang dipakai:** uji database putus setelah startup dan
  setelah pemeriksaan kesehatan sukses. Jalur potret saat database sejak
  awal mati sudah lulus; itu belum membuktikan kegagalan di tengah query
  otomatis tertangani. Jangan mengubah database produksi untuk pengujian ini.
- **Peringatan:** panel rute dan komponen paparan dapat menampilkan pesan
  ganda; komponen kedua mengisi jam dengan tanda `—`. Rapikan agar lokasi,
  jam, dan estimasi yang dibaca juri konsisten.
- **POI:** titik tujuan Pelabuhan dan Terboyo dipindah sekitar 669 m dan
  525 m dari titik POI sumber agar melekat ke jalan. Periksa apakah sesuai
  akses masuk sebenarnya; jangan menyebutnya navigasi sampai pintu tujuan
  sebelum diverifikasi.
- **Rentang emisi negatif:** perkalian selisih jarak negatif dapat membuat
  nilai `bawah > atas`. Urutkan ujung rentang; jelaskan asumsi ±30% sebagai
  rentang skenario, bukan interval kepercayaan statistik.
- **CI:** tambahkan build frontend dan regresi untuk kontrak waktu, retry,
  serta routing. Enam permintaan `/api/jam` dari cache tidak membuktikan
  enam pengguna menghitung rute bersamaan; uji beban kecil yang representatif.

Skrip HTTP saat ini menerima respons 200 untuk tahun 2099 sebagai lulus.
Karena itu angka 35/35 mengukur kontrak yang sudah ditulis, bukan membuktikan
seluruh perilaku produk benar. Perketat kriteria tes yang berhubungan dengan
temuan, jangan hanya menambah jumlah tes.

## 4. Klaim dan bukti untuk dibawa ke juri

Kalimat inti yang disarankan:

> PASANG SURUT membantu pengguna membandingkan rute dan jam keberangkatan di
> pesisir Semarang menggunakan rekonstruksi pasut dan indeks kerentanan jalan,
> sekaligus memperlihatkan biaya tambahan serta potensi paparan.

| Hal | Cara menyampaikan yang dapat dipertanggungjawabkan |
|---|---|
| Akurasi | Korelasi 0,78–0,91 dan RMSE sekitar 0,10–0,12 m adalah evaluasi pasut pada jendela yang diuji, bukan akurasi genangan per ruas |
| Indeks | Bobot tiga komponen adalah asumsi; belum punya ground truth per ruas |
| Kedalaman | Besaran turunan dari fungsi rancangan, bukan pengukuran sentimeter |
| Sentinel-1 | Metode label/model yang dicoba tim ditolak; jangan menggeneralisasi bahwa Sentinel-1 tidak bisa memantau banjir |
| Hujan | Tidak dipakai dalam indeks runtime sekarang; pernah menjadi fitur model yang ditolak |
| Dampak | Waktu dan jarak hasil simulasi; biaya adaptasi dibanding baseline bebas genangan. Tidak otomatis berarti penghematan perjalanan nyata |
| Rendah karbon | Membantu memperlihatkan konsekuensi BBM/emisi dari pilihan rute/jam; belum membuktikan penurunan emisi kota |
| Offline | Stack lokal bisa melayani dari potret. PWA di ponsel yang bergantung API Render bukan aplikasi offline penuh |
| Nilai ekonomi/kesehatan | Jangan mengubah baseline kerugian kota menjadi klaim uang yang diselamatkan, atau mengklaim penurunan kasus penyakit |

Empat koreksi metodologi/dokumentasi perlu masuk lembar bukti:

1. **“Radius 500 m” belum sesuai implementasi.** Kode memakai median
   sembilan sel grid dengan sisi 500 m, bukan penyaringan jarak lingkaran
   500 m. Uji dua titik berjarak 999 m menunjukkan keduanya ikut saling
   memengaruhi. Pilih mendokumentasikan neighborhood grid yang sebenarnya
   atau memperbaiki radius dan meregenerasi hasil. Perubahan data memerlukan
   uji ulang demo, jadi jangan dilakukan mendadak pada H-1.
2. **Penurunan simpangan baku elevasi bukan bukti penurunan galat DEM.**
   Angka 5,86→2,99 m menggambarkan sebaran, bukan RMSE terhadap elevasi
   lapangan. Gunakan istilah yang tepat pada slide/jawaban.
3. **Angka 10% dalam pipeline adalah asumsi skala.** Skrip 11 memakai
   proporsi puncak untuk memilih jumlah ruas. Angka jaringan seluruh kota
   tidak langsung memvalidasi proporsi hitungan ruas pada AOI pilot;
   jangan menyebut transfer tersebut pasti konservatif atau hasil kalibrasi.
4. **Bukti pasut perlu dipisahkan dari kalibrasi.** Offset dipilih dengan
   membandingkan rekaman terukur. Jika ada kapasitas, tambah evaluasi periode
   terpisah setelah parameter dibekukan. Laporkan hasil apa adanya. Ini lebih
   berguna daripada mengulang lima eksperimen Sentinel-1 menjelang final.

Satu tugas bukti pengguna yang realistis sebelum 24 September: **5–8 sesi
uji tugas singkat**, idealnya melibatkan warga/pengendara yang mengenal wilayah.
Minta memilih dua titik, membandingkan jam, membaca peringatan, lalu menjelaskan
arti angka dampak tanpa bantuan. Catat keberhasilan tugas, waktu, kesalahan,
dan apakah label estimasi dipahami. Angka 5–8 adalah target kegiatan, bukan
hasil yang sudah diperoleh atau bukti representasi populasi. Jika peserta
hanya teman kampus, laporkan komposisi tersebut. Ini validasi kegunaan UI,
bukan validasi akurasi rob.

Untuk Code Project, selesaikan pekerjaan murah tetapi terlihat:

- Isi tautan README dari proposal: [video](https://youtu.be/CeXsEN_1Zvk) dan
  [Figma](https://www.figma.com/design/EtACxc7jD6wvMJjHh7bq3p/PasangSurut?node-id=1-907).
- Ganti `docs/arsitektur.md` dan `docs/metodologi.md` yang masih berupa
  heading kosong dengan penjelasan ringkas atau rujukan jelas ke isi yang ada.
- Selaraskan `faktor_emisi.json` yang masih null dengan dokumentasi sitasi,
  tabel runtime, dan satuan. Rumus saat ini memakai faktor CO2 bahan bakar;
  label CO2e perlu dasar tambahan atau disederhanakan sesuai yang dihitung.
- Koreksi komentar lama “fitur menyusul”, angka kinerja historis, klaim
  tidak ada jaringan runtime (produksi tetap mengakses database), dan
  langkah refresh hujan yang tidak relevan untuk indeks runtime.
- Pertahankan arsip proposal submission. Jika koreksi diperlukan, buat
  lembar perubahan untuk final; penggantian berkas submission mengikuti
  arahan panitia. Jangan menimpa diam-diam dokumen yang dinilai penyisihan.

## 5. Paket presentasi, pameran, dan tanya jawab

### Presentasi utama: target 9 menit

| Waktu | Isi | Pemilik usulan |
|---|---|---|
| 00.00–00.45 | Satu perjalanan konkret di pesisir: berangkat kapan, lewat mana? | Dzaky |
| 00.45–01.30 | Pengguna, masalah, keputusan yang dibantu | Dzaky |
| 01.30–04.30 | Demo rute, pergantian jam, biaya adaptasi, peringatan | Daffa |
| 04.30–05.30 | Cara kerja dan arsitektur ringkas | Daffa/Dzaky |
| 05.30–06.30 | Yang sudah diuji; batas akurasi; alasan model ditolak | Dzaky |
| 06.30–07.30 | Bukti kegunaan, hasil simulasi, kaitan mobilitas/Eco-Health | Naufal |
| 07.30–08.30 | Rencana pilot, pengelola data, keberlanjutan dan keterbatasan | Naufal |
| 08.30–09.00 | Tutup dengan keputusan pengguna yang kini terbantu | Naufal |

Siapkan sekitar 8–10 slide utama dan lampiran bukti. Bahas penolakan model
secukupnya dalam satu slide; detail lima eksperimen masuk lampiran. Kejujuran
metode mendukung kepercayaan, tetapi juri tetap perlu melihat manfaat produk.

Lampiran minimum: arsitektur; definisi indeks; validasi pasut dan jendela uji;
alasan penolakan S1; sumber angka dan asumsi; baseline dampak; bukti pengujian
terbaru; rencana pilot/pembaruan data. Setiap angka mencantumkan tanggal,
jenis bukti, dan sumber, sehingga tidak tercampur dengan hasil Agustus.

### Skenario demo yang sudah dicoba dari potret

Moda **motor**, asal **Stasiun Semarang Tawang**, tujuan **Kawasan Industri
Terboyo**. Angka berikut hasil kode saat audit, harus diukur ulang setelah
perbaikan dan tidak diperlakukan sebagai kondisi nyata jalan:

| Waktu WIB | Hasil simulasi |
|---|---|
| 26 September 08.00 | Pembanding 7,0 menit; sadar rob 13,9 menit; tambahan 6,9 menit dan 4,27 km; ruas berestimasi genangan pada rute turun dari 29 menjadi 14; peringatan paparan tetap muncul |
| 26 September 13.00 | Kedua rute 7,0 menit, selisih nol, tidak ada genangan menurut indeks |
| 27 September 09.00 | Pembanding 7,0 menit; sadar rob 11,7 menit; tambahan 4,7 menit dan 4,27 km |

Alur: pilih dua tujuan → tunjukkan kondisi jam pasang → jelaskan biaya
memutar dan peringatan yang masih ada → pindah ke jam yang lebih rendah
risikonya → tutup dengan satu kalimat batas validasi. Jangan menyebut semua
rute hasil sistem aman atau pengurangan jumlah ruas sebagai penurunan risiko
kesehatan yang telah terukur.

Produksi menampilkan 72 jam dari jam berjalan. Jika presentasi 26 September
berlangsung setelah pukul 08.00, gunakan puncak berikutnya **27 September
09.00**, atau gunakan potret lokal bertanggal yang disebut terang-terangan.
Jangan bergantung pada jam pagi yang sudah keluar dari slider produksi.
Potret lokal selalu mulai 26 September 00.00; itu skenario beku, bukan jam kini.

### Pameran: target 4 menit 30 detik

- 30 detik: jelaskan keputusan yang dibantu.
- 60 detik: demonstrasikan perubahan rute/jam.
- 90 detik: serahkan kendali kepada juri/pengunjung untuk mencoba.
- 60 detik: jelaskan satu manfaat dan satu batasan, jawab pertanyaan.
- 30 detik: QR aplikasi/repo dan ajakan uji pilot.

Siapkan satu poster/A3 atau display sesuai izin TM: masalah, tiga langkah,
satu ilustrasi perbandingan rute, batas estimasi, dan QR dengan URL tertulis.
Poster adalah rekomendasi pameran, belum diketahui sebagai kewajiban panitia.
Peran meja: penjelas, operator/pemandu interaksi, pencatat pertanyaan sekaligus
penjaga kesiapan teknis. Ketiganya perlu dapat mengambil alih demo.

### Bank tanya jawab yang dilatih

| Pertanyaan | Inti jawaban/bukti | Pemilik usulan |
|---|---|---|
| Seberapa akurat? | Pisahkan pasut terukur dan indeks yang belum punya validasi per ruas | Dzaky |
| Mengapa model S1 ditolak? | Kualitas label/proksi, evaluasi waktu, uji penyelamatan; tidak menyimpulkan semua S1 buruk | Dzaky |
| Dari mana kedalaman dan ambang moda? | Fungsi/asumsi yang transparan; bukan pengukuran atau standar keselamatan | Dzaky |
| Kenapa DEM meter dipakai untuk rob sentimeter? | Fitur relatif untuk peringkat kerentanan; belum membuktikan galat sentimeter | Dzaky |
| Hujan, tanggul, pompa, cuaca ekstrem? | Belum masuk runtime; jelaskan konsekuensi pada cakupan produk | Dzaky |
| Rute ini benar-benar paling cepat? | Jelaskan model biaya, waktu tiba, dan status penyelesaian temuan T4 | Pemilik backend |
| Apa manfaat bila median selisih kecil? | Median seluruh pasangan dapat kecil; jelaskan kebutuhan pengguna tertentu dan biaya adaptasi; jangan mengganti median dengan kasus demo | Naufal |
| Mengapa subtema rendah karbon jika rute memutar? | Transparansi konsekuensi energi dan pilihan waktu; belum mengklaim penghematan total | Naufal |
| Apa beda dengan aplikasi lain? | Tunjukkan fitur keputusan perjalanan milik sendiri; perbandingan spesifik hanya setelah memeriksa produk pembanding | Daffa |
| Apa terjadi tanpa internet? | Demonstrasikan stack lokal + potret; PWA publik tetap memerlukan API | Daffa |
| Siapa memperbarui data dan menanggung biaya? | Pemilik operasional, jadwal pembaruan, monitoring, dan sumber biaya pilot; status rencana belum kemitraan | Naufal |
| Apakah sudah dipakai warga/BPBD? | Sebut hanya pengguna/komunikasi yang benar-benar terjadi; belum ada mitra terkonfirmasi dari bukti audit | Naufal |

Format jawaban latihan: jawaban inti 15–20 detik, bukti satu angka/contoh,
lalu batasannya. Jangan tiga orang menjawab serentak. Anggota lain menambah
hanya bila diperlukan. Latih satu sesi 15 menit tanpa melihat naskah.

## 6. Jadwal kerja 20–26 September

Pembagian kerja yang diusulkan untuk segera dipakai: Dzaky bertanggung jawab
backend/data dan ketepatan metode; Daffa bertanggung jawab UI, kinerja peta,
alur demo dan materi visual; Naufal bertanggung jawab slide/narasi, daftar
bukti, pengujian pengguna, logistik dan checklist. Ketiganya ikut latihan dan
memahami bagian anggota lain. Naufal menguji hasil perbaikan Dzaky/Daffa dari
sudut pemakai. Dzaky tetap memegang keputusan akhir klaim angka.

**Kapasitas ideal:** sisa 20 September sekitar 3 jam efektif per anggota,
21–24 September masing-masing 6 jam efektif per anggota per hari. Total
anggaran awal sekitar **81 jam-orang**, termasuk latihan dan koordinasi.
Sisihkan 20% sebagai cadangan bug/TM/urusan kampus; komitmen pekerjaan inti
sekitar 65 jam-orang. Bukan seluruhnya untuk menulis kode. Jika jadwal nyata
lebih sempit, kurangi scope P1 sebelum mengurangi latihan dan demo cadangan.

Pola harian yang disarankan: 09.00–12.00 pengerjaan fokus; 13.00–15.30
pengerjaan/pengujian; 15.30–16.00 integrasi dan evaluasi. Total 6 jam efektif
dengan jeda makan. Pindahkan blok sesuai jadwal kuliah dan TM. Hindari
perubahan besar larut malam 24–25 September.

| Hari | Dzaky | Daffa | Naufal |
|---|---|---|---|
| 20, sekitar 3 jam | Triase T2/T4 dan kunci klaim produk | Reproduksi T1, daftar masalah interaksi, inventaris bahan visual | Inventaris slide/video, outline 9 menit, checklist TM/logistik |
| 21, 6 jam | T2: cakupan data; mulai cache T3 | T1: retry; status pembaruan; pisahkan geometri/dinamika T3 | Draf slide lengkap + sumber angka; rekrut peserta uji tugas |
| 22, 6 jam termasuk TM | T4: uji kasus dan keputusan solusi; integrasi backend | Benchmark interaksi; siapkan kedua laptop; bantu ekspor diagram | Hadiri/catat TM bersama tim; FAQ; koordinasi latihan pertama |
| 23, 6 jam | Tutup regresi prioritas; periksa klaim/metrik | Tutup regresi UI; tes HP dan jalur cadangan; tangkapan layar baru | Jalankan uji tugas dengan bantuan tim; perbaiki narasi; siapkan poster/QR |
| 24, 6 jam | Uji release dan bekukan versi; lembar metode final | Rekam demo, bundel lokal dan cadangan; cek proyektor bila tersedia | Satukan PDF, lampiran, checklist berkas; pastikan ketentuan kirim |

Pada 22–24 September, latihan adalah bagian dari jatah 6 jam, bukan pekerjaan
tambahan setelah semua tugas selesai. Latihan 24 September minimal dua putaran
9 menit ditambah satu sesi Q&A 15 menit dan evaluasi. T4 diberi sesi diagnosis
terbatas pada 21–22 September; bila membutuhkan perubahan besar, tetapkan
scope dan batas klaim saat itu, jangan menggeser seluruh persiapan ke H-1.

| Hari | Teknis | Materi/tim | Hasil yang harus ada |
|---|---|---|---|
| Minggu 20 | Tetapkan T1–T4, bekukan baseline dan skenario demo | Inventaris slide/video/poster; peran; cek transport/penginapan | Daftar tugas prioritas dan pemilik; outline slide |
| Senin 21 | Perbaiki retry, batas waktu data, status pemuatan; mulai cache/geometri | Draf slide lengkap; susun lembar angka dan pertanyaan TM | Demo inti membaik; slide versi pertama sudah bisa dipresentasikan |
| Selasa 22 | Putuskan/selesaikan pendekatan T4, regresi dan benchmark | Hadiri TM; catat urutan, teknis layar, tenggat PDF; latihan pertama | Persyaratan final tertulis; keputusan scope final |
| Rabu 23 | Tutup bug prioritas, uji cadangan dan dua perangkat | Uji tugas 5–8 orang jika memungkinkan; rapikan narasi/FAQ | Bukti penggunaan dan daftar masalah tersisa |
| Kamis 24 | **Bekukan fitur**; uji produksi, potret, batas waktu dan skenario gagal | Latihan kedua/ketiga berwaktu, rekam video cadangan, ekspor PDF | Paket final lengkap pada dua laptop/flashdisk; keputusan siap demo |
| Jumat 25 | Verifikasi build final dan potret; hanya perbaikan blocker | Perjalanan/registrasi sesuai rencana tim; latihan ringan dan cek alat | Tidak ada perubahan besar, semua anggota tahu alur cadangan |
| Sabtu 26 | Buka produksi H-30 menit; ping; lokal siap dari awal | Pameran, presentasi, Q&A; jaga meja setelah presentasi | Demo stabil dan penjelasan konsisten |

Jika TM menetapkan deadline PDF sebelum 24 September, tarik penyelesaian
materi ke deadline panitia tersebut. Target internal 24 September tidak
menggantikan tenggat resmi.

Jika kapasitas terbatas: dahulukan pengendalian lonjakan memori, retry/cakupan
waktu, jalur lokal, batas model routing, slide selesai, dan latihan.
Tunda model baru, login, laporan warga, perluasan wilayah, integrasi lalu
lintas, dan redesign menyeluruh. Penambahan RAM/migrasi API dipilih menurut
biaya dan waktu penyiapan; migrasi database tetap di luar scope final.

## 7. Paket cadangan dan kriteria siap tampil

Urutan cadangan: **produksi → aplikasi lokal → MP4 lokal → screenshot di PDF**.
Semua lapisan harus memiliki cerita yang sama. Jangan menunggu produksi gagal
untuk baru menyalakan backend lokal.

Backend lokal pada PowerShell, dari akar repo (perintah menjalankan server
harus dibiarkan hidup selama demo):

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -c "import os; os.environ['DATABASE_URL']=''; import uvicorn; uvicorn.run('app.main:app', host='127.0.0.1', port=8000)"
```

Pada Windows PowerShell sesi audit, `$env:DATABASE_URL=''` menghapus variabel,
sehingga dotenv justru membaca URL database dari `.env`. Karena itu kosongkan
di dalam proses Python seperti contoh, lalu periksa `/api/kesehatan` benar-benar
`database: false` dan `asal_jaringan: potret`. Jangan mencetak URL database.

Frontend di terminal kedua, dari akar repo:

```powershell
Set-Location frontend
$env:VITE_API_URL='http://127.0.0.1:8000'
npm.cmd run dev -- --host 127.0.0.1
```

Buka alamat yang diberikan Vite. Sebelum hari H, siapkan juga build lokal
yang sudah menunjuk API localhost; port preview harus disesuaikan dengan
izin CORS backend. Instal dependency pada kedua laptop saat masih online.
Tes ulang dengan Wi-Fi dimatikan, termasuk font, peta, rute, dan Validasi.

Pemantauan produksi harus memakai koneksi internet; laptop yang menjalankan
demo offline tidak otomatis bisa sekaligus menjaga Render lewat ping. Tetapkan
perangkat penanggung jawab dengan hotspot aktif. Perintah ping PowerShell:

```powershell
while ($true) {
    try {
        $cekFinal = Invoke-RestMethod 'https://pasang-surut-api.onrender.com/api/kesehatan' -TimeoutSec 60
        Write-Host (Get-Date) $cekFinal.status $cekFinal.database
    } catch {
        Write-Host (Get-Date) 'API belum menjawab; cek koneksi dan jalur cadangan'
    }
    Start-Sleep -Seconds 300
}
```

Kriteria siap pada 24 September:

- [ ] Seluruh anggota bisa memulai demo dan beralih ke cadangan.
- [ ] Tidak ada request ulang yang macet tanpa cara retry.
- [ ] Data hilang/kedaluwarsa dibedakan dari kondisi kering.
- [ ] Temuan routing ditangani, atau keterbatasan disebut eksplisit dengan scope yang disepakati tim.
- [ ] Rute dan label jam konsisten setelah slider digerakkan cepat.
- [ ] Dua laptop menjalankan potret yang sama tanpa database/internet.
- [ ] HP nyata diuji pada jaringan seluler; produksi bisa dipakai lewat QR.
- [ ] Presentasi selesai dalam ≤9 menit pada dua latihan berturut-turut.
- [ ] Latihan setup ≤5 menit dan Q&A 15 menit selesai.
- [ ] PDF diperiksa setelah ekspor; diagram terbaca di proyektor; MP4 bisa diputar tanpa jaringan.
- [ ] Tautan video/Figma/repo/aplikasi dapat dibuka tanpa akun khusus juri.
- [ ] Tenggat dan bukti penerimaan PDF dicatat setelah panitia menginformasikan.

Perlengkapan: laptop utama/cadangan + charger; adaptor sesuai port layar,
HDMI, terminal listrik, hotspot dan kuota, flashdisk, identitas/KTM, PDF,
MP4, poster/QR bila diizinkan, timer dan catatan peran. Transport, penginapan,
registrasi, dan pakaian mengikuti hasil TM serta keputusan tim.

## 8. Pertanyaan tersisa

Untuk dicatat tim saat mulai bekerja: status bahan presentasi/pameran/video,
penyesuaian blok kerja dengan jadwal kuliah, pembagian bicara yang nyaman,
akses calon pengguna uji, dan kesiapan laptop kedua. Pembagian kapasitas
ideal sekarang tersedia dalam paket kerja 20 September. Kehadiran sudah
selesai divalidasi. Hosting sedang dievaluasi ulang atas permintaan Dzaky
setelah insiden OOM; belum ada VPS siap pakai atau anggaran yang ditetapkan.
Pilihan konkret tersedia pada dokumen teknis, tanpa transaksi dilakukan.

Untuk TM: jam/gedung registrasi; urutan tampil; tenggat/kanal/penamaan PDF;
boleh revisi sampai kapan; laptop sendiri atau panitia; rasio layar dan port;
durasi demo apakah termasuk 10 menit; perangkat yang dipakai juri;
ketersediaan listrik/internet/meja; izin dan ukuran poster; kewajiban
pengumpulan kode/build/proposal ulang; aturan pakaian.

Keberadaan kompetitor dan isi video mereka dalam catatan 19 September belum
diverifikasi ulang di sesi ini. Benchmark kompetitor boleh menjadi tugas
pendukung, tetapi jangan menunda perbaikan demo dan latihan karena itu.
