/**
 * Peta.jsx — jendela peta. Memenuhi layar, bukan diletakkan di dalam kartu.
 *
 * Peta adalah KONTEN, bukan latar. Tidak ada lapisan kartu yang menutupinya;
 * yang menumpang di atasnya hanya pelat instrumen kecil di sudut.
 *
 * Peta dasar OSM siap pakai dari CARTO dipilih tim untuk rilis final.
 * Data genangan dan perutean tetap berasal dari API PASANG SURUT.
 */

import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import "maplibre-gl/dist/maplibre-gl.css";

// ESM v6 memerlukan worker terbundel; ?url saja kehilangan impor sibling.
maplibregl.setWorkerUrl(workerUrl);

import { token, tokenPx } from "../lib/token.js";
import { t } from "../lib/teks.js";
import { pasangLabelPeta } from "../lib/labelPeta.js";
import { buatLabelJalan } from "../lib/jalanLabel.js";
import { GAYA_OSM, tataPetaDasar } from "../lib/petaDasar.js";

/* Batas kelas tangga kedalaman, DESIGN.md Bagian 3.4.
   Nilainya sentimeter. */
const BATAS_TIPIS = 1;
const BATAS_SEDANG = 10;
const BATAS_DALAM = 25;
const BATAS_SANGAT_DALAM = 50;

/**
 * Buat gambar pola titik halftone untuk ditumpuk di atas warna kedalaman.
 *
 * KENAPA POLA INI WAJIB ADA. DESIGN.md Bagian 3.4: kedalaman tidak pernah
 * disampaikan lewat warna saja. Dua kelas terdalam harus bisa dibedakan
 * juga oleh pengguna buta warna, dan harus tetap terbaca saat tangkapan
 * layar dicetak hitam putih di proposal. Warna --air-3 dan --air-4 punya
 * luminansi yang berdekatan; dicetak abu-abu keduanya nyaris sama. Pola
 * titik dengan kerapatan berbeda itulah yang membedakannya.
 *
 * @param {number} sisi      ukuran ubin dalam piksel; makin kecil makin rapat
 * @param {number} jariJari  jari-jari titik
 * @param {string} warna     warna titik, diambil dari token
 */
function buatPolaTitik(sisi, jariJari, warna) {
  const skala = 2; // gambar dua kali lipat supaya tidak pecah di layar rapat
  const kanvas = document.createElement("canvas");
  kanvas.width = sisi * skala;
  kanvas.height = sisi * skala;
  const kuas = kanvas.getContext("2d");

  // Latar dibiarkan transparan supaya warna kedalaman di lapisan bawah
  // tetap terlihat di sela-sela titik.
  kuas.clearRect(0, 0, kanvas.width, kanvas.height);
  kuas.fillStyle = warna;

  // Dua titik diletakkan berselang seperti kisi halftone sungguhan,
  // bukan satu titik di tengah yang akan tampak seperti garis putus-putus.
  const titik = [
    [sisi * 0.25, sisi * 0.25],
    [sisi * 0.75, sisi * 0.75],
  ];
  for (const [x, y] of titik) {
    kuas.beginPath();
    kuas.arc(x * skala, y * skala, jariJari * skala, 0, Math.PI * 2);
    kuas.fill();
  }

  return {
    data: kuas.getImageData(0, 0, kanvas.width, kanvas.height),
    pixelRatio: skala,
  };
}

/** Ekspresi MapLibre: warna ruas menurut tangga kedalaman. */
function ekspresiWarnaKedalaman() {
  return [
    "step",
    ["coalesce", ["feature-state", "kedalaman_cm"], 0],
    token("--air-1"),
    BATAS_SEDANG, token("--air-2"),
    BATAS_DALAM, token("--air-3"),
    BATAS_SANGAT_DALAM, token("--air-4"),
  ];
}

/**
 * Ekspresi MapLibre: lebar ruas menebal seiring kedalaman.
 * DESIGN.md Bagian 8 — 3px kering, menebal sampai 6px seiring kedalaman.
 */
function ekspresiLebarKedalaman() {
  const kering = tokenPx("--ruas-lebar-kering");
  const dalam = tokenPx("--ruas-lebar-dalam");
  return [
    "interpolate", ["linear"], ["coalesce", ["feature-state", "kedalaman_cm"], 0],
    0, kering,
    BATAS_SANGAT_DALAM, dalam,
  ];
}

export default function Peta({ geojson, kondisi, rute, asal, tujuan, onKlikPeta, onSiap, onStatusPetaDasar }) {
  const wadahRef = useRef(null);
  const petaRef = useRef(null);
  const basahRef = useRef([]);

  // Peta baru bisa menerima data setelah event load selesai. Data dari API
  // sering tiba lebih dulu, jadi kesiapan itu disimpan sebagai state supaya
  // efek pembaruan data ikut dijalankan ulang saat peta akhirnya siap.
  // Tanpa ini, GeoJSON yang datang duluan akan hilang begitu saja dan peta
  // tetap kosong meski tidak ada satu pun galat di console.
  const [siap, setSiap] = useState(false);
  const [galatGrafis, setGalatGrafis] = useState(false);

  // Handler klik disimpan di ref, bukan ditutup langsung di dalam efek
  // pembuatan peta. Kalau ditutup langsung, ia akan memegang nilai state
  // dari render pertama selamanya.
  const klikRef = useRef(null);
  klikRef.current = onKlikPeta;

  // ── Pembuatan peta, sekali saja ────────────────────────────────────
  useEffect(() => {
    if (petaRef.current || !wadahRef.current) return;
    let dibatalkan = false;

    let lokal = false;
    const gayaLokal = {
        version: 8,
        // Tanpa URL glyphs: MapLibre menggambar teks melalui TinySDF
        // memakai font lokal yang sudah dibundel, tanpa layanan glyph luar.
        sources: {},
        layers: [
          {
            id: "latar-dek",
            type: "background",
            // Jendela peta terang di atas badan instrumen gelap.
            paint: { "background-color": token("--dek-1") },
          },
        ],
      };
    onStatusPetaDasar?.("memuat");
    let peta;
    try {
      peta = new maplibregl.Map({
      container: wadahRef.current,
      style: GAYA_OSM,
      // Pusat dan zoom awal diisi ulang oleh fitBounds begitu data datang.
      center: [110.4425, -6.96],
      zoom: 12,
      attributionControl: false,
      // Peta ini dipakai sambil berdiri dan terburu-buru. Rotasi hanya
      // membuat pengguna tersesat, jadi dimatikan.
      pitchWithRotate: false,
      dragRotate: false,
      touchZoomRotate: true,
      });
      // MapLibre dapat mengembalikan objek parsial saat inisialisasi GPU
      // gagal, tanpa melempar exception dari constructor.
      if (!peta.touchZoomRotate) throw new Error('Map initialization failed');
      peta.touchZoomRotate.disableRotation();
    } catch {
      setGalatGrafis(true);
      return;
    }
    const batasMuat = setTimeout(() => {
      if (dibatalkan || peta.loaded()) return;
      lokal = true;
      onStatusPetaDasar?.("lokal");
      peta.setStyle(gayaLokal);
    }, 10000);

    // Kontrol perbesar dan perkecil. Labelnya diambil dari copy.id.json
    // supaya tidak ada teks Inggris bawaan yang lolos ke layar.
    const kontrol = new maplibregl.NavigationControl({ showCompass: false });
    peta.addControl(kontrol, "bottom-right");
    if (import.meta.env.DEV) window.__peta = peta;

    peta.on("error", (e) => console.warn("[peta]", e && e.error));
    peta.on("load", async () => {
      clearTimeout(batasMuat);
      // Tunggu font sebelum glyph pertama dirasterisasi; jika terlalu awal,
      // font fallback akan tersimpan di cache glyph sepanjang umur peta.
      await document.fonts.load('400 24px "Barlow Semi Condensed"').catch(() => {});
      if (dibatalkan) return;
      if (!lokal) {
        // Font label aplikasi tidak ada di server glyph CARTO. Pakai font
        // bundel untuk semua teks, sambil mempertahankan layer/gaya basemap.
        peta.setGlyphs(null);
        for (const layer of peta.getStyle().layers) {
          if (layer.type === "symbol" && layer.layout?.["text-field"]) {
            peta.setLayoutProperty(layer.id, "text-font", ["Barlow Semi Condensed"]);
          }
        }
      }
      // Pola halftone didaftarkan sebelum lapisan yang memakainya dibuat.
      const warnaTitik = token("--dek-1");
      const jarang = buatPolaTitik(10, 1.4, warnaTitik);
      const rapat = buatPolaTitik(6, 1.3, warnaTitik);
      peta.addImage("titik-jarang", jarang.data, { pixelRatio: jarang.pixelRatio });
      peta.addImage("titik-rapat", rapat.data, { pixelRatio: rapat.pixelRatio });

      peta.addSource("ruas", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });

      // ── Lapisan 1: jaringan jalan itu sendiri ─────────────────────
      // Digambar untuk SELURUH ruas, tergenang maupun tidak. Tanpa lapisan
      // ini, ruas kering tidak akan terlihat sama sekali karena --air-0
      // bernilai transparent.
      peta.addLayer({
        id: "ruas-dasar",
        type: "line",
        source: "ruas",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          // --tinta-2, BUKAN --tinta-3, karena dua alasan yang keduanya
          // terukur.
          //
          // Pertama, kontras. --tinta-3 di atas --dek-1 hanya 2,80:1,
          // di bawah ambang 3:1 yang dituntut untuk objek grafis, dan
          // DESIGN.md Bagian 11 mensyaratkan peta ini terbaca di bawah
          // matahari langsung. --tinta-2 memberi 5,86:1.
          //
          // Kedua, --rute-abai dan --tinta-3 adalah nilai heks yang SAMA
          // PERSIS. Menggambar jalan dengan --tinta-3 membuat rute
          // pembanding yang putus-putus lenyap di atas jalan, padahal
          // selisih antara kedua rute justru argumen produk ini.
          "line-color": token("--tinta-2"),
          // Jalan utama digambar sedikit lebih tebal supaya rangka kota
          // terbaca sekilas dari jarak dua meter, sesuai kebutuhan pameran.
          "line-width": [
            "interpolate", ["linear"], ["zoom"],
            11, ["match", ["get", "jenis"],
              ["trunk", "primary"], 1.6,
              ["secondary", "tertiary"], 1.1,
              0.6],
            16, ["match", ["get", "jenis"],
              ["trunk", "primary"], 4.5,
              ["secondary", "tertiary"], 3.2,
              1.8],
          ],
        },
      });

      // ── Lapisan 2: warna kedalaman genangan ───────────────────────
      peta.addLayer({
        id: "ruas-air",
        type: "line",
        source: "ruas",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-opacity": ["case", [">=", ["coalesce", ["feature-state", "kedalaman_cm"], 0], BATAS_TIPIS], 1, 0],
          "line-color": ekspresiWarnaKedalaman(),
          "line-width": ekspresiLebarKedalaman(),
          // Satu-satunya animasi di aplikasi ini: ruas terisi dan surut saat
          // jam berganti. DESIGN.md Bagian 9.
          "line-width-transition": {
            duration: tokenPx("--gerak-air"),
            delay: 0,
          },
        },
      });

      // ── Lapisan 3 dan 4: pola titik untuk dua kelas terdalam ──────
      // line-pattern menggantikan line-color sepenuhnya, jadi lapisan ini
      // ditumpuk DI ATAS lapisan warna, bukan menggantikannya. Titiknya
      // buram, sela-selanya transparan, sehingga warna di bawahnya tembus.
      peta.addLayer({
        id: "ruas-air-pola-dalam",
        type: "line",
        source: "ruas",
        layout: { "line-cap": "butt", "line-join": "round" },
        paint: {
          "line-opacity": ["case", [
          "all",
          [">=", ["coalesce", ["feature-state", "kedalaman_cm"], 0], BATAS_DALAM],
          ["<", ["coalesce", ["feature-state", "kedalaman_cm"], 0], BATAS_SANGAT_DALAM],
        ], 1, 0],
          "line-pattern": "titik-jarang",
          "line-width": ekspresiLebarKedalaman(),
        },
      });

      peta.addLayer({
        id: "ruas-air-pola-sangat-dalam",
        type: "line",
        source: "ruas",
        layout: { "line-cap": "butt", "line-join": "round" },
        paint: {
          "line-opacity": ["case", [">=", ["coalesce", ["feature-state", "kedalaman_cm"], 0], BATAS_SANGAT_DALAM], 1, 0],
          "line-pattern": "titik-rapat",
          "line-width": ekspresiLebarKedalaman(),
        },
      });

      // ── Lapisan 5 sampai 8: rute ──────────────────────────────────
      // DESIGN.md Bagian 8. Keduanya tampil BERSAMAAN dengan sengaja:
      // selisih antara rute yang menembus genangan dan rute yang
      // menghindarinya adalah argumen produk ini. Menyembunyikan
      // pembandingnya berarti mengklaim penghematan tanpa dasar.
      peta.addSource("rute", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });

      // Rute pembanding: putus-putus, tipis, warna mati.
      peta.addLayer({
        id: "rute-abai",
        type: "line",
        source: "rute",
        filter: ["==", ["get", "jenis"], "rute_abai_rob"],
        layout: { "line-cap": "butt", "line-join": "round" },
        paint: {
          "line-color": token("--rute-abai"),
          "line-width": tokenPx("--rute-abai-lebar"),
          "line-dasharray": [2, 2],
        },
      });

      // Garis luar gelap 1px di tiap sisi, supaya rute ambar tetap terbaca
      // saat melintas di atas air biru tua.
      peta.addLayer({
        id: "rute-sadar-luar",
        type: "line",
        source: "rute",
        filter: ["==", ["get", "jenis"], "rute_sadar_rob"],
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": token("--lambung-1"),
          "line-width": tokenPx("--rute-lebar") + 2,
        },
      });

      peta.addLayer({
        id: "rute-sadar",
        type: "line",
        source: "rute",
        filter: ["==", ["get", "jenis"], "rute_sadar_rob"],
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": token("--rute"),
          "line-width": tokenPx("--rute-lebar"),
        },
      });

      // Titik berangkat dan tujuan.
      peta.addSource("titik", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });
      peta.addLayer({
        id: "titik-cincin",
        type: "circle",
        source: "titik",
        paint: {
          "circle-radius": 9,
          "circle-color": token("--lambung-1"),
          "circle-stroke-color": token("--rute"),
          "circle-stroke-width": 2,
        },
      });
      peta.addLayer({
        id: "titik-inti",
        type: "circle",
        source: "titik",
        paint: {
          "circle-radius": 3.5,
          "circle-color": [
            "match", ["get", "peran"],
            "asal", token("--rute"),
            token("--aman"),
          ],
        },
      });

      pasangLabelPeta(peta);
      if (!lokal) tataPetaDasar(peta);
      onStatusPetaDasar?.(lokal ? "lokal" : "osm");
      petaRef.current = peta;
      setSiap(true);

      // Kait pengembangan. Verifikasi otomatis perlu memproyeksikan
      // bujur-lintang ke piksel layar untuk mengetuk titik yang tepat, dan
      // itu hanya bisa dilakukan lewat instance peta. Tidak ikut ke hasil
      // build produksi karena import.meta.env.DEV bernilai salah di sana.
      if (import.meta.env.DEV) window.__peta = peta;

      if (onSiap) onSiap(peta);
    });

    // Ketuk peta untuk memilih titik. Handler disimpan di ref supaya
    // pendengar tidak perlu dipasang ulang tiap kali fungsi berubah.
    peta.on("click", (e) => {
      const fn = klikRef.current;
      if (!fn) return;
      const tempat = peta.getLayer("nama-tempat")
        ? peta.queryRenderedFeatures(e.point, { layers: ["nama-tempat", "tempat-titik"] })[0]
        : null;
      // Label berada di lokasi asli tempat; perjalanan menuju akses jalan
      // yang sudah dipakai tombol tujuan cepat, bukan pusat bangunannya.
      fn(tempat ? [tempat.properties.lon_rute, tempat.properties.lat_rute]
        : [e.lngLat.lng, e.lngLat.lat]);
    });
    peta.getCanvas().style.cursor = "crosshair";

    return () => {
      dibatalkan = true;
      clearTimeout(batasMuat);
      peta.remove();
      petaRef.current = null;
      setSiap(false);
    };
    // Sengaja hanya dijalankan sekali. Data masuk lewat efek di bawah.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Pembaruan data ─────────────────────────────────────────────────
  useEffect(() => {
    const peta = petaRef.current;
    if (!siap || !peta || !geojson) return;

    const sumber = peta.getSource("ruas");
    if (!sumber) return;
    sumber.setData(geojson);
    peta.getSource("label-jalan").setData(buatLabelJalan(geojson));

    // Peta digeser ke kotak pembatas data, sekali saja saat data pertama
    // datang. Kalau diulang setiap pembaruan jam, tampilan akan melompat
    // dan pengguna kehilangan tempat yang sedang dilihatnya.
    if (!peta._sudahDipaskan && geojson.features?.length) {
      const batas = new maplibregl.LngLatBounds();
      for (const fitur of geojson.features) {
        for (const koordinat of fitur.geometry.coordinates) {
          batas.extend(koordinat);
        }
      }
      peta.fitBounds(batas, { padding: 24, animate: false });
      peta._sudahDipaskan = true;
    }
  }, [geojson, siap]);

  // ── Pembaruan rute ─────────────────────────────────────────────────
  // Nilai per jam berubah melalui feature state; geometri tidak disalin
  // kembali ke worker MapLibre setiap slider digeser.
  useEffect(() => {
    const peta = petaRef.current;
    if (!siap || !peta || !peta.getSource("ruas")) return;
    for (const id of basahRef.current) peta.removeFeatureState({ source: "ruas", id });
    basahRef.current = [];
    for (const [id, kedalaman] of kondisi?.ruas ?? []) {
      peta.setFeatureState({ source: "ruas", id }, { kedalaman_cm: kedalaman });
      basahRef.current.push(id);
    }
  }, [kondisi, geojson, siap]);

  useEffect(() => {
    const peta = petaRef.current;
    if (!siap || !peta) return;
    const sumber = peta.getSource("rute");
    if (!sumber) return;

    // Fitur tanpa geometri, misalnya rute yang tidak ditemukan, dibuang
    // supaya MapLibre tidak menerima geometri null.
    const fitur = (rute?.features ?? []).filter((f) => f.geometry);
    sumber.setData({ type: "FeatureCollection", features: fitur });
  }, [rute, siap]);

  // ── Pembaruan titik berangkat dan tujuan ───────────────────────────
  useEffect(() => {
    const peta = petaRef.current;
    if (!siap || !peta) return;
    const sumber = peta.getSource("titik");
    if (!sumber) return;

    const fitur = [];
    if (asal) {
      fitur.push({
        type: "Feature",
        properties: { peran: "asal" },
        geometry: { type: "Point", coordinates: asal },
      });
    }
    if (tujuan) {
      fitur.push({
        type: "Feature",
        properties: { peran: "tujuan" },
        geometry: { type: "Point", coordinates: tujuan },
      });
    }
    sumber.setData({ type: "FeatureCollection", features: fitur });
  }, [asal, tujuan, siap]);

  return (
    <div
      ref={wadahRef}
      className="peta"
      id="konten-utama"
      role="region"
      aria-label={t("aksesibilitas.petaLabel")}
    >
      {galatGrafis ? <div className="pesan pesan--galat" role="alert">{t('peta.gagalGrafis')}</div> : null}
    </div>
  );
}
