/**
 * api.js — satu-satunya tempat frontend berbicara dengan backend.
 *
 * Alamat backend dibaca dari variabel lingkungan Vite supaya bisa berbeda
 * antara pengembangan dan produksi tanpa mengubah kode.
 */

const ALAMAT = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function ambil(jalur) {
  const jawaban = await fetch(`${ALAMAT}${jalur}`);
  if (!jawaban.ok) {
    let rincian = `HTTP ${jawaban.status}`;
    try {
      const isi = await jawaban.json();
      if (isi.detail) rincian = isi.detail;
    } catch {
      /* jawaban bukan JSON, pakai kode status apa adanya */
    }
    throw new Error(rincian);
  }
  return jawaban.json();
}

/** Keadaan sistem: jumlah ruas, sumber data, rentang waktu prediksi. */
export function ambilKesehatan() {
  return ambil("/api/kesehatan");
}

/**
 * Jaringan jalan sebagai GeoJSON, dengan kedalaman genangan pada satu jam.
 * @param {string|null} waktuIso jam ISO 8601; null berarti jam berjalan
 */
export function ambilRuas(waktuIso = null) {
  const kueri = waktuIso ? `?waktu=${encodeURIComponent(waktuIso)}` : "";
  return ambil(`/api/ruas${kueri}`);
}
