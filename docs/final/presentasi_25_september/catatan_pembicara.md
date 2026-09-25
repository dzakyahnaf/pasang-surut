# Catatan pembicara

Pembagian latihan; target 9 menit. Belum hasil latihan tim dengan stopwatch.

## 01. Pembuka

00:00 sampai 00:30 | Dzaky

Selamat pagi, Bapak dan Ibu juri. Kami tim trio la albiceleste dari ITS. PASANG SURUT membantu pengendara membandingkan rute dan jam berangkat di pesisir Semarang. Hari ini kami memakai satu perjalanan, dari akses Stasiun Tawang menuju kawasan industri Terboyo. Dari perjalanan itu, kami akan memperlihatkan apa yang sudah bekerja dan batas data yang masih perlu kami perbaiki.

Aksi operator: Tunjuk Tawang dan Terboyo. Jangan membuka dengan daftar teknologi.

Sumber: README tim; data OSM; potret demo 26 September.

---

## 02. Kebutuhan perjalanan

00:30 sampai 01:20 | Dzaky

Tawang dan Terboyo berada di kawasan pesisir yang menjadi konteks proyek ini. Rob di Semarang juga masih masuk agenda penanganan pemerintah pada 2026. Kami mengambil kebutuhan yang sederhana: seseorang perlu menuju kawasan industri dengan motor. Kalau jam berangkatnya tetap, ia perlu memahami rute dan konsekuensi memutar. Kalau jadwalnya bisa digeser, ia ingin membandingkan jam lain. Ilustrasi ini belum kami uji lewat wawancara. Karena itu, kebutuhan dan kemudahan pemakaiannya tetap masuk rencana uji pengguna setelah final. Daffa akan memperlihatkan alur yang sudah bisa dicoba.

Aksi operator: Daffa menyiapkan tab lokal saat Dzaky berbicara. Perpindahan pembicara dilakukan setelah kalimat terakhir.

Sumber: BBWS Pemali Juana 15 Februari 2026; user mengonfirmasi belum ada uji pengguna pada 25 September.

---

## 03. Alur pemakaian

01:20 sampai 02:05 | Daffa

Di layar ini, pengguna memilih titik berangkat, tujuan, dan kendaraan. Empat akses tempat sudah tersedia sebagai pilihan cepat. Pita Pasut di bawah mengatur jam yang dibandingkan. Setelah jam berubah, peta dan hasil rute ikut dihitung. Panel kiri memperlihatkan waktu tempuh dan peringatan; selisih jarak serta bahan bakar bisa dibaca pada panel biaya. Nama tempat membantu orientasi, tetapi titik aksesnya masih hasil pelekatan ke jaringan jalan. Sekarang kita coba perjalanan yang sama.

Aksi operator: Tunjuk lokasi kontrol, pita waktu, dan panel hasil. Tidak perlu membacakan seluruh teks pada screenshot.

Sumber: docs/final/presentasi/aset/demo_08.png; tujuan_cepat.geojson.

---

## 04. Demo dua jam

02:05 sampai 04:30 | Daffa

Kami memakai potret bertanggal 26 September agar hasil demo dapat diulang. Asal dan tujuannya tetap, dengan moda motor. Pada pukul delapan, rute sadar rob menghasilkan 13,9 menit untuk 10,58 kilometer. Peringatannya masih muncul karena rute ini tetap melewati ruas yang diberi genangan oleh model. Jadi, jangan membacanya sebagai jaminan aman.

Sekarang jamnya digeser ke pukul satu siang. Pada skenario ini hasilnya menjadi 7 menit dan 6,32 kilometer. Rutenya sama dengan pembanding, dan model tidak menandai ruas basah pada rute itu. Kondisi lapangan tetap perlu diperiksa. Kalau jadwal pengguna fleksibel, perbandingan seperti ini bisa menjadi bahan memilih jam. Kalau harus berangkat pagi, biaya memutarnya tetap terlihat. Dzaky akan menjelaskan bagaimana angka tadi dibentuk.

Aksi operator: 00-20 detik: Alt+Tab ke lokal yang siap. 20-65: Tawang, Terboyo, motor, jam 08.00 dan peringatan. 65-105: geser ke 13.00. 105-130: bandingkan pilihan. 130-145: kembali ke slide 5. Bila satu permintaan tertahan 10 detik, langsung buka slide 11 lalu 12; jangan mengulang-ulang request.

Sumber: aset/skenario.json pada paket 23 September; 919aa345-7492-4a53-9e7c-c34086775d18.

---

## 05. Metode aktif

04:30 sampai 05:30 | Dzaky

Ada dua jalur masukan. Kondisi wilayah membentuk indeks dari elevasi relatif, jarak pantai, dan laju penurunan tanah. Pasut dihitung per jam dari konstanta harmonik. Keduanya bertemu dalam aturan pemilihan ruas dan estimasi kedalaman, lalu dipakai mesin rute. Bobot tiga fitur sama besar. Proporsi puncak sepuluh persen dan kedalaman sepuluh sampai lima puluh sentimeter masih asumsi yang perlu diuji. Data subsidensi berasal dari 2015 sampai 2018, sedangkan konstanta pasut berasal dari 2014. Mesin rute memakai kondisi jam berangkat sepanjang perjalanan. Perubahan genangan ketika kendaraan sudah berjalan belum dimodelkan.

Aksi operator: Ikuti diagram dari kiri ke kanan. Jangan menyebut indeks sebagai probabilitas. Detail grid dan algoritme tersedia di lampiran 15.

Sumber: Audit data 25 September; script 11; backend/app/domain/{kerentanan,pasut,genangan,routing}.py.

---

## 06. Apa yang sudah dibuktikan

05:30 sampai 06:40 | Dzaky

Tes perangkat lunak memeriksa perilaku aplikasi: pencarian ulang, pergantian jam, dan penolakan waktu tanpa data. Pada audit VPS, 412 permintaan dijalankan selama sekitar satu setengah menit tanpa kehabisan memori atau restart. Ada respons sibuk yang memang dibatasi, jadi kami tidak menyebutnya semua permintaan berhasil.

Untuk pasut, kami membandingkan model yang dibekukan dengan 10.020 rekaman IOC pada 18 sampai 25 September. Korelasinya 0,834 dan RMSE simpangannya 12,44 sentimeter. Itu pengujian pasut di stasiun. Akurasi genangan tiap ruas belum tersedia, dan data IOC sendiri belum melalui pemeriksaan mutu. Uji pengguna juga belum dilakukan. Sesudah ini, Naufal akan membahas keputusan yang bisa dibaca dari contoh perjalanan tadi.

Aksi operator: Jangan mengubah korelasi menjadi persen akurasi. Rincian sensor di slide 14 dan beban VPS di slide 16.

Sumber: audit_regresi_22_verifikasi.json; uji_pasut_independen_25_september.json; konfirmasi pengguna 25 September.

---

## 07. Manfaat dan biaya adaptasi

06:40 sampai 07:40 | Naufal

Pada jam delapan, rute sadar rob mengurangi jumlah ruas yang ditandai basah dalam model, dari 29 menjadi 14. Jaraknya justru bertambah 4,27 kilometer dan waktunya bertambah 6,9 menit. Artinya, menghindari sebagian paparan punya biaya. Estimasi bahan bakar dan CO₂ juga bertambah pada pilihan ini. Kalau jadwalnya fleksibel, pengguna bisa membandingkan jam satu siang. Menunggu lima jam tentu punya biaya jadwal yang belum kami hitung. Kaitan kami dengan Smart Low-Carbon Urban Mobility ada pada pembacaan konsekuensi energi dari pilihan perjalanan. Penghematan nyata baru bisa dinilai setelah ada perjalanan pengguna dan pembanding yang diukur.

Aksi operator: Tunjuk baris 08.00 dulu, lalu 13.00. Sebut CO₂ pembakaran, bukan CO₂e. Jangan menyebut rute 13.00 pasti kering.

Sumber: aset/skenario.json; backend/app/domain/dampak.py; subtema 4 rulebook halaman 3.

---

## 08. Rencana validasi berikut

07:40 sampai 08:35 | Naufal

Langkah terdekat kami adalah uji tugas dengan lima sampai delapan calon pengguna. Yang dicari bukan sekadar pendapat bagus atau buruk. Kami ingin melihat apakah mereka bisa memilih tujuan, mengganti waktu, dan memahami bahwa kedalaman pada layar masih estimasi. Secara paralel, diperlukan pengamatan ruas dengan lokasi, jam, dan kedalaman yang jelas. Data itu dipisahkan untuk pengembangan dan pengujian. Pembaruan pasut serta data jalan juga perlu dijadwalkan. Aplikasi tidak bisa ditinggal dengan data beku selama tiga tahun. Kerja sama dengan pemilik data dan pengguna masih perlu dijajaki; belum ada mitra aktif yang kami klaim.

Aksi operator: Jangan menyebut target sebagai komitmen peserta. Bila waktu sudah 08.30, pakai dua kalimat: uji pengguna dan validasi ruas, lalu lanjut penutup.

Sumber: User mengonfirmasi belum ada uji pengguna; audit_asal_data_25_september.md.

---

## 09. Penutup

08:35 sampai 09:00 | Naufal

PASANG SURUT sudah bisa dipakai untuk mencoba satu perjalanan dan membandingkan pilihan waktunya. Pengujian genangan lapangan menjadi pekerjaan berikutnya. Aplikasi, kode, dan bukti pengujian kami buka melalui tautan ini. Terima kasih, Bapak dan Ibu juri. Kami siap membahas pertanyaan atau mencoba skenario lain bersama.

Aksi operator: Berhenti pada slide ini. Jangan lanjut otomatis ke lampiran. Bila juri ingin detail, klik menu lampiran atau ketik 10 lalu Enter.

Sumber: Alamat publik aplikasi dan repo.

---

## 10. Navigasi lampiran

Lampiran untuk tanya jawab | Sesuai topik

Jawab singkat dahulu, lalu buka bukti yang diminta. Data dan metode ke Dzaky; demo dan antarmuka ke Daffa; dampak serta rencana uji ke Naufal. Anggota lain menambahkan setelah pembicara selesai.

Aksi operator: Satu pembicara menjawab satu pertanyaan. Jangan membuka semua lampiran secara berurutan.

Sumber: Menu internal PPT.

---

## 11. Cadangan demo 8.00

Lampiran untuk tanya jawab | Daffa

Ini tangkapan aplikasi dari potret yang sama dengan skenario presentasi. Pada 08.00, hasilnya 13,9 menit, 10,58 kilometer dan 14 ruas basah dalam model. Kedalaman maksimum model 24,8 sentimeter, sehingga peringatan tetap perlu dibaca.

Aksi operator: Gunakan bila live demo tertahan. Setelah halaman 12, kembali ke slide 5. Nomor 11 dan 12 dapat diketik langsung saat slideshow.

Sumber: docs/final/presentasi/aset/demo_08.png; demo_13.png; skenario.json.

---

## 12. Cadangan demo 13.00

Lampiran untuk tanya jawab | Daffa

Ini tangkapan aplikasi dari potret yang sama dengan skenario presentasi. Pada 13.00, hasilnya 7 menit, 6,32 kilometer dan nol ruas basah dalam model. Hasil ini menjadi bahan perbandingan waktu, bukan bukti jalan sedang kering.

Aksi operator: Gunakan bila live demo tertahan. Setelah halaman 12, kembali ke slide 5. Nomor 11 dan 12 dapat diketik langsung saat slideshow.

Sumber: docs/final/presentasi/aset/demo_08.png; demo_13.png; skenario.json.

---

## 13. Sumber dan keberlanjutan

Lampiran untuk tanya jawab | Dzaky

Sumbernya dapat ditelusuri, tetapi umurnya berbeda. Jalan diekstrak pada 2026, konstanta pasut berasal dari 2014, dan subsidensi memakai periode 2015 sampai 2018 pada tingkat kecamatan. Tahun akuisisi raster belum terverifikasi. Pasut sudah dibandingkan dengan rekaman September, tetapi genangan per ruas belum. Untuk tiga tahun operasi, kami perlu data yang diperbarui dan diuji berkala. Saat audit, produksi berakhir 5 Oktober 07.00 WIB; jadwal permanen penerbit data belum tersedia. IOC juga membatasi penggunaan komersial; rencana produk perlu pembicaraan dengan pemilik data.

Aksi operator: Bila juri meminta data mentah, buka tautan audit. Jangan mengekstrapolasi laju subsidensi lama secara linear lalu menyebutnya elevasi 2029.

Sumber: audit_asal_data_25_september.md; data/referensi; status_produksi_25_september.json.

---

## 14. Uji pasut independen

Lampiran untuk tanya jawab | Dzaky

Ada 10.020 rekaman sensor tekanan sema. Model lama dan offset tujuh jam dipertahankan. Korelasi 0,8340, RMSE simpangan 12,44 sentimeter, dan MAE 10,32 sentimeter. Titik nol alat dan rekonstruksi berbeda; setiap deret dikurangi rata-rata periode sebelum dibandingkan. Sensor pada layanan IOC belum melalui quality control, dan sampel yang berdekatan saling berkorelasi. Satu minggu ini tidak membuktikan ketelitian lintas musim, ketepatan tinggi absolut, atau akurasi genangan ruas. Uji Agustus memakai jendela yang ikut memilih offset, sehingga sifatnya berbeda dengan uji baru ini.

Aksi operator: Tunjuk selisih kurva di puncak. Jangan menyatakan r 0,834 sebagai akurasi 83,4%.

Sumber: data/uji_pasut_independen_25_september.json; CSV IOC; disclaimer IOC.

---

## 15. Model dan routing

Lampiran untuk tanya jawab | Dzaky

Indeks memakai tiga fitur sama besar, dinormalisasi dalam wilayah studi. Elevasi relatif memakai sembilan sel grid, bukan radius lingkaran. Indeks dan pasut lalu diubah menjadi estimasi genangan dengan parameter yang belum dikalibrasi. Hujan, debit sungai, pompa dan tanggul belum masuk rumus aktif. Model Sentinel-1 pernah dilatih, tetapi label dan hasilnya tidak layak dijadikan prediktor rilis. Routing sekarang menggunakan kondisi jam berangkat yang tetap agar konsisten. Uji 2.400 pencarian pada 40 graf kecil dibandingkan dengan Bellman-Ford menguji model bobot tetap itu; tidak membuktikan optimalitas pada genangan yang berubah selama perjalanan.

Aksi operator: Bila ditanya kenapa bukan AI, jelaskan keputusan berdasarkan hasil eksperimen. Jangan menyebut indeks sebagai model ML terlatih.

Sumber: backend/tests/test_routing_properti.py; metrik_model.json; domain routing dan kerentanan.

---

## 16. Hosting dan uji beban

Lampiran untuk tanya jawab | Dzaky / Daffa

Render sebelumnya restart karena melewati 512 MB. Perbaikan mencakup penggunaan bersama graf, pembatasan cache dan request berat, lalu migrasi layanan ke VPS yang diuji bertahap. Dalam audit tambahan, 412 permintaan selesai dengan status yang diharapkan: 316 berhasil, 32 sibuk, 58 payload terlalu besar, empat waktu atau koordinat di luar cakupan, dan dua masukan buruk. Tidak ada OOM atau restart dalam jendela 94,47 detik. Ini bukan janji kapasitas tanpa batas. Origin HTTP 18080 masih sementara; jalur origin terenkripsi dan penguatan operasional masuk pekerjaan setelah final. Layanan lain di VPS tidak diubah.

Aksi operator: Jika ditanya kecepatan maksimum atau SLA, jawab belum diukur. Angka audit memori berbeda dari audit sebelumnya karena kondisi cache berbeda.

Sumber: audit_regresi_22_requests.json; audit_regresi_22_verifikasi.json; deploy/vps/README.md.

---

## 17. Struktur kode dan reproduksi

Lampiran untuk tanya jawab | Dzaky / Daffa

Perhitungan berada di domain sehingga tidak harus diuji lewat tampilan peta. API memeriksa waktu, koordinat dan versi data. Frontend menangani permintaan yang dibatalkan saat jam berubah serta pencarian ulang. Backend memiliki tes regresi dan pembanding algoritme; CI menjalankan tes pada lingkungan bersih. Data dan script pipeline terpisah dari image API. Untuk reproduksi demo, gunakan deploy/demo_lokal.py dan konfigurasi Vite khusus demo. Panduan backup dan pemulihan database ada pada deploy/vps. Repositori terbuka bagi juri.

Aksi operator: Klik direktori yang ditanyakan saja. Jangan melakukan deploy, migrasi, atau tes beban baru di depan juri.

Sumber: README; backend/app; backend/tests; frontend/src/App.test.jsx; .github/workflows/uji.yml; deploy/vps.

---

## 18. Asumsi BBM dan emisi

Lampiran untuk tanya jawab | Naufal / Dzaky

Selisih jarak dikalikan konsumsi wakil moda, lalu faktor pembakaran. Untuk motor digunakan 0,020 liter per kilometer dengan rentang sensitivitas tiga puluh persen, dan faktor 2,31 kilogram CO₂ per liter bensin. Ada penjelasan literatur faktor di docs/sumber_angka.md, tetapi konsumsi kendaraan dan rentang sensitivitas tetap asumsi rilis, bukan hasil pengukuran perjalanan ini. CO₂ tersebut tidak mencakup gas lain atau daur hidup. Kami belum punya dasar untuk mengubah hasil satu skenario menjadi penghematan satu kota atau dampak kesehatan terukur.

Aksi operator: Gunakan tanda tambah ketika membicarakan skenario 08.00. Jangan menyebut biaya menghindar sebagai penghematan.

Sumber: backend/app/domain/dampak.py; docs/sumber_angka.md; db/schema.sql; aset/skenario.json.
