# Sumber angka — provenans lengkap

Berkas ini memuat asal-usul penuh setiap angka yang dikutip proposal, termasuk
yang **tidak** berhasil ditemukan sumbernya. Proposal hanya memuat sitasi
ringkasnya, karena batas 30 halaman.

Ditelusuri 30 Agustus 2026.

---

## 1. Baseline dampak WRI — Rp848 miliar per tahun

**Dipakai di:** Abstrak, Bagian 3.2, Bagian 11.1, seluruh Bagian 11.
**Rujukan proposal:** [2]

Angkanya berasal dari paparan **Afrizal Ma'arif**, Sustainable Mobility Analyst
WRI Indonesia, pada diskusi WRI Indonesia *"Mengelola Risiko Banjir: Politik
Kebijakan, Tata Ruang, dan Adaptasi Kota-kota Pesisir di Indonesia"*, Rabu
8 April 2026.

| Sumber | Yang tertulis |
|---|---|
| Suara.com, 9 April 2026 | "Sekitar 10 persen jaringan jalan di Semarang, setara dengan 11 persen aktivitas mobilitas masyarakat, berpotensi terdampak banjir rob." dan "total kerugian akibat terganggunya transportasi di Semarang mencapai sekitar Rp848 miliar per tahun." |
| Forum Kajian Pembangunan (ringkasan diskusi) | "sekitar 11% jaringan jalan (±569 km) berada dalam kondisi rentan"; "waktu tempuh melonjak hingga dua kali lipat"; "biaya logistik naik sekitar 30–40%" |

Tautan:
- suara.com/news/2026/04/09/165500/banjir-rob-di-semarang-bikin-tekor-rp848-miliar-akibat-bagaimana-cara-mengatasinya
- fkpindonesia.org/summary-report/mengelola-risiko-banjir

### Dua hal yang wajib disebut

**Pertama, ini sumber sekunder.** Laporan riset primer WRI belum terbit, atau
setidaknya tidak ditemukan. Yang dikutip adalah pemberitaan atas sebuah
paparan. Kalau juri menanyakan laporan aslinya, jawabannya adalah: belum ada,
dan itu sudah kami catat.

**Kedua, kedua sumber sekunder TIDAK sepenuhnya cocok.** Suara.com menulis
10 persen jaringan jalan dan 11 persen aktivitas mobilitas; ringkasan FKP
menulis 11 persen jaringan jalan setara ±569 km. Proposal memakai rumusan
Suara.com karena ia mengutip paparan secara langsung dan memuat angka
rupiahnya. Angka ±569 km dari FKP tidak dipakai di mana pun.

Ringkasan FKP juga memuat dua angka yang **tidak** kami pakai tetapi berguna
kalau nanti dibutuhkan: waktu tempuh melonjak dua kali lipat, dan biaya
logistik naik 30–40 persen.

---

## 2. Leptospirosis Kota Semarang — 32 kasus (2024), 59 kasus (2025)

**Dipakai di:** Bagian 3.4.
**Rujukan proposal:** [9]

Dikutip dari **Abdul Hakam**, Kepala Dinas Kesehatan Kota Semarang, oleh
sekurangnya tiga media: Beritajateng.id, Tribun Jateng, dan JPNN Jateng.

| Tahun | Kasus | Meninggal |
|---:|---:|---:|
| 2023 | tidak disebut | 10 |
| 2024 | **32** | 5 |
| 2025 | **59** | 8 |

Angka tambahan dari pemberitaan yang sama: uji petik Dinkes 2025 menemukan
sekitar **30 persen tikus dan celurut** membawa bakteri *Leptospira*.

**Yang tidak berhasil dilakukan.** Publikasi data primer Dinas Kesehatan Kota
Semarang tidak dapat diakses — halaman beritajateng.id dan Tribun Jateng
menolak permintaan otomatis (HTTP 403), dan situs Dinkes tidak memuat tabel
yang bisa dikutip langsung. Angkanya konsisten di tiga media yang mengutip
pejabat yang sama, dan itulah dasar kepercayaannya. Bukan data primer.

---

## 3. Faktor emisi — bensin 2,31 dan solar 2,67 kg CO2 per liter

**Dipakai di:** tabel `ambang_moda`, panel dampak di antarmuka, Bagian 11.3.
**Rujukan proposal:** [10]

Bukan angka kutipan, melainkan **hasil hitungan dengan cara baku IPCC**:

```
faktor emisi per liter = faktor emisi per satuan energi x nilai kalor per liter
```

| Bahan bakar | Faktor IPCC | Nilai kalor | Hasil |
|---|---:|---:|---:|
| Solar | 74.100 kg CO2/TJ | 36 x 10^-6 TJ/liter | **2,668** |
| Bensin | 69.300 kg CO2/TJ | ~33 x 10^-6 TJ/liter | **2,29–2,31** |

Sumber: IPCC, *2006 Guidelines for National Greenhouse Gas Inventories*,
Volume 2 (Energy), Tabel 1.4. Nilai kalor solar mengikuti acuan KLHK.

### Batas yang jujur, dan arahnya menguntungkan

Keduanya faktor **bahan bakar murni**. DEFRA 2026 memakai angka lebih rendah —
bensin 2,075 dan solar 2,584 kg CO2e per liter — karena bahan bakar Inggris
dicampur biofuel.

Indonesia menjalankan mandat biodiesel, sehingga faktor solar yang sesungguhnya
berlaku **kemungkinan lebih rendah** dari 2,68. Artinya angka yang dipakai
proposal ini konservatif ke atas: ia **melebihkan** emisi, bukan mengecilkannya.
Kalau ada yang mengoreksi, koreksinya akan menurunkan angka kami, bukan
menaikkannya. Itu arah kesalahan yang aman untuk sebuah klaim dampak.

---

## 4. Konsumsi bahan bakar per kilometer

**Dipakai di:** tabel `ambang_moda`, panel dampak di antarmuka.
**Rujukan proposal:** [11]

| Moda | Nilai | Setara | Status |
|---|---:|---:|---|
| Motor | 0,020 liter/km | 50 km/liter | **bersitasi** |
| Mobil | 0,090 liter/km | 11,1 km/liter | **BELUM bersitasi** |
| Truk | 0,250 liter/km | 4 km/liter | **BELUM bersitasi** |

Untuk motor, 50 km/liter berada di dalam rentang angka pabrikan skuter yang
lazim dipakai di Indonesia:

| Model | Konsumsi |
|---|---|
| Honda BeAT | 55–60 km/liter |
| Honda Supra X 125 FI (2025) | 61,8 km/liter |
| Suzuki Nex II | 44–49 km/liter |

Sumber: Kompas Otomotif dan situs resmi dealer Honda, ditelusuri 30 Agustus
2026. Nilai 50 km/liter berada **di bawah** ketiganya, jadi konsumsi motor pun
cenderung dilebihkan sedikit — kembali ke arah yang aman.

**Yang tidak ada.** Tidak ditemukan rata-rata nasional resmi yang diterbitkan
pemerintah untuk konsumsi bahan bakar per kilometer, baik motor maupun mobil.
AISI menargetkan 1 liter per 100 km untuk motor ICE pada 2029–2030, tetapi itu
target masa depan, bukan rata-rata sekarang.

**Angka mobil dan truk tetap asumsi rancangan** dan ditulis begitu di Bagian 5
butir 8. Jangan diisi angka lain tanpa sumber.

---

## Yang masih kosong, dan sudah diputuskan tidak dikejar

| Angka | Di mana | Keputusan |
|---|---|---|
| Panjang jaringan jalan Kota Semarang | 11.2 | Boleh kosong. Bagian 11.5 berdiri tanpanya |
| Perjalanan terdampak per hari | 11.2 | Boleh kosong. Justru alasan nilai rupiah TIDAK dihitung |
| Normal hujan BMKG | 5.6 | Boleh kosong. Hanya pembanding, bukan dasar klaim |
| Tingkat adopsi | 11.2 | **Bukan** TODO(sumber). Ini asumsi dan wajib tetap ditulis sebagai asumsi |

---

## Cara memakai berkas ini

Kalau juri menanyakan satu angka, cari di sini lebih dulu. Setiap bagian
menyebut dengan jelas mana yang dikutip, mana yang dihitung, dan mana yang
masih asumsi. Tidak ada angka di proposal yang tidak muncul di salah satu dari
tiga kategori itu.
