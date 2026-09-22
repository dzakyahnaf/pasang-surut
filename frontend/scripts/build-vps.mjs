// Menetapkan string kosong di Node juga bekerja pada Windows PowerShell,
// yang menghapus variabel environment bila diberi nilai kosong.
process.env.VITE_API_URL = "";
const { build } = await import("vite");
await build();
