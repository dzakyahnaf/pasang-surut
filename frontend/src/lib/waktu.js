/**
 * waktu.js — satu-satunya tempat waktu diubah dari UTC menjadi WIB.
 *
 * Aturan repo: database menyimpan UTC, antarmuka menampilkan WIB. Konversi
 * itu hanya boleh terjadi di lapisan tampilan, dan supaya tidak tersebar,
 * hanya di berkas ini.
 *
 * Zona dipaksa Asia/Jakarta lewat Intl, BUKAN diserahkan ke zona laptop
 * yang membuka aplikasi. Anggota tim di Surabaya, juri di Semarang, dan
 * server di mana pun harus melihat jam yang sama.
 */

import { t } from "./teks.js";

const ZONA = "Asia/Jakarta";

/* Nama hari pendek diambil dari copy.id.json, bukan dari keluaran Intl,
   supaya singkatannya seragam dengan sisa antarmuka. Urutannya mengikuti
   penanggalan Inggris karena itulah yang dikembalikan Intl. */
const KUNCI_HARI = {
  Sunday: "waktu.minggu",
  Monday: "waktu.senin",
  Tuesday: "waktu.selasa",
  Wednesday: "waktu.rabu",
  Thursday: "waktu.kamis",
  Friday: "waktu.jumat",
  Saturday: "waktu.sabtu",
};

function bagian(iso, opsi) {
  return new Intl.DateTimeFormat("id-ID", { timeZone: ZONA, ...opsi })
    .formatToParts(new Date(iso))
    .reduce((kumpul, b) => ({ ...kumpul, [b.type]: b.value }), {});
}

/** Nama hari pendek dalam Bahasa Indonesia, contoh "Sen". */
export function labelHari(iso) {
  const inggris = new Intl.DateTimeFormat("en-US", {
    timeZone: ZONA,
    weekday: "long",
  }).format(new Date(iso));
  return t(KUNCI_HARI[inggris] ?? "waktu.senin");
}

/** Jam saja dalam WIB, dua digit, contoh "16". */
export function labelJamSaja(iso) {
  return bagian(iso, { hour: "2-digit", hour12: false }).hour ?? "00";
}

/** Jam dan menit dalam format copy.id.json, contoh "16.00". */
export function labelJam(iso) {
  const b = bagian(iso, { hour: "2-digit", minute: "2-digit", hour12: false });
  return t("waktu.formatJam", { jam: b.hour, menit: b.minute });
}

/** Baris pendek untuk kepala Pita Pasut, contoh "Sen 25 · pukul 16.00 WIB". */
export function labelHariJam(iso) {
  const b = bagian(iso, { day: "numeric" });
  return `${labelHari(iso)} ${b.day} · ${t("waktu.pukul")} ${labelJam(iso)} ${t("waktu.zona")}`;
}

/** Label lengkap untuk pembaca layar, memakai kalimat dari copy.id.json. */
export function labelAksesibilitas(iso) {
  const b = bagian(iso, { day: "numeric" });
  return t("aksesibilitas.pitaPasutNilai", {
    hari: labelHari(iso),
    tanggal: b.day,
    jam: labelJam(iso),
  });
}
