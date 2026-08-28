/**
 * PeringatanPaparan.jsx — peringatan bila rute sadar rob TETAP menembus air.
 *
 * DESIGN.md Bagian 8. Latar --bahaya, tanpa ikon emoji, tanpa tanda seru.
 *
 * NADANYA SENGAJA DATAR. Kalimat risiko leptospirosis di copy.id.json ditulis
 * informatif tanpa menakut-nakuti, dan tidak boleh diubah nadanya. Peringatan
 * yang berteriak akan diabaikan setelah kali ketiga; peringatan yang
 * menjelaskan apa yang terjadi dan apa yang bisa dilakukan akan dibaca.
 *
 * Komponen ini hanya muncul bila rute yang SUDAH menghindari genangan tetap
 * terpaksa menembusnya. Rute biasa yang menembus air bukan urusan peringatan
 * ini — itu memang sifat rute pembanding.
 */

import { t } from "../lib/teks.js";
import { labelHariJam } from "../lib/waktu.js";

function angka(nilai, desimal = 0) {
  if (nilai === null || nilai === undefined) return "–";
  return nilai.toFixed(desimal).replace(".", ",");
}

export default function PeringatanPaparan({ paparan, jamAman, namaJalan, onPilihJam }) {
  if (!paparan || !paparan.menembus) return null;

  const jalan = namaJalan && namaJalan.length ? namaJalan[0] : null;

  return (
    <section className="peringatan" role="alert">
      <h2 className="peringatan__judul t-bagian">
        {t("peringatan.judulMenembus")}
      </h2>

      <p className="peringatan__isi">
        {jalan
          ? t("peringatan.isiMenembus", {
              kedalaman: angka(paparan.kedalaman_maks_cm),
              namaJalan: jalan,
              jam: "—",
            })
          : `${angka(paparan.kedalaman_maks_cm)} ${t("satuan.sentimeter")}`}
      </p>

      {/* Kalimat kesehatan diambil apa adanya dari copy.id.json. Angka kasus
          leptospirosis TIDAK diulang di sini: yang relevan bagi pengguna
          adalah tindakannya, bukan statistiknya. */}
      <p className="peringatan__kesehatan">{t("peringatan.risikoKesehatan")}</p>

      {jamAman ? (
        <button
          type="button"
          className="peringatan__saran"
          onClick={() => onPilihJam && onPilihJam(jamAman)}
        >
          {t("peringatan.saranJamLain", {
            jam: labelHariJam(jamAman.waktu_utc),
            kedalaman: angka(jamAman.kedalaman_maks_cm),
          })}
        </button>
      ) : (
        <p className="peringatan__tanpa-saran t-label">
          {t("peringatan.tidakAdaJamAman")}
        </p>
      )}
    </section>
  );
}
