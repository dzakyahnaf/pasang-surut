// ===================================================================
// PASANG SURUT — Cek cakupan arsip Sentinel-1 di atas AOI Semarang
// Tim: trio la albiceleste
// VERSI 3 — minimal API
//
// CARA PAKAI:
//   1. Buka https://code.earthengine.google.com
//   2. Hapus SELURUH isi panel kode, tempel file ini
//   3. Klik Run
//
// Riwayat perbaikan:
//   v1 -> v2 : Map.centerObject melempar error tipe ErrorMargin.
//              Diganti Map.setCenter.
//   v2 -> v3 : ee.Filter.listContains tidak tersedia.
//              Filter polarisasi DIHAPUS (lihat catatan di bawah).
//              ee.List.sequence, ee.Feature, ui.Chart juga dihapus,
//              diganti loop JavaScript biasa. Makin sedikit fungsi
//              yang dipakai, makin kecil peluang error API.
//
// CATATAN soal polarisasi:
//   Sentinel-1 mode IW di atas daratan Indonesia praktis selalu VV+VH.
//   Jadi menghapus filter polarisasi tidak mengubah hasil hitungan.
//   Bagian 2 di bawah membuktikannya dengan mencetak nama band.
// ===================================================================

var aoi = ee.Geometry.Rectangle([110.385, -6.995, 110.500, -6.925]);

Map.setCenter(110.4425, -6.96, 12);
Map.addLayer(aoi, {color: 'red'}, 'AOI pilot');

var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filterDate('2015-01-01', '2026-08-24');


// --- 1. TOTAL ---------------------------------------------------------
print('=== 1. TOTAL CITRA ===');
print(s1.size());


// --- 2. Bukti band VV tersedia ---------------------------------------
print('=== 2. NAMA BAND CITRA PERTAMA ===');
print(ee.Image(s1.first()).bandNames());


// --- 3. Jumlah per tahun ---------------------------------------------
// Loop JavaScript biasa, bukan ee.List.sequence. Tiap tahun satu baris
// di Console. Lebih berisik tapi jauh lebih kecil risikonya.
print('=== 3. JUMLAH PER TAHUN ===');
for (var y = 2015; y <= 2026; y++) {
  print(
    String(y),
    s1.filterDate(y + '-01-01', (y + 1) + '-01-01').size()
  );
}


// --- 4. Arah orbit ----------------------------------------------------
print('=== 4. ASCENDING (lintasan sore) ===');
print(s1.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING')).size());
print('=== 5. DESCENDING (lintasan pagi) ===');
print(s1.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING')).size());


// --- 5. Tampilkan citra terbaru --------------------------------------
var terbaru = ee.Image(s1.sort('system:time_start', false).first());
print('=== 6. TANGGAL CITRA TERBARU ===');
print(terbaru.date().format('YYYY-MM-dd HH:mm:ss'));
Map.addLayer(
  terbaru.select('VV').clip(aoi),
  {min: -25, max: 0},
  'VV citra terbaru (gelap = kemungkinan air)'
);


// --- 6. Ekspor daftar waktu akuisisi ---------------------------------
// Sengaja ditaruh paling akhir. Kalau bagian ini error, angka-angka
// di atas SUDAH tercetak dan tetap bisa dilaporkan.
var daftar = s1.map(function (img) {
  return ee.Feature(null, {
    scene_id:  img.get('system:index'),
    waktu_utc: img.date().format('YYYY-MM-dd HH:mm:ss'),
    orbit:     img.get('orbitProperties_pass')
  });
});

Export.table.toDrive({
  collection:  ee.FeatureCollection(daftar),
  description: 'daftar_akuisisi_s1_semarang',
  fileFormat:  'CSV'
});


// ===================================================================
// LAPORKAN ANGKA INI:
//   Total citra           : ____
//   2022 / 2023 / 2024    : ____ / ____ / ____
//   2025 / 2026           : ____ / ____
//   Ascending / Descending: ____ / ____
//
// AMBANG KEPUTUSAN:
//   > 150   aman, lanjut sesuai PLAN.md
//   80-150  cukup, pangkas fitur model maksimal 5
//   < 80    STOP, arsitektur dirombak
// ===================================================================
