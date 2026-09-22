import { expect, test } from "vitest";
import { namaLokasi } from "./lokasi.js";

const garis = (nama, lat) => ({ type: "Feature", properties: { nama },
  geometry: { type: "LineString", coordinates: [[110.42, lat], [110.43, lat]] } });

test("nama akses tujuan cepat dipertahankan, bukan menebak lokasi pusat tempat", () => {
  const tempat = [{ lon: 110.42744, lat: -6.96374, label: "Stasiun Semarang Tawang" }];
  expect(namaLokasi([110.42744, -6.96374], null, tempat)).toBe("Akses Stasiun Semarang Tawang");
});

test("ruas terdekat tanpa nama tidak meminjam nama jalan lain", () => {
  const jaringan = { features: [garis("Jalan Bernama", -6.9604), garis(null, -6.96)] };
  expect(namaLokasi([110.425, -6.96001], jaringan)).toBe("Dekat ruas tanpa nama");
});

test("nama jalan hanya ditampilkan untuk titik yang benar-benar dekat", () => {
  const jaringan = { features: [garis("Jalan Kaligawe", -6.96)] };
  expect(namaLokasi([110.425, -6.9601], jaringan)).toBe("Dekat Jalan Kaligawe");
  expect(namaLokasi([110.425, -6.98], jaringan)).toBe("Titik pilihan di peta");
  expect(namaLokasi(null, jaringan)).toBeNull();
});
