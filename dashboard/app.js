// app.js — landing Pasang Surut. Tanpa framework, tanpa dependency.
// 1. Menu navigasi ponsel. 2. Pembanding rute (range + tombol panah,
//    keyboard bawaan dari input range). 3. URL dashboard adaptif.

(function () {
  "use strict";

  // ── Menu ponsel ──
  var nav = document.querySelector(".navigasi");
  var tombolMenu = document.querySelector(".navigasi__tombol");
  if (nav && tombolMenu) {
    tombolMenu.addEventListener("click", function () {
      var buka = nav.classList.toggle("navigasi--buka");
      tombolMenu.setAttribute("aria-expanded", buka ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("navigasi--buka");
        tombolMenu.setAttribute("aria-expanded", "false");
      }
    });
  }

  // ── Pembanding sebelum/sesudah ──
  var panggung = document.getElementById("panggung-banding");
  var range = document.querySelector(".banding__range");
  function terapkan(nilai) {
    var v = Math.max(0, Math.min(100, Number(nilai) || 0));
    range.value = String(v);
    range.setAttribute("aria-valuetext", v + " persen menampilkan rute disarankan");
    panggung.style.setProperty("--pos", v + "%");
  }
  if (panggung && range) {
    range.addEventListener("input", function () { terapkan(range.value); });
    document.querySelectorAll(".banding__panah").forEach(function (btn) {
      btn.addEventListener("click", function () {
        terapkan(Number(range.value) + Number(btn.dataset.geser));
      });
    });
    terapkan(range.value);
  }

  // ── URL dashboard ──
  // Produksi menunjuk ke Vercel. Saat landing dibuka dari localhost
  // (pengembangan), CTA mengarah ke Vite dev server :5173.
  // Override manual: ?dashboard=https://alamat-lain
  var PRODUKSI = "https://pasang-surut.vercel.app";
  var url = PRODUKSI;
  try {
    var host = window.location.hostname;
    var param = new URLSearchParams(window.location.search).get("dashboard");
    if (param) {
      url = param;
    } else if (host === "localhost" || host === "127.0.0.1") {
      url = "http://127.0.0.1:5173";
    }
  } catch (e) {
    url = PRODUKSI;
  }
  document.querySelectorAll("a.js-dashboard").forEach(function (a) {
    a.href = url;
  });
})();
