# PASANG SURUT

Sistem perutean sadar banjir rob untuk Semarang.
Tim: trio la albiceleste (ITS Surabaya) — lomba ANFORCOM 2026 DSDC.
**Deadline keras: 31 Agustus 2026, 23.59 WIB.**

Spesifikasi lengkap ada di `PLAN.md`. Baca bagian yang relevan saat diminta,
jangan baca seluruhnya di setiap sesi.

Seluruh keputusan visual ada di `DESIGN.md`. Seluruh teks antarmuka ada di
`copy.id.json`. **Keduanya wajib dibuka pada sesi mana pun yang menyentuh
antarmuka.** DESIGN.md mengunci tampilan, copy.id.json mengunci kalimat.

## Perintah

Struktur folder mengikuti `PLAN.md` bagian 5: backend di `backend/`,
frontend di `frontend/`. Seluruh perintah di bawah dijalankan dari akar repo
kecuali disebutkan lain.

```bash
source .venv/Scripts/activate           # Windows Git Bash
source .venv/bin/activate               # Linux dan macOS

pytest -q                               # test, dari akar repo

cd backend && uvicorn app.main:app --reload   # API di :8000
cd frontend && npm run dev                    # frontend di :5173

cd backend && python -m scripts.<nama>  # skrip pipeline
```

Urutan pipeline data, dijalankan dari `backend/`:

```bash
python -m scripts.01_bangun_graf        # SEKALI saja, menyentuh Overpass
python -m scripts.02_isi_ruas_jalan     # graf -> tabel ruas_jalan
python -m scripts.03_isi_dummy          # data contoh 72 jam, sumber='dummy'
```

## Konvensi

- Istilah domain Bahasa Indonesia: `genangan`, `pasut`, `ruas`, `kedalaman_cm`, `moda`
- Istilah teknis Bahasa Inggris: `router`, `service`, `repository`, `schema`
- Komentar dan docstring Bahasa Indonesia
- UI Bahasa Indonesia
- Commit message Bahasa Indonesia, deskriptif
- Zona waktu: simpan UTC di database, tampilkan WIB di UI

## Aturan yang tidak boleh dilanggar

1. **Jangan pernah mengarang angka.** Tidak ada akurasi, AUC, atau metrik
   karangan. Kalau model belum dilatih, kembalikan `null` dan UI menulis
   "Belum tersedia". Kriteria lomba menghukum overclaim.
2. **Data sintetis wajib bertanda** `sumber = 'dummy'`, dan UI wajib
   menampilkan badge "DATA CONTOH". Badge hilang otomatis saat
   `sumber = 'model_v1'`.
3. **Kedalaman genangan adalah estimasi turunan.** Sentinel-1 hanya memberi
   label basah/kering. Setiap tampilan kedalaman harus menyebut itu estimasi.
4. **DEMNAS RMSE vertikal 2,79 m**, rob 10–50 cm. DEM dipakai sebagai fitur
   model, tidak pernah sebagai ambang genangan. Dilarang menulis
   `if elevasi < muka_air: tergenang`.
5. **Split latih/uji berdasarkan waktu**, tidak pernah acak.
   Latih 2015–2023, uji 2024–2026.
6. **Jalur demo offline.** Tidak ada panggilan API eksternal saat runtime.
   Graf OSM disimpan ke file, pasut dihitung sekali dan disimpan.
7. **Tidak ada secret di repo.** Pakai `.env`, sertakan `.env.example`.
8. **Jangan commit file raster mentah** (DEMNAS `.tif`, `.osm.pbf`).

## Larangan teks

- Dilarang menulis kalimat berbahasa Indonesia langsung di dalam komponen.
  Semua lewat `t()` dari `copy.id.json`
- Butuh kalimat baru? Tambahkan ke `copy.id.json` lebih dulu, baru dipakai
- Patuhi glosarium di `copy.id.json` — "ruas" bukan "segmen", "genangan"
  bukan "banjir", "moda" bukan "transportasi"
- Galat menjelaskan apa yang terjadi dan apa yang bisa dilakukan. Tidak
  meminta maaf, tidak kabur, tidak memakai tanda seru
- Nama tombol tidak berubah di tengah alur

## Larangan visual

- Setiap warna, ukuran huruf, radius, dan jarak berasal dari `DESIGN.md`
- Dilarang menulis nilai heks di dalam komponen. Semua lewat custom property
- Huruf hanya Barlow Semi Condensed dan IBM Plex Mono. Dilarang Inter, Geist,
  Poppins, Montserrat
- Radius hanya 3px dan 6px. Bayangan dilarang kecuali satu di lembar bawah
- Dilarang emoji sebagai ikon antarmuka
- Dilarang gradien, kecuali satu pada Pita Pasut
- Dilarang kartu berbayang di atas kisi. Peta adalah konten penuh layar
- Kedalaman tidak pernah disampaikan lewat warna saja — wajib disertai pola
- Penggeser waktu adalah Pita Pasut, bukan pemilih tanggal biasa

## Larangan teknis

- Jangan pakai Mapbox — pakai MapLibre GL JS
- Jangan pakai deep learning untuk model genangan — gradient boosting saja
- Jangan panggil Overpass API saat runtime
- Jangan tambah dependency tanpa alasan tertulis

## Batas sesi

Satu sesi = satu milestone. Jangan mengerjakan milestone berikutnya tanpa
diminta. Setelah selesai, perbarui `docs/PROGRESS.md`, commit, lalu berhenti
dan laporkan.

Kalau ada yang ambigu: **berhenti dan tanya.** Jangan berasumsi.
