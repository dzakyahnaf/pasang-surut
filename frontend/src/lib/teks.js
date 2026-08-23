/**
 * teks.js — akses tunggal ke seluruh teks antarmuka.
 *
 * Dilarang menulis kalimat Bahasa Indonesia langsung di dalam komponen.
 * Semua lewat t(). Butuh kalimat baru? Tambahkan ke copy.id.json lebih dulu.
 *
 * KENAPA HELPER INI MELEMPAR ERROR, BUKAN MENGEMBALIKAN KUNCI MENTAH.
 *
 * Kalau kunci yang salah ketik hanya dikembalikan apa adanya, layar akan
 * menampilkan "hasilRute.judul" alih-alih kalimat. Itu lolos dari review,
 * lolos dari uji coba cepat, lalu muncul di depan juri babak final saat
 * mereka memakai aplikasi ini sendiri. Bobot Keberhasilan Implementasi 25
 * persen, dan kesalahan seperti ini tidak bisa diperbaiki saat itu juga.
 *
 * Karena itu: gagal keras, gagal saat mengetik kode.
 */

import copy from "../copy.id.json";

/**
 * Di produksi, error yang tidak tertangkap akan mematikan seluruh layar.
 * Peta yang hidup dengan satu label salah masih lebih berguna bagi pengguna
 * daripada layar putih. Jadi di produksi galatnya diturunkan menjadi
 * console.error — tetapi TIDAK PERNAH didiamkan.
 */
const MODE_PENGEMBANGAN = import.meta.env.DEV;

function laporkan(pesan) {
  if (MODE_PENGEMBANGAN) {
    throw new Error(`[teks] ${pesan}`);
  }
  console.error(`[teks] ${pesan}`);
}

/**
 * Telusuri objek copy.id.json memakai kunci bertitik.
 * Contoh: "hasilRute.judul" -> copy.hasilRute.judul
 */
function telusuri(kunci) {
  const bagian = kunci.split(".");
  let simpul = copy;
  for (const nama of bagian) {
    if (simpul === null || typeof simpul !== "object" || !(nama in simpul)) {
      return undefined;
    }
    simpul = simpul[nama];
  }
  return simpul;
}

/**
 * Ambil satu string dari copy.id.json.
 *
 * @param {string} kunci  kunci bertitik, contoh "peta.judulLegenda"
 * @param {object} params nilai pengganti placeholder {namaVariabel}
 * @returns {string}
 *
 * Melempar error bila:
 *   - kunci tidak ditemukan
 *   - kunci menunjuk ke blok, bukan ke string
 *   - masih ada placeholder yang belum terganti setelah interpolasi
 */
export function t(kunci, params = {}) {
  const nilai = telusuri(kunci);

  if (nilai === undefined) {
    laporkan(
      `kunci "${kunci}" tidak ada di copy.id.json. ` +
        `Tambahkan ke berkas itu lebih dulu, jangan mengarang kalimat di komponen.`
    );
    return "";
  }

  if (typeof nilai !== "string") {
    laporkan(
      `kunci "${kunci}" menunjuk ke ${typeof nilai}, bukan string. ` +
        `Mungkin kurang satu tingkat, misalnya "${kunci}.judul".`
    );
    return "";
  }

  // Placeholder ditulis {namaVariabel} dalam kurung kurawal tunggal.
  const terisi = nilai.replace(/\{(\w+)\}/g, (cocok, nama) => {
    if (!(nama in params)) {
      return cocok; // biarkan, nanti tertangkap pemeriksaan di bawah
    }
    return String(params[nama]);
  });

  // Placeholder yang tidak terganti harus memicu error, bukan tampil apa
  // adanya. "Rute melintasi genangan {kedalaman} cm" di layar juri adalah
  // kegagalan yang lebih buruk daripada layar galat saat pengembangan.
  const tersisa = terisi.match(/\{(\w+)\}/g);
  if (tersisa) {
    laporkan(
      `placeholder ${tersisa.join(", ")} pada kunci "${kunci}" tidak terganti. ` +
        `Kirimkan nilainya lewat argumen kedua: t("${kunci}", { ${tersisa[0]
          .slice(1, -1)}: ... })`
    );
    return "";
  }

  return terisi;
}

/**
 * Periksa keberadaan kunci tanpa memicu galat.
 * Dipakai hanya untuk percabangan, bukan untuk menampilkan teks.
 */
export function adaKunci(kunci) {
  return typeof telusuri(kunci) === "string";
}

export default t;
