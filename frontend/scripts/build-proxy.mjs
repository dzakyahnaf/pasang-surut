import { copyFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Vercel menjadi alamat HTTPS masuk. Aset aplikasi disajikan VPS.
const depan = dirname(fileURLToPath(import.meta.url)); // frontend/scripts
const akarRepo = join(depan, "..", "..");
const keluar = join(depan, "..", "dist-proxy");
mkdirSync(keluar, { recursive: true });
writeFileSync(join(keluar, "proxy-info.json"), JSON.stringify({ layanan: "pasang-surut", mode: "vps" }));

// Landing ikut ter-deploy apa adanya dari dashboard/ — DISALIN, bukan
// dipindah atau disunting. Satu-satunya sumber landing tetap dashboard/.
// vercel.json me-rewrite "/" ke berkas-berkas ini.
const landing = join(keluar, "lp");
mkdirSync(landing, { recursive: true });
for (const berkas of ["index.html", "styles.css", "app.js"]) {
  copyFileSync(join(akarRepo, "dashboard", berkas), join(landing, berkas));
}
