/**
 * App.jsx — susunan layar.
 *
 * Tata letak DESIGN.md Bagian 7: peta memenuhi layar, tidak ada kisi kartu.
 * Rail kiri berbadan gelap berisi kontrol dan hasil, Pita Pasut melintang
 * penuh di bawah.
 *
 * Pengambilan data, pembatalan request, dan percobaan ulang ada di
 * usePerjalanan agar interaksi peta dan panel memakai waktu yang sama.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import Peta from "./components/Peta.jsx";
import PitaPasut from "./components/PitaPasut.jsx";
import PanelRute from "./components/PanelRute.jsx";
import LencanaContoh from "./components/LencanaContoh.jsx";
import Legenda from "./components/Legenda.jsx";
import PanelDampak from "./components/PanelDampak.jsx";
import PeringatanPaparan from "./components/PeringatanPaparan.jsx";
import TujuanCepat from "./components/TujuanCepat.jsx";
import HalamanValidasi from "./pages/HalamanValidasi.jsx";
import { ambilTujuanCepat } from "./lib/api.js";
import { usePerjalanan } from "./lib/usePerjalanan.js";
import { t } from "./lib/teks.js";
import { labelHariJam } from "./lib/waktu.js";
import { namaLokasi } from "./lib/lokasi.js";

export default function App() {
  const [petaDasar, setPetaDasar] = useState("memuat");
  const [asal, setAsal] = useState(null);
  const [tujuan, setTujuan] = useState(null);
  const [modePilih, setModePilih] = useState("asal");
  const [moda, setModa] = useState("motor");

  const { jam, infoJam, indeksJam, setIndeksJam, waktuAktif, waktuTersedia,
    geojson, kondisi, hasil, memuat, memuatJam, galatMuat, sedangMencari,
    galatRute, cariUlang, muatUlang } = usePerjalanan(asal, tujuan, moda);
  const [tampilkanRuteBiasa, setTampilkanRuteBiasa] = useState(true);

  const [tujuanCepat, setTujuanCepat] = useState([]);
  const [memuatTujuan, setMemuatTujuan] = useState(true);
  const [galatTujuan, setGalatTujuan] = useState(false);
  const [ulangTujuan, setUlangTujuan] = useState(0);
  const [tujuanTerpilih, setTujuanTerpilih] = useState(null);
  const namaAsal = useMemo(() => namaLokasi(asal, geojson, tujuanCepat), [asal, geojson, tujuanCepat]);
  const namaTujuan = useMemo(() => namaLokasi(tujuan, geojson, tujuanCepat), [tujuan, geojson, tujuanCepat]);

  // Dua tampilan saja, jadi tidak perlu pustaka perutean. Menambah
  // react-router untuk satu halaman berarti membawa dependency,
  // pemuatan, dan satu lagi hal yang bisa rusak saat demo.
  const [tampilan, setTampilan] = useState("peta");

  useEffect(() => {
    document.title = t("aplikasi.nama");
  }, []);

  useEffect(() => {
    const c = new AbortController();
    setMemuatTujuan(true);
    setGalatTujuan(false);
    ambilTujuanCepat({ signal: c.signal }).then((data) => {
      if (!c.signal.aborted) setTujuanCepat(data.tujuan ?? []);
    }).catch(() => { if (!c.signal.aborted) setGalatTujuan(true); }).finally(() => {
      if (!c.signal.aborted) setMemuatTujuan(false);
    });
    return () => c.abort();
  }, [ulangTujuan]);

  const klikPeta = useCallback((koordinat) => {
    if (modePilih === "asal") {
      setAsal(koordinat);
      setModePilih("tujuan");
    } else {
      setTujuan(koordinat);
      setModePilih("asal");
    }
  }, [modePilih]);

  const hapusTitik = useCallback((peran) => {
    if (peran === "asal") setAsal(null);
    else setTujuan(null);
    setModePilih(peran);
  }, []);

  // Tombol tujuan cepat mengisi SLOT YANG MASIH KOSONG: asal lebih dulu,
  // lalu tujuan.
  //
  // Rancangan awalnya selalu mengisi tujuan, dan itu keliru untuk pameran.
  // Orang yang baru melihat aplikasi ini menekan satu tombol lalu menunggu
  // sesuatu terjadi. Kalau asal masih kosong, tidak ada yang terjadi, dan ia
  // menyimpulkan aplikasinya rusak — padahal ia hanya belum tahu harus
  // mengetuk peta lebih dulu. Dengan mengisi slot kosong, dua kali tekan
  // sudah menghasilkan rute tanpa perlu dituntun sama sekali.
  const pilihTujuanCepat = useCallback((tj) => {
    setTujuanTerpilih(tj.kunci);
    if (!asal) {
      setAsal([tj.lon, tj.lat]);
      setModePilih("tujuan");
    } else {
      setTujuan([tj.lon, tj.lat]);
      setModePilih("asal");
    }
  }, [asal]);

  const pilihJamAman = useCallback((jamAman) => {
    const i = jam.findIndex((j) => Date.parse(j.waktu_utc) === Date.parse(jamAman.waktu_utc));
    if (i >= 0 && jam[i].tersedia) setIndeksJam(i);
  }, [jam]);

  const sumberData = hasil?.sumber_data ?? kondisi?.sumber_data ?? infoJam?.sumber_data ?? [];

  // Rute yang dikirim ke peta. Rute pembanding bisa disembunyikan pengguna,
  // tetapi rute sadar rob tidak pernah.
  const ruteTampil = hasil?.rute
    ? {
        ...hasil.rute,
        features: hasil.rute.features.filter(
          (f) => tampilkanRuteBiasa || f.properties.jenis !== "rute_abai_rob"
        ),
      }
    : null;

  if (tampilan === "validasi") {
    return <HalamanValidasi onKembali={() => setTampilan("peta")} />;
  }

  return (
    <div className="layar">
      <a className="lewati" href="#konten-utama">
        {t("aksesibilitas.lewatiKeKonten")}
      </a>

      <div className="layar__isi">
        <PanelRute
          asal={asal}
          tujuan={tujuan}
          namaAsal={namaAsal}
          namaTujuan={namaTujuan}
          modePilih={modePilih}
          moda={moda}
          hasil={hasil}
          sedangMencari={sedangMencari}
          galat={galatRute}
          tampilkanRuteBiasa={tampilkanRuteBiasa}
          onPilihMode={setModePilih}
          onHapusTitik={hapusTitik}
          onGantiModa={setModa}
          onCari={cariUlang}
          waktuTersedia={waktuTersedia}
          onTampilkanRuteBiasa={() => setTampilkanRuteBiasa((v) => !v)}
        >
          <button
            type="button"
            className="rail__tautan-validasi"
            onClick={() => setTampilan("validasi")}
          >
            {t("navigasi.validasi")}
          </button>
          <TujuanCepat
            daftar={tujuanCepat}
            memuat={memuatTujuan}
            terpilih={tujuanTerpilih}
            onPilih={pilihTujuanCepat}
            galat={galatTujuan}
            onUlang={() => setUlangTujuan((n) => n + 1)}
          />
          <PeringatanPaparan
            paparan={hasil?.paparan}
            jamAman={hasil?.jam_lebih_aman}
            waktu={hasil?.waktu_berangkat_utc}
            bisaPilihJam={jam.some((j) => j.tersedia && Date.parse(j.waktu_utc) === Date.parse(hasil?.jam_lebih_aman?.waktu_utc))}
            namaJalan={
              hasil?.rute?.features?.find(
                (f) => f.properties.jenis === "rute_sadar_rob"
              )?.properties?.nama_jalan
            }
            onPilihJam={pilihJamAman}
          />
          <PanelDampak dampak={hasil?.dampak} moda={moda} />
        </PanelRute>

        <div className="jendela-peta">
          <Peta
            geojson={geojson}
            kondisi={kondisi}
            rute={ruteTampil}
            asal={asal}
            tujuan={tujuan}
            onKlikPeta={klikPeta}
            onStatusPetaDasar={setPetaDasar}
          />

          <div className="plat plat--kiri-atas">
            <div className="plat__judul t-judul">{t("aplikasi.nama")}</div>
            <div className="plat__anak t-label">{t("aplikasi.wilayah")}</div>
            <div className="plat__anak t-label" role="status">{t(`petaDasar.${petaDasar}`)}</div>
            {infoJam?.asal_jaringan === "potret" ? <div className="t-label">{t("peta.potretDemo")}</div> : null}
            {waktuAktif ? (
              <div className="plat__jam t-data">{labelHariJam(waktuAktif)}</div>
            ) : null}
          </div>

          <LencanaContoh sumberData={sumberData} />

          <div className="plat plat--kiri-bawah">
            <Legenda />
            {!kondisi ? <p className="peta__keterangan-batas t-label">{t('peta.kondisiBelumTersedia')}</p> : null}
            <p className="peta__keterangan-batas t-label">{t("peta.batasWilayah")}</p>
          </div>

          <div className="atribusi t-label">
            <span className="atribusi__petunjuk">
              {modePilih === "asal"
                ? t("peta.ketukUntukAsal")
                : t("peta.ketukUntukTujuan")}
            </span>
            {/* Atribusi OpenStreetMap wajib tampil. Lisensi ODbL menuntutnya,
                dan ia tidak boleh digeser oleh petunjuk sesaat. */}
            <span><a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">{t("peta.atribusi")}</a>{" | "}<a href="https://carto.com/attributions" target="_blank" rel="noreferrer">{t("petaDasar.carto")}</a></span>
          </div>

          {memuat ? (
            <div className="pesan pesan--muat" role="status" aria-live="polite">
              <span className="t-bagian">{t(geojson ? "memuat.memperbarui" : "memuat.jaringanJalan")}</span>
              <span className="t-label pesan__rincian">
                {t("memuat.jaringanJalanRincian")}
              </span>
            </div>
          ) : null}

          {galatMuat ? (
            <div className="pesan pesan--galat" role="alert">
              <span className="t-bagian">{galatMuat}</span>
              <button type="button" className="tombol-utama" onClick={muatUlang}>{t("pencarianRute.cariUlang")}</button>
            </div>
          ) : null}
        </div>
      </div>

      <PitaPasut jam={jam} indeks={indeksJam} onPilih={setIndeksJam}
                 memuat={memuatJam} />
    </div>
  );
}
