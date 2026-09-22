import konteks from "../data/konteks-peta.json";
import { token, tokenPx } from "./token.js";
import { t } from "./teks.js";

/** Label native MapLibre: collision/zoom dikelola renderer, tanpa ubin luar. */
export function pasangLabelPeta(peta) {
  peta.addSource("konteks", { type: "geojson", data: konteks });
  peta.addSource("label-jalan", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
  peta.addLayer({
    id: "batas-wilayah", type: "line", source: "konteks",
    filter: ["==", ["get", "jenis"], "batas"],
    paint: { "line-color": token("--tinta-2"), "line-width": 1,
      "line-dasharray": [4, 4], "line-opacity": 0.35 },
  }, "ruas-dasar");
  peta.addLayer({
    id: "garis-pantai", type: "line", source: "konteks",
    filter: ["==", ["get", "jenis"], "pantai"],
    paint: { "line-color": token("--air-3"), "line-width": 2 },
  }, "ruas-dasar");

  const font = ["Barlow Semi Condensed"];
  const paint = { "text-color": token("--tinta-1"),
    "text-halo-color": token("--dek-1"), "text-halo-width": 2 };
  const named = ["!=", ["coalesce", ["get", "nama"], ""], ""];
  const mainRoad = ["==", ["get", "utama"], true];
  for (const [id, minzoom, filter] of [
    ["nama-jalan-utama", 10.5, ["all", named, mainRoad]],
    ["nama-jalan-lokal", 14.5, ["all", named, ["!", mainRoad]]],
  ]) {
    peta.addLayer({ id, type: "symbol", source: "label-jalan", minzoom, filter,
      layout: { "symbol-placement": "line", "symbol-spacing": 320,
        "text-field": ["get", "label"], "text-font": font,
        "text-size": ["interpolate", ["linear"], ["zoom"],
          12, tokenPx("--t-label-ukuran"), 16, tokenPx("--t-isi-ukuran")],
        "text-padding": 4, "text-max-angle": 30 }, paint,
    }, "titik-cincin");
  }
  peta.addLayer({
    id: "nama-wilayah", type: "symbol", source: "konteks", maxzoom: 15,
    filter: ["==", ["get", "jenis"], "wilayah"],
    layout: { "text-field": ["upcase", ["get", "nama"]], "text-font": font,
      "text-size": tokenPx("--t-isi-ukuran"), "text-letter-spacing": 0.08,
      "text-max-width": 12, "text-padding": 12, "text-variable-anchor": ["center", "top", "bottom"] },
    paint: { ...paint, "text-color": token("--tinta-2") },
  }, "titik-cincin");
  peta.addLayer({
    id: "tempat-titik", type: "circle", source: "konteks",
    filter: ["==", ["get", "jenis"], "tempat"],
    paint: { "circle-radius": 4, "circle-color": token("--lambung-1"),
      "circle-stroke-color": token("--dek-1"), "circle-stroke-width": 2 },
  }, "titik-cincin");
  peta.addLayer({
    id: "nama-tempat", type: "symbol", source: "konteks",
    filter: ["==", ["get", "jenis"], "tempat"],
    layout: { "text-field": ["get", "nama"], "text-font": font,
      "text-size": tokenPx("--t-isi-ukuran"), "text-max-width": 12,
      "text-variable-anchor": ["top", "bottom", "left", "right"],
      "text-radial-offset": 0.6, "text-padding": 8 }, paint,
  }, "titik-cincin");
  peta.addLayer({
    id: "nama-titik", type: "symbol", source: "titik",
    layout: { "text-field": ["match", ["get", "peran"], "asal", t("peta.titikAsal"), t("peta.titikTujuan")],
      "text-font": font, "text-size": tokenPx("--t-label-ukuran"),
      "text-offset": [0, 1.2], "text-anchor": "top", "text-padding": 4 }, paint,
  });
}
