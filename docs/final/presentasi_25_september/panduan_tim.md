# Panduan tim untuk final 26 September

Pakai [PPTX revisi 25 September](Pasang_Surut_Final_2026_25Sep.pptx). Target
sembilan menit, termasuk demo. Batas resmi sepuluh menit. Catatan pembicara
tersimpan di PPTX dan [naskah terpisah](catatan_pembicara.md); pahami maksudnya,
lalu ucapkan dengan gaya sendiri. Jangan membacakan setiap tulisan di layar.

## Rundown dan persiapan

TM halaman 9 mencantumkan **showcase 08.50-09.20, presentasi tim 1
09.20-09.30, dan tanya jawab 09.30-09.45 WIB**. Tim ini mendapat urutan 1.
TM halaman 6 memberi jatah persiapan lima menit, tetapi rundown tidak
menuliskan slot persiapan tim 1 secara terpisah. Koordinasikan transisi
perangkat dengan MC di lokasi; jangan mengandalkan slot 09.15 yang tidak
tercantum. Kehadiran lengkap dan konfirmasi panitia sudah diterima.

**Usulan persiapan pukul 08.20**, 30 menit sebelum showcase, jika akses
ruangan memungkinkan: buka aplikasi publik, lakukan satu pencarian, dan
siapkan tab lokal beserta PPT. Ini waktu internal tim, bukan jam panggilan
resmi. Ping dari laptop sesuai kebiasaan tim cukup untuk memantau layanan;
jangan mengulang uji beban ketika acara. Demo lokal tetap perlu siap meski
halaman publik sudah terbuka.

| Anggota | Saat presentasi | Sebelum tampil |
|---|---|---|
| Dzaky | Pembuka, metode, bukti; menjawab data/backend | Pastikan potret dan sumber angka cocok; jalankan API lokal |
| Daffa | Alur, demo, operasi perpindahan aplikasi | Jalankan frontend; uji slide cadangan, layar dan QR |
| Naufal | Dampak, rencana uji dan penutup | Jaga waktu, simpan salinan berkas, urus informasi pengumpulan |

Ini pembagian latihan yang diusulkan, belum keputusan tugas yang pernah
dikonfirmasi tim. Anggota yang sedang tidak berbicara tidak memotong
jawaban; tambahkan bukti sesudah rekannya selesai.

Pada jatah persiapan perangkat: pasang daya/adaptor, cek layar juri dan
Presenter View, matikan notifikasi, buka tab lokal yang sudah hangat, lalu
uji tombol kembali ke slide 5. Bawa PPTX, kedua PDF, dan video pameran pada
dua laptop/media cadangan. Pastikan ukuran teks terbaca dari belakang.

## Menyalakan demo lokal

Dependency laptop cadangan harus terpasang sebelum berangkat. Dari akar
repo, buka dua terminal:

```powershell
# Terminal 1: API potret tanpa database.
.\.venv\Scripts\python.exe deploy/demo_lokal.py
```

```powershell
# Terminal 2: frontend khusus demo lokal.
Set-Location frontend
npm.cmd run dev -- --config ../deploy/demo.vite.mjs --configLoader runner
```

Buka `http://127.0.0.1:5182`. API berada di `127.0.0.1:8012`. Konfigurasi
ini mengabaikan DATABASE_URL dan tidak menulis database. Jika port sudah
dipakai oleh demo yang aktif, gunakan proses tersebut; jangan menghentikan
proses lain. Hentikan dua terminal demo dengan `Ctrl+C` setelah selesai.

Potret memuat 26 September 00.00 sampai 28 September 23.00 WIB; batas
eksklusifnya 29 September 00.00 WIB. Versi yang dipakai deck:
`919aa345-7492-4a53-9e7c-c34086775d18`. Halaman Vercel yang tersimpan dalam
cache browser tidak menggantikan API lokal. Jangan melakukan seed atau
mengganti data menjelang tampil tanpa mengulang pemeriksaan angka.

## Demo 2 menit 25 detik pada slide 4

Tab lokal sudah terbuka sebelum presentasi. Gunakan motor, **26 September**,
asal **Stasiun Semarang Tawang**, tujuan **Kawasan Industri Terboyo**. Titik
tersebut adalah akses hasil pelekatan ke graf, bukan pintu masuk tersurvei.

| Waktu demo | Aksi Daffa | Pesan utama |
|---|---|---|
| 00-20 detik | Alt+Tab ke lokal | Sebut tanggal dan potret yang dapat diulang |
| 20-65 detik | Pilih asal/tujuan, motor, 08.00 | 13,9 menit; 10,58 km; peringatan tetap muncul |
| 65-105 detik | Geser ke 13.00, tunggu hasil | 7,0 menit; 6,32 km; nol ruas basah menurut model |
| 105-130 detik | Bandingkan kedua pilihan | Jadwal tetap: baca biaya memutar. Jadwal fleksibel: bandingkan jam lain |
| 130-145 detik | Kembali ke slide 5 | Serahkan penjelasan metode kepada Dzaky |

Pita dimulai dari 00.00 WIB. Fokus penggeser, tekan `Home`, lalu panah kanan
delapan kali untuk 08.00; tambah lima kali untuk 13.00. Pastikan angka pada
hasil sudah berubah sebelum menjelaskan. Pada 26 September tim memilih
peta OSM/CARTO untuk aplikasi. Gambar deck tetap peta lokal sebelumnya;
angka/geometri potret diuji ulang dan tetap sama. Saat CARTO tidak tersedia,
peta lokal cadangan digunakan. Lihat [catatan rilis](../peta_osm_final_26_september.md).

**Jika satu permintaan tertahan sepuluh detik**, langsung kembali ke PPT,
ketik `11` + Enter, lanjut `12` + Enter, kemudian `5` + Enter. Kedua gambar
cadangan menampilkan skenario yang sama. Katakan, “Kita lanjut dengan
tangkapan hasil dari potret yang sama.” Jangan menambah waktu dengan
mengulang request atau membuka log di depan juri. Di PDF, gunakan versi
lengkap untuk mengakses halaman 11/12.

QR mengarah ke aplikasi publik: `https://pasang-surut.vercel.app/app`.
Data publik dapat berganti sehingga angka tidak dijanjikan selalu identik
dengan potret. Juri bisa mencoba publik saat showcase atau Q&A; jelaskan
tanggal/sumber hasil yang sedang terlihat.

## Latihan terakhir dan pengaturan waktu

Lakukan dua latihan penuh: pertama untuk alur dan perpindahan pembicara,
kedua dengan satu gangguan demo yang disengaja. Ukur sampai ucapan penutup,
termasuk Alt+Tab dan menunggu hasil. Sasaran selesai 09:00, batas 10:00.
Naskah utama sekitar 742 kata; tindakan demo, jeda dan menunjuk bukti turut
memakai waktu. Jangan menganggap jumlah kata sebagai bukti durasi nyata.

Jika demo selesai lewat 04:30, singkatkan penjelasan cara mengoperasikan
layar, lalu lanjut. Jika pada 08:30 masih di roadmap, cukup sampaikan
“Berikutnya kami menguji pemahaman pengguna dan memvalidasi genangan per
ruas,” lalu penutup. Jangan menghapus keterangan estimasi atau mengganti
keterbatasan data dengan klaim aman agar presentasi terdengar lebih kuat.

Yang masih perlu dilakukan tim:

- Tetapkan pembicara/operator, lakukan dua latihan dengan stopwatch.
- Coba proyektor/adaptor, QR dengan HP, serta perpindahan aplikasi di laptop
  yang dibawa. Uji lokal dengan jaringan laptop dimatikan secara nyata.
- Salin berkas ke laptop cadangan dan media kedua; cek bisa dibuka di sana.
- Tanyakan deadline dan jalur pengumpulan PDF kepada panitia. Informasi
  deadline belum ada pada dua PDF acuan maupun konfirmasi terakhir.

## Showcase: kunjungan juri paling lama lima menit

Putar [video branding 105 detik](../pameran/branding/README.md) berulang saat
pengunjung lewat. Ketika juri datang, utamakan percakapan dan kesempatan
mencoba. Video tidak perlu diputar penuh dalam presentasi sepuluh menit.
Video versi 24 September belum membawa evaluasi pasut baru 25 September;
pakai slide 6/14 atau laporan audit saat membahas hasil terbaru.

| Durasi kunjungan | Kegiatan |
|---|---|
| 00:00-00:40 | Cerita singkat perjalanan Tawang ke Terboyo dan pilihan jam |
| 00:40-02:40 | Ajak juri memilih tujuan dan menggeser waktu sendiri |
| 02:40-03:30 | Baca perubahan rute, peringatan dan biaya memutar bersama |
| 03:30-04:20 | Terangkan sumber data, status estimasi dan bukti yang tersedia |
| 04:20-05:00 | Jawab pertanyaan, tunjukkan QR dan tautan kode |

Ini alokasi latihan, bukan aturan urutan interaksi. Jika juri bertanya
lebih awal, ikuti pertanyaannya. Hindari promosi “pasti bebas rob” atau
“akurasi 83,4%”. Poster kompetisi dan kelengkapan pameran lainnya tetap
mengikuti daftar kesiapan tim; paket PPT ini tidak menggantikannya.

## Bekal jawaban juri

Jawab inti pertanyaan dalam 20-30 detik, baru buka lampiran jika dibutuhkan.
Jika bukti belum ada, sebutkan pekerjaan yang diperlukan untuk mendapatkannya.

**1. Apa bedanya dengan aplikasi peta yang sudah ada?** (slide 3-4, Daffa)

“Fokus prototipe kami adalah membandingkan rute dan jam pada skenario rob
pesisir Semarang, sambil memperlihatkan biaya memutar dan sumber estimasinya.
Kami belum melakukan studi pembanding fitur menyeluruh atau uji pengguna
terhadap aplikasi lain, jadi keunggulan kegunaannya masih perlu diuji.”

**2. Apakah genangan yang ditampilkan benar terjadi?** (13/15, Dzaky)

“Belum dapat dipastikan per ruas. Jalan berasal dari OSM; tiga fitur wilayah
membentuk indeks, lalu pasut dan aturan internal menghasilkan estimasi
genangan. Pengukuran ruas dengan lokasi, waktu dan kedalaman diperlukan
untuk menguji hasil itu. Angka di layar belum menjadi dasar jaminan aman.”

**3. Mengapa masih memakai data 2014 dan 2015-2018?** (13/14, Dzaky)

“Itu sumber yang berhasil kami lacak dan implementasikan untuk prototipe.
Pasutnya sudah dibandingkan dengan pengamatan September 2026, tetapi
subsidensi lama belum diganti pengukuran terbaru. Uji pasut tidak membenarkan
seluruh masukan lain. Pembaruan dan validasi lapangan menjadi prioritas.”

**4. Jadi akurasinya berapa?** (14, Dzaky)

“Pada pasut di stasiun, korelasi 0,834 dan RMSE simpangan 12,44 cm dari
10.020 rekaman satu minggu. Kedua deret dikurangi rata-ratanya karena datum
berbeda. Itu bukan persentase akurasi atau akurasi kedalaman di jalan.
Genangan per ruas belum punya ukuran akurasi; data IOC juga belum melalui
pemeriksaan mutu.”

**5. Mengapa modelnya bukan machine learning? Apakah berubah dari proposal?** (15, Dzaky)

“Eksperimen Sentinel-1 sudah dicoba, tetapi label dan hasilnya tidak cukup
baik untuk dijadikan prediktor rilis. Karena itu yang aktif adalah indeks
berbobot, dan klaim kami dibatasi. Riwayat hasil eksperimen serta addendum
tersedia. Indeks ini juga perlu validasi; pemilihannya tidak otomatis
membuat estimasi genangan benar.”

**6. Apakah algoritmenya memberi rute optimal?** (15/17, Dzaky)

“Dalam model sekarang, kondisi jam keberangkatan dipakai tetap sepanjang
pencarian. Hasil diuji dengan pembanding Bellman-Ford pada 2.400 pencarian
di 40 graf kecil. Itu menguji routing dengan bobot tetap, belum membuktikan
optimalitas ketika genangan berubah selama kendaraan berjalan.”

**7. Kok rute sadar rob masih lewat genangan?** (11/15, Daffa)

“Skenario 08.00 masih menghasilkan 14 ruas yang ditandai basah dan maksimum
estimasi 24,8 cm. Karena itu panel tetap memberi peringatan. Rute tersebut
adalah keluaran biaya model dan batas moda, bukan rekomendasi bahwa pengguna
pasti boleh melintas. Kondisi lapangan tetap perlu diperiksa.”

**8. Mengapa sesuai tema rendah karbon kalau emisinya naik?** (7/18, Naufal)

“Pada contoh pagi ini, biaya menghindari sebagian paparan memang menambah
jarak dan estimasi CO₂. Kami memperlihatkan konsekuensinya agar pengguna
bisa membandingkan perjalanan dan waktu. Penghematan nyata belum diukur.
Kaitan tema ada pada keputusan energi perjalanan; kami belum membuktikan
dampak kesehatan atau pengurangan emisi tingkat kota.”

**9. Apakah harus menunggu lima jam? Dari mana BBM dihitung?** (7/18, Naufal)

“Jam 08.00 dan 13.00 adalah dua contoh perbandingan, bukan anjuran wajib
menunggu. Pilihan jam hanya relevan jika jadwal fleksibel; biaya menunggu
belum dihitung. Tambahan jarak dikalikan asumsi konsumsi motor 0,020 L/km
dengan sensitivitas ±30%, lalu 2,31 kg CO₂/L. Itu emisi pembakaran dan belum
hasil pengukuran kendaraan pada perjalanan ini.”

**10. Sudah diuji pengguna atau punya mitra?** (8, Naufal)

“Belum ada uji pengguna nyata atau mitra aktif yang kami klaim. Rencana
pertama adalah uji tugas 5-8 calon pengguna: pilih tujuan, ubah jam, dan
jelaskan kembali arti estimasi serta peringatan. Kami akan mencatat tugas
selesai, waktu, kesalahan, dan salah tafsir sebelum memperluas pemakaian.”

**11. Mengapa server sebelumnya gagal; apakah sekarang tahan banyak pengguna?** (16, Dzaky)

“Render mencapai batas 512 MB. Kami memperbaiki pemakaian graf/cache dan
membatasi request berat, lalu memindahkan layanan ke VPS. Audit 412 request
selama 94,47 detik tidak menemukan OOM/restart; 32 request mendapat respons
sibuk terkendali. Itu bukti pada jendela uji, bukan SLA atau kapasitas
maksimum. Origin HTTP sementara masih perlu penguatan setelah final.”

**12. Bisa dipakai terus selama tiga tahun?** (13, Dzaky)

“Belum dengan data beku sekarang. Saat audit, cakupan produksi berakhir
5 Oktober 2026 pukul 07.00 WIB dan belum ada penerbit data permanen. Perlu
pembaruan terjadwal, pemeriksaan mutu, validasi ruas, pemantauan layanan,
dan izin sumber sesuai penggunaan. Memperpanjang timestamp saja tidak
memperbarui kondisi fisik Semarang.”

**13. Mengapa kode dan demo lokal mudah diperiksa?** (17, Dzaky/Daffa)

“Perhitungan domain, validasi API, dan antarmuka dipisah. Repo memuat tes
regresi, pipeline, data olahan, dan panduan demo dengan potret tetap.
Kesamaan hasil dapat dibandingkan ulang. Raster mentah dan kredensial
tidak dimasukkan repo. Tautan kode tersedia di slide ini.”

Seluruh angka jawaban mengikuti [pemetaan bukti](acuan_dan_sumber.md).
Jangan menambah klaim klinis, jaminan keselamatan, testimoni, atau angka
adopsi ketika menjawab spontan.
