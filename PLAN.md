# PLAN.md — PASANG SURUT

Spesifikasi eksekusi untuk Claude Code. Baca seluruh file ini sebelum menulis baris kode pertama.

---

## 0. CARA MEMPERLAKUKAN DOKUMEN INI

Kamu adalah agen pengembang untuk tim 3 mahasiswa IT yang mengikuti lomba dengan tenggat keras.

**Aturan main:**

1. **Jangan pernah mengarang angka.** Kalau butuh angka dan tidak ada sumbernya, tulis `TODO(sumber)` dan lanjut. Kriteria penilaian menghukum overclaim sebesar 20%.
2. **Jangan menambah fitur di luar daftar MVP** di bagian 6. Kalau punya ide bagus, tulis di `IDEAS.md`, jangan diimplementasikan.
3. **Kalau menemui ambiguitas, berhenti dan tanya.** Jangan berasumsi. Satu asumsi salah di hari ke-3 berarti dua hari terbuang.
4. **Commit kecil dan sering**, pesan commit bahasa Indonesia yang deskriptif. Juri menilai Code Project 10% di final termasuk praktik pengembangan.
5. **Setiap modul harus bisa dijalankan sendiri** sebelum diintegrasikan. Tidak ada big bang integration.
6. **Prioritas kalau waktu menipis:** aplikasi jalan > fitur lengkap. Lebih baik 5 fitur solid daripada 9 fitur setengah jadi.

**Konvensi penamaan:** istilah domain pakai Bahasa Indonesia (`genangan`, `pasut`, `ruas`, `kedalaman_cm`), istilah teknis pakai Inggris (`router`, `service`, `repository`, `schema`). Komentar dan docstring Bahasa Indonesia.

---

## 1. KONTEKS LOMBA

**Lomba:** Diponegoro Software Development Competition (DSDC), rangkaian ANFORCOM 2026, HMIF Universitas Diponegoro.

**Tema besar:** *Circular Economy for Eco-Health Cities*
**Tema DSDC:** *Engineering the Circular City: Software Solutions for a Sustainable and Healthy Urban Future*
**Subtema dipilih:** Nomor 4 — Smart Low-Carbon Urban Mobility

**Kaitan tema:** Rulebook halaman 2 menyatakan masalah cukup relevan dengan **salah satu atau keduanya** dari Circular Economy atau Eco-Health. Proyek ini mengambil jalur **Eco-Health** (paparan air genangan dan risiko leptospirosis) plus **efisiensi energi perkotaan** (emisi akibat memutar). Jangan paksakan narasi Circular Economy — cukup sebutkan sebagai dampak sekunder berupa kerusakan komponen kendaraan akibat paparan air asin.

**SDG:** SDG 11 (kota tangguh), SDG 13 (adaptasi iklim), SDG 3 (kesehatan).

### Tenggat

| Tanggal | Kegiatan |
|---|---|
| **31 Agustus 2026, 23.59 WIB** | Batas kumpul proposal + progres 50–75% |
| 16 September 2026 | Pengumuman finalis (5 tim) |
| 22 September 2026 | Technical Meeting |
| 26 September 2026 | Final offline di Universitas Diponegoro |

**Hari ini: 23 Agustus 2026. Sisa 9 hari.**

### Bobot penilaian — pakai ini untuk memutuskan prioritas

**Babak penyisihan (yang harus dikejar sekarang):**

| Kriteria | Bobot | Implikasi teknis |
|---|---|---|
| Impact Projection | 20% | Rantai estimasi eksplisit, tiap angka bersumber, tampilkan ketidakpastian |
| Progres & Validasi Implementasi | 20% | Fitur inti benar-benar jalan, bukan mockup |
| Kesesuaian Tema/Subtema | 15% | Konteks Semarang harus kental di seluruh UI |
| Originalitas dan Kreativitas | 15% | Kalibrasi Sentinel-1 adalah pembedanya |
| Format & Struktur Proposal | 10% | Ikuti sistematika 14 bagian persis |
| Video | 10% | 3–7 menit, wajah peserta wajib tampil sepanjang video |
| Metodologi Pengembangan | 10% | Dokumentasikan metode, analisis kebutuhan, arsitektur |

**Babak final (rancang produk untuk ini sejak sekarang):**

| Kriteria | Bobot | Implikasi teknis |
|---|---|---|
| Presentasi | 30% | — |
| **Keberhasilan Implementasi** | **25%** | **Juri memakai aplikasi langsung sebagai user.** Ini alasan aplikasi harus jalan tanpa dependensi jaringan yang rapuh |
| Sesi Tanya Jawab | 20% | Setiap batasan harus sudah kamu tulis sendiri di proposal |
| Pameran | 15% | Peta harus memukau saat dilihat sekilas dari jarak 2 meter |
| Code Project | 10% | Struktur, keterbacaan, dokumentasi, praktik pengembangan |

---

## 2. RINGKASAN PRODUK

**Nama kerja:** PASANG SURUT (lihat bagian 3, nama final belum dikonfirmasi)

**Satu kalimat:** Mesin perutean sadar rob untuk Semarang yang memprediksi genangan di jaringan jalan sampai 72 jam ke depan, lalu merutekan warga dan logistik menghindari ruas yang akan tergenang pada jam keberangkatan mereka.

**Masalah yang dijawab:** Riset World Resources Institute Indonesia (April 2026) menemukan sekitar 10% jaringan jalan Semarang — setara 11% aktivitas mobilitas — berpotensi terdampak rob, dengan total kerugian akibat gangguan transportasi sekitar **Rp848 miliar per tahun**. WRI sendiri menyatakan pendekatan berbasis infrastruktur fisik belum cukup dan diperlukan pergeseran ke perencanaan transportasi yang lebih adaptif.

**Kenapa perangkat lunak, bukan tanggul:** Tanggul tidak akan selesai sebelum besok pagi. Warga tetap harus berangkat kerja.

**Pembeda teknis:** Model genangan **dikalibrasi dari genangan yang benar-benar teramati** lewat citra radar Sentinel-1, bukan model bathtub naif berbasis ambang elevasi. Ini penting karena DEMNAS punya RMSE vertikal 2,79 m sementara rob yang dimodelkan tingginya 10–50 cm — ambang elevasi absolut secara matematis tidak sah dan akan dibantah juri dari Teknik Geodesi Undip.

---

## 3. ASUMSI YANG HARUS DIKONFIRMASI SEBELUM EKSEKUSI

> **Claude Code: jangan mulai coding sebelum blok ini terisi.** Minta user mengisinya.

```yaml
# WAJIB — memblokir deliverable
nama_tim:            "???"    # dipakai di nama file proposal & judul video
nama_karya:          "???"    # nama aplikasi final, dipakai di nama file & judul video
anggota:
  - nama: "???"      # 3 orang, urutan sesuai deskripsi video
  - nama: "???"
  - nama: "???"

# WAJIB — memblokir arsitektur
jumlah_citra_s1:     "???"    # hasil gee_cek_cakupan_s1.js
                              # >150 = lanjut rencana ini
                              # 80-150 = pangkas fitur model, maksimal 5 fitur
                              # <80  = STOP, ganti pendekatan (lihat 9.A)
skill_tim:
  python:            "???"    # belum pernah / pernah / lancar
  react:             "???"
  sql:               "???"
  geospasial:        "???"    # kemungkinan besar "belum pernah" — itu wajar

# ASUMSI SAYA — koreksi kalau salah
bentuk_produk:       "PWA"    # rulebook membolehkan website ATAU mobile; PWA memenuhi keduanya
bahasa_ui:           "Indonesia"
budget:              "Rp0"    # semua layanan pakai free tier
punya_domain:        false
repo_sudah_ada:      false
```

---

## 4. TECH STACK — DIKUNCI, JANGAN DIPERDEBATKAN LAGI

| Lapisan | Pilihan | Alasan dikunci |
|---|---|---|
| Bahasa backend | Python 3.11 | Ekosistem geospasial hanya ada di sini |
| Framework API | FastAPI + Uvicorn | Cepat disiapkan, dokumentasi OpenAPI otomatis (bagus untuk Code Project 10%) |
| Geospasial | OSMnx, NetworkX, GeoPandas, rasterio, Shapely, pyproj | OSMnx memangkas pembuatan graf jalan dari berhari-hari jadi satu pemanggilan |
| Model | scikit-learn — **gradient boosting** | Bukan deep learning. Data tabular, sampel terbatas, dan feature importance bisa dijelaskan ke juri |
| Citra satelit | Google Earth Engine (Python API + `geemap`) | Komputasi di server Google, laptop 8 GB cukup |
| Database | PostgreSQL + PostGIS via Supabase | Free tier, PostGIS untuk query spasial |
| Frontend | React + Vite + **MapLibre GL JS** | MapLibre open source, tanpa token yang bisa habis kuota di tengah demo |
| Styling | Tailwind CSS | Cepat, konsisten |
| Deploy API | Railway atau Render | Free tier |
| Deploy frontend | Vercel | Free tier |
| Prototype desain | **Figma — WAJIB** | Rulebook poin 7.9 mewajibkan |

**Larangan keras:**
- Jangan pakai Mapbox (butuh token, kuota bisa habis saat demo)
- Jangan pakai deep learning untuk model genangan
- Jangan pakai layanan berbayar apa pun
- Jangan memanggil Overpass API saat runtime produksi — unduh graf sekali, simpan ke file

---

## 4B. SISTEM VISUAL — DILARANG IMPROVISASI

Seluruh keputusan visual sudah ditetapkan di **`DESIGN.md`**. Baca file itu
sebelum menulis satu baris CSS atau satu komponen. Ringkasnya:

- **Arah desain:** chartplotter — badan instrumen gelap, jendela peta terang.
  Diturunkan dari papan duga air dan instrumen navigasi kapal, bukan dari tren
  antarmuka.
- **Warna:** hanya lewat CSS custom property. Dilarang menulis nilai heks di
  dalam komponen.
- **Huruf:** Barlow Semi Condensed untuk antarmuka, IBM Plex Mono untuk semua
  angka hasil pengukuran. Dilarang Inter, Geist, Poppins, Montserrat.
- **Radius:** hanya 3px dan 6px. Bayangan dilarang kecuali satu di lembar bawah.
- **Elemen tanda tangan:** Pita Pasut — penggeser waktu berbentuk kurva pasang
  surut 72 jam dengan jam berisiko genangan terarsir. Ini menggantikan pemilih
  tanggal, bukan melengkapinya.
- **Gerak:** satu animasi saja, yaitu ruas terisi dan surut 180ms saat Pita
  Pasut digeser.
- **Kedalaman tidak pernah disampaikan lewat warna saja.** Dua kelas terdalam
  wajib ditumpuk pola titik halftone, supaya tangkapan layar tetap terbaca saat
  proposal dicetak hitam putih oleh penguji.

**Teks antarmuka:** seluruhnya di `copy.id.json` — 214 string dalam 21 blok,
lengkap dengan glosarium istilah baku dan aturan suara tulisan. Diakses lewat
helper `t()`. Dilarang menulis kalimat langsung di komponen. Butuh kalimat
baru, tambahkan ke berkas itu lebih dulu.

`DESIGN.md` Bagian 12 memuat daftar tolak berisi dua belas hal. Bila salah
satunya muncul di kode, pekerjaan itu diulang.

## 5. STRUKTUR REPO

```
pasang-surut/
├── README.md                  # gerbang utama untuk juri — lihat bagian 11
├── PLAN.md                    # file ini
├── LICENSE                    # MIT
├── .env.example
├── .gitignore
│
├── data/
│   ├── aoi/
│   │   └── aoi_semarang_pilot.geojson    # SUDAH ADA — jangan ubah tanpa umumkan tim
│   ├── raw/                   # .gitignore — DEMNAS dll, jangan di-commit
│   ├── processed/             # hasil olahan kecil, boleh di-commit
│   └── referensi/
│       ├── konstanta_pasut_semarang.json  # TODO(sumber): dari jurnal
│       ├── laju_subsidensi.json           # TODO(sumber): dari jurnal
│       └── faktor_emisi.json
│
├── notebooks/                 # eksplorasi Orang A — HARUS dibersihkan sebelum submit
│   ├── 01_eksplorasi_s1.ipynb
│   ├── 02_ekstraksi_label.ipynb
│   └── 03_latih_model.ipynb
│
├── gee/
│   └── cek_cakupan_s1.js      # SUDAH ADA
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── api/
│   │   │   ├── rute.py
│   │   │   ├── genangan.py
│   │   │   └── validasi.py
│   │   ├── domain/
│   │   │   ├── graf.py        # bangun & muat graf jalan
│   │   │   ├── routing.py     # time-dependent shortest path
│   │   │   ├── pasut.py       # rekonstruksi harmonik
│   │   │   ├── genangan.py    # inference model
│   │   │   └── dampak.py      # waktu, BBM, emisi, paparan
│   │   └── schemas/           # Pydantic
│   ├── scripts/
│   │   ├── 01_bangun_graf.py
│   │   ├── 02_ekstraksi_fitur.py
│   │   ├── 03_latih_model.py
│   │   └── 04_prediksi_72jam.py
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Peta.jsx
│   │   │   ├── PemilihWaktu.jsx
│   │   │   ├── FormRute.jsx
│   │   │   ├── PanelDampak.jsx
│   │   │   └── PeringatanPaparan.jsx
│   │   ├── pages/
│   │   │   ├── Beranda.jsx
│   │   │   └── Validasi.jsx
│   │   └── lib/api.js
│   ├── public/manifest.json   # PWA
│   └── package.json
│
├── db/
│   └── schema.sql             # SUDAH ADA
│
└── docs/
    ├── arsitektur.md
    ├── metodologi.md          # bahan bagian 6 proposal
    ├── batasan.md             # bahan bagian 5 proposal — PENTING
    └── validasi.md            # angka akurasi model
```

---

## 6. LINGKUP MVP — DIBEKUKAN

### Wilayah
**Hanya Semarang Utara dan Semarang Timur**: Tanjungmas, Bandarharjo, Kemijen, Kaligawe, Terboyo Kulon, Terboyo Wetan. Batasnya ada di `data/aoi/aoi_semarang_pilot.geojson`.

Alasan: wilayah rob terparah sekaligus laju penurunan tanah tertinggi (9–13 cm/tahun). Kedalaman di satu wilayah mengalahkan kedangkalan di seluruh kota.

### Harus jalan (= definisi progres 50–75%)

- [ ] **F1** Peta wilayah pilot dengan jaringan jalan asli dari OSM
- [ ] **F2** Pemilih waktu keberangkatan, rentang 72 jam ke depan, resolusi 1 jam
- [ ] **F3** Overlay prediksi genangan per jam, berubah saat slider digeser
- [ ] **F4** Perutean A ke B yang menghindari genangan, moda motor dan mobil
- [ ] **F5** Panel dampak: tambahan waktu, jarak, BBM, CO2e vs rute terpendek
- [ ] **F6** Peringatan paparan kesehatan bila rute terpaksa menembus genangan
- [ ] **F7** Halaman validasi: perbandingan prediksi model vs genangan teramati Sentinel-1, lengkap dengan angka akurasi
- [ ] **F8** Tombol tujuan cepat (Pelabuhan Tanjung Emas, Kawasan Industri Terboyo, RS terdekat) — supaya juri bisa mencoba dalam 5 detik tanpa mengetik

### Ditunda — WAJIB ditulis di bagian Batasan Perangkat Lunak

Cakupan seluruh kota; moda transit dan pejalan kaki; laporan genangan real-time dari warga; dashboard khusus BPBD/Dishub; notifikasi push; model hidrodinamik penuh; integrasi data lalu lintas real-time; akun pengguna dan riwayat perjalanan.

---

## 7. KONTRAK DATA

Sumber kebenaran ada di `db/schema.sql`. Tabel `prediksi_genangan` adalah **kontrak antara Orang A dan Orang B**:

```
prediksi_genangan(edge_id, waktu, kedalaman_cm, probabilitas, sumber)
```

**Aturan paralelisasi:** Orang B mengisi tabel ini dengan `sumber = 'dummy'` sejak hari pertama, memakai fungsi sintetis sederhana (misalnya kedalaman naik saat pasut tinggi di ruas berelevasi rendah). Dengan begitu seluruh mesin routing, API, dan frontend bisa dibangun dan diuji **tanpa menunggu model Orang A selesai di hari ke-4**. Saat model asli siap, tinggal ganti isi tabel — nol perubahan kode.

Perubahan pada bentuk tabel ini wajib diumumkan ke seluruh tim.

---

## 8. SUMBER DATA

| Data | Sumber | Catatan kritis |
|---|---|---|
| Jaringan jalan | OpenStreetMap via OSMnx | Unduh sekali, simpan GraphML. Jangan panggil Overpass saat demo |
| Elevasi | DEMNAS (BIG), 0,27 arc-second ≈ 8 m, EGM2008 | **RMSE vertikal 2,79 m.** Dipakai sebagai FITUR model, bukan ambang genangan absolut |
| Laju penurunan tanah | Literatur terpublikasi | Jangan olah InSAR sendiri. Cantumkan sumber tiap angka |
| Pasang surut | Rekonstruksi harmonik dari konstanta terpublikasi | **Offline penuh.** Jangan bergantung API saat presentasi |
| Curah hujan | Open-Meteo (utama), BMKG (sekunder) | Open-Meteo gratis tanpa kunci dan stabil |
| Label genangan | Sentinel-1 GRD IW VV via Earth Engine | Jantung proyek |
| Titik tujuan | OSM POI | Untuk tombol tujuan cepat |
| Faktor emisi | IPCC / pedoman nasional | Pakai rentang, bukan angka tunggal |
| Baseline dampak | WRI Indonesia 2026 | Rp848 miliar/tahun — jangkar Impact Projection |

### Cara membangun dataset latih — JANGAN SALAH DI SINI

**Insting yang salah:** cari tanggal rob, ambil citra Sentinel-1 di tanggal itu, tandai genangan. Ini menghasilkan segelintir sampel karena Sentinel-1 lewat pada jam tetap sementara puncak rob hanya beberapa jam.

**Cara yang benar:** ambil **semua** citra Sentinel-1 di atas AOI sejak 2015. Untuk setiap citra, catat tinggi pasut pada detik akuisisi dan curah hujan beberapa hari sebelumnya. Setiap citra menjadi satu set sampel — sebagian saat pasut tinggi, sebagian saat rendah. Model belajar hubungan tinggi muka air terhadap genangan dari ratusan titik data.

Ini bukan trik menambah data. Ini yang membuat model bisa memprediksi pada tinggi pasut apa pun, termasuk yang belum pernah terjadi.

**Waspadai lubang arsip:** Sentinel-1B berakhir 23 Desember 2021 dan Sentinel-1C baru reguler sejak 26 Maret 2025, sehingga sebagian wilayah punya cakupan sangat sedikit pada Desember 2021–April 2025. Verifikasi dengan `gee/cek_cakupan_s1.js` sebelum apa pun dibangun.

### Kuota Earth Engine — RISIKO NYATA

Sejak 27 April 2026 proyek nonkomersial punya kuota compute bulanan yang reset tanggal 1. Hari ini 23 Agustus, deadline 31 Agustus. **Kalau kuota Agustus habis, tidak ada tambahan sebelum deadline.**

Mitigasi wajib:
- Tiap anggota tim daftarkan Cloud project sendiri (kuota per proyek, 3 orang = 3 jatah)
- Ekstraksi label pakai `scale=20` atau `30`, jangan `10`
- Ekspor tabel, jangan raster
- Pakai `.limit()` selama eksperimen

---

## 9. MILESTONE HARIAN

Setiap milestone punya kriteria terima. Jangan lanjut sebelum kriteria terpenuhi.

### M1 — Minggu 23 Agustus: fondasi
- Repo dibuat, **publik**, struktur folder sesuai bagian 5
- `schema.sql` dijalankan di Supabase
- AOI dibekukan
- Environment Python jalan di tiga laptop
- Skrip cek cakupan Sentinel-1 dijalankan, angkanya dicatat di `docs/validasi.md`

**Terima:** `git clone` + `pip install -r requirements.txt` berhasil di mesin bersih.

### M2 — Senin 24 Agustus: graf & data dummy
- `01_bangun_graf.py` menghasilkan graf jalan AOI, disimpan sebagai GraphML
- Tabel `ruas_jalan` terisi
- `prediksi_genangan` terisi data dummy 72 jam
- Frontend menampilkan peta + jaringan jalan

**Terima:** buka browser, lihat jalan Semarang Utara di peta.

### M3 — Selasa 25 Agustus: routing jalan
- Time-dependent shortest path berfungsi di atas data dummy
- Endpoint `POST /api/rute` mengembalikan geometri rute + ETA
- Frontend: pilih asal, tujuan, waktu berangkat, tampil rute

**Terima:** ubah jam keberangkatan, rutenya berubah.

### M4 — Rabu 26 Agustus: model asli
- Label genangan diekstrak dari Sentinel-1 untuk seluruh citra tersedia
- Fitur digabung (elevasi, subsidensi, jarak pantai, pasut, hujan)
- Model dilatih, **angka AUC dan F1 dicatat**
- Pasut 72 jam ke depan dihitung, prediksi masuk database menggantikan dummy

**Terima:** `sumber = 'model_v1'` di database, dan `docs/validasi.md` berisi angka akurasi asli.

### M5 — Kamis 27 Agustus: dampak + INTEGRASI, FITUR DIBEKUKAN
- Panel dampak jalan (waktu, jarak, BBM, CO2e)
- Peringatan paparan kesehatan
- Halaman validasi
- Tombol tujuan cepat
- **End-to-end berjalan malam ini**

**Terima:** dari halaman kosong sampai rute + dampak tanpa error. Kalau belum tercapai malam ini, **potong fitur, jangan tambah hari.**

### M6 — Jumat 28 Agustus: deploy & rekam
- API di Railway, frontend di Vercel, keduanya hidup dengan URL publik
- README lengkap
- Figma prototype selesai
- Rekam footage demo
- Ketiga anggota mulai menulis proposal

**Terima:** buka URL dari HP orang lain, aplikasi jalan.

### M7 — Sabtu 29 Agustus: proposal & video
- Draft 14 bagian proposal lengkap
- Video diedit, durasi 3–7 menit

### M8 — Minggu 30 Agustus: format & unggah
- Proposal diformat: A4, Times New Roman 12, spasi 1.5, margin 4-3-3-3, maksimal 30 halaman termasuk cover dan lampiran
- Nama file: `Anforcom2026_DSDC_[Nama Tim]_[Nama Karya].pdf`
- Video diunggah ke YouTube, **visibilitas publik**
- Repo dirapikan, notebook dibersihkan

### M9 — Senin 31 Agustus: SUBMIT SIANG HARI
Unggah ke app.anforcom.com. **Jangan submit jam 23.00.**

### 9.A — Rencana darurat kalau citra Sentinel-1 kurang dari 80

Jangan panik dan jangan memaksakan model. Ganti pendekatan jadi **model susceptibility berbasis aturan yang dikalibrasi terhadap sedikit kejadian teramati**: skor kerentanan per ruas dari elevasi relatif, jarak ke pantai, dan laju subsidensi, dengan ambang yang di-fit ke kejadian yang ada. Turunkan klaim dari "prediksi" jadi "indeks kerentanan", dan **katakan terus terang di proposal**. Kejujuran ini bernilai di kriteria realistis dan tidak overclaim.

---

## 10. SPESIFIKASI MODUL

### 10.1 Graf jalan (`domain/graf.py`)
Bangun graf berarah dari OSM lewat OSMnx, batasi ke AOI, tipe `drive`. Simpan GraphML ke `data/processed/`. Isi kolom fitur di `ruas_jalan` (elevasi dari sampling DEMNAS di titik tengah ruas, jarak ke garis pantai, laju subsidensi dari raster interpolasi). Muat sekali saat startup API, simpan di memori.

### 10.2 Pasut (`domain/pasut.py`)
Rekonstruksi harmonik: tinggi muka air sebagai jumlah kosinus dari komponen M2, S2, N2, K2, K1, O1, P1 dengan amplitudo dan fase dari `data/referensi/konstanta_pasut_semarang.json`. Sepenuhnya offline. Sediakan fungsi `tinggi_pasut(waktu) -> float` dan `deret_pasut(mulai, selesai, langkah_jam) -> DataFrame`. Validasi terhadap tide table terbitan, catat selisihnya di `docs/validasi.md`.

### 10.3 Model genangan (`scripts/03_latih_model.py`)
Fitur: elevasi, laju subsidensi, jarak pantai, jarak sungai, tinggi pasut saat akuisisi, hujan 24 jam, hujan 72 jam. Target: biner basah/kering dari Sentinel-1. Model: `GradientBoostingClassifier` atau `HistGradientBoostingClassifier`.

**Wajib:** pisah train/test **berdasarkan waktu**, bukan acak — kalau acak, citra yang sama bocor ke dua sisi dan akurasinya palsu. Laporkan AUC, F1, dan confusion matrix. Simpan feature importance sebagai gambar untuk proposal dan slide.

Konversi probabilitas ke `kedalaman_cm` dengan fungsi monotonik sederhana yang dikalibrasi terhadap tinggi pasut. **Dokumentasikan fungsi ini sebagai asumsi di `docs/batasan.md`** — ini titik terlemah metodologi dan harus kamu akui sendiri sebelum juri menemukannya.

### 10.4 Routing (`domain/routing.py`)
Time-dependent Dijkstra pada graf. Bobot ruas = waktu tempuh dasar × penalti(kedalaman, moda), dengan waktu tiba di tiap ruas dihitung berjalan. Ambang per moda ada di tabel `ambang_moda`. Kedalaman di atas `tidak_bisa_lewat_cm` berarti ruas dibuang dari graf untuk moda itu.

Hitung dua rute: **rute terpendek biasa** (mengabaikan genangan) dan **rute sadar rob**. Selisih keduanya adalah angka dampak.

### 10.5 Dampak (`domain/dampak.py`)
Δwaktu, Δjarak, ΔBBM (`konsumsi_l_per_km`), ΔCO2e (`faktor_emisi_kg_per_l`). **Tampilkan sebagai rentang, bukan angka tunggal.** Bila rute sadar rob tetap melewati ruas dengan kedalaman di atas `berisiko_cm`, keluarkan peringatan paparan yang menyebut risiko kesehatan air genangan dan menyarankan menunda keberangkatan ke jam dengan prediksi lebih rendah.

### 10.6 API
```
GET  /api/kesehatan
GET  /api/genangan?waktu=ISO8601          -> GeoJSON ruas + kedalaman
POST /api/rute                            -> {asal, tujuan, waktu, moda}
GET  /api/tujuan-cepat                    -> daftar POI penting
GET  /api/validasi                        -> metrik model + contoh kejadian
```

### 10.7 Frontend
Peta MapLibre memenuhi layar, slider waktu di bawah, form rute di panel kiri, hasil dampak di panel kanan. Warna genangan pakai skala yang tetap terbaca dari jarak 2 meter — **ini dirancang untuk babak pameran yang berbobot 15%.**

---

## 11. README.md — INI GERBANG JURI

Juri menilai Code Project 10% dan sebagian besar hanya akan membaca README. Wajib memuat:

1. Nama karya, tim, anggota
2. Satu paragraf masalah + angka Rp848 miliar
3. Tautan aplikasi live, video YouTube, Figma
4. Screenshot atau GIF alur utama
5. Arsitektur (diagram + penjelasan singkat)
6. **Sumber data lengkap dengan tautan**
7. **Angka validasi model — apa adanya, termasuk kalau jelek**
8. Cara menjalankan lokal, langkah demi langkah
9. **Batasan yang diketahui** — salin dari `docs/batasan.md`
10. Roadmap fitur yang ditunda

---

## 12. CHECKLIST KEPATUHAN RULEBOOK

Verifikasi satu per satu sebelum submit.

**Proposal**
- [ ] Sistematika persis 14 bagian: Judul Karya, Abstrak, Latar Belakang Masalah, Tujuan dan Manfaat, Batasan Perangkat Lunak, Metodologi Pengembangan, Analisis Kebutuhan dan Desain Solusi, Arsitektur Sistem dan Spesifikasi Tools/Teknologi, Implementasi Perangkat Lunak, Mockup/Tangkapan Layar, Impact Projection, Penutup, Daftar Pustaka, Lampiran
- [ ] A4, Times New Roman 12, spasi 1.5, margin 4-3-3-3
- [ ] Maksimal 30 halaman termasuk cover dan lampiran
- [ ] Nama file `Anforcom2026_DSDC_[Nama Tim]_[Nama Karya].pdf`
- [ ] Lampiran memuat tautan video demo dan repository GitHub
- [ ] Ide orisinil, tidak menjiplak desain yang sudah ada
- [ ] Tidak mengandung unsur SARA, kekerasan, pornografi
- [ ] Karya belum pernah memenangkan penghargaan di lomba manapun

**Video**
- [ ] Resolusi minimal 1280 x 720
- [ ] Durasi 3–7 menit
- [ ] Berisi demo aplikasi mencakup alur fitur-fitur utama
- [ ] **Peserta tampil dari awal hingga akhir video**
- [ ] Judul YouTube `Anforcom2026_DSDC_[Nama Tim]_[Nama Karya]`
- [ ] Deskripsi format rulebook: `Anforcom 2026` / `[Nama Tim] - [Deskripsi karya]` / daftar nama anggota
- [ ] Tag `#Anforcom2026`
- [ ] **Visibilitas publik**

**Teknis & administratif**
- [ ] Repo GitHub publik atau juri diberi akses
- [ ] Source code mencerminkan progres 50–75%
- [ ] Tautan website atau build aplikasi hidup
- [ ] **Prototype dibuat dengan Figma** (poin 7.9)
- [ ] Twibbon diunggah ke Instagram masing-masing anggota, tag @anforcom
- [ ] Poster diunggah ke Instagram masing-masing anggota, tag @anforcom
- [ ] Diunggah lewat app.anforcom.com pakai akun tim terdaftar

---

## 12B. KEPATUHAN VISUAL

Diperiksa sebelum M6 dinyatakan selesai:

- [ ] Setiap warna, ukuran huruf, radius, dan jarak berasal dari `DESIGN.md`
- [ ] Tidak ada nilai heks yang ditulis langsung di komponen
- [ ] Barlow Semi Condensed dan IBM Plex Mono termuat, bukan huruf bawaan sistem
- [ ] Pita Pasut terpasang dan dapat dioperasikan lewat papan ketik
- [ ] Kedalaman tampil lewat warna sekaligus pola, bukan warna saja
- [ ] Tidak ada komponen shadcn atau Material bawaan yang belum disesuaikan token
- [ ] Tidak ada emoji sebagai ikon antarmuka
- [ ] Peta adalah konten penuh layar, bukan latar di belakang kisi kartu
- [ ] Lantai mutu di `DESIGN.md` Bagian 11 terpenuhi seluruhnya
- [ ] Tidak ada kalimat berbahasa Indonesia yang ditulis langsung di komponen
- [ ] Helper `t()` melempar error saat kunci atau placeholder tidak ditemukan
- [ ] Istilah mengikuti glosarium `copy.id.json`

## 13. ANTI-PATTERN — JANGAN LAKUKAN

1. **Menaruh angka dampak tanpa sumber.** Setiap angka di UI dan proposal harus bisa ditelusuri.
2. **Mengklaim akurasi tanpa split berbasis waktu.** Akurasi 99% dari split acak adalah kebohongan yang akan ketahuan.
3. **Menyembunyikan batasan.** Juri yang menemukan batasan yang sudah kamu tulis sendiri menilai kamu jujur. Yang menemukan batasan tersembunyi menilai kamu overclaim.
4. **Bergantung pada API eksternal saat demo.** Semua yang bisa di-precompute harus di-precompute dan disimpan.
5. **Menambah fitur setelah M5.** Fitur beku artinya beku.
6. **Meninggalkan notebook berantakan di repo.** Code Project 10%.
7. **Meng-commit file DEMNAS mentah.** Repo membengkak, clone gagal.
8. **Menunda video sampai H-1.** Video 10% dan wajib menampilkan wajah peserta — butuh waktu rekam ulang.
9. **Memaksakan narasi Circular Economy.** Rulebook membolehkan salah satu saja.
10. **Submit jam 23.00 tanggal 31.** Submit siang.

---

## 14. FILE PENDAMPING

| File | Fungsi |
|---|---|
| `aoi_semarang_pilot.geojson` | AOI wilayah pilot, taruh di `data/aoi/` |
| `schema.sql` | Skema database, jalankan di Supabase SQL Editor, taruh di `db/` |
| `gee_cek_cakupan_s1.js` | Cek arsip Sentinel-1, tempel di code.earthengine.google.com, taruh di `gee/` |
| `CHECKLIST_MALAM_INI.md` | Checklist pendaftaran akun dan tautan |

---

## 15. LANGKAH PERTAMA UNTUK CLAUDE CODE

1. Baca seluruh file ini
2. **Minta user mengisi blok asumsi di bagian 3.** Jangan lanjut sebelum terisi
3. Bila `jumlah_citra_s1` kurang dari 80, hentikan dan diskusikan rencana 9.A
4. Buat struktur repo bagian 5
5. Siapkan environment, verifikasi di mesin bersih
6. Mulai M1
