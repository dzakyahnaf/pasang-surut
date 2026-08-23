/**
 * token.js — baca nilai custom property dari CSS.
 *
 * KENAPA TIDAK MENULIS HEKS LANGSUNG DI SINI. MapLibre butuh warna sebagai
 * nilai JavaScript, bukan sebagai var(--nama) di dalam stylesheet. Godaannya
 * adalah menyalin "#1c7f9e" ke dalam berkas peta. Itu butir nomor 6 pada
 * Daftar Tolak DESIGN.md Bagian 12, dan artinya token.css berhenti menjadi
 * sumber tunggal.
 *
 * Jadi nilainya dibaca kembali dari CSS saat berjalan. Satu tempat berubah,
 * semuanya ikut.
 */

/** Ambil satu custom property dari :root sebagai teks. */
export function token(nama) {
  const nilai = getComputedStyle(document.documentElement)
    .getPropertyValue(nama)
    .trim();
  if (!nilai) {
    throw new Error(
      `[token] custom property ${nama} tidak ada di token.css. ` +
        `Tambahkan ke DESIGN.md lalu turunkan ke token.css.`
    );
  }
  return nilai;
}

/** Ambil custom property yang berisi panjang dalam px, kembalikan angkanya. */
export function tokenPx(nama) {
  const nilai = token(nama);
  const angka = Number.parseFloat(nilai);
  if (Number.isNaN(angka)) {
    throw new Error(`[token] ${nama} bernilai "${nilai}", bukan panjang px.`);
  }
  return angka;
}
