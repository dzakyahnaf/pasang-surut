/**
 * api.js — satu-satunya tempat frontend berbicara dengan backend.
 *
 * Alamat backend dibaca dari variabel lingkungan Vite supaya bisa berbeda
 * antara pengembangan dan produksi tanpa mengubah kode.
 */

const ALAMAT = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function ambil(jalur, opsi) {
  const jawaban = await fetch(`${ALAMAT}${jalur}`, opsi);
  if (!jawaban.ok) {
    let rincian = `HTTP ${jawaban.status}`;
    let kode = null;
    try {
      const isi = await jawaban.json();
      if (isi.detail && typeof isi.detail === "object") {
        kode = isi.detail.kode ?? null;
        rincian = JSON.stringify(isi.detail);
      } else if (isi.detail) {
        rincian = isi.detail;
      }
    } catch {
      /* jawaban bukan JSON, pakai kode status apa adanya */
    }
    const galat = new Error(rincian);
    galat.status = jawaban.status;
    galat.kode = kode;
    throw galat;
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

/** Ruas yang tergenang saja pada satu jam. Jauh lebih ringan dari ambilRuas. */
export function ambilGenangan(waktuIso = null) {
  const kueri = waktuIso ? `?waktu=${encodeURIComponent(waktuIso)}` : "";
  return ambil(`/api/genangan${kueri}`);
}

/** Sumbu waktu Pita Pasut: 72 jam ke depan beserta tinggi pasut per jam. */
export function ambilJam() {
  return ambil("/api/jam");
}

/**
 * Dua rute sekaligus: pembanding yang mengabaikan rob, dan yang sadar rob.
 * @param {{asal:number[], tujuan:number[], waktu:string, moda:string}} isi
 */
export function hitungRute(isi) {
  return ambil("/api/rute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(isi),
  });
}

/** Titik tujuan penting, disiapkan luring oleh skrip 17. */
export function ambilTujuanCepat() {
  return ambil("/api/tujuan-cepat");
}

/**
 * Metrik model dan indeks kerentanan.
 *
 * Endpoint ini mengembalikan `tersedia: false` dan seluruh metrik null
 * selama model belum ada. Halaman validasi TIDAK boleh menambal nilai
 * kosong dengan angka apa pun — kalau kosong, yang ditulis adalah
 * validasi.belumDilatih.
 */
export function ambilValidasi() {
  return ambil("/api/validasi");
}
