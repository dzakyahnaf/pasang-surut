/**
 * Legenda.jsx — tangga kedalaman, DESIGN.md Bagian 3.4.
 *
 * Contoh warna di legenda WAJIB memakai pola titik yang sama persis dengan
 * yang dipakai di peta untuk dua kelas terdalam. Kalau legenda hanya
 * menampilkan kotak warna polos sementara peta memakai titik, pengguna
 * tidak bisa mencocokkan keduanya, dan aturan "kedalaman tidak pernah
 * disampaikan lewat warna saja" hanya terpenuhi setengah.
 */

import { useState } from "react";

import { t } from "../lib/teks.js";

/* Kelas disusun dari dangkal ke dalam supaya urutannya sejalan dengan
   luminansi yang menurun. Kolom `pola` menyatakan kerapatan titik:
   null berarti polos, angka berarti jarak antar titik dalam satuan viewBox. */
const KELAS = [
  { warna: null, nama: "kedalaman.kering", rentang: null, pola: null },
  { warna: "--air-1", nama: "kedalaman.tipis", rentang: "kedalaman.rentangTipis", pola: null },
  { warna: "--air-2", nama: "kedalaman.sedang", rentang: "kedalaman.rentangSedang", pola: null },
  { warna: "--air-3", nama: "kedalaman.dalam", rentang: "kedalaman.rentangDalam", pola: 8 },
  { warna: "--air-4", nama: "kedalaman.sangatDalam", rentang: "kedalaman.rentangSangatDalam", pola: 5 },
];

const LEBAR_CONTOH = 32;
const TINGGI_CONTOH = 12;

/** Susun titik halftone di dalam kotak contoh legenda. */
function titikPola(jarak) {
  const titik = [];
  for (let x = jarak / 2; x < LEBAR_CONTOH; x += jarak) {
    for (let y = jarak / 2; y < TINGGI_CONTOH; y += jarak) {
      titik.push([x, y]);
    }
  }
  return titik;
}

function ContohWarna({ kelas }) {
  // Kelas kering memakai --air-0 yang bernilai transparent, jadi yang
  // ditampilkan adalah warna garis jalan itu sendiri, bukan kotak kosong.
  const isi = kelas.warna ? `var(${kelas.warna})` : "var(--tinta-2)";
  const tinggi = kelas.warna ? TINGGI_CONTOH : 3;

  return (
    <svg
      className="legenda__contoh"
      viewBox={`0 0 ${LEBAR_CONTOH} ${TINGGI_CONTOH}`}
      width={LEBAR_CONTOH}
      height={TINGGI_CONTOH}
      aria-hidden="true"
    >
      <rect
        x="0"
        y={(TINGGI_CONTOH - tinggi) / 2}
        width={LEBAR_CONTOH}
        height={tinggi}
        style={{ fill: isi }}
      />
      {kelas.pola ? (
        <g style={{ fill: "var(--dek-1)" }}>
          {titikPola(kelas.pola).map(([cx, cy], i) => (
            <circle key={i} cx={cx} cy={cy} r="1.2" />
          ))}
        </g>
      ) : null}
    </svg>
  );
}

export default function Legenda() {
  const [terbuka, setTerbuka] = useState(true);

  return (
    <div className="legenda">
      <button
        type="button"
        className="legenda__saklar t-bagian"
        aria-expanded={terbuka}
        onClick={() => setTerbuka((n) => !n)}
      >
        {t("peta.judulLegenda")}
        <span className="khusus-pembaca-layar">
          {terbuka ? t("peta.sembunyikanLegenda") : t("peta.tampilkanLegenda")}
        </span>
      </button>

      {terbuka ? (
        <div className="legenda__isi" aria-label={t("aksesibilitas.legendaLabel")}>
          <ul className="legenda__daftar">
            {KELAS.map((kelas) => (
              <li key={kelas.nama} className="legenda__baris">
                <ContohWarna kelas={kelas} />
                <span className="legenda__nama t-label">{t(kelas.nama)}</span>
                {kelas.rentang ? (
                  <span className="legenda__rentang t-data">{t(kelas.rentang)}</span>
                ) : null}
              </li>
            ))}
          </ul>

          {/* Setiap tampilan kedalaman wajib menyebut bahwa angkanya
              estimasi turunan. Sentinel-1 hanya memberi label basah atau
              kering; kedalaman tidak pernah diukur langsung. */}
          <p className="legenda__catatan t-label">{t("kedalaman.estimasi")}</p>
        </div>
      ) : null}
    </div>
  );
}
