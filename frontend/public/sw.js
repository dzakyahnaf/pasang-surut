/**
 * sw.js — service worker.
 *
 * TUJUANNYA BUKAN LURING PENUH, dan itu keputusan sadar.
 *
 * Menyimpan seluruh prediksi 72 jam ke cache akan membuat aplikasi tampak
 * berfungsi saat jaringan mati, tetapi menampilkan genangan yang sudah
 * kedaluwarsa. Untuk aplikasi yang menyarankan kapan orang boleh berangkat
 * menembus air, data basi lebih berbahaya daripada layar kosong.
 *
 * ── KESALAHAN VERSI PERTAMA, DAN KENAPA DIPERBAIKI ─────────────────────
 *
 * Versi pertama melayani SEMUA permintaan cache-first, termasuk /index.html,
 * dan memakai nama cache tetap yang tidak pernah berubah. Akibatnya baru
 * terlihat di produksi dan cukup parah:
 *
 *   1. index.html lama tersimpan di cache dan disajikan selamanya.
 *   2. index.html lama menunjuk ke bundel lama yang namanya ber-hash.
 *   3. Bundel lama itu menyimpan alamat API yang salah di dalamnya.
 *
 * Jadi pengunjung yang pernah membuka aplikasi SEBELUM perbaikan akan terus
 * mendapat versi rusak walau server sudah menyajikan yang benar — dan tidak
 * ada galat apa pun yang muncul, halamannya hanya diam.
 *
 * Perbaikannya dua lapis:
 *
 *   HTML dan navigasi   JARINGAN LEBIH DULU. Cache hanya dipakai bila
 *                       jaringan benar-benar gagal. Cangkang selalu segar,
 *                       dan aplikasi tetap terbuka saat luring.
 *
 *   Berkas ber-hash     CACHE LEBIH DULU, karena aman: nama berkasnya
 *                       memuat hash isinya, sehingga isi yang berubah selalu
 *                       punya nama baru dan tidak mungkin tertukar.
 *
 * VERSI juga dinaikkan supaya cache lama benar-benar dibuang saat aktivasi.
 * Setiap kali perilaku cache berubah, NAIKKAN NOMORNYA.
 */

const VERSI = "pasang-surut-v3";
const CANGKANG = ["/", "/index.html", "/manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches
      .open(VERSI)
      .then((c) => c.addAll(CANGKANG))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((kunci) =>
        Promise.all(kunci.filter((k) => k !== VERSI).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  );
});

/** Berkas hasil build Vite; namanya memuat hash isi sehingga aman di-cache. */
function berhash(url) {
  return url.pathname.startsWith("/assets/");
}

/** Permintaan halaman, bukan aset. */
function navigasi(request, url) {
  return (
    request.mode === "navigate" ||
    url.pathname === "/" ||
    url.pathname.endsWith(".html") ||
    url.pathname === "/manifest.webmanifest"
  );
}

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // Data prediksi TIDAK PERNAH dari cache. Lihat catatan di atas.
  if (url.pathname.startsWith("/api/")) return;
  if (e.request.method !== "GET") return;
  if (url.origin !== self.location.origin) return;

  // ── Cangkang: jaringan lebih dulu ──────────────────────────────────
  if (navigasi(e.request, url)) {
    e.respondWith(
      fetch(e.request)
        .then((balasan) => {
          if (balasan && balasan.status === 200) {
            const salinan = balasan.clone();
            caches.open(VERSI).then((c) => c.put(e.request, salinan));
          }
          return balasan;
        })
        // Hanya saat jaringan benar-benar gagal. Cangkang basi lebih baik
        // daripada layar galat peramban, dan datanya sendiri tetap dari
        // jaringan karena /api/ tidak pernah di-cache.
        .catch(() => caches.match(e.request).then((c) => c || caches.match("/")))
    );
    return;
  }

  // ── Aset ber-hash: cache lebih dulu ────────────────────────────────
  if (berhash(url)) {
    e.respondWith(
      caches.match(e.request).then((tersimpan) => {
        if (tersimpan) return tersimpan;
        return fetch(e.request).then((balasan) => {
          if (balasan && balasan.status === 200 && balasan.type === "basic") {
            const salinan = balasan.clone();
            caches.open(VERSI).then((c) => c.put(e.request, salinan));
          }
          return balasan;
        });
      })
    );
    return;
  }

  // Sisanya (ikon, berkas publik lain) diambil apa adanya dari jaringan.
});
