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
import PanelDampak from "./components/PanelDampak.jsx";
import PeringatanPaparan from "./components/PeringatanPaparan.jsx";
import TujuanCepat from "./components/TujuanCepat.jsx";
import HalamanValidasi from "./pages/HalamanValidasi.jsx";
import { ambilJam, ambilRuas, ambilTujuanCepat, hitungRute } from "./lib/api.js";
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

  const [tujuanCepat, setTujuanCepat] = useState([]);
  const [memuatTujuan, setMemuatTujuan] = useState(true);
  const [tujuanTerpilih, setTujuanTerpilih] = useState(null);

  // Dua tampilan saja, jadi tidak perlu pustaka perutean. Menambah
  // react-router untuk satu halaman berarti membawa dependency,
  // pemuatan, dan satu lagi hal yang bisa rusak saat demo.
  const [tampilan, setTampilan] = useState("peta");

  useEffect(() => {
    document.title = t("aplikasi.nama");
  }, []);

  // ── Muat sumbu waktu SAJA ─────────────────────────────────────────
  //
  // KENAPA HANYA JAM, DAN KENAPA INI PERNAH SALAH.
  //
  // Versi sebelumnya menarik `/api/jam` dan `/api/ruas` bersama-sama dengan
  // `Promise.all`. Keduanya lalu menunggu yang paling lambat, dan yang paling
  // lambat jauh lebih besar: sumbu waktu 72 jam hanya beberapa kilobita,
  // sedangkan jaringan jalan 19.394 ruas berukuran 6,6 MB.
  //
  // Akibatnya Pita Pasut — elemen tanda tangan antarmuka ini — menampilkan
  // "belum dihitung" selama seluruh unduhan berlangsung, padahal datanya
  // sudah tiba sejak detik pertama. Di ponsel kelas menengah pada jaringan
  // seluler, yaitu pengguna yang disebut DESIGN.md bagian 1, layar pertama
  // tampak rusak selama puluhan detik.
  //
  // Lebih buruk lagi, `ambilRuas()` tanpa argumen di sini SIA-SIA: begitu
  // `jam` masuk, `waktuAktif` terisi dan efek di bawah segera menarik ulang
  // jaringan yang sama untuk jam aktif. Muat pertama mengunduh 13,2 MB dan
  // membuang separuhnya.
  //
  // Jadi di sini hanya sumbu waktu. Jaringan jalan dibiarkan diambil satu
  // kali oleh efek `waktuAktif`, yang memang harus berjalan.
  useEffect(() => {
    let dibatalkan = false;
    (async () => {
      setGalatMuat(null);
      try {
        const dataJam = await ambilJam();
        if (!dibatalkan) setJam(dataJam.jam ?? []);
      } catch (e) {
        if (dibatalkan) return;
        setGalatMuat(pesanGalat(e));
        // Tanpa jam, `waktuAktif` tidak pernah ada dan efek di bawah tidak
        // pernah berjalan. Penanda muat harus dilepas di sini, kalau tidak
        // peta tertahan pada "memuat" selamanya tanpa galat apa pun.
        setMemuat(false);
      }
    })();
    return () => { dibatalkan = true; };
  }, []);

  // ── Muat tujuan cepat, sekali ─────────────────────────────────────
  // Kegagalannya sengaja tidak memunculkan galat di layar: tujuan cepat
  // adalah jalan pintas, bukan syarat. Peta dan perutean tetap berguna
  // tanpanya, dan galat yang tidak menghalangi apa pun hanya menambah
  // kebisingan.
  useEffect(() => {
    let dibatalkan = false;
    (async () => {
      try {
        const data = await ambilTujuanCepat();
        if (!dibatalkan) setTujuanCepat(data.tujuan ?? []);
      } catch {
        if (!dibatalkan) setTujuanCepat([]);
      } finally {
        if (!dibatalkan) setMemuatTujuan(false);
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
      } finally {
        // Penanda muat peta ditutup DI SINI, bukan saat sumbu waktu tiba,
        // karena yang digerbanginya memang jaringan jalan.
        if (!dibatalkan) setMemuat(false);
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
    setAsal((asalSekarang) => {
      if (!asalSekarang) {
        setModePilih("tujuan");
        return [tj.lon, tj.lat];
      }
      setTujuan([tj.lon, tj.lat]);
      setModePilih("asal");
      return asalSekarang;
    });
  }, []);

  // Saran "berangkat pukul sekian" hanya berguna kalau bisa ditekan dan
  // langsung memindahkan Pita Pasut ke jam itu.
  const pilihJamAman = useCallback((jamAman) => {
    const i = jam.findIndex((j) => j.waktu_utc === jamAman.waktu_utc);
    if (i >= 0) setIndeksJam(i);
  }, [jam]);

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
          />
          <PeringatanPaparan
            paparan={hasil?.paparan}
            jamAman={hasil?.jam_lebih_aman}
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
