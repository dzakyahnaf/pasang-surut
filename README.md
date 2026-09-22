# PASANG SURUT

[![Uji](https://github.com/dzakyahnaf/pasang-surut/actions/workflows/uji.yml/badge.svg)](https://github.com/dzakyahnaf/pasang-surut/actions/workflows/uji.yml)

**Perutean sadar rob untuk Semarang.**

Pembaruan 22 September: retry, cakupan data, kinerja/memori, dan model routing
sudah diperbaiki. API, frontend, serta database sudah diuji pada VPS privat;
alamat publik masih memakai deployment sebelumnya. Baca
[hasil migrasi, pengukuran, dan langkah publik yang tertahan](docs/final/migrasi_vps_22_september.md).

Memprediksi **kapan** tiap ruas jalan berisiko tergenang rob untuk 72 jam ke
depan, lalu merutekan warga dan logistik menghindarinya pada jam keberangkatan
mereka — bukan pada kondisi saat ini.

| | |
|---|---|
| **Tim** | trio la albiceleste |
| **Institusi** | Institut Teknologi Sepuluh Nopember (ITS), Surabaya |
| **Lomba** | Diponegoro Software Development Competition — ANFORCOM 2026 |
| **Subtema** | 4 — Smart Low-Carbon Urban Mobility |

**Anggota**

| Nama | NRP |
|---|---|
| Muhammad Dzaky Ahnaf | 5027231039 |
| Daffa Rajendra Priyatama | 5027231009 |
| Naufal Syafi' Hakim | 5027231022 |

---

## 1. Masalah

Riset World Resources Institute Indonesia (April 2026) menemukan sekitar 10
persen jaringan jalan Semarang — setara 11 persen aktivitas mobilitas kota —
berpotensi terdampak banjir rob, dengan total kerugian akibat gangguan
transportasi sekitar **Rp848 miliar per tahun**. WRI menyatakan pendekatan
berbasis infrastruktur fisik saja belum cukup dan diperlukan pergeseran ke
perencanaan transportasi yang lebih adaptif.

Tanggul tidak akan selesai sebelum besok pagi, sementara warga tetap harus
berangkat kerja. PASANG SURUT menjawab celah waktu itu: bukan mencegah robnya,
melainkan membuat orang tahu jalan mana yang berisiko pada jam mereka
berangkat.

---

## 2. Tautan

| | |
|---|---|
| Aplikasi live | https://pasang-surut.vercel.app |
| API | https://pasang-surut-api.onrender.com |
| Video YouTube | https://youtu.be/CeXsEN_1Zvk |
| Prototype Figma | https://www.figma.com/design/EtACxc7jD6wvMJjHh7bq3p/PasangSurut?node-id=1-907 |
| Repositori | https://github.com/dzakyahnaf/pasang-surut |

---

## 3. Apa yang benar-benar dilakukan sistem ini

Ini bagian yang paling penting dibaca, karena judul "berbasis Sentinel-1"
pernah benar lalu berhenti benar, dan kami mengubahnya.

**Komponen waktu — tervalidasi.** Kapan tiap ruas berisiko ditentukan
rekonstruksi harmonik pasang surut dari konstanta terpublikasi. Rekonstruksi
itu diuji terhadap muka air **terukur** stasiun pasut Badan Informasi
Geospasial: korelasi **0,78–0,91**, RMSE **0,10–0,12 m**. Diuji silang lagi
secara independen terhadap 16 kejadian rob terdokumentasi, dan menempatkan
hari kejadian pada median persentil **80,2** dari 50 yang diharapkan bila
tidak berhubungan.

**Komponen ruang — indeks berbasis aturan, TANPA angka akurasi.** Ruas mana
yang lebih rentan ditentukan indeks dari tiga besaran fisik berbobot sama
rata: elevasi relatif terhadap median lingkungan 3 × 3 sel grid (sisi sel
500 m), jarak ke garis pantai,
dan laju penurunan muka tanah. Indeks ini **tidak punya akurasi yang bisa
dilaporkan**, dan tidak akan punya sampai ada pengamatan genangan per ruas.

**Model Sentinel-1 — dilatih, lalu ditolak sendiri.** Lihat bagian 6.

### Bukti visual

![Sebaran tinggi pasut pada 725 waktu akuisisi Sentinel-1, dibandingkan
sebaran pada seluruh jam](docs/pasut_saat_akuisisi.png)

*Jam lintasan tetap Sentinel-1 justru menguntungkan pemantauan rob. Persentil
ke-95 pasut saat akuisisi +0,338 m berbanding +0,302 m pada seluruh jam —
arsipnya memuat lebih banyak pengamatan pasang tinggi daripada pencuplikan
acak. Yang tidak terwakili justru surut terdalam.*

![Kepentingan permutasi enam fitur model Sentinel-1 yang
ditolak](docs/kepentingan_fitur.png)

*Merah adalah ketiga fitur yang bergantung waktu. Ketiganya nol dalam batas
ketidakpastiannya — model ini mempelajari ruas mana yang sering beranomali,
bukan kapan ruas tergenang. Itulah alasan model ditolak.*

---

## 4. Arsitektur

```
                 SEKALI, DI LAPTOP                    SAAT MELAYANI
    ┌──────────────────────────────────────┐    ┌──────────────────────┐
    │  OpenStreetMap ──► graf jalan        │    │                      │
    │  DEMNAS ──────────► elevasi          │    │   FastAPI            │
    │  Literatur ───────► subsidensi       │    │     │                │
    │  Open-Meteo ──────► hujan            │    │     ├─ Dijkstra      │
    │  Sentinel-1 ──────► label (DITOLAK)  │    │     │  sadar waktu   │
    │  Konstanta pasut ─► rekonstruksi     │    │     │                │
    │             │                        │    │     └─ indeks +      │
    │             ▼                        │    │        pasut         │
    │      PostGIS / Supabase ─────────────┼───►│          │           │
    │             │                        │    │          ▼           │
    │             └──► potret_demo.json ───┼───►│   React + MapLibre   │
    └──────────────────────────────────────┘    └──────────────────────┘
        tidak pernah dipanggil saat melayani      NOL panggilan keluar
```

**Nol ketergantungan jaringan saat melayani.** Diaudit dan ditegakkan tiga
lapis:

1. `backend/app/` tidak mengimpor satu pun pustaka jaringan. Yang ada hanya
   `fastapi`, `pydantic`, `psycopg2`, `numpy`, `dotenv`.
2. Gaya peta MapLibre ditulis **inline** — tanpa URL ubin, glyph, atau
   sprite. Tidak ada permintaan ke server peta mana pun.
3. Citra Docker **tidak memasang** `earthengine-api`, `osmnx`, `geopandas`,
   `rasterio`, `scikit-learn`, maupun `pandas`. Kode yang keliru memanggilnya
   akan gagal saat start, bukan diam-diam saat juri memakainya.

**Tahan banting.** `backend/scripts/18_seed_demo.py` membekukan potret 72 jam
ke `data/processed/potret_demo.json`. Bila database tidak terjangkau, seluruh
tujuh endpoint tetap melayani dari potret — termasuk **perutean, yang tetap
menghitung sungguhan**, bukan mengembalikan rute yang sudah disiapkan.
Terukur: 7/7 endpoint hidup dengan `DATABASE_URL` sengaja dirusak, dan
peruteannya justru lebih cepat (0,07 s berbanding 1,3 s lewat Supabase).

Potret membawa `berlaku_sampai` dan **ditolak setelah kedaluwarsa**. Untuk
sistem yang menyarankan kapan orang boleh menembus air, prediksi basi lebih
berbahaya daripada layar kosong.

Versi terbaru menyimpan metadata jam lengkap, termasuk jam kering. Waktu
tanpa cakupan tidak menghasilkan rute. Frontend mengunduh geometri statis
sekali lalu mengambil kondisi ringkas ketika pilihan jam berubah. Pengukuran
lama di atas adalah riwayat; hasil lokal terbaru ada pada laporan 21 September.

Routing memakai kondisi jam keberangkatan tetap sepanjang satu pencarian;
perubahan kondisi di tengah perjalanan belum dimodelkan. Mengganti pilihan
jam menghitung ulang rute. Evaluasi akurasi pasut bukan validasi genangan
per ruas.

### Tech stack

| Lapisan | Pilihan | Alasan singkat |
|---|---|---|
| API | FastAPI + Uvicorn | dokumentasi OpenAPI otomatis, tipe terperiksa |
| Database | PostgreSQL + PostGIS (Supabase) | kueri spasial tanpa ORM |
| Perutean | Dijkstra dengan kondisi jam keberangkatan | biaya tetap selama satu pencarian; dihitung ulang saat pilihan jam berubah |
| Frontend | React + Vite + MapLibre GL JS | MapLibre bebas token, bisa gaya inline |
| Gaya | CSS custom property | tiap warna dari `DESIGN.md`, nol heks di komponen |
| Model | HistGradientBoostingClassifier | dilatih lalu ditolak, lihat bagian 6 |

---

## 5. Sumber data

| Data | Sumber | Tautan | Catatan |
|---|---|---|---|
| Jaringan jalan | OpenStreetMap via OSMnx | [openstreetmap.org](https://www.openstreetmap.org) | ODbL. 19.394 ruas, 1.289 km |
| Elevasi | DEMNAS, Badan Informasi Geospasial | [tanahair.indonesia.go.id](https://tanahair.indonesia.go.id/portal-web/unduh/demnas) | tile 1409-22. **RMSE vertikal 2,79 m** |
| Garis pantai | OpenStreetMap `natural=coastline` | — | 21 garis, diambil sekali |
| Penurunan muka tanah | Rahmawati, Prasetyo & Sasmito (2020) | [ejournal3.undip.ac.id](https://ejournal3.undip.ac.id/index.php/geodesi/article/viewFile/26032/23173) | *Jurnal Geodesi Undip* 9(1):29–36, SBAS Sentinel-1A |
| Konstanta pasut | Rachman, Ismunarti & Handoyo (2015) | [ejournal3.undip.ac.id](https://ejournal3.undip.ac.id/index.php/joce/article/download/7646/7406) | *Jurnal Oseanografi* 4(1):1–9, Admiralty 15 hari |
| Muka air terukur | Stasiun IOC `sema` (BIG + GFZ) | [ioc-sealevelmonitoring.org](https://www.ioc-sealevelmonitoring.org/station.php?code=sema) | dipakai memvalidasi rekonstruksi |
| Curah hujan | Open-Meteo Archive (ERA5) | [open-meteo.com](https://open-meteo.com) | 102.552 jam, 2015–2026 |
| Citra radar | Sentinel-1 GRD IW VV via Earth Engine | [developers.google.com](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD) | 725 citra, 2015–2026 |
| Baseline dampak | WRI Indonesia, April 2026 | `[ ISI tautan ]` | Rp848 miliar/tahun |
| Faktor emisi | belum bersitasi | — | `faktor_emisi.json` masih `null` |

---

## 6. Validasi — angka apa adanya, termasuk yang jelek

### 6.1 Model Sentinel-1: DILATIH, LALU DITOLAK

725 citra ditarik seluruhnya, 2.502 ruas berstrata, **1.813.950 nilai
backscatter**. Pemisahan berdasarkan **waktu**, tidak pernah acak: latih
2015–2023 (1.366.092 baris), uji 2024–2026 (447.858 baris).

| Metrik | Nilai |
|---|---:|
| ROC-AUC | 0,6579 |
| PR-AUC | 0,0371 (proporsi dasar 0,0160) |
| F1 | 0,0894 pada ambang 0,665 |
| Skor Brier | 0,1942 |

Matriks konfusi: TN 422.350 · FP 18.352 · FN 5.962 · TP 1.194.

**Kenapa ditolak.** Kepentingan permutasi pada data uji:

| Fitur | Penurunan ROC-AUC |
|---|---:|
| Jarak ke pantai | +0,1417 ± 0,0039 |
| Elevasi DEMNAS | +0,0619 ± 0,0016 |
| Laju subsidensi | +0,0342 ± 0,0014 |
| **Tinggi pasut saat akuisisi** | **+0,0010 ± 0,0014** |
| **Hujan 24 jam** | **+0,0004 ± 0,0010** |
| **Hujan 72 jam** | **−0,0026 ± 0,0011** |

Ketiga fitur yang bergantung waktu **nol dalam batas ketidakpastiannya**.
Model ini mempelajari ruas mana yang sering beranomali, bukan **kapan** ruas
tergenang — dan seluruh guna sistem perutean terletak pada kata "kapan".
Aturan "pasut saja" menghasilkan ROC-AUC 0,4935, setara lemparan koin.

### 6.2 Lima upaya penyelamatan, semuanya gagal

| Upaya | Hasil |
|---|---|
| Cuplik radius 100 m, bukan piksel titik | ROC-AUC **0,5982** pada ambang setara — lebih buruk |
| Kriteria dua arah (pantulan ganda kota) | arah benar, besarnya hanya **0,47σ** pada 12 citra |
| Luas air kawasan terbuka | korelasi terhadap pasut **negatif** (tambak paling halus saat surut) |
| Muka air **terukur**, bukan astronomis | mentah −0,29, **semu** — tinggal +0,05 setelah layangan diluruskan |
| Topeng air permanen, lalu label per ruas | mentah **+0,362**, tersisa **+0,107** setelah musim dikendalikan |

Dua upaya terakhir sempat tampak berhasil, dan keduanya runtuh saat diperiksa.

Upaya keempat memberi −0,29, sepuluh kali lebih kuat. Ia semu: kriteria "turun"
dan "naik" berkorelasi hampir sama besar dengan tanda berlawanan (khas
pergeseran radiometrik seluruh citra, bukan genangan per ruas), dan rekaman
stasiun **melayang naik 0,92 m dalam sepuluh tahun**.

Upaya kelima bertahan paling lama. Setelah tubuh air tetap ditopengkan, luas
**daratan** yang tampak berair berkorelasi **+0,362** terhadap pasut pada orbit
76 — positif, arah yang benar secara fisika. Dua keberatan lalu diuji, bukan
diasumsikan:

| Keberatan | Uji | Hasil |
|---|---|---|
| Yang diukur luas kawasan, sistem merutekan per ruas | 487.890 cuplikan atas 2.502 ruas | +0,362 → **+0,230** |
| Sinkron matahari: K1 dan P1 bergeser fase berperiode setahun, bisa rancu dengan musim hujan | regresi hari-dalam-tahun dari kedua deret | +0,230 → **+0,107** |

Musim ternyata menjelaskan **38,6 persen ragam pasut** pada waktu akuisisi.
Dan bukti yang sepenuhnya bebas — tanggal kejadian rob terdokumentasi —
**berlawanan arah**: label basah justru lebih jarang muncul pada hari kejadian
(−0,77σ). Korelasi +0,11 dengan bukti kejadian yang berlawanan bukan dasar
untuk melabeli 19.394 ruas.

### 6.3 Rekonstruksi pasut: INI yang tervalidasi

Acuan waktu fase konstanta tidak disebutkan sumbernya, jadi seluruh offset
−12 sampai +12 jam disisir terhadap muka air terukur:

| Jendela | Fase = UTC | Fase = WIB |
|---|---:|---:|
| 2 hari | −0,289 | **+0,907** |
| 4 hari | −0,362 | **+0,909** |
| 7 hari | −0,427 | **+0,858** |
| 10 hari | −0,465 | **+0,782** |

Memakai UTC bukan sekadar kurang tepat, melainkan **berkebalikan**.

### 6.4 Yang TIDAK kami klaim

- Indeks kerentanan tidak punya angka akurasi
- Kedalaman sentimeter adalah **estimasi turunan**, bukan pengukuran
- Perbandingan visual prediksi versus genangan teramati tidak dibuat, karena
  tidak ada pengamatan genangan per ruas untuk dijadikan pembanding

Rincian lengkap: [`docs/validasi.md`](docs/validasi.md).

---

## 7. Menjalankan secara lokal

### Prasyarat

Python 3.11, Node 20+, dan PostgreSQL + PostGIS (Docker atau Supabase).

### Langkah

```bash
git clone https://github.com/dzakyahnaf/pasang-surut
cd pasang-surut

python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
source .venv/bin/activate          # Linux dan macOS
pip install -r requirements.txt

cp .env.example .env               # lalu isi DATABASE_URL
```

Periksa sambungan database sebelum apa pun dijalankan — skrip ini menemukan
kesalahan URL yang paling sering terjadi tanpa pernah mencetak kata sandi:

```bash
cd backend
python -m scripts.13_periksa_database              # memeriksa
python -m scripts.13_periksa_database --perbaiki   # persen-encode sandi
python -m scripts.13_periksa_database --pasang-skema
```

### Pipeline data, berurutan, dari `backend/`

```bash
python -m scripts.01_bangun_graf        # SEKALI saja, menyentuh Overpass
python -m scripts.02_isi_ruas_jalan     # graf -> tabel ruas_jalan
python -m scripts.05_isi_fitur_ruas     # elevasi, jarak pantai, subsidensi
python -m scripts.06_isi_pemicu         # hujan Open-Meteo + pasut
python -m scripts.06_isi_pemicu --prakiraan   # 16 hari ke depan
python -m scripts.11_indeks_kerentanan  # indeks -> prediksi_genangan
python -m scripts.17_tujuan_cepat       # POI dari OSM, sekali
python -m scripts.18_seed_demo          # potret tahan banting
```

### Skrip verifikasi — boleh dijalankan kapan saja

```bash
python -m scripts.04_kalibrasi_pasut    # acuan fase vs data terukur IOC
python -m scripts.07_uji_silang_rob     # pasut vs tanggal kejadian rob
python -m scripts.12_uji_isyarat_s1     # apakah S1 melihat pasut sama sekali
python -m scripts.14_uji_dua_arah       # kriteria label, tanpa kuota GEE
python -m scripts.16_muka_air_terukur   # label vs muka air terukur
```

### Menjalankan

```bash
cd backend && uvicorn app.main:app --reload   # API di :8000
cd backend && DATABASE_URL= uvicorn app.main:app   # tanpa database, dari potret
cd frontend && npm install && npm run dev     # UI di :5173
pytest -q                                     # 43 uji, dari akar repo
```

Baris kedua menjalankan API sepenuhnya dari `data/processed/potret_demo.json`,
tanpa database dan tanpa internet, selama potretnya masih berlaku.

### Deploy

```bash
docker build -f backend/Dockerfile -t pasang-surut-api .
docker run -p 8000:8000 -e DATABASE_URL=... -e ASAL_DIIZINKAN=... pasang-surut-api
```

Render membaca [`render.yaml`](render.yaml) sebagai blueprint. Vercel membaca
[`frontend/vercel.json`](frontend/vercel.json). Dua variabel wajib diisi di
dasbor masing-masing: `DATABASE_URL` dan `ASAL_DIIZINKAN` di sisi API,
`VITE_API_URL` di sisi frontend.

### Otomasi GitHub Actions

- [`uji.yml`](.github/workflows/uji.yml) menjalankan `pytest -q` pada setiap
  push dan pull request, di mesin bersih tanpa `.env` dan tanpa database.
- [`jaga_hidup.yml`](.github/workflows/jaga_hidup.yml) memeriksa
  `/api/kesehatan`, terjadwal tiap 10 menit atau dipicu manual. Ia gagal bila
  API tidak menjawab atau basis data tidak terjangkau, dan memberi peringatan
  bila prediksi tinggal kurang dari 72 jam atau potret cadangan sudah basi.
  Jadwal GitHub Actions tidak dijamin tepat waktu, jadi workflow ini adalah
  alarm, bukan penjaga agar Render tetap bangun.

---

## 8. Batasan yang diketahui

Ringkasan. Daftar penuh di [`docs/batasan.md`](docs/batasan.md).

1. **Kedalaman adalah estimasi turunan.** Sentinel-1 hanya memberi label
   basah atau kering. Angka sentimeter lahir dari fungsi monotonik yang
   dibatasi 10–50 cm — batas itu sendiri asumsi.
2. **Indeks kerentanan tanpa akurasi.** Bobot sepertiga tiap komponen adalah
   keputusan sadar, bukan hasil penyetelan terhadap data.
3. **DEMNAS RMSE 2,79 m** jauh lebih besar daripada rob 10–50 cm. Karena itu
   dipakai elevasi **relatif** terhadap median 3 × 3 sel grid bersisi 500 m, yang
   meniadakan galat berkorelasi spasial: simpangan baku turun 5,86 → 2,99 m.
4. **Hujan dari reanalisis satu titik** untuk seluruh AOI 13×8 km. Hujan
   konvektif setempat tidak tertangkap.
5. **Subsidensi per kecamatan, periode 2015–2018.** Memakainya untuk 2026
   adalah ekstrapolasi delapan tahun.
6. **Konsumsi bahan bakar belum bersitasi**, dan angkanya kini tampil di
   antarmuka lewat panel dampak.
7. **Bukan peringatan dini resmi.** Untuk keputusan evakuasi, ikuti BPBD.
8. **Hanya wilayah pilot**, bukan seluruh Kota Semarang.

---

## 9. Roadmap — ditunda dari MVP

- Perbandingan visual prediksi versus genangan teramati. **Dipotong di M5
  karena bahannya tidak ada**, bukan karena kehabisan waktu — tidak ada
  pengamatan genangan per ruas untuk dijadikan pembanding
- Ground truth per ruas dari BPBD atau laporan warga
- Cakupan seluruh kota, moda angkutan umum dan pejalan kaki
- Model hidrodinamik dan integrasi lalu lintas waktu nyata
- Koreksi nodal 18,6 tahun pada rekonstruksi pasut
- Prakiraan gelombang badai, supaya komponen non-astronomis ikut diprediksi

---

## Struktur repo

```
backend/app/          lapisan API dan domain — TIDAK ada pustaka jaringan
backend/scripts/      pipeline data dan verifikasi, 01 sampai 18
backend/tests/        43 uji
frontend/src/         React, MapLibre, seluruh teks lewat t()
data/aoi/             batas wilayah pilot
data/processed/       potret demo, jaringan jalan, indeks, tujuan cepat
data/referensi/       konstanta pasut, metrik model, hasil tiap uji
db/schema.sql         5 tabel, kontrak antar anggota tim
docs/                 validasi, batasan, progres, naskah demo
copy.id.json          SELURUH teks antarmuka
DESIGN.md             sistem visual, dikunci
```

---

## Lisensi

Kode di bawah [LICENSE](LICENSE). Data OpenStreetMap di bawah ODbL,
© kontributor OpenStreetMap. DEMNAS © Badan Informasi Geospasial.
