# Prototipe Figma — jalur yang tersedia dan prompt siap pakai

Rulebook poin 7.9 mewajibkan prototipe Figma. Berkas ini menjawab dua hal:
**apa yang bisa dan tidak bisa dikerjakan Claude Code**, lalu memberi bahan
jadi untuk dua jalur pengerjaan.

Ditulis 30 Agustus 2026. **Sisa waktu ke tenggat: sekitar 36 jam.**

---

## Jawaban jujur atas pertanyaan "apakah bisa?"

**Tidak, saya tidak bisa membuat berkas Figma sendiri.** Alasannya bukan
teknis melainkan batas aturan yang saya pegang di seluruh proyek ini: saya
tidak masuk ke akun, tidak memasukkan kata sandi, dan tidak menyetujui syarat
layanan atau memberi izin OAuth atas nama tim. Memasang plugin Figma dan
menyimpan berkas ke akun Anda melewati ketiganya.

Yang **bisa** saya kerjakan, dan sudah: menyiapkan seluruh bahannya — token
yang tepat, struktur layar, dan prompt yang tinggal ditempel.

Perlu diluruskan juga: alat desain yang tersambung ke sesi ini adalah
**Canva**, bukan Figma. Kalau rulebook menerima Canva, jalurnya berbeda dan
saya bisa membantu lebih jauh. Kalau harus Figma, dua jalur di bawah ini.

---

## JALUR A — impor aplikasi yang sudah jadi (SANGAT DISARANKAN)

**Waktu: 10 sampai 20 menit. Hasil paling mirip, karena memang barang aslinya.**

Aplikasinya sudah tayang dan desainnya sudah final. Menggambar ulang di Figma
dari nol, 36 jam sebelum tenggat, adalah pekerjaan yang hasilnya justru lebih
buruk daripada yang sudah ada.

1. Buka Figma, buat berkas baru.
2. Pasang plugin **html.to.design** (gratis untuk pemakaian dasar).
3. Jalankan plugin, tempel URL berikut:

   | Layar | URL |
   |---|---|
   | Peta dan Pita Pasut | `https://pasang-surut.vercel.app/` |
   | Halaman validasi | buka URL yang sama, klik tombol **Validasi** |

4. Impor pada dua lebar: **1440px** desktop dan **390px** ponsel.
5. Rapikan nama layer, lalu buat tautan prototype: Peta ke Validasi, dan
   kembali.

**Kenapa ini paling masuk akal.** Prototipe yang diminta juri adalah bukti
rancangan antarmuka. Mengimpor aplikasi yang benar-benar berjalan memberi
bukti yang lebih kuat daripada mockup, dan tidak berisiko menyimpang dari
produk yang mereka lihat di tautan.

**Catatan:** langkah 2 menuntut penerimaan syarat layanan plugin. Itu sebabnya
saya tidak mengerjakannya sendiri.

---

## JALUR B — prompt generasi, bila harus digambar dari nol

Tempel prompt di bawah **utuh** ke Claude Design, Figma Make, atau alat
serupa. Prompt ini sengaja memuat larangan, bukan hanya perintah, karena
tanpa larangan alat generatif akan mengembalikan tampilan SaaS bawaannya.

### Prompt

> Rancang antarmuka aplikasi web bernama **PASANG SURUT**, alat pengambilan
> keputusan perjalanan untuk warga pesisir Semarang yang rutin tergenang
> banjir rob. Bahasa antarmuka Bahasa Indonesia.
>
> **Arah visual: chartplotter.** Rujukannya dua benda dari dunia subjeknya
> sendiri — papan duga air yang dipasang di dinding pelabuhan, dan instrumen
> navigasi kapal. Badan antarmuka gelap dan tidak memantul; jendela peta
> terang dan menyala. Peta adalah konten, bukan latar belakang.
>
> **Pengguna** memakai ponsel Android kelas menengah, layar 5 sampai 6,5
> inci, sering di bawah matahari langsung atau dalam gelap sebelum subuh,
> hampir selalu terburu-buru. Satu pekerjaan layar ini: menjawab apakah jalan
> yang saya lewati akan terendam pada jam saya berangkat, dan berapa ongkosnya
> kalau saya menghindar.
>
> **Warna, pakai persis ini, jangan menambah.** Badan instrumen `#0B1F2A`
> panel utama, `#12303E` panel terangkat, `#1B4356` garis rambut. Permukaan
> terang `#F2F5F6`, `#E3EAEC`, `#CBD7DB` — sejuk kebiruan, warna dek baja
> bercat, bukan krem hangat. Tinta `#0B1F2A` utama, `#46626F` sekunder,
> `#7E97A3` label, `#E8F1F4` di atas gelap. Tangga kedalaman genangan
> `#A5DBDF` untuk 1 sampai 10 cm, `#4FB3C4` untuk 10 sampai 25 cm, `#1C7F9E`
> untuk 25 sampai 50 cm, `#0E4C6E` untuk di atas 50 cm. Aksen rute `#FFB020`
> ambar, rute pembanding `#7E97A3` putus-putus, bahaya `#C8322B`.
>
> **Huruf.** Barlow Semi Condensed untuk seluruh antarmuka, IBM Plex Mono
> untuk setiap angka hasil pengukuran: jam, sentimeter, menit, kilometer,
> liter, kg CO2e. Hanya dua keluarga huruf. Angka utama 34px tebal 600, judul
> layar 22px tebal 600, judul bagian 13px tebal 700 huruf besar dengan spasi
> huruf 0.08em, isi 15px tebal 400, label 12px tebal 500, satuan 11px tebal
> 500 dan selalu lebih kecil serta lebih redup daripada angkanya.
>
> **Bentuk.** Radius hanya 3px dan 6px, tidak ada nilai lain. Jarak hanya
> kelipatan 4: 4, 8, 12, 16, 24, 32, 48. Sasaran sentuh minimal 44 kali 44px.
> Kedalaman dinyatakan lewat garis rambut 1px dan pergeseran warna panel.
>
> **Layar yang dirancang.**
>
> 1. Peta penuh layar dengan ruas jalan tergenang diwarnai tangga kedalaman.
>    Rail kiri berisi pilihan titik berangkat dan tujuan, pemilih moda motor
>    atau mobil, tombol cari rute, dan daftar tujuan cepat. Di layar ponsel
>    rail menjadi lembar bawah yang menumpang di atas peta.
> 2. Pita Pasut: bilah penuh lebar di dasar layar, tinggi sekitar 96px. Ini
>    penggeser waktu 72 jam dan elemen tanda tangan aplikasi. Isinya kurva
>    pasang surut dengan gradasi vertikal halus menandai kolom air, garis ukur
>    seperti papan duga air, palang merah `#C8322B` menandai jam-jam
>    tergenang, dan pegangan ambar. Ini bukan pemilih tanggal biasa.
> 3. Panel hasil rute: waktu tempuh dan jarak sebagai angka besar mono, jumlah
>    ruas tergenang di jalur, perbandingan terhadap rute yang mengabaikan
>    genangan, dan peringatan paparan kesehatan bila rute tetap menembus air.
> 4. Halaman validasi berlatar terang, menampilkan metrik model apa adanya
>    termasuk yang buruk.
>
> **Larangan keras. Langgar satu saja dan hasilnya ditolak.**
>
> - Dilarang Inter, Geist, Poppins, Montserrat, atau huruf berkait.
> - Dilarang gradien kecuali satu: gradasi vertikal pada Pita Pasut.
> - Dilarang bayangan, kecuali satu di bawah lembar bawah.
> - Dilarang kartu berbayang mengambang di atas peta. Peta adalah konten
>   penuh layar.
> - Dilarang emoji sebagai ikon antarmuka.
> - Dilarang latar krem hangat dengan aksen terakota. Arah itu sudah
>   dipertimbangkan dan ditolak karena merupakan tampilan bawaan desain
>   buatan AI.
> - Dilarang garis tebal berwarna di satu sisi kartu.
> - Dilarang menyampaikan kedalaman lewat warna saja. Dua kelas terdalam wajib
>   ditumpuk pola titik halftone dengan kerapatan berbeda, supaya tetap
>   terbaca saat dicetak hitam putih dan oleh pengguna buta warna.
> - Dilarang radius selain 3px dan 6px.

---

## Variabel Figma siap salin

Buat koleksi variabel berikut. Nama dipertahankan sama persis dengan CSS
custom property di kode, supaya berkas Figma dan kode tidak menyimpang.

| Koleksi | Nama | Nilai |
|---|---|---|
| Lambung | `lambung-1` / `lambung-2` / `lambung-3` | `#0B1F2A` / `#12303E` / `#1B4356` |
| Dek | `dek-1` / `dek-2` / `dek-3` | `#F2F5F6` / `#E3EAEC` / `#CBD7DB` |
| Tinta | `tinta-1` / `tinta-2` / `tinta-3` / `tinta-balik` | `#0B1F2A` / `#46626F` / `#7E97A3` / `#E8F1F4` |
| Air | `air-1` / `air-2` / `air-3` / `air-4` | `#A5DBDF` / `#4FB3C4` / `#1C7F9E` / `#0E4C6E` |
| Semantik | `bahaya` / `rute` / `rute-abai` / `aman` | `#C8322B` / `#FFB020` / `#7E97A3` / `#3E9C6D` |
| Radius | `r-1` / `r-2` | `3` / `6` |
| Jarak | `s-1` sampai `s-7` | `4` / `8` / `12` / `16` / `24` / `32` / `48` |

---

## Bahan pendukung yang sudah ada di repo

| Berkas | Isi |
|---|---|
| `DESIGN.md` | seluruh keputusan visual, termasuk alasan setiap penolakan |
| `copy.id.json` | seluruh kalimat antarmuka, sudah final |
| `docs/tangkapan/` | enam tangkapan layar aplikasi yang berjalan |

Untuk Jalur B, lampirkan enam tangkapan layar itu ke prompt sebagai rujukan
visual. Alat generatif jauh lebih patuh bila diberi contoh daripada hanya
diberi aturan.
