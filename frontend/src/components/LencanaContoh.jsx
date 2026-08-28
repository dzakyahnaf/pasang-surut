/**
 * LencanaContoh.jsx — lencana peringatan sumber data, DESIGN.md Bagian 8.
 *
 * Latar --bahaya, teks --tinta-balik, huruf besar 12px, radius 3px,
 * melekat di kanan atas peta.
 *
 * PENTING: lencana ini TIDAK punya saklar manual. Ia ditentukan sepenuhnya
 * oleh daftar sumber data yang dikembalikan API, dan hilang dengan
 * sendirinya begitu tabel prediksi diisi model yang sudah tervalidasi.
 * Tidak ada tombol yang bisa lupa dimatikan sebelum demo.
 *
 * DUA TINGKAT PERINGATAN, BUKAN SATU.
 *
 * 'dummy'          data contoh, sama sekali tidak punya dasar fisik
 * 'kerentanan_v1'  indeks kerentanan berbasis aturan, bukan prediksi model
 *
 * Tingkat kedua ditambahkan setelah model genangan berbasis Sentinel-1
 * dilatih lalu DITOLAK sendiri karena labelnya tidak berkorelasi dengan
 * pasut. Tanpa tingkat kedua, indeks kerentanan akan tampil tanpa
 * peringatan apa pun dan terbaca seolah prediksi model — persis overclaim
 * yang dilarang aturan repo nomor 1.
 *
 * Hanya sumber 'model_v1' yang membuat peta tampil tanpa lencana, dan itu
 * baru sah setelah docs/validasi.md memuat angka akurasi yang sebenarnya.
 */

import { t } from "../lib/teks.js";

const SUMBER_CONTOH = "dummy";
const SUMBER_KERENTANAN = "kerentanan_v1";

export default function LencanaContoh({ sumberData }) {
  const daftar = Array.isArray(sumberData) ? sumberData : [];

  // Data contoh diperiksa lebih dulu: bila keduanya ada sekaligus, yang
  // ditampilkan adalah peringatan yang paling keras.
  const tingkat = daftar.includes(SUMBER_CONTOH)
    ? "contoh"
    : daftar.includes(SUMBER_KERENTANAN)
      ? "kerentanan"
      : null;

  if (!tingkat) return null;

  const teks =
    tingkat === "contoh"
      ? {
          judul: t("sumberData.lencanaContohPanjang"),
          penjelasan: t("sumberData.penjelasanContoh"),
          pembacaLayar: t("aksesibilitas.lencanaContohLabel"),
        }
      : {
          judul: t("sumberData.lencanaKerentananPanjang"),
          penjelasan: t("sumberData.penjelasanKerentanan"),
          pembacaLayar: t("aksesibilitas.lencanaKerentananLabel"),
        };

  return (
    <div className="lencana-contoh" role="status" data-tingkat={tingkat}>
      <span className="lencana-contoh__teks t-bagian" title={teks.penjelasan}>
        {teks.judul}
      </span>
      <span className="khusus-pembaca-layar">{teks.pembacaLayar}</span>
    </div>
  );
}
