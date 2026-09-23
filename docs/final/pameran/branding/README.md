# PASANG SURUT — video branding pameran

Versi **1 menit 45 detik**, landscape **1920 × 1080, 30 fps**, MP4 H.264
dengan musik instrumental dan narasi sintetis Bahasa Indonesia. Subtitle
sudah menyatu dengan gambar sehingga video tetap dapat dipahami tanpa suara.
Versi 60 detik di folder induk tetap disimpan.

- [Video siap putar](Pasang_Surut_Branding_105s.mp4)
- [Pemutar lokal dengan loop](putar.html)
- [Storyboard](Storyboard_Branding.jpg)
- [Naskah dan teks layar](naskah.json)
- [Subtitle terpisah](Pasang_Surut_Branding_ID.srt)
- [Hasil verifikasi MP4](verifikasi.json)

Unduh MP4 ke laptop, lalu buka dengan pemutar video dan aktifkan **Repeat**.
Untuk pemutar HTML, simpan `putar.html`, MP4, dan `Poster_Branding.jpg` dalam
folder yang sama. Buka `putar.html`, klik **Putar dengan suara**, lalu **Layar
penuh**. Pemutar mengulang otomatis. Video yang sudah diunduh tidak perlu
internet; QR tetap menuju aplikasi publik yang membutuhkan koneksi.

Uji volume speaker dan keterbacaan dari jarak pengunjung pada perangkat acara.
Gunakan layar kedua bila aplikasi sedang didemokan di laptop utama.

## Alur

| Waktu | Pesan | Visual |
|---|---|---|
| 00:00–00:08 | Kondisi jalan pesisir berubah karena rob | Tipografi besar, motif air dan rute bergerak |
| 00:08–00:16 | Berangkat kapan, lewat mana, biaya memutar | Jam dan kendaraan pengiriman |
| 00:16–00:24 | Perkenalan PASANG SURUT | Nama produk dan tagline |
| 00:24–00:38 | Pilih tujuan, moda, dan waktu | Screenshot aplikasi asli, sorotan kontrol, perbesaran halus |
| 00:38–00:58 | Bandingkan rute dan jam | Rute dari data potret, 08.00 versus 13.00 WIB |
| 00:58–01:10 | Pahami biaya memutar | Tambahan waktu/jarak model dan konteks BBM/CO2 |
| 01:10–01:22 | Cara kerja | Pasut, kerentanan ruas, jaringan OSM, pilihan rute |
| 01:22–01:32 | Langkah pengembangan | Uji pengguna, validasi lapangan, pembaruan data |
| 01:32–01:45 | Ajakan mencoba | Nama produk, tim, QR besar dan alamat aplikasi |

## Sumber dan batas klaim

Visual aplikasi memakai `../../presentasi/aset/demo_08.png`. Graf dan
rute digambar dari potret lokal melalui renderer `../buat_video.py`, bukan
dibuat sebagai rute fiktif. Skenario bertanggal **26 September 2026**, motor,
Tawang–Terboyo. Nilai 13,9 / 7,0 menit, tambahan 6,9 menit / 4,27 km, serta
kedalaman maksimum 24,8 cm dibaca dari `skenario.json`.

Waktu merupakan hasil model, bukan ETA kemacetan. Kedalaman bukan pengukuran
sensor. Rute 08.00 masih memiliki paparan; hasil 13.00 menyebut nol ruas
tergenang **dalam model**, bukan jaminan kering. Narasi pilihan waktu dibatasi
pada jadwal fleksibel. Biaya menunggu belum dihitung. BBM/CO2 berbasis asumsi;
video tidak mengklaim penghematan atau pengurangan emisi kota terukur.
Validasi lapangan dan uji pengguna ditampilkan sebagai rencana.

Lihat [sumber angka presentasi](../../presentasi/sumber_angka.md).
Peta main tetap menjadi tampilan produk; preview CARTO tidak dipromosikan
seolah sudah menjadi versi produksi. Atribusi OpenStreetMap terlihat pada peta.

## Audio

- Narasi: suara sintetis Indonesia `id-ID-ArdiNeural`, Microsoft Edge TTS,
  dibuat melalui [edge-tts](https://github.com/rany2/edge-tts). Bukan rekaman
  atau tiruan suara anggota tim. Naskah yang dikirim hanya isi video publik.
- Musik: komposisi instrumental prosedural 96 BPM yang dibuat pada
  `buat_audio.py`; seluruh nada/ketukan disintesis, tanpa sampel lagu pihak lain.
- Volume musik turun ketika narasi berbunyi. Mix akhir dinormalisasi pada
  target -16 LUFS, batas true peak -1,5 dBTP; nilai hasil ekspor dicatat di
  `verifikasi.json`.
- Teks subtitle mempertahankan ejaan/tanda baca naskah, dengan waktu dari
  metadata kata TTS. Naskah tidak perlu dibaca oleh penjaga stan.

## Membuat ulang

Dari akar repo, setelah dependency frontend dan lingkungan materi tersedia:

```powershell
.venv/Scripts/python.exe -m pip install --target .deploy-local/voice-tools edge-tts==7.2.8
.venv/Scripts/python.exe -m pip install --target .deploy-local/video-tools imageio-ffmpeg==0.6.0
.venv/Scripts/python.exe docs/final/pameran/branding/buat_audio.py
.venv/Scripts/python.exe docs/final/pameran/branding/buat_branding.py --cuplikan --render
.venv/Scripts/python.exe docs/final/pameran/branding/verifikasi_video.py
```

Audio TTS disimpan di `audio/` supaya naskah yang tidak berubah tidak memanggil
layanan kembali. Berkas WAV perantara berada di `.deploy-local/branding/`.
Generator membaca warna dan font proyek; dependency produksi aplikasi tidak
diubah. Animasi untuk video sengaja lebih ekspresif daripada interaksi aplikasi.
