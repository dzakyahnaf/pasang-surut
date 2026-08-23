# PASANG SURUT — Checklist malam ini (22 Agustus 2026)

Deadline proposal: **31 Agustus 2026, 23.59 WIB**

---

## BLOK 1 — Pendaftaran (± 60 menit, berurutan)

### 1. Google Earth Engine — kerjakan paling awal

**Tautan:** https://code.earthengine.google.com

Urutan klik:
1. Login pakai akun Google
2. Klik logo akun di **pojok kanan atas** → **Register a new Cloud Project**
3. Project name: `pasang-surut-anforcom` (Project ID otomatis jadi `ee-namaanda`)
4. Organization dan Location: pilih **No Organization** kalau pakai akun pribadi
5. Panel **See if you are eligible for noncommercial use** → **Get Started**
6. Pilih **Academic or educational institution using Earth Engine for research or teaching**
7. Isi pertanyaan kelayakan → **Check eligibility**
8. Bagian **Choose your plan** → pilih **Community tier**
9. Kalau diminta enable API, klik **Enable**

Referensi resmi: https://developers.google.com/earth-engine/guides/access
Halaman noncommercial: https://earthengine.google.com/noncommercial/

> **PENTING — kuota.** Sejak 27 April 2026 tiap proyek noncommercial punya kuota
> compute bulanan yang reset tanggal 1. Kuota Agustus Anda tidak akan bertambah
> sebelum deadline. **Tiap anggota tim daftarkan proyek sendiri-sendiri** —
> kuota dihitung per proyek, jadi tiga orang berarti tiga jatah cadangan.

---

### 2. Copernicus Data Space — asuransi, jangan dilewat

**Tautan:** https://dataspace.copernicus.eu → tombol **Register**
**Browser citra:** https://browser.dataspace.copernicus.eu

Aktif langsung tanpa persetujuan. Ini jaring pengaman kalau GEE tersendat atau
kuotanya habis. Lima menit sekarang, menyelamatkan dua hari nanti.

---

### 3. DEMNAS

**Tautan:** https://tanahair.indonesia.go.id/demnas/
**Alternatif portal unduh:** https://tanahair.indonesia.go.id/portal-web/unduh

1. Registrasi akun (gratis)
2. Cari area Jawa Tengah / Semarang
3. Unduh tile GeoTIFF yang menutupi AOI
4. **Langsung clip ke AOI setelah diunduh.** Jangan olah tile penuh.

Spesifikasi: resolusi 0,27 arc-second (± 8 m), datum vertikal EGM2008, RMSE 2,79 m.

Cadangan tanpa registrasi: Copernicus DEM GLO-30 atau SRTM, sudah tersedia
langsung di dalam Earth Engine.

---

### 4. AVISO — daftar, tapi jangan diandalkan

**Tautan:** https://www.aviso.altimetry.fr → menu Data → Data access → registration form

Untuk model pasut FES lewat pyTMD. Persetujuannya bisa berhari-hari, jadi daftar
sekarang lalu **lupakan**. Jalur utama pasut Anda adalah rekonstruksi harmonik
dari konstanta terpublikasi (lihat Blok 2 nomor 12).

---

### 5. Infrastruktur (instan, ± 10 menit total)

| Layanan | Tautan | Fungsi |
|---|---|---|
| Supabase | https://supabase.com | PostgreSQL + PostGIS, free tier |
| Vercel | https://vercel.com | Hosting frontend |
| Railway | https://railway.app | Hosting API Python |
| GitHub | https://github.com | Repo — **set PUBLIC sejak awal** |

Di Supabase: New project → tunggu provisioning → **SQL Editor** → tempel isi
`schema.sql` → Run.

---

### 6. Figma — wajib menurut rulebook poin 7.9

**Tautan:** https://www.figma.com
**Paket pendidikan:** https://www.figma.com/education/

Daftar pakai email kampus. Simpan tautan file Figma — harus masuk Lampiran proposal.

---

## BLOK 2 — Tugas nol-latensi (± 90 menit)

### 8. Bekukan AOI — SUDAH DIBUATKAN

File `aoi_semarang_pilot.geojson` sudah siap. Yang perlu Anda lakukan:

1. Buka https://geojson.io, drag file-nya ke sana
2. Cocokkan dengan batas kelurahan sebenarnya, geser kalau perlu
3. Isi field `dibekukan_pada` dengan tanggal hari ini
4. Commit ke repo di `data/aoi/`
5. **Umumkan ke grup: mulai sekarang semua orang pakai file ini**

### 9. Kontrak tabel — SUDAH DIBUATKAN

File `schema.sql` sudah siap, tinggal Run di Supabase SQL Editor.

Yang perlu disepakati lisan malam ini: **Orang B boleh mengisi
`prediksi_genangan` dengan `sumber = 'dummy'` mulai besok pagi**, supaya seluruh
mesin routing bisa dibangun tanpa menunggu model Orang A selesai di hari ke-4.

### 10. Kumpulkan tanggal kejadian rob Semarang 2015–2026

Tugas browser murni, tidak butuh koding. Target 20–30 tanggal.

Kata kunci pencarian:
- "banjir rob Semarang [tahun]"
- "rob Kaligawe" / "rob Tanjung Emas" / "rob Terboyo"
- "BMKG peringatan dini banjir pesisir Semarang"
- "rob Semarang lumpuh" / "rob Semarang tertinggi"

Catat di spreadsheet: tanggal, lokasi terdampak, tinggi genangan kalau disebut,
tautan sumber. Kolom sumber ini nanti langsung masuk Daftar Pustaka proposal.

### 12. Cari konstanta harmonik pasut Semarang

Kata kunci: "konstanta harmonik pasang surut Semarang", "komponen pasut Tanjung
Emas", "amplitudo fase M2 S2 K1 O1 Semarang". Yang dicari: amplitudo dan fase
untuk M2, S2, N2, K2, K1, O1, P1.

Ini jalur pasut utama Anda. Offline, tidak bisa mati saat presentasi.

---

## BLOK 3 — Kalau GEE sudah disetujui

### 11. Cek cakupan arsip Sentinel-1 — SCRIPT SUDAH DIBUATKAN

1. Buka https://code.earthengine.google.com
2. Tempel seluruh isi `gee_cek_cakupan_s1.js`
3. Klik **Run**
4. Baca Console
5. Tab **Tasks** → Run task ekspor CSV

**Angka yang harus Anda laporkan ke tim malam ini:**

- [ ] Total citra: _______
- [ ] Jumlah 2022, 2023, 2024 (ini yang rawan berlubang): ___ / ___ / ___
- [ ] Jumlah 2025 dan 2026 (kalau nol, GEE belum memuat Sentinel-1C/1D): ___ / ___
- [ ] Ascending: _______  Descending: _______

**Ambang keputusan:**

| Total citra | Artinya |
|---|---|
| > 150 | Aman, lanjut sesuai rencana |
| 80–150 | Cukup, tapi pangkas fitur model supaya tidak overfit |
| < 80 | Kabari tim malam ini juga. Pendekatan harus diubah |

---

## Kalau cuma sempat tiga hal

1. Daftar Google Earth Engine (nomor 1)
2. Daftar Copernicus Data Space (nomor 2)
3. Jalankan `schema.sql` di Supabase (nomor 9)

Sisanya bisa besok pagi.
