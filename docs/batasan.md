# Batasan yang diketahui

**Pembaruan runtime 21 September 2026:** perutean memakai kondisi jam
keberangkatan tetap sepanjang satu pencarian. Optimalitas hanya untuk model
biaya tetap tersebut; perubahan kondisi selama perjalanan belum dimodelkan.
Data tanpa cakupan lengkap ditolak. Potret final bertanggal 26–28 September,
bukan pembacaan genangan langsung. Elevasi relatif memakai median lingkungan
3 × 3 sel grid bersisi 500 m; angka akurasi rekonstruksi pasut tidak berlaku
sebagai akurasi genangan per ruas. Lihat [hasil implementasi](final/hasil_21_september.md).

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

### 2.1 Model genangan Sentinel-1 dilatih, lalu DITOLAK sendiri

Model berbasis 725 citra Sentinel-1 sudah dilatih. Hasilnya tidak dipakai,
dan itu keputusan sadar. Angka lengkapnya di `docs/validasi.md` bagian 6.

Alasannya satu kalimat: **label basah yang dibuat dari penurunan backscatter
VV tidak berkorelasi dengan pasut sama sekali** (aturan "pasut saja"
menghasilkan ROC-AUC 0,4935, setara lemparan koin), dan pada 12 citra yang
jatuh di tanggal kejadian rob terdokumentasi tandanya justru terbalik. Yang
dipelajari model adalah ruas mana yang sering beranomali, bukan kapan ruas
tergenang — dan seluruh guna sistem perutean terletak pada kata "kapan".

ROC-AUC 0,6579 yang dicapai model itu hampir seluruhnya berasal dari fitur
statis. Kepentingan permutasi tiga fitur waktu: pasut +0,0010 ± 0,0014,
hujan 24 jam +0,0004 ± 0,0010, hujan 72 jam −0,0026 ± 0,0011. Ketiganya nol
dalam batas ketidakpastiannya.

Tiga upaya penyelamatan dijalankan sebelum model ditinggalkan, dan ketiganya
gagal: pencuplikan radius 100 meter (ROC-AUC turun ke 0,5982), kriteria dua
arah untuk menangkap pantulan ganda (paling kuat hanya 0,47 simpangan baku),
dan pengukuran luas air kawasan terbuka (korelasi terhadap pasut justru
negatif). Rinciannya di `docs/validasi.md` bagian 6.5.

`PLAN.md` bagian 9.A menyiapkan jalur cadangan untuk keadaan ini. Sistem
memakainya. Klaim produk TIDAK diturunkan menjadi sekadar indeks: yang
diklaim sekarang adalah memprediksi KAPAN tiap ruas berisiko, dengan komponen
waktu dari rekonstruksi pasut yang tervalidasi terhadap data terukur dan
komponen ruang dari indeks kerentanan. Yang gugur hanyalah klaim bahwa
prediksi itu dipelajari dari genangan teramati Sentinel-1.

**Satu keterbatasan yang berlaku untuk seluruh pengujian di atas.**
Rekonstruksi pasut yang dipakai sebagai pembanding hanya memuat komponen
ASTRONOMIS. Rob sesungguhnya terjadi saat pasang astronomis bertemu kenaikan
muka air akibat angin, tekanan udara, dan gelombang badai, dan komponen itu
tidak ada di dalam rekonstruksi kami. Sebagian ketiadaan korelasi bisa saja
berasal dari pembandingnya, bukan dari labelnya.

### 2.2 Indeks kerentanan tidak punya akurasi yang bisa dilaporkan

Yang dipakai sekarang adalah indeks berbasis aturan dari tiga besaran:
elevasi relatif, jarak ke pantai, dan laju subsidensi, masing-masing
berbobot sepertiga.

**Tidak ada satu pun angka akurasi untuk indeks ini, dan tidak akan ada
sampai ada pengamatan genangan per ruas.** Pemeriksaan terhadap jalan yang
dilaporkan tergenang di media memang memberi hasil yang bagus — Bandarharjo
persentil 97,7, Kaligawe 90,5 — tetapi pemeriksaan itu **melingkar**:
kawasan yang dilaporkan seluruhnya pesisir, dan jarak ke pantai adalah salah
satu komponen indeks. Ia menunjukkan kodenya tidak keliru, bukan indeksnya
benar.

Bobot sepertiga itu sendiri asumsi. Tidak ada data untuk menyetelnya, dan
menyetel tanpa data uji hanya menyembunyikan tebakan di balik desimal.

### 2.3 Kedalaman sentimeter adalah asumsi berlapis dua

Angka sentimeter yang dilihat pengguna lahir dari `app/domain/genangan.py`,
yang memetakan indeks dan tinggi pasut ke rentang 10 sampai 50 cm.

Dua lapis asumsi menumpuk di sini. Pertama, batas 10 dan 50 cm berasal dari
aturan repo nomor 4, bukan dari pengukuran kami. Kedua, bobot 50 berbanding
50 antara indeks dan pasut tidak dikalibrasi terhadap apa pun, karena tidak
ada satu pun pengukuran kedalaman genangan di repo ini.

Berapa banyak ruas yang terdampak diikat ke perkiraan WRI Indonesia bahwa
sekitar 10 persen jaringan jalan Kota Semarang berpotensi terdampak rob.
Angka itu se-kota sementara AOI ini bagian terparahnya, jadi pemakaiannya
konservatif — tetapi tetap angka pinjaman, bukan hasil hitungan sendiri.

**Setiap tampilan kedalaman wajib menyebut kata estimasi.** Aturan repo
nomor 3.

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

### 2.6 Angka bahan bakar dan emisi memakai faktor rata-rata per moda

Panel dampak menghitung liter dan kilogram CO2 ekuivalen dari dua faktor di
tabel `ambang_moda`: konsumsi per kilometer dan faktor emisi per liter.

**Konsumsi per kilometer masih asumsi tanpa sitasi.** Angkanya setara 50 km
per liter untuk motor, 11,1 untuk mobil, dan 4,0 untuk truk. Nilai itu masuk
akal, tetapi masuk akal bukan sitasi. Sampai sumbernya ada, angka dampak
disajikan sebagai RENTANG dengan lebar ±30 persen, dan lebar itu sendiri juga
asumsi yang dinyatakan sekali di `KETIDAKPASTIAN_KONSUMSI`.

**Faktor emisi 2,31 kg CO2 per liter bensin dan 2,68 untuk solar** adalah
nilai baku pembakaran bahan bakar. Sitasi resminya belum dimasukkan ke repo;
`data/referensi/faktor_emisi.json` masih `null`.

Sejak M5 angka ini TAMPIL DI ANTARMUKA, tidak lagi hanya tersimpan di
database. Konsekuensinya sitasinya menjadi lebih mendesak, bukan kurang.

### 2.7 Peringatan paparan memakai ambang moda yang juga asumsi

Peringatan kesehatan keluar bila rute sadar rob tetap menembus ruas dengan
kedalaman di atas `berisiko_cm`. Angka ambang itu berasal dari tabel
`ambang_moda` yang komentarnya di `db/schema.sql` sendiri menyebutnya asumsi.

Artinya kapan peringatan muncul dan kapan tidak bergantung pada angka yang
belum bersumber. Ambangnya sengaja dibaca dari tabel dan tidak pernah ditulis
tetap di kode, supaya koreksinya cukup satu baris SQL.

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
