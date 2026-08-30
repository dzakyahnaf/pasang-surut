# Progres

Satu entri per sesi kerja. Ditulis apa adanya, termasuk yang gagal.

Bagian **Papan Blokade** di bawah ini adalah ringkasan keadaan sekarang dan
diperbarui setiap sesi. Kalau hanya sempat membaca satu bagian dari berkas
ini, baca bagian itu.

---

## PAPAN BLOKADE — keadaan per 30 Agustus 2026, sore

> Bagian ini DIPERBARUI SETIAP SESI dan selalu menggambarkan keadaan
> sekarang, bukan riwayat. Riwayat ada di entri per milestone di bawahnya.
> Sisa waktu ke tenggat: **sekitar 36 jam** (31 Agustus 2026, 23.59 WIB).

### A. BLOKADE — menghentikan pekerjaan berikutnya

| # | Blokade | Menghambat | Siapa |
|---|---|---|---|
| ~~A1~~ | **SELESAI 29 Agustus.** Supabase hidup di `aws-0-ap-southeast-2.pooler.supabase.com:6543`, PostGIS 3.3 aktif, skema terpasang, dan terisi 19.394 ruas berfitur, 102.552 baris pemicu, 21.778 prediksi. | — | — |
| ~~A2~~ | **SELESAI 28 Agustus.** Acuan fase adalah WIB, dibuktikan dengan menyisir seluruh offset −12 sampai +12 jam terhadap data terukur stasiun IOC `sema`. UTC memberi korelasi NEGATIF di seluruh jendela uji, yang berarti pasang tertukar surut. | — | — |
| A3 | **SEBAGIAN SELESAI.** Proyek pertama `pasang-surut-anforcom` terverifikasi: terdaftar nonkomersial, Community tier, pemakaian 0,07 persen, uji 723 lolos, dan Python sudah tersambung. **Proyek Daffa dan Naufal masih belum ada** — kuota per proyek, jadi jatah tim baru sepertiga. | Kapasitas kuota untuk ekstraksi label M4 | Manual, dua orang |
| ~~A4~~ | **SELESAI 28 Agustus.** `data/raw/DEMNAS_1409-22_v1.0.tif`, 43 MB, terverifikasi menutupi seluruh AOI, 100 persen piksel valid, median elevasi 2,60 m. | — | — |
| ~~A5~~ | **SELESAI 29 Agustus.** github.com/dzakyahnaf/pasang-surut. Riwayat git diperiksa: `.env` tidak pernah masuk, dan tidak ada rahasia di seluruh riwayat. | — | — |

### B. PERLU PERHATIAN — tidak menghentikan, tetapi akan menggigit

| # | Hal | Kenapa penting |
|---|---|---|
| ~~B1~~ | **SELESAI 29 Agustus.** Dipindah ke `docs/identitas_tim.yaml`, `jumlah_citra_s1` diperbaiki menjadi 725, dan komentar ambang keputusan lama dibuang karena sudah tidak berlaku. | — |
| B2 | Tautan **riset WRI April 2026** di README masih `TODO(verifikasi tautan)`. | Tautan mati di gerbang juri lebih buruk daripada tidak ada tautan |
| B3 | Commit membawa trailer `Co-Authored-By: Claude Opus 5`. | Kalau rulebook DSDC mempersoalkan, putuskan sekarang selagi baru empat commit |
| ~~B4~~ | **SELESAI 29 Agustus.** Kolam koneksi `ThreadedConnectionPool` maksimum 5, ditambah cache kesehatan 5 detik sehingga `database_tersedia()` tidak lagi membuka koneksi sendiri. | — |
| B5 | `copy.id.json` ada di dua tempat, akar dan `frontend/src/`, tanpa apa pun yang menjaganya sinkron. | Begitu satu disunting, keduanya menyimpang diam-diam |
| ~~B6~~ | **SELESAI 29 Agustus.** `manifest.webmanifest`, service worker, dan tiga ikon. Service worker sengaja TIDAK luring penuh: `/api/` selalu menembus jaringan, karena prediksi basi lebih berbahaya daripada layar kosong. | — |
| B7 | Test menutupi `config.py`, `routing.py`, `genangan.py`, `kerentanan.py`, dan fungsi murni di skrip 06 dan 07 — 43 uji lolos. `db.py`, `main.py`, skrip 01 sampai 05 dan 08 sampai 11, dan `teks.js` masih tanpa test. | `t()` adalah mekanisme pengaman yang melempar galat, dan tidak ada test yang membuktikan ia melempar |
| B8 | Data contoh kedaluwarsa setelah 72 jam sejak dibuat. | Kalau Pita Pasut tampak kering seluruhnya, jalankan ulang `python -m scripts.03_isi_dummy` dari `backend/` |
| B9 | Ada PostgreSQL lain di mesin ini yang memakai port 5433, jadi kontainer pengembangan dipindah ke 55433. | Jangan bingung kalau `docker run` di 5433 gagal |
| B10 | Kontras kelas genangan paling dangkal `--air-1` terhadap latar dek hanya 1,39:1. | DESIGN.md Bagian 11 mensyaratkan terbaca di bawah matahari langsung dan saat dicetak hitam putih. Belum diuji di luar ruangan |
| B11 | Kecepatan ruas untuk jalan tanpa tag `maxspeed` berasal dari imputasi OSMnx. | Asumsi, bukan pengukuran. Sudah tercatat di `docs/batasan.md` bagian 2.4 |
| B12 | Penalti genangan (1,0 → 2,5 → 8,0) adalah angka rancangan, bukan hasil pengukuran lapangan. | Juri berhak menanyakan dasarnya. Sudah tercatat di `docs/batasan.md` |
| B13 | **`geemap` versi terbaru menuntut Python 3.12**, sementara proyek dikunci 3.11. PLAN.md bagian 4 menyebutnya sebagai bagian tech stack. | Rekomendasi: JANGAN pakai geemap. `earthengine-api` saja sudah cukup untuk pipeline yang mengekspor tabel, dan geemap 0.37.2 yang masih cocok menarik lebih dari 70 paket tambahan |
| B14 | **Berkas DEMNAS tidak membawa CRS.** `rasterio` melaporkan `CRS: None` walau koordinatnya jelas derajat WGS84. | **Sudah ditangani** di `scripts/05_isi_fitur_ruas.py`, yang menetapkan `EPSG:4326` eksplisit dan mencetak peringatan saat berkas dibuka. Berlaku untuk setiap kode baru yang membuka berkas itu |
| B16 | **Proposal tersisa 20 penanda `[[ISI]]` dari semula 58.** Seluruhnya tertahan pada tugas manual atau sumber yang belum ada: tautan deploy, repo, video, Figma; angka rantai dampak yang menunggu faktor emisi; dan dua sitasi tanpa sumber (leptospirosis dan WRI), turun dari tiga. | Rincian dan status per bagian ada di `docs/sisa_proposal.md` |
| B17 | **Tujuh kotak `[ ISI MANUAL ]` sudah dikeluarkan dari proposal** dan dipindah ke `docs/sisa_proposal.md`. Isinya tidak hilang. | Kotak itu instruksi untuk penulis, bukan isi proposal, dan berisiko ikut tercetak ke PDF yang dibaca juri |
| B34 | **Stasiun pasut IOC `sema` merekam kenaikan muka air relatif sekitar 9 cm per tahun** sepanjang 2015 sampai 2025, dari median +0,861 m menjadi +1,781 m. | Ini BUKAN kenaikan muka laut absolut — ia campuran kenaikan muka laut, penurunan tanah tempat alat berdiri, dan kemungkinan perubahan datum. Layak diperiksa lebih lanjut karena besarnya sepadan dengan laju subsidensi di literatur, tetapi jangan dikutip sebagai kenaikan muka laut |
| ~~B35~~ | **SELESAI 29 Agustus, diverifikasi dari luar.** https://pasang-surut.vercel.app dan https://pasang-surut-api.onrender.com hidup. `database: true`, 19.394 ruas, 21.778 prediksi, jendela 72 jam sampai 1 September. CORS meloloskan asal Vercel dan menolak asal asing. `/api/rute` mengembalikan `sumber_data` berupa LIST, jadi bug lencana benar-benar hilang di produksi. | — |
| ~~B43~~ | **SELESAI 30 Agustus.** `sw.js` di produksi kini `pasang-surut-v2` dan remote sejajar dengan lokal. | — |
| B50 | **`.docx` DAN PDF KINI DIBANGUN SKRIP, DAN JUMLAH HALAMANNYA TERUKUR.** `backend/scripts/22_bangun_docx.py` membangun ulang `.docx` dari Markdown. Dibuka dengan Microsoft Word lewat COM: **23 halaman** dari batas 30, A4 21×29,7 cm, margin 4-3-3-3, Times New Roman 12, spasi 1,5, delapan gambar tertanam. PDF diekspor dari Word yang sama. | **Perkiraan 156 kata/halaman ternyata jauh terlalu ketat** — ia menaksir 30 halaman padahal hasilnya 23. Sejumlah pemangkasan dikerjakan tanpa perlu, dan dua gambar yang sempat dibuang sudah dikembalikan. Sejak sekarang **jumlah halaman hanya dibaca dari Word**, tidak ditaksir. Ada sisa tujuh halaman |
| B51 | **Proposal diaudit ulang dengan asumsi juri HANYA membaca proposal.** Ditemukan 13 penanda `TODO` yang akan terbaca juri — termasuk tiga nama anggota tim tertulis `TODO — konfirmasi tim` di Lampiran C — Bagian 10 yang seluruhnya berupa instruksi kepada penulis, empat rujukan ke berkas repo, dan satu tabel tautan yang menduplikasi Lampiran A. | Semua sudah diperbaiki. Uji mandiri otomatis kini lulus delapan dari delapan. **Aturan barunya tertulis di proposal sendiri:** tidak ada `TODO`, tidak ada rujukan berkas repo sebagai tempat isi, tidak ada kode milestone internal |
| B52 | **Panduan produksi video terbit sebagai artifact.** https://claude.ai/code/artifact/40ee9168-8481-4c13-8c1f-ff305b15c875 | Video berbobot **10 persen** dan masih nol. Keputusan yang tercatat di sana: **bertiga, bukan sendirian** — rulebook 8.2.4 mewajibkan peserta tampil dari awal hingga akhir, dan bila dibaca sebagai "semua anggota", tim sendirian jatuh ke pasal gugur 5b |
| B46 | **BUG MUAT YANG MEMBUAT APLIKASI TAMPAK RUSAK — DIPERBAIKI 30 Agustus.** `App.jsx` menarik `/api/jam` dan `/api/ruas` bersama `Promise.all`. Yang kedua berukuran **6,6 MB**, sehingga Pita Pasut — elemen tanda tangan — menampilkan "belum dihitung" selama seluruh unduhan, padahal datanya tiba dalam sedetik. Lebih buruk, `ambilRuas()` tanpa argumen di sana SIA-SIA: efek `waktuAktif` langsung menariknya ulang. Muat pertama mengunduh **13,2 MB dan membuang separuhnya**. | Inilah yang membuat layar pertama tampak rusak, dan besar dugaan inilah yang memicu kesan "UI-nya jelek". Setelah dipisah, Pita Pasut tampil dalam ~2 detik dan peta menyusul. **Yang tersisa: 6,6 MB itu sendiri masih besar untuk ponsel kelas menengah di jaringan seluler.** Belum dioptimalkan; kandidat termurah adalah memangkas presisi koordinat GeoJSON |
| B47 | **UI DIUJI TERHADAP 61 ATURAN ANTI-POLA `impeccable`, HASILNYA NOL TEMUAN.** Satu-satunya temuan awal — `border-left: 3px solid var(--bahaya)` pada blok model ditolak di halaman validasi — sekaligus **melanggar DESIGN.md 3.6.1**, yang membatasi `--bahaya` hanya pada ruas tak bisa dilewati dan pita jam bahaya, "dilarang untuk dekorasi apa pun". Dihapus. | Detektor dan spesifikasi sepakat, jadi ini bukan soal selera. Kesimpulannya: antarmuka ini **bukan AI slop** — `DESIGN.md` menolak tampilan default AI secara eksplisit dan tertulis, hurufnya Barlow Semi Condensed dan IBM Plex Mono, tidak ada gradien selain Pita Pasut, dan kedalaman selalu disertai pola halftone |
| B48 | **PROPOSAL PERSIS DI BATAS: 29,99 halaman dari 30.** Sitasi yang ditambahkan 30 Agustus memakan seluruh margin yang tadinya sekitar satu halaman. | **Pemformatan Word hampir pasti mendorongnya lewat 30.** Pangkas lebih dulu, jangan tunggu. Urutan aman ada di bagian "Perkiraan halaman" proposal; yang paling murah adalah memindahkan catatan panjang di rujukan [2], [9], [10], [11] seluruhnya ke `docs/sumber_angka.md` |
| B49 | **Tiga dari empat TODO(sumber) wajib SELESAI.** WRI Rp848 miliar, faktor emisi, dan leptospirosis kini bersitasi. | Yang tersisa hanya **konsumsi BBM mobil 0,090 dan truk 0,250 L/km** — tidak ada rata-rata nasional resmi. Sudah ditulis sebagai asumsi rancangan, jangan diisi angka karangan. Provenans penuh di `docs/sumber_angka.md` |
| B44 | **Rancu musiman diuji, dan penolakan model Sentinel-1 kini berdiri di atas dasar yang jauh lebih kokoh.** Musim menjelaskan **38,6 persen ragam pasut** pada waktu akuisisi. Korelasi +0,362 di tingkat luas menyusut ke +0,230 di tingkat ruas, lalu ke **+0,107** setelah hari-dalam-tahun dikendalikan. Bukti bebas — tanggal kejadian rob — **berlawanan arah** (−0,77σ). | Dua keberatan terakhir yang menggantung sudah dijawab. Tidak ada lagi jalan penyelamatan yang tersisa untuk diuji, dan itu justru kabar baik: keputusan beralih ke indeks kerentanan kini terdokumentasi tuntas. Rinciannya di `docs/validasi.md` 6.5, skripnya `20_label_luas_ke_ruas.py` dan `21_uji_rancu_musiman.py` |
| B45 | **Perkiraan halaman proposal sempat salah hitung dan hampir memicu pemangkasan yang tidak perlu.** Kepadatan 156 kata/halaman diturunkan dari `.docx` yang SUDAH memuat enam gambar, lalu 1,5 halaman untuk enam tangkapan layar ditambahkan lagi di atasnya. | Gambar yang sama terhitung dua kali dan draft tampak 30,3 halaman padahal 29,0. Diperiksa dengan membuka `word/media/` di dalam `.docx`: enam PNG tertanam. **Jumlah halaman final tetap wajib diperiksa dengan Word, bukan dengan perkiraan ini** |
| B36 | **`data/processed/potret_demo.json` 7,8 MB WAJIB ikut di-commit.** Tanpa berkas itu, aplikasi yang di-deploy mati begitu Supabase tersendat. | Jalankan ulang `python -m scripts.18_seed_demo` sebelum demo — potret membawa tanggal kedaluwarsa dan ditolak API setelah lewat |
| B37 | **Uji dari HP di jaringan seluler belum dilakukan.** | Kriteria terima M6 menuntutnya. Perlu perangkat fisik |
| ~~B38~~ | **DIPUTUSKAN 29 Agustus:** Markdown jadi acuan, `.docx` dibangun ulang darinya di M8. Sebelumnya: **DUA SUMBER KEBENARAN untuk proposal.** `.docx` di akar (27 halaman, dirawat sejak sesi keempat) dan `docs/proposal_draft.md` (M7, 28,9 halaman perkiraan) kini memuat isi yang sama. | **Tetapkan satu sebagai acuan sebelum M8.** Saran: Markdown jadi acuan karena bisa di-diff di git, lalu `.docx` dibangun ulang darinya. Dibiarkan, keduanya akan menyimpang dalam satu sesi |
| B39 | **Empat TODO(sumber) WAJIB diisi**: tautan riset WRI, konsumsi bahan bakar per km, faktor emisi, dan data leptospirosis. | Keempatnya angka yang sudah tercetak di proposal, dan dua di antaranya tampil di antarmuka. Rincian di `docs/proposal_draft.md` bagian Ringkasan TODO |
| B40 | **Rantai dampak menghasilkan angka yang KECIL, dan itu dilaporkan apa adanya.** Median selisih rute 0,12 menit, median hemat menggeser jam 0,14 menit, p90 2,99 menit. | Bagian 11.5 menjelaskan mengapa nilai rupiah TIDAK dikalikan dari angka itu. Jangan tergoda mengubahnya menjadi angka besar sebelum ada data perjalanan per hari yang bersumber |
| ~~B41~~ | **SELESAI 29 Agustus, di-push tim.** Sebelumnya: **LIMA COMMIT BELUM DI-PUSH.** Remote publik di `1b7c475` (M4), lokal di `438e261` (M7). Diuji dengan clone dari nol: repo publik TIDAK memuat panel dampak, halaman validasi, artefak deploy, potret tahan banting, maupun draft proposal. | **Paling mendesak.** Satu perintah `git push origin main`. Juri menilai Code Project 10 persen dari repo itu |
| ~~B42~~ | **SELESAI 29 Agustus.** Sampul diperbaiki, dokumen kini memuat satu subjudul saja. Sebelumnya: **halaman sampul memakai subjudul lama** "Berbasis Kalibrasi Citra Radar Sentinel-1", sementara Bagian 1 dokumen yang sama sudah memakai rumusan baru. | Dokumen memuat DUA subjudul berbeda, dan yang lama justru di halaman pertama yang dilihat juri |
| ~~B43~~ | **SELESAI 29 Agustus, dihapus.** Sebelumnya: **`pratinjau_proposal.pdf` berasal dari 23 Agustus (M1)**, mendahului seluruh temuan M4 sampai M7. | Juri yang menelusuri repo bisa membukanya dan mengira itu proposalnya. Hapus atau ganti |
| B44 | **`deret_pasut()` di `domain/pasut.py` tidak pernah dipanggil.** | Diwajibkan `PLAN.md` 10.2 sebagai API modul. Pertahankan atau buang — keputusan tim, bukan keputusan teknis |
| ~~B45~~ | **SELESAI 29 Agustus, diisi tim.** Bundel produksi kini menunjuk ke Render. Sebelumnya: **`VITE_API_URL` belum diisi** Bundel yang di-deploy menunjuk ke `http://127.0.0.1:8000`, alamat cadangan localhost. Setiap panggilan API pergi ke laptop pengunjung sendiri. | **Aplikasi mati bagi siapa pun yang membukanya.** Vercel > Settings > Environment Variables > `VITE_API_URL` = `https://pasang-surut-api.onrender.com`, lalu Redeploy. API dan CORS-nya sendiri sudah benar |
| B46 | **Uji topeng air permanen SELESAI dan hasilnya tidak nol:** orbit 76 memberi korelasi +0,362 terhadap pasut, orbit 127 hanya +0,032. Tandanya positif, arah yang benar secara fisika. | Tetap TIDAK mencabut penolakan model: hanya satu dari dua orbit, rancu musiman belum disingkirkan (fase K1 dan P1 bergeser setahunan pada jam lintas tetap), besarnya sedang, dan yang diukur luas bukan ruas. Dicatat sebagai arah lanjutan di `docs/validasi.md` 6.5 |
| B47 | **SERVICE WORKER MENYAJIKAN CANGKANG BASI SELAMANYA.** Versi pertama melayani `/index.html` cache-first dengan nama cache tetap, sehingga pengunjung yang pernah membuka aplikasi sebelum perbaikan terus mendapat `index.html` lama yang menunjuk bundel lama yang menyimpan alamat API salah — tanpa satu pun galat yang terlihat. Terbukti di produksi: halaman memuat `index-B8OZuCn5.js` padahal server menyajikan `index-BYdTmoIX.js`. | **Diperbaiki:** cangkang kini jaringan-lebih-dulu, aset ber-hash tetap cache-lebih-dulu, dan `VERSI` dinaikkan ke v2 supaya cache lama dibuang. **WAJIB deploy ulang Vercel** agar sampai ke pengunjung |
| B30 | **Uji responsif 360px BELUM terverifikasi.** Jendela peramban diubah tetapi viewport tetap 1440, jadi hasilnya tidak sah. | Butuh perangkat sungguhan atau devtools. Lantai mutu DESIGN.md Bagian 11 butir pertama |
| B31 | **Uji baca di bawah matahari langsung dan uji cetak hitam putih BELUM dilakukan.** | Keduanya memerlukan orang, bukan kode. Pola halftone sudah dirancang untuk keduanya tetapi belum dibuktikan |
| B32 | **Proposal kini 27 halaman**, naik dari 26 setelah paragraf perbandingan Sentinel-1 versus rekonstruksi pasut ditambahkan. | Masih di bawah batas rulebook 30. Diukur dengan Word |
| B33 | **Konsumsi bahan bakar di `ambang_moda` masih asumsi tanpa sitasi**, dan kini angka itu tampil di antarmuka lewat panel dampak. | Sebelumnya hanya ada di database. Sekarang pengguna dan juri melihatnya, jadi sitasinya lebih mendesak daripada sebelumnya |
| B26 | **Region Supabase ap-southeast-2 (Sydney), bukan Singapura.** Tiap kueri memakan sekitar 370 ms bolak-balik. | Endpoint `/api/ruas` 2,0 detik dan `/api/rute` 1,3 detik. Masih terpakai, tetapi region ap-southeast-1 akan memangkasnya kira-kira separuh. Memindahkan region berarti membuat proyek Supabase baru |
| B27 | **Permintaan rute PERTAMA sempat 11,9 detik** karena graf 19.394 ruas dibangun saat permintaan datang. Sudah diperbaiki dengan pemanasan cache saat startup, kini 1,7 detik. | Kalau server di-deploy ke layanan yang tidur saat menganggur, cold start akan mengulang persoalan ini. Ping layanan sebelum juri memakainya |
| B28 | **`sampel_latih` 1,8 juta baris TIDAK dipindahkan ke Supabase.** Itu artefak pelatihan, tidak dibutuhkan saat runtime, dan akan memakan sebagian besar kuota 500 MB paket gratis. | Kalau dibutuhkan untuk audit juri, jalankan skrip 09 tanpa `--tanpa-database` sambil menunjuk ke database lokal |
| B29 | **Subjudul karya diubah** dari "Berbasis Kalibrasi Citra Radar Sentinel-1" menjadi "Berbasis Rekonstruksi Pasang Surut Terkalibrasi". | Subjudul lama mengklaim sistem dibangun di atas kalibrasi Sentinel-1, dan itu tidak lagi benar. **Perlu diselaraskan ke Figma, slide, dan judul video** |
| B18 | **Angka subsidensi "9–13 cm/tahun" tidak didukung sumber yang kita punya.** Rahmawati dkk (2020) memilih varian SBAS tanpa koreksi karena RMSE-nya terkecil (±1,3 cm/th); menurut varian itu nilai TERTINGGI seluruh Kota Semarang 9,4 cm/th, rata-rata Semarang Utara 4,6 cm/th. Angka belasan hanya muncul pada varian terkoreksi atmosfer yang justru TIDAK dipilih penulisnya. | PLAN.md bagian 6 dan abstrak proposal memakai 9–13. Proposal SUDAH saya turunkan ke 9,4 karena aturan repo nomor 1, tetapi **PLAN.md belum**. Sitasinya jurnal Geodesi Undip, dan PLAN.md sendiri memperingatkan juri Geodesi Undip akan membantah. Lihat C15 |
| B19 | **Rerata hujan tahunan ERA5 1.830 mm belum diadu dengan normal BMKG.** Reanalisis diketahui meratakan hujan konvektif setempat. | Angka ini belum layak dikutip di proposal. Sudah tercatat di `docs/batasan.md` bagian 1.9 dan `docs/validasi.md` bagian 5 |
| B20 | **Enam dari 16 kejadian rob terdokumentasi terjadi pada pasut yang TIDAK tinggi**, dan hujan 24 jamnya juga sedang saja (2,5 sampai 20,4 mm). | Dua pemicu yang kita punya belum menjelaskan seluruh kejadian. Ini memperkuat alasan memakai model, tetapi juga berarti fitur angin dan kondisi tanggul absen. Rincian di `docs/validasi.md` bagian 3.2 |
| B21 | **990 dari 19.394 ruas tanpa nilai subsidensi, 26 tanpa elevasi.** Yang pertama karena kecamatannya tidak dilaporkan sumber; yang kedua karena jatuh di tepi timur tile DEMNAS. | Keduanya `NULL`, bukan nol — gradient boosting menangani `NULL`, tetapi jangan sampai ada kode yang mengisinya dengan nol diam-diam |
| B22 | **MODEL GENANGAN SENTINEL-1 DITOLAK, DAN KLAIM PRODUK TURUN.** Model dilatih atas 725 citra dan 1,81 juta nilai backscatter, lalu ditolak sendiri karena label basahnya tidak berkorelasi dengan pasut (aturan "pasut saja" ROC-AUC 0,4935, dan pada tanggal kejadian rob tandanya terbalik). Sistem beralih ke indeks kerentanan sesuai PLAN.md 9.A. | **Ini perubahan terbesar sesi ini dan perlu keputusan tim.** Proposal sudah saya turunkan klaimnya dari "memprediksi genangan" menjadi "indeks kerentanan", dan Tabel 8 diisi angka model yang ditolak beserta alasannya. Rincian di `docs/validasi.md` bagian 6. Lihat C16 |
| B23 | **Antarmuka kini punya DUA tingkat lencana**, bukan satu. `dummy` memunculkan DATA CONTOH, `kerentanan_v1` memunculkan INDEKS KERENTANAN. Hanya `model_v1` yang membuat peta tampil tanpa lencana. | Tanpa tingkat kedua, indeks kerentanan akan tampil polos dan terbaca seolah prediksi model — overclaim yang dilarang aturan repo nomor 1 |
| B24 | **Tarikan mentah Sentinel-1 219 MB dan TIDAK di-commit.** Sudah masuk `.gitignore`. | Bisa dibangun ulang dengan `python -m scripts.08_ekstrak_s1`; daftar ruas dan benih acaknya terkunci di `data/processed/ruas_sampel_latih.json` sehingga hasilnya sama persis. Perlu kuota Earth Engine lagi, sekitar satu jam |
| B25 | **Prakiraan hujan cepat basi.** Tabel `pemicu` kini memuat prakiraan Open-Meteo sampai 12 September 2026, bertanda `sumber_hujan = 'open-meteo-prakiraan'`. | Sebelum demo atau rekaman video, jalankan ulang `python -m scripts.06_isi_pemicu --prakiraan` lalu `python -m scripts.11_indeks_kerentanan` |
| B15 | **Autentikasi Earth Engine memberi empat cakupan sekaligus**: earthengine, cloud-platform, drive, dan devstorage.full_control. | Itu bawaan alat resmi, bukan pilihan kita, tetapi cakupan Drive dan Cloud Storage luas. Token tersimpan di laptop yang menjalankan perintah |

### C. HANYA BISA DIKERJAKAN MANUAL — di luar jangkauan Claude Code

Saya tidak membuat akun, tidak memasukkan kata sandi, dan tidak menyetujui
syarat layanan atas nama tim. Ini batas aturan, bukan batas alat, dan tidak
berubah oleh tersedianya browser otomatis.

| # | Tugas | Rujukan |
|---|---|---|
| C1 | Daftar Google Earth Engine, **tiap anggota proyek sendiri** karena kuota per proyek. Pilih Community Tier, jangan Contributor karena menuntut akun billing | CHECKLIST nomor 1, panduan lengkap di `docs/panduan_akun_dan_data.md` |
| C2 | Daftar Copernicus Data Space sebagai cadangan bila kuota GEE habis | CHECKLIST nomor 2 |
| ~~C3~~ | ~~Daftar DEMNAS, unduh tile `1409-22`~~ — **SELESAI 28 Agustus** | — |
| C4 | Daftar AVISO — persetujuannya berhari-hari, daftar sekarang lalu lupakan | CHECKLIST nomor 4 |
| C5 | Buat proyek Supabase, lalu jalankan `db/schema.sql` di SQL Editor | CHECKLIST nomor 5 dan 9 |
| C6 | Buat akun Vercel dan Railway | CHECKLIST nomor 5 |
| C7 | Buat repo GitHub **PUBLIK** dan dorong seluruh commit ke sana | CHECKLIST nomor 5 |
| C8 | Daftar Figma dan buat prototype — rulebook poin 7.9 mewajibkan, dan tautannya masuk Lampiran proposal | CHECKLIST nomor 6 |
| C9 | Uji `pip install -r requirements.txt` dan `pytest -q` di laptop Daffa dan Naufal | Kriteria terima M1 |
| C10 | Minta rekap kejadian rob 2015 sampai 2019 ke BPBD Kota Semarang | Melengkapi `kejadian_rob_semarang.json` |
| C11 | Verifikasi tautan **riset WRI April 2026**. Tautan DEMNAS sudah dikoreksi ke `/portal-web/unduh/demnas` | B2 |
| C12 | Rekam video 3 sampai 7 menit, wajah peserta wajib tampil sepanjang video | Rulebook, bobot 10 persen |
| C14 | Konfirmasi pembagian peran di Lampiran C proposal. Saya isi mengikuti pembagian kerja PLAN.md, bukan berdasarkan kesepakatan tim | `docs/sisa_proposal.md` |
| C13 | Buka satu per satu 19 entri `perlu_verifikasi` di `kejadian_rob_semarang.json` dan salin angkanya dari isi artikel | Angka belum terverifikasi tidak boleh masuk proposal |
| C16 | **Setujui atau tolak penurunan klaim produk** dari "prediksi genangan" menjadi "indeks kerentanan". Saya sudah menurunkannya di proposal karena aturan repo nomor 1, tetapi ini keputusan strategis tim, bukan keputusan teknis. | B22, `docs/validasi.md` bagian 6 |
| C15 | **Putuskan angka subsidensi mana yang dipakai tim.** Kalau 9–13 cm/tahun hendak dipertahankan, sediakan sumber yang bisa dibuka dan dibaca sampai ke tabelnya. Kalau tidak, PLAN.md bagian 6 perlu diturunkan menyusul proposal. | B18 |

### D. SUDAH TERPECAHKAN — jangan dikerjakan lagi

| Hal | Terpecahkan di |
|---|---|
| Apakah `graph.graphml` perlu ikut di-commit untuk deploy | M3. Mesin routing membangun grafnya dari tabel `ruas_jalan`, jadi server yang di-deploy cukup membawa database. GraphML hanya dibutuhkan skrip 02, bukan runtime |
| Arah jalan satu arah salah pada 1.025 ruas | M3. Arah kini diperiksa ulang terhadap graf berarah asli, bukan diambil dari atribut hasil penggabungan |
| Kontras garis jalan 2,80:1 di bawah ambang grafis | M3. Diganti `--tinta-2`, kini 5,92:1 |
| `docs/batasan.md` kosong | Riset pendukung 24 Agustus. Kini 5 bagian, 17 batasan |
| Konstanta pasut seluruhnya `null` | Riset pendukung 24 Agustus. Terisi dari Rachman dkk 2015, dengan seluruh keterbatasannya tercatat |
| Tile DEMNAS mana yang dibutuhkan | 28 Agustus. `1409-22` saja, dikonfirmasi dua indeks independen dan dibuktikan dengan membuka berkasnya |
| Apakah akses Earth Engine benar-benar bekerja | 28 Agustus. 723 direproduksi dari Code Editor dan dari Python |
| Zona waktu acuan fase konstanta pasut | 28 Agustus. WIB, dibuktikan lewat penyisiran offset terhadap data terukur IOC `sema`. UTC memberi korelasi negatif. Sistem memakai +7,0 jam, bukan +7,9 hasil pencocokan terbaik |
| `laju_subsidensi.json` seluruhnya `null` | 28 Agustus. Terisi dari Rahmawati, Prasetyo & Sasmito (2020), PDF dibaca langsung sampai ke tabelnya. Angkanya lebih kecil daripada yang selama ini dipakai — lihat B18 |
| Curah hujan Open-Meteo belum diambil | 28 Agustus. 102.168 jam 2015–2026 masuk tabel `pemicu`, dengan cadangan mentahnya di `data/referensi/hujan_open_meteo.json` |
| Jarak pantai belum dihitung | 28 Agustus. Terisi untuk seluruh 19.394 ruas, dihitung di EPSG:32749 terhadap garis pantai OSM |
| Apakah label Sentinel-1 bisa dipakai melatih model genangan | 28 Agustus. TIDAK. Dibuktikan, bukan ditebak: korelasi anomali terhadap pasut +0,04 sampai +0,07, dan pada tanggal kejadian rob tandanya terbalik. Jangan ulangi percobaan yang sama dengan ambang berbeda — menyetel ambang tidak menciptakan isyarat yang tidak ada |
| Apakah memakai muka air TERUKUR menyelamatkan label Sentinel-1 | 29 Agustus. TIDAK. Angka mentahnya -0,29 dan tampak menjanjikan, tetapi seluruhnya semu: rekaman stasiun melayang naik 0,92 m dalam sepuluh tahun, dan arsip Sentinel-1 juga berubah lintas dekade. Setelah diluruskan per tahun tinggal +0,05. Keempat jalur penyelamatan kini tertutup |
| Apakah tombol tujuan cepat sebaiknya mengisi asal atau tujuan | 29 Agustus. Mengisi SLOT YANG KOSONG, asal lebih dulu. Ketahuan saat menjalankan skenario wajib: menekan satu tombol tidak menghasilkan apa-apa kalau selalu mengisi tujuan |
| Apakah cuplikan radius 100 m menyelamatkan model Sentinel-1 | 29 Agustus. TIDAK. ROC-AUC 0,5982 pada ambang setara, lebih buruk daripada cuplikan titik 0,6579. Arsip ditarik ulang penuh untuk mengujinya |
| Apakah genangan kota justru MENAIKKAN backscatter | 29 Agustus. Arahnya konsisten sesuai dugaan pantulan ganda, tetapi besarnya hanya 0,47 simpangan baku pada 12 citra. Tidak cukup untuk dijadikan label |
| Apakah jam lintasan tetap Sentinel-1 membuat pencuplikan pasut bias | 29 Agustus. Bias, tetapi ke arah yang MENGUNTUNGKAN. Persentil ke-95 pasut saat akuisisi +0,338 m berbanding +0,302 m pada seluruh jam. Yang tidak terwakili justru surut terdalam. Gambar buktinya di `docs/pasut_saat_akuisisi.png` |
| Bagaimana memakai DEMNAS tanpa melanggar aturan repo nomor 4 | 28 Agustus. Elevasi RELATIF terhadap tetangga radius 500 m. Galat DEM berkorelasi spasial sehingga sebagian besar saling meniadakan; simpangan baku turun dari 5,86 m ke 2,99 m |

---

## M1 — 23 Agustus 2026: fondasi repo

**Status: selesai.**

### Yang dibuat

- Struktur folder lengkap sesuai PLAN.md bagian 5
- `backend/requirements.txt` dengan 14 dependency berversi kunci, di-resolve
  dan diuji pasang nyata di Python 3.11.8
- `.env.example` berisi `DATABASE_URL`, dan `.gitignore` yang mengecualikan
  `.env`, `data/raw/`, `*.tif`, `*.osm.pbf`, `.venv/`
- `backend/app/config.py`: pemuatan AOI, konstanta CRS, zona waktu, path proyek
- `backend/tests/test_config.py` dan `pytest.ini`
- `README.md` sesuai kerangka PLAN.md bagian 11
- `docs/validasi.md` berisi hasil cek arsip Sentinel-1
- `docs/batasan.md`, `docs/arsitektur.md`, `docs/metodologi.md` — kerangka heading
- `data/referensi/` — tiga berkas JSON kerangka, seluruh nilai `null` menunggu sitasi
- Berkas pendamping dipindah ke tempatnya: AOI ke `data/aoi/`, `schema.sql`
  ke `db/`, `gee_cek_cakupan_s1.js` ke `gee/cek_cakupan_s1.js`

### Yang diverifikasi

- `pip install -r requirements.txt` berhasil di venv Python 3.11.8 bersih
- Keempat belas paket terimpor tanpa galat, termasuk rasterio dan geopandas
  yang paling rawan gagal di Windows
- Transformasi EPSG:4326 ke EPSG:32749 diuji pada titik Semarang, hasilnya
  masuk akal untuk UTM 49S
- `pytest -q` dari akar repo: 1 lolos

### Cek arsip Sentinel-1

723 citra di atas AOI. Ambang 150 dari PLAN.md bagian 3 terlampaui, jadi
rencana 9.A tidak dipakai dan model dibangun dengan set fitur penuh. Sebaran
per tahun dan catatan lubang arsip 2022 sampai 2024 ada di `validasi.md`.

### Keputusan yang diambil dalam sesi ini

- **Python dikunci 3.11.8**, bukan 3.13 yang jadi default di mesin. PLAN.md
  bagian 4 menetapkan 3.11. Ditulis ke `.python-version`.
- **`requirements.txt` di akar repo hanya meneruskan** ke
  `backend/requirements.txt`. Berkas aslinya tetap di `backend/` sesuai
  struktur PLAN.md bagian 5, sementara kriteria terima M1 menyebut
  `pip install -r requirements.txt` dari akar. Satu baris `-r` memenuhi
  keduanya tanpa menduplikasi daftar.
- **`pytest.ini` ditambahkan di akar repo.** Tidak ada di PLAN.md bagian 5,
  tetapi tanpa `pythonpath = backend` perintah `pytest -q` dari akar tidak
  bisa mengimpor paket `app`.
- **Berkas komponen frontend dan modul domain belum dibuat**, hanya foldernya.
  Keduanya milik milestone lain.

### Yang masih terbuka

- `BAGIAN_3_TERISI.yaml` masih menulis `jumlah_citra_s1: "BELUM ADA"`.
  Angka sebenarnya 723. Perlu diperbarui, juga blok `???` di PLAN.md bagian 3.
- Tautan DEMNAS dan riset WRI April 2026 di README masih `TODO(verifikasi
  tautan)`. Belum diverifikasi, jadi sengaja tidak ditulis.
- Tiga berkas di `data/referensi/` masih bernilai `null` seluruhnya.
- Repo belum dipublikasikan. M1 mensyaratkan repo publik.
- `schema.sql` belum dijalankan di Supabase.
- Environment belum diuji di laptop kedua dan ketiga.

---

## M2 — 24 Agustus 2026: graf jalan, database, dan peta

**Status: selesai.**

### Angka hasil

| | |
|---|---|
| Sisi berarah dari OSM | 36.724 |
| **Ruas fisik masuk `ruas_jalan`** | **19.394** |
| Panjang jaringan | 1.289,4 km |
| Ruas punya nama jalan | 12.876 |
| Ruas satu arah | 2.064 |
| Baris `prediksi_genangan` | 33.401 |
| Jam yang punya genangan | 33 dari 72 |
| Sumber data | `dummy` |

### Yang dibuat

- `backend/scripts/01_bangun_graf.py` — OSMnx mengunduh jaringan `drive` di
  dalam poligon AOI, disimpan ke `data/processed/graph.graphml` (18 MB,
  14.139 simpul). Unduhan memakan 13,5 detik. Setelah ini Overpass tidak
  pernah disentuh lagi.
- `backend/scripts/02_isi_ruas_jalan.py` — graf jadi baris tabel. Panjang
  dihitung di EPSG:32749, geometri disimpan EPSG:4326.
- `backend/scripts/03_isi_dummy.py` — data contoh 72 jam.
- `backend/app/db.py` — koneksi dan dua repository.
- `backend/app/main.py` — `GET /api/kesehatan` dan `GET /api/ruas`.
- `frontend/` — React, Vite, MapLibre. Token, huruf, peta penuh layar,
  tangga kedalaman, lencana DATA CONTOH, helper `t()`.

### Keputusan yang perlu diketahui tim

**Ruas dua arah disimpan SATU baris, bukan dua.** OSMnx mengembalikan graf
berarah, jadi jalan dua arah muncul dua kali. Kalau keduanya masuk tabel,
panjang jaringan terhitung dua kali lipat, peta menggambar dua garis
bertumpuk di atas aspal yang sama, dan `prediksi_genangan` ikut membengkak
dua kali. `to_undirected()` menggabungkannya. Arah disimpan di kolom
`satu_arah`. Angka 36.724 menjadi 19.394 karena ini, bukan karena ada data
yang hilang.

**Hanya ruas TERGENANG yang disimpan di `prediksi_genangan`.** Ruas kering
tidak menghasilkan baris sama sekali. Skema memang dirancang begitu:
`kedalaman_cm` bawaannya 0 dan `v_bobot_ruas` memakai LEFT JOIN dengan
COALESCE, sehingga ruas tanpa baris otomatis terbaca kering. Bedanya besar —
19.394 x 72 = 1.396.368 baris kalau semua disimpan, versus 33.401 yang
sebenarnya ditulis. Supabase paket gratis hanya 500 MB.
**Konsekuensi yang harus diingat:** tabel ini tidak bisa membedakan
"diprediksi kering" dari "tidak ada prediksi". Untuk data contoh itu tidak
masalah; saat model asli masuk, keputusan ini perlu ditinjau ulang.

**Pengganti elevasi pada data contoh.** DEMNAS di luar lingkup sesi ini,
jadi kerentanan ruas didekati lewat lintang — makin ke utara makin dekat
Laut Jawa. Sebaran kerentanan diukur lebih dulu dan ternyata condong ke
selatan (persentil ke-50 hanya 0,274), karena jalan permukiman jauh lebih
rapat di darat daripada di kawasan pelabuhan. Ambang dikalibrasi dari angka
terukur itu, bukan ditebak, supaya sekitar 12 persen ruas tergenang saat
pasut puncak dan keempat kelas tangga kedalaman muncul di peta.
**Ini pengganti sementara dan wajib dibuang di M4.**

**Peta tidak memakai penyedia ubin dari luar.** Latarnya satu warna dek dan
seluruh yang tergambar adalah data sendiri. Huruf dimuat dari paket
`@fontsource`, bukan Google Fonts. Keduanya demi aturan jalur demo offline.

**`data/processed/ruas_jalan.geojson` di-commit, `graph.graphml` tidak.**
GeoJSON 5,6 MB membuat peta tetap terbuka pada hasil `git clone` tanpa
database dan tanpa Overpass. GraphML 18 MB dibangun ulang skrip 01 dalam
belasan detik. **Terbuka untuk M6:** server yang di-deploy juga butuh
GraphML untuk routing — perlu diputuskan apakah dibangun saat deploy atau
ikut di-commit.

**Struktur folder.** Blok Perintah di `CLAUDE.md` sebelumnya menyebut
`api/main.py` dan `web/`, bertentangan dengan `PLAN.md` bagian 5 yang
memakai `backend/` dan `frontend/`. Tim memilih mempertahankan PLAN.md, dan
blok Perintah sudah dikoreksi.

**MapLibre dikunci 5.24.0, bukan 6.5.0.** Penurunan versi ini dilakukan atas
diagnosis yang KELIRU saat menelusuri peta kosong; MapLibre 6 kemungkinan
besar tidak bermasalah. Versi 5.24.0 tetap dipakai karena jalurnya lebih
matang menjelang tenggat. Perlu diketahui: MapLibre 6 tidak lagi punya
default export, jadi menaikkan versi berarti mengubah impor di `Peta.jsx`.

### Jebakan yang terpecahkan, catat supaya tidak terulang

- **Nama jalan sempat tersimpan sebagai teks `"nan"`.** Sebagian besar jalan
  kampung tidak punya tag `name` di OSM, dan pandas mewakilinya sebagai NaN.
  `str(NaN)` menghasilkan `"nan"`, yang akan terbaca juri sebagai nama jalan
  di peta. Sekarang dikembalikan `None`. 6.518 ruas memang tanpa nama.
- **Peta tampak kosong di tab yang dikendalikan otomasi.** Tab berstatus
  `hidden`, sehingga `requestAnimationFrame` tidak pernah menyala, dan
  MapLibre menunda pemuatan gaya ke frame berikutnya — selamanya, tanpa satu
  pun pesan galat. Ini BUKAN cacat aplikasi; pengguna dengan tab terlihat
  tidak terpengaruh. Kalau perlu diperiksa otomatis lagi, ganti `rAF` dengan
  `setTimeout` di halaman harness terpisah.
- **Data bisa tiba sebelum peta siap.** GeoJSON dari API sering datang lebih
  dulu daripada event `load` MapLibre. Tanpa penanda kesiapan, `setData`
  dilewati dan tidak pernah dicoba lagi. Sekarang kesiapan disimpan sebagai
  state React.

### Yang masih terbuka

- Database yang dipakai masih PostGIS lokal di Docker, bukan Supabase.
  `schema.sql` belum dijalankan di Supabase.
- Belum ada Pita Pasut, jadi belum ada cara memilih jam dari antarmuka.
  Peta selalu menampilkan jam berjalan. Pemilih tanggal biasa TIDAK boleh
  dipakai sebagai penggantinya — DESIGN.md Bagian 12 butir 10.
- Satu string baru ditambahkan ke `copy.id.json`:
  `sumberData.lencanaContohPanjang`, karena DESIGN.md Bagian 8 mewajibkan
  lencana berbunyi "DATA CONTOH — bukan prediksi" sementara berkas teks baru
  memuat "DATA CONTOH" saja.
- `kosong.tidakAdaGenanganIsi` berbunyi "Geser Pita Pasut untuk melihat jam
  lain", jadi belum dipakai — kalimatnya menunjuk kontrol yang belum ada.
- Kecepatan ruas berasal dari imputasi OSMnx untuk ruas tanpa tag `maxspeed`.
  Ini asumsi dan wajib ditulis di `docs/batasan.md`.
- Repo belum dipublikasikan.

---

## Riset pendukung — 24 Agustus 2026

Bukan milestone kode. Tiga butir CHECKLIST_MALAM_INI.md dikerjakan supaya
tidak jadi penghalang di M3 ke atas.

### Nomor 12 — konstanta harmonik pasut Semarang

`data/referensi/konstanta_pasut_semarang.json` **terisi**, sebelumnya seluruh
nilainya `null`.

Sumber: Rachman, Ismunarti, Handoyo, "Pengaruh Pasang Surut Terhadap Sebaran
Genangan Banjir Rob di Kecamatan Semarang Utara", Jurnal Oseanografi Undip
Vol 4 No 1, 2015. Tabelnya dibaca langsung dari PDF aslinya, bukan dari
ringkasan mesin pencari. Sepuluh komponen lengkap dengan amplitudo dan fase,
ditambah MSL, HHWL, LLWL, dan Formzahl.

Stasiunnya di 6°56'55,78" LS / 110°25'7,00" BT, yaitu **di dalam AOI**, dan
hanya berjarak sekitar 120 meter dari stasiun pasut IOC berkode `sema` yang
dikelola BIG. Untuk proyek ini keduanya boleh dianggap titik yang sama.

Tiga temuan yang mengubah cara angka ini harus dipakai:

1. **P1 dan K2 bukan hasil pengukuran.** Rekamannya hanya 15 hari, terlalu
   pendek untuk memisahkan komponen berfrekuensi dekat. Keduanya diturunkan
   dari K1 dan S2 memakai rasio tetap Admiralty. Buktinya aritmetis:
   P1/K1 = 0,3305 dan K2/S2 = 0,2697, keduanya persis rasio baku, dan
   fasenya disamakan dengan komponen induk. Dua dari tujuh komponen yang
   diminta PLAN.md 10.2 karena itu tidak berdiri sendiri.
2. **Zona waktu acuan fase tidak disebut sumber.** Disimpan sebagai `null`,
   bukan ditebak. Salah menebak menggeser kurva sampai 7 jam, dan untuk M2
   yang periodenya 12,4 jam itu bisa membalik pasang jadi surut. Cara
   menyelesaikannya ditulis di berkas: rekonstruksi dua kali, sekali dengan
   acuan UTC dan sekali WIB, lalu bandingkan dengan data terukur stasiun
   `sema`.
3. **Sumber lain tidak sepakat soal tipe pasut.** Az Zahro dkk (Prosiding SNF
   UNJ) memakai data Pushidrosal 29 piantan Januari–Februari 2018 dan
   memperoleh Formzahl 3,94, yaitu harian tunggal. Sumber kita memperoleh
   1,121, campuran condong ke harian ganda. Rekaman mereka lebih panjang.
   Tabel komponennya berupa gambar sehingga angkanya tidak bisa disalin.
   Perbedaan ini belum terselesaikan dan sudah masuk `batasan.md`.

Formzahl dihitung ulang dari angka yang tersimpan: 1,1235 versus 1,121 yang
ditulis makalah. Cocok dalam batas pembulatan, jadi transkripsinya benar.

**Jalan keluar yang direkomendasikan:** stasiun IOC `sema` punya empat sensor
aktif dan dikelola BIG bersama GFZ. Menghitung konstanta sendiri dari rekaman
satu tahun akan memisahkan P1 dari K1 dan K2 dari S2 dengan benar, sekaligus
menghapus keraguan zona waktu karena kita sendiri yang menetapkannya.

### Nomor 10 — tanggal kejadian rob

`data/referensi/kejadian_rob_semarang.json` **dibuat**, 21 entri.

Yang jujur harus disebut: **hanya 2 entri yang sudah dibaca sampai sumber
primernya**, sisanya masih berstatus `perlu_verifikasi` karena baru berasal
dari ringkasan mesin pencari. Tiga entri bahkan belum punya tautan. Periode
**2015, 2017, 2018, dan 2019 kosong sama sekali** — arsip berita daring dari
rentang itu tidak muncul di pencarian.

Jadi target 20 sampai 30 tanggal tercapai secara jumlah, TIDAK tercapai
secara mutu. Jangan masukkan angka berstatus `perlu_verifikasi` ke proposal
sebelum artikelnya dibuka.

Entri paling berguna, 23 Mei 2022, terverifikasi penuh dari CNN Indonesia
lengkap dengan tinggi muka air per jam: 155 cm pukul 11.00, puncak 210 cm
pukul 16.00, 190 cm pukul 19.45, 180 cm pukul 21.00. Deret ini bisa dipakai
menguji rekonstruksi pasut nanti.

Peringatan yang ditulis di berkas: **jangan pakai daftar ini untuk memilih
citra Sentinel-1.** PLAN.md bagian 8 menyebutnya sebagai insting yang salah.

Jalur tercepat melengkapi 2015–2019 adalah meminta rekap kejadian ke BPBD
Kota Semarang. Sumbernya resmi dan jauh lebih kuat daripada arsip berita.

### Nomor 8 — AOI dibekukan

`data/aoi/aoi_semarang_pilot.geojson`: `dibekukan_pada` diisi `2026-08-24`.
**Geometri tidak disentuh sama sekali** dan itu diverifikasi dengan
membandingkan geometri sebelum dan sesudah penyuntingan. Graf, tabel
ruas_jalan, dan prediksi tetap sah.

Batas administratif keenam kelurahan sasaran diambil dari OpenStreetMap lewat
Nominatim, lalu diuji satu per satu. Hasilnya: **keenamnya seluruhnya berada
di dalam AOI.** Margin AOI di luar gabungan kelurahan: barat 2,47 km, timur
3,24 km, utara 0,89 km, selatan 2,90 km.

Temuan yang perlu diketahui tim: **AOI sekitar 3,6 kali lebih luas daripada
gabungan enam kelurahan sasaran** — 98,4 km persegi berbanding 27,6 km
persegi. Rekomendasi saya **jangan dipangkas**: routing membutuhkan jaringan
jalan di luar wilayah tergenang untuk menghitung rute memutar, dan AOI yang
dipotong persis di batas kelurahan akan membuat rute alternatif terputus di
tepi peta. Tetapi konsekuensinya harus diingat — statistik apa pun yang
dihitung atas seluruh AOI akan terlihat jauh lebih optimistis daripada
kenyataan di enam kelurahan pesisir. Ini juga yang menjelaskan kenapa sebaran
kerentanan condong ke selatan saat mengkalibrasi data contoh.

### docs/batasan.md akhirnya terisi

Sebelumnya hanya heading kosong, padahal PLAN.md menandainya bahan bagian 5
proposal dan berlabel PENTING. Sekarang berisi 5 bagian dan 17 batasan yang
benar-benar diketahui, termasuk seluruh temuan riset di atas ditambah imputasi
kecepatan OSMnx dan konsekuensi penyimpanan hanya-ruas-tergenang.

### Yang tetap tidak bisa saya kerjakan

Seluruh BLOK 1 checklist — Earth Engine, Copernicus, DEMNAS, AVISO, Supabase,
Vercel, Railway, GitHub, Figma — dan nomor 9 menjalankan `schema.sql` di
Supabase. Semuanya menuntut pembuatan akun, pemasukan kata sandi, atau
persetujuan syarat layanan atas nama tim. Ini batas aturan, bukan batas alat,
dan tidak berubah oleh tersedianya browser otomatis.

---

## M3 — 25 Agustus 2026: perutean sadar genangan

**Status: selesai.** Kriteria terima terpenuhi — Pita Pasut digeser ke jam
pasut tinggi, rutenya berubah.

### Bukti kriteria terima

Asal `[110,49290, -6,96452]` menuju `[110,43853, -6,97545]`, moda motor.

| Jam WIB | Rute pembanding | Rute sadar rob | Putusan |
|---|---|---|---|
| Sel 25 · 16.00 (surut) | 10,3 mnt · 9,34 km · 0 ruas tergenang | sama persis | Tidak perlu memutar |
| Jum 28 · 06.00 (pasut puncak) | 10,3 mnt · 9,34 km · **35 ruas tergenang** | 13,3 mnt · 11,33 km · **1 ruas tergenang** | Memutar, +3,0 mnt +2,0 km |

Bayar tiga menit dan dua kilometer untuk menghindari 34 ruas tergenang.
Itulah seluruh argumen produk ini dalam satu baris.

### Yang dibuat

- `backend/app/domain/routing.py` — Dijkstra sadar waktu. Bobot ruas
  dihitung pada perkiraan waktu TIBA di ruas itu, bukan waktu berangkat.
- `backend/app/domain/pasut.py` — rumah baru untuk pasut. Isinya masih
  sinusoid contoh; M4 mengganti isinya tanpa mengubah pemanggilnya.
- `POST /api/rute`, `GET /api/genangan`, `GET /api/jam`.
- `frontend/src/components/PitaPasut.jsx` — elemen tanda tangan.
- `frontend/src/components/PanelRute.jsx` — rail kiri.
- `frontend/src/lib/waktu.js` — satu-satunya tempat UTC menjadi WIB.
- `backend/tests/test_routing.py` — 13 uji.

### Dua cacat data yang ditemukan dan diperbaiki

**1. Arah jalan satu arah salah pada 1.025 dari 2.059 ruas.**

Asumsi M2 bahwa `osm_u -> osm_v` adalah arah jalan ternyata SALAH.
`ox.convert.to_undirected()` tidak menjamin sisi hasil penggabungan
mempertahankan orientasi aslinya, jadi arahnya praktis seperti lemparan
koin — dan memang tepat separuh yang terbalik.

Akibatnya terukur: ketika mesin routing menghormati kolom `satu_arah` apa
adanya, hanya **13,6 persen** simpul terjangkau dari Pelabuhan Tanjung Emas.
Jalan satu arah yang arahnya terbalik bekerja seperti tembok.

Perbaikannya di sumber, bukan di routing: skrip 02 kini memeriksa ulang
setiap ruas terhadap graf BERARAH aslinya. Kalau hanya `(v, u)` yang ada,
pasangan simpul ditukar dan geometrinya dibalik, sehingga `osm_u -> osm_v`
selalu berarti arah yang boleh dilalui. Jangkauan naik ke **99,7 persen**.

Menambal ini di routing dengan mengabaikan arah akan menyuruh orang melawan
arus di jalan protokol. Itu sebabnya diperbaiki di data.

**2. Rute pembanding tidak terlihat di peta.**

`--rute-abai` dan `--tinta-3` adalah nilai heks yang SAMA PERSIS, `#7E97A3`.
Karena jalan digambar dengan `--tinta-3` sejak M2, rute pembanding yang
putus-putus lenyap di atas jalan — padahal selisih antara kedua rute justru
argumen produk ini.

Jalan diganti ke `--tinta-2`. Sekaligus menaikkan kontras jalan terhadap
latar dek dari 2,80:1 menjadi **5,92:1**, melewati ambang 3:1 untuk objek
grafis yang sebelumnya tercatat sebagai temuan audit.

### Keputusan yang perlu diketahui tim

**Graf routing dibangun dari tabel `ruas_jalan`, bukan dari GraphML.**
Jumlah simpul uniknya persis sama dengan graf OSMnx aslinya, 14.139, jadi
tidak ada konektivitas yang hilang. Keuntungannya dua: `edge_id` menempel
langsung pada sisi graf sehingga tidak ada kemungkinan salah pasang pada 87
ruas paralel, dan **server yang di-deploy cukup membawa database tanpa
berkas GraphML 18 MB**. Ini menutup pertanyaan terbuka M6.

**Bobot dihitung pada waktu TIBA, bukan waktu berangkat.** Ini bukan detail.
Ruas yang kering saat pengguna berangkat bisa sudah terendam ketika ia
benar-benar sampai di sana. Ada satu uji khusus yang mengunci perilaku ini
dan akan gagal kalau seseorang menyederhanakannya.

**Ambang moda dibaca dari tabel `ambang_moda`, tidak ditulis di kode.**
Angka di tabel itu masih berstatus asumsi menurut komentar `schema.sql`,
jadi tim harus bisa mengoreksinya tanpa menyentuh kode.

**Rute dihitung ulang otomatis saat Pita Pasut digeser.** Tidak perlu
menekan Cari rute lagi. Ini yang membuat menggeser pita benar-benar
mengubah rute, bukan sekadar mengubah warna genangan.

### Jebakan yang terpecahkan, catat supaya tidak terulang

- **Sepuluh kali Page Up hanya bergerak enam jam.** Handler papan ketik
  menghitung dari prop `indeks` yang masih basi ketika beberapa penekanan
  tiba dalam satu batch React. Diperbaiki dengan pembaruan fungsional.
- **Kaki Pita Pasut terpotong keluar layar.** `flex: 1 1 auto` memakai
  tinggi SVG sebagai dasar perhitungan, sehingga total isi melebihi tinggi
  pita. Diperbaiki dengan `flex: 1 1 0` dan `min-height: 0`.
- **SVG Pita Pasut tetap berukuran 720x120 di dalam wadah 1408x64.**
  `useLayoutEffect` dengan senarai kosong berjalan saat data jam belum
  datang, sehingga elemennya belum ada, dan tidak pernah dijalankan lagi.
  Diperbaiki dengan menjadikan `n` sebagai kebergantungan.
- **Atribusi OpenStreetMap sempat tertimpa petunjuk ketuk.** Atribusi ODbL
  adalah kewajiban lisensi, bukan hiasan. Kini keduanya berdampingan.
- **Klik sintetis tidak sampai ke MapLibre di tab tersembunyi.** Keluarga
  masalah yang sama dengan `requestAnimationFrame`. Verifikasi otomatis
  memakai `peta.fire('click', ...)` yang tetap melewati jalur kode
  aplikasi yang sebenarnya.

### Alat verifikasi yang kini disimpan di repo

`frontend/uji-render.html` — halaman harness yang mengganti
`requestAnimationFrame` dengan `setTimeout`. Tanpa ini, peta selalu tampak
kosong pada tab yang dikendalikan otomasi, dan pernah memakan satu sesi
penuh untuk ditelusuri. Tidak ikut ke hasil build.

`window.__peta` diekspos di `Peta.jsx`, hanya saat `import.meta.env.DEV`,
supaya verifikasi otomatis bisa memproyeksikan bujur-lintang ke piksel layar.

### Yang TIDAK dikerjakan, sesuai batas sesi

Model asli, panel dampak empat angka, halaman validasi, dan tombol tujuan
cepat. Selisih waktu dan jarak antara kedua rute sudah dikembalikan API di
field `selisih` sebagai bahan mentah panel dampak M5.

---

## Persiapan M4 — 28 Agustus 2026: pasut terbukti, fitur terisi, pemicu terkumpul

**Status: selesai.** Ini pekerjaan penyiapan sebelum M4, bukan M4 itu
sendiri. Model genangan belum dilatih dan tidak ada satu pun metrik model di
sesi ini.

### A2 tuntas — acuan waktu fase konstanta pasut adalah WIB

Ini blokade tertua di papan. Rachman dkk (2015) tidak menyebutkan zona waktu
acuan fase konstantanya, dan selisih tujuh jam setara 203 derajat pada M2 —
lebih dari setengah siklus. Salah menebak berarti pasang tertukar surut pada
fitur terpenting model.

Rencana semula menguji dua tebakan. Yang dikerjakan lebih baik daripada itu:
seluruh offset −12 sampai +12 jam disisir dengan langkah 0,25 jam terhadap
data terukur stasiun IOC `sema`. Menyisir lebih baik karena hasilnya
menunjukkan sendiri apakah ada puncak kecocokan yang tegas; kalau tidak ada,
itu pertanda konstantanya yang bermasalah, bukan offsetnya.

Lebih dulu dibuktikan bahwa waktu pada layanan IOC memang UTC, secara
empiris: rekaman terbaru hanya berselang menit dari waktu UTC berjalan.
Kalau dibaca sebagai waktu lokal ia akan tertinggal tujuh jam padahal
stasiunnya melapor hampir seketika.

| Jendela | Offset terbaik | Fase = UTC | Fase = WIB |
|---|---:|---:|---:|
| 2 hari | +7,50 j | −0,289 | +0,907 |
| 4 hari | +7,75 j | −0,362 | +0,909 |
| 7 hari | +8,25 j | −0,427 | +0,858 |
| 10 hari | +8,00 j | −0,465 | +0,782 |

**Memakai UTC bukan sekadar kurang tepat, melainkan berkebalikan.** Sistem
memakai +7,0 jam, bukan +7,9 hasil pencocokan terbaik, karena +7,0 berdasar
sedangkan +7,9 hasil pencocokan terhadap sepuluh hari data. Sisa ~0,9 jam
diduga koreksi nodal 18,6 tahun yang belum diterapkan.

Sinusoid data contoh di `domain/pasut.py` dihapus. Rekonstruksi harmonik kini
satu-satunya jalur.

### Uji silang kedua: apakah tanggal rob memang berpasut tinggi

Kalibrasi di atas memakai sepuluh hari data terukur. Uji ini memakai bukti
yang sama sekali terpisah — 21 entri kejadian rob dari pemberitaan dan
dokumen resmi — dan bertanya apakah hari kejadian jatuh pada pasut tinggi.

| Ukuran | Median persentil | ≥ p75 | ≥ p90 |
|---|---:|---:|---:|
| Per hari (37 hari) | 71,5 | 16 (43%) | 7 (19%) |
| Per kejadian (16 kejadian) | 80,2 | 9 (56%) | 5 (31%) |

Bila tanggal kejadian tidak berhubungan dengan pasut, medianya mendekati 50.
**Putusan yang dicatat "sedang", diambil dari ukuran per hari yang angkanya
lebih rendah** — ukuran per kejadian diperkenalkan setelah ukuran per hari
dihitung, jadi memakainya sebagai dasar putusan akan terlihat seperti memilih
ukuran yang hasilnya paling enak.

Temuan yang lebih berguna daripada putusannya: **enam dari 16 kejadian justru
terjadi pada pasut yang tidak tinggi**, dan hujan 24 jamnya juga sedang saja.
Salah satunya, `2026-05-18`, berstatus verifikasi `primer` — sumber terkuat
yang kita punya — dengan persentil pasut hanya 29,2. Pasut saja tidak
menjelaskan rob, dan dua pemicu yang kita punya pun belum menjelaskan
seluruhnya. Itu argumen untuk model, bukan ambang.

### Fitur ruas terisi

`scripts/05_isi_fitur_ruas.py`, atas 19.394 ruas:

| Fitur | Terisi | Minimum | Median | Maksimum |
|---|---:|---:|---:|---:|
| Elevasi DEMNAS | 19.368 | −0,13 m | 4,07 m | 57,31 m |
| Jarak ke garis pantai | 19.394 | 7 m | 3.565 m | 7.909 m |
| Laju subsidensi | 18.404 | 2,1 cm/th | — | 5,8 cm/th |

Garis pantai (21 garis, `natural=coastline`) dan batas delapan kecamatan
diunduh sekali dari OSM lalu disimpan ke `data/processed/`. Poligon kecamatan
diperiksa tidak saling tumpang tindih. Jarak dihitung di EPSG:32749, bukan di
derajat.

### Variabel pemicu terkumpul

`scripts/06_isi_pemicu.py` mengisi tabel `pemicu` dengan **102.168 baris jam**
dari 2015-01-01 sampai 2026-08-27, mencakup seluruh periode latih dan uji.
Hujan dari Open-Meteo Archive (reanalisis ERA5), diakumulasi 24 dan 72 jam;
pasut dari rekonstruksi harmonik. Cadangan mentahnya disimpan ke
`data/referensi/hujan_open_meteo.json` supaya tabel bisa dibangun ulang tanpa
internet — aturan repo nomor 6 melarang panggilan API saat runtime, dan hujan
adalah godaan terbesar untuk melanggarnya.

Rerata tahunan yang dihasilkan 1.830 mm. **Belum diadu dengan normal BMKG**,
dan reanalisis diketahui meratakan hujan konvektif setempat, jadi angka itu
belum layak dikutip. Dicatat sebagai B19.

### Laju subsidensi: sumbernya ketemu, angkanya lebih kecil

`laju_subsidensi.json` terisi dari Rahmawati, Prasetyo & Sasmito (2020),
*Jurnal Geodesi Undip* 9(1):29–36 — SBAS atas 13 citra Sentinel-1A 2015–2018.
PDF-nya dibaca langsung sampai ke tabelnya, bukan dikutip dari ringkasan
pencarian, mengikuti disiplin yang dipakai sejak ringkasan pencarian pernah
mengacaukan amplitudo pasut.

Makalah menguji enam varian; **penulisnya memilih varian tanpa koreksi karena
RMSE-nya terkecil**, ±1,3 cm/tahun. Berkas ini memakai varian yang dipilih
penulisnya sendiri, bukan varian yang angkanya paling mengesankan.

| Kecamatan | Minimum | Maksimum | Rata-rata |
|---|---:|---:|---:|
| Genuk | 2,3 | 9,4 | 5,8 |
| Semarang Utara | 0,8 | 7,4 | 4,6 |
| Semarang Timur | 0,1 | 7,4 | 4,5 |
| Gayamsari | 0,1 | 8,1 | 3,6 |

**Konsekuensinya tidak nyaman: "9–13 cm/tahun" di PLAN.md bagian 6 dan di
abstrak proposal tidak didukung sumber ini.** Angka belasan memang muncul di
makalah yang sama, tetapi hanya pada varian terkoreksi atmosfer yang RMSE-nya
dua sampai lima kali lebih besar dan justru tidak dipilih penulisnya. Proposal
sudah diturunkan ke 9,4 mengikuti aturan repo nomor 1; **PLAN.md belum, dan
itu keputusan tim.** Lihat B18 dan C15.

### Proposal

26 halaman sebelum dan sesudah, diukur dengan Word, bukan diperkirakan.
3.823 → 3.954 kata.

- Abstrak dan bagian 3.1: 9–13 → 9,4 cm/tahun, dengan sitasinya
- Tabel 6: sumber subsidensi dan hujan disebut spesifik
- Tabel 7: baris pasut Belum → Selesai; ditambah baris "Fitur ruas dan
  variabel pemicu" (19.394 ruas, 102.168 jam)
- Bagian 9.2: satu paragraf baru yang menyatakan terus terang metrik model
  belum ada, sekaligus melaporkan apa yang sudah tervalidasi. Tabel 8 tetap
  "Belum tersedia" seluruhnya
- Daftar Pustaka: satu `[[ISI]]` terisi. Sisa 20, turun dari 21

### Yang dibuat

- `backend/scripts/05_isi_fitur_ruas.py`, `06_isi_pemicu.py`,
  `07_uji_silang_rob.py`
- `db.RepositoriRuas.perbarui_fitur()` dan `ringkasan_fitur()`
- `db.RepositoriPemicu` — repositori ketiga
- `backend/tests/test_pemicu.py`, 10 uji. Total suite 24 uji, seluruhnya lolos
- `data/referensi/laju_subsidensi.json`, `uji_silang_rob.json`,
  `hujan_open_meteo.json`
- `data/processed/garis_pantai.geojson`, `kecamatan.geojson`

### Yang TIDAK dikerjakan, sesuai batas sesi

Ekstraksi label Sentinel-1 dan pelatihan model — itu M4 sebenarnya. Tidak ada
satu pun metrik model di sesi ini, dan Tabel 8 di proposal tetap kosong.

---

## M4 — 28 Agustus 2026: model dilatih, model ditolak, sistem beralih

**Status: selesai, dengan hasil negatif sebagai temuan utamanya.**

Model genangan berbasis Sentinel-1 dibangun sampai tuntas, diuji, lalu
**ditolak oleh tim sendiri**. Sistem beralih ke indeks kerentanan sesuai
`PLAN.md` bagian 9.A. Ini bukan pekerjaan yang gagal diselesaikan; ini
pekerjaan yang selesai dan jawabannya tidak enak.

### Yang dikerjakan pada jalur utama

Seluruh arsip ditarik, bukan sebagian: **725 citra**, 2.502 ruas berstrata,
**1.813.950 nilai backscatter VV**, skala 30 m dengan median fokal 30 m.
Ditarik lewat `toBands()` per tahun sehingga satu permintaan mengembalikan
seluruh deret setahun untuk lima ratus ruas sekaligus — 72 permintaan, sekitar
satu jam, jauh di bawah kuota bulanan.

Keputusan rancangan yang menyelamatkan banyak waktu: **Earth Engine hanya
menarik nilai mentah, seluruh klasifikasi basah/kering dilakukan di laptop.**
Kalau ambang diputuskan di dalam GEE, tiap percobaan berarti menarik ulang
seluruh arsip dan kuota bulanan habis untuk eksperimen. Karena mentahnya
tersimpan, seluruh diagnosis di bawah ini gratis dan tanpa internet.

Terlihat juga lubang arsip yang diperingatkan PLAN.md: 2019 punya 92 citra,
2022 hanya 33.

### Kenapa modelnya ditolak

Pemeriksaan kewarasan dipasang **sebelum** pelatihan, bukan setelahnya, dan
pemeriksaan itulah yang menyalakan lampu merah:

| Pemeriksaan | Hasil |
|---|---:|
| Pasut rata-rata saat label basah | +0,092 m |
| Pasut rata-rata saat label kering | +0,095 m |
| Selisih | **−0,003 m** |

Diagnosis dilanjutkan pada agregat per citra, yang meratakan speckle atas
2.502 titik sekaligus. Korelasi anomali terhadap pasut: **+0,040** seluruh
sampel, +0,054 untuk ruas di bawah 1.000 m dari pantai, +0,072 di bawah 500 m.
Tidak ada isyarat.

Uji terakhir, terhadap 12 citra yang jatuh pada atau berdekatan tanggal
kejadian rob: anomali **+0,148 dB lebih TINGGI** saat kejadian. **Tandanya
terbalik** — genangan seharusnya menurunkan backscatter — dan besarnya hanya
0,34 sampai 0,46 simpangan baku, jadi tidak signifikan ke arah mana pun.

Modelnya sendiri mencapai ROC-AUC 0,6579 pada uji 2024–2026 dan mengalahkan
ketiga pembanding naif. Tetapi kepentingan permutasi membongkar dari mana
angka itu berasal:

| Fitur | Penurunan ROC-AUC |
|---|---:|
| Jarak ke pantai | +0,1417 ± 0,0039 |
| Elevasi DEMNAS | +0,0619 ± 0,0016 |
| Laju subsidensi | +0,0342 ± 0,0014 |
| Tinggi pasut | +0,0010 ± 0,0014 |
| Hujan 24 jam | +0,0004 ± 0,0010 |
| Hujan 72 jam | −0,0026 ± 0,0011 |

Ketiga fitur waktu nol dalam batas ketidakpastiannya. **Model ini mempelajari
ruas mana yang sering beranomali, bukan kapan ruas tergenang.** Untuk sistem
perutean yang seluruh gunanya ada pada kata "kapan", itu tidak berguna.

Godaan yang ditolak: menurunkan ambang dari −3 dB ke −2 dB akan menaikkan
jumlah label empat kali lipat dan mungkin menaikkan AUC. Itu tidak akan
menciptakan isyarat yang tidak ada, hanya menyembunyikan ketiadaannya.

### Jalur cadangan yang dipakai

`app/domain/kerentanan.py` — indeks kerentanan berbasis aturan, tiga komponen
berbobot **sama rata**:

- Elevasi **relatif** terhadap tetangga radius 500 m
- Jarak ke garis pantai
- Laju penurunan muka tanah

**Elevasi relatif, bukan mutlak, adalah temuan metodologis sesi ini.** Aturan
repo nomor 4 melarang ambang elevasi absolut karena RMSE DEMNAS 2,79 m jauh
lebih besar daripada rob 10–50 cm. Tetapi galat DEM sebagian besar
**berkorelasi spasial**: bila satu petak terangkat, tetangganya ikut terangkat
kira-kira sama. Mengurangkan nilai tengah tetangga meniadakan sebagian besar
galat itu. Terukur: simpangan baku turun dari **5,86 m menjadi 2,99 m**.

Bobot sama rata adalah keputusan sadar. Tidak ada data untuk menyetelnya, dan
menyetel tanpa data uji hanya menyembunyikan tebakan di balik desimal.

Pemeriksaan kewarasan terhadap jalan yang dilaporkan tergenang: Bandarharjo
persentil 97,7, Kaligawe 90,5, Genuk 86,0, Terboyo 68,7, terhadap dasar 50.
**Ini tidak dilaporkan sebagai akurasi** — kawasan itu pesisir dan jarak
pantai adalah komponen indeks, jadi pemeriksaannya melingkar. Ia menunjukkan
kodenya tidak keliru, bukan indeksnya benar.

### Dari indeks menjadi genangan per jam

Kesalahan yang sempat masuk database dan langsung diperbaiki: ambang indeks
**tetap** menandai 44,7 persen jaringan tergenang pada SETIAP jam, termasuk
saat surut terdalam. Itu jelas salah.

Gantinya, proporsi ruas terdampak **mengikuti pasut** — nol saat pasut di atau
di bawah nilai tengahnya, naik sampai puncaknya saat pasut menyentuh persentil
ke-99,9. Skala puncaknya 10 persen jaringan, diikat ke perkiraan WRI Indonesia
yang sudah menjadi jangkar proposal. Yang menentukan ruas MANA adalah indeks;
yang menentukan BERAPA BANYAK adalah pasut.

Hasil 72 jam sejak 28 Agustus: **33 dari 72 jam tanpa genangan sama sekali**,
puncak 1.028 ruas (5,3 persen), 21.778 baris. Baris `dummy` dihapus.

### Antarmuka: dua tingkat lencana, bukan satu

`LencanaContoh.jsx` semula hanya mengenal `dummy`. Dengan sumber baru
`kerentanan_v1`, lencana akan hilang dan indeks kerentanan tampil polos
seolah prediksi model — persis overclaim yang dilarang aturan repo nomor 1.

Kini ada dua tingkat: `dummy` memunculkan **DATA CONTOH**, `kerentanan_v1`
memunculkan **INDEKS KERENTANAN — bukan prediksi genangan**. Hanya `model_v1`
yang membuat peta tampil tanpa lencana, dan itu baru sah bila
`docs/validasi.md` bagian 6 memuat angka yang benar-benar lolos.

### Yang dibuat

- `backend/scripts/08_ekstrak_s1.py`, `09_latih_model.py`, `10_prediksi.py`,
  `11_indeks_kerentanan.py`
- `backend/app/domain/genangan.py` — konversi ke kedalaman, 10–50 cm
- `backend/app/domain/kerentanan.py` — indeks kerentanan
- `db.RepositoriSampelLatih` — repositori keempat
- `backend/tests/test_genangan.py` (9 uji), `test_kerentanan.py` (10 uji).
  Total suite **43 uji**, seluruhnya lolos
- `docs/kepentingan_fitur.svg` — ditulis langsung sebagai SVG. matplotlib
  sengaja tidak ditambahkan: komentar di `requirements.txt` justru menyebut
  penghindaran matplotlib sebagai alasan menolak `geemap`, jadi menariknya
  masuk lewat pintu belakang tidak pantas
- Mode `--prakiraan` pada skrip 06, karena tabel `pemicu` berhenti di 27
  Agustus sementara prediksi butuh 72 jam ke depan
- `data/referensi/metrik_model.json`, `data/processed/indeks_kerentanan.json`,
  `ruas_sampel_latih.json`, `s1_daftar_citra.json`,
  `model_genangan_v1.joblib`

### Diperiksa ujung ke ujung

`/api/kesehatan` melaporkan `sumber_data: ["kerentanan_v1"]` dan 21.778
prediksi. Permintaan rute mobil Tanjungmas ke Genuk pada jam pasut tinggi
mengembalikan dua rute yang berbeda 1,0 menit dan 0,44 km.

### Yang TIDAK dikerjakan, sesuai batas sesi

Panel dampak empat angka dan halaman validasi di antarmuka — itu M5.
Faktor emisi masih `null` sehingga rantai dampak tetap tidak bisa dihitung.

---

## M4 lanjutan — 29 Agustus 2026: tiga upaya penyelamatan, Supabase hidup

**Status: selesai.** Model Sentinel-1 diberi tiga kesempatan lagi dan gagal
ketiganya. Klaim produk diperbaiki, bukan diturunkan. Database pindah ke
Supabase dan aplikasi berjalan di atasnya.

### Tiga upaya penyelamatan model

| Upaya | Hasil | Putusan |
|---|---|---|
| Cuplik radius 100 m, bukan piksel titik tengah | ROC-AUC 0,5982 pada ambang setara, turun dari 0,6579 | gagal |
| Kriteria dua arah, dugaan pantulan ganda | arah benar tetapi hanya 0,47 simpangan baku pada 12 citra | gagal |
| Luas air kawasan terbuka | korelasi terhadap pasut NEGATIF, −0,10 sampai −0,27 | gagal |

Yang penting dari upaya pertama: perbandingannya dibuat ADIL. Perataan radius
menekan ragam sampai label basah nyaris lenyap — pada ambang −3 dB yang sama
hanya tersisa 838 label dari 1,8 juta. Ambang diturunkan ke −1,4 dB supaya
laju labelnya setara, dan barulah dibandingkan. Tanpa penyesuaian itu
kesimpulannya akan benar karena alasan yang salah.

Yang penting dari upaya ketiga: korelasi negatifnya bukan kejanggalan. Luas
gelap di AOI didominasi tambak dan muara, dan air dangkal yang tenang saat
surut justru lebih halus, lebih gelap, dan lebih luas terlihat daripada air
dalam yang beriak saat pasang.

Rinciannya di `docs/validasi.md` bagian 6.5.

### Temuan yang justru menguntungkan: jam lintasan Sentinel-1

Keberatan yang hampir pasti muncul di sesi tanya jawab: Sentinel-1 sinkron
matahari, selalu melintas pada jam lokal yang sama, jadi arsipnya tidak akan
memuat pasang tinggi.

Diukur, dan **keberatan itu terbalik**:

| | Saat akuisisi | Seluruh jam |
|---|---:|---:|
| Median | **+0,097 m** | +0,014 m |
| Persentil ke-95 | **+0,338 m** | +0,302 m |
| Persentil ke-99 | **+0,396 m** | +0,370 m |
| Minimum | −0,249 m | −0,575 m |

Komponen S2 berperiode tepat 12,000 jam sehingga fasenya TERKUNCI pada waktu
matahari, dan kedua jam lintasan (05.16 dan 17.58 WIB) kebetulan jatuh dekat
fase tingginya. Arsip karena itu memuat LEBIH BANYAK pengamatan pasang tinggi
daripada pencuplikan acak. Yang tidak terwakili justru surut terdalam, dan itu
tidak menjadi masalah karena rob tidak terjadi saat surut.

Perlu dicatat: argumen yang beredar di tim — bahwa fase bergeser sepanjang
bulan lunar — hanya benar sebagian. M2 (12,42 jam) dan O1 (25,82 jam) memang
menyapu penuh dalam dua minggu, tetapi S2 tidak pernah bergeser sama sekali,
dan K1 serta P1 bergeser dengan periode sekitar satu tahun.

Gambar: `docs/pasut_saat_akuisisi.png` dan `.svg`.

### Klaim produk: diperbaiki, bukan diturunkan

Sesi sebelumnya menurunkan klaim menjadi "indeks kerentanan". Itu terlalu
merendahkan. Sistem ini memang MEMPREDIKSI — yang keliru hanya menyebut
sumber prediksinya.

Klaim yang dipakai sekarang: **memprediksi KAPAN tiap ruas berisiko tergenang
untuk 72 jam ke depan, dengan komponen waktu dari rekonstruksi pasut yang
tervalidasi terhadap data terukur stasiun BIG (korelasi 0,78 sampai 0,91,
RMSE 0,10 sampai 0,12 m) dan komponen ruang dari indeks kerentanan per ruas.**

Yang gugur hanyalah klaim bahwa prediksi itu dipelajari dari genangan teramati
Sentinel-1.

Subjudul karya ikut berubah, dari "Berbasis Kalibrasi Citra Radar Sentinel-1"
menjadi "Berbasis Rekonstruksi Pasang Surut Terkalibrasi". **Ini perlu
diselaraskan ke Figma, slide, dan judul video.**

### Supabase hidup, aplikasi berjalan di atasnya

Sambungan pertama gagal dengan pesan yang menyesatkan — psycopg2 menyebut
socket lokal padahal host-nya Supabase. Penyebabnya kata sandi memuat `@`,
sehingga pengurai URL memotong di `@` terakhir dan sisa sandi terbaca sebagai
nama host. `scripts/13_periksa_database.py` dibuat untuk menemukan hal ini
tanpa pernah mencetak kata sandinya.

Setelah diperbaiki dan dipindah ke connection pooler: PostGIS 3.3 aktif,
skema terpasang, dan seluruh pipeline dijalankan ulang dari nol menuju
Supabase — 19.394 ruas berfitur, 102.552 baris pemicu, 21.778 prediksi. Itu
sekaligus membuktikan pipeline-nya reprodusibel tanpa Docker lokal.

### B4 selesai, dan satu masalah baru yang ditemukan karenanya

Kolam koneksi `ThreadedConnectionPool` maksimum lima, ditambah cache kesehatan
lima detik sehingga `database_tersedia()` tidak lagi membuka koneksi
sendiri — sebelumnya tiap permintaan membuka DUA koneksi.

Pengukuran setelahnya membongkar masalah yang tidak pernah terlihat di Docker:
**permintaan rute pertama memakan 11,9 detik**, sisanya 1,3 detik. Graf 19.394
ruas dibangun saat permintaan datang, dan lewat jaringan ke Sydney itu mahal.
Sebelas detik itu jatuh tepat pada klik pertama, dan di babak final pengguna
pertamanya adalah juri.

Diperbaiki dengan memanaskan cache saat startup di utas terpisah. Permintaan
pertama kini **1,7 detik**.

### Yang dibuat

- `backend/scripts/12_uji_isyarat_s1.py`, `13_periksa_database.py`,
  `14_uji_dua_arah.py`, `15_gambar_bukti.py`
- `--radius-m` pada skrip 08, `--berkas`, `--label`, dan kurva kalibrasi pada
  skrip 09
- Kolam koneksi dan cache kesehatan di `app/db.py`
- Pemanasan cache dan penutupan kolam di `app/main.py`
- `backend/requirements-analisis.txt` — matplotlib, terpisah dari
  requirements utama supaya server yang di-deploy tetap ramping
- `docs/pasut_saat_akuisisi.png` dan `.svg`, `docs/kepentingan_fitur.png`

### Yang TIDAK dikerjakan

Uji luas air kawasan terbuka setelah topeng air permanen dibuang belum
selesai; ia menunggu Earth Engine lebih dari satu jam. Hasil parsialnya sudah
cukup untuk menyimpulkan, dan skripnya bisa dijalankan ulang kapan saja.

---

## M5 — 29 Agustus 2026: panel dampak, halaman validasi, FEATURE FREEZE

**Status: selesai.** Setelah entri ini tidak ada fitur baru sampai submit.

### Skenario wajib berjalan tanpa dituntun

Diuji di peramban sungguhan, bukan diasumsikan:

    buka aplikasi -> tekan Pelabuhan Tanjung Emas -> tekan Kawasan Industri
    Terboyo -> rute muncul -> panel dampak terisi -> peringatan paparan keluar
    -> saran jam alternatif bisa ditekan -> geser Pita Pasut -> rute berubah

**Nol galat di konsol.** Satu-satunya pengecualian terjadi saat pengembangan
dan itu justru pengaman yang bekerja: `t()` melempar galat karena placeholder
`{tanggal}` tidak diisi. Mekanisme yang dipasang di M2 menangkap kesalahan
yang seharusnya lolos ke layar.

### Satu perubahan rancangan yang lahir dari mengujinya

Tombol tujuan cepat semula selalu mengisi TUJUAN. Saat skenario dijalankan,
menekan satu tombol tidak menghasilkan apa-apa karena asal masih kosong —
dan orang yang baru melihat aplikasi akan menyimpulkan aplikasinya rusak,
bukan bahwa ia belum mengetuk peta.

Sekarang tombol mengisi SLOT YANG KOSONG: asal lebih dulu, lalu tujuan. Dua
kali tekan sudah menghasilkan rute tanpa perlu menyentuh peta sama sekali.

### Fitur yang DIPOTONG, dan alasannya

Brief M5 meminta perbandingan visual prediksi versus genangan teramati untuk
dua sampai tiga kejadian uji. **Dipotong, dan bukan karena kehabisan waktu:
bahannya tidak ada.** Tidak ada satu pun pengamatan genangan per ruas jalan
di repo ini. Menyandingkan dua peta tanpa kebenaran lapangan berarti
membandingkan tebakan dengan tebakan lalu menyebutnya validasi.

Halaman validasi memuat blok khusus yang menyatakan hal itu, dan alasannya
masuk peta jalan di proposal.

### Lantai mutu DESIGN.md Bagian 11, diperiksa satu per satu

| Butir | Status | Bukti |
|---|---|---|
| Responsif sampai 360px | **BELUM TERVERIFIKASI** | jendela diubah ke 360px tetapi viewport tetap 1440; perlu diuji di perangkat atau devtools sungguhan |
| Fokus papan ketik terlihat | terpenuhi | `:focus-visible` 2px `--rute` offset 2px di `dasar.css` |
| `prefers-reduced-motion` | terpenuhi | `dasar.css` baris 133, pudar silang 80 ms |
| Pita Pasut lewat papan ketik | terpenuhi | `role="slider"`, `aria-valuetext` terisi, PageUp/Down berfungsi |
| Kedalaman tidak lewat warna saja | terpenuhi | pola titik halftone dua kerapatan di peta DAN legenda |
| Kontras teks minimal 4.5:1 | **terpenuhi setelah diperbaiki** | 3 kegagalan ditemukan dan dibetulkan, lihat di bawah |
| Sasaran sentuh 44×44 | **terpenuhi setelah diperbaiki** | 8 elemen di bawah ambang ditemukan dan dibetulkan |
| Terbaca di bawah matahari | **BELUM DIUJI** | perlu orang membawa laptop ke luar ruangan |
| Terbaca saat dicetak hitam putih | terpenuhi secara rancangan | dua kelas terdalam dibedakan pola, bukan warna; belum diuji cetak sungguhan |

**Dua kegagalan yang ditemukan dan diperbaiki.**

Kontras: `--tinta-2` dipakai di atas rail gelap dan hanya mencapai **2,13:1**.
Tokennya sendiri tidak salah — ia dirancang untuk latar TERANG, dan
`--tinta-3` di latar yang sama mencapai 5,50:1. Yang keliru pemakaiannya.
Diperbaiki di `.titik__kosong` dan `.tombol-utama:disabled`. Tombol nonaktif
sebenarnya dikecualikan WCAG 1.4.3, tetapi 2,13:1 membuatnya nyaris hilang.

Sasaran sentuh: enam tombol baru berukuran 40px dan dua kontrol zoom bawaan
MapLibre berukuran 29px. Kontrol MapLibre tidak bisa diubah lewat opsinya,
hanya lewat CSS. Seluruhnya kini 44px.

### Yang dibuat

- `backend/app/domain/dampak.py` — selisih waktu, jarak, liter, kg CO2e.
  Setiap faktor membawa komentar sumbernya, termasuk pernyataan terbuka
  bahwa konsumsi bahan bakar masih asumsi tanpa sitasi
- `GET /api/tujuan-cepat` dan `GET /api/validasi`
- `backend/scripts/17_tujuan_cepat.py` — empat POI diambil dari OSM lalu
  DILEKATKAN ke simpul jalan terdekat, sehingga tombol tidak pernah
  mengembalikan galat "terlalu jauh dari jalan"
- `kedalaman_per_ruas_cm` pada `HasilRute`, dipakai peringatan paparan
- `PanelDampak.jsx`, `PeringatanPaparan.jsx`, `TujuanCepat.jsx`,
  `pages/HalamanValidasi.jsx`
- Manifest PWA, service worker, dan tiga ikon
- 15 kunci teks baru di kedua `copy.id.json`

### Dua cacat tampilan yang ditemukan saat menguji

Pemisah desimal tidak konsisten: panel lama memakai titik (`9.7`) sementara
panel baru memakai koma (`1,7`). Seluruhnya kini koma.

Bahan bakar tampil `0,000–0,000` untuk selisih rute yang sangat pendek.
Angkanya benar tetapi terbaca seperti rusak. Kini ditampilkan `< 0,001`.

### Service worker: sengaja TIDAK luring penuh

Hanya cangkang aplikasi yang di-cache. Seluruh permintaan `/api/` selalu
menembus ke jaringan. Untuk aplikasi yang menyarankan kapan orang boleh
berangkat menembus air, prediksi basi lebih berbahaya daripada layar kosong.

### Yang TIDAK dikerjakan

Uji responsif 360px sungguhan, uji baca di bawah matahari, dan uji cetak
hitam putih. Ketiganya memerlukan perangkat atau orang, bukan kode.

---

## Tambahan 29 Agustus 2026: upaya penyelamatan keempat, dan korelasi semu

Dijalankan setelah feature freeze karena tidak menyentuh fitur — hanya
pengujian dan dokumentasi.

**Dugaan yang diuji.** Seluruh pengujian sebelumnya membandingkan label
Sentinel-1 terhadap pasut ASTRONOMIS. Rob sesungguhnya terjadi saat pasang
astronomis bertemu angin, tekanan udara, dan gelombang badai. Bisa jadi
labelnya benar dan pembandingnya yang kurang lengkap.

**Hasil pertama tampak meyakinkan.** Muka air terukur stasiun IOC `sema`
ditarik untuk 725 waktu akuisisi, 699 berhasil. Korelasi label melonjak dari
-0,03 terhadap pasut astronomis menjadi **-0,29** terhadap muka air terukur.

**Dan seluruhnya semu.** Dua hal yang menyingkapnya:

Pertama, kriteria "turun" dan "naik" berkorelasi hampir sama besar dengan
tanda berlawanan (-0,290 dan +0,291). Kalau genangan penyebabnya, salah satu
arah seharusnya jauh lebih kuat. Simetri itu tanda khas pergeseran
radiometrik SELURUH citra.

Kedua, rekaman stasiun MELAYANG NAIK 0,92 meter dalam sepuluh tahun — median
+0,861 m pada 2015 menjadi +1,781 m pada 2025. Arsip Sentinel-1 juga berubah
sepanjang dekade yang sama: 1A ke 1B lalu 1C, dengan baseline pengolahan yang
diperbarui. Dua deret yang sama-sama melayang akan berkorelasi tanpa hubungan
sebab.

Setelah layangan diluruskan per tahun, korelasinya tinggal **+0,05** dan
**-0,11**. Putusan skrip berubah dari "LABEL BERMAKNA" menjadi "TETAP DATAR".

**Keempat jalur penyelamatan kini tertutup**, dan penutupannya dibuktikan
bukan diasumsikan.

**Pelajaran yang layak dicatat.** Angka -0,29 sempat saya laporkan sebagai
petunjuk kuat sebelum diluruskan. Yang menyelamatkan bukan kehati-hatian
melainkan dua pemeriksaan mekanis: memeriksa apakah rentang nilainya masuk
akal secara fisik, dan memeriksa apakah tanda korelasinya simetris. Keduanya
sekarang tertanam di dalam skrip 16 sehingga tidak bergantung pada ingatan.

**Temuan sampingan.** Kenaikan muka air relatif sekitar 9 cm per tahun di
stasiun itu tercatat sebagai B34. Bukan kenaikan muka laut absolut, dan
jangan dikutip sebagai itu.

---

## M6 — 29 Agustus 2026: tahan banting, artefak deploy, audit kepatuhan

**Status: selesai untuk bagian yang bisa dikerjakan kode.** Penerapan
sesungguhnya ke Render dan Vercel menuntut pembuatan akun dan persetujuan
OAuth, dan itu di luar batas yang boleh saya kerjakan. Seluruh artefaknya
sudah siap dan sudah DIUJI, jadi yang tersisa hanya menekan tombol.

### Yang terpenting: aplikasi tidak bisa mati

`scripts/18_seed_demo.py` membekukan potret 72 jam ke
`data/processed/potret_demo.json`. Diuji dengan `DATABASE_URL` sengaja
dirusak:

| Endpoint | Tanpa database |
|---|---|
| `/api/kesehatan` | 200 · 0,16 s |
| `/api/jam` | 200 · 0,005 s |
| `/api/ruas` | 200 · 0,095 s |
| `/api/genangan` | 200 · 0,11 s |
| `/api/validasi` | 200 · 0,009 s |
| `/api/tujuan-cepat` | 200 · 0,004 s |
| `/api/rute` | 200 · 0,069 s |

Tujuh dari tujuh hidup, dan **peruteannya justru lebih cepat** daripada lewat
Supabase (0,07 detik berbanding 1,3 detik).

Yang TIDAK dibekukan: hasil rute. Membekukannya berarti menyiapkan jawaban
untuk pasangan titik pilihan kita sendiri, dan juri yang mengetuk titik lain
akan menemukan aplikasinya diam. Graf dibangun dari potret, jadi perutean
tetap menghitung sungguhan.

Potret membawa `berlaku_sampai` dan **ditolak API setelah kedaluwarsa**.
Untuk sistem yang menyarankan kapan orang boleh menembus air, prediksi basi
lebih berbahaya daripada layar kosong.

### Dua bug ditemukan karena mengujinya, bukan karena membacanya

**Potret tanpa simpul ujung.** `geojson()` tidak memuat `osm_u` dan `osm_v`
karena frontend tidak membutuhkannya. Tetapi mesin routing membangun grafnya
dari pasangan simpul itu; tanpa keduanya seluruh 19.394 ruas tersambung ke
simpul yang sama, graf menjadi satu titik, dan perutean gagal dengan
`IndexError` yang tidak menyebut sebabnya sama sekali.

**Tiga `db.koneksi()` tanpa penjagaan.** Endpoint genangan, validasi, dan
rute masih membuka koneksi langsung meski database mati. Ketiganya hanya
ketahuan dengan benar-benar mematikan database, tidak dengan membaca kode.

### Audit ketergantungan runtime: LULUS, ditegakkan tiga lapis

1. `backend/app/` tidak mengimpor satu pun pustaka jaringan. Diperiksa dengan
   AST, bukan dengan grep: yang dipakai hanya `fastapi`, `pydantic`,
   `psycopg2`, `numpy`, `dotenv`.
2. Gaya peta MapLibre ditulis inline — tanpa URL ubin, glyph, atau sprite.
3. **Citra Docker tidak memasang** `earthengine-api`, `osmnx`, `geopandas`,
   `rasterio`, `scikit-learn`, `pandas`. Diverifikasi dengan mengimpornya di
   dalam kontainer yang berjalan; keenamnya `ImportError`.

Lapis ketiga itu yang paling berharga. Aturan repo nomor 6 kini ditegakkan
oleh isi kontainer, bukan oleh niat baik siapa pun.

### Citra Docker: 1,44 GB menjadi 244 MB

Dua sebab, keduanya ketahuan dari mengukur:

`requirements.txt` memuat seluruh alat pipeline. Dibuat
`requirements-runtime.txt` berisi lima paket yang benar-benar diimpor
`backend/app/`. 1,44 GB → 723 MB.

`.dockerignore` saya taruh di `backend/`, padahal konteks build-nya akar
repo — jadi tidak pernah dibaca, dan `COPY data/processed` menyalin 471 MB
tarikan Sentinel-1 ke dalam citra. Dipindah ke akar. 723 MB → **244 MB**.

### 6a. Audit teks: NOL temuan

Perintah bantu memberi 16 baris. Diperiksa satu per satu: dua di dalam
komentar, sepuluh literal GeoJSON (`"FeatureCollection"`, `"Point"`), empat
nama tombol DOM (`"ArrowLeft"`, `"PageDown"`). **Tidak ada satu pun kalimat
antarmuka berbahasa Indonesia yang ditulis harfiah di komponen.**

Diperiksa juga dengan dua pola yang lebih tajam — teks JSX yang benar-benar
dirender, dan atribut `title`/`placeholder`/`alt`/`aria-label` berisi literal
— keduanya nol.

### 6b. Audit kepatuhan visual PLAN.md Bagian 12B

| Butir | Status | Bukti |
|---|---|---|
| Warna, ukuran huruf, radius, jarak dari DESIGN.md | **LULUS setelah diperbaiki** | 2 nilai jarak `2px` di luar skala `--s-*` diganti `var(--s-1)`; 3 nilai `44px` diganti `var(--sentuh-min)` yang ternyata sudah ada |
| Tidak ada heks di komponen | LULUS | 0 temuan; satu-satunya kemunculan ada di dalam komentar yang melarangnya |
| Barlow + IBM Plex Mono termuat | LULUS | 6 `@import "@fontsource/..."` di `dasar.css`, swadaya bukan CDN |
| Pita Pasut lewat papan ketik | LULUS | `role="slider"`, `aria-valuetext` terisi, PageUp/Down berfungsi |
| Kedalaman lewat warna DAN pola | LULUS | pola titik dua kerapatan di peta dan legenda |
| Tidak ada shadcn / Material | LULUS | `package.json` bersih dari shadcn, mui, antd, chakra, bootstrap, tailwind |
| Tidak ada emoji sebagai ikon | LULUS | 0 temuan pada rentang Unicode emoji |
| Peta konten penuh layar | LULUS | `.jendela-peta` mengisi layar, rail di sampingnya, bukan kartu di atas kisi |
| Lantai mutu DESIGN.md Bagian 11 | **GAGAL SEBAGIAN** | 3 dari 9 butir belum terpenuhi — lihat B30 dan B31 |
| Tidak ada kalimat Indonesia di komponen | LULUS | audit 6a, nol temuan |
| `t()` melempar galat | LULUS | terbukti di M5: melempar karena placeholder `{tanggal}` tidak diisi |
| Istilah mengikuti glosarium | LULUS | "segmen", "banjir rob", "transportasi" hanya muncul di dalam definisi glosarium yang melarangnya |

**Sepuluh LULUS, satu LULUS setelah diperbaiki, satu GAGAL SEBAGIAN.**
Yang gagal adalah lantai mutu Bagian 11: responsif 360px belum terverifikasi,
uji baca di bawah matahari dan uji cetak hitam putih belum dilakukan.
Ketiganya butuh perangkat atau orang.

### Yang dirapikan

- Tiga notebook rintisan berisi "Kosong. Diisi pada milestone model" dihapus.
  Analisisnya ada di skrip 12, 14, 15, dan 16 — yang bisa dijalankan ulang
  dan diuji, tidak seperti notebook.
- `BAGIAN_3_TERISI.yaml` → `docs/identitas_tim.yaml`, dan `jumlah_citra_s1`
  diperbaiki dari `"BELUM ADA"` menjadi 725. Komentar ambang keputusan lama
  ("80-150 = pangkas fitur model") dibuang karena sudah tidak berlaku:
  citranya 725 dan modelnya tetap ditolak, bukan karena kurang citra.
- `CHECKLIST_MALAM_INI.md` → `docs/checklist_pendaftaran.md`.
- Akar repo kini hanya memuat berkas yang memang milik akar.

### Yang dibuat

- `backend/scripts/18_seed_demo.py` — potret tahan banting
- `backend/Dockerfile` (244 MB, diuji jalan), `.dockerignore` di akar,
  `render.yaml`, `Procfile`, `frontend/vercel.json`
- `backend/requirements-runtime.txt`
- CORS dari `ASAL_DIIZINKAN` dan `ASAL_POLA`, daftar putih bukan `*` —
  diuji: asal terdaftar lolos, asal asing tidak mendapat header
- `README.md` ditulis ulang penuh sesuai PLAN.md bagian 11
- `docs/demo_script.md` — naskah 4 menit 30 detik plus enam pertanyaan yang
  hampir pasti muncul beserta jawabannya

### Yang TIDAK bisa saya kerjakan

**Penerapan sesungguhnya.** Render, Railway, dan Vercel semuanya menuntut
pembuatan akun, kata sandi, dan persetujuan OAuth. Saya tidak membuat akun
dan tidak menyetujui syarat layanan atas nama tim. Ini batas aturan, bukan
batas alat.

**Uji dari HP di jaringan seluler.** Perlu perangkat fisik.

---

## M7 — 29 Agustus 2026: draft proposal 14 bagian, dan rantai dampak yang jujur

**Status: selesai.**

### Rantai dampak: angkanya dihitung, bukan dikarang

Placeholder `[[ISI]]` pada rantai estimasi sebagian bisa dihitung dari sistem
sendiri. `scripts/19_rantai_dampak.py` merutekan 150 pasangan asal-tujuan acak
berjarak minimal 2 km pada jam pasut tertinggi, lalu melaporkan median dan
kuartil — bukan rata-rata, karena sebarannya sangat menceng.

| Ukuran | Nilai |
|---|---|
| Rute berubah karena rob | 44 persen dari 150 pasangan |
| Selisih waktu per perjalanan | median 0,12 mnt · p75 1,67 mnt |
| Selisih jarak per perjalanan | median 0,00 km · p75 0,14 km |
| Hemat menggeser jam berangkat | median 0,14 mnt · p90 2,99 mnt · maks 6,83 mnt |

**Angkanya kecil, dan itu temuan.** Sebabnya bisa dijelaskan: jaringan jalan
Semarang rapat sehingga memutar mengelilingi ruas tergenang biasanya pendek,
dan pada jendela yang diuji tidak ada ruas yang melampaui ambang tak-bisa-lewat
sehingga tidak ada ruas yang benar-benar dibuang dari graf.

Ukuran pertama sempat memakai moda mobil dan hasilnya lebih kecil lagi (median
0,03 menit). Sebabnya kedalaman puncak 40 cm sementara ambang tak-bisa-lewat
mobil 50 cm — tidak ada satu pun ruas yang dibuang. Motor berambang 30 cm,
sehingga dipakai untuk pelaporan, dan modanya disebutkan.

Ditambahkan ukuran kedua yang lebih tepat mengukur klaim produk: nilai
**menggeser jam berangkat**, bukan nilai memutar. Klaim sistem ini adalah
memprediksi KAPAN, jadi nilainya muncul saat orang memindahkan jam berangkat.

### Keputusan yang paling penting di sesi ini

**Nilai rupiah TIDAK dihitung.** Mengalikan 0,14 menit dengan jumlah perjalanan
per hari yang belum bersumber dan tingkat adopsi yang kami tetapkan sendiri
akan menghasilkan angka rupiah besar yang seluruh besarnya berasal dari dua
bilangan karangan.

Bagian 11.5 menjelaskan hal itu terbuka, termasuk pengakuan bahwa nilai
sesungguhnya sistem ini kemungkinan bukan pada menit yang dihemat melainkan
pada kerusakan kendaraan dan paparan kesehatan yang dihindari — dan keduanya
tidak kami ukur.

### Draft proposal

`docs/proposal_draft.md`, 14 bagian persis sesuai rulebook, **4.305 kata pada
Bagian 1–14**, perkiraan **28,9 halaman** termasuk enam tangkapan layar. Masuk
batas 30 dengan sisa sekitar satu halaman.

Perkiraan halaman dihitung dari acuan terukur: `.docx` yang ada memuat 4.242
kata dalam 27 halaman, yaitu 157 kata per halaman. Perkiraan pertama saya
meleset karena menghitung seluruh berkas termasuk 711 kata materi untuk tim
yang tidak masuk dokumen Word; dikoreksi.

Delapan `TODO(sumber)` diurutkan menurut akibatnya bila ditanya juri. Empat
wajib diisi, dua boleh tetap kosong karena Bagian 11.5 sudah berdiri tanpa
keduanya, satu ringan, satu bukan TODO melainkan asumsi yang harus tetap
ditulis sebagai asumsi.

### Peringatan yang saya sampaikan, bukan saya putuskan sendiri

Proposal kini punya **dua sumber kebenaran**: `.docx` di akar dan draft
Markdown ini. Keduanya memuat isi yang sama hari ini dan akan menyimpang dalam
satu sesi bila dibiarkan. Saya tidak menghapus salah satunya — itu keputusan
tim. Tercatat sebagai B38.

### Yang TIDAK dikerjakan

Pemformatan Word (M8), pengisian TODO yang butuh sumber luar, dan enam
tangkapan layar aplikasi.

---

## M8 — 29 Agustus 2026: audit akhir sebelum unggah

**Status: selesai.** Peran sesi ini audit, bukan perbaikan. Temuan dilaporkan,
tidak diperbaiki diam-diam, kecuali dua berkas dokumentasi baru.

### Temuan paling penting: repo publik tertinggal lima commit

Diuji dengan `git clone` tanpa kredensial ke direktori bersih. Repo **memang
publik** dan bisa di-clone, tetapi HEAD-nya `1b7c475` (M4) sementara lokal
`438e261` (M7).

Yang **tidak ada** di repo yang akan dibaca juri: `domain/dampak.py`,
`HalamanValidasi.jsx`, `Dockerfile`, `render.yaml`, `vercel.json`,
`potret_demo.json`, `proposal_draft.md`, `demo_script.md`.

Tidak saya push sendiri: mendorong ke repo publik adalah tindakan keluar yang
belum diizinkan di sesi ini. Tercatat sebagai B41 dan M1 di `tugas_manual.md`.

### Temuan kedua: `.docx` memuat DUA subjudul

Halaman sampul masih "Berbasis Kalibrasi Citra Radar Sentinel-1"; Bagian 1
dokumen yang sama sudah "Berbasis Rekonstruksi Pasang Surut Terkalibrasi".
Pembaruan pada M4-lanjutan hanya menyentuh Bagian 1, tidak sampulnya — dan
sampullah yang pertama dilihat juri. B42.

### Audit angka: bersih

Audit pertama memakai regex atas seluruh angka memberi 63 "temuan". Diperiksa
ulang pada tingkat kalimat, seluruhnya positif palsu: sitasi berada di akhir
kalimat yang membentang beberapa baris, atau angkanya keluaran sistem sendiri
dan parameter rancangan yang tidak menuntut sitasi luar.

Audit terarah atas 15 klaim tentang dunia luar: **seluruhnya bersitasi atau
ditandai `TODO(sumber)`**. Tidak ada angka karangan.

Pelajarannya: heuristik kasar atas angka menghasilkan 63 alarm palsu dan nol
temuan nyata. Yang menemukan sesuatu justru daftar klaim yang disusun manual.

### Audit README versus proposal: nol pertentangan

26 angka kunci dibandingkan. Setiap angka yang muncul di keduanya cocok
persis. Beberapa hanya muncul di salah satu, dan itu wajar.

Satu catatan kecil: kalimat pembuka README tidak menyebut "wilayah pilot"
sementara proposal menyebutnya. Bukan pertentangan, tetapi README bisa terbaca
seolah cakupannya seluruh kota. README menyebut "wilayah pilot" dua kali di
bagian lain, jadi tidak menyesatkan pembaca yang membaca sampai selesai.

### Audit repo

| Yang diperiksa | Hasil |
|---|---|
| Rahasia di seluruh riwayat git | **bersih**, nol temuan pada 15 commit |
| Berkas terlacak terbesar | 7,4 MB `potret_demo.json`, memang dibutuhkan |
| Ukuran `.git` | 11 MB, sehat |
| Komponen frontend yatim | nol |
| Fungsi domain tak terpakai | satu: `deret_pasut()`, diwajibkan PLAN 10.2 |
| Berkas basi di akar | `pratinjau_proposal.pdf` dari 23 Agustus |

### Yang dibuat

- `docs/checklist_submit.md` — 46 butir dari PLAN.md 12 dan 12B dengan status
  per butir. Ringkasannya: **16 selesai, 7 sebagian, 23 belum**
- `docs/tugas_manual.md` — satu tempat untuk seluruh tugas manual dari seluruh
  sesi, 30 butir, diurutkan menurut kemendesakan

### Yang TIDAK dikerjakan, sesuai batas peran

Pemformatan Word, ekspor PDF, unggah video, Twibbon dan poster. Seluruhnya
dikerjakan manusia menurut brief sesi ini.

---

## M9 lanjutan — 29 Agustus 2026: perbaikan setelah verifikasi

Dikerjakan setelah tim melakukan push dan deploy.

### Bug lencana diperbaiki, dan ini yang paling penting

`/api/rute` memadatkan list bersatu anggota menjadi string sebagai
"kemudahan": `sumber[0] if len(sumber) == 1 else sumber`. Endpoint lain
mengembalikan list. `LencanaContoh.jsx` menolak yang bukan array, sehingga
**lencana peringatan hilang tepat setelah pengguna menghitung rute** — di
tengah alur demo, pada layar yang dilihat juri.

Aturan repo nomor 2 menuntut lencana muncul selama sumbernya belum model
tervalidasi. Bentuk data yang tidak konsisten antar endpoint membatalkan
jaminan itu tanpa satu pun galat yang terlihat.

Diverifikasi di peramban setelah diperbaiki: lencana "INDEKS KERENTANAN —
bukan prediksi genangan" bertahan saat aplikasi dibuka, setelah rute dihitung,
dan pada jam pasut puncak.

### Temuan deploy: frontend menunjuk ke localhost

Bundel di Vercel memuat `http://127.0.0.1:8000`. `VITE_API_URL` tidak pernah
diisi, jadi setiap panggilan API pergi ke laptop pengunjung sendiri. API dan
CORS-nya sendiri sudah benar — `render.yaml` memasang `ASAL_POLA` berpola
`*.vercel.app` sehingga Vercel diizinkan tanpa perlu variabel tambahan.
Tercatat sebagai B45.

### Yang diperbaiki di dokumen

- Sampul `.docx` memakai subjudul lama; dokumen tadinya memuat DUA subjudul.
  Kini satu. Tetap 27 halaman.
- `pratinjau_proposal.pdf` dari 23 Agustus dihapus.
- README menyematkan dua gambar dan mengisi tautan live.
- Proposal merujuk pustaka [8] sampai [11] yang tadinya yatim.
- Bagian 5 bertambah dua batasan: **penalti perutean 1,0/2,5/8,0 adalah angka
  rancangan** yang menentukan seluruh isi Bagian 11, dan **sebagian besar
  kejadian rob yang dipakai memvalidasi berstatus belum terverifikasi**.
- `docs/validasi.md` 6.5 dikoreksi: uji topeng air permanen kini SELESAI,
  bukan "tidak selesai dalam waktu sesi ini". Hasilnya dicatat apa adanya
  beserta empat alasan mengapa ia tetap tidak mencabut penolakan model.
