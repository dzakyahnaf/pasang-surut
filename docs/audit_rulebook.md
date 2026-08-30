# Audit proposal terhadap Rulebook DSDC ANFORCOM 2026

Diperiksa 30 Agustus 2026 terhadap `Rulebook-dsdc-final.pdf` (11 halaman).
Vonis per butir: **LULUS**, **PERLU TINDAKAN**, atau **MANUAL**.

---

## 8.1 Ketentuan Proposal

| Butir rulebook | Vonis | Catatan |
|---|---|---|
| Ide orisinil, tidak menjiplak desain | LULUS | Arah visual diturunkan dari papan duga air dan chartplotter; alasan setiap penolakan tercatat di `DESIGN.md` |
| Tidak mengandung SARA, kekerasan, pornografi | LULUS | — |
| Berupa perangkat lunak berbasis website | LULUS | React + FastAPI, tayang di Vercel dan Render |
| Belum pernah menang lomba manapun | **MANUAL** | Hanya tim yang bisa memastikan |
| **Sistematika 14 bagian** | LULUS | Diperiksa satu per satu terhadap urutan rulebook, cocok persis |
| A4, Times New Roman 12, spasi 1,5, margin 4-3-3-3 | **MANUAL** | Pemformatan Word |
| **Maksimal 30 halaman termasuk cover dan lampiran** | **PERLU TINDAKAN** | Perkiraan **29,9 halaman**. Nyaris tanpa sisa — periksa dengan Word, jangan percaya perkiraan |
| Nama berkas `Anforcom2026_DSDC_[Tim]_[Karya].pdf` | LULUS | `.docx` sudah bernama `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut` |
| Unggah lewat app.anforcom.com | **MANUAL** | — |
| **Source code dapat diakses juri, progres 50–75%** | LULUS | Repo publik menjawab HTTP 200; progres jauh di atas ambang minimum |

---

## 8.2 Ketentuan Video — SELURUHNYA MANUAL

| Butir | Status |
|---|---|
| Resolusi minimal 1280x720 | belum dikerjakan |
| Durasi 3–7 menit | naskah `docs/demo_script.md` berdurasi 4 menit 30 detik — **masuk rentang** |
| Berisi demo alur fitur utama | naskah sudah menyusunnya |
| **Peserta tampil dari awal hingga akhir** | wajib, mudah terlewat |
| Judul `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut` | belum |
| Deskripsi `Anforcom 2026 [Tim] - [Deskripsi] - Nama 1 - Nama 2 - Nama 3` | belum |
| Tag `#Anforcom2026` | belum |
| **Visibilitas PUBLIK**, bukan unlisted | belum |

---

## Butir 7 — syarat peserta

| Butir | Vonis |
|---|---|
| 7.9 **Wajib memakai Figma** untuk prototipe; software desain pendukung boleh | **PERLU TINDAKAN** — bahan siap di `docs/prompt_figma.md`. Canva hanya boleh sebagai pendukung, tidak menggantikan Figma |
| 7.10 Twibbon dan poster ke Instagram tiap anggota, tag `@anforcom` | **MANUAL**, tiga anggota |

---

## 8.3 Kriteria penilaian babak penyisihan

| Kriteria | Bobot | Posisi kita |
|---|---:|---|
| **Impact Projection** | 20% | **Kuat.** Kriterianya berbunyi "keterukuran, realistis (**tidak overclaim**), aplikatif". Keputusan Bagian 11.5 untuk **tidak** mengalikan angka rupiah dari dua bilangan tak bersumber justru persis yang diminta kriteria ini |
| **Progres & Validasi Implementasi** | 20% | **Kuat.** Aplikasi tayang dan dipakai juri langsung; halaman validasi menampilkan metrik apa adanya |
| **Kesesuaian Tema/Subtema** | 15% | **Sebelumnya lemah, sudah diperbaiki.** Lihat catatan di bawah |
| **Originalitas dan Kreativitas** | 15% | **Kuat.** Model dilatih, lima kali diupayakan diselamatkan, lalu ditolak — dan dilaporkan di dalam aplikasinya sendiri |
| **Format & Struktur Proposal** | 10% | **Berisiko pada jumlah halaman.** Sistematika sudah cocok persis |
| **Video** | 10% | **Belum ada.** Seluruh 10 persen ini masih nol |
| **Metodologi Pengembangan** | 10% | **Kuat.** Bagian 6.2 menjelaskan kenapa bathtub ditolak secara aritmetis |

**Catatan penting:** "Code Project 10%" ada di kriteria **babak final**, bukan
penyisihan. Catatan sesi sebelumnya yang menyebutnya sebagai bagian penilaian
penyisihan keliru.

---

## Temuan yang diperbaiki 30 Agustus

### 1. Tema besar ANFORCOM tidak pernah disebut — bobot 15 persen

Kriteria berbunyi: *"Karya mencerminkan tema besar ANFORCOM **dan** salah satu
subtema DSDC"*. Sebelum diperbaiki, proposal menyebut subtema **satu kali** di
satu baris tabel, dan **tidak pernah** menyebut:

- tema ANFORCOM 2026 "Circular Economy for Eco-Health Cities"
- tema DSDC "Engineering the Circular City"
- Eco-Health sebagai konsep
- SDG 3 dan SDG 11

Diperbaiki dengan menambah empat baris pada tabel Bagian 1 dan **Bagian 4.5
baru**. Rulebook membolehkan bersandar pada salah satu dari Circular Economy
atau Eco-Health, jadi 4.5 menyatakan terang-terangan bahwa karya ini bersandar
pada **Eco-Health** dan tidak memaksakan kaitan circular economy yang tidak
ada. Rulebook halaman 2 juga memperingatkan "proyek generik tanpa konteks
lokal", dan 4.5 menjawabnya langsung.

### 2. Penutup masih menulis "empat kali" upaya penyelamatan

Bagian 9.3 sudah memuat lima. Diperbaiki menjadi lima.

### 3. Rujukan pustaka menggantung

Lampiran merujuk rulebook sebagai `[11]`, padahal penyisipan entri faktor emisi
dan konsumsi BBM menggeser rulebook ke `[12]`. `[11]` menunjuk entri yang
salah. Diperbaiki, dan seluruh rujukan kini diperiksa otomatis: nol rujukan
menggantung, nol entri yatim.

---

## Yang tersisa sebelum kirim

| # | Hal | Siapa |
|---|---|---|
| 1 | **Video YouTube** — 10 persen penilaian, masih nol | tim |
| 2 | **Prototipe Figma** — diwajibkan 7.9 | tim, bahan siap |
| 3 | **Format Word dan ekspor PDF**, lalu **hitung halaman dengan Word** | tim |
| 4 | Twibbon dan poster Instagram, tag @anforcom | tiga anggota |
| 5 | Konfirmasi pembagian peran tim (Lampiran C) | tim |
| 6 | Konfirmasi karya belum pernah menang lomba lain | tim |
| 7 | Unggah lewat app.anforcom.com | tim |

**Submit siang hari, jangan jam 23.00.**
