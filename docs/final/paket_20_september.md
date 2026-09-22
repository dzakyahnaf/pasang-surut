# Paket kerja 20 September 2026

**Pembaruan 21 September:** empat perbaikan aplikasi selesai diuji lokal;
lihat [hasil implementasi dan VPS](hasil_21_september.md). Checklist materi
dan pelaksanaan tugas anggota di bawah belum otomatis selesai.

Status: pembagian kerja, inventaris, prioritas, dan outline sudah disusun.
Ini penetapan pekerjaan dalam rencana, bukan pernyataan anggota sudah
menyelesaikan tugas atau menyetujui jam kerja pribadi. Kode aplikasi belum
diubah dalam penyusunan paket ini.

Rujukan: [audit lengkap](../rencana_final_20_september.md),
[rancangan teknis dan pilihan hosting](solusi_teknis_dan_hosting.md), dan
[outline delapan slide, sembilan menit](outline_slide.md).

## 1. Identitas produk yang dikunci untuk materi

> PASANG SURUT membantu pengguna membandingkan rute dan jam keberangkatan
> di pesisir Semarang menggunakan rekonstruksi pasut dan indeks kerentanan
> jalan, serta memperlihatkan tambahan waktu, jarak, dan estimasi biaya.

Sasaran demo: orang yang perlu melakukan perjalanan di pesisir Semarang.
Satu cerita utama: perjalanan Stasiun Semarang Tawang–Kawasan Industri
Terboyo dengan motor pada dua waktu berbeda. Nama tempat, wilayah, dan
legenda harus terbaca sebelum membahas algoritme.

Batas klaim: evaluasi pasut bukan akurasi genangan per ruas; keluaran
kedalaman merupakan estimasi model; rute tidak dijamin aman; angka dampak
merupakan simulasi terhadap baseline, belum penghematan nyata pengguna.
Model routing untuk versi final mengikuti keputusan T4 dalam rancangan
teknis. Jangan menjanjikan kemampuan baru sebelum implementasi diverifikasi.

## 2. Pembagian tugas dan hasil malam ini

Kapasitas ideal: tiga jam efektif per anggota pada 20 September, lalu enam
jam per hari pada 21–24 September. Total 81 jam-orang; sekitar 16 jam-orang
disisihkan untuk integrasi, gangguan, dan penyesuaian TM. Latihan termasuk
jam kerja tersebut. Blok malam ini dapat digeser mengikuti waktu tersedia.

| PIC | Kepemilikan sampai final | Hasil 20 September | Kriteria selesai |
|---|---|---|---|
| Dzaky | Backend, data, metode, keputusan hosting, jawaban teknis | Tinjau T0/T2/T4; simpan waktu insiden dan ringkasan metrik Render; pilih arah hosting setelah menilai biaya; setujui batas klaim materi | Semua keputusan dan hal yang belum diketahui tertulis; pekerjaan backend punya urutan dan tes penerimaan |
| Daffa | Frontend, label peta, interaksi, operator demo, paket lokal | Daftar perubahan retry/slider/label; pilih enam tangkapan layar yang perlu diperbarui; inventaris dua laptop dan kebutuhan port/proyektor | Satu alur demo bernama lokasi, daftar aset, dan daftar ketergantungan backend jelas |
| Naufal | Slide, sumber bukti, uji kegunaan, poster, administrasi TM | Pindahkan outline ke berkas slide editable; cocokkan aset luar repo; buat daftar pertanyaan TM dan logistik | Delapan halaman slide dengan judul/visual/penanggung jawab, status semua aset diketahui atau diberi label belum ditemukan |

Urutan tiga jam malam ini:

1. 30 menit bersama: sepakati kalimat produk, prioritas, dan skenario demo.
2. 90 menit terpisah: Dzaky triase/metrik; Daffa inventaris visual dan UI;
   Naufal membuat kerangka slide dari outline.
3. 45 menit bersama: baca slide dengan suara, periksa klaim dan ketergantungan.
4. 15 menit: tulis hasil, blocker, dan pekerjaan pertama besok.

Pembagian ini belum dikirim kepada anggota melalui aplikasi komunikasi.

## 3. Inventaris bahan yang benar-benar diketahui

| Bahan | Lokasi/bukti | Status dan tindakan | PIC |
|---|---|---|---|
| Rulebook | PDF Downloads yang ditunjuk; salinan daring identik saat audit | Sudah dibaca; final 26 September, TM 22 September; simpan salinan lokal | Naufal |
| Proposal submission | `Anforcom2026_DSDC_trio la albiceleste_Pasang Surut.pdf` di Downloads, 29 halaman | Acuan submission; jangan menimpa; buat lembar koreksi metode terpisah | Dzaky |
| Slide final editable dan PDF | Belum ditemukan berkas yang dapat diidentifikasi sebagai slide final dalam area yang diperiksa | Cek penyimpanan anggota/Canva/Drive; kerangka tersedia di outline; PDF wajib menurut jawaban panitia, deadline belum diketahui | Naufal |
| Poster final | Belum ditemukan artefak final | Buat setelah narasi stabil; kebutuhan ukuran/cetak mengikuti TM | Naufal + Daffa |
| Video penyisihan | [YouTube dari proposal](https://youtu.be/CeXsEN_1Zvk) | Tautan ada; isi/durasi belum diperiksa ulang dalam audit; bukan bukti MP4 cadangan tersedia | Naufal |
| Prototype | [Figma dari proposal](https://www.figma.com/design/EtACxc7jD6wvMJjHh7bq3p/PasangSurut?node-id=1-907) | Tautan ada; cek akses tanpa akun khusus juri | Daffa |
| Enam screenshot historis | `docs/tangkapan/01_peta_genangan.jpg` sampai `06_pita_pasut.png` | Bahan storyboard; ambil ulang setelah perbaikan label dan data | Daffa |
| Diagram arsitektur | `docs/arsitektur.png` | Ada; cocokkan dengan runtime sekarang sebelum masuk slide | Dzaky + Daffa |
| Bukti metode | `docs/validasi.md`, `docs/batasan.md`, `docs/sumber_angka.md`, berkas metrik | Ada; pisahkan evaluasi pasut, eksperimen yang ditolak, asumsi, dan hasil terbaru | Dzaky + Naufal |
| Naskah lama | `docs/demo_script.md` | Naskah penyisihan; perlu koreksi klaim dan durasi; gunakan outline baru sebagai acuan final | Naufal |
| Data demo lokal | `data/processed/potret_demo.json` | API potret pernah lulus 35 tes HTTP; belum bukti dua laptop dan browser berfungsi tanpa Wi-Fi | Dzaky + Daffa |
| Konteks peta lokal | `ruas_jalan.geojson`, `kecamatan.geojson`, `garis_pantai.geojson`, `tujuan_cepat.geojson` | Nama jalan/wilayah/tujuan tersedia; layer label belum tampil | Daffa |
| MP4 demo final | Belum ditemukan artefak yang dapat diidentifikasi | Rekam versi yang sudah stabil pada 24 September; simpan lokal pada dua laptop | Daffa |
| Bukti kehadiran | Konfirmasi Dzaky: panitia menerima, tiga anggota hadir | Simpan bukti korespondensi; tidak perlu mengulang konfirmasi | Naufal |

“Belum ditemukan” berlaku pada berkas yang diperiksa, bukan klaim berkas
tidak ada di seluruh perangkat/akun anggota. Inventaris luar repo tetap
perlu dicocokkan oleh tim. Jangan mencampur video penyisihan dengan video
cadangan final yang harus dapat diputar tanpa internet.

## 4. Prioritas yang dikunci

| Urutan | Pekerjaan | PIC utama | Target internal |
|---|---|---|---|
| P0-A | T0/T3: batasi tumpukan request, ukur RAM, cache terbatas, keputusan kapasitas hosting | Dzaky + Daffa | 21 September; ukur ulang 22 |
| P0-B | T1: retry benar-benar meminta ulang, status galat/pembaruan konsisten | Daffa | 21 September |
| P0-C | T2: cakupan data eksplisit; data hilang bukan kondisi kering | Dzaky | 21–22 September |
| P0-D | T4: model routing yang dapat dipertanggungjawabkan dan regresi pergantian jam | Dzaky | Keputusan 21; implementasi/uji 22 |
| P0-E | Label jalan, wilayah, tujuan dan legenda; demo lokal tanpa jaringan | Daffa | Label 22; dua laptop 23 |
| P0-F | Slide utuh, bukti sumber, koreksi metode, latihan | Naufal, tinjauan Dzaky/Daffa | Versi pertama 21; final internal 24 |
| P1 | Uji tugas 5–8 peserta, poster, dokumentasi, detail saran jam/emisi | Sesuai peran | 23–24; kurangi jika P0 belum selesai |

Tidak menambah model ML, login, wilayah baru, atau migrasi database dalam
scope final. VPS hanya dipilih bila manfaat kapasitas/biaya sepadan dengan
waktu operasionalnya; pembelian belum diputuskan. Perubahan hosting harus
selesai diuji sebelum 23 September, bukan menjelang tampil.

## 5. Urutan 21–24 September

| Hari | Dzaky | Daffa | Naufal | Hasil bersama |
|---|---|---|---|---|
| 21 | Cakupan data, profil RAM, pembatasan kerja backend; keputusan T4/hosting | Retry, pembatasan slider, status data, rancangan geometri statis | Slide versi pertama dan lembar sumber; persiapan uji tugas | Slide bisa dibacakan; perbaikan inti bisa diuji lokal |
| 22 | Integrasi cache/routing; uji regresi dan kinerja | Label peta, kontrak data kecil, uji interaksi | Catat TM, FAQ, sesuaikan ketentuan/deadline | Latihan pertama; solusi teknis dan scope dibekukan |
| 23 | Tutup kegagalan regresi; periksa angka dan metode | Uji HP dan dua laptop tanpa jaringan; screenshot terbaru | Uji tugas, perbaikan narasi, poster bila diperlukan | Satu kandidat versi final dan bukti kegunaan apa adanya |
| 24 | Uji penerimaan dan bekukan kode/data demo | Rekam MP4, paket lokal, salin cadangan | Ekspor PDF, periksa tampilan, inventaris pengiriman | Dua latihan ≤9 menit, satu Q&A 15 menit, paket final tersedia |

Setiap hari: evaluasi 15–30 menit masuk jatah enam jam. Laporkan tiga hal:
hasil yang dapat dibuka, hasil tes relevan, dan blocker berikut pemiliknya.
Jika deadline panitia lebih awal, geser penyelesaian PDF mengikuti panitia.

## 6. Selesai pada level perencanaan vs pekerjaan berikutnya

- [x] Identitas produk dan batas klaim ditulis.
- [x] Pembagian PIC dan urutan kerja disusun.
- [x] Inventaris repo/referensi dan status bahan yang belum ditemukan ditulis.
- [x] Prioritas teknis dan batas scope dikunci dalam rencana.
- [x] Outline slide lengkap dengan waktu, pembicara, visual, dan lampiran dibuat.
- [x] Opsi hosting dibandingkan dengan sumber resmi dan biaya indikatif.
- [ ] Anggota mencocokkan aset di luar repo dan jam kerja pribadi.
- [ ] Metrik/log Render sekitar 17.09 WIB diperiksa untuk akar lonjakan RAM.
- [ ] Kerangka dipindahkan ke aplikasi slide; PDF dan MP4 final belum dibuat.
- [ ] Perbaikan aplikasi diimplementasikan, diuji, dan dideploy.

Pertanyaan TM yang dicatat Naufal: deadline/kanal/nama berkas PDF; apakah
slide boleh direvisi setelah pengumpulan; ukuran layar/resolusi/port; internet
dan listrik meja; ketentuan poster; urutan tampil dan waktu registrasi.
