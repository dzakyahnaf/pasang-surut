/**
 * HalamanValidasi.jsx — halaman yang harus bertahan di sesi tanya jawab.
 *
 * Aturan yang mengatur seluruh berkas ini: TIDAK ADA SATU ANGKA PUN YANG
 * DITAMBAL DI SINI. Kalau API mengembalikan null, yang ditampilkan adalah
 * kalimat "belum tersedia", bukan tanda hubung yang menyamar sebagai nol
 * dan bukan nilai bawaan yang kelihatan masuk akal.
 *
 * Halaman ini menampilkan tiga hal, berurutan, dan urutannya disengaja:
 *
 *   1. Model yang DITOLAK, beserta angkanya dan alasan penolakannya.
 *   2. Yang benar-benar dipakai sekarang.
 *   3. Yang tidak kami klaim sama sekali.
 *
 * Menaruh model yang ditolak paling atas terasa melawan naluri. Justru itu
 * gunanya: juri yang membuka halaman ini akan menemukan kelemahan terbesar
 * kami sudah tertulis sendiri sebelum sempat ditanyakan.
 */

import { useEffect, useState } from "react";

import { ambilValidasi } from "../lib/api.js";
import { t } from "../lib/teks.js";

/** Angka bergaya Indonesia. Null tetap null, tidak pernah jadi nol. */
function angka(nilai, desimal = 4) {
  if (nilai === null || nilai === undefined) return null;
  return nilai.toFixed(desimal).replace(".", ",");
}

function Metrik({ label, nilai, keterangan }) {
  return (
    <div className="validasi__metrik">
      <span className="validasi__metrik-label t-label">{label}</span>
      <span className="validasi__metrik-nilai t-data">
        {nilai === null ? (
          <em className="validasi__kosong">{t("validasi.belumDilatih")}</em>
        ) : (
          nilai
        )}
      </span>
      {keterangan ? (
        <span className="validasi__metrik-catatan t-label">{keterangan}</span>
      ) : null}
    </div>
  );
}

/**
 * Diagram batang kepentingan fitur.
 *
 * Ditulis sebagai SVG langsung, bukan dengan pustaka grafik. Satu diagram
 * batang tidak sepadan dengan menambah dependency, dan pustaka grafik
 * membawa gaya visualnya sendiri yang akan bertabrakan dengan DESIGN.md.
 */
function KepentinganFitur({ daftar }) {
  if (!daftar || daftar.length === 0) return null;
  const maks = Math.max(...daftar.map((d) => Math.abs(d.penurunan_roc_auc)), 1e-9);
  const waktu = new Set([
    "tinggi_pasut_m", "hujan_24j_mm", "hujan_72j_mm",
  ]);

  return (
    <ul className="validasi__fitur">
      {daftar.map((d) => {
        const lebar = (Math.abs(d.penurunan_roc_auc) / maks) * 100;
        const fiturWaktu = waktu.has(d.fitur);
        return (
          <li key={d.fitur} className="validasi__fitur-baris">
            <span className="validasi__fitur-nama t-label">{d.nama}</span>
            <span className="validasi__fitur-batang" aria-hidden="true">
              <span
                className={
                  "validasi__fitur-isi" +
                  (fiturWaktu ? " validasi__fitur-isi--waktu" : "")
                }
                style={{ width: `${lebar}%` }}
              />
            </span>
            <span className="validasi__fitur-nilai t-data">
              {angka(d.penurunan_roc_auc)}
              {fiturWaktu ? (
                <span className="validasi__fitur-tanda t-label">
                  {" "}
                  {t("validasi.fiturWaktuNol")}
                </span>
              ) : null}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

export default function HalamanValidasi({ onKembali }) {
  const [data, setData] = useState(null);
  const [memuat, setMemuat] = useState(true);
  const [galat, setGalat] = useState(false);

  useEffect(() => {
    let dibatalkan = false;
    (async () => {
      try {
        const d = await ambilValidasi();
        if (!dibatalkan) setData(d);
      } catch {
        if (!dibatalkan) setGalat(true);
      } finally {
        if (!dibatalkan) setMemuat(false);
      }
    })();
    return () => { dibatalkan = true; };
  }, []);

  const km = data?.matriks_konfusi;

  return (
    <main className="validasi" id="konten-utama">
      <div className="validasi__kepala">
        <h1 className="validasi__judul">{t("validasi.judul")}</h1>
        <button type="button" className="validasi__kembali" onClick={onKembali}>
          {t("validasi.kembaliKePeta")}
        </button>
      </div>

      <p className="validasi__pengantar">{t("validasi.pengantar")}</p>

      {memuat ? <p className="t-label">{t("memuat.validasi")}</p> : null}
      {galat ? <p className="t-label">{t("galat.serverTidakMerespons")}</p> : null}

      {data && !data.tersedia ? (
        <section className="validasi__blok validasi__blok--kosong">
          <h2 className="t-bagian">{t("validasi.belumDilatih")}</h2>
          <p>{t("validasi.belumDilatihIsi")}</p>
        </section>
      ) : null}

      {data && data.tersedia ? (
        <>
          {/* ── 1. Model yang ditolak ─────────────────────────────── */}
          <section className="validasi__blok validasi__blok--ditolak">
            <h2 className="t-bagian">{t("validasi.judulDitolak")}</h2>
            <p>{t("validasi.ditolakIsi")}</p>
            {data.alasan_ditolak ? (
              <p className="validasi__alasan">{data.alasan_ditolak}</p>
            ) : null}

            <div className="validasi__kisi">
              <Metrik label={t("validasi.rocAuc")} nilai={angka(data.roc_auc)} />
              <Metrik
                label={t("validasi.prAuc")}
                nilai={angka(data.pr_auc)}
                keterangan={
                  data.proporsi_dasar !== null
                    ? `dasar ${angka(data.proporsi_dasar)}`
                    : null
                }
              />
              <Metrik label={t("validasi.f1")} nilai={angka(data.f1)} />
              <Metrik
                label={t("validasi.ambang")}
                nilai={angka(data.ambang_probabilitas, 3)}
              />
              <Metrik
                label={t("validasi.skorBrier")}
                nilai={angka(data.kalibrasi?.skor_brier ?? null, 4)}
              />
              <Metrik
                label={t("validasi.jumlahSampelLatih")}
                nilai={data.baris_latih?.toLocaleString("id-ID") ?? null}
                keterangan={data.periode_latih}
              />
              <Metrik
                label={t("validasi.jumlahSampelUji")}
                nilai={data.baris_uji?.toLocaleString("id-ID") ?? null}
                keterangan={data.periode_uji}
              />
            </div>

            {km ? (
              <table className="validasi__matriks">
                <caption className="t-label">
                  {t("validasi.matriksKebingungan")}
                </caption>
                <tbody>
                  <tr>
                    <th scope="row" className="t-label">
                      {t("validasi.benarNegatif")}
                    </th>
                    <td className="t-data">{km.TN.toLocaleString("id-ID")}</td>
                    <th scope="row" className="t-label">
                      {t("validasi.salahPositif")}
                    </th>
                    <td className="t-data">{km.FP.toLocaleString("id-ID")}</td>
                  </tr>
                  <tr>
                    <th scope="row" className="t-label">
                      {t("validasi.salahNegatif")}
                    </th>
                    <td className="t-data">{km.FN.toLocaleString("id-ID")}</td>
                    <th scope="row" className="t-label">
                      {t("validasi.benarPositif")}
                    </th>
                    <td className="t-data">{km.TP.toLocaleString("id-ID")}</td>
                  </tr>
                </tbody>
              </table>
            ) : null}

            <h3 className="t-bagian">{t("validasi.kepentinganFitur")}</h3>
            <KepentinganFitur daftar={data.kepentingan_fitur} />

            {Object.keys(data.pembanding_naif || {}).length ? (
              <>
                <h3 className="t-bagian">{t("validasi.judulPembandingNaif")}</h3>
                <p className="t-label">{t("validasi.keteranganPembandingNaif")}</p>
                <ul className="validasi__pembanding">
                  {Object.entries(data.pembanding_naif).map(([nama, nilai]) => (
                    <li key={nama}>
                      <span className="t-label">{nama}</span>
                      <span className="t-data">{angka(nilai)}</span>
                    </li>
                  ))}
                </ul>
              </>
            ) : null}

            <p className="validasi__catatan t-label">
              {t("validasi.catatanPembagian")}
            </p>
          </section>

          {/* ── 2. Yang dipakai ───────────────────────────────────── */}
          <section className="validasi__blok">
            <h2 className="t-bagian">{t("validasi.judulYangDipakai")}</h2>
            <p>{t("validasi.yangDipakaiIsi")}</p>
            {data.indeks_kerentanan?.bobot ? (
              <ul className="validasi__bobot">
                {Object.entries(data.indeks_kerentanan.bobot).map(([k, v]) => (
                  <li key={k}>
                    <span className="t-label">{k.replace(/_/g, " ")}</span>
                    <span className="t-data">{angka(v, 3)}</span>
                  </li>
                ))}
              </ul>
            ) : null}
          </section>

          {/* ── Fitur yang DIPOTONG, dan alasannya ────────────────── */}
          {/* Brief M5 meminta perbandingan visual prediksi versus genangan
              teramati untuk dua sampai tiga kejadian uji. Fitur itu dipotong,
              bukan ditunda karena kehabisan waktu: bahannya tidak ada. Tidak
              ada satu pun pengamatan genangan per ruas jalan di repo ini,
              dan membuat perbandingan tanpa kebenaran lapangan berarti
              menyandingkan dua tebakan lalu menyebutnya validasi. */}
          <section className="validasi__blok">
            <h2 className="t-bagian">
              {t("validasi.judulTidakBisaDibandingkan")}
            </h2>
            <p>{t("validasi.tidakBisaDibandingkanIsi")}</p>
          </section>

          {/* ── 3. Yang tidak diklaim ─────────────────────────────── */}
          <section className="validasi__blok">
            <h2 className="t-bagian">{t("validasi.judulTidakDiklaim")}</h2>
            <p>{t("validasi.tidakDiklaimIsi")}</p>
            {data.indeks_kerentanan?.peringatan?.length ? (
              <ul className="validasi__peringatan">
                {data.indeks_kerentanan.peringatan.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            ) : null}
          </section>
        </>
      ) : null}
    </main>
  );
}
