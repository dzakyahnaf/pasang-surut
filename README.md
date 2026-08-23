# PASANG SURUT

**Perutean sadar rob untuk Semarang.**

Memprediksi genangan rob di jaringan jalan sampai 72 jam ke depan, lalu
merutekan warga dan logistik menghindari ruas yang akan tergenang pada jam
keberangkatan mereka.

| | |
|---|---|
| **Tim** | trio la albiceleste |
| **Institusi** | Institut Teknologi Sepuluh Nopember (ITS), Surabaya |
| **Lomba** | Diponegoro Software Development Competition — ANFORCOM 2026 |
| **Subtema** | 4 — Smart Low-Carbon Urban Mobility |
| **Status** | Dalam pengerjaan. Lihat [Status pengerjaan](#status-pengerjaan) |

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
perencanaan transportasi yang lebih adaptif. Tanggul tidak akan selesai
sebelum besok pagi, sementara warga tetap harus berangkat kerja. PASANG SURUT
menjawab celah waktu itu: bukan mencegah robnya, melainkan membuat orang tahu
jalan mana yang akan tergenang pada jam mereka berangkat.

**Pembeda teknis.** Model genangan dikalibrasi dari genangan yang benar-benar
teramati lewat citra radar Sentinel-1, bukan dari model bathtub berbasis
ambang elevasi. Ini penting karena DEMNAS punya RMSE vertikal 2,79 m
sementara rob yang dimodelkan setinggi 10 sampai 50 cm — membandingkan
elevasi absolut terhadap tinggi muka air pada selisih sebesar itu secara
statistik tidak sah. DEM tetap dipakai, tetapi sebagai fitur model, tidak
pernah sebagai ambang.

---

## 2. Tautan

| | |
|---|---|
| Aplikasi live | Belum tersedia |
| Video YouTube | Belum tersedia |
| Prototype Figma | Belum tersedia |
| Repositori | Belum tersedia |

---

## 3. Tangkapan layar

Belum tersedia. Antarmuka belum dibangun.

---

## 4. Arsitektur

```
Sentinel-1 GRD ──┐
DEMNAS           ├──> ekstraksi fitur ──> gradient boosting ──┐
pasut harmonik   │                                            │
curah hujan    ──┘                                            v
                                                    prediksi_genangan
                                                    (edge_id, waktu,
                                                     kedalaman_cm,
                                                     probabilitas, sumber)
                                                              │
OpenStreetMap ──> OSMnx ──> graf jalan (GraphML) ──┐          │
                                                    v          v
                                          routing sadar waktu (NetworkX)
                                                              │
                                                              v
                                       FastAPI ──> React + MapLibre GL JS
```

Rincian ada di [`docs/arsitektur.md`](docs/arsitektur.md) — belum diisi.

**Catatan desain yang menentukan bentuk sistem:** jalur demo harus jalan
penuh offline. Tidak ada panggilan API eksternal saat runtime. Graf jalan
diunduh sekali lalu disimpan ke file, pasut dihitung sekali lalu disimpan.
Juri babak final memakai aplikasi ini langsung sebagai pengguna, jadi tidak
boleh ada dependensi jaringan yang bisa gagal di tengah demo.

### Tech stack

| Lapisan | Pilihan |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Geospasial | OSMnx, NetworkX, GeoPandas, rasterio, Shapely, pyproj |
| Model | scikit-learn — gradient boosting |
| Citra satelit | Sentinel-1 GRD IW VV via Google Earth Engine |
| Database | PostgreSQL + PostGIS (Supabase) |
| Frontend | React, Vite, MapLibre GL JS, Tailwind CSS |

---

## 5. Sumber data

| Data | Sumber | Tautan | Catatan |
|---|---|---|---|
| Jaringan jalan | OpenStreetMap via OSMnx | <https://www.openstreetmap.org> | Diunduh sekali, disimpan GraphML. Overpass tidak dipanggil saat runtime |
| Label genangan | Sentinel-1 GRD IW VV, Google Earth Engine | <https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD> | Jantung proyek. Hanya memberi label basah atau kering |
| Elevasi | DEMNAS, Badan Informasi Geospasial | TODO(verifikasi tautan) | 0,27 arc-second sekitar 8 m, datum EGM2008. RMSE vertikal 2,79 m. Dipakai sebagai fitur, bukan ambang |
| Curah hujan | Open-Meteo | <https://open-meteo.com> | Gratis tanpa kunci API |
| Curah hujan sekunder | BMKG | <https://www.bmkg.go.id> | Pembanding |
| Pasang surut | Rekonstruksi harmonik dari konstanta terpublikasi | TODO(sumber) | Offline penuh. Konstanta belum diisi, lihat `data/referensi/konstanta_pasut_semarang.json` |
| Laju penurunan tanah | Literatur terpublikasi | TODO(sumber) | Belum diisi, lihat `data/referensi/laju_subsidensi.json` |
| Faktor emisi | IPCC atau pedoman nasional | TODO(sumber) | Dinyatakan sebagai rentang, bukan angka tunggal |
| Baseline dampak | WRI Indonesia, April 2026 | TODO(verifikasi tautan) | Rp848 miliar per tahun |

Baris bertanda TODO belum punya sitasi yang bisa diverifikasi. Nilainya
sengaja dibiarkan `null` di `data/referensi/` sampai sumbernya ditemukan.

---

## 6. Validasi

**Akurasi model: belum tersedia.** Model belum dilatih. Angka akan diisi apa
adanya setelah pelatihan, termasuk kalau hasilnya jelek.

Yang sudah terverifikasi sejauh ini:

- **Arsip Sentinel-1 di atas AOI: 723 citra** (2015 sampai 2026), diperiksa
  23 Agustus 2026. Di atas ambang 150 yang ditetapkan rencana, sehingga model
  dibangun dengan set fitur penuh.

Sebaran per tahun, sebaran per arah orbit, dan catatan soal lubang arsip
2022 sampai 2024 ada di [`docs/validasi.md`](docs/validasi.md).

**Split latih dan uji berbasis waktu, tidak pernah acak:** latih 2015–2023,
uji 2024–2026.

**Soal data contoh.** Selama model asli belum siap, tabel prediksi diisi data
sintetis bertanda `sumber = 'dummy'` supaya routing, API, dan frontend bisa
dibangun paralel. Setiap tampilan yang memakainya membawa badge **DATA
CONTOH** yang hilang otomatis begitu sumbernya berganti ke model asli.

**Soal kedalaman.** Sentinel-1 hanya memberi label basah atau kering.
Kedalaman genangan adalah estimasi turunan, dan setiap tampilan kedalaman
menyebutkannya sebagai estimasi.

---

## 7. Menjalankan secara lokal

**Prasyarat:** Python 3.11, Git. Node.js menyusul saat frontend dibangun.

```bash
git clone <url-repo>
cd pasang-surut
```

**1. Environment Python**

```bash
python3.11 -m venv .venv

source .venv/bin/activate          # Linux dan macOS
source .venv/Scripts/activate      # Windows, Git Bash
.venv\Scripts\activate             # Windows, PowerShell

pip install -r requirements.txt
```

**2. Variabel lingkungan**

```bash
cp .env.example .env               # lalu isi DATABASE_URL
```

**3. Database**

Jalankan `db/schema.sql` di Supabase SQL Editor.

**4. Uji**

```bash
pytest -q
```

**5. API**

Belum tersedia. `backend/app/main.py` dibangun di milestone berikutnya.
Setelah ada, dijalankan dari `backend/` dengan `uvicorn app.main:app --reload`.

**6. Frontend**

Belum tersedia.

---

## 8. Batasan yang diketahui

Lihat [`docs/batasan.md`](docs/batasan.md) — kerangka sudah ada, isinya
ditulis sepanjang pengerjaan.

Yang sudah pasti masuk daftar:

- Kedalaman genangan adalah estimasi turunan, bukan hasil pengukuran. Radar
  Sentinel-1 hanya membedakan permukaan basah dan kering
- DEMNAS punya RMSE vertikal 2,79 m, jauh lebih besar dari tinggi rob yang
  dimodelkan. DEM hanya dipakai sebagai fitur model
- Cakupan hanya Semarang Utara dan Semarang Timur, bukan seluruh kota
- Kepadatan citra Sentinel-1 di jendela uji 2024–2026 lebih rendah daripada
  di jendela latih, akibat jeda antara berakhirnya Sentinel-1B dan mulai
  regulernya Sentinel-1C
- Tidak ada data lalu lintas real-time, sehingga estimasi waktu tempuh
  berdasarkan kecepatan bebas hambatan yang dikoreksi genangan

---

## 9. Roadmap — ditunda dari MVP

Cakupan seluruh kota; moda transit dan pejalan kaki; laporan genangan
real-time dari warga; dashboard khusus BPBD dan Dishub; notifikasi push;
model hidrodinamik penuh; integrasi data lalu lintas real-time; akun pengguna
dan riwayat perjalanan.

---

## Status pengerjaan

| Milestone | Isi | Status |
|---|---|---|
| M1 | Fondasi repo, environment, AOI, cek arsip Sentinel-1 | Selesai |
| M2 | Graf jalan dan data dummy | Belum |
| M3 | Routing jalan | Belum |
| M4 | Model genangan asli | Belum |
| M5 | Panel dampak dan integrasi | Belum |
| M6 | Deploy | Belum |

Rincian per hari ada di [`docs/PROGRESS.md`](docs/PROGRESS.md).

---

## Struktur repo

```
data/         AOI, data mentah (tidak di-commit), data olahan, referensi
notebooks/    eksplorasi — dibersihkan sebelum submit
gee/          skrip Earth Engine
backend/      app/ (API, domain, schemas), scripts/, tests/
frontend/     React dan MapLibre — dibangun di milestone berikutnya
db/           schema.sql
docs/         arsitektur, metodologi, batasan, validasi, progres
```

Aturan pengembangan ada di `CLAUDE.md`. Rencana lengkap ada di `PLAN.md`.
Keputusan visual ada di `DESIGN.md`. Seluruh teks antarmuka ada di
`copy.id.json`.

---

## Lisensi

MIT. Lihat [`LICENSE`](LICENSE).
