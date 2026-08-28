/**
 * TujuanCepat.jsx — tombol tujuan yang sering dituju.
 *
 * Titiknya disiapkan luring oleh skrip 17 dan sudah dilekatkan ke simpul
 * jalan terdekat, sehingga menekan tombol tidak pernah menghasilkan galat
 * "terlalu jauh dari jalan". Itu penting untuk skenario demo: juri yang
 * menekan tombol pertama lalu mendapat galat akan menyimpulkan aplikasinya
 * rusak, bukan bahwa titiknya kebetulan di tengah laut.
 *
 * Nama tombol TIDAK berubah di tengah alur, sesuai larangan teks di
 * CLAUDE.md. Yang berubah hanya keadaan terpilih.
 */

import { t } from "../lib/teks.js";

export default function TujuanCepat({ daftar, memuat, terpilih, onPilih }) {
  if (memuat) {
    return (
      <section className="tujuan-cepat">
        <h2 className="tujuan-cepat__judul t-bagian">{t("tujuanCepat.judul")}</h2>
        <p className="tujuan-cepat__pesan t-label">{t("tujuanCepat.muat")}</p>
      </section>
    );
  }

  if (!daftar || daftar.length === 0) {
    return (
      <section className="tujuan-cepat">
        <h2 className="tujuan-cepat__judul t-bagian">{t("tujuanCepat.judul")}</h2>
        <p className="tujuan-cepat__pesan t-label">{t("tujuanCepat.kosong")}</p>
      </section>
    );
  }

  return (
    <section className="tujuan-cepat">
      <h2 className="tujuan-cepat__judul t-bagian">{t("tujuanCepat.judul")}</h2>
      <p className="tujuan-cepat__petunjuk t-label">{t("tujuanCepat.petunjuk")}</p>
      <ul className="tujuan-cepat__daftar">
        {daftar.map((tj) => {
          const aktif = terpilih === tj.kunci;
          return (
            <li key={tj.kunci}>
              <button
                type="button"
                className="tujuan-cepat__tombol"
                aria-pressed={aktif}
                onClick={() => onPilih(tj)}
              >
                {tj.label}
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
