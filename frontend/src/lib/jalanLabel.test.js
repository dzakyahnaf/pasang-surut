import { expect, test } from "vitest";
import { buatLabelJalan } from "./jalanLabel.js";
const ruas = (nama, coordinates) => ({ type: "Feature", properties: { nama, jenis: "primary" },
  geometry: { type: "LineString", coordinates } });

test("label menyambung ruas pendek dan membuang duplikat arah tanpa mengubah input", () => {
  const jalan = { features: [ruas("Jalan A", [[1, 1], [2, 2]]),
    ruas("Jalan A", [[2, 2], [1, 1]]), ruas("Jalan A", [[2, 2], [3, 3]])] };
  const sebelum = JSON.stringify(jalan);
  const hasil = buatLabelJalan(jalan);
  expect(hasil.features).toHaveLength(1);
  expect(hasil.features[0].geometry.coordinates).toEqual([[1, 1], [2, 2], [3, 3]]);
  expect(hasil.features[0].properties.label).toBe("Jl. A");
  expect(JSON.stringify(jalan)).toBe(sebelum);
});

test("nama berbeda, cabang, dan ruas tanpa nama tidak digabung menjadi label palsu", () => {
  const hasil = buatLabelJalan({ features: [ruas("Jalan A", [[1, 1], [2, 2]]),
    ruas("Jalan A", [[2, 2], [3, 3]]), ruas("Jalan A", [[2, 2], [4, 4]]),
    ruas("Jalan B", [[3, 3], [5, 5]]), ruas(null, [[5, 5], [6, 6]])] });
  expect(hasil.features).toHaveLength(4);
  expect(hasil.features.every((f) => f.geometry.coordinates.length === 2)).toBe(true);
});
