# Data pendukung audit 25 September 2026

[Laporan asal data dan kelayakan jangka panjang](../audit_asal_data_25_september.md)
menjelaskan hubungan sumber dengan dashboard. Berkas di folder ini adalah
bukti audit, bukan input baru untuk produksi.

| Berkas | Isi dan cara membacanya |
|---|---|
| [status_produksi_25_september.json](status_produksi_25_september.json) | Respons publik `/api/kesehatan` dan `/api/jam` pada 25 September. `akhir_eksklusif_utc` adalah batas waktu data, bukan tanggal pengukuran lapangan. |
| [contoh_database_produksi_26_september_08wib.csv](contoh_database_produksi_26_september_08wib.csv) | Dua ruas dari database VPS, dibaca dalam transaksi hanya baca. Ruas 8584 memiliki indeks 0,9802 dan estimasi 39 cm pada 26 September 08.00 WIB; ruas 1 tidak memiliki baris genangan model pada jam tersebut. Kolom kosong bukan pengukuran kering. |
| [ioc_sema_18_25_september_2026.csv](ioc_sema_18_25_september_2026.csv) | 10.020 pengamatan publik sensor tekanan `prs`, disertai hasil harmonik aplikasi pada waktu yang sama. `muka_air_sensor_m` memakai nol sensor; `harmonik_v1_m` memakai acuan model. Bandingkan kolom simpangan setelah masing-masing dikurangi rata-rata tujuh hari. |
| [uji_pasut_independen_25_september.json](uji_pasut_independen_25_september.json) | URL permintaan, hash balasan mentah, model, epoch, offset, jumlah sampel, celah waktu, metrik seluruh periode dan metrik per hari. Per hari memakai rata-rata harian, sehingga tidak sama dengan potongan galat yang memakai rata-rata tujuh hari. |
| [perbandingan_pasut_september.png](perbandingan_pasut_september.png), [PDF](perbandingan_pasut_september.pdf) | Grafik seluruh jendela pengujian, sumbu waktu WIB. Tidak memakai smoothing atau penyetelan ulang. |
| [jadwal_pasang_surut_vps.json](jadwal_pasang_surut_vps.json) | Hasil pemeriksaan entri cron khusus PASANG SURUT serta entri root/timer yang memuat namanya; yang ditemukan hanya backup. Penilaian tidak ada pipeline permanen juga didukung README deploy dan workflow repo. |
| [manifest_berkas_diaudit.json](manifest_berkas_diaudit.json) | SHA-256 dan ukuran 17 input/kode yang diaudit, termasuk GraphML dan raster yang hanya tersedia lokal. Hash bukan verifikasi tahun pengukuran atau mutu ilmiah data. |
| [audit_pasut.py](audit_pasut.py) | Skrip pembandingan yang dapat diulang tanpa menjalankan pipeline atau mengubah parameter pasut. |

Perintah dari akar repo, memakai environment proyek yang sudah berisi
dependency Python backend:

```powershell
.venv\Scripts\python.exe docs\final\data\audit_pasut.py
```

Skrip mengunduh ulang periode tetap 18 September 06.00 UTC–25 September
06.00 UTC. Skrip menyimpan balasan mentah semua sensor di `.deploy-local/`
yang diabaikan Git, kemudian menulis CSV/JSON audit pada folder ini. Data
layanan bisa direvisi, sehingga pengunduhan berikutnya mungkin menghasilkan
hash atau metrik berbeda. Grafik arsip tidak dibuat ulang oleh skrip ini.
Untuk mereproduksi metrik arsip persis, gunakan CSV yang sudah disimpan dan
kode/model pada commit audit. Rumusnya:

```python
import csv
import numpy as np

with open('docs/final/data/ioc_sema_18_25_september_2026.csv') as f:
    rows = list(csv.DictReader(f))
y = np.array([float(r['muka_air_sensor_m']) for r in rows])
p = np.array([float(r['harmonik_v1_m']) for r in rows])
y -= y.mean()
p -= p.mean()
print('Korelasi:', np.corrcoef(p, y)[0, 1])
print('RMSE meter:', np.sqrt(np.mean((p - y)**2)))
```

Sumber pengamatan: Flanders Marine Institute (VLIZ) dan Intergovernmental
Oceanographic Commission (IOC), *Sea level station monitoring facility*,
[DOI 10.14284/482](https://doi.org/10.14284/482), diakses 25 September 2026.
[Metadata sema](https://www.ioc-sealevelmonitoring.org/station.php?code=sema):
Semarang, −6,9479; 110,42012, kontak lokal BIG.

[Kebijakan sumber](https://www.ioc-sealevelmonitoring.org/disclaimer.php)
menyebut data belum melalui quality control dan tidak boleh dipakai untuk
tujuan komersial tanpa menghubungi originator. CSV ini disimpan untuk audit
penelitian; ketersediaan publiknya bukan pemberian izin komersial. Nol sensor
tidak disamakan dengan datum DEMNAS. Tidak ada klaim akurasi genangan per ruas
dari uji pasut ini.
