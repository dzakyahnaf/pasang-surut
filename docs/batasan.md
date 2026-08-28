# Batasan yang diketahui

> Bahan bagian 5 proposal dan bagian 8 README. Diisi sepanjang pengerjaan,
> bukan di akhir. Setiap batasan yang ditulis sendiri di sini adalah satu
> pertanyaan juri yang sudah terjawab lebih dulu.

Aturan menulis di berkas ini: sebut apa yang tidak kita ketahui, sebut
akibatnya terhadap hasil, lalu sebut apa yang akan dilakukan. Jangan
memperhalus.

---

## 1. Batasan data

### 1.1 Kedalaman genangan adalah estimasi turunan

Sentinel-1 adalah radar. Ia membedakan permukaan basah dan kering lewat
hamburan balik, dan hanya itu. **Radar tidak mengukur kedalaman air.**
Seluruh angka sentimeter yang muncul di aplikasi ini adalah hasil fungsi
turunan dari probabilitas basah dan tinggi muka air, bukan hasil pengukuran.

Akibatnya: angka kedalaman tidak boleh disajikan sebagai fakta terukur.
Setiap tampilan kedalaman di antarmuka menyebutkan bahwa ia estimasi.

### 1.2 DEMNAS punya RMSE vertikal 2,79 m

Rob yang dimodelkan tingginya 10 sampai 50 cm. Ketidakpastian vertikal DEM
hampir enam kali lebih besar daripada gejala yang diamati.

Akibatnya: DEM dipakai sebagai **fitur** model, tidak pernah sebagai ambang.
Membandingkan elevasi absolut terhadap tinggi muka air pada selisih sebesar
itu secara statistik tidak sah, dan repo ini melarangnya secara eksplisit.

### 1.3 Kepadatan citra Sentinel-1 tidak merata

Dari 723 citra di atas AOI sejak 2015, jendela uji 2024 sampai 2026 hanya
berisi 177 citra atau sekitar 24 persen. Penyebabnya jeda antara berakhirnya
Sentinel-1B pada 23 Desember 2021 dan mulai regulernya Sentinel-1C pada 26
Maret 2025. Terlihat di data: 2022 sampai 2024 di kisaran 33 sampai 53 citra
per tahun, sementara 2018 sampai 2021 di kisaran 76 sampai 92.

Akibatnya: metrik pada jendela uji berdiri di atas sampel yang lebih jarang
daripada jendela latih. Ini wajib disebut saat membahas hasil model.

Rincian ada di `validasi.md`.

### 1.4 Konstanta pasut berasal dari rekaman 15 hari, dan dua komponen tidak diukur

Konstanta harmonik di `data/referensi/konstanta_pasut_semarang.json` diambil
dari Rachman, Ismunarti, dan Handoyo (Jurnal Oseanografi Undip, 2015), hasil
metode Admiralty atas pengamatan 15 hari pada Maret 2014.

Rekaman 15 hari tidak dapat memisahkan komponen yang frekuensinya berdekatan.
Akibatnya terlihat langsung di tabel: **P1 dan K2 bukan hasil pengukuran.**
Keduanya diturunkan dari K1 dan S2 memakai rasio tetap Admiralty. Buktinya
aritmetis — P1/K1 = 0,3305 dan K2/S2 = 0,2697, keduanya persis rasio baku,
dan fasenya disamakan dengan komponen induknya. Dua dari tujuh komponen yang
dipakai rekonstruksi karena itu tidak berdiri sendiri.

**Zona waktu acuan fase tidak disebutkan di sumber.** Ini bukan detail kecil.
Salah menebak menggeser seluruh kurva pasut sampai 7 jam, dan untuk M2 yang
periodenya 12,4 jam pergeseran sebesar itu bisa membalik pasang menjadi surut.
Rencana penyelesaiannya ada di berkas konstanta.

**Sumber lain tidak sepakat soal tipe pasut.** Az Zahro dan kawan-kawan
(Prosiding SNF Universitas Negeri Jakarta) menganalisis data Pushidrosal
selama 29 piantan pada Januari sampai Februari 2018 dan memperoleh Formzahl
3,94, yaitu harian tunggal. Sumber utama kita memperoleh 1,121, yaitu
campuran condong ke harian ganda. Rekaman mereka lebih panjang. Perbedaan ini
belum terselesaikan.

### 1.5 Datum vertikal tidak sama antar sumber

Elevasi pasut di berkas konstanta relatif terhadap nol palem pasut setempat.
DEMNAS memakai EGM2008. Keduanya tidak boleh dikurangkan langsung. Ini
alasan tambahan mengapa ambang elevasi absolut tidak dipakai.

### 1.6 Daftar kejadian rob belum lengkap dan sebagian besar belum diverifikasi

`data/referensi/kejadian_rob_semarang.json` berisi 21 entri, tetapi hanya 2
yang sudah dibaca sampai ke sumber primernya. Periode 2015 sampai 2019 nyaris
kosong karena arsip berita daring dari rentang itu sulit ditemukan.

Akibatnya: daftar ini belum layak dipakai sebagai dasar klaim frekuensi
kejadian. Untuk itu perlu rekap resmi dari BPBD Kota Semarang.

### 1.7 Laju penurunan tanah: sudah punya sitasi, tetapi angkanya lebih kecil daripada yang beredar

`laju_subsidensi.json` terisi 28 Agustus 2026 dari Rahmawati, Prasetyo &
Sasmito (2020), *Jurnal Geodesi Undip* 9(1):29–36, ISSN 2337-845X — metode
SBAS atas 13 citra Sentinel-1A SLC 2015–2018, diolah dengan GMTSAR.

Empat batasan melekat pada angka itu.

**Pertama, angkanya lebih kecil daripada yang selama ini dipakai tim.**
Makalah menguji enam varian pengolahan; penulisnya memilih varian **tanpa
koreksi** karena RMSE-nya terkecil, ±1,3 cm/tahun. Menurut varian itu, nilai
tertinggi di seluruh Kota Semarang adalah **9,4 cm/tahun** dan rata-rata
Semarang Utara hanya **4,6 cm/tahun**.

| Kecamatan | Minimum | Maksimum | Rata-rata |
|---|---:|---:|---:|
| Genuk | 2,3 | 9,4 | 5,8 |
| Semarang Utara | 0,8 | 7,4 | 4,6 |
| Semarang Timur | 0,1 | 7,4 | 4,5 |
| Gayamsari | 0,1 | 8,1 | 3,6 |

Angka belasan memang muncul di makalah yang sama, tetapi hanya pada varian
terkoreksi atmosfer yang RMSE-nya dua sampai lima kali lebih besar dan justru
**tidak** dipilih penulisnya. **Klaim "9–13 cm/tahun" di PLAN.md bagian 6 dan
di abstrak proposal karena itu tidak didukung sumber ini.** Ini perlu
keputusan tim: turunkan klaimnya, atau sediakan sitasi lain yang dibaca
sendiri sampai ke tabelnya.

**Kedua, ketidakpastiannya besar relatif terhadap nilainya.** Untuk Gayamsari
yang rata-ratanya 3,6 cm/tahun, ±1,3 cm/tahun setara sekitar 36 persen.
Sajikan sebagai rentang, jangan sebagai angka tunggal.

**Ketiga, periodenya 2015–2018.** Memakainya untuk 2026 adalah ekstrapolasi
delapan tahun dan wajib disebut demikian, terutama karena laju subsidensi
berubah bila pengambilan air tanah berubah.

**Keempat, daya pisahnya per kecamatan, bukan per ruas.** Seluruh ruas di
dalam satu kecamatan menerima nilai yang sama, sehingga sebagai fitur model
ia lebih berperan sebagai penanda wilayah daripada ukuran lokal. Dari 19.394
ruas, 18.404 mendapat nilai; 990 sisanya berada di kecamatan yang tidak
dilaporkan sumbernya dan tetap `NULL`.

### 1.8 Faktor emisi masih `null`

`faktor_emisi.json` belum terisi. Akibatnya panel dampak belum bisa
menghitung emisi, dan seluruh baris rantai dampak di proposal masih
"Belum tersedia".

### 1.9 Curah hujan berasal dari reanalisis, satu titik untuk seluruh AOI

Hujan diambil dari Open-Meteo Archive (reanalisis ERA5), 102.168 jam
2015–2026, pada satu titik di tengah AOI. Dua konsekuensinya.

**Petak reanalisis jauh lebih besar daripada AOI.** AOI hanya sekitar 13 × 8
kilometer, sehingga seluruh wilayah pilot berbagi satu deret hujan yang sama.
Hujan konvektif di Semarang kerap sangat setempat; perbedaan antara
Tanjungmas yang deras dan Genuk yang kering tidak akan tertangkap.

**Reanalisis bukan pengamatan.** Rerata tahunan yang dihasilkan 1.830 mm dan
belum dibandingkan terhadap normal BMKG stasiun Semarang. Reanalisis
diketahui cenderung meratakan hujan setempat, jadi angka ini belum layak
dikutip sebelum diperiksa.

### 1.10 Ruas di tepi timur AOI berada tepat di tepi tile DEMNAS

Tile `1409-22` berakhir persis di bujur 110,5000, yang juga tepi timur AOI.
26 dari 19.394 ruas jatuh di piksel tanpa data dan elevasinya tetap `NULL`.
Jumlahnya kecil (0,13 persen) sehingga tidak diambil tindakan, tetapi bila
AOI diperluas ke timur, tile tetangga wajib diunduh lebih dulu.

---

## 2. Batasan model

### 2.1 Model belum dilatih

Belum ada satu pun angka akurasi. Selama itu, seluruh prediksi berasal dari
data contoh bertanda `sumber = 'dummy'` dan antarmuka menampilkan lencana
DATA CONTOH.

### 2.2 Fungsi data contoh tidak punya dasar fisik

Selama model asli belum ada, kedalaman dihitung dari satu sinusoid pasut
periode 24,8 jam dan satu pengganti elevasi berupa lintang, dengan anggapan
makin ke utara makin dekat Laut Jawa. Kenyataannya genangan rob mengikuti
elevasi, laju penurunan tanah, dan jaringan drainase, bukan garis lintang.

Akibatnya: peta yang terlihat sekarang benar secara bentuk tetapi salah
secara nilai. Fungsi ini dibuang begitu model asli masuk.

### 2.3 Konversi probabilitas ke kedalaman akan jadi titik terlemah

Model menghasilkan probabilitas basah. Angka sentimeter yang dilihat pengguna
lahir dari fungsi monotonik yang dikalibrasi terhadap tinggi pasut. Fungsi itu
adalah asumsi, bukan hasil pengukuran, dan harus diakui sendiri sebelum juri
menemukannya.

### 2.4 Penalti genangan pada routing adalah angka rancangan

Mesin perutean mengalikan waktu tempuh dengan penalti yang tumbuh seiring
kedalaman: 1,0 di bawah ambang lambat, 2,5 di ambang berisiko, dan 8,0
menjelang ambang tidak bisa lewat. **Ketiga angka itu dipilih agar
bentuknya monoton dan bisa dijelaskan, bukan diukur di lapangan.**

Ambang kedalamannya sendiri dibaca dari tabel `ambang_moda` dan bukan
ditulis di kode, sehingga bisa dikoreksi tanpa menyentuh mesin routing.
Tetapi komentar di `db/schema.sql` sendiri menyatakan angka di tabel itu
masih asumsi dan rujukannya perlu dicari.

Akibatnya: selisih waktu antara rute pembanding dan rute sadar rob
bergantung pada angka yang belum bersumber. Selisih jarak tidak, karena itu
geometri murni. Saat menyajikan dampak, jarak lebih kuat dipertahankan
daripada waktu.

### 2.5 Kecepatan ruas sebagian hasil imputasi

Ruas jalan yang tidak punya tag `maxspeed` di OpenStreetMap diisi kecepatan
rata-rata jenis jalan yang sama di dalam AOI, memakai OSMnx. Dari 19.394 ruas,
sebagian besar jalan permukiman memang tanpa tag itu.

Akibatnya: estimasi waktu tempuh membawa ketidakpastian yang tidak dilaporkan
sebagai rentang. Ini imputasi, bukan pengukuran.

---

## 3. Batasan cakupan wilayah

### 3.1 Hanya wilayah pilot, bukan seluruh kota

AOI meliputi sekitar 98,4 km persegi di Semarang Utara dan Timur. Enam
kelurahan sasaran — Tanjungmas, Bandarharjo, Kemijen, Kaligawe, Terboyo
Kulon, dan Terboyo Wetan — seluruhnya berada di dalamnya, terverifikasi pada
24 Agustus 2026 terhadap batas administratif OpenStreetMap.

### 3.2 AOI sengaja lebih luas daripada wilayah terdampak

Gabungan keenam kelurahan sasaran hanya 27,6 km persegi, sekitar 3,6 kali
lebih kecil daripada AOI. Kelebihan itu disengaja: mesin routing membutuhkan
jaringan jalan di luar wilayah tergenang untuk menghitung rute memutar.

Akibatnya yang harus diingat: sebagian besar ruas di dalam AOI adalah jalan
permukiman di darat yang tidak pernah tergenang. Statistik apa pun yang
dihitung atas seluruh AOI akan terlihat jauh lebih optimistis daripada
kenyataan di enam kelurahan pesisir.

---

## 4. Batasan fitur — yang ditunda

Cakupan seluruh kota; moda transit dan pejalan kaki; laporan genangan
real-time dari warga; dashboard khusus BPBD dan Dishub; notifikasi push;
model hidrodinamik penuh; integrasi data lalu lintas real-time; akun pengguna
dan riwayat perjalanan.

---

## 5. Batasan operasional

### 5.1 Tidak ada data lalu lintas real-time

Waktu tempuh dihitung dari kecepatan bebas hambatan yang dikoreksi genangan.
Kemacetan biasa tidak diperhitungkan sama sekali. Pada jam sibuk di Kaligawe,
selisih antara estimasi dan kenyataan bisa besar.

### 5.2 Graf jalan adalah potret sesaat

Jaringan jalan diunduh sekali dari OpenStreetMap pada 24 Agustus 2026 lalu
disimpan. Jalan baru, penutupan, dan perubahan arah setelah tanggal itu tidak
terlihat sampai skrip dijalankan ulang. Ini konsekuensi yang disengaja dari
aturan jalur demo offline.

Sejak M3, mesin perutean membangun grafnya dari tabel `ruas_jalan` dan bukan
dari berkas GraphML, sehingga aplikasi yang berjalan cukup membawa database.
GraphML hanya dibutuhkan skrip 02 saat data disiapkan.

### 5.3 Kelengkapan OpenStreetMap tidak seragam

Dari 19.394 ruas, 6.518 tidak punya nama jalan. Jalan kampung memang jarang
dipetakan selengkap jalan arteri. Peringatan paparan yang menyebut nama jalan
karena itu tidak selalu bisa menyebutkan nama.

### 5.4 Prediksi hanya disimpan untuk ruas yang tergenang

Tabel `prediksi_genangan` tidak menyimpan baris untuk ruas kering. Ruas tanpa
baris terbaca sebagai kering lewat LEFT JOIN. Konsekuensinya sistem tidak bisa
membedakan "diprediksi kering" dari "belum ada prediksi". Untuk data contoh
tidak masalah; saat model asli masuk, keputusan ini perlu ditinjau ulang.
