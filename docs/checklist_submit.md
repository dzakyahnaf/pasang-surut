# Checklist submit final

Disusun dari `PLAN.md` bagian 12 dan 12B. Status diperiksa 29 Agustus 2026.

**Tenggat: 31 Agustus 2026, 23.59 WIB.**

Legenda status:

| Tanda | Arti |
|---|---|
| ✅ | selesai dan diverifikasi |
| ⚠️ | selesai sebagian, atau selesai tetapi ada catatan |
| ❌ | belum dikerjakan |
| 👤 | hanya bisa dikerjakan manusia |

---

## A. Proposal

| # | Butir | Status | Catatan |
|---|---|---|---|
| A1 | Sistematika persis 14 bagian | ✅ | diverifikasi di `docs/proposal_draft.md`, urutannya cocok dengan rulebook |
| A2 | A4, Times New Roman 12, spasi 1,5, margin 4-3-3-3 | 👤 ❌ | pemformatan Word, M8 |
| A3 | Maksimal 30 halaman termasuk cover dan lampiran | ⚠️ | perkiraan **28,9 halaman**; sisa tipis, ukur ulang dengan Word setelah diformat |
| A4 | Nama berkas `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.pdf` | 👤 ❌ | ekspor PDF |
| A5 | Lampiran memuat tautan video dan repositori | ⚠️ | repositori sudah ada; **video masih TODO** |
| A6 | Ide orisinil, tidak menjiplak | ✅ | seluruh kode dan metode ditulis sendiri; sumber data bersitasi |
| A7 | Tidak mengandung SARA, kekerasan, pornografi | ✅ | — |
| A8 | Karya belum pernah menang di lomba manapun | 👤 | konfirmasi tim |

## B. Video

| # | Butir | Status | Catatan |
|---|---|---|---|
| B1 | Resolusi minimal 1280 × 720 | 👤 ❌ | — |
| B2 | Durasi 3–7 menit | 👤 ❌ | naskah 4 menit 30 detik siap di `docs/demo_script.md` |
| B3 | Demo mencakup alur fitur utama | 👤 ❌ | skenario sudah diuji berjalan tanpa galat konsol |
| B4 | **Peserta tampil dari awal hingga akhir** | 👤 ❌ | sering terlewat; rulebook menegaskan |
| B5 | Judul `Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut` | 👤 ❌ | tanpa spasi |
| B6 | Deskripsi format rulebook | 👤 ❌ | `Anforcom 2026` / `[Nama Tim] - [Deskripsi]` / daftar anggota |
| B7 | Tag `#Anforcom2026` | 👤 ❌ | — |
| B8 | **Visibilitas PUBLIK** | 👤 ❌ | bukan "unlisted" |

## C. Teknis dan administratif

| # | Butir | Status | Catatan |
|---|---|---|---|
| C1 | Repo GitHub publik | ✅ | diuji clone tanpa kredensial dari direktori bersih: berhasil |
| C2 | **Repo memuat pekerjaan terbaru** | ❌ | **lima commit belum di-push.** Remote di `1b7c475` (M4), lokal di `438e261` (M7). Lihat Perbaikan 1 |
| C3 | Source code mencerminkan progres 50–75% | ✅ | tujuh milestone, 43 uji, fitur inti berjalan |
| C4 | Tautan website atau build aplikasi hidup | ❌ | artefak deploy siap dan teruji, penerapannya belum |
| C5 | **Prototype dibuat dengan Figma** (poin 7.9) | 👤 ❌ | wajib menurut rulebook |
| C6 | Twibbon ke Instagram tiap anggota, tag @anforcom | 👤 ❌ | tiga anggota |
| C7 | Poster ke Instagram tiap anggota, tag @anforcom | 👤 ❌ | tiga anggota |
| C8 | Diunggah lewat app.anforcom.com pakai akun tim | 👤 ❌ | langkah terakhir |

## D. Kepatuhan visual (PLAN.md 12B)

| # | Butir | Status | Bukti |
|---|---|---|---|
| D1 | Warna, huruf, radius, jarak dari `DESIGN.md` | ✅ | diperbaiki M6: 2 nilai jarak dan 3 nilai sentuh dijadikan token |
| D2 | Tidak ada heks di komponen | ✅ | 0 temuan |
| D3 | Barlow + IBM Plex Mono termuat | ✅ | 6 `@import "@fontsource/..."`, swadaya |
| D4 | Pita Pasut lewat papan ketik | ✅ | `role="slider"`, `aria-valuetext`, PageUp/Down |
| D5 | Kedalaman lewat warna DAN pola | ✅ | pola titik dua kerapatan di peta dan legenda |
| D6 | Tidak ada shadcn / Material | ✅ | `package.json` bersih |
| D7 | Tidak ada emoji sebagai ikon | ✅ | 0 temuan |
| D8 | Peta konten penuh layar | ✅ | rail di samping, bukan kartu di atas kisi |
| D9 | Lantai mutu `DESIGN.md` 11 | ⚠️ | **6 dari 9 terpenuhi**; tiga sisanya di E |
| D10 | Tidak ada kalimat Indonesia di komponen | ✅ | 0 temuan dari tiga pola audit |
| D11 | `t()` melempar galat | ✅ | terbukti di M5 |
| D12 | Istilah mengikuti glosarium | ✅ | istilah terlarang hanya muncul di definisi yang melarangnya |

## E. Lantai mutu yang belum terpenuhi

| # | Butir | Status | Kenapa belum |
|---|---|---|---|
| E1 | Responsif sampai lebar 360px | ❌ 👤 | jendela diubah tetapi viewport tetap 1440; perlu perangkat atau devtools |
| E2 | Terbaca di bawah matahari langsung | ❌ 👤 | perlu orang membawa laptop ke luar |
| E3 | Tangkapan layar terbaca saat dicetak hitam putih | ⚠️ 👤 | dirancang untuk itu (pola halftone), belum diuji cetak |

## F. Angka yang belum bersumber

Rincian dan urutan prioritas di `docs/proposal_draft.md` bagian
"Ringkasan TODO(sumber)".

| # | Yang belum bersumber | Status | Akibat bila ditanya juri |
|---|---|---|---|
| F1 | Tautan riset WRI April 2026 | ❌ 👤 | **terparah** — baseline seluruh Bagian 11 dan angka pembuka Abstrak |
| F2 | Konsumsi bahan bakar per km | ❌ 👤 | tampil di antarmuka, juri melihatnya saat mencoba aplikasi |
| F3 | Faktor emisi bahan bakar | ❌ 👤 | idem |
| F4 | Kasus leptospirosis 32 → 59 | ❌ 👤 | dipakai membangun argumen kesehatan |
| F5 | Panjang jaringan jalan Kota Semarang | boleh kosong | Bagian 11.5 berdiri tanpanya |
| F6 | Perjalanan terdampak per hari | boleh kosong | idem |
| F7 | Normal hujan BMKG | boleh kosong | sudah dinyatakan sebagai batasan |

---

## Ringkasan

| Kategori | ✅ | ⚠️ | ❌ | Total |
|---|---:|---:|---:|---:|
| A. Proposal | 3 | 2 | 3 | 8 |
| B. Video | 0 | 0 | 8 | 8 |
| C. Teknis dan administratif | 2 | 0 | 6 | 8 |
| D. Kepatuhan visual | 11 | 1 | 0 | 12 |
| E. Lantai mutu | 0 | 1 | 2 | 3 |
| F. Sumber angka | 0 | 3 | 4 | 7 |
| **Total** | **16** | **7** | **23** | **46** |

**Yang paling mendesak, berurutan:**

1. **Push lima commit ke GitHub.** Satu perintah. Tanpa ini juri membaca repo
   tanpa M5, M6, dan M7.
2. **Perbaiki subjudul di halaman sampul `.docx`.** Masih memakai rumusan lama
   yang sudah tidak benar.
3. **Deploy** — artefak siap dan teruji.
4. **Video** — delapan butir rulebook, seluruhnya belum.
5. **Figma** — diwajibkan rulebook poin 7.9.
6. **Empat sumber angka** (F1–F4).
