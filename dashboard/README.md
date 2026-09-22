# dashboard/ — landing page Pasang Surut

Folder statis, terpisah dari `frontend/` (dashboard aplikasinya).
Tanpa build, tanpa dependency: sajikan sebagai situs statis.

```
dashboard/
  index.html   struktur + teks (Bahasa Indonesia)
  styles.css   token visual, nilai warna hanya di :root
  app.js       menu ponsel + pembanding rute + URL dashboard adaptif
  vercel.json  deploy statis opsional
```

## Arah desain

Gaya mengikuti referensi Codera-style yang diminta pengguna, dipadankan
dengan hasil skill (bukan dari UI aplikasi saat ini):

- `ui-ux-pro-max` → style `minimalism-and-swiss-style`, light mode:
  monokrom hitam/putih + satu aksen, tanpa dekorasi berlebih.
- Kartu putih radius besar di atas latar abu hangat, pil hitam tunggal
  sebagai satu-satunya tombol (**Cek Dashboard** — tanpa login/register,
  tanpa tombol sekunder), headline grotesque tengah yang besar.
- Pola `before-after-transformation` (domain `landing`): hero berisi
  pembanding interaktif rute biasa vs rute disarankan — pointer maupun
  keyboard (input range bawaan + tombol panah), diam saat
  `prefers-reduced-motion`.
- `landing-page-design`: formula above-the-fold, CTA pil di header
  lengket (selalu terlihat) + CTA akhir, responsif 375/768/1024.

Keputusan sadar: **tanpa testimoni** — tidak ada kutipan pengguna yang
terverifikasi, dan aturan repo melarang angka/klaim karangan. Bagian
"Hasil yang bicara" diganti kartu validasi jujur (model ditolak +
chart kepentingan fitur asli) dan chips sumber data.

## Menjalankan lokal

```powershell
cd dashboard
python -m http.server 8130
# buka http://127.0.0.1:8130 — tombol "Cek Dashboard" otomatis ke :5173
```

## URL tombol "Cek Dashboard"

| Konteks | Tujuan |
|---|---|
| Dibuka dari `localhost` | `http://127.0.0.1:5173` (Vite dev `frontend/`) |
| Produksi/pratinjau | `/app` pada origin yang sedang dibuka |
| Override | `?dashboard=https://alamat-lain` atau `/app`; hanya HTTP/HTTPS |

Parameter kosong memakai tujuan bawaan, bukan kembali ke landing.
Skema `javascript:` dan `data:` ditolak. Kasus ini diuji di
`frontend/src/landing.test.js`.

## Angka yang dipakai (semua dari proposal)

Korelasi pasut 0,78–0,91 · RMSE 0,10–0,12 m · median persentil
kejadian rob 80,2 · 19.394 ruas · 1.289 km · 72 jam · Rp848 M/tahun
(WRI Apr 2026) · ROC-AUC 0,6579 / PR-AUC 0,0371 / F1 0,0894
(model Sentinel-1 yang ditolak).
