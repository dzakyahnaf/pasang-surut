# Tugas manual — yang hanya bisa dikerjakan manusia

Berkas ini adalah **satu tempat** untuk seluruh tugas yang tidak bisa
dikerjakan Claude Code, dikumpulkan dari seluruh sesi. Diperbarui tiap sesi.

**Kenapa ada batasnya.** Saya tidak membuat akun, tidak memasukkan kata sandi,
dan tidak menyetujui syarat layanan atau izin OAuth atas nama tim. Itu batas
aturan, bukan batas alat, dan tidak berubah oleh tersedianya browser otomatis.
Beberapa tugas lain butuh perangkat fisik atau orang.

Diperbarui: 29 Agustus 2026, sore. **Sisa waktu ke tenggat: 2 hari.**

---

## MENDESAK — kerjakan hari ini

### M1. Push perbaikan service worker, lalu REDEPLOY Vercel

Push sebelumnya sudah masuk — remote kini di `f09000c`. Tetapi perbaikan
service worker ada di satu commit lokal yang belum terkirim, dan produksi
**masih menyajikan versi lama**:

```
https://pasang-surut.vercel.app/sw.js  ->  const VERSI = "pasang-surut-v1"
```

Selama itu masih v1, siapa pun yang pernah membuka aplikasi sebelum perbaikan
akan terus menerima cangkang lama dari cache — dan cangkang lama menunjuk
bundel lama yang memuat alamat API `localhost`. Halamannya diam saja, tanpa
pesan galat. Menguji dengan `curl` tidak memperlihatkan gejala ini karena
`curl` tidak memakai service worker; harus dibuka di peramban.

```bash
cd "C:/Users/Dzaky Ahnaf/kompetisi/anforcom"
git push origin main
```

Lalu **picu ulang deploy di Vercel** dan periksa dari peramban:

```bash
curl -s https://pasang-surut.vercel.app/sw.js | grep VERSI   # harus v2
```

Bagi yang sudah pernah membuka: muat ulang keras sekali (Ctrl+Shift+R), atau
tutup seluruh tab aplikasi lalu buka lagi.

### M2 dan M3 — SELESAI, diverifikasi

`.docx` kini memuat subjudul baru dua kali dan subjudul lama nol kali; diuji
dengan membaca `word/document.xml` langsung, bukan dengan membuka Word.
`pratinjau_proposal.pdf` yang berasal dari 23 Agustus sudah tidak ada di repo.

Yang masih perlu diselaraskan ke subjudul baru: **judul video YouTube, slide
presentasi, dan Figma.**

### M4 dan M5 — SELESAI, diverifikasi dari luar

Keduanya sudah hidup dan diperiksa 29 Agustus dari luar jaringan lokal:

| Bagian | Alamat | Hasil |
|---|---|---|
| Frontend | https://pasang-surut.vercel.app | bundel memuat alamat API yang benar |
| API | https://pasang-surut-api.onrender.com | `database: true`, 19.394 ruas, 21.778 prediksi |

Jendela prediksi terbentang sampai 1 September pukul 17.00 WIB, jadi menutupi
tenggat. CORS meloloskan asal Vercel dan menolak asal asing. `/api/rute`
mengembalikan `sumber_data` berupa list, sehingga lencana "DATA CONTOH" tidak
lagi hilang setelah pengguna menghitung rute.

Yang tersisa hanya M1 di atas: service worker.

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
