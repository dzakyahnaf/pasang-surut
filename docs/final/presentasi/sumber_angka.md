# Sumber angka dan batas klaim

Semua angka deck dapat dilacak ke berkas di repo. Ini paket materi 23
September 2026, dengan audit backend 22 September pada main `1651ad3` dan
koreksi panel/frontend 23 September `c554e27`. Tidak ada angka wawancara,
testimoni, adopsi, penghematan kota, atau kemitraan yang dikarang.

| Slide | Bukti | Interpretasi dan batas |
|---|---|---|
| 1–3, 9–10 | `data/processed/tujuan_cepat.geojson`, `ruas_jalan.geojson`, `garis_pantai.geojson`; [aset](aset/) | Lokasi OSM dan akses hasil pelekatan ke graf. Bukan verifikasi pintu masuk bangunan. Peta utama tetap peta lokal berlabel. Basemap CARTO/OSM masih branch pratinjau terpisah. |
| 3, 6, 9–10 | [skenario.json](aset/skenario.json) | Respons aktual API lokal: motor, 26 Sep 08.00/13.00 WIB, versi potret `919aa345-7492-4a53-9e7c-c34086775d18`. Waktu dan kedalaman dari model, bukan observasi/ETA lalu lintas. |
| 4, 12 | `backend/app/domain/kerentanan.py`, `routing.py`, `runtime.py` | 19.394 ruas; tiga fitur bobot sama; grid 3×3 sisi500m; kondisi keberangkatan tetap selama satu pencarian. Tidak mengklaim optimalitas dinamis. |
| 5, 11 | `data/referensi/kalibrasi_pasut.json`, `docs/validasi.md` §3.1 | Pada WIB, 10 hari: r0,7821, RMSE0,1155m, 12.317 rekaman. Jendela sama ikut memilih acuan waktu; bukan uji independen. Jendela2/4/7hari saling bertumpang tindih. |
| 5, 13 | [audit 22 September](../audit_regresi_22_september.md), [koreksi panel](../koreksi_panel_23_september.md) | 95 tes backend Windows/Linux. 25 frontend saat audit, menjadi26 setelah koreksi panel. Lulus tes tidak berarti bebas seluruh bug. |
| 6, 14 | `backend/app/domain/dampak.py`, `aset/skenario.json` | Motor0,020L/km; konsumsi±30%; faktor2,31kgCO₂/L. Asumsi rilis. Sitasi faktor belum lengkap, `data/referensi/faktor_emisi.json` masih null. Rentang bukan interval kepercayaan. |
| 7 | Rencana tim pada outline final | Target5–8 peserta adalah rencana uji tugas; belum ada hasil uji kegunaan atau mitra aktif yang diklaim. |
| 12 | `data/referensi/metrik_model.json` | Eksperimen Sentinel-1: ROC-AUC0,6579, PR-AUC0,0371, F1 0,0894, dasarPR0,016. Model eksperimen tidak dipakai sebagai prediktor rilis. |
| 13 | [telemetri audit](../bukti/audit_regresi_22_verifikasi.json), [request audit](../bukti/audit_regresi_22_requests.json) | 412 request/94,47detik, 0OOM/restart dalam jendela uji, 32 respons sibuk terkendali. Puncak sampel berbeda dari uji beban sebelumnya; bukan kapasitas maksimum atau jaminan uptime. |

## Angka skenario potret

| Jam WIB | Jenis | Menit model | Kilometer | Ruas tergenang dalam model | Maksimum model pada rute |
|---|---|---:|---:|---:|---:|
| 08.00 | Pembanding mengabaikan genangan | 7,0 | 6,32 | 29 | 28,7cm |
| 08.00 | Sadar rob | 13,9 | 10,58 | 14 | 24,8cm |
| 13.00 | Sadar rob = pembanding | 7,0 | 6,32 | 0 | 0cm |

Selisih08.00 dihitung sebelum pembulatan tampilan: +6,9menit, +4,27km,
BBM+0,060–0,111L, CO₂+0,138–0,256kg. Karena pembulatan, pengurangan angka
jarak yang ditampilkan (10,58−6,32) dapat berbeda0,01km dari keluaran selisih.
Rute08.00 masih berisiko menurut ambang model motor;13.00 tidak membuktikan
jalan kering. Jumlah ruas bukan ukuran risiko kesehatan atau lama paparan.
Menunggu lima jam juga punya biaya jadwal yang belum dimodelkan.

## Kalimat yang dipertahankan saat menjawab juri

- Produk membantu perencanaan dan perbandingan perjalanan; belum menjadi
  peringatan dini resmi atau jaminan keselamatan.
- Korelasi pasut bukan persentase akurasi dan bukan akurasi genangan jalan.
- Median3×3 sel sisi500m, bukan radius500m.
- Runtime memakai kondisi jam keberangkatan, bukan kondisi saat tiba di
  setiap ruas; perubahan selama perjalanan belum dimodelkan.
- Emisi adalah CO₂ pembakaran berbasis asumsi, bukan CO₂e, inventaris daur
  hidup, atau pengurangan emisi kota yang telah terukur.
- Pengujian VPS tetap dibatasi agar layanan lain tidak terganggu. Data
  produksi dan potret memiliki batas waktu; scheduler publikasi belum ada.

Tautan sumber publik utama untuk penelusuran: [repo](https://github.com/dzakyahnaf/pasang-surut),
[atribusi OSM](https://www.openstreetmap.org/copyright), dan
[layanan IOC sema](https://www.ioc-sealevelmonitoring.org/service.php?query=data&code=sema).
Deck menggunakan hasil evaluasi yang tersimpan, tidak mengunduh/mengganti
rekaman IOC atau mengklaim telah mengkalibrasi ulang pada 23 September.
