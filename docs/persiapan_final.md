# Persiapan tahap final DSDC ANFORCOM 2026

Disusun 19 September 2026 dari rulebook bagian 9 dan 10, catatan panitia, dan
pemeriksaan langsung terhadap aplikasi yang sedang tayang. Nomor pasal di
bawah merujuk ke rulebook.

## Jadwal

| Tanggal | Kegiatan | Keterangan |
|---|---|---|
| Sabtu 19 September | hari ini | tujuh hari sebelum final |
| **Selasa 22 September** | **Technical Meeting, wajib** (10.3) | urutan presentasi diundi di sini (9.1.2); info lewat Instagram ANFORCOM |
| **Rabu 23 September** | batas konfirmasi ketidakhadiran anggota (10.4) | paling lambat 3 hari sebelum final, lewat CP DSDC |
| Kamis 24 September | segarkan data, uji jalur cadangan | lihat PR nomor 5 dan 6 |
| Jumat 25 September | berangkat ke Semarang | jangan berangkat pada hari H |
| **Sabtu 26 September** | **Final offline di Universitas Diponegoro** | pameran lalu presentasi |

Narahubung: Arya Fathdillah Adi Saputra (WA 0814-6973-5184), Akbar Mukti
Wibowo (WA 0882-1511-0873).

## Bentuk final

1. **Pameran** (9.1.3). Kelima tim di satu ruangan. Selama 30 menit rombongan
   juri berkeliling, paling lama 5 menit per tim.
2. **Presentasi** (9.1.4 sampai 9.1.6), dipanggil sesuai urutan undian: 5 menit
   persiapan, paling lama 10 menit presentasi, paling lama 15 menit tanya
   jawab. Setelah itu kembali ke ruang pameran. Tim berikutnya diharapkan sudah
   siap sebelum dipanggil.

Catatan panitia: slide dan demo boleh format apa pun saat tampil, tetapi
**berkas yang dikumpulkan ke panitia wajib PDF**. Berkas itu dipakai sebagai
cadangan dan pegangan panitia.

### Bobot penilaian (9.2)

| Kriteria | Bobot | Bunyi rulebook |
|---|---:|---|
| Presentasi | 30% | pemaparan materi, manajemen waktu, kekompakan tim saat presentasi **dan pameran** |
| Keberhasilan implementasi | 25% | kinerja dan fungsionalitas aplikasi saat **digunakan langsung oleh juri** |
| Tanya jawab | 20% | menjawab secara kritis, logis, dan cepat, serta etika menjawab |
| Pameran | 15% | kemampuan interaktif dan persuasif kepada pengunjung pameran |
| Code project | 10% | struktur, keterbacaan, dokumentasi, praktik pengembangan yang baik |

Implementasi dan pameran sama-sama menuntut aplikasi yang hidup di tangan
orang lain. Jumlahnya 40 persen.

### Yang bisa menggugurkan atau menggantikan tim

- Terlambat mengonfirmasi kehadiran. Tim lima besar yang terlambat
  digantikan peringkat 6, 7, dan seterusnya (10.1), dan tim yang terlambat
  mengonfirmasi kehadiran dinyatakan gugur (10.5e).
- Anggota yang hadir kurang dari 2 orang (10.2).
- Anggota tidak lengkap tanpa konfirmasi alasan yang jelas (10.5f).
- Technical Meeting berstatus wajib (10.3). Sanksinya tidak ditulis, jadi
  jangan diuji.

## Status aplikasi, diperiksa 19 September

**Belum siap. Fitur inti mati di produksi.**

Yang dilihat juri kalau membuka https://pasang-surut.vercel.app hari ini:
peta kosong tanpa satu ruas pun, pesan "Server tidak merespons. Coba lagi
sebentar lagi.", dan Pita Pasut yang hanya berbunyi "Muat ulang halaman untuk
mengambil data pasut." Yang masih bisa diklik hanya tombol tujuan cepat dan
halaman Validasi.

| Uji terhadap API produksi | Hasil |
|---|---|
| `/api/kesehatan` | menjawab, tetapi `database: false` |
| `/api/jam`, sumbu waktu Pita Pasut | HTTP 503 |
| `/api/genangan` | HTTP 503 |
| `/api/rute`, perutean | HTTP 503 |
| `/api/ruas` | 200, 19.394 ruas dari berkas |
| `/api/tujuan-cepat`, `/api/validasi`, CORS | lulus |
| `23_uji_menyeluruh` | 12 lulus, 2 gagal, bagian perutean tidak bisa dijalankan |
| Bangun dari tidur | 26 detik (Render gratis tidur setelah 15 menit menganggur) |

Rantai sebabnya:

1. **Proyek Supabase dijeda.** Galatnya `tenant/user
   postgres.<ref-proyek> not found`, tanda proyek gratis yang dijeda
   setelah seminggu tanpa aktivitas. Aplikasi terakhir dipakai sekitar akhir
   Agustus.
2. **Potret cadangan kedaluwarsa** sejak 31 Agustus 23.00 UTC. API sengaja
   menolak potret basi, karena prediksi basi lebih berbahaya daripada layar
   kosong. Akibatnya pengaman kedua juga tidak menolong.
3. `/api/ruas` sebetulnya menjawab, tetapi frontend baru memintanya setelah
   sumbu waktu tiba. Karena sumbu waktunya gagal, peta tetap kosong.

Di luar itu, **5 commit lokal belum di-push** (remote masih `9dc8445`). Salah
satunya perbaikan tampilan 390 piksel: tanpa itu, spanduk peringatan menutupi
judul aplikasi di layar ponsel.

## PR, diurutkan dari yang menghambat

### Aplikasi

| # | Pekerjaan | Siapa | Kapan |
|---|---|---|---|
| 1 | **Pulihkan proyek Supabase** di dasbor, tombol *Restore project*. Ref proyeknya ada di `DATABASE_URL` dalam `.env`. Kalau tombolnya tidak ada, kabari dan pakai rencana cadangan di bawah | pemilik akun Supabase | Sabtu 19 atau Minggu 20 |
| 2 | Periksa basis data, jalankan `06_isi_pemicu --prakiraan`, `11_indeks_kerentanan`, dan `18_seed_demo` dengan `--mulai` dan `--jam` diarahkan supaya seluruh hari final tercakup, lalu commit potretnya | Claude | begitu nomor 1 selesai |
| 3 | Push seluruh commit lokal, lalu pastikan Vercel dan Render ikut deploy ulang | tim | setelah nomor 2 |
| 4 | `23_uji_menyeluruh` terhadap produksi sampai nol gagal, dan aplikasi dibuka di lebar ponsel | Claude | setelah nomor 3 |
| 5 | Segarkan prakiraan hujan sekali lagi supaya umurnya paling lama dua hari saat final, lalu push dan uji ulang | Claude, push oleh tim | Kamis 24 malam |
| 6 | Jalur cadangan di laptop: backend dan frontend lokal memakai potret, diuji dengan wifi dimatikan | tim, dibantu Claude | Kamis 24 |
| 7 | Uji dari HP sungguhan di jaringan seluler. Belum pernah dikerjakan (B37) | tim | setelah nomor 4 |

Tambahan yang bisa saya kerjakan bila disetujui:

| # | Pekerjaan | Gunanya |
|---|---|---|
| 8 | Ping terjadwal ke `/api/kesehatan` lewat GitHub Actions | Render tidak tidur saat juri membuka, dan Supabase tidak dijeda lagi |
| 9 | Peta tetap menampilkan jaringan jalan ketika sumbu waktu gagal dimuat | Kegagalan berikutnya tidak lagi berupa layar kosong |
| 10 | CI yang menjalankan `pytest` setiap push, plus test yang menjaga dua salinan `copy.id.json` tetap sama (B5) | Poin "praktik pengembangan yang baik" di Code Project |

**Rencana cadangan bila nomor 1 gagal.** Buat basis data baru, di proyek
Supabase baru atau di Postgres lokal lewat Docker, lalu jalankan ulang pipeline
dari skrip 02. Bahannya masih lengkap di laptop: DEMNAS 43 MB, graf jalan, dan
data olahan. Render otomatis beralih ke potret ketika basis data tidak
terjangkau, jadi potret yang dibangun dari basis data lokal pun cukup untuk
menghidupkan produksi pada hari final. Docker Desktop sedang tidak berjalan,
jadi isi kontainer lama belum diperiksa.

**Supabase akan dijeda lagi** seminggu setelah aktivitas terakhir. Menjalankan
pipeline pada 24 September kemungkinan besar sudah menjaganya sampai final,
tetapi ping harian (PR nomor 8) membuatnya tidak bergantung pada tebakan.

### Presentasi, pameran, dan non-teknis

| # | Pekerjaan | Siapa | Kapan |
|---|---|---|---|
| 11 | Pastikan konfirmasi kehadiran final sudah diterima panitia | tim | secepatnya |
| 12 | Hadiri Technical Meeting, catat urutan tampil dan jawaban atas daftar pertanyaan di bawah | tim | Selasa 22 |
| 13 | Tonton keempat video finalis lain bersama | tim | Minggu 20 |
| 14 | Slide, pembagian bicara, dan latihan berwaktu minimal tiga kali | tim | draf Senin 21, final Kamis 24 |
| 15 | Ekspor slide ke PDF dan kirim ke panitia sesuai arahan Technical Meeting | tim | sesuai arahan |
| 16 | Bank pertanyaan juri, lalu latihan menjawab | Claude menyusun, tim berlatih | Rabu 23 |
| 17 | Materi pameran: pitch, kode QR ke aplikasi, skenario yang dicoba juri sendiri | tim | Kamis 24 |
| 18 | Transport dan penginapan di Semarang, dispensasi kuliah Jumat bila perlu | tim | Senin 21 |

## Persiapan per bidang

### Aplikasi, 25 persen

Juri memegang aplikasinya sendiri. Dua jalur harus hidup: tautan produksi untuk
juri yang membuka dari ponselnya lewat kode QR, dan laptop tim yang bisa
berjalan tanpa internet.

Pada hari H, 30 menit sebelum pameran, buka aplikasi sampai Pita Pasut dan peta
muncul. Langkah ini membangunkan Render dari tidurnya. Pastikan juga
`/api/kesehatan` menjawab `database: true`, atau potretnya masih berlaku.

### Demo

`docs/demo_script.md` sudah memuat naskah demo. Perbarui jam yang dipakai ke jam
pasang tertinggi pada hari final setelah data disegarkan.

Alur inti, sekitar tiga menit: pilih asal dan tujuan dari tujuan cepat, hitung
rute pada jam surut, geser Pita Pasut ke jam pasang, tunjukkan rute yang
berubah beserta ongkos menghindarnya, lalu buka halaman Validasi.

Siapkan cadangan berlapis: produksi, lalu laptop lokal, lalu berkas video asli
di laptop, lalu tangkapan layar alur demo di dalam slide. Lapisan terakhir itu
yang membuat PDF untuk panitia tetap bisa bercerita kalau semua lapisan lain
gagal. Pakai hotspot sendiri, jangan wifi tempat.

### Presentasi, 30 persen

Batasnya 10 menit. Targetkan 9, karena waktu hampir selalu molor saat tampil.
Susunan yang disarankan:

| Menit | Isi |
|---|---|
| 0 sampai 1 | Masalahnya, lewat satu adegan konkret di jalan yang sering tergenang rob |
| 1 sampai 2 | Keputusan yang dijawab dan siapa penggunanya |
| 2 sampai 5 | Demo langsung |
| 5 sampai 7 | Cara kerja: pasut terkalibrasi, indeks kerentanan per ruas, perutean, arsitektur |
| 7 sampai 8 | Validasi: model Sentinel-1 yang ditolak dan alasannya |
| 8 sampai 9 | Dampak, keterbatasan, dan kaitannya dengan tema |

Kekompakan ikut dinilai, jadi ketiganya bicara. Pembagian yang paling alami
mengikuti peran di Lampiran C proposal: Dzaky membawakan data, pemodelan, dan
validasi; Daffa membawakan demo dan antarmuka; Naufal membawakan dampak,
keterbatasan, dan penutup.

Waktu persiapan 5 menit dipakai menyambungkan laptop, membuka aplikasi, dan
memeriksa layar. Latih juga proses ini, bukan hanya presentasinya. Subjudul di
slide harus sama dengan proposal: "Berbasis Rekonstruksi Pasang Surut
Terkalibrasi" (B29).

### Pameran, 15 persen

Rombongan juri paling lama 5 menit di meja kita, dan yang dinilai adalah
interaktif dan persuasif. Jadi bicara singkat, lalu serahkan kendali.

- Pitch 60 sampai 90 detik, lalu minta juri menggeser Pita Pasut sendiri.
- Siapkan dua versi: 5 menit untuk juri, 30 detik untuk pengunjung yang lewat.
- Kode QR tercetak ke aplikasi, supaya pengunjung mencoba di ponselnya.
- Bagi tugas: satu memegang laptop, satu menjelaskan, satu menyambut pengunjung
  berikutnya.
- Pameran berlanjut setelah presentasi. Jaga tenaga.

### Tanya jawab, 20 persen

Lima belas menit, dinilai dari kritis, logis, cepat, dan etika. Bagi pemilik
topik supaya tidak saling menunggu: data dan model ke Dzaky, antarmuka dan
teknis ke Daffa, dampak dan batasan ke Naufal.

Jawab dengan angka yang ada di proposal. Kalau angkanya belum ada, katakan
belum diukur lalu jelaskan cara mengukurnya. Aturan nomor 1 repo berlaku juga di
depan juri.

Pertanyaan yang hampir pasti muncul:

1. Kenapa model Sentinel-1 ditolak, dan apa buktinya?
2. Kedalaman genangan dari mana, kalau Sentinel-1 hanya memberi basah atau
   kering?
3. DEMNAS punya RMSE 2,79 m, bagaimana dipakai untuk rob 10 sampai 50 cm?
4. Seberapa dekat pasut rekonstruksi dengan data terukur?
5. Apa bedanya dengan Google Maps, Waze, atau aplikasi pemantauan rob?
6. Dari mana penalti perutean 1,0, 2,5, dan 8,0?
7. Median selisih rutenya hanya 0,12 menit. Kenapa tetap berguna?
8. Bagaimana data diperbarui setelah lomba, dan berapa biayanya?
9. Bisa dipakai di kota pesisir lain?
10. Apa hubungannya dengan tema Circular City?
11. Kenapa bukan deep learning?
12. Angka subsidensi 9,4 cm per tahun dari mana? Final di Undip, dan sumbernya
    jurnal Geodesi Undip, jadi siapkan jawaban sampai ke tabelnya.

`docs/demo_script.md` sudah memuat enam jawaban. Sisanya bisa saya susun.

### Code project, 10 persen

Juri menilai repo publik, jadi seluruh commit harus sudah di-push. README sudah
lengkap; pastikan tautan live di dalamnya hidup pada hari final. Siapkan satu
orang yang bisa menjelaskan struktur folder dalam satu menit.

### Non-teknis

- Pastikan konfirmasi kehadiran sudah diterima (10.1, 10.5e). Ini satu-satunya
  hal di dokumen ini yang bisa membuat kita kehilangan kursi final.
- Kalau ada anggota yang tidak bisa hadir, konfirmasi lewat CP paling lambat
  Rabu 23 September (10.4).
- Pantau Instagram ANFORCOM untuk jam dan tempat Technical Meeting.
- Kartu identitas ketiga anggota. Rulebook 7 butir 3 mewajibkan tiap peserta
  memiliki identitas.
- Jas almamater menambah kesan kompak. Tanyakan aturan pakaian di Technical
  Meeting.

### Pertanyaan untuk Technical Meeting

- Kapan dan ke mana PDF slide dikirim?
- Apakah presentasi memakai laptop sendiri? Layarnya proyektor atau TV, dengan
  port apa?
- Apakah juri menguji aplikasi di perangkat tim atau di perangkatnya sendiri?
- Apa yang tersedia di meja pameran: colokan, layar, wifi? Bolehkah membawa
  poster atau banner?
- Gedung, jam registrasi ulang, dan aturan pakaian.
- Apakah Code Project dinilai dari tautan repo di proposal, atau perlu dikirim
  ulang?

## Benchmark lima finalis

Deskripsi di bawah diambil dari deskripsi video YouTube masing-masing tim pada
19 September, belum dari menonton videonya.

| Tim | Kampus | Karya | Video | Durasi |
|---|---|---|---|---:|
| TERTOLAK UNDIP | Binus Semarang | **OCEANAGARA**: PWA dengan AI, citra NASA GIBS, dan data BMKG untuk peringatan dini sampah laut dan pencemaran, serta kualitas ikan | https://www.youtube.com/watch?v=hVrlKpYG6po | 6:57 |
| inilah 4 trio | UGM | **PRAKIRA**: peringatan dini penyakit sensitif iklim (DBD, ISPA, leptospirosis) per kecamatan di Semarang, ensemble Random Forest, XGBoost, ExtraTrees, Ridge, dan ElasticNet | https://www.youtube.com/watch?v=4mr3wBQ1qUc | 5:17 |
| wts buku kalkulus 1, 45k nego | ITS | **CIRQUO**: deskripsinya tidak menjelaskan produk, perlu ditonton | https://www.youtube.com/watch?v=8ZxBlfipm4o | 6:56 |
| di ajak ilham mah kita gass | Telkom University | **RobSense**: pemantauan dan peringatan dini rob yang diperparah penurunan muka tanah, untuk masyarakat dan pemerintah | https://www.youtube.com/watch?v=VCNYWIGFm1U | 6:53 |
| trio la albiceleste | ITS | **PASANG SURUT** | https://www.youtube.com/watch?v=CeXsEN_1Zvk | 4:28 |

### Yang perlu diwaspadai

**RobSense adalah pesaing langsung.** Masalahnya sama, rob di Semarang, dan
penyebab yang mereka tekankan juga sama, penurunan muka tanah. Juri hampir
pasti membandingkan. Menurut deskripsinya, RobSense memantau, memberi
peringatan dini, dan memvisualisasikan data. PASANG SURUT menjawab keputusan
perjalanan: lewat ruas mana, pada jam berapa, dan berapa ongkos menghindarinya.
Tonton video mereka sebelum menyusun kalimat pembeda, dan jangan merendahkan
karya tim lain di depan juri.

**PRAKIRA bersinggungan di leptospirosis dan Semarang**, dan mereka memakai
ensemble machine learning. Pertanyaan yang hampir pasti muncul: tim lain
memakai model, kenapa kalian justru menolak model kalian? Jawabannya sudah
terdokumentasi: label Sentinel-1 tidak berkorelasi dengan pasut, aturan pasut
saja setara lemparan koin, dan lima upaya penyelamatan gagal dengan angka
lengkap.

**Selain kita, tiga finalis lain bermain di isu iklim atau pesisir**: RobSense,
PRAKIRA, dan OCEANAGARA. Topik saja tidak akan membedakan kita. Pembedanya dua:
keputusan pada jam keberangkatan, dan keberanian melaporkan model yang ditolak.

## Perlengkapan hari final

- Laptop utama dan laptop cadangan, masing-masing dengan pengisi daya
- Adaptor USB-C ke HDMI, kabel HDMI, colokan terminal
- Hotspot ponsel sendiri
- Kartu identitas ketiga anggota
- PDF slide di laptop dan di flashdisk
- Berkas video asli demo di laptop
- Kode QR tercetak ke aplikasi
