# Review branch, peta, dan presentasi — 23 September 2026

Review ini memeriksa delapan branch remote, enam PR yang pernah dibuat,
log kegagalan Vercel dari pengguna, rulebook final halaman 9–10, dan deck
8 + 6 slide. Rekomendasi isi PPT di bawah **belum mengubah berkas PPTX/PDF**.

## Email Vercel: kegagalan lama, penyebab sudah jelas

Preview commit `8d74b2f` gagal karena script menyalin
`dashboard/index.html`, tetapi berkas itu belum masuk tree Git commit
tersebut. `ENOENT` adalah berkas tidak ditemukan; log ini tidak menunjukkan
kehabisan RAM atau gangguan VPS. Mesin build memiliki 8 GB RAM, berbeda dari
insiden API Render 512 MB yang dibahas sebelumnya.

Commit `97d8408` menyertakan folder dashboard. Branch landing kemudian
digabung melalui [PR #4](https://github.com/dzakyahnaf/pasang-surut/pull/4).
Pemeriksaan ulang: build `node frontend/scripts/build-proxy.mjs` berhasil;
deployment main `3988c56` berstatus sukses; landing dan `/app` dapat diakses.
Email kegagalan deployment lama tetap menjadi riwayat, bukan indikator
bahwa main saat ini gagal. Menghapus branch tidak menghapus commit yang
sudah digabung, landing produksi, atau email/riwayat deployment lama.

## Hasil pemeriksaan dan pembersihan branch

Dasar pemeriksaan main: `3988c5673e5b3f1a33f6c242a7c8fe333a7242c9`.
Setiap branch yang dihapus lulus `merge-base --is-ancestor` dan tidak
memiliki commit unik terhadap main. Penghapusan remote dilakukan atomik
dengan lease pada SHA hasil audit; perubahan baru di remote akan membuat
penghapusan ditolak. Branch lokal yang ada dihapus dengan `git branch -d`.

| Branch | Status saat audit | Tindakan |
|---|---|---|
| `deploy/vps-uji-20260922` | Seluruh commit masuk main | Hapus remote dan lokal |
| `development-tahap-final` | Seluruh commit masuk main | Hapus remote; tidak ada branch lokal |
| `docs/presentasi-final-20260923` | PR #6 merged | Hapus remote dan lokal |
| `fix/regresi-final-20260922` | PR #5 merged | Hapus remote dan lokal |
| `test/stress-vps-20260922` | PR #2 merged | Hapus remote dan lokal |
| `vercel-landing-first` | PR #4 merged | Hapus remote; tidak ada branch lokal |
| `main` | Produksi dan materi final | Pertahankan |
| `preview/peta-dasar-osm` | Draft PR #3, pilihan visual belum diputuskan | Pertahankan branch, worktree, dan PR |

PR #1,2,4,5,6 sudah merged/tertutup. Branch PR #1 sudah lebih dulu dihapus;
referensi tracking yang tersisa dipangkas saat fetch. Tidak ada PR selesai
yang masih terbuka untuk ditutup ulang. Draft#3 sengaja tetap terbuka untuk
review peta tim. Laporan ini diterbitkan melalui PR dokumentasi tersendiri;
branch laporan dihapus setelah merge sehingga dua branch di atas tetap
menjadi keadaan akhir.

### Temuan CI selama review

Pada commit dokumentasi `8f45e57`, workflow push berhasil, tetapi workflow
PR gagal pada dua tes frontend. Tes pertama kehabisan waktu saat menunggu
kondisi awal; tes berikutnya lalu menerima mock galat yang belum terpakai.
Reproduksi kecil menunjukkan `mockClear()` mempertahankan antrean respons
`mockRejectedValueOnce`, sedangkan `mockReset()` membuangnya. Penyebab persis
lambatnya pemuatan pada runner pertama tidak dapat disimpulkan dari log.

Fixture sekarang memakai `resetAllMocks()` sebelum mengatur seluruh
respons, dan helper awal menunggu efek Promise melalui `act()` asinkron.
Assertion retry, pembatalan, pergantian jam dan versi tetap dipertahankan;
timeout tidak dinaikkan. Seluruh 26 tes frontend lulus lokal. Perubahan ini
hanya menyentuh tes; runtime/API dan layanan VPS tidak berubah. Bukti CI
akhir dapat dilihat pada checks PR laporan.

## Tautan untuk review tim

- [Peta main/produksi](https://pasang-surut.vercel.app/app).
- [Landing Daffa](https://pasang-surut.vercel.app/).
- [Preview OSM, deployment b1072e3](https://pasang-surut-gdbt5hhjl-dzakyahnafs-projects-100ecc4e.vercel.app/).
- [Alias branch OSM](https://pasang-surut-git-preview-p-a68888-dzakyahnafs-projects-100ecc4e.vercel.app/).
- [Draft PR #3](https://github.com/dzakyahnaf/pasang-surut/pull/3).

Kedua alamat preview Vercel terverifikasi menuju login Vercel. Login/izin
proyek mungkin diperlukan anggota tim; keberhasilan build tidak otomatis
berarti preview terbuka untuk publik. Pengaturan perlindungan tidak diubah.

Untuk review visual tanpa login Vercel, gunakan gambar berpasangan berikut:

| Main | OSM/CARTO |
|---|---|
| [Gambar main](bukti/review_peta_main_23.png) | [Gambar OSM](bukti/review_peta_osm_23.png) |

Keduanya dibuat dengan viewport 1440×1000, motor, Tawang–Terboyo,
**24 September 07.00 WIB**, versi data `715e64e7…`, versi graf `5ffae21c…`.
Sumber main adalah produksi, sumber OSM adalah build dev branch lokal
yang memproksi API produksi yang sama. Seluruh properti dua rute identik;
tidak ada galat JavaScript pada kedua pengambilan. Ini perbandingan visual,
bukan benchmark latensi Vercel versus localhost.
[Bukti](bukti/review_peta_23.json).

Pada laptop Dzaky, OSM juga aktif di `http://127.0.0.1:5175` selama server
pratinjau menyala. Alamat localhost ini tidak dapat dibuka dari laptop tim
lain sebagai layanan publik. Untuk menjalankannya sendiri, checkout branch
OSM di salinan terpisah lalu `npm ci` dan `npm run preview:osm` dari frontend.

## Perbedaan peta secara rinci

Keduanya memakai MapLibre GL JS 6.4.1. OSM menyediakan data geografi;
MapLibre menggambarnya. Versi main mengambil fitur terpilih dari ekstrak
OSM lokal. Versi preview menambahkan gaya dan vector tiles CARTO Voyager
berbasis OSM. Label tidak hilang karena OSM tidak punya nama tempat,
melainkan karena lapisan data/gaya yang sebelumnya digambar terbatas.

| Aspek | Main sekarang | Preview OSM/CARTO |
|---|---|---|
| Orientasi wilayah | Jaringan jalan, pantai dan label lokal dalam wilayah pilot | Daratan, laut, kawasan sekitar dan hierarki jalan lebih mudah dikenali secara visual |
| Nama jalan | Nama ruas dari ekstrak/graf tersimpan, dipilih menurut zoom | Label dari basemap; jalan yang tampil mengikuti gaya dan level zoom CARTO |
| Wilayah | Tujuh nama kecamatan dalam AOI, batas indikatif | Banyak nama kawasan/kelurahan; contoh Tanjungmas, Kaligawe, Terboyo Kulon/Wetan dan Tambakrejo |
| Tempat | Empat tujuan utama lokal | Empat tujuan lokal tetap ada, ditambah label tempat basemap pada zoom rinci seperti Polder Tawang, Taman Bubakan, Taman Garuda, Rumah Akar Kota Lama |
| Klik/pencarian tempat | Empat akses cepat dan pilih titik di peta | Fitur sama; label tambahan bukan otomatis fitur pencarian/geocoding atau verifikasi pintu masuk |
| Jalan tanpa genangan model | Seluruh garis graf tetap digambar sebagai konteks | Garis dasar graf disembunyikan; konteks jalan disediakan basemap agar tidak bertumpuk |
| Genangan dan rute | Overlay dari API PASANG SURUT | Overlay, kondisi, hasil rute dan versi data tetap sama; basemap tidak menambah cakupan analisis |
| Lapisan lokal | Label jalan/wilayah dan pantai lokal terlihat | Label jalan/wilayah/pantai lokal tertentu disembunyikan saat CARTO aktif; empat tujuan tetap digambar |
| Internet tambahan | Peta dasar tidak memanggil penyedia tile eksternal; produksi tetap butuh API | Browser memuat style/tiles CARTO selain API; bukan unduhan basemap oleh API VPS |
| Kegagalan awal basemap | Tidak ada ketergantungan tile luar | Bila pemuatan awal tidak selesai dalam 10 detik, tampilan lokal menjadi cadangan dengan status terlihat |
| Demo tanpa internet | Bisa dengan frontend dan API potret lokal yang sudah siap | Basemap eksternal perlu internet; fallback lokal tersedia. Service worker saja tidak menggantikan API |
| Pembaruan | Mengikuti ekstrak yang tersimpan pada aplikasi | Mengikuti data/gaya penyedia, tidak dijamin sinkron dengan versi graf analisis |
| Atribusi | OpenStreetMap | OpenStreetMap dan CARTO |
| Hosting frontend | Alamat Vercel, aplikasi dilayani VPS; root adalah landing | Preview dibangun sebagai frontend Vercel; root langsung membuka peta, API tetap ke VPS |
| Backend dan keamanan regresi | Rilis audit + koreksi panel | Backend, data, dependency MapLibre dan koreksi panel setara; perbedaan difokuskan pada basemap |

Hasil saat diperbesar dapat dilihat pada
[gambar detail OSM](https://github.com/dzakyahnaf/pasang-surut/blob/b1072e3/docs/final/bukti/osm_pratinjau_detail_final.png).
Tidak semua tempat OSM dijamin ditampilkan. Klaim performa kedua basemap
belum dibandingkan dalam benchmark yang setara; tambahan request/lapisan
berada di browser, sementara perutean API tetap sama.

Dokumentasi [CARTO](https://docs.carto.com/faqs/carto-basemaps) diperiksa ulang
23 September: vector belum terkena watermark raster; penyedia merekomendasikan
API key. Atribusi tetap wajib. Tidak dibuat akun, key, atau langganan baru.
Konsep data nama/fitur didukung oleh [dokumentasi OSM](https://wiki.openstreetmap.org/wiki/Map_features).

**Penilaian visual:** preview lebih mudah dikenali sebagai kota pesisir dan
memberi konteks kawasan lebih kaya. Main menonjolkan graf analisis, tetapi
garis rapat dapat membebani orientasi juri. Pada preview, perhatikan bahwa
jalan utama CARTO berwarna kuning, mendekati rute ambar; halo rute membantu,
tetapi keterbacaannya tetap perlu diuji pada proyektor. Warna laut adalah
latar basemap, bukan area genangan hasil model.

Usulan uji tim: tanpa narasi awal, minta setiap anggota menemukan Tawang,
Terboyo dan pantai dalam 10 detik; menunjuk rute sadar rob dan pembanding;
membedakan laut dengan ruas berwarna; membaca sumber/tanggal/peringatan;
lalu mengulangi di HP. Keputusan final basemap tetap belum diambil.

## Penilaian kritis PPT terhadap rulebook

Sumber: `Rulebook-dsdc-final.pdf` halaman 9–10. TM sudah mengonfirmasi durasi
tetap dan tim pertama. Ketentuan: persiapan 5 menit, presentasi maksimal 10 menit,
tanya jawab maksimal 15 menit. Pameran kunjungan juri maksimal 5 menit per tim.

| Kriteria final | Bobot | Cakupan deck saat ini | Penguatan yang disarankan |
|---|---:|---|---|
| Presentasi | 30% | Alur 8 slide koheren, target 9 menit, tiga pembicara | Latihan nyata; satu persoalan pengguna dan satu kesimpulan keputusan yang mudah diingat |
| Keberhasilan implementasi | 25% | Demo, screenshot cadangan, bukti tes | Tonjolkan fungsi yang dapat dicoba juri dan perilaku ketika data/jaringan bermasalah; jumlah unit test bukan ukuran keberhasilan penggunaan |
| Tanya jawab | 20% | Enam lampiran dan catatan batas model | Latih jawaban singkat 20–30 detik, lalu tunjukkan bukti bila diminta; jangan membacakan semua lampiran saat 10 menit utama |
| Pameran | 15% | QR dan aplikasi tersedia | Siapkan pitch 60 detik + hands-on juri; deck 9 menit bukan pengganti alur pameran 5 menit |
| Code project | 10% | Link repo, metode, tes/regresi terdokumentasi | Satu lampiran tambahan tentang pemisahan API/domain/data, validasi, CI, dan cara reproduksi; tidak perlu membuka seluruh source saat presentasi utama |

**Putusan:** urutan masalah → demo → metode → bukti/batasan → dampak →
pengembangan sudah tepat. Tidak perlu menambah jumlah slide utama. Namun,
deck saat ini lebih kuat sebagai penjelasan teknis yang jujur daripada
sebagai cerita manfaat pengguna yang tajam. PPT belum sama dengan seluruh
kesiapan final: hands-on, pameran dan kemampuan menjawab ikut dinilai.

### Prioritas revisi isi, dengan delapan slide tetap

1. **Slide 1–2: pertegas pengguna dan pembeda.** Pilih satu persona dan
   kebutuhan nyata: perjalanan/pengiriman di pesisir dengan pilihan jam.
   Jelaskan pembeda dalam satu kalimat: jam keberangkatan, kerentanan ruas,
   moda dan biaya memutar dibaca dalam satu alur. Hindari klaim bahwa semua
   aplikasi navigasi lain tidak memiliki informasi banjir.
2. **Slide 3: persingkat menjadi 2 menit 30 detik.** Dua jam, satu asal–tujuan,
   satu moda sudah cukup. Tampilkan pilihan, perubahan hasil, lalu keputusan
   yang mungkin dipertimbangkan pengguna. Uji semua fitur tidak perlu
   diulang di panggung. Simpan kasus galat untuk Q&A/pameran.
3. **Slide 5: naikkan nilai bukti fungsional.** Angka 95/26 tes diperkecil atau
   dipindahkan ke lampiran. Tampilkan contoh yang dimengerti juri: waktu
   tanpa data ditolak; pencarian dapat diulang; uji VPS tidak OOM pada beban
   dan durasi yang disebutkan. Sisakan satu pernyataan tegas bahwa evaluasi
   pasut tidak memvalidasi genangan jalan. Metrik pasut rinci ada di lampiran.
4. **Slide 6: perbaiki realisme skenario.** Menunggu 08.00→13.00 berarti lima
   jam. Itu lemah untuk komuter yang harus tiba pada jam tertentu. Gunakan
   persona berjadwal fleksibel, atau ganti skenario ke jam lebih dekat
   setelah hasilnya diverifikasi. Jangan menyebut perubahan itu hemat biaya
   total; biaya menunggu belum dihitung. Angka 13,9 menit juga waktu model,
   bukan ETA kemacetan langsung.
5. **Slide 6: kuatkan hubungan subtema dengan hati-hati.** Saat 08.00 memutar
   justru menambah BBM/CO₂. Manfaat yang sudah ditunjukkan adalah keterbukaan
   biaya adaptasi dan pilihan waktu, bukan penurunan emisi kota yang telah
   terbukti. Jelaskan peluang efisiensi bersyarat pada perjalanan fleksibel;
   jangan menghapus biaya detour yang positif atau menyebutnya penghematan.
6. **Slide 7: fokuskan roadmap.** Tiga prioritas cukup: uji pengguna,
   observasi genangan bertanggal pada data terpisah, serta pembaruan data
   dan pemantauan operasi. Jangan menambah daftar fitur ambisius sebelum
   bukti inti diperkuat. Tambahkan lampiran kualitas kode bila ada waktu.

Pembahasan Sentinel-1 yang ditolak, formula lengkap, rincian memori,
dan jumlah kasus uji tetap di lampiran. Batas model tetap terlihat; narasi
utama tidak perlu mengulang semua keterbatasan pada setiap slide. Bukti
pengguna nyata, walaupun kecil dan hasilnya campuran, lebih berguna daripada
menambah angka proyeksi tanpa validasi. Jangan mengisi hasil sebelum diuji.

### Usulan alokasi setelah revisi

| Slide | Durasi | Kumulatif | Pembicara usulan |
|---|---:|---|---|
| 1 Masalah | 0:45 | 0:00–0:45 | Dzaky |
| 2 Solusi/pembeda | 0:45 | 0:45–1:30 | Dzaky |
| 3 Demo | 2:30 | 1:30–4:00 | Daffa |
| 4 Metode | 1:00 | 4:00–5:00 | Dzaky |
| 5 Bukti dan batasan | 1:30 | 5:00–6:30 | Dzaky |
| 6 Dampak/biaya adaptasi | 1:15 | 6:30–7:45 | Naufal |
| 7 Pengembangan | 0:45 | 7:45–8:30 | Naufal |
| 8 Penutup | 0:30 | 8:30–9:00 | Naufal |

Total 9 menit termasuk perpindahan pembicara/tab; tersedia buffer 1 menit.
Ini usulan, belum pengukuran latihan atau perubahan pada notes PPT sekarang.
Lakukan minimal dua latihan dengan stopwatch dan satu perpindahan cadangan.
Untuk pameran: 60 detik masalah/produk, 2 menit juri mencoba, 1 menit membaca
hasil/batas, 1 menit dialog. Deadline PDF tetap perlu dikonfirmasi tim.
