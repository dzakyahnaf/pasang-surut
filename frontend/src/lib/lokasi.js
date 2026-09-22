import { t } from "./teks.js";

/** Nama titik pilihan tanpa reverse geocoding atau menebak nama ruas kosong. */
export function namaLokasi(titik, jaringan, tempat = []) {
  if (!titik) return null;
  const akses = tempat.find((p) => Math.abs(p.lon - titik[0]) < 0.000001
    && Math.abs(p.lat - titik[1]) < 0.000001);
  if (akses) return t("peta.aksesTempat", { nama: akses.label });

  // Jarak pendek lokal, dalam meter. Hanya untuk memberi konteks label;
  // snapping dan perhitungan rute tetap dilakukan backend.
  const xScale = 111320 * Math.cos(titik[1] * Math.PI / 180);
  const local = ([x, y]) => [(x - titik[0]) * xScale, (y - titik[1]) * 111320];
  let dekat = null;
  let jarak2 = 80 ** 2;
  for (const fitur of jaringan?.features ?? []) {
    const points = fitur.geometry?.type === "LineString" ? fitur.geometry.coordinates : [];
    for (let i = 1; i < points.length; i++) {
      const [ax, ay] = local(points[i - 1]);
      const [bx, by] = local(points[i]);
      const dx = bx - ax, dy = by - ay;
      const den = dx * dx + dy * dy;
      const f = den ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / den)) : 0;
      const d2 = (ax + f * dx) ** 2 + (ay + f * dy) ** 2;
      if (d2 < jarak2) { jarak2 = d2; dekat = fitur; }
    }
  }
  const nama = dekat?.properties?.nama?.trim();
  if (nama) return t("peta.dekatJalan", { nama });
  return t(dekat ? "peta.ruasTanpaNama" : "peta.titikPilihan");
}
