/** Peta dasar OSM pilihan tim, dilayani CARTO; overlay berasal dari API. */
export const GAYA_OSM = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json";

export function tataPetaDasar(peta) {
  // Jalan kering dan label geografis sudah tersedia di basemap.
  // Tetap gunakan geometri analisis untuk warna/pola genangan serta rute.
  peta.setPaintProperty("ruas-dasar", "line-opacity", 0);
  for (const id of ["nama-jalan-utama", "nama-jalan-lokal", "nama-wilayah",
    "garis-pantai"]) {
    peta.setLayoutProperty(id, "visibility", "none");
  }
  // Label bawaan tetap terbaca di atas genangan dan garis perjalanan.
  for (const layer of peta.getStyle().layers) {
    if (layer.type === "symbol" && layer.source === "carto") {
      peta.moveLayer(layer.id, "tempat-titik");
    }
  }
}
