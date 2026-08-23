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
