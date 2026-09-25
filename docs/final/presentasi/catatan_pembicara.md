# Catatan pembicara PASANG SURUT

Usulan pembagian; target 9 menit, maksimum 10 menit.

01 — Masalah pengguna
WAKTU: 00.00–00.45 (45 detik)
PEMBICARA (usulan): Dzaky

Bayangkan seorang pengendara yang perlu berangkat dari sekitar Tawang menuju kawasan industri Terboyo. Pada kawasan pesisir, pilihannya tidak berhenti pada “jalan mana yang paling cepat”. Ia juga perlu mempertimbangkan jam berangkat dan kondisi ruas yang dilalui.
PASANG SURUT membantu membandingkan pilihan perjalanan itu. Kami fokus pada pesisir Semarang, dengan tujuan agar waktu, rute, dan konsekuensi memutar dapat dibaca dalam satu alur.
Skenario ini ilustrasi kebutuhan pengguna, bukan kutipan wawancara atau bukti aplikasi sudah dipakai warga. Penanda pada peta adalah akses jaringan jalan, bukan pintu bangunan yang telah diverifikasi.

SUMBER: data/processed/tujuan_cepat.geojson; ruas_jalan.geojson; garis_pantai.geojson; proposal tim.

---

02 — Nilai produk
WAKTU: 00.45–01.30 (45 detik)
PEMBICARA (usulan): Dzaky

Ada tiga informasi yang kami satukan. Pertama, asal–tujuan dan kendaraan, karena batas motor berbeda dengan mobil. Kedua, waktu keberangkatan yang dapat digeser untuk membandingkan kondisi model. Ketiga, konsekuensi rute yang dipilih: tambahan waktu, jarak, serta estimasi biaya bahan bakar dan emisi.
Sumber yang aktif adalah indeks kerentanan; kedalaman yang terlihat bukan hasil pengukuran langsung. Karena itu aplikasi juga menampilkan sumber, waktu data, dan peringatan paparan.
Daffa akan memperlihatkan satu perjalanan yang sama pada dua jam berbeda.

SUMBER: frontend/src/components/PanelRute.jsx, PitaPasut.jsx, PanelDampak.jsx; copy.id.json.

---

03 — Demo
WAKTU: 01.30–04.30 (3 menit, termasuk perpindahan)
PEMBICARA (usulan): Daffa

00–30 detik: buka aplikasi yang sudah siap. Sebut Semarang, asal akses Tawang, tujuan akses Terboyo, moda motor, serta tanggal/sumber yang terlihat. Gambar di slide berasal dari potret lokal 26 September, bukan keadaan lapangan hari ini.
30–90 detik: pilih 26 September 08.00 WIB. Tunjukkan rute sadar rob 13,9 menit/10,58 km dan pembanding 7,0 menit/6,32 km yang mengabaikan genangan. Maksimum model pada rute sadar rob 24,8 cm; rute masih menembus ruas berisiko. Jangan sebut rute ini “aman”.
90–135 detik: geser ke 13.00 WIB. Tunggu pembaruan selesai. Pada potret ini rute sadar rob dan pembanding sama: 7,0 menit/6,32 km. Tidak ada genangan yang dimodelkan pada rute; ini tidak membuktikan jalan benar-benar kering.
135–165 detik: simpulkan pilihan yang dapat dipertimbangkan bila jadwal fleksibel, sambil tetap memeriksa kondisi lapangan. Waktu 7,0 menit adalah model kecepatan, bukan ETA lalu lintas langsung.
165–180 detik: kembali ke slide metode.
Jika produksi tertahan lebih dari sekitar 10 detik, gunakan lokal yang sudah menyala. Jika lokal gagal, buka slide 9 lalu 10 (nomor + Enter); kembali ke slide 4. Screenshot sudah tertanam. MP4 belum termasuk paket ini. Jangan menunggu server berulang kali.
Produksi memakai dataset berbeda dari potret; jangan menjanjikan angka persis sama. Untuk cerita yang konsisten, demo lokal potret adalah pilihan siap pakai; cek cakupan produksi sebelum tampil.

SUMBER: aset/demo_08.png; aset/demo_13.png; aset/skenario.json; data/processed/tujuan_cepat.geojson.

---

04 — Metode
WAKTU: 04.30–05.30 (60 detik)
PEMBICARA (usulan): Dzaky

Pasut memberi komponen waktu. Sementara itu, indeks kerentanan membedakan ruas berdasarkan elevasi relatif, jarak dari pantai, dan laju subsidensi. Ketiga komponen memakai bobot sama sebagai asumsi, belum hasil kalibrasi genangan lapangan.
Kondisi per jam disiapkan dalam dataset, lalu API membandingkan rute sadar rob dan rute yang mengabaikan genangan. Klik pengguna tidak mengunduh ulang graf OSM atau melatih model. Browser membaca hasil dari API; dataset dapat berasal dari database VPS atau potret untuk demo lokal.
Untuk menghindari masalah pergantian jam pada algoritme lama, rilis final memakai kondisi jam keberangkatan sepanjang satu pencarian. Kami tidak mengklaim rute optimal terhadap kondisi yang berubah selama perjalanan.
Jika ditanya elevasi: median dari kumpulan 3 × 3 sel, sisi sel 500 meter. Ini bukan radius melingkar 500 meter.

SUMBER: backend/app/domain/kerentanan.py; backend/app/domain/routing.py; backend/app/runtime.py. OSM sebagai graf; DEMNAS sebagai fitur relatif.

---

05 — Bukti dan batasan
WAKTU: 05.30–06.30 (60 detik)
PEMBICARA (usulan): Dzaky

Ada dua lapis bukti yang perlu dibedakan. Pada perangkat lunak, 95 tes backend lulus di Windows dan container Linux. Frontend kini memiliki 26 tes setelah peringatan kedalaman di panel rute dikoreksi. Salah satu tes backend membandingkan 2.400 pencarian pada graf kecil dengan Bellman-Ford; angka itu bagian dari tes, bukan tambahan 2.400 unit test.
Pada pasut, pilihan acuan WIB memberi korelasi 0,7821 dan RMSE 0,1155 meter dalam jendela sepuluh hari terhadap rekaman IOC. Perbandingan memakai simpangan muka air karena datum berbeda. Data tersebut juga digunakan untuk memilih acuan waktu, sehingga hasilnya bukan evaluasi independen pada data baru.
Kami belum punya pengamatan genangan per ruas untuk menguji indeks, dan belum punya bukti dampak perjalanan lapangan. Karena itu kami melaporkan kedalaman dan biaya sebagai estimasi serta menampilkan batasnya pada antarmuka.

SUMBER: docs/final/audit_regresi_22_september.md; frontend/src/App.test.jsx; data/referensi/kalibrasi_pasut.json (hipotesis_wib); docs/validasi.md §3.1.

---

06 — Dampak yang dapat dijelaskan
WAKTU: 06.30–07.30 (60 detik)
PEMBICARA (usulan): Naufal

Kami menyebut angka ini biaya adaptasi. Pembanding pukul delapan mengabaikan genangan: 7,0 menit dan 6,32 kilometer. Rute sadar rob memerlukan 13,9 menit dan 10,58 kilometer. Model menunjukkan jumlah ruas tergenang yang dilalui turun dari 29 menjadi 14, tetapi rute masih memiliki paparan. Jumlah ruas bukan pengukuran risiko atau lama paparan.
Memutar menambah sekitar 6,9 menit dan 4,27 kilometer. Dari asumsi konsumsi motor, itu setara tambahan 0,060 sampai 0,111 liter BBM serta 0,138 sampai 0,256 kilogram CO₂ pembakaran. Ini rentang asumsi, bukan interval kepercayaan dan bukan penurunan emisi yang sudah diukur.
Pada pukul tiga belas di potret ini, kedua rute sama dan model tidak memberi genangan di jalur. Bila jadwal fleksibel, informasi ini dapat menjadi bahan mempertimbangkan jam lain. Menunggu lima jam juga memiliki biaya jadwal yang belum kami hitung. Jangan menyebut selisih ini penghematan total atau dampak kota.

SUMBER: aset/skenario.json, motor, versi 919aa345-7492-4a53-9e7c-c34086775d18; backend/app/domain/dampak.py.

---

07 — Rencana pengembangan
WAKTU: 07.30–08.30 (60 detik)
PEMBICARA (usulan): Naufal

Tahap selanjutnya dimulai dengan uji tugas pada lima sampai delapan peserta yang relevan, misalnya pengendara atau pengiriman di wilayah pilot. Kami ingin mengukur apakah mereka dapat memilih asal–tujuan, membaca waktu, serta memahami bahwa peringatan adalah estimasi. Jumlah ini rencana, bukan peserta yang sudah diuji.
Berikutnya, kami memerlukan observasi ruas yang memiliki lokasi dan waktu jelas. Data baru dipisahkan untuk evaluasi, sehingga bobot dan estimasi tidak dinilai pada data yang sama dengan penyetelannya. Calon instansi atau komunitas belum disebut sebagai mitra aktif.
Secara operasional, kami perlu jadwal publikasi data, penanggung jawab pemeliharaan, pemantauan memori serta latensi, dan biaya hosting. Rilis saat ini belum punya scheduler publikasi otomatis. Perluasan wilayah dilakukan setelah bukti pada pilot membaik.

SUMBER: docs/final/outline_slide.md; docs/final/audit_regresi_22_september.md; rencana tim, belum hasil uji pengguna.

---

08 — Penutup
WAKTU: 08.30–09.00 (30 detik)
PEMBICARA (usulan): Naufal

PASANG SURUT membantu pengguna membandingkan rute, mempertimbangkan waktu, dan memahami konsekuensi perjalanan di pesisir Semarang. Produk yang kami tunjukkan sudah memiliki alur interaktif dan bukti pengujian perangkat lunak. Pengujian genangan dan dampak lapangan adalah langkah berikutnya.
Aplikasi dan kode tersedia melalui tautan ini. Kami siap menjelaskan implementasi serta batas bukti yang kami punya. Terima kasih.
Berhenti pada slide ini. Slide 9–14 adalah lampiran, bukan lanjutan presentasi utama. Untuk Q&A, ketik nomor slide lalu Enter. Pembagian pembicara adalah usulan; lakukan latihan bersama sebelum dibekukan.

SUMBER: https://pasang-surut.vercel.app/app; https://github.com/dzakyahnaf/pasang-surut

---

09 — Cadangan demo 08.00
WAKTU: Di dalam alokasi 3 menit demo bila diperlukan
PEMBICARA (usulan): Daffa

Gunakan narasi slide 3 untuk jam 08.00. Gambar asli tertanam; tidak memerlukan jaringan untuk ditampilkan. Sumber kerentanan_v1, versi potret 919aa345…; mode motor. Jangan menyebut angka ini observasi lapangan. Kembali ke slide 4 setelah kedua kondisi ditunjukkan.

SUMBER: aset/demo_08.png; aset/skenario.json.

---

10 — Cadangan demo 13.00
WAKTU: Di dalam alokasi 3 menit demo bila diperlukan
PEMBICARA (usulan): Daffa

Gunakan narasi slide 3 untuk jam 13.00. Gambar asli tertanam; tidak memerlukan jaringan untuk ditampilkan. Sumber kerentanan_v1, versi potret 919aa345…; mode motor. Jangan menyebut angka ini observasi lapangan. Kembali ke slide 4 setelah kedua kondisi ditunjukkan.

SUMBER: aset/demo_13.png; aset/skenario.json.

---

11 — Q&A pasut
WAKTU: Lampiran, di luar 9 menit
PEMBICARA (usulan): Dzaky

Nilai 0,7821 dan 0,1155 m berasal dari hipotesis WIB pada jendela 10 hari. Jangan tertukar dengan offset terbaik +8 jam yang menghasilkan r 0,8465/RMSE 0,097 m: sistem memilih +7 jam, bukan offset yang paling cocok pada sampel.
Jendela 2/4/7 hari pada docs/validasi.md memberi korelasi WIB 0,907/0,909/0,858. Jendela saling tumpang tindih, bukan empat uji independen. Rekaman IOC untuk 10 hari berjumlah 12.317. Karena datum berbeda, yang dibandingkan simpangan terhadap rata-rata.
Acuan dipilih menggunakan data yang sama; evaluasi ini bersifat kalibrasi/in-sample. Konstanta berasal dari rekaman 15 hari pada 2014, P1/K2 diturunkan dari komponen lain, dan koreksi nodal belum diterapkan. Belum ada klaim akurasi genangan per ruas.

SUMBER: data/referensi/kalibrasi_pasut.json; docs/validasi.md; backend/scripts/04_kalibrasi_pasut.py.

---

12 — Q&A indeks dan Sentinel-1
WAKTU: Lampiran, di luar 9 menit
PEMBICARA (usulan): Dzaky

Indeks memakai tiga skor relatif, dinormalisasi, dengan bobot sepertiga. Elevasi relatif adalah elevasi ruas dikurangi median dari anggota 3 × 3 sel grid dengan sisi 500 m. Nama metadata lama radius_elevasi_relatif_m dipertahankan pada artefak lama, tetapi bukan jendela Euclidean radius 500 m. Tinggi DEM tidak dipotong langsung dengan muka air untuk membuat genangan.
Eksperimen HistGradientBoostingClassifier dengan label perubahan VV Sentinel-1 tidak dipakai pada rilis. Angka uji berdasarkan split waktu tercatat apa adanya: ROC-AUC 0,6579, PR-AUC 0,0371, F1 0,0894. Kelas basah pada uji 1,6%; metrik klasifikasi label satelit tidak mengukur akurasi genangan jalan. Pengujian lanjutan label dan kaitan muka air tidak menghasilkan landasan yang cukup untuk memakai model sebagai prediksi rob.
Keputusan rilis adalah menampilkan indeks dengan batas klaim jelas. Kami masih memerlukan observasi genangan per ruas pada waktu tertentu untuk mengevaluasinya.

SUMBER: backend/app/domain/kerentanan.py; data/processed/indeks_kerentanan.json; data/referensi/metrik_model.json; uji_muka_air_terukur.json; docs/validasi.md.

---

13 — Q&A pengujian dan hosting
WAKTU: Lampiran, di luar 9 menit
PEMBICARA (usulan): Dzaky / Daffa

Insiden Render memakai lebih dari 512 MB dan restart. Rilis sekarang memakai VPS bersama, dengan isolasi container API 320 MiB, database 192 MiB, web 64 MiB, satu worker API, cache graf bersama, dan pembatasan dua request berat bersamaan.
Audit tambahan 22 September berisi 412 request dalam 94,47 detik: 316 HTTP200, 58 HTTP413, empat HTTP422, dua HTTP400, dan 32 HTTP503 sibuk yang diharapkan. Tidak ada respons tak terduga, OOM, restart, atau kenaikan failcnt. Puncak dari 188 sampel: API186,89; DB93,20; web51,71 MiB. Minimum RAM host tersedia645,92 MiB. Uji memakai guard sumber daya; bukan DDoS atau kapasitas maksimum.
Uji beban terdahulu 1.596 request selama7m41d juga tersedia di laporan terpisah; jangan menjumlahkan atau menyamakan puncak memori karena keadaan cache berbeda. Layanan Maknaprice tidak diubah; identitas container/config sama dan semua10 probe tambahan HTTP200.
95 tes backend mencakup satu tes properti dengan2.400 perbandingan pada40 graf kecil, bukan bukti optimalitas dinamis. Frontend26 tes per23 September. Batas20 detik request dan10 detik SQL bukan jaminan kecepatan. Browser fisik/proyektor tetap harus diuji tim.
Vercel adalah alamat masuk; runtime API/frontend/database ada pada VPS. Origin HTTP18080 bersifat sementara dengan izin pemilik. Kode audit main1651ad3; tag APIaudit22-11c58776b1ca. Koreksi copy panel23 September tidak mengubah algoritme backend.

SUMBER: docs/final/audit_regresi_22_september.md; docs/final/uji_beban_vps_22_september.md; backend/tests/test_routing_properti.py; frontend/src/App.test.jsx.

---

14 — Q&A dampak
WAKTU: Lampiran, di luar 9 menit
PEMBICARA (usulan): Naufal / Dzaky

Rumus dihitung atas selisih jarak dua rute. Nilai konsumsi motor0,020 L/km, rentang±30%, dan faktor2,31 kg CO₂/L dibaca dari konfigurasi rilis. Rentang tersebut adalah asumsi sensitivitas konsumsi; bukan rentang hasil pengukuran atau interval kepercayaan.
Repositori belum melengkapi sitasi faktor; data/referensi/faktor_emisi.json masih template null. Karena itu kami menyebutnya asumsi implementasi dan tidak mengklaim metodologi inventarisasi emisi yang tervalidasi. Jika ditanya dampak kota, jawab belum tersedia. Perlu data pemakaian, perjalanan nyata, kendaraan, baseline, dan biaya perubahan jadwal.
Istilah CO₂e tidak dipakai: faktor ini hanya pembakaranCO₂, tidak memasukkan gas lain atau siklus hidup. Ketika salah satu rute tidak tersedia, API mengembalikan dampak null, bukan “hemat nol”.

SUMBER: backend/app/domain/dampak.py; db/schema.sql; docs/batasan.md; data/referensi/faktor_emisi.json; aset/skenario.json.
