# Progres

Satu entri per sesi kerja. Ditulis apa adanya, termasuk yang gagal.

Bagian **Papan Blokade** di bawah ini adalah ringkasan keadaan sekarang dan
diperbarui setiap sesi. Kalau hanya sempat membaca satu bagian dari berkas
ini, baca bagian itu.

---

## PAPAN BLOKADE — keadaan per 28 Agustus 2026

> Bagian ini DIPERBARUI SETIAP SESI dan selalu menggambarkan keadaan
> sekarang, bukan riwayat. Riwayat ada di entri per milestone di bawahnya.
> Sisa waktu ke tenggat: **3 hari** (31 Agustus 2026, 23.59 WIB).

### A. BLOKADE — menghentikan pekerjaan berikutnya

| # | Blokade | Menghambat | Siapa |
|---|---|---|---|
| A1 | **Supabase belum ada.** Database yang dipakai masih PostGIS lokal di Docker. `db/schema.sql` belum pernah dijalankan di Supabase. | Deploy M6, dan kerja paralel antar anggota tim | Manual |
| ~~A2~~ | **SELESAI 28 Agustus.** Acuan fase adalah WIB, dibuktikan dengan menyisir seluruh offset −12 sampai +12 jam terhadap data terukur stasiun IOC `sema`. UTC memberi korelasi NEGATIF di seluruh jendela uji, yang berarti pasang tertukar surut. | — | — |
| A3 | **SEBAGIAN SELESAI.** Proyek pertama `pasang-surut-anforcom` terverifikasi: terdaftar nonkomersial, Community tier, pemakaian 0,07 persen, uji 723 lolos, dan Python sudah tersambung. **Proyek Daffa dan Naufal masih belum ada** — kuota per proyek, jadi jatah tim baru sepertiga. | Kapasitas kuota untuk ekstraksi label M4 | Manual, dua orang |
| ~~A4~~ | **SELESAI 28 Agustus.** `data/raw/DEMNAS_1409-22_v1.0.tif`, 43 MB, terverifikasi menutupi seluruh AOI, 100 persen piksel valid, median elevasi 2,60 m. | — | — |
| A5 | **Repo belum dipublikasikan.** M1 mensyaratkan repo publik, dan juri menilai Code Project 10 persen dari sana. | Penilaian | Manual |

### B. PERLU PERHATIAN — tidak menghentikan, tetapi akan menggigit

| # | Hal | Kenapa penting |
|---|---|---|
| B1 | `BAGIAN_3_TERISI.yaml` masih menulis `jumlah_citra_s1: "BELUM ADA"`, padahal angkanya 723. Blok `???` di PLAN.md bagian 3 juga masih kosong. | Sesi berikutnya bisa berhenti karena membaca angka yang salah |
| B2 | Tautan **riset WRI April 2026** di README masih `TODO(verifikasi tautan)`. | Tautan mati di gerbang juri lebih buruk daripada tidak ada tautan |
| B3 | Commit membawa trailer `Co-Authored-By: Claude Opus 5`. | Kalau rulebook DSDC mempersoalkan, putuskan sekarang selagi baru empat commit |
| B4 | Koneksi database dibuka DUA KALI per permintaan, tanpa pooling. `database_tersedia()` membuka satu, endpoint membuka lagi. | Supabase paket gratis membatasi koneksi. Akan menggigit saat juri memakai aplikasi bersamaan di babak final |
| B5 | `copy.id.json` ada di dua tempat, akar dan `frontend/src/`, tanpa apa pun yang menjaganya sinkron. | Begitu satu disunting, keduanya menyimpang diam-diam |
| B6 | Belum ada `manifest.json`. Bentuk produk yang dikunci PLAN.md bagian 3 adalah PWA. | PWA itu yang membuat rulebook "website ATAU mobile" terpenuhi keduanya |
| B7 | Test menutupi `config.py`, `routing.py`, dan fungsi murni di skrip 06 dan 07 — 24 uji lolos. `db.py`, `main.py`, skrip 01 sampai 05, dan `teks.js` masih tanpa test. | `t()` adalah mekanisme pengaman yang melempar galat, dan tidak ada test yang membuktikan ia melempar |
| B8 | Data contoh kedaluwarsa setelah 72 jam sejak dibuat. | Kalau Pita Pasut tampak kering seluruhnya, jalankan ulang `python -m scripts.03_isi_dummy` dari `backend/` |
| B9 | Ada PostgreSQL lain di mesin ini yang memakai port 5433, jadi kontainer pengembangan dipindah ke 55433. | Jangan bingung kalau `docker run` di 5433 gagal |
| B10 | Kontras kelas genangan paling dangkal `--air-1` terhadap latar dek hanya 1,39:1. | DESIGN.md Bagian 11 mensyaratkan terbaca di bawah matahari langsung dan saat dicetak hitam putih. Belum diuji di luar ruangan |
| B11 | Kecepatan ruas untuk jalan tanpa tag `maxspeed` berasal dari imputasi OSMnx. | Asumsi, bukan pengukuran. Sudah tercatat di `docs/batasan.md` bagian 2.4 |
| B12 | Penalti genangan (1,0 → 2,5 → 8,0) adalah angka rancangan, bukan hasil pengukuran lapangan. | Juri berhak menanyakan dasarnya. Sudah tercatat di `docs/batasan.md` |
| B13 | **`geemap` versi terbaru menuntut Python 3.12**, sementara proyek dikunci 3.11. PLAN.md bagian 4 menyebutnya sebagai bagian tech stack. | Rekomendasi: JANGAN pakai geemap. `earthengine-api` saja sudah cukup untuk pipeline yang mengekspor tabel, dan geemap 0.37.2 yang masih cocok menarik lebih dari 70 paket tambahan |
| B14 | **Berkas DEMNAS tidak membawa CRS.** `rasterio` melaporkan `CRS: None` walau koordinatnya jelas derajat WGS84. | **Sudah ditangani** di `scripts/05_isi_fitur_ruas.py`, yang menetapkan `EPSG:4326` eksplisit dan mencetak peringatan saat berkas dibuka. Berlaku untuk setiap kode baru yang membuka berkas itu |
| B16 | **Proposal tersisa 20 penanda `[[ISI]]` dari semula 58.** Seluruhnya tertahan pada tugas manual atau sumber yang belum ada: tautan deploy, repo, video, Figma; angka rantai dampak yang menunggu faktor emisi; dan dua sitasi tanpa sumber (leptospirosis dan WRI), turun dari tiga. | Rincian dan status per bagian ada di `docs/sisa_proposal.md` |
| B17 | **Tujuh kotak `[ ISI MANUAL ]` sudah dikeluarkan dari proposal** dan dipindah ke `docs/sisa_proposal.md`. Isinya tidak hilang. | Kotak itu instruksi untuk penulis, bukan isi proposal, dan berisiko ikut tercetak ke PDF yang dibaca juri |
| B18 | **Angka subsidensi "9–13 cm/tahun" tidak didukung sumber yang kita punya.** Rahmawati dkk (2020) memilih varian SBAS tanpa koreksi karena RMSE-nya terkecil (±1,3 cm/th); menurut varian itu nilai TERTINGGI seluruh Kota Semarang 9,4 cm/th, rata-rata Semarang Utara 4,6 cm/th. Angka belasan hanya muncul pada varian terkoreksi atmosfer yang justru TIDAK dipilih penulisnya. | PLAN.md bagian 6 dan abstrak proposal memakai 9–13. Proposal SUDAH saya turunkan ke 9,4 karena aturan repo nomor 1, tetapi **PLAN.md belum**. Sitasinya jurnal Geodesi Undip, dan PLAN.md sendiri memperingatkan juri Geodesi Undip akan membantah. Lihat C15 |
| B19 | **Rerata hujan tahunan ERA5 1.830 mm belum diadu dengan normal BMKG.** Reanalisis diketahui meratakan hujan konvektif setempat. | Angka ini belum layak dikutip di proposal. Sudah tercatat di `docs/batasan.md` bagian 1.9 dan `docs/validasi.md` bagian 5 |
| B20 | **Enam dari 16 kejadian rob terdokumentasi terjadi pada pasut yang TIDAK tinggi**, dan hujan 24 jamnya juga sedang saja (2,5 sampai 20,4 mm). | Dua pemicu yang kita punya belum menjelaskan seluruh kejadian. Ini memperkuat alasan memakai model, tetapi juga berarti fitur angin dan kondisi tanggul absen. Rincian di `docs/validasi.md` bagian 3.2 |
| B21 | **990 dari 19.394 ruas tanpa nilai subsidensi, 26 tanpa elevasi.** Yang pertama karena kecamatannya tidak dilaporkan sumber; yang kedua karena jatuh di tepi timur tile DEMNAS. | Keduanya `NULL`, bukan nol — gradient boosting menangani `NULL`, tetapi jangan sampai ada kode yang mengisinya dengan nol diam-diam |
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
