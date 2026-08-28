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
 * Yang di-cache karena itu hanya CANGKANGNYA: HTML, JavaScript, CSS, huruf,
 * dan gaya peta. Semua permintaan ke /api/ selalu menembus ke jaringan dan
 * tidak pernah dilayani dari cache.
 */

const VERSI = "pasang-surut-v1";
const CANGKANG = ["/", "/index.html", "/manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(VERSI).then((c) => c.addAll(CANGKANG)).then(() => self.skipWaiting())
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

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // Data prediksi TIDAK PERNAH dari cache. Lihat catatan di atas.
  if (url.pathname.startsWith("/api/")) return;
  if (e.request.method !== "GET") return;
  if (url.origin !== self.location.origin) return;

  e.respondWith(
    caches.match(e.request).then((tersimpan) => {
      if (tersimpan) return tersimpan;
      return fetch(e.request).then((balasan) => {
        if (!balasan || balasan.status !== 200 || balasan.type !== "basic") {
          return balasan;
        }
        const salinan = balasan.clone();
        caches.open(VERSI).then((c) => c.put(e.request, salinan));
        return balasan;
      });
    })
  );
});
