import { mkdirSync, writeFileSync } from "node:fs";

// Vercel menjadi alamat HTTPS masuk. Aset aplikasi disajikan VPS.
mkdirSync("dist-proxy", { recursive: true });
writeFileSync("dist-proxy/proxy-info.json", JSON.stringify({ layanan: "pasang-surut", mode: "vps" }));
