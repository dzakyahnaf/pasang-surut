# Acuan lomba, alur dan sumber bukti

Paket ini disusun 25 September 2026. Angka mengikuti main `69eae60`, audit
data 25 September, serta potret demo versi
`919aa345-7492-4a53-9e7c-c34086775d18`. Tidak ada hasil wawancara, testimoni,
adopsi, mitra atau dampak lapangan yang ditambahkan tanpa bukti.

## Ketentuan yang dipakai

Nomor halaman berikut adalah halaman PDF, termasuk sampul.

| Acuan | Isi yang dipakai | Penerapan |
|---|---|---|
| Rulebook hlm. 2-3 | Konteks kota dan subtema; pilihan proyek Smart Low-Carbon Urban Mobility | Perjalanan pesisir Semarang dan konsekuensi energi pada slide 2/7 |
| Rulebook hlm. 9; TM hlm. 5-6 | Showcase 30 menit, kunjungan juri maks. 5 menit; persiapan 5 menit; presentasi maks. 10 menit; Q&A 15 menit | Target 9 menit termasuk demo; lampiran terpisah; panduan showcase |
| Rulebook hlm. 10; TM hlm. 7 | Bobot final 30/25/20/15/10 | Pemetaan di tabel berikut |
| TM hlm. 9 | Showcase 08.50-09.20; presentasi tim 1 09.20-09.30; Q&A 09.30-09.45 | Persiapan lebih awal karena tim mendapat urutan 1 |
| Konfirmasi Dzaky | Semua anggota hadir, konfirmasi diterima, TM selesai, tim urutan 1 | Rundown tim; tidak menanyakan ulang kehadiran |
| Jawaban panitia kepada Dzaky | PDF slide perlu dikumpulkan; deadline belum diketahui | Sediakan PDF utama/lengkap; pengumpulan menunggu informasi jalur/deadline |
| Konfirmasi Dzaky 25 September | Belum ada uji pengguna nyata | Slide 8 berisi rencana, bukan hasil |

Dokumen lokal yang dibaca lengkap:

- [Rulebook-dsdc-final.pdf](</C:/Users/Dzaky Ahnaf/Downloads/Rulebook-dsdc-final.pdf>).
- [TM Final DSDC Anforcom 2026.pdf](</C:/Users/Dzaky Ahnaf/Downloads/TM Final DSDC Anforcom 2026.pdf>).

Berkas acuan tetap di lokasi pengguna, tidak disalin ke repo publik.
[Metadata acuan](acuan_berkas.json) mencatat hash dan jumlah halamannya.
Ketentuan Times New Roman, A4, serta batas 30 halaman adalah aturan proposal;
tidak diterapkan sebagai aturan slide final. Video 3-7 menit pada bagian
penyisihan juga tidak menjadi durasi video branding pameran.

## Hubungan dengan penilaian final

| Aspek | Bobot | Dukungan materi | Yang tetap dinilai lewat tindakan tim |
|---|---:|---|---|
| Presentasi | 30% | Satu perjalanan, 9 slide, catatan dan waktu; perubahan pembicara jelas | Penyampaian, kekompakan dan ketepatan waktu |
| Implementasi | 25% | Demo slide 4; akses aplikasi; cadangan 11/12 | Juri mencoba fitur; kemampuan tim menjelaskan hasilnya |
| Tanya jawab | 20% | Lampiran 13-18, sumber dan bekal jawaban | Jawaban sesuai pertanyaan, bukti, etika dan penguasaan batas |
| Showcase | 15% | Panduan kunjungan 5 menit, QR; video pameran tersedia terpisah | Percakapan dan kesempatan mencoba, bukan hanya menonton layar |
| Code project | 10% | Slide 17 menautkan modul, tes, CI dan dokumentasi | Struktur/kualitas kode yang benar-benar diperiksa juri |

PPT membantu menampilkan bukti; kelengkapan slide tidak otomatis memenuhi
nilai implementasi, kualitas kode atau hasil uji pengguna. Figma disebut
sebagai ketentuan umum di rulebook hlm. 5; paket ini tidak mengklaim berkas
prototype tersebut sudah dilengkapi atau dinilai.

## Adaptasi referensi yang diberikan

Referensi DekapAutis dibaca dari
[PPTX](</C:/Users/Dzaky Ahnaf/kompetisi/itconvert/presentasi-alternatif/ITC2026_1_SOFTDEV_PPT_Fable5Enjoyer_DekapAutis_Revisi_v3.pptx>)
dan [PDF 11 halaman](</C:/Users/Dzaky Ahnaf/kompetisi/itconvert/presentasi-alternatif/ITC2026_1_SOFTDEV_PPT_Fable5Enjoyer_DekapAutis_Revisi_v3.pdf>).
Yang diambil adalah cara menghubungkan kebutuhan, alur produk, gambar
implementasi, dan mekanisme yang bisa dijelaskan. Klaim riset pengguna,
AI, kesehatan dan data proyek referensi tidak dipindahkan ke PASANG SURUT.

Perubahan untuk konteks DSDC ini:

- Demo ditempatkan lebih awal agar juri melihat fungsi sebelum mendengar
  rincian metode. Bobot implementasi 25% memberi alasan untuk melindungi
  waktu mencoba aplikasi.
- Daftar fitur dan teknologi dipadatkan menjadi satu alur penggunaan dan
  satu diagram metode. Detail kode menjadi lampiran yang dapat dibuka saat
  ditanya, bukan paragraf yang dibacakan di presentasi utama.
- Satu perjalanan dipakai berulang agar pembuka, demo dan dampak saling
  terhubung. Lokasi disebut dan ditampilkan pada peta beratribusi OSM.
- Bukti dipisahkan sesuai pertanyaannya: tes aplikasi, pengujian pasut di
  stasiun, serta genangan ruas yang belum tervalidasi.
- Roadmap menyebut pengamatan dan uji yang dibutuhkan. Penutup cukup satu
  halaman dengan akses produk dan bukti, tanpa mengulang seluruh isi.

Gaya tulisan mengikuti panduan
[anti-slop-writing Bahasa Indonesia](https://github.com/adenaufal/anti-slop-writing/blob/main/indonesian/SKILL.md)
yang diminta pengguna. Penerapannya berupa kalimat yang dapat diucapkan,
lokasi dan angka spesifik, serta pengurangan slogan. Klaim panduan tersebut
tentang detektor AI tidak dipakai sebagai bukti ilmiah.

## Sumber per slide

| Slide | Sumber yang dapat dibuka | Batas penafsiran |
|---|---|---|
| 1-3 | [Tujuan cepat](../../../data/processed/tujuan_cepat.geojson), [jalan](../../../data/processed/ruas_jalan.geojson), [pantai](../../../data/processed/garis_pantai.geojson); screenshot di [aset lama](../presentasi/aset/) | OSM dan akses graf; belum survei pintu masuk atau wawancara pengguna |
| 2 | [BBWS Pemali Juana, 15 Februari 2026](https://sda.pu.go.id/balai/bbwspemalijuana/pages/posts/perkuat-pengendalian-rob-pantura-wapres-tinjau-pembangunan-tol-semrang-demak-seksi-1) | Konteks penanganan rob 2026, bukan bukti kedalaman di jalan pada skenario demo |
| 4/7/11/12 | [Respons skenario asli](../presentasi/aset/skenario.json), [uji ulang lokal](verifikasi_demo_lokal.json) | Motor, 26 September 08.00/13.00, potret tetap; bukan ETA lalu lintas atau observasi genangan |
| 5/13/15 | [Audit sumber data](../audit_asal_data_25_september.md), [kerentanan.py](../../../backend/app/domain/kerentanan.py), [genangan.py](../../../backend/app/domain/genangan.py), [routing.py](../../../backend/app/domain/routing.py) | Tiga fitur bobot sama; grid 3×3 sel sisi 500 m; asumsi ruas puncak 10%, kedalaman 10-50 cm; jam berangkat tetap |
| 6/16/17 | [Audit regresi](../audit_regresi_22_september.md), [koreksi frontend](../koreksi_panel_23_september.md), [telemetri](../bukti/audit_regresi_22_verifikasi.json), [request](../bukti/audit_regresi_22_requests.json) | 95 tes backend, 26 frontend; 412 request/94,47 detik, 0 OOM/restart dalam jendela uji; bukan janji bebas bug atau SLA |
| 6/14 | [Metadata uji pasut](../data/uji_pasut_independen_25_september.json), [CSV pengamatan](../data/ioc_sema_18_25_september_2026.csv), [grafik](../data/perbandingan_pasut_september.png) | r 0,8340, RMSE simpangan 12,44 cm, MAE 10,32 cm; model dibekukan, bukan akurasi genangan |
| 7/18 | [Perhitungan dampak](../../../backend/app/domain/dampak.py), [penelusuran angka](../../sumber_angka.md), skenario asli | Konsumsi dan sensitivitas asumsi rilis; CO₂ pembakaran, belum pengukuran perjalanan atau CO₂e |
| 8 | Konfirmasi pengguna dalam percakapan; audit data | Uji 5-8 peserta dan kemitraan masih rencana |
| 13 | [Status produksi saat audit](../data/status_produksi_25_september.json), [demo lokal](../../../deploy/demo_lokal.py) | Produksi berakhir eksklusif 5 Oktober 07.00 WIB; lokal 29 September 00.00 WIB; belum ada pipeline permanen |
| 15 | [Uji pembanding routing](../../../backend/tests/test_routing_properti.py), [eksperimen ML](../../../data/referensi/metrik_model.json) | 2.400 pencarian/40 graf kecil dengan bobot tetap; model Sentinel-1 ditolak |
| 17 | [Backend](../../../backend/app), [tes](../../../backend/tests), [frontend](../../../frontend/src), [CI](../../../.github/workflows/uji.yml), [deployment](../../../deploy/vps) | Tautan kode aktual; slide tidak mengubah implementasi |

### Angka yang perlu diucapkan dengan tepat

| Jam | Rute | Menit | Km | Ruas basah dalam model | Maksimum estimasi |
|---|---|---:|---:|---:|---:|
| 08.00 | Mengabaikan genangan | 7,0 | 6,32 | 29 | 28,7 cm |
| 08.00 | Sadar rob | 13,9 | 10,58 | 14 | 24,8 cm |
| 13.00 | Kedua rute sama | 7,0 | 6,32 | 0 | 0 cm |

Tambahan pada 08.00: **6,9 menit, 4,27 km, 0,060-0,111 L BBM, dan
0,138-0,256 kg CO₂**. Selisih dihitung sebelum pembulatan; pengurangan dua
jarak yang dibulatkan dapat berbeda 0,01 km. Ruas basah adalah sisi graf,
bukan jumlah nama jalan, luas genangan, risiko kesehatan, atau orang
terdampak. Nol pada model 13.00 tidak membuktikan jalan kering. Menunggu
lima jam punya biaya jadwal yang belum dihitung.

### Sumber primer data

- [OpenStreetMap dan lisensinya](https://www.openstreetmap.org/copyright).
  Graf lokal dibuat 24 Agustus 2026, 19.394 sisi berarah.
- [Rachman dkk. (2015)](https://ejournal3.undip.ac.id/index.php/joce/article/download/7646/7406).
  Konstanta berasal dari pengamatan 13-27 Maret 2014 sekitar Tanjung Emas.
- [DEMNAS, BIG](https://www.big.go.id/en/content/produk/demnas).
  Tile 1409-22 tersedia lokal; tahun akuisisinya belum terverifikasi.
- [Rahmawati dkk. (2020)](https://ejournal3.undip.ac.id/index.php/geodesi/article/viewFile/26032/23173).
  Subsidensi dari 13 citra Sentinel-1A periode 2015-2018, diringkas per kecamatan.
- [IOC/VLIZ sema](https://www.ioc-sealevelmonitoring.org/station.php?code=sema)
  dan [ketentuan data](https://www.ioc-sealevelmonitoring.org/disclaimer.php).
  Pengamatan baru dipakai menguji pasut, tidak menjadi sensor langsung di
  aplikasi. Data belum melalui quality control; perhatikan ketentuan sumber
  sebelum rencana penggunaan komersial.

Uji September memakai 10.020 rekaman sensor tekanan, 18 September 13.00
sampai 25 September 13.00 WIB. Datum berbeda sehingga masing-masing deret
dikurangi rata-rata. Sampel berdekatan berkorelasi dan jendela hanya satu
minggu. Hasil tidak menguji tinggi absolut, musim lain, atau kedalaman ruas.
Hujan dan model Sentinel-1 tidak masuk penerbit genangan aktif.

### Perbedaan terhadap paket 23 September

Deck lama tetap diarsipkan. Versi ini menambah penjelasan kebutuhan dan
alur produk, mengganti bukti pasut utama dengan evaluasi September, membuat
umur/asumsi data terlihat, menghubungkan dampak dengan subtema secara
terbatas, serta menambah menu lampiran dan struktur kode. Cadangan demo
menggunakan hasil yang sama; tidak ada data baru yang dibuat untuk membuat
hasil perjalanan terlihat lebih baik. Video pameran 24 September belum
direvisi dalam pekerjaan PPT ini.
