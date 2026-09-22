/**
 * PitaPasut.jsx — elemen tanda tangan produk. DESIGN.md Bagian 6.
 *
 * INI BUKAN PEMILIH TANGGAL, dan tidak boleh diganti pemilih tanggal.
 * DESIGN.md Bagian 12 butir 10 menyebutnya sebagai penolakan.
 *
 * Alasannya ada di kepala pengguna, bukan di kode. Pengguna tidak sedang
 * bertanya "bagaimana keadaan jam empat sore". Pengguna sedang bertanya
 * "kapan saya sebaiknya berangkat". Pemilih tanggal memaksa mereka menebak
 * satu jam demi satu jam. Pita Pasut menjawabnya dalam satu pandangan:
 * jendela merah terlihat, jendela aman terlihat.
 *
 * Kontrak prop onPilih: menerima nomor indeks, ATAU fungsi yang memetakan
 * indeks sebelumnya menjadi indeks baru — sama seperti penyetel state React.
 * Bentuk fungsi dipakai untuk perpindahan lewat papan ketik; alasannya ada
 * di komentar saatTombol().
 *
 * Yang digambar:
 *   - Kurva pasang surut 72 jam sebagai kurva sungguhan
 *   - Kolom air di bawah kurva, satu-satunya gradien yang diizinkan di
 *     seluruh aplikasi ini (DESIGN.md Bagian 3.6 butir 3)
 *   - Jam berisiko genangan diarsir --bahaya
 *   - Jam aman ditandai --aman
 *   - Guratan jam bergradasi seperti papan duga air: panjang tiap 6 jam,
 *     pendek tiap jam
 */

import { useCallback, useLayoutEffect, useRef, useState } from "react";

import { t } from "../lib/teks.js";
import { labelAksesibilitas, labelHariJam, labelJamSaja } from "../lib/waktu.js";

const TEPI_KIRI = 8;
const TEPI_KANAN = 8;
const TINGGI_KEPALA = 4;

/** Bangun path SVG dari deret titik. */
function garis(titik) {
  return titik.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
}

export default function PitaPasut({ jam, indeks, onPilih, memuat = false }) {
  const wadahRef = useRef(null);
  const [lebar, setLebar] = useState(720);
  const [tinggi, setTinggi] = useState(120);
  const [menggeser, setMenggeser] = useState(false);

  const n = jam.length;

  // Lebar diukur dari elemen sungguhan, bukan diserahkan ke viewBox yang
  // meregang. Kalau viewBox yang meregang, tebal garis dan guratan ikut
  // meregang dan pita terlihat penyok di layar sempit.
  //
  // Bergantung pada n, BUKAN pada senarai kosong. Saat pertama dirender,
  // data jam belum datang sehingga komponen menampilkan keadaan kosong dan
  // elemen kanvas belum ada. Efek dengan senarai kosong akan berjalan
  // sekali pada saat itu, gagal menemukan elemen, lalu tidak pernah
  // dijalankan lagi — dan SVG tetap memakai ukuran bawaan 720x120 di dalam
  // wadah yang sebenarnya jauh lebih pendek, sehingga guratan jam dan
  // arsiran jam bahaya terpotong keluar layar.
  useLayoutEffect(() => {
    const el = wadahRef.current;
    if (!el) return;
    const ukur = () => {
      setLebar(el.clientWidth || 720);
      setTinggi(el.clientHeight || 120);
    };
    ukur();
    const pengamat = new ResizeObserver(ukur);
    pengamat.observe(el);
    return () => pengamat.disconnect();
  }, [n]);
  const lebarGambar = Math.max(lebar - TEPI_KIRI - TEPI_KANAN, 10);
  const x = useCallback(
    (i) => TEPI_KIRI + (n <= 1 ? 0 : (i * lebarGambar) / (n - 1)),
    [n, lebarGambar]
  );

  // Sumbu tegak. Nol berada di tengah karena tinggi pasut dinyatakan
  // relatif terhadap muka air rata-rata, jadi nilainya bisa negatif.
  const dasar = tinggi - 18;          // sisakan ruang untuk sumbu jam
  const puncak = TINGGI_KEPALA + 6;
  const tengah = (dasar + puncak) / 2;
  const maksAbs = Math.max(
    0.1,
    ...jam.map((j) => Math.abs(j.tinggi_pasut_m ?? 0))
  );
  const y = useCallback(
    (meter) => tengah - ((meter ?? 0) / maksAbs) * ((dasar - puncak) / 2) * 0.86,
    [tengah, maksAbs, dasar, puncak]
  );

  const titikKurva = jam.map((j, i) => [x(i), y(j.tinggi_pasut_m)]);

  // ── Interaksi ────────────────────────────────────────────────────────
  const indeksDariX = useCallback(
    (klienX) => {
      const kotak = wadahRef.current?.getBoundingClientRect();
      if (!kotak || n <= 1) return 0;
      const rel = klienX - kotak.left - TEPI_KIRI;
      const i = Math.round((rel / lebarGambar) * (n - 1));
      return Math.min(n - 1, Math.max(0, i));
    },
    [n, lebarGambar]
  );

  const mulaiGeser = (e) => {
    e.currentTarget.setPointerCapture?.(e.pointerId);
    setMenggeser(true);
    const calon = indeksDariX(e.clientX);
    if (jam[calon]?.tersedia) onPilih(calon);
  };
  const saatGeser = (e) => {
    if (!menggeser) return;
    const calon = indeksDariX(e.clientX);
    if (jam[calon]?.tersedia) onPilih(calon);
  };
  const selesaiGeser = (e) => {
    e.currentTarget.releasePointerCapture?.(e.pointerId);
    setMenggeser(false);
  };

  // Papan ketik: panah kiri-kanan satu jam, Page Up/Down enam jam.
  // DESIGN.md Bagian 6 mewajibkan ini, bukan menyarankan.
  //
  // Perpindahan dihitung lewat PEMBARUAN FUNGSIONAL, bukan dari prop
  // `indeks`. Kalau beberapa penekanan tiba dalam satu batch React —
  // misalnya saat tombol ditahan sehingga berulang cepat — prop `indeks`
  // masih bernilai lama pada seluruh penekanan itu, dan hanya penekanan
  // terakhir yang berpengaruh. Sepuluh kali Page Up akan bergerak enam jam,
  // bukan enam puluh.
  const saatTombol = (e) => {
    let langkah = null;
    let mutlak = null;

    if (e.key === "ArrowLeft" || e.key === "ArrowDown") langkah = -1;
    else if (e.key === "ArrowRight" || e.key === "ArrowUp") langkah = 1;
    else if (e.key === "PageDown") langkah = -6;
    else if (e.key === "PageUp") langkah = 6;
    else if (e.key === "Home") mutlak = 0;
    else if (e.key === "End") mutlak = n - 1;
    else return;

    e.preventDefault();
    const batasi = (nilai) => Math.min(n - 1, Math.max(0, nilai));
    onPilih((sebelumnya) => {
      let calon = mutlak !== null ? mutlak : batasi(sebelumnya + langkah);
      const arah = mutlak === 0 ? 1 : mutlak === n - 1 ? -1 : Math.sign(langkah);
      while (calon >= 0 && calon < n && !jam[calon]?.tersedia) calon += arah;
      return calon >= 0 && calon < n ? calon : sebelumnya;
    });
  };

  if (!n) {
    // Selama sumbu waktu masih dalam perjalanan, yang benar adalah
    // mengatakan sedang memuat. Menampilkan keadaan kosong di sini menyuruh
    // pengguna memuat ulang halaman yang sebenarnya baik-baik saja — saran
    // yang salah, dan saran yang salah lebih buruk daripada diam.
    return (
      <div className="pita pita--kosong">
        <span className="t-label">
          {t(memuat ? "memuat.pasut" : "pitaPasut.tidakAdaData")}
        </span>
      </div>
    );
  }

  const aktif = jam[indeks];
  const posisiPegangan = x(indeks);

  return (
    <section className="pita" aria-label={t("pitaPasut.judul")}>
      <header className="pita__kepala">
        <span className="t-bagian pita__judul">{t("pitaPasut.judul")}</span>
        <span className="t-data pita__terpilih">{labelHariJam(aktif.waktu_utc)}</span>
      </header>

      <div
        ref={wadahRef}
        className="pita__kanvas"
        role="slider"
        tabIndex={0}
        aria-label={t("aksesibilitas.pitaPasutLabel")}
        aria-valuemin={0}
        aria-valuemax={n - 1}
        aria-valuenow={indeks}
        aria-valuetext={labelAksesibilitas(aktif.waktu_utc)}
        onPointerDown={mulaiGeser}
        onPointerMove={saatGeser}
        onPointerUp={selesaiGeser}
        onPointerCancel={selesaiGeser}
        onKeyDown={saatTombol}
      >
        <svg width={lebar} height={tinggi} className="pita__svg" aria-hidden="true">
          <defs>
            {/* SATU-SATUNYA GRADIEN YANG DIIZINKAN DI SELURUH APLIKASI.
                DESIGN.md Bagian 3.6 butir 3: gradasi vertikal halus pada
                Pita Pasut yang menandai kolom air. */}
            <linearGradient id="kolom-air" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--air-2)" stopOpacity="0.55" />
              <stop offset="100%" stopColor="var(--air-4)" stopOpacity="0.15" />
            </linearGradient>
          </defs>

          {jam.map((j, i) => !j.tersedia ? (
            <rect key={`kosong-${i}`} x={x(i) - lebarGambar / Math.max(n - 1, 1) / 2}
              y={puncak} width={Math.max(lebarGambar / Math.max(n - 1, 1), 1.5)}
              height={Math.max(dasar - puncak, 1)} fill="var(--tinta-3)" opacity="0.25" />
          ) : null)}
          {/* Arsiran jam berisiko genangan. Digambar paling bawah supaya
              kurva dan guratan tetap terbaca di atasnya. */}
          {jam.map((j, i) =>
            j.ruas_tergenang > 0 ? (
              <rect
                key={`bahaya-${i}`}
                x={x(i) - lebarGambar / (n - 1) / 2}
                y={dasar - 7}
                width={Math.max(lebarGambar / (n - 1), 1.5)}
                height={7}
                fill="var(--bahaya)"
                opacity="0.85"
              />
            ) : null
          )}

          {/* Penanda jam aman */}
          {jam.map((j, i) =>
            j.tersedia && j.ruas_tergenang === 0 ? (
              <rect
                key={`aman-${i}`}
                x={x(i) - 0.75}
                y={dasar - 2}
                width={1.5}
                height={2}
                fill="var(--aman)"
              />
            ) : null
          )}

          {/* Kolom air di bawah kurva */}
          <path
            d={`${garis(titikKurva)} L${x(n - 1)} ${dasar - 8} L${x(0)} ${dasar - 8} Z`}
            fill="url(#kolom-air)"
          />

          {/* Garis muka air rata-rata */}
          <line
            x1={TEPI_KIRI} y1={y(0)} x2={lebar - TEPI_KANAN} y2={y(0)}
            stroke="var(--lambung-3)" strokeWidth="1"
          />

          {/* Kurva pasut */}
          <path
            d={garis(titikKurva)}
            fill="none"
            stroke="var(--tinta-balik)"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />

          {/* Guratan jam bergradasi seperti papan duga air:
              panjang tiap 6 jam, pendek tiap jam. */}
          {jam.map((j, i) => {
            const jamWib = Number(labelJamSaja(j.waktu_utc));
            const panjang = jamWib % 6 === 0;
            return (
              <line
                key={`gurat-${i}`}
                x1={x(i)} y1={dasar}
                x2={x(i)} y2={dasar + (panjang ? 6 : 3)}
                stroke="var(--tinta-3)"
                strokeWidth={panjang ? 1 : 0.75}
                opacity={panjang ? 0.9 : 0.45}
              />
            );
          })}

          {/* Pegangan geser */}
          <line
            x1={posisiPegangan} y1={puncak - 2}
            x2={posisiPegangan} y2={dasar + 6}
            stroke="var(--rute)" strokeWidth="2"
          />
          <circle
            cx={posisiPegangan} cy={y(aktif.tinggi_pasut_m)} r="4.5"
            fill="var(--rute)" stroke="var(--lambung-1)" strokeWidth="1.5"
          />
        </svg>

        {/* Sasaran sentuh 44px, tidak terlihat tetapi bisa diraih jempol.
            DESIGN.md Bagian 6 mensyaratkan pegangan minimal 44px. */}
        <div
          className="pita__pegangan"
          style={{ left: `${posisiPegangan}px` }}
          aria-hidden="true"
        />
      </div>

      <footer className="pita__kaki">
        <span className="t-label pita__petunjuk">{t("pitaPasut.petunjuk")}</span>
        <span className="pita__bacaan">
          <span className="t-label">{t("pitaPasut.tinggiAir")}</span>{" "}
          <span className="t-data">
            {(aktif.tinggi_pasut_m >= 0 ? "+" : "") +
              aktif.tinggi_pasut_m.toFixed(2)}
          </span>{" "}
          <span className="t-satuan">{t("satuan.meter")}</span>
        </span>
      </footer>
    </section>
  );
}
