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

export default function TujuanCepat({ daftar, memuat, terpilih, onPilih, galat, onUlang }) {
  if (memuat) {
    // Rangka STATIS, tidak berdenyut. DESIGN.md Bagian 9 revisi 30 Agustus:
    // nilai sebuah rangka pemuatan ada pada BENTUKNYA — ia menunjukkan apa
    // yang akan datang dan menjaga tata letak tidak melompat saat data tiba.
    // Nilainya bukan pada denyutnya, dan denyut tetap dilarang.
    return (
      <section className="tujuan-cepat" aria-busy="true">
        <h2 className="tujuan-cepat__judul t-bagian">{t("tujuanCepat.judul")}</h2>
        <p className="tujuan-cepat__pesan t-label">{t("tujuanCepat.muat")}</p>
        <div className="tujuan-cepat__daftar" aria-hidden="true">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="tujuan-cepat__rangka" />
          ))}
        </div>
      </section>
    );
  }

  if (galat) return <section className="tujuan-cepat" role="alert">
    <p className="tujuan-cepat__pesan t-label">{t('tujuanCepat.gagal')}</p>
    <button type="button" className="tombol-utama" onClick={onUlang}>{t('tujuanCepat.ulang')}</button>
  </section>;

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
