/**
 * App.jsx — susunan layar.
 *
 * Tata letak DESIGN.md Bagian 7: peta memenuhi layar, tidak ada kisi kartu.
 * Yang menumpang di atasnya hanya pelat instrumen kecil di sudut.
 *
 * Yang BELUM ada di milestone ini dan menyusul berikutnya: Pita Pasut,
 * formulir rute, panel dampak, peringatan paparan.
 */

import { useEffect, useState } from "react";

import Peta from "./components/Peta.jsx";
import LencanaContoh from "./components/LencanaContoh.jsx";
import Legenda from "./components/Legenda.jsx";
import { ambilKesehatan, ambilRuas } from "./lib/api.js";
import { t } from "./lib/teks.js";

/* Nama hari pendek, diambil dari copy.id.json. Urutannya mengikuti
   Date.getDay(): 0 adalah Minggu. */
const KUNCI_HARI = [
  "waktu.minggu", "waktu.senin", "waktu.selasa", "waktu.rabu",
  "waktu.kamis", "waktu.jumat", "waktu.sabtu",
];

/**
 * Susun label jam dalam WIB dari potongan yang sudah ada di copy.id.json.
 *
 * Waktu datang dari server dalam UTC. Aturan repo: simpan UTC, tampilkan
 * WIB. Konversinya terjadi di sini, di lapisan tampilan, dan tidak di
 * tempat lain.
 */
function labelJamWib(isoUtc) {
  if (!isoUtc) return "";
  const tanggal = new Date(isoUtc);

  // Intl dipakai untuk memaksa zona Asia/Jakarta, bukan zona laptop yang
  // sedang membuka aplikasi. Anggota tim di Surabaya dan juri di Semarang
  // sama-sama harus melihat WIB.
  const bagian = new Intl.DateTimeFormat("id-ID", {
    timeZone: "Asia/Jakarta",
    weekday: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    hour12: false,
  }).formatToParts(tanggal);

  const ambil = (jenis) => bagian.find((b) => b.type === jenis)?.value ?? "";

  // Nama hari diambil dari copy.id.json, bukan dari keluaran Intl, supaya
  // singkatannya seragam dengan sisa antarmuka. Untuk memetakannya, hari
  // dibaca sekali dalam bahasa Inggris di zona Asia/Jakarta lalu dicari
  // indeksnya. Tidak bisa memakai getDay() begitu saja, karena itu
  // mengembalikan hari menurut zona waktu laptop yang membuka aplikasi.
  const HARI_INGGRIS = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
  ];
  const hariInggris = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Jakarta",
    weekday: "long",
  }).format(tanggal);
  const indeksHari = Math.max(0, HARI_INGGRIS.indexOf(hariInggris));

  const hari = t(KUNCI_HARI[indeksHari]);
  const jam = t("waktu.formatJam", { jam: ambil("hour"), menit: ambil("minute") });

  return `${hari} ${ambil("day")} · ${t("waktu.pukul")} ${jam} ${t("waktu.zona")}`;
}

export default function App() {
  const [kesehatan, setKesehatan] = useState(null);
  const [geojson, setGeojson] = useState(null);
  const [galat, setGalat] = useState(null);
  const [memuat, setMemuat] = useState(true);

  useEffect(() => {
    document.title = t("aplikasi.nama");
  }, []);

  useEffect(() => {
    let dibatalkan = false;

    async function muat() {
      setMemuat(true);
      setGalat(null);
      try {
        const [k, r] = await Promise.all([ambilKesehatan(), ambilRuas()]);
        if (dibatalkan) return;
        setKesehatan(k);
        setGeojson(r);
      } catch (e) {
        if (dibatalkan) return;
        // Galat menjelaskan apa yang terjadi dan apa yang bisa dilakukan.
        // Tidak meminta maaf, tidak kabur, tidak memakai tanda seru.
        setGalat(e.message || t("galat.serverTidakMerespons"));
      } finally {
        if (!dibatalkan) setMemuat(false);
      }
    }

    muat();
    return () => {
      dibatalkan = true;
    };
  }, []);

  const sumberData = geojson?.sumber_data ?? kesehatan?.sumber_data ?? [];

  return (
    <div className="layar">
      <a className="lewati" href="#konten-utama">
        {t("aksesibilitas.lewatiKeKonten")}
      </a>

      {/* Peta adalah konten dan mengisi seluruh layar. Elemen di bawah ini
          menumpang di atasnya sebagai pelat instrumen, bukan sebagai kartu
          yang menjadikan peta sekadar latar. */}
      <Peta geojson={geojson} />

      <div className="plat plat--kiri-atas">
        <div className="plat__judul t-judul">{t("aplikasi.nama")}</div>
        <div className="plat__anak t-label">{t("aplikasi.wilayah")}</div>
        {geojson?.waktu_utc ? (
          <div className="plat__jam t-data">{labelJamWib(geojson.waktu_utc)}</div>
        ) : null}
      </div>

      <LencanaContoh sumberData={sumberData} />

      <div className="plat plat--kiri-bawah">
        <Legenda />
      </div>

      <div className="atribusi t-label">{t("peta.atribusi")}</div>

      {memuat ? (
        <div className="pesan" role="status">
          <span className="t-bagian">{t("memuat.jaringanJalan")}</span>
        </div>
      ) : null}

      {galat ? (
        <div className="pesan pesan--galat" role="alert">
          <span className="t-bagian">{t("galat.serverTidakMerespons")}</span>
          <span className="pesan__rincian t-data">{galat}</span>
        </div>
      ) : null}
    </div>
  );
}
