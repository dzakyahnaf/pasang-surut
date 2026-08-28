# Panduan: Earth Engine dan DEMNAS

Dua blokade yang menghentikan M4. Keduanya hanya bisa dikerjakan manual —
saya tidak membuat akun, tidak memasukkan kata sandi, dan tidak menyetujui
syarat layanan atas nama tim.

Seluruh angka dan tautan di halaman ini diverifikasi 25 Agustus 2026, lalu
dikoreksi dan sebagian dikerjakan pada 28 Agustus 2026. Bagian yang sudah
selesai ditandai di tempatnya.

---

## Kenapa ini mendesak — hitung sendiri

Kuota Earth Engine nonkomersial **reset tanggal 1 tiap bulan, tengah malam
waktu Pasifik**. Tanggal 1 berikutnya adalah **1 September 2026**, yaitu
**setelah tenggat lomba 31 Agustus**.

Artinya: **kuota Agustus yang kalian punya sekarang adalah seluruh kuota
yang akan pernah kalian punya sebelum submit.** Tidak ada tambahan.

| Tier | Kuota per bulan | Syarat |
|---|---|---|
| **Community** | **150 EECU-hours** | Tidak ada syarat tambahan. Ini bawaan |
| Contributor | 1.000 EECU-hours | Butuh akun billing aktif |
| Partner | 100.000 EECU-hours | Lamaran terpisah, berhari-hari |

Kuota dihitung **per proyek**, bukan per orang. Tiga orang dengan tiga
proyek berarti 450 EECU-hours. Itu alasan tunggal kenapa ketiganya harus
mendaftar, bukan cuma satu.

> **Koreksi atas Papan Blokade.** A3 sebelumnya saya tulis "Earth Engine
> belum didaftarkan". Itu tidak tepat: cek cakupan Sentinel-1 sudah pernah
> dijalankan dan menghasilkan 723 citra, dan itu mustahil tanpa akses GEE.
> Jadi **minimal satu akun sudah ada.** Yang benar-benar kurang adalah dua
> proyek sisanya. Siapa pun yang menjalankan cek itu, tolong konfirmasi
> Project ID-nya ke tim.

---

## Bagian A — Google Earth Engine

**Dikerjakan oleh: ketiganya, masing-masing.** Sekitar 15 menit per orang.

### A0. Pilih akun Google dulu

Akun pribadi atau akun kampus, keduanya bisa. Satu hal yang perlu diketahui:
pada akun institusi yang dikelola Google Workspace, kalau administrator
menghapus akun, seluruh data Earth Engine ikut terhapus dalam sekitar 30
hari. Dalam rentang enam hari ke depan itu tidak relevan, jadi **pakai yang
mana saja yang paling cepat**. Akun pribadi biasanya lebih sedikit gesekan.

Yang penting: **catat akun mana yang dipakai**, karena Project ID akan
menempel di situ.

### A1. Buka halaman registrasi

<https://console.cloud.google.com/earth-engine>

Halaman ini menggantikan alur manual lama. Jangan mulai dari
code.earthengine.google.com — mulai dari sini.

### A2. Buat project baru

Pilih **Create a new Cloud project** (bukan mendaftarkan project lama,
kecuali kalian memang sudah punya).

**Beri nama yang membedakan pemiliknya**, karena nanti ada tiga:

```
pasang-surut-dzaky
pasang-surut-daffa
pasang-surut-naufal
```

Project ID akan dibuat otomatis dan biasanya berawalan `ee-`. **Salin
Project ID itu** — bukan nama project, tetapi ID-nya. Kode Python nanti
memakainya.

Organization dan Location: pilih **No Organization** kalau memakai akun
pribadi.

### A3. Isi kuesioner kelayakan nonkomersial

Sistem akan menampilkan kuesioner untuk memastikan pemakaian nonkomersial.

Pilih: **Academic or educational institution using Earth Engine for research
or teaching.**

Itu memang benar — kalian mahasiswa ITS mengerjakan lomba akademik. Jangan
memilih opsi komersial, dan jangan mengarang afiliasi.

### A4. Pilih tier

Pilih **Community Tier**.

- 150 EECU-hours per bulan
- **Tidak butuh akun billing sama sekali**
- Bisa diganti kapan saja lewat halaman Manage Tier di Cloud Console

Jangan tergoda Contributor Tier. Kuotanya memang tujuh kali lipat, tetapi
menuntut akun billing aktif, dan aturan proyek ini menetapkan budget Rp0.

### A5. Selesai — akses langsung aktif

Menurut dokumentasi resmi, akses Earth Engine aktif **seketika** setelah
registrasi. Tidak ada masa tunggu berhari-hari seperti sistem lama.

Kalau diminta mengaktifkan API, klik **Enable**.

### A6. Uji lewat Code Editor

Buka <https://code.earthengine.google.com>, tempel ini, klik **Run**:

```javascript
var aoi = ee.Geometry.Rectangle([110.385, -6.995, 110.500, -6.925]);
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filterDate('2015-01-01', '2026-08-25')
  .filter(ee.Filter.eq('instrumentMode', 'IW'));
print('Jumlah citra Sentinel-1 di atas AOI:', s1.size());
```

**Yang harus muncul di Console: 723.**

Kalau angkanya berbeda jauh, kabari saya — berarti ada yang berubah di
arsip sejak pengecekan terakhir, dan `docs/validasi.md` harus dikoreksi.

Kalau muncul galat soal project, pastikan project yang benar terpilih di
pojok kanan atas Code Editor.

**SUDAH DIKERJAKAN 28 Agustus 2026, untuk proyek pertama.**

| | |
|---|---|
| Project ID | **`pasang-surut-anforcom`** |
| Organisasi | `dzakyahnf-org` |
| Status registrasi | "Your Cloud project is registered for non-commercial use" |
| Tier | **Community** |
| Pemakaian EECU bulan ini | **0,07 persen** — kuota praktis masih utuh |
| Hasil uji A6 | **723**, cocok dengan `docs/validasi.md` |

Perhatikan Project ID-nya **tidak** berawalan `ee-`. Itu wajar: awalan `ee-`
hanya muncul kalau ID dibuat otomatis oleh Google. Nama ini ditetapkan
manual sesuai `CHECKLIST_MALAM_INI.md`.

Selagi kredensialnya hidup, seluruh isi `docs/validasi.md` ikut diperiksa
ulang dari sumber: **kedua belas angka per tahun dan kedua arah orbit cocok
seluruhnya.** Tabel itu naik status dari "dilaporkan tim" menjadi
"terverifikasi dari sumber".

**Dua proyek lain — milik Daffa dan Naufal — masih belum ada.** Itu tetap
penting: kuota dihitung per proyek, dan tanpa keduanya jatah tim hanya
sepertiga.

### A7. Sambungkan ke Python

Ini yang membuat pipeline bisa jalan dari repo, bukan dari peramban.

```bash
# dari akar repo, dengan .venv aktif
pip install earthengine-api
earthengine authenticate
```

Perintah `earthengine authenticate` membuka peramban, meminta izin, lalu
menyimpan token di komputer kalian. Setelah itu uji:

```bash
python -c "import ee; ee.Initialize(project='ISI-PROJECT-ID-ANDA'); print(ee.Number(1).add(1).getInfo())"
```

Harus mencetak `2`.

**SUDAH DIKERJAKAN 28 Agustus 2026.** `earthengine-api` 1.7.41 terpasang,
`earthengine authenticate` berhasil dan tokennya tersimpan, dan
`ee.Initialize(project='pasang-surut-anforcom')` berjalan dari venv proyek.
Hitungan 723 juga direproduksi langsung dari Python, bukan hanya dari
peramban.

> **Cakupan izin yang diberikan.** Alur `earthengine authenticate` meminta
> empat cakupan sekaligus: `earthengine`, `cloud-platform`, `drive`, dan
> `devstorage.full_control`. Itu bawaan alat resmi Earth Engine, bukan
> pilihan kita, tetapi cakupan Drive dan Cloud Storage memang luas. Token
> tersimpan di komputer yang menjalankan perintah. Kalau ingin
> mencabutnya nanti, lewat halaman Izin Akun Google.

> **Catatan dependency.** `earthengine-api==1.7.41` kini SUDAH masuk
> `backend/requirements.txt` beserta alasan tertulisnya, sesuai aturan repo.
> Diuji tidak berkonflik dengan 14 paket yang sudah dikunci.
>
> **`geemap` sebaiknya TIDAK dipakai.** Versi terbarunya, 0.38.3, menuntut
> Python 3.12 sementara proyek ini dikunci 3.11. Pip memang akan mundur ke
> 0.37.2 yang masih cocok, tetapi itu menarik lebih dari 70 paket tambahan
> termasuk matplotlib, ipython, ipywidgets, ipyleaflet, folium, dan plotly.
> Pipeline kita mengekspor tabel, bukan menggambar peta di notebook, dan
> untuk menggambar kita sudah punya MapLibre. PLAN.md bagian 4 menyebut
> geemap, tetapi enam hari sebelum tenggat itu risiko tanpa imbalan.

---

## Bagian B — Disiplin kuota, baca sebelum menulis skrip apa pun

150 EECU-hours terdengar banyak sampai satu kesalahan menghabiskannya dalam
satu sore. Empat aturan berikut bukan saran.

**1. Pakai `.limit()` selama bereksperimen.** Sepanjang skrip belum benar,
jalankan pada 5 sampai 10 citra saja. Baru lepas batasnya setelah
keluarannya terbukti benar.

```javascript
var uji = s1.limit(5);   // buang baris ini hanya setelah yakin
```

**2. `scale=20` atau `30`, jangan pernah `10`.** Biaya komputasi tumbuh
kuadratik terhadap resolusi. Turun dari 20 m ke 10 m berarti empat kali
lipat biaya untuk ketelitian yang tidak kita butuhkan — ruas jalan kita
lebarnya belasan meter.

**3. Ekspor tabel, bukan raster.** Yang kita perlukan adalah satu baris per
ruas per citra, bukan gambar. Ekspor raster menghabiskan kuota tanpa
memberi apa pun yang dipakai model.

**4. Pantau pemakaian.** Cloud Console punya halaman pemakaian Earth Engine.
Cek setelah setiap ekspor besar, jangan menunggu kehabisan.

**Kalau kuota satu proyek habis:** ganti ke Project ID anggota lain lewat
`ee.Initialize(project=...)`. Itulah gunanya punya tiga.

---

## Bagian C — DEMNAS

**Dikerjakan oleh: satu orang saja.** Hasilnya dibagikan ke tim.

### C1. Tile yang dibutuhkan sudah diketahui

Saya sudah menanyakannya ke layanan indeks resmi BIG. Hasilnya pasti,
kalian tidak perlu mencari-cari di peta:

| Tile | Cakupan | Perlu? |
|---|---|---|
| **`1409-22`** | bujur 110,25–110,50 · lintang −7,00 sampai −6,75 | **YA — ini saja sudah cukup** |
| `1409-31` | bujur 110,50–110,75 · lintang −7,00 sampai −6,75 | Tidak. Hanya menyentuh garis tepi timur AOI |

AOI kita membentang 110,385–110,500 bujur dan −6,995 sampai −6,925 lintang.
Seluruhnya berada di dalam `1409-22`. Tile `1409-31` muncul di hasil kueri
hanya karena batas timur AOI tepat bersinggungan di 110,500.

**Unduh `1409-22`. Itu saja.**

### C2. Buka portal

<https://tanahair.indonesia.go.id/portal-web/unduh/demnas>

**KOREKSI 28 Agustus 2026.** Panduan ini sebelumnya menunjuk
`tanahair.indonesia.go.id/demnas/` dan menyatakan tautannya hidup karena
mengembalikan HTTP 200. Itu SALAH: alamat itu mengembalikan HTTP 200 dengan
badan KOSONG, `Content-Length: 0`, dan berkasnya terakhir diubah 20
September 2024. Memeriksa kode status saja tidak cukup, isi respons juga
harus dilihat.

Portal yang sebenarnya hidup adalah **Ina-Geoportal**, aplikasi React di
`/portal-web/unduh`. Kartu yang dicari bernama **Data Demnas**.

### C3. Registrasi

Gratis. Isi formulir pendaftaran, lalu masuk. Setelah masuk, nama Anda
muncul di kanan atas.

### C4. Cari dan unduh

Pada peta pemilih tile, klik kotak **`1409-22`**. Popup akan menawarkan
tombol **UNDUH DEMNAS_1409-22_v1.0.tif**. Pastikan nama berkas di tombol
benar-benar memuat `1409-22` sebelum diklik — tile tetangga `1409-21`
letaknya persis di sebelah barat dan mudah tertukar.

Pastikan pula yang dipilih **Demnas**, bukan **Batnas** — Batnas adalah
batimetri, kedalaman laut, dan kita tidak memerlukannya.

**SUDAH DIKERJAKAN 28 Agustus 2026.** Berkasnya sudah diunduh dan
diverifikasi. Lihat C7.

Spesifikasi yang akan kalian dapat:

- Resolusi 0,27 arc-second, sekitar 8 meter
- Datum vertikal **EGM2008**
- **RMSE vertikal 2,79 m** — ingat angka ini, ia yang membuat kita dilarang
  memakai ambang elevasi absolut

### C5. Simpan di tempat yang benar

```
data/raw/DEMNAS_1409-22_v1.0.tif
```

`data/raw/` sudah masuk `.gitignore`, dan `*.tif` juga. **Jangan pernah
memaksa meng-commit berkas ini** — aturan repo nomor 8 melarangnya, dan
ukurannya akan membengkakkan repo.

Bagikan ke anggota lain lewat Google Drive atau WhatsApp, bukan lewat git.

### C6. Clip ke AOI segera setelah diunduh

Jangan mengolah tile penuh. Tile `1409-22` menutupi 0,25 × 0,25 derajat,
sekitar 27 × 27 km, sementara AOI kita hanya 12,7 × 7,7 km. Mengolah tile
penuh berarti membuang waktu dan memori untuk area yang tidak dipakai.

### C7. Hasil verifikasi berkas, 28 Agustus 2026

Berkas sudah ada di `data/raw/DEMNAS_1409-22_v1.0.tif`, 43 MB, dan sudah
diperiksa dengan rasterio:

| | |
|---|---|
| Ukuran | 3.333 × 3.333 piksel, satu band, float32 |
| Cakupan | bujur 110,2500–110,5000 · lintang −7,0000 sampai −6,7500 |
| Menutupi seluruh AOI | **ya** |
| Resolusi | 0,00007501 derajat, sekitar 8,35 m |
| Nodata | NaN |
| Piksel valid di dalam AOI | 1.430.289 dari 1.430.289, yaitu 100 persen |
| Elevasi di dalam AOI | minimum −1,15 m · median **2,60 m** · maksimum 55,95 m |
| Persentil ke-25 | **0,16 m** |

Angka terakhir itu layak masuk proposal: **seperempat wilayah pilot berada
di bawah 0,16 meter.** Itulah alasan fisik kenapa rob melumpuhkan kawasan
ini. Sekaligus penegasan kenapa ambang elevasi absolut tidak sah — RMSE
vertikal DEMNAS 2,79 m jauh lebih besar daripada sebaran elevasi yang
sedang dibedakan.

> **JEBAKAN YANG WAJIB DIINGAT DI M4: berkas ini TIDAK membawa CRS.**
> `rasterio` melaporkan `CRS: None`. Koordinatnya jelas derajat WGS84 —
> cakupannya persis cocok dengan indeks tile — tetapi tidak dideklarasikan
> di dalam berkas. Setiap kali berkas ini dibuka, CRS harus ditetapkan
> secara eksplisit, misalnya lewat parameter `crs` saat membuka atau dengan
> menulis ulang berkasnya. Kalau dilewatkan, proyeksi dan pengambilan
> sampel akan gagal atau, lebih buruk, diam-diam salah.

### C7. Kalau registrasi DEMNAS macet

Ada jalan cadangan yang **tidak butuh registrasi sama sekali**: Copernicus
DEM GLO-30 dan SRTM sudah tersedia langsung di dalam Earth Engine.

Resolusinya lebih kasar, 30 meter berbanding 8 meter, dan itu harus ditulis
jujur di `docs/batasan.md`. Tetapi model yang jalan dengan DEM 30 meter jauh
lebih baik daripada model yang tidak pernah jalan karena menunggu
registrasi. **Jangan biarkan DEMNAS memblokir M4 lebih dari satu hari.**

---

## Bagian D — Yang harus dikabarkan balik ke saya

Setelah selesai, kirim ini supaya M4 bisa langsung dimulai:

- [x] ~~Project ID pertama~~ — **`pasang-surut-anforcom`**, Community tier
- [x] ~~Angka uji A6~~ — **723**, cocok
- [x] ~~`earthengine authenticate`~~ — berhasil, diuji dari Python
- [x] ~~Berkas DEMNAS `1409-22`~~ — ada di `data/raw/`, 43 MB, terverifikasi
- [ ] **Project ID Daffa** — belum ada
- [ ] **Project ID Naufal** — belum ada

Dua baris terakhir itu satu-satunya yang tersisa di halaman ini.

Begitu daftar ini lengkap, yang bisa saya kerjakan berikutnya adalah skrip
ekstraksi label Sentinel-1 dan skrip sampling DEM ke tiap ruas — dua bahan
utama model M4.

---

## Sumber

- [Earth Engine Noncommercial Tiers](https://developers.google.com/earth-engine/guides/noncommercial_tiers) — angka kuota tiap tier
- [Earth Engine access](https://developers.google.com/earth-engine/guides/access) — alur registrasi dan status billing
- [Earth Engine quotas](https://developers.google.com/earth-engine/guides/usage) — waktu reset kuota
- [Indeks DEM Nasional, BIG](https://geoservices.big.go.id/rbi/rest/services/INDEKS/DEM_Nasional/MapServer) — sumber nama tile `1409-22`
- [Portal DEMNAS](https://tanahair.indonesia.go.id/demnas/)
