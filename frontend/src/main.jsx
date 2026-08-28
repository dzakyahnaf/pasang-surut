import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./styles/dasar.css";
import "./styles/tata-letak.css";
import App from "./App.jsx";

createRoot(document.getElementById("akar")).render(
  <StrictMode>
    <App />
  </StrictMode>
);

// ── Service worker ──────────────────────────────────────────────────────
// Hanya didaftarkan pada build produksi. Di pengembangan ia akan menyajikan
// berkas lama dari cache dan membuat perubahan kode tampak tidak berpengaruh,
// yang memakan waktu jauh lebih banyak daripada manfaatnya.
if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // Kegagalan pendaftaran tidak boleh menghentikan aplikasi. PWA adalah
      // tambahan; peta dan perutean tetap berjalan tanpanya.
    });
  });
}
