# Persiapan tahap final DSDC ANFORCOM 2026

> **Pembaruan produksi 22 September:** Vercel sudah mengarah ke frontend/API
> VPS dengan database VPS; Maknaprice tidak diubah. Label jalan, wilayah,
> dan tempat serta nama akses di panel sudah tampil. Browser produksi dan
> uji publik lulus. Lihat [hasil publikasi](final/publikasi_dan_label_22_september.md).
> Pernyataan “tertahan”/“belum deploy” pada riwayat di bawah sudah diselesaikan.

> **Pembaruan 22 September:** API, frontend, dan database sudah dipindahkan
> ke staging privat VPS dan diuji, termasuk backup/restore serta pemulihan
> database. Maknaprice tidak diubah. Alamat Vercel dipertahankan, tetapi
> pengalihan publik tertahan persetujuan spesifik pembukaan origin HTTP.
> Baca [laporan migrasi terbaru](final/migrasi_vps_22_september.md).
> Label nama jalan/wilayah/tempat tetap perlu diselesaikan sebelum rekaman
> demo; jangan menyamakan validasi pasut dengan akurasi genangan per ruas.

> **Pembaruan 21 September:** empat perbaikan sudah diterapkan dan diuji lokal.
> Render berbayar ditolak; VPS Maknaprice sudah diperiksa sebagai kandidat API
> dan frontend. Belum ada deploy/migrasi. Baca
> [hasil implementasi dan pemeriksaan VPS](final/hasil_21_september.md).

> **Pembaruan 20 September:** gunakan
> [rencana berdasarkan audit terbaru](rencana_final_20_september.md) untuk
> prioritas, jadwal, dan pembagian tugas hingga 24 September. Kehadiran ketiga
> anggota sudah dikonfirmasi dan diterima panitia. Kewajiban PDF dikonfirmasi
> Dzaky berasal dari jawaban langsung panitia. Setelah laporan OOM Render
> pukul 17.09 WIB, kapasitas hosting sedang dievaluasi atas permintaan Dzaky;
> belum ada migrasi/pembelian. Paket hari pertama tersedia dalam
> [pembagian kerja dan inventaris](final/paket_20_september.md).
> Run terjadwal Jaga hidup kini sudah berjalan, tetapi interval teramati masih
> berjam-jam. Temuan baru mencakup retry UI, cakupan waktu data, kinerja, dan
> kasus routing saat pergantian jam; 43 unit test serta 35 tes HTTP yang lama
> belum mencakup seluruh temuan tersebut. Isi di bawah adalah catatan 19–20
> September sebelum audit terbaru dan perlu dibaca dengan pembaruan ini.

Disusun 19 September 2026 dari rulebook bagian 9 dan 10, catatan panitia, dan
pemeriksaan langsung terhadap aplikasi yang sedang tayang. Nomor pasal di
bawah merujuk ke rulebook.

## Jadwal

| Tanggal | Kegiatan | Keterangan |
|---|---|---|
| Sabtu 19 September | hari ini | tujuh hari sebelum final |
| **Selasa 22 September** | **Technical Meeting, wajib** (10.3) | urutan presentasi diundi di sini (9.1.2); info lewat Instagram ANFORCOM |
| **Rabu 23 September** | batas konfirmasi ketidakhadiran anggota (10.4) | paling lambat 3 hari sebelum final, lewat CP DSDC |
| Kamis 24 September | uji jalur cadangan laptop, ukur ulang waktu rute | PR nomor 6 |
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

## Status aplikasi

**Diperbarui 19 September malam: hidup kembali dan lulus seluruh uji.**

| Pemeriksaan | Hasil |
|---|---|
| `23_uji_menyeluruh` terhadap produksi | 35 lulus, 0 gagal |
| `/api/kesehatan` | `database: true`, commit terbaru sudah tayang |
| Prediksi di basis data | 67.442 baris, sampai 1 Oktober 00.00 UTC |
| Potret cadangan | 26 September 00.00 WIB sampai 28 September 23.00 WIB |
| Uji dengan basis data dimatikan | 35 lulus, 0 gagal, perutean ikut hidup dari potret |
| Tampilan 390 piksel | spanduk dan judul tidak lagi bertumpuk, tanpa gulir mendatar |
| CI `Uji` di GitHub Actions | lulus |
| Workflow `Jaga hidup` | run manual lulus; jadwalnya belum pernah berjalan, lihat di bawah |
| Satu rute di produksi | 3 sampai 8 detik, berubah-ubah antar-pengukuran |
| Satu kali geser Pita Pasut di produksi | sekitar 8 detik server, lalu unduh 6,6 MB |

**Kinerja adalah masalah terbesar yang tersisa, dan sebabnya sudah diukur.**
Menghitung rute sendiri praktis nol detik. Yang mahal adalah data yang
ditarik dari Supabase di Sydney pada SETIAP permintaan: rute memuat seluruh
67.442 baris prediksi, dan setiap geser Pita Pasut memuat ulang GeoJSON 6,6 MB.
Tabel prediksi kini tiga kali lebih besar daripada Agustus karena jendelanya
diperpanjang sampai 1 Oktober. Angka 1,3 detik yang tercatat 29 Agustus diukur
dari server lokal dengan tabel 21.778 baris, jadi tidak sebanding.

Pilihan perbaikannya dibahas di laporan sesi 20 September dan menunggu
keputusan tim: memindahkan Supabase ke Singapura, atau menyajikan data dari
memori server seperti jalur potret.

Siang harinya produksi sempat mati total. Proyek Supabase dijeda karena
seminggu tanpa aktivitas, dan potret cadangan sudah kedaluwarsa sejak 31
Agustus. Juri yang membuka aplikasi akan melihat peta kosong, pesan "Server
tidak merespons", dan Pita Pasut kosong. Tim memulihkan Supabase, lalu pipeline
dijalankan ulang dan seluruh commit di-push.

## PR, diurutkan dari yang menghambat

### Aplikasi

| # | Pekerjaan | Status |
|---|---|---|
| ~~1~~ | Pulihkan proyek Supabase | **Selesai 19 September**, oleh tim |
| ~~2~~ | Jalankan ulang pipeline dengan jendela yang menutupi hari final | **Selesai 19 September.** `06_isi_pemicu --prakiraan`, lalu `11_indeks_kerentanan --mulai 2026-09-19T14:00 --jam 275`, lalu `18_seed_demo --mulai 2026-09-25T17:00 --jam 72` |
| ~~3~~ | Push seluruh commit, pastikan Vercel dan Render deploy ulang | **Selesai 19 September.** Keduanya menayangkan `9b1229a` |
| ~~4~~ | Uji produksi sampai nol gagal, dan buka di lebar ponsel | **Selesai 19 September.** 35 lulus, 0 gagal |
| ~~5~~ | ~~Segarkan prakiraan hujan pada Kamis~~ | **Dicoret, ternyata tidak berguna.** Prediksi dihitung dari pasut harmonik dan indeks per ruas yang tetap. Data hujan tidak dipakai di runtime, jadi menyegarkannya tidak mengubah satu angka pun di aplikasi |
| 6 | Jalur cadangan di laptop, diuji dengan wifi dimatikan | **Terbuka**, tim. Perintahnya di bagian Demo, sudah diuji: 35 lulus |
| 7 | Uji dari HP sungguhan di jaringan seluler (B37) | **Terbuka**, tim |
| 8 | Ping terjadwal ke `/api/kesehatan` | **Terpasang, tetapi belum bekerja.** `.github/workflows/jaga_hidup.yml` lulus saat dipicu manual, namun jadwalnya belum pernah berjalan. Penjaga Render perlu pemantau luar, lihat di bawah |
| 9 | Peta tetap menampilkan jaringan jalan ketika sumbu waktu gagal dimuat | Belum disetujui |
| ~~10~~ | CI yang menjalankan `pytest` setiap push | **Selesai 19 September.** `.github/workflows/uji.yml`. Test yang menjaga dua salinan `copy.id.json` tetap sama (B5) belum dikerjakan |

**Kalau Supabase mati pada hari final**, tidak perlu berbuat apa-apa. Render
beralih sendiri ke potret, dan jalur itu sudah diuji dengan basis data
dimatikan: 35 lulus, termasuk perutean.

**Workflow `Jaga hidup` TIDAK menjaga Render tetap bangun.** Diperiksa 20
September dini hari: run manualnya lulus, tetapi jadwalnya belum pernah
berjalan satu kali pun dalam 2,5 jam. Konfigurasinya benar dan status GitHub
normal. Gejala yang sama dilaporkan di
github.com/orgs/community/discussions/205984 sejak 27 Agustus dan belum
selesai. Kalaupun jadwalnya pulih, GitHub hanya menjanjikan "boleh jalan tiap
10 menit"; saat beban tinggi jaraknya bisa berjam-jam, sedangkan Render tidur
setelah 15 menit.

Akibatnya dua hal:

- **Tidak ada surel kegagalan bukan berarti aman.** Surel hanya datang dari
  run terjadwal yang benar-benar berjalan.
- **Penjaga agar Render bangun harus datang dari luar GitHub.** Pilihannya di
  bawah.

| Pilihan | Caranya | Catatan |
|---|---|---|
| Pemantau luar | Daftar UptimeRobot atau cron-job.org, lalu buat monitor HTTP ke `https://pasang-surut-api.onrender.com/api/kesehatan` tiap 5 menit | Tidak dipilih |
| **Ping dari laptop pada hari H** | Satu anggota menjalankan perulangan di Git Bash, lihat di bawah | **DIPILIH TIM 20 September** |
| **Buka aplikasi 30 menit sebelum pameran** | Membangunkan Render sebelum juri datang | **DIPILIH TIM 20 September**, dipakai bersama ping dari laptop |

```bash
while true; do curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" https://pasang-surut-api.onrender.com/api/kesehatan; sleep 300; done
```

Supabase lebih longgar: ia baru dijeda setelah seminggu tanpa aktivitas, dan
setiap kali tim membuka aplikasi untuk latihan, basis data ikut tersentuh.
Kalaupun ia dijeda tepat pada hari final, Render beralih sendiri ke potret.

Layanan yang dijaga bangun terus memakai 720 sampai 744 dari 750 jam gratis
Render per bulan. Setelah lomba, matikan pemantau luar dan workflow `Jaga
hidup` (tab Actions, pilih Jaga hidup, lalu Disable workflow).

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

`docs/demo_script.md` sudah memuat naskah demo. Jam yang dipakai perlu
disesuaikan dengan profil hari final di bawah.

Alur inti, sekitar tiga menit: pilih asal dan tujuan dari tujuan cepat, hitung
rute pada jam surut, geser Pita Pasut ke jam pasang, tunjukkan rute yang
berubah beserta ongkos menghindarnya, lalu buka halaman Validasi.

**Profil Sabtu 26 September**, dari potret. Kedalaman di sini estimasi turunan
dari indeks kerentanan, bukan hasil pengukuran, dan harus disebut begitu saat
demo.

| Jam WIB | Pasut | Ruas tergenang | Kedalaman maksimum, estimasi |
|---|---:|---:|---:|
| 00.00 sampai 03.00 | −0,09 sampai −0,01 m | 0 | — |
| 04.00 | +0,05 m | 173 | 31,8 cm |
| 06.00 | +0,17 m | 739 | 37,6 cm |
| **08.00, puncak** | **+0,23 m** | **1.043** | **40,8 cm** |
| 10.00 | +0,19 m | 859 | 38,9 cm |
| 12.00 | +0,07 m | 276 | 32,8 cm |
| 13.00 sampai 23.00 | +0,00 sampai −0,16 m | 0 | — |

Pita Pasut di produksi selalu dimulai dari jam berjalan. Kalau giliran
presentasi jatuh setelah pukul 13.00, jam berjalan sudah kering, jadi geser ke
pasang berikutnya: Minggu 27 September pukul 09.00, 805 ruas. Dari potret, Pita
Pasut dimulai pukul 00.00 hari final, jadi puncak 08.00 selalu terjangkau.

**Jalur cadangan laptop (PR nomor 6).** Wajib berjalan dari potret, bukan dari
basis data. Dari laptop ke Sydney, satu rute terukur sampai 60 detik; dari
potret, di bawah 0,1 detik. Dua terminal Git Bash dari akar repo:

```bash
cd backend && DATABASE_URL= ../.venv/Scripts/python -m uvicorn app.main:app --port 8000
cd frontend && npm run dev
```

Lalu buka http://localhost:5173. `DATABASE_URL=` yang dikosongkan memaksa API
memakai potret. Huruf dan peta tidak memanggil internet sama sekali, jadi uji
akhirnya dengan wifi dimatikan. Perintah ini sudah diuji 19 September: 35
lulus, 0 gagal.

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
