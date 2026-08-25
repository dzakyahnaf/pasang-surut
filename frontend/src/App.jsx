/**
 * App.jsx — susunan layar.
 *
 * Tata letak DESIGN.md Bagian 7: peta memenuhi layar, tidak ada kisi kartu.
 * Rail kiri berbadan gelap berisi kontrol dan hasil, Pita Pasut melintang
 * penuh di bawah.
 *
 * Yang BELUM ada dan menyusul di milestone berikutnya: panel dampak dengan
 * empat angka, tombol tujuan cepat, dan halaman validasi.
 */

import { useCallback, useEffect, useState } from "react";

import Peta from "./components/Peta.jsx";
import PitaPasut from "./components/PitaPasut.jsx";
import PanelRute from "./components/PanelRute.jsx";
import LencanaContoh from "./components/LencanaContoh.jsx";
import Legenda from "./components/Legenda.jsx";
import { ambilJam, ambilRuas, hitungRute } from "./lib/api.js";
import { t } from "./lib/teks.js";
import { labelHariJam } from "./lib/waktu.js";

/** Ubah galat dari API menjadi kalimat yang ada di copy.id.json. */
function pesanGalat(e) {
  if (e?.kode === "asal_jauh_dari_jalan" || e?.kode === "tujuan_jauh_dari_jalan") {
    return t("galat.titikTerlaluJauhDariJalan");
  }
  if (e?.status === 503) return t("galat.serverTidakMerespons");
  if (e?.status === 422 || e?.status === 400) return t("galat.ruteGagal");
  return t("galat.serverTidakMerespons");
}

export default function App() {
  const [jam, setJam] = useState([]);
  const [indeksJam, setIndeksJam] = useState(0);
  const [geojson, setGeojson] = useState(null);
  const [memuat, setMemuat] = useState(true);
  const [galatMuat, setGalatMuat] = useState(null);

  const [asal, setAsal] = useState(null);
  const [tujuan, setTujuan] = useState(null);
  const [modePilih, setModePilih] = useState("asal");
  const [moda, setModa] = useState("motor");

  const [hasil, setHasil] = useState(null);
  const [sedangMencari, setSedangMencari] = useState(false);
  const [galatRute, setGalatRute] = useState(null);
  const [tampilkanRuteBiasa, setTampilkanRuteBiasa] = useState(true);

  useEffect(() => {
    document.title = t("aplikasi.nama");
  }, []);

  // ── Muat sumbu waktu dan jaringan jalan ───────────────────────────
  useEffect(() => {
    let dibatalkan = false;
    (async () => {
      setMemuat(true);
      setGalatMuat(null);
      try {
        const [dataJam, dataRuas] = await Promise.all([ambilJam(), ambilRuas()]);
        if (dibatalkan) return;
        setJam(dataJam.jam ?? []);
        setGeojson(dataRuas);
      } catch (e) {
        if (!dibatalkan) setGalatMuat(pesanGalat(e));
      } finally {
        if (!dibatalkan) setMemuat(false);
      }
    })();
    return () => { dibatalkan = true; };
  }, []);

  // ── Jam berganti: muat ulang lapisan genangan ─────────────────────
  const waktuAktif = jam[indeksJam]?.waktu_utc ?? null;

  useEffect(() => {
    if (!waktuAktif) return;
    let dibatalkan = false;
    (async () => {
      try {
        const data = await ambilRuas(waktuAktif);
        if (!dibatalkan) setGeojson(data);
      } catch (e) {
        if (!dibatalkan) setGalatMuat(pesanGalat(e));
      }
    })();
    return () => { dibatalkan = true; };
  }, [waktuAktif]);

  // Rute ikut dihitung ulang saat jam berganti, selama kedua titik sudah
  // dipilih. Inilah yang membuat menggeser Pita Pasut benar-benar mengubah
  // rute di layar, bukan hanya mengubah warna genangan.
  useEffect(() => {
    if (!waktuAktif || !asal || !tujuan) return;
    let dibatalkan = false;
    (async () => {
      setSedangMencari(true);
      setGalatRute(null);
      try {
        const data = await hitungRute({
          asal, tujuan, waktu: waktuAktif, moda,
        });
        if (!dibatalkan) setHasil(data);
      } catch (e) {
        if (!dibatalkan) { setHasil(null); setGalatRute(pesanGalat(e)); }
      } finally {
        if (!dibatalkan) setSedangMencari(false);
      }
    })();
    return () => { dibatalkan = true; };
  }, [waktuAktif, asal, tujuan, moda]);

  // ── Ketuk peta memilih titik ──────────────────────────────────────
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
    setHasil(null);
    setGalatRute(null);
    setModePilih(peran);
  }, []);

  const sumberData = hasil?.sumber_data ?? geojson?.sumber_data ?? [];

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

  return (
    <div className="layar">
      <a className="lewati" href="#konten-utama">
        {t("aksesibilitas.lewatiKeKonten")}
      </a>

      <div className="layar__isi">
        <PanelRute
          asal={asal}
          tujuan={tujuan}
          modePilih={modePilih}
          moda={moda}
          hasil={hasil}
          sedangMencari={sedangMencari}
          galat={galatRute}
          tampilkanRuteBiasa={tampilkanRuteBiasa}
          onPilihMode={setModePilih}
          onHapusTitik={hapusTitik}
          onGantiModa={setModa}
          onCari={() => setIndeksJam((i) => i)}
          onTampilkanRuteBiasa={() => setTampilkanRuteBiasa((v) => !v)}
        />

        <div className="jendela-peta">
          <Peta
            geojson={geojson}
            rute={ruteTampil}
            asal={asal}
            tujuan={tujuan}
            onKlikPeta={klikPeta}
          />

          <div className="plat plat--kiri-atas">
            <div className="plat__judul t-judul">{t("aplikasi.nama")}</div>
            <div className="plat__anak t-label">{t("aplikasi.wilayah")}</div>
            {waktuAktif ? (
              <div className="plat__jam t-data">{labelHariJam(waktuAktif)}</div>
            ) : null}
          </div>

          <LencanaContoh sumberData={sumberData} />

          <div className="plat plat--kiri-bawah">
            <Legenda />
          </div>

          <div className="atribusi t-label">
            <span className="atribusi__petunjuk">
              {modePilih === "asal"
                ? t("peta.ketukUntukAsal")
                : t("peta.ketukUntukTujuan")}
            </span>
            {/* Atribusi OpenStreetMap wajib tampil. Lisensi ODbL menuntutnya,
                dan ia tidak boleh digeser oleh petunjuk sesaat. */}
            <span>{t("peta.atribusi")}</span>
          </div>

          {memuat ? (
            <div className="pesan" role="status">
              <span className="t-bagian">{t("memuat.jaringanJalan")}</span>
            </div>
          ) : null}

          {galatMuat ? (
            <div className="pesan pesan--galat" role="alert">
              <span className="t-bagian">{galatMuat}</span>
            </div>
          ) : null}
        </div>
      </div>

      <PitaPasut jam={jam} indeks={indeksJam} onPilih={setIndeksJam} />
    </div>
  );
}
