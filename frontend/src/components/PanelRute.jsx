/**
 * PanelRute.jsx — rail kiri: kontrol pencarian dan hasil rute.
 *
 * DESIGN.md Bagian 7: di desktop rail kiri selebar 360px berbadan gelap
 * berisi kontrol dan hasil, peta mengisi sisanya.
 *
 * DESIGN.md Bagian 10: nama tombol tidak berubah di tengah alur. Yang
 * bertuliskan "Cari rute" menghasilkan panel berjudul "Rute", bukan
 * "Hasil". Itu sebabnya judul panel hasil di bawah memakai
 * t("hasilRute.judul") dan bukan kalimat lain.
 */

import { t } from "../lib/teks.js";
import { labelJam } from "../lib/waktu.js";

const MODA = ["motor", "mobil"];

function Koordinat({ titik }) {
  if (!titik) return null;
  return (
    <span className="titik__koordinat t-data">
      {titik[1].toFixed(4)}, {titik[0].toFixed(4)}
    </span>
  );
}

function BarisTitik({ label, kosong, titik, nama, aktif, onPilihMode, onHapus, labelHapus }) {
  return (
    <div className={`titik ${aktif ? "titik--aktif" : ""}`}>
      <button
        type="button"
        className="titik__utama"
        onClick={onPilihMode}
        aria-pressed={aktif}
      >
        <span className="titik__label t-label">{label}</span>
        {titik ? (
          <>
            {nama ? <span className="titik__nama">{nama}</span> : null}
            <Koordinat titik={titik} />
          </>
        ) : (
          <span className="titik__kosong t-label">{kosong}</span>
        )}
      </button>
      {titik ? (
        <button
          type="button"
          className="titik__hapus"
          onClick={onHapus}
          aria-label={labelHapus}
          title={labelHapus}
        >
          <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
            <path d="M2 2 L10 10 M10 2 L2 10" stroke="currentColor"
                  strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      ) : null}
    </div>
  );
}

function AngkaDampak({ nilai, satuan, label, bertanda = false }) {
  // Pemisah desimal KOMA, sesuai kaidah bahasa Indonesia. Seluruh angka di
  // aplikasi ini memakai koma; satu tempat yang memakai titik sudah cukup
  // untuk membuat panel terlihat disusun dua orang yang tidak bicara.
  const teks =
    nilai === null || nilai === undefined
      ? "—"
      : (bertanda && nilai > 0 ? "+" : "") + nilai.toFixed(1).replace(".", ",");
  return (
    <div className="dampak">
      <div className="dampak__angka t-angka">{teks}</div>
      <div className="dampak__satuan">
        <span className="t-satuan">{satuan}</span>
      </div>
      <div className="dampak__label t-label">{label}</div>
    </div>
  );
}

export default function PanelRute({
  asal, tujuan, namaAsal, namaTujuan, modePilih, moda, hasil, sedangMencari, galat,
  onPilihMode, onHapusTitik, onGantiModa, onCari, onTampilkanRuteBiasa,
  tampilkanRuteBiasa, children, waktuTersedia = true,
}) {
  const siap = Boolean(asal && tujuan);

  const fiturSadar = hasil?.rute?.features?.find(
    (f) => f.properties.jenis === "rute_sadar_rob"
  );
  const fiturAbai = hasil?.rute?.features?.find(
    (f) => f.properties.jenis === "rute_abai_rob"
  );
  const sadar = fiturSadar?.properties;
  const abai = fiturAbai?.properties;

  return (
    <aside className="rail">
      {/* ── Pencarian ─────────────────────────────────────────────── */}
      <section className="rail__blok">
        <h2 className="t-bagian rail__judul">{t("pencarianRute.judul")}</h2>

        <BarisTitik
          label={t("pencarianRute.asal")}
          kosong={t("pencarianRute.asalKosong")}
          titik={asal}
          nama={namaAsal}
          aktif={modePilih === "asal"}
          onPilihMode={() => onPilihMode("asal")}
          onHapus={() => onHapusTitik("asal")}
          labelHapus={t("pencarianRute.hapusAsal")}
        />
        <BarisTitik
          label={t("pencarianRute.tujuan")}
          kosong={t("pencarianRute.tujuanKosong")}
          titik={tujuan}
          nama={namaTujuan}
          aktif={modePilih === "tujuan"}
          onPilihMode={() => onPilihMode("tujuan")}
          onHapus={() => onHapusTitik("tujuan")}
          labelHapus={t("pencarianRute.hapusTujuan")}
        />
      </section>

      {/* ── Moda ──────────────────────────────────────────────────── */}
      <section className="rail__blok">
        <h2 className="t-bagian rail__judul">{t("moda.judul")}</h2>
        <div className="moda" role="radiogroup" aria-label={t("moda.pilihModa")}>
          {MODA.map((m) => (
            <button
              key={m}
              type="button"
              role="radio"
              aria-checked={moda === m}
              className={`moda__tombol ${moda === m ? "moda__tombol--aktif" : ""}`}
              onClick={() => onGantiModa(m)}
            >
              <span className="t-label">{t(`moda.${m}`)}</span>
            </button>
          ))}
        </div>
        <p className="moda__keterangan t-label">
          {t(moda === "motor" ? "moda.keteranganMotor" : "moda.keteranganMobil")}
        </p>
      </section>

      <button
        type="button"
        className="tombol-utama t-bagian"
        disabled={!siap || sedangMencari || !waktuTersedia}
        onClick={onCari}
      >
        {sedangMencari
          ? t("pencarianRute.sedangMencari")
          : hasil || galat
            ? t("pencarianRute.cariUlang")
            : t("pencarianRute.cariRute")}
      </button>

      {/* ── Keadaan kosong ────────────────────────────────────────── */}
      {!siap && !hasil ? (
        <section className="rail__blok kosong">
          <h3 className="t-judul kosong__judul">
            {asal ? t("kosong.belumAdaTujuanJudul") : t("kosong.belumAdaRuteJudul")}
          </h3>
          <p className="t-label kosong__isi">
            {asal ? t("kosong.belumAdaTujuanIsi") : t("kosong.belumAdaRuteIsi")}
          </p>
        </section>
      ) : null}

      {/* ── Galat ─────────────────────────────────────────────────── */}
      {galat ? (
        <section className="rail__blok galat" role="alert">
          <p className="t-label">{galat}</p>
        </section>
      ) : null}

      {/* ── Hasil ─────────────────────────────────────────────────── */}
      {hasil && sadar ? (
        <section className="rail__blok hasil">
          <h2 className="t-bagian rail__judul">{t("hasilRute.judul")}</h2>
          <p className="t-label">{t("hasilRute.batasModel")}</p>

          {sadar.ditemukan ? (
            <>
              <div className="hasil__angka">
                <AngkaDampak
                  nilai={sadar.menit}
                  satuan={t("satuan.menit")}
                  label={t("hasilRute.waktuTempuh")}
                />
                <AngkaDampak
                  nilai={sadar.jarak_km}
                  satuan={t("satuan.kilometer")}
                  label={t("hasilRute.jarak")}
                />
              </div>

              {sadar.waktu_tiba_wib ? (
                <p className="t-label hasil__baris">
                  {t("hasilRute.tibaSekitar", { jam: labelJam(sadar.waktu_tiba_wib) })}
                </p>
              ) : null}

              <p className="t-label hasil__baris">
                {t("hasilRute.melewatiRuas", { jumlah: sadar.jumlah_ruas })}
              </p>

              <p className="t-label hasil__baris">
                {sadar.ruas_tergenang > 0
                  ? t("hasilRute.ruasTergenang", { jumlah: sadar.ruas_tergenang })
                  : t("hasilRute.tidakAdaGenangan")}
              </p>

              {/* Peringatan paparan bila rute terpaksa menembus genangan. */}
              {sadar.ruas_tergenang > 0 ? (
                <div className="peringatan" role="alert">
                  <p className="t-bagian peringatan__judul">
                    {t("peringatan.judulMenembus")}
                  </p>
                  <p className="t-label peringatan__isi">
                    {t("peringatan.isiMenembus", {
                      kedalaman: Math.round(sadar.kedalaman_maks_cm),
                      namaJalan: sadar.nama_jalan?.[0] ?? t("hasilRute.ruteDisarankan"),
                      jam: labelJam(hasil.waktu_berangkat_wib),
                    })}
                  </p>
                  <p className="t-label peringatan__isi">
                    {t("peringatan.risikoKesehatan")}
                  </p>
                </div>
              ) : null}

              {/* Pembanding. Selisih inilah argumen produk ini. */}
              {abai?.ditemukan ? (
                <div className="pembanding">
                  {hasil.selisih?.sama_persis ? (
                    <p className="t-label pembanding__sama">
                      {t("hasilRute.samaDenganRuteBiasa")}
                    </p>
                  ) : (
                    <>
                      <p className="t-label pembanding__judul">
                        {t("hasilRute.ruteBiasa")} — {t("hasilRute.keteranganRuteBiasa")}
                      </p>
                      <div className="hasil__angka">
                        <AngkaDampak
                          nilai={hasil.selisih?.menit}
                          satuan={t("satuan.menit")}
                          label={t("hasilRute.waktuTempuh")}
                          bertanda
                        />
                        <AngkaDampak
                          nilai={hasil.selisih?.km}
                          satuan={t("satuan.kilometer")}
                          label={t("hasilRute.jarak")}
                          bertanda
                        />
                      </div>
                    </>
                  )}
                  <button
                    type="button"
                    className="tombol-kecil t-label"
                    onClick={onTampilkanRuteBiasa}
                  >
                    {tampilkanRuteBiasa
                      ? t("hasilRute.sembunyikanRuteBiasa")
                      : t("hasilRute.tampilkanRuteBiasa")}
                  </button>
                </div>
              ) : null}
            </>
          ) : (
            <div className="peringatan" role="alert">
              <p className="t-bagian peringatan__judul">
                {t(sadar.alasan === 'tidak_terhubung' ? 'peringatan.judulTidakTerhubung' : "peringatan.judulSemuaTertutup")}
              </p>
              <p className="t-label peringatan__isi">
                {sadar.alasan === 'tidak_terhubung' ? t('peringatan.isiTidakTerhubung') : t("peringatan.isiSemuaTertutup", { moda: t(`moda.${moda}`) })}
              </p>
              {moda === "motor" && sadar.alasan !== 'tidak_terhubung' ? (
                <p className="t-label peringatan__isi">
                  {t("peringatan.saranGantiModa")}
                </p>
              ) : null}
            </div>
          )}
        </section>
      ) : null}

      {/* Tujuan cepat, peringatan paparan, dan panel dampak disisipkan dari
          App.jsx sebagai anak. Panel ini yang memiliki tata letak rail-nya,
          jadi urutan dan jaraknya diputuskan di sini; isinya diputuskan di
          sana. Pemisahan itu membuat PanelRute tidak perlu tahu apa pun
          tentang tujuan cepat maupun faktor emisi. */}
      {children}
    </aside>
  );
}
