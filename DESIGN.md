# DESIGN.md — Sistem Visual PASANG SURUT

Acuan tunggal untuk seluruh keputusan visual. Claude Code **wajib** membaca file
ini sebelum menulis satu baris CSS atau komponen. Tidak ada warna, ukuran huruf,
atau radius yang boleh muncul di kode tanpa asalnya ada di sini.

---

## 1. Brief

### Pengecualian branch pratinjau peta dasar

Atas permintaan Dzaky 22 September, `preview/peta-dasar-osm` membandingkan
basemap OSM siap pakai (CARTO Voyager) dengan tampilan lokal pada `main`.
Palet basemap mengikuti gaya penyedia, termasuk daratan, bangunan, jalan,
dan label tempat. Font tetap Barlow; panel, warna genangan, pola, serta rute
memakai token aplikasi. Jalan kering dan label lokal disembunyikan agar
tidak bertumpuk dengan basemap. Ini belum merupakan keputusan desain main.


**Produk.** PASANG SURUT — alat pengambilan keputusan perjalanan di kota pesisir
yang rutin tergenang rob.

**Pengguna.** Warga pesisir Semarang Utara dan Timur. Pengendara motor yang
berangkat kerja subuh, sopir logistik menuju Pelabuhan Tanjung Emas, pemilik
usaha yang menjadwalkan pengiriman. Ponsel Android kelas menengah ke bawah,
layar 5–6,5 inci, sering di bawah matahari langsung atau dalam gelap sebelum
subuh, hampir selalu sedang terburu-buru.

**Satu pekerjaan layar ini.** Menjawab: *apakah jalan yang saya lewati akan
terendam pada jam saya berangkat, dan berapa ongkosnya kalau saya menghindar.*

**Konsekuensi desain.** Ini instrumen, bukan aplikasi hiburan. Peta adalah
konten, bukan latar. Angka harus terbaca sambil berdiri di teras rumah dalam
sepuluh detik. Tidak ada onboarding, tidak ada registrasi, tidak ada tur fitur.

---

## 2. Arah visual: chartplotter

Rujukannya dua artefak dari dunia subjeknya sendiri.

**Papan duga air.** Papan bergaris ukur yang dipasang di dinding pelabuhan dan
pilar jembatan, dicat berselang agar tinggi muka air terbaca dari jauh. Dari
sinilah tangga kedalaman dan pita waktu diturunkan.

**Chartplotter.** Instrumen navigasi kapal: badan gelap tidak memantul, jendela
peta yang menyala, angka ambar yang bertahan terbaca di atas biru laut. Dari
sinilah pembagian gelap-terang antarmuka diturunkan.

Hasilnya: **badan instrumen gelap, jendela peta terang.** Peta dan data
genangan adalah satu-satunya hal yang menyala di layar, karena memang itu
isinya. Badan gelap juga menekan silau saat dipakai subuh, yaitu jam paling
sering orang mengecek rob.

### Yang sengaja tidak dipakai

| Arah | Alasan ditolak |
|---|---|
| Latar krem hangat + serif + aksen terakota | Rujukan peta laut kuno sempat mengarah ke sini. Ditolak karena sudah jadi tampilan bawaan desain buatan AI dan bukan pilihan yang lahir dari brief ini |
| Hitam pekat + satu aksen hijau asam | Kontras berlebihan, tidak ada dasarnya di dunia subjek |
| Tata letak koran, kolom padat, radius nol | Antarmuka ini dipakai sambil berdiri di teras, bukan dibaca sambil duduk |
| Kartu berbayang di atas kisi | Menjadikan peta latar belakang, padahal peta adalah kontennya |

---

## 3. Warna

Seluruh nilai ditulis sebagai CSS custom property. **Dilarang menulis nilai heks
langsung di komponen.**

### 3.1 Badan instrumen

```css
--lambung-1:  #0B1F2A;   /* panel utama, bilah bawah, rail kiri */
--lambung-2:  #12303E;   /* panel terangkat, kontrol aktif      */
--lambung-3:  #1B4356;   /* garis rambut di atas gelap          */
```

### 3.2 Permukaan terang

Sengaja **sejuk kebiruan**, bukan krem hangat. Ini warna dek baja bercat, bukan
kertas.

```css
--dek-1:  #F2F5F6;   /* lembar bawah, panel hasil */
--dek-2:  #E3EAEC;   /* baris berselang, pembatas */
--dek-3:  #CBD7DB;   /* garis pemisah             */
```

### 3.3 Tinta

```css
--tinta-1:  #0B1F2A;   /* teks utama di atas terang */
--tinta-2:  #46626F;   /* teks sekunder             */
--tinta-3:  #7E97A3;   /* label, satuan, teks mati  */
--tinta-balik: #E8F1F4; /* teks di atas gelap       */
```

### 3.4 Tangga kedalaman — inti sistem

Diturunkan dari gradasi papan duga air. Luminansi menurun monoton seiring
kedalaman, sehingga urutannya tetap terbaca saat dicetak abu-abu atau oleh
pengguna buta warna.

```css
--air-0:  transparent;  /* kering            */
--air-1:  #A5DBDF;      /* 1–10 cm  · tipis  */
--air-2:  #4FB3C4;      /* 10–25 cm · sedang */
--air-3:  #1C7F9E;      /* 25–50 cm · dalam  */
--air-4:  #0E4C6E;      /* >50 cm   · sangat dalam */
```

**Aturan wajib:** kedalaman tidak pernah disampaikan lewat warna saja. Dua kelas
terdalam **wajib** ditumpuk pola titik halftone dengan kerapatan berbeda. Ini
sekaligus membuat tangkapan layar tetap terbaca di proposal PDF yang dibaca
penguji dalam cetakan hitam putih.

### 3.5 Peran semantik

```css
--bahaya:     #C8322B;  /* ruas tidak bisa dilewati, pita jam bahaya */
--rute:       #FFB020;  /* rute sadar rob — garis penuh              */
--rute-abai:  #7E97A3;  /* rute pembanding — garis putus-putus       */
--aman:       #3E9C6D;  /* penanda jam aman                          */
```

Ambar di atas biru bukan pilihan selera. Itu konvensi tampilan navigasi laut dan
penerbangan, karena ambar adalah warna yang paling bertahan terbaca di atas
latar biru gelap.

### 3.6 Aturan penggunaan

1. `--bahaya` hanya untuk dua hal: ruas yang tidak bisa dilewati, dan pita jam
   bahaya di Pita Pasut. Dilarang untuk tombol hapus, galat formulir, atau
   dekorasi apa pun.
2. `--rute` hanya untuk rute yang direkomendasikan. Bukan warna tombol utama.
3. Gradien dilarang, kecuali satu: gradasi vertikal halus pada Pita Pasut yang
   menandai kolom air. Tidak ada gradien lain di seluruh aplikasi.
4. Kontras teks utama terhadap latarnya minimal 4.5:1, teks besar minimal 3:1.

### 3.7 Keadaan interaksi — ditambahkan 30 Agustus 2026

**Kenapa bagian ini ada.** Berkas ini semula hanya mengatur hover dan fokus.
Audit terhadap panduan mode *Operate* (antarmuka yang dipakai untuk
menyelesaikan tugas, bukan untuk dilihat) menunjukkan kekurangan yang nyata:
setiap kontrol wajib punya **default, hover, fokus, ditekan, nonaktif, memuat,
dan galat** — dan ditemukan `:active` tidak ada sama sekali di seluruh CSS.

Kekurangan itu bukan soal estetika. Antarmuka ini dipakai sambil berdiri dan
terburu-buru, dan **jari menutupi tombol yang sedang disentuh**. Tanpa keadaan
ditekan, umpan balik satu-satunya adalah perubahan yang tertutup jari itu
sendiri.

| Keadaan | Cara menyatakan | Token |
|---|---|---|
| Default | latar panel | `--lambung-1` atau `--dek-1` |
| Hover | panel naik satu tingkat, transisi 120ms | `--lambung-3` |
| Fokus papan ketik | garis luar 2px, offset 2px | `--rute` |
| **Ditekan** | panel turun satu tingkat + tepi `--rute` | `--lambung-2` |
| Nonaktif | teks diredupkan, kursor default | `--tinta-3` |
| Memuat | lihat Bagian 8, "Keadaan memuat" | — |
| Galat | tepi, bukan latar penuh | `--bahaya` |

**Ditekan dinyatakan lewat pergeseran warna panel, bukan lewat gerak.**
Bagian 9 hanya mengizinkan satu animasi terkoreografi, dan aturan itu tetap
berlaku.

---

## 4. Huruf

```css
--font-ui:   "Barlow Semi Condensed", system-ui, sans-serif;
--font-data: "IBM Plex Mono", ui-monospace, monospace;
```

**Barlow Semi Condensed** untuk seluruh antarmuka. Barlow lahir dari kosakata
rambu jalan dan kendaraan umum, jadi ia sudah berada di dunia yang sama dengan
produk ini. Versi semi condensed penting secara praktis: label seperti
"Terboyo Kulon" dan "kawasan industri" harus muat di layar 5 inci tanpa
dipotong.

**IBM Plex Mono** untuk **setiap angka yang merupakan hasil pengukuran**: jam,
kedalaman sentimeter, menit, kilometer, liter, kilogram CO₂e, metrik model.
Alasannya fungsional, bukan gaya: lebar digit yang tetap membuat angka tidak
bergoyang saat Pita Pasut digeser, dan nol bergaris miring mencegah salah baca.

**Larangan.** Jangan memakai Inter, Geist, Poppins, atau Montserrat. Jangan
memakai huruf berkait untuk judul. Jangan memakai lebih dari dua keluarga huruf.

### Tangga ukuran

| Peran | Ukuran | Tebal | Spasi huruf | Keterangan |
|---|---|---|---|---|
| Angka utama | 34px | 600 | −0.01em | Mono. Menit, kedalaman |
| Judul layar | 22px | 600 | −0.01em | |
| Judul bagian | 13px | 700 | 0.08em | HURUF BESAR. Gaya rambu |
| Isi | 15px | 400 | 0 | |
| Label | 12px | 500 | 0.02em | |
| Data sekunder | 13px | 400 | 0 | Mono |
| Satuan | 11px | 500 | 0.04em | Selalu `--tinta-3`, tidak pernah sebesar angkanya |

Satuan selalu lebih kecil dan lebih redup daripada angkanya. `18` besar, `cm`
kecil. Mata membaca besarannya lebih dulu.

---

## 5. Bentuk dan ruang

```css
--r-1: 3px;    /* tombol, kolom isian, lencana */
--r-2: 6px;    /* panel, lembar bawah          */
--radius-lain: DILARANG;
```

Radius 3px adalah bezel instrumen. Bukan nol, karena antarmuka ini disentuh
bukan dibaca. Bukan 16px, karena itu tampilan aplikasi gaya hidup.

**Bayangan dilarang**, kecuali satu bayangan keras di bawah lembar bawah:
`0 -1px 0 var(--lambung-3), 0 -12px 24px rgba(11,31,42,.18)`.

Kedalaman dinyatakan lewat garis rambut 1px dan pergeseran warna panel, bukan
lewat bayangan lembut.

Ruang memakai kelipatan 4: `4 8 12 16 24 32 48`. Tidak ada nilai di luar itu.

Sasaran sentuh minimal 44×44px. Ini bukan anjuran — penggunanya memakai aplikasi
ini sambil berdiri dan terburu-buru.

---

## 6. Elemen tanda tangan: Pita Pasut

**Ini satu-satunya tempat proyek ini boleh berani. Sisanya tenang.**

Penggeser waktu bukan pemilih tanggal. Penggeser waktu **adalah kurva pasang
surut 72 jam ke depan**, digambar sebagai kurva sungguhan, dengan jam berisiko
genangan diarsir `--bahaya` dan jam aman ditandai `--aman`.

```
┌────────────────────────────────────────────────────────────┐
│  PITA PASUT · 72 JAM                          Sen 25 · 16:00│
│                                                             │
│      ╱╲            ╱╲            ╱╲                        │
│     ╱  ╲    ╱╲    ╱  ╲    ╱╲    ╱  ╲     ╱╲               │
│  ──╱────╲──╱──╲──╱────╲──╱──╲──╱────╲───╱──╲──────────    │
│    ▓▓▓▓▓▓        ▓▓▓▓▓▓▓▓        ▓▓▓▓▓▓                    │
│  │    │    │    │    │    │    │    │    │    │            │
│  00   06   12   18   00   06   12   18   00   06           │
│              ▲ pegangan geser                              │
└────────────────────────────────────────────────────────────┘
```

Kenapa ini penting: pengguna tidak sedang bertanya "bagaimana jam 4 sore".
Pengguna sedang bertanya "**kapan saya sebaiknya berangkat**". Pemilih tanggal
memaksa mereka menebak satu per satu. Pita Pasut menjawabnya dalam satu
pandangan — jendela merah terlihat, jendela aman terlihat.

Guratan jamnya digambar bergradasi seperti papan duga air: guratan panjang tiap
6 jam, pendek tiap jam.

**Ketentuan teknis**
- Tinggi 96px di ponsel, 120px di desktop
- Dapat digeser, dapat digeser lewat papan ketik (panah kiri-kanan 1 jam,
  Page Up/Down 6 jam), dan dapat diketuk langsung
- Nilai aktif diumumkan ke pembaca layar sebagai jam, bukan angka mentah
- Pegangan geser lebar minimal 44px

---

## 7. Tata letak

Peta memenuhi layar. Tidak ada kisi kartu.

**Ponsel**
```
┌─────────────────────┐
│  ▓ DATA CONTOH      │  lencana, hanya saat sumber = dummy
│                     │
│        PETA         │  penuh, terang
│   ruas berwarna     │
│   sesuai kedalaman  │
│                     │
├─────────────────────┤
│    PITA PASUT       │  gelap, tanda tangan
├─────────────────────┤
│ RUTE                │  lembar bawah, dapat ditarik
│ 14 mnt · 6,2 km     │  mono
│ +4 mnt +1,1 km      │
│ ⚠ genangan 18 cm    │
└─────────────────────┘
```

**Desktop**: rail kiri 360px berbadan gelap berisi kontrol dan hasil, peta
mengisi sisanya, Pita Pasut melintang penuh di bawah.

---

## 8. Komponen

### Ruas jalan di peta
Lebar 3px kering, menebal sampai 6px seiring kedalaman. Isi warna dari tangga
kedalaman. Dua kelas terdalam ditumpuk pola titik. Ruas tak dapat dilewati:
`--bahaya`, garis putus-putus rapat.

### Rute
Rute sadar rob: `--rute`, lebar 5px, garis penuh, ada garis luar gelap 1px agar
tetap terbaca di atas air. Rute pembanding: `--rute-abai`, 3px, putus-putus.
Keduanya tampil bersamaan — selisihnya adalah argumen produk ini.

### Panel dampak
Empat angka mono berjajar dengan label kecil di bawahnya. Selisih ditulis
bertanda: `+4` menit, `+1,1` km. Ditampilkan sebagai rentang bila tersedia.

### Keadaan memuat, dan bedanya dari keadaan kosong

Ditambahkan 30 Agustus 2026 setelah cacat yang ditemukan di produksi.

**Keduanya wajib dibedakan.** Selama data masih dalam perjalanan, yang benar
adalah mengatakan sedang memuat. Menampilkan keadaan kosong pada saat itu
membuat antarmuka menyarankan tindakan yang tidak perlu — misalnya menyuruh
memuat ulang halaman yang sebenarnya baik-baik saja. **Saran yang salah lebih
buruk daripada diam.**

Aturannya:

- Kontrol yang datanya belum tiba menampilkan teks memuat, bukan teks kosong.
- Keadaan kosong hanya muncul setelah pemuatan **selesai** dan hasilnya nihil.
- Keadaan kosong adalah ajakan bertindak, bukan pengumuman kekosongan.
  Aturan ini sudah ada di Bagian 10 dan berlaku penuh di sini.

### Lencana data contoh
`--bahaya` sebagai latar, teks `--tinta-balik`, huruf besar 12px, radius 3px,
melekat di kanan atas peta. Berbunyi: **DATA CONTOH — bukan prediksi**.
Hilang otomatis saat sumber data berganti ke `model_v1`.

### Peringatan paparan
Bilah `--bahaya` dengan teks putih. Menyebutkan ruas, kedalaman, dan jam
alternatif terdekat yang lebih aman. Bukan sekadar tanda seru.

---

### Konteks lokasi peta — 22 September 2026

Nama jalan utama tampil mulai zoom 10,5 jika ruang mencukupi; jalan lokal mulai 14,5. Nama
kecamatan membantu orientasi sampai zoom 15; tempat penting tetap ditandai.
Label jalan memakai tangga Label 12px menuju Isi 15px ketika diperbesar;
wilayah/tempat memakai Isi 15px. Warna teks `--tinta-1`/`--tinta-2`, halo
`--dek-1` selebar 2px menjaga keterbacaan tanpa mengubah warna risiko.
Renderer menghindari label bertumpuk. Batas kecamatan adalah garis tipis
1px putus-putus, `--tinta-2` opasitas 0,35; garis pantai 2px `--air-3`.
Titik tempat radius 4px berwarna `--lambung-1` dengan tepi 2px `--dek-1`.
Label tempat mengikuti lokasi OSM asli; perjalanan memakai akses jalan
yang diberi awalan “Akses” di panel. Ruas tanpa nama tidak diberi nama rekaan.
Font Barlow yang dibundel harus dimuat sebelum renderer membuat glyph.

## 9. Gerak

Satu momen terkoreografi, tidak lebih.

Saat Pita Pasut digeser, ruas tergenang **terisi dan surut** selama 180ms dengan
`cubic-bezier(.4,0,.2,1)`. Air naik dan turun. Itu satu-satunya animasi yang
menceritakan isi produk.

Selain itu: transisi warna 120ms pada hover, fokus, dan keadaan ditekan.

**Dilarang**: animasi masuk saat gulir, efek parallax, angka berputar, hover
mengambang, dan **denyut pada indikator pemuatan**.

### Revisi 30 Agustus 2026 — larangan pemuatan dipersempit

Aturan sebelumnya berbunyi "dilarang pemuatan berdenyut" dan dibaca sebagai
larangan atas **seluruh** rangka pemuatan. Pembacaan itu keliru dan merugikan.

Panduan mode *Operate* menyatakan: *rangka pemuatan, bukan pemutar di tengah
konten.* Alasannya benar dan dapat diuji — nilai sebuah rangka pemuatan
terletak pada **bentuknya**, yang menunjukkan apa yang akan datang dan menjaga
tata letak tidak melompat. Nilainya **tidak** terletak pada denyutnya.

Maka aturannya dipersempit menjadi:

| Boleh | Dilarang |
|---|---|
| Rangka statis yang meniru bentuk isi yang akan datang | Rangka yang berdenyut atau berkilau |
| Strip status berlabuh di tepi, menyebut apa yang sedang dimuat | Kotak pemuatan melayang di tengah kanvas |
| Menyebutkan bagian yang **sudah** bisa dipakai | Menutupi seluruh layar saat sebagian sudah siap |

**Kotak di tengah kanvas kosong terbaca sebagai dialog yang menghalangi**, dan
selama unduhan berlangsung layarnya tampak rusak alih-alih tampak sedang
bekerja. Itu ditemukan langsung di produksi, bukan dalam teori.

`prefers-reduced-motion: reduce` mengganti isi-surut menjadi pudar silang 80ms.

---

## 10. Suara tulisan

> **Seluruh string sudah ditulis di `copy.id.json`.** Bagian ini adalah alasan
> di baliknya, bukan sumber yang dipakai kode. Ambil teks dari berkas itu lewat
> helper `t()`, jangan menyalin dari tabel di bawah.

Bahasa Indonesia. Kalimat biasa, bukan huruf besar semua kecuali label bagian.
Kata kerja aktif. Tanpa basa-basi.

| Konteks | Tulis | Jangan tulis |
|---|---|---|
| Tombol utama | Cari rute | Submit, Kirim |
| Layar kosong | Ketuk dua titik di peta untuk mulai | Belum ada data |
| Galat | Prediksi untuk jam itu belum tersedia. Pilih jam lain. | Terjadi kesalahan |
| Peringatan | Rute ini melintasi genangan 18 cm di Jl. Kaligawe | Perhatian! |
| Saran | Berangkat pukul 19.00, genangan surut | Optimalkan perjalanan Anda |
| Model belum ada | Model belum dilatih | Akurasi: — |

Nama tombol tidak berubah di tengah alur. Yang bertuliskan "Cari rute"
menghasilkan panel berjudul "Rute", bukan "Hasil".

---

## 11. Lantai mutu

Bukan tambahan, ini syarat selesai.

- [ ] Responsif sampai lebar 360px
- [ ] Fokus papan ketik terlihat jelas: garis luar 2px `--rute`, offset 2px
- [ ] `prefers-reduced-motion` dihormati
- [ ] Pita Pasut dapat dioperasikan penuh lewat papan ketik
- [ ] Kedalaman tidak pernah hanya disampaikan lewat warna
- [ ] Kontras teks utama minimal 4.5:1
- [ ] Sasaran sentuh minimal 44×44px
- [ ] Setiap kontrol punya tujuh keadaan Bagian 3.7, termasuk ditekan
- [ ] Keadaan memuat tidak pernah tertukar dengan keadaan kosong
- [ ] Terbaca di bawah matahari langsung — sudah diuji di luar ruangan
- [ ] Tangkapan layar tetap terbaca saat dicetak hitam putih

---

## 12. Daftar tolak

Bila salah satu muncul di kode, itu bukan desain ini.

1. Gradien ungu ke biru di mana pun
2. Kartu berbayang lembut di atas kisi
3. Radius selain 3px atau 6px
4. Inter, Geist, Poppins, atau Montserrat
5. Emoji sebagai ikon antarmuka
6. Warna heks langsung di komponen tanpa lewat custom property
7. Komponen shadcn atau Material bawaan tanpa penyesuaian token
8. Animasi masuk saat gulir
9. Kedalaman disampaikan hanya lewat warna
10. Pemilih tanggal biasa menggantikan Pita Pasut
11. Latar krem hangat dengan aksen terakota
12. Peta sebagai latar di belakang lapisan kartu
