/**
 * PanelDampak.jsx — empat angka biaya menghindar, DESIGN.md Bagian 8.
 *
 * Angka memakai IBM Plex Mono lewat kelas `t-data`; satuannya selalu lebih
 * kecil dan lebih redup lewat kelas `t-satuan`. Aturan itu bukan hiasan:
 * ketika angka dan satuan sama besar, mata membaca "0,039 L" sebagai satu
 * kata dan kehilangan besarannya.
 *
 * BAHAN BAKAR DAN EMISI SELALU RENTANG, TIDAK PERNAH ANGKA TUNGGAL.
 * Konsumsi per kilometer bergantung kendaraan, muatan, dan lalu lintas.
 * Menyajikan satu angka pasti sampai tiga desimal akan menyesatkan, dan
 * juri berhak menanyakan dari mana ketelitian itu datang.
 *
 * Waktu dan jarak TIDAK diberi rentang, karena keduanya dihitung langsung
 * dari geometri dan kecepatan ruas — ketidakpastiannya ada di kecepatan
 * yang sudah tercatat sebagai batasan tersendiri, bukan di aritmetikanya.
 */

import { t } from "../lib/teks.js";

/** Angka bergaya Indonesia: pemisah desimal koma. */
function angka(nilai, desimal = 2) {
  if (nilai === null || nilai === undefined || Number.isNaN(nilai)) return "–";
  return nilai.toFixed(desimal).replace(".", ",");
}

/**
 * Rentang yang tidak pernah tampil sebagai "0,000-0,000".
 *
 * Selisih rute yang pendek menghasilkan bahan bakar di bawah satu mililiter.
 * Dibulatkan ke tiga desimal, keduanya menjadi nol, dan panel terbaca seperti
 * rusak padahal angkanya benar. Yang ditampilkan dalam keadaan itu adalah
 * batas atasnya saja dengan tanda "kurang dari" — jujur, dan tidak memaksa
 * pembaca menghitung sendiri bahwa nol bukan berarti tidak ada.
 */
function rentangTeks(rentang, desimal) {
  if (!rentang) return "–";
  const bawah = angka(rentang.bawah, desimal);
  const atas = angka(rentang.atas, desimal);
  const nol = (x) => Number.parseFloat(x.replace(",", ".")) === 0;
  if (nol(bawah) && nol(atas)) {
    const satuanTerkecil = Math.pow(10, -desimal);
    return `< ${angka(satuanTerkecil, desimal)}`;
  }
  if (bawah === atas) return bawah;
  return t("dampak.rentang", { bawah, atas });
}

function Nilai({ label, nilai, satuan, desimal = 2, rentang = null }) {
  return (
    <div className="dampak__butir">
      <span className="dampak__label t-label">{label}</span>
      <span className="dampak__angka t-data">
        {rentang ? rentangTeks(rentang, desimal) : angka(nilai, desimal)}
        <span className="dampak__satuan t-satuan"> {satuan}</span>
      </span>
    </div>
  );
}

export default function PanelDampak({ dampak, moda }) {
  if (!dampak) return null;

  // Selisih yang lebih kecil daripada ambang di domain/dampak.py berasal dari
  // pembulatan geometri, bukan dari pilihan rute yang berbeda. Menyajikannya
  // sebagai penghematan akan mengklaim manfaat yang tidak ada.
  if (!dampak.berarti) {
    return (
      <section className="dampak" aria-label={t("dampak.judul")}>
        <h2 className="dampak__judul t-bagian">{t("dampak.judul")}</h2>
        <p className="dampak__kosong t-label">{t("dampak.tidakAdaSelisih")}</p>
      </section>
    );
  }

  return (
    <section className="dampak" aria-label={t("dampak.judul")}>
      <h2 className="dampak__judul t-bagian">{t("dampak.judul")}</h2>
      <p className="dampak__keterangan t-label">{t("dampak.keterangan")}</p>

      <div className="dampak__kisi">
        <Nilai
          label={t("dampak.selisihWaktu")}
          nilai={dampak.menit}
          satuan={t("satuan.menit")}
          desimal={1}
        />
        <Nilai
          label={t("dampak.selisihJarak")}
          nilai={dampak.km}
          satuan={t("satuan.kilometer")}
        />
        <Nilai
          label={t("dampak.bahanBakar")}
          rentang={dampak.liter}
          satuan={t("satuan.liter")}
          desimal={3}
        />
        <Nilai
          label={t("dampak.emisi")}
          rentang={dampak.kg_co2 ?? dampak.kg_co2e}
          satuan={t("satuan.kilogramCo2e")}
          desimal={3}
        />
      </div>

      {/* Faktornya rata-rata per moda, bukan kendaraan pengguna. Dinyatakan
          di antarmuka, bukan hanya di dokumentasi, karena yang membaca angka
          ini adalah pengguna dan juri, bukan pembaca repo. */}
      <p className="dampak__catatan t-label">{t("dampak.catatanFaktor")}</p>
    </section>
  );
}
