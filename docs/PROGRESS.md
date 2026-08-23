# Progres

Satu entri per sesi kerja. Ditulis apa adanya, termasuk yang gagal.

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
