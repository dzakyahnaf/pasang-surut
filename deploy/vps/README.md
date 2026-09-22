# PASANG SURUT pada VPS bersama

Status 22 September: API, frontend, dan PostGIS **aktif di produksi** melalui
`https://pasang-surut.vercel.app`. Origin sementara `0.0.0.0:18080` dibuka
dengan izin Dzaky; Vercel–origin memakai HTTP. Direktori runtime masih
bernama `staging` untuk mempertahankan jalur dan volume yang sudah diuji.
Lihat [hasil publikasi](../../docs/final/publikasi_dan_label_22_september.md).

Proyek Docker Compose `pasang-surut` memakai direktori, jaringan, volume,
akun database, dan port sendiri. Jangan menjalankan perintah Compose dari
direktori Maknaprice, mengubah container/Caddy/database Maknaprice, atau
menjalankan pembersihan Docker global. Caddy PASANG SURUT adalah container
baru; port 80/443 milik layanan lama tidak digunakan.

## Lokasi dan akses privat

Runtime berada di `/opt/pasang-surut/staging`; backup di
`/opt/pasang-surut/backups`. Direktori induk mode 700 dan env rahasia mode
600. Sumber lokal `.deploy-local/` diabaikan Git. Jangan menyalin env atau
backup ke repo, output command publik, maupun build context.

Dari laptop dengan kunci yang sudah terdaftar:

```sh
ssh -i ~/.ssh/bermakna_vps -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o ExitOnForwardFailure=yes -N -L 127.0.0.1:18080:127.0.0.1:18080 root@38.103.171.82
```

Buka `http://127.0.0.1:18080`. Perintah berjalan sampai dihentikan; tunnel
hanya perlu satu kali. Fingerprint host harus sesuai yang sudah diverifikasi
sebelumnya. Jangan menonaktifkan pemeriksaan host key.

## Konfigurasi yang aktif

`compose.yml`: API 320 MiB/0,8 CPU, DB 192 MiB/0,35 CPU, web 48 MiB/0,15 CPU,
satu worker API, BLAS/OMP/MKL satu thread, tanpa swap tambahan container.
Database tidak memiliki port host. Compose network dan volume dimiliki
project `pasang-surut`. API memakai akun SELECT-only dengan transaksi
read-only; pekerjaan migrasi menggunakan akun admin berbeda.

File di staging yang **tidak ada di Git**:

- `.env`: `PASANG_RELEASE` dan `PASANG_BIND=0.0.0.0`, bukan password.
  Default template Compose tetap loopback supaya instalasi baru tidak
  terbuka ke publik tanpa pengaturan eksplisit.
- `db.env`: kredensial admin database PASANG SURUT.
- `api.db.env` dan aktif `api.env`: DSN akun baca database internal.
- `api.potret.env`: DSN kosong eksplisit untuk rollback potret.
- `migration.env`: kredensial pekerjaan migrasi khusus PASANG SURUT.

Image aktif `pasang-surut-api:21sep-d76a27388461`. Batas RAM 320 MiB adalah
penyesuaian konfigurasi setelah image dibuat. Jangan menganggap tag image
sebagai hash konfigurasi Compose terbaru.

Periksa keadaan tanpa mencetak nilai env:

```sh
cd /opt/pasang-surut/staging
docker compose --profile database ps
curl -fsS http://127.0.0.1:18080/api/kesehatan
docker stats --no-stream pasang-surut-api-1 pasang-surut-db-1 pasang-surut-web-1
free -m
```

Health harus menyatakan `database: true`, `data_tersedia: true`, serta
cakupan waktu yang sesuai. `database: false` dapat berarti fallback potret;
periksa `asal_jaringan` dan cakupannya, bukan hanya HTTP 200.

## Build dan pembaruan

Build frontend dari direktori `frontend`, lalu paket dari akar repo:

```sh
npm run build:vps
```

```sh
python deploy/vps/buat_paket.py
```

Script build menetapkan `VITE_API_URL` kosong di Node, termasuk pada Windows
PowerShell, supaya browser meminta `/api` pada origin yang sama. Paket
allowlist memuat runtime, data minimum, build frontend, dan konfigurasi
nonrahasia. Hasil `runtime.tar.gz` dan manifest SHA-256 berada di
`.deploy-local/`. Prefix `21sep` pada tag adalah nama keluarga rilis awal,
bukan jaminan tanggal build; gunakan hash manifest untuk identifikasi.

Transfer via SFTP ke direktori PASANG SURUT. Simpan salinan rilis lama dan
ekstrak paket ke direktori calon rilis sebelum mengganti runtime. Pertahankan
file env remote. Gunakan LF untuk shell script. Dockerfile berada pada
`backend/Dockerfile`; context adalah akar paket.

Build Linux sebelumnya dijalankan memakai builder `pasang-build` khusus,
dibatasi 384 MiB dan 0,8 CPU. Builder itu dihentikan setelah build, tidak
dijadikan builder default. Jangan build tanpa batas atau mengganti builder
Maknaprice. Setelah mengganti image hanya buat ulang API; mengganti aset
frontend cukup pada mount frontend PASANG SURUT. Uji sebelum mengalihkan
pengguna. Hindari penyalinan aset sebagian ketika sudah melayani publik.

`frontend/scripts/build-proxy.mjs` sudah aktif pada Vercel. Aturan `/`
secara eksplisit menuju index VPS, diikuti wildcard aset/API. Cache API
dinonaktifkan. Build Vercel tidak membangun frontend aplikasi; setiap
perubahan UI harus melalui `npm run build:vps` dan deploy aset ke VPS.
Push Git saja belum mengganti aset yang sedang disajikan Caddy VPS.

Rilis aset label saat publikasi: `label-a29a25013940`. Upload aset dengan nama
hash baru dahulu dan pertahankan aset lama, lalu ganti `index.html` secara
atomik dalam direktori mount. Backup sebelum perubahan ada di
`/opt/pasang-surut/backups/frontend-before-label-a29a25013940.tar.gz`.
Service worker produksi v3 memakai network-first untuk HTML, tidak menyimpan
API, dan menghapus cache cangkang versi sebelumnya.

## Migrasi dan publikasi data

`impor_dan_uji.py` khusus bootstrap database PASANG SURUT yang kosong.
Script memverifikasi lima tabel terhadap manifest ekspor, menjalankan
migrasi metadata, dan menguji transaksi publikasi. **Jangan jalankan ulang
pada database aktif yang sudah diisi.** Ekspor source memakai snapshot
read-only dan tidak memodifikasi Supabase.

`publikasi_awal.py` menerbitkan ulang prediksi dari pemicu yang sudah
disalin, paling jauh 14 hari, melalui script 11. Ini pekerjaan bootstrap
final, bukan scheduler pembaruan permanen. Pipeline dan dependency data
tambahan dijalankan dalam container sementara terbatas, bukan dipasang ke
image API. Rencana setelah final: perbarui pemicu, publikasikan prediksi
beserta metadata secara atomik, dan periksa cakupan melalui API.

Runtime memeriksa versi dataset setiap 60 detik. Bila jaringan jalan
diganti, restart **API PASANG SURUT** supaya graf database dimuat ulang.
Jangan hanya mengganti tanggal metadata untuk memperpanjang data lama.

## Backup dan rollback

Job `/etc/cron.d/pasang-surut-backup` memanggil `/opt/pasang-surut/backup.sh`
pukul 03.20 WIB setiap hari. Lihat `/opt/pasang-surut/backup.log`; job menunda
ketika RAM host terlalu rendah. Periksa log agar penundaan tidak terlewat.
Backup manual yang sama:

```sh
/opt/pasang-surut/backup.sh
```

Format custom `pg_dump`, diverifikasi dengan `pg_restore --list`. Pemulihan
telah diuji ke database baru di container PASANG SURUT, dengan jumlah ruas,
prediksi, dan jam lengkap cocok. Untuk menguji ulang, buat database uji baru,
restore dengan `--no-owner --no-acl`, verifikasi isi, lalu hapus hanya database
uji itu. Jangan restore menimpa database aktif atau database Maknaprice.

Salin backup ke laptop setelah pembaruan data. Backup harian masih berada
pada disk VPS; belum ada sinkronisasi backup luar server. Pantau disk karena
belum ada retensi penghapusan otomatis. Backup sebelum publikasi juga
dipertahankan untuk audit.

Rollback ke potret pada **PASANG SURUT saja**:

```sh
cd /opt/pasang-surut/staging
cp api.potret.env api.env
chmod 600 api.env
docker compose up -d --no-deps --force-recreate api
curl -fsS http://127.0.0.1:18080/api/kesehatan
```

Pastikan potret masih berlaku dan jam demo termasuk cakupannya. Kembali ke
database dilakukan dengan menyalin `api.db.env` ke `api.env` dan membuat ulang
API dengan cara yang sama. File sumber potret untuk final berlaku 26–28
September; tidak melayani jam lain seolah-olah kering.

Jika host kekurangan RAM atau Maknaprice terpengaruh, hentikan hanya
container PASANG SURUT:

```sh
cd /opt/pasang-surut/staging
docker compose --profile database stop api web db
```

Jangan memakai `down -v`, global prune, atau menghentikan Docker daemon.
Rollback pengguna memakai deployment Vercel sebelum pengalihan atau build
frontend lama yang kompatibel. Render dan Supabase sumber dipertahankan sampai gladi
selesai dan ada keputusan penghentian terpisah.

## Alat verifikasi

`ukur_api.py` hanya mengukur loopback; `uji_browser.py` menguji retry dan
slider pada build produksi. `pantau.py` mengambil sampel RAM host, status
container, dan HTTP Maknaprice. Guard menghentikan **PASANG SURUT saja** bila
RAM tersedia di bawah 350 MiB pada dua sampel berturut-turut atau Maknaprice
gagal tiga sampel. Guard itu respons darurat, bukan jaminan isolasi sempurna
pada host bersama.

```sh
python3 /opt/pasang-surut/pantau.py --menit 45 --out /opt/pasang-surut/monitor-baru.jsonl
```

Simpan log mentah host secara privat. Repo hanya memuat ringkasan yang
tidak mengekspos identitas container layanan lain. Pengujian yang sudah
lulus tidak perlu diulang sebagai beban rutin pada layanan publik.
