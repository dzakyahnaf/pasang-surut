# Video pameran PASANG SURUT

Motion design **60 detik** untuk diputar berulang di meja pameran final,
23 September 2026. Tanpa suara, karena ruang pameran bising dan video harus
tetap bercerita tanpa penjaga.

| | |
|---|---|
| Berkas | `Pasang_Surut_Pameran.mp4` |
| Format | MP4 H.264, 1920 × 1080, 30 fps, tanpa trek audio, 7,5 MB |
| Diperiksa | 1.800 bingkai; QR pada bingkai MP4 terbaca ke `https://pasang-surut.vercel.app/app`; bingkai transisi ditinjau |
| Ujung | Bingkai pertama dan terakhir sama-sama gelap, jadi pengulangan tidak terlihat patah |

## Cara memutar

- **Laptop:** buka dengan VLC, aktifkan *Loop* (tombol ulang sampai ikon
  berangka satu hilang), lalu layar penuh dengan F. Windows Media Player
  juga bisa, pilih *Repeat*.
- **TV lewat flashdisk:** hampir semua TV memutar MP4 H.264. Cari opsi
  *Repeat* atau *Ulangi* di pemutar media TV. Uji sebelum hari H.
- Laptop yang memutar video jangan dipakai untuk demo, karena aplikasi dan
  video bersaing merebut perhatian juri di layar yang sama.

## Isi, per adegan

| Detik | Adegan | Yang dilihat pengunjung |
|---|---|---|
| 0–6 | Pembuka | "Berangkat kapan, lewat mana?" dan papan duga air yang naik ke tinggi pasut Sab 26 pukul 08.00 |
| 6–15 | Pita Pasut | Kurva pasut 72 jam digambar, jam berisiko diarsir merah, jam aman ditandai hijau |
| 15–28 | Peta per ruas | 19.394 ruas; Pita bergeser 00.00 ke 08.00 dan ruas pesisir terisi air sampai 1.043 ruas |
| 28–44 | Rute | Tawang ke Terboyo, motor: rute biasa lawan rute disarankan pada 08.00, lalu Pita digeser ke 13.00 dan kedua rute menyatu |
| 44–52 | Cara kerja | Kapan dari pasut harmonik, di mana dari indeks kerentanan, lewat mana dari graf OSM; model Sentinel-1 yang tidak dipakai |
| 52–60 | Penutup | Nama, tagline, QR ke `/app`, tim, dan batas klaim |

## Dari mana setiap angka

Tidak ada angka yang diketik tangan. Generator membacanya dari berkas yang
sama dengan aplikasi dan paket presentasi, dengan batas klaim
[sumber_angka.md](../presentasi/sumber_angka.md):

| Angka di video | Sumber |
|---|---|
| 19.394 ruas, 173 ruas pukul 04.00, 1.043 ruas pukul 08.00, 0 ruas pukul 13.00 | `data/processed/potret_demo.json` |
| Kurva dan tinggi pasut (+0,23 m pukul 08.00) | `backend/app/domain/pasut.py`, diperiksa cocok dengan nilai per jam di potret sebelum video dibuat |
| 7,0 dan 13,9 menit; 6,32 dan 10,58 km; 29 dan 14 ruas; +6,9 menit; +4,27 km; 24,8 cm | `docs/final/presentasi/aset/skenario.json` |
| r 0,78 dan RMSE 0,12 m | `data/referensi/kalibrasi_pasut.json`, seperti dikutip `sumber_angka.md` |

Kalimat kejujuran yang sengaja ikut tampil: lencana "INDEKS KERENTANAN —
BUKAN PREDIKSI GENANGAN", "Kedalaman adalah estimasi, bukan hasil pengukuran
langsung", "Skenario potret 26 September 2026", "Itu kecocokan pasut, bukan
akurasi genangan", dan "Alat bantu perencanaan perjalanan, bukan peringatan
dini resmi". Rute disarankan pukul 08.00 yang masih menembus genangan
24,8 cm juga ditampilkan apa adanya.

## Membuat ulang

```powershell
# sekali, dari akar repo: encoder dipasang di luar runtime aplikasi
.\.venv\Scripts\python.exe -m pip install --target .deploy-local/video-tools -r docs/final/pameran/requirements-video.txt

# PNG uji pada detik tertentu, untuk diperiksa sebelum encoding penuh
.\.venv\Scripts\python.exe docs/final/pameran/buat_video.py --cuplikan 3,11,25,36,43,56

# video penuh, beberapa menit
.\.venv\Scripts\python.exe docs/final/pameran/buat_video.py
```

Jalankan ulang bila potret, skenario demo, atau warna token berubah. Jangan
menyunting MP4 langsung: angka di dalamnya harus tetap bisa ditelusuri ke
berkas sumber.

Visual mengikuti [DESIGN.md](../../../DESIGN.md): badan instrumen gelap,
jendela peta terang, tangga kedalaman dengan pola titik untuk kelas dalam,
rute ambar bergaris luar gelap, dan Pita Pasut sebagai satu-satunya gradien.
Dua penyesuaian untuk layar pameran yang dilihat dari dua sampai tiga meter:
garis rute ditebalkan 1,5 kali, dan rute biasa diberi garis luar gelap
seperti rute disarankan. Tanpa garis luar itu, abu-abu terang rute biasa
hilang di atas jalan abu-abu gelap.
