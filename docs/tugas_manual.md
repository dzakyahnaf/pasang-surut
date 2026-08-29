# Tugas manual — yang hanya bisa dikerjakan manusia

Berkas ini adalah **satu tempat** untuk seluruh tugas yang tidak bisa
dikerjakan Claude Code, dikumpulkan dari seluruh sesi. Diperbarui tiap sesi.

**Kenapa ada batasnya.** Saya tidak membuat akun, tidak memasukkan kata sandi,
dan tidak menyetujui syarat layanan atau izin OAuth atas nama tim. Itu batas
aturan, bukan batas alat, dan tidak berubah oleh tersedianya browser otomatis.
Beberapa tugas lain butuh perangkat fisik atau orang.

Diperbarui: 29 Agustus 2026. **Sisa waktu ke tenggat: 2 hari.**

---

## MENDESAK — kerjakan hari ini

### M1. Push lima commit ke GitHub

Repo publik masih di `1b7c475` (M4). Lokal di `438e261` (M7). Juri akan
membaca repo **tanpa** panel dampak, halaman validasi, artefak deploy, potret
tahan banting, dan draft proposal.

```bash
cd "C:/Users/Dzaky Ahnaf/kompetisi/anforcom"
git push origin main
git push origin feature-freeze     # tag M5
```

Saya tidak melakukannya sendiri karena mendorong ke repo publik adalah
tindakan keluar yang belum Anda izinkan di sesi ini. Verifikasi sesudahnya:

```bash
git ls-remote origin HEAD          # harus 438e261 atau lebih baru
```

### M2. Perbaiki subjudul di halaman sampul `.docx`

Halaman sampul masih berbunyi *"Berbasis Kalibrasi Citra Radar Sentinel-1"*.
Rumusan itu tidak lagi benar — kalibrasinya dikerjakan lalu ditolak. Yang
benar, dan sudah dipakai di Bagian 1 dokumen yang sama:

> Sistem Perutean Sadar Banjir Rob **Berbasis Rekonstruksi Pasang Surut
> Terkalibrasi** untuk Mobilitas Rendah Karbon di Kota Semarang

Dokumen itu kini memuat DUA subjudul yang berbeda. Halaman sampul yang pertama
dilihat juri.

**Selaraskan juga ke:** judul video YouTube, slide presentasi, dan Figma.

### M3. Hapus atau perbarui `pratinjau_proposal.pdf`

Berkas di akar repo itu berasal dari **23 Agustus (M1)**, mendahului seluruh
temuan. Juri yang menelusuri repo bisa membukanya dan mengira itu proposalnya.
Hapus, atau ganti dengan ekspor terbaru.

---

## DEPLOY — artefaknya siap dan sudah diuji

### M4. Render (API)

Render → New → Blueprint → pilih repo. `render.yaml` sudah menyiapkan
sisanya. Dua variabel wajib diisi di dasbor:

| Variabel | Nilai |
|---|---|
| `DATABASE_URL` | URL Supabase **pooler port 6543**, bukan koneksi langsung 5432 |
| `ASAL_DIIZINKAN` | alamat Vercel, tanpa garis miring di ujung |

Citra Docker sudah dibangun dan dijalankan lokal: 244 MB, tujuh endpoint
menjawab, CORS menolak asal yang tidak terdaftar.

### M5. Vercel (frontend)

Vercel → Import repo → root directory `frontend`. Satu variabel:

| Variabel | Nilai |
|---|---|
| `VITE_API_URL` | alamat Render, tanpa garis miring di ujung |

### M6. Uji dari HP di jaringan seluler, bukan wifi

Kriteria terima M6 menuntutnya, dan wifi tidak mewakilinya. Kirim URL ke
seseorang yang belum pernah melihat aplikasi ini dan **jangan jelaskan apa
pun** — kalau ia bingung, itu temuan.

---

## SEBELUM DEMO ATAU REKAMAN

### M7. Segarkan potret tahan banting

Potret membawa tanggal kedaluwarsa dan **ditolak API setelah lewat**. Jalankan
dari `backend/`:

```bash
python -m scripts.06_isi_pemicu --prakiraan
python -m scripts.11_indeks_kerentanan
python -m scripts.18_seed_demo
python -m scripts.18_seed_demo --periksa    # pastikan masih berlaku
```

Lalu commit ulang `data/processed/potret_demo.json` dan push, karena berkas
itulah yang dipakai server saat Supabase tersendat.

### M8. Panaskan layanan

Paket gratis tidur saat menganggur. Buka aplikasi 5–10 menit sebelum juri
memakainya, dan jalankan skenario sekali penuh supaya cache graf panas.
Permintaan rute pertama setelah tidur bisa memakan puluhan detik.

---

## SUMBER ANGKA — empat yang wajib

Rincian dan urutan prioritas di `docs/proposal_draft.md`.

| # | Angka | Di mana muncul |
|---|---|---|
| M9 | **Tautan riset WRI April 2026** | Abstrak, 3.2, 11.1 — baseline seluruh Bagian 11 |
| M10 | **Konsumsi BBM per km** (0,020 / 0,090 / 0,250 L/km) | tabel `ambang_moda`, **tampil di antarmuka** |
| M11 | **Faktor emisi** (2,31 bensin / 2,68 solar kg CO₂/L) | idem |
| M12 | **Kasus leptospirosis** (32 pada 2024, 59 pada 2025) | Bagian 3.4 |

Bila sumbernya benar-benar tidak ditemukan, **turunkan klaimnya**, jangan
diisi angka lain. Tiga sumber lain (panjang jaringan kota, perjalanan per
hari, normal hujan BMKG) boleh tetap kosong — Bagian 11.5 sudah berdiri
tanpa ketiganya.

---

## RULEBOOK — administratif

| # | Tugas | Catatan |
|---|---|---|
| M13 | Video YouTube | delapan butir rulebook; naskah 4 menit 30 detik siap di `docs/demo_script.md`. **Peserta wajib tampil dari awal hingga akhir**, dan visibilitas wajib **PUBLIK** bukan unlisted |
| M14 | Prototipe Figma | diwajibkan rulebook poin 7.9 |
| M15 | Twibbon ke Instagram tiap anggota, tag @anforcom | tiga anggota |
| M16 | Poster ke Instagram tiap anggota, tag @anforcom | tiga anggota |
| M17 | Unggah lewat app.anforcom.com | langkah terakhir |
| M18 | Format Word A4, TNR 12, spasi 1,5, margin 4-3-3-3 | maksimal 30 halaman |
| M19 | Ekspor PDF bernama `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.pdf` | tanpa spasi |
| M20 | Enam tangkapan layar aplikasi | dua gambar sudah siap di `docs/` |
| M21 | Konfirmasi pembagian peran tim | Lampiran C proposal; saya isi mengikuti rencana kerja, **bukan** kesepakatan tim |

---

## LANTAI MUTU — butuh perangkat atau orang

| # | Tugas | Kenapa saya tidak bisa |
|---|---|---|
| M22 | Uji responsif 360px | jendela peramban diubah tetapi viewport tetap 1440; perlu perangkat atau devtools sungguhan |
| M23 | Uji baca di bawah matahari langsung | perlu orang membawa laptop ke luar ruangan |
| M24 | Uji cetak hitam putih | dirancang untuk itu lewat pola halftone, belum dibuktikan |

---

## KEPUTUSAN TIM — bukan keputusan teknis

| # | Keputusan | Konteks |
|---|---|---|
| M25 | **Angka subsidensi mana yang dipakai** | "9–13 cm/tahun" di `PLAN.md` bagian 6 tidak didukung sumber yang kita punya. Proposal sudah diturunkan ke 9,4; PLAN.md belum |
| M26 | **Terima atau tolak penurunan klaim produk** | dari "prediksi genangan" menjadi "prediksi kapan berisiko + indeks kerentanan". Sudah diterapkan atas dasar aturan repo nomor 1 |
| M27 | ~~Sumber kebenaran proposal~~ | **DIPUTUSKAN 29 Agustus:** Markdown jadi acuan, `.docx` dibangun ulang darinya di M8 |
| M28 | Region Supabase | sekarang ap-southeast-2 Sydney, ±370 ms per kueri. Singapura memangkas separuh, tetapi berarti membuat proyek baru |
| M29 | Trailer `Co-Authored-By: Claude Opus 5` di commit | bila rulebook DSDC mempersoalkannya, putuskan sekarang selagi baru 15 commit |
| M30 | Nasib `deret_pasut()` di `domain/pasut.py` | diwajibkan `PLAN.md` 10.2 tetapi tidak pernah dipanggil. Pertahankan sebagai API modul, atau buang |

---

## SUDAH SELESAI — jangan dikerjakan lagi

| Tugas | Selesai |
|---|---|
| Daftar Google Earth Engine, proyek pertama | 28 Agustus |
| Unduh DEMNAS tile 1409-22 | 28 Agustus |
| Buat proyek Supabase | 29 Agustus |
| Perbaiki URL Supabase yang gagal karena `@` di kata sandi | 29 Agustus |
| Aktifkan PostGIS dan pasang skema di Supabase | 29 Agustus |
| Isi Supabase dari pipeline | 29 Agustus |
| Buat repo GitHub publik | 29 Agustus |
| Tetapkan Markdown sebagai sumber kebenaran proposal | 29 Agustus |
