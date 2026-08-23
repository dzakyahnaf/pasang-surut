/**
 * LencanaContoh.jsx — lencana DATA CONTOH, DESIGN.md Bagian 8.
 *
 * Latar --bahaya, teks --tinta-balik, huruf besar 12px, radius 3px,
 * melekat di kanan atas peta.
 *
 * PENTING: lencana ini TIDAK punya saklar manual. Ia muncul selama daftar
 * sumber data masih memuat 'dummy', dan hilang dengan sendirinya begitu
 * tabel prediksi diisi model asli. Tidak ada tombol yang bisa lupa
 * dimatikan sebelum demo.
 */

import { t } from "../lib/teks.js";

const SUMBER_CONTOH = "dummy";

export default function LencanaContoh({ sumberData }) {
  const perluTampil =
    Array.isArray(sumberData) && sumberData.includes(SUMBER_CONTOH);

  if (!perluTampil) return null;

  return (
    <div className="lencana-contoh" role="status">
      <span
        className="lencana-contoh__teks t-bagian"
        title={t("sumberData.penjelasanContoh")}
      >
        {t("sumberData.lencanaContohPanjang")}
      </span>
      <span className="khusus-pembaca-layar">
        {t("aksesibilitas.lencanaContohLabel")}
      </span>
    </div>
  );
}
