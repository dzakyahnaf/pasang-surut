# Tugas manual — yang hanya bisa dikerjakan manusia

> **Pembaruan 21 September:** perbaikan kode selesai diuji lokal; kandidat
> hosting beralih ke VPS Maknaprice yang sudah diperiksa. Belum ada deploy.
> Rincian pada [hasil 21 September](final/hasil_21_september.md). Materi,
> konfirmasi tenggat PDF saat TM, dan gladi perangkat tetap perlu tim.

> **Pembaruan 20 September:** F1 sudah selesai: Dzaky mengonfirmasi panitia
> menerima kehadiran dan seluruh anggota hadir. PDF merupakan ketentuan dari
> jawaban langsung panitia; tenggat belum diumumkan. Demo lokal serta
> pemanasan/ping tetap disiapkan. Setelah notifikasi OOM pukul 17.09 WIB,
> kapasitas Render dan opsi VPS sedang dievaluasi; belum ada pembelian.
> Pembagian kerja/inventaris ada di [paket 20 September](final/paket_20_september.md);
> checklist lengkap ada di [rencana final](rencana_final_20_september.md).
> Catatan F7 di bawah sudah historis: jadwal Actions kini berjalan, tetapi
> jedanya masih berjam-jam sehingga tidak menggantikan penjagaan hari H.

Berkas ini adalah **satu tempat** untuk seluruh tugas yang tidak bisa
dikerjakan Claude Code, dikumpulkan dari seluruh sesi. Diperbarui tiap sesi.

**Kenapa ada batasnya.** Saya tidak membuat akun, tidak memasukkan kata sandi,
dan tidak menyetujui syarat layanan atau izin OAuth atas nama tim. Itu batas
aturan, bukan batas alat, dan tidak berubah oleh tersedianya browser otomatis.
Beberapa tugas lain butuh perangkat fisik atau orang.

Diperbarui: 19 September 2026. **Final offline di Universitas Diponegoro, 26
September 2026.** Bagian di bawah garis pertama berasal dari masa penyisihan
dan disimpan sebagai riwayat.

---

## TAHAP FINAL — tugas manual per 19 September

Rincian dan alasannya ada di `docs/persiapan_final.md`. Aplikasi di produksi
sudah hidup kembali dan lulus 35 dari 35 uji; yang tersisa di bawah ini hanya
bisa dikerjakan tim.

| # | Tugas | Batas |
|---|---|---|
| F1 | Pastikan konfirmasi kehadiran final sudah diterima panitia (rulebook 10.1 dan 10.5e) | secepatnya |
| F2 | Hadiri Technical Meeting dan catat urutan tampil | Selasa 22 September |
| F3 | Kalau ada anggota yang tidak bisa hadir, konfirmasi lewat CP DSDC (10.4) | Rabu 23 September |
| F4 | Uji jalur cadangan laptop dengan wifi dimatikan; perintahnya di `docs/persiapan_final.md` bagian Demo | Kamis 24 September |
| F5 | Uji dari HP sungguhan di jaringan seluler (M6 di bawah, belum pernah dikerjakan) | Kamis 24 September |
| F6 | Slide, latihan berwaktu, dan PDF slide untuk panitia | Kamis 24 September |
| F7 | Buka setiap surel kegagalan GitHub Actions minggu ini. Tetapi jadwal `Jaga hidup` belum pernah berjalan (masalah di sisi GitHub), jadi **tidak ada surel bukan berarti aman** | sampai final |
| F8 | Matikan workflow `Jaga hidup` dan pemantau luar setelah lomba | setelah 26 September |
| F9 | **Diputuskan 20 September: ping dari laptop pada hari H, ditambah membuka aplikasi 30 menit sebelum pameran.** Tunjuk satu anggota yang laptopnya menjalankan perulangan ping sepanjang acara; perintahnya di `docs/persiapan_final.md` | hari H |

---

## MENDESAK — kerjakan hari ini

### M1 — SELESAI, diverifikasi 30 Agustus

`https://pasang-surut.vercel.app/sw.js` kini berbunyi `pasang-surut-v2`, dan
remote sejajar dengan lokal. Bug cangkang basi tertutup.

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

## SUMBER ANGKA — tiga dari empat SELESAI

Ditelusuri 30 Agustus. Provenans lengkap di **`docs/sumber_angka.md`**.

| # | Angka | Status |
|---|---|---|
| ~~M9~~ | Riset WRI April 2026, Rp848 miliar | **SELESAI.** Paparan Afrizal Ma'arif (WRI Indonesia) 8 April 2026, dilaporkan Suara.com 9 April 2026. Laporan primer WRI belum terbit — dicatat apa adanya |
| ~~M11~~ | Faktor emisi 2,31 dan 2,68 | **SELESAI.** Bukan kutipan melainkan hitungan baku IPCC 2006 Tabel 1.4 dikali nilai kalor KLHK. Keduanya bahan bakar murni, jadi emisi solar cenderung DILEBIHKAN untuk Indonesia yang memakai biodiesel — arah kesalahan yang aman |
| ~~M12~~ | Leptospirosis 32 dan 59 kasus | **SELESAI.** Abdul Hakam, Kepala Dinkes Kota Semarang, dikutip tiga media. Data primer Dinkes tidak dapat diakses (HTTP 403) — dicatat apa adanya |
| **M10** | **Konsumsi BBM mobil 0,090 dan truk 0,250 L/km** | **MASIH KOSONG.** Motor 0,020 L/km sudah bersitasi angka pabrikan skuter. Tidak ada rata-rata nasional resmi untuk mobil dan truk |

**Untuk M10, jangan diisi angka karangan.** Sudah ditulis sebagai asumsi
rancangan di Bagian 5 butir 8. Kalau menemukan sumber, ganti; kalau tidak,
biarkan sebagai asumsi.

### M9b. Keputusan tim yang keluar dari proposal

Catatan pada Lampiran C yang berbunyi *"Diisi mengikuti pembagian kerja pada
rencana kerja, bukan berdasarkan kesepakatan tim"* **dikeluarkan dari
proposal** 30 Agustus. Alasannya sama dengan B17: itu instruksi untuk penulis,
bukan isi proposal, dan berisiko ikut tercetak ke PDF yang dibaca juri.

**Pembagian perannya sendiri tetap wajib dikonfirmasi tim sebelum kirim.**

## RULEBOOK — administratif

| # | Tugas | Catatan |
|---|---|---|
| M13 | **Video YouTube — 10 persen penilaian, masih nol** | **Panduan lengkap siap:** https://claude.ai/code/artifact/40ee9168-8481-4c13-8c1f-ff305b15c875 — memuat sembilan ketentuan rulebook, pembagian peran bertiga beserta alasannya, naskah bertimestamp 4 menit 40 detik, daftar periksa teknis, judul dan deskripsi YouTube siap salin, serta enam pertanyaan juri beserta jawabannya |
| M14 | Prototipe Figma | diwajibkan rulebook 7.9. **Bahan sudah siap di `docs/prompt_figma.md`** — dua jalur, dan Jalur A (impor aplikasi lewat plugin html.to.design) makan 10–20 menit. Saya tidak mengerjakannya sendiri karena butuh login akun dan penerimaan syarat layanan plugin |
| M17 | Unggah lewat app.anforcom.com | langkah terakhir |
| ~~M18~~ | Format Word A4, TNR 12, spasi 1,5, margin 4-3-3-3 | **SELESAI, dikerjakan skrip.** `python -m scripts.22_bangun_docx` membangun ulang `.docx` dari Markdown. Diverifikasi dengan membuka di Word: **23 halaman** dari batas 30, kertas 21×29,7 cm, margin 4-3-3-3, TNR 12, spasi 1,5, 8 gambar |
| ~~M19~~ | Ekspor PDF | **SELESAI.** `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.pdf`, 23 halaman, 8 gambar. Ekspor ulang bila Markdown berubah |
| ~~M20~~ | Enam tangkapan layar aplikasi | **SELESAI.** Ada di `docs/tangkapan/`, diambil dari aplikasi yang berjalan |

---

## LANTAI MUTU — butuh perangkat atau orang

| # | Tugas | Kenapa saya tidak bisa |
|---|---|---|
| M22 | Tangkapan layar dari HP sungguhan | **Uji responsifnya SUDAH dikerjakan** dengan merender aplikasi di dalam iframe 390×844 — media query merespons lebar iframe, bukan lebar jendela. Ditemukan dan diperbaiki: spanduk peringatan menimpa pelat judul. Yang masih perlu perangkat hanya **tangkapan layarnya**, karena MapLibre gagal menggambar peta di dalam iframe bersarang. Bila diambil, tambahkan ke Bagian 10 proposal — masih ada enam halaman sisa |
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

## DIPUTUSKAN 30 Agustus — jangan diangkat lagi

| Hal | Keputusan |
|---|---|
| Pembagian peran tim di Lampiran C | **Disetujui apa adanya.** Dzaky ketua dan rekayasa data serta pemodelan; Daffa antarmuka dan visualisasi peta; Naufal analisis dampak, dokumentasi, dan pengujian |
| Twibbon dan poster Instagram | Dikeluarkan dari daftar atas permintaan tim |
| Karya belum pernah menang lomba | **Terkonfirmasi.** Karya ini baru diikutkan pada ANFORCOM 2026 |

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
