import React from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App.jsx";

const api = vi.hoisted(() => ({ ambilJam: vi.fn(), ambilJaringan: vi.fn(),
  ambilKondisi: vi.fn(), ambilTujuanCepat: vi.fn(), hitungRute: vi.fn() }));
vi.mock("./lib/api.js", () => api);
vi.mock("./components/Peta.jsx", () => ({ default: ({ onKlikPeta, rute, kondisi }) => <div>
  <button onClick={() => onKlikPeta([110.4, -6.95])}>titik A</button>
  <button onClick={() => onKlikPeta([110.401, -6.95])}>titik B</button>
  <div data-testid="rute">{rute?.features?.[0]?.properties?.label ?? "kosong"}</div>
  <div data-testid="kondisi">{kondisi?.waktu_utc ?? "kosong"}</div>
</div> }));

const jam = [0, 1, 2, 3].map((i) => ({ waktu_utc: `2026-09-26T0${i}:00:00+00:00`,
  tersedia: true, ruas_tergenang: 0, tinggi_pasut_m: .1 }));
function hasil(label = "baru") {
  return { rute: { type: "FeatureCollection", features: [{ type: "Feature",
    geometry: { type: "LineString", coordinates: [] },
    properties: { jenis: "rute_sadar_rob", label, ditemukan: true, menit: 5,
      jarak_km: 1, ruas_tergenang: 0, nama_jalan: [] } }] },
    sumber_data: ["kerentanan_v1"], selisih: { tersedia: false } };
}
beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal("ResizeObserver", class { observe() {} disconnect() {} });
  api.ambilJam.mockResolvedValue({ jam, asal_jaringan: "potret" });
  api.ambilJaringan.mockResolvedValue({ type: "FeatureCollection", features: [], versi_jaringan: "g1" });
  api.ambilKondisi.mockImplementation(async (w) => ({ waktu_utc: w, versi_jaringan: "g1", ruas: [] }));
  api.ambilTujuanCepat.mockResolvedValue({ tujuan: [] });
  api.hitungRute.mockResolvedValue(hasil());
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

async function mulai() {
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("kondisi").textContent).toBe(jam[0].waktu_utc));
  fireEvent.click(screen.getByRole("button", { name: "titik A" }));
  fireEvent.click(screen.getByRole("button", { name: "titik B" }));
}

test("Cari ulang mengirim request baru setelah gagal tanpa mengubah input", async () => {
  api.hitungRute.mockRejectedValueOnce(new Error("offline"));
  await mulai();
  const tombol = await screen.findByRole("button", { name: "Cari ulang" });
  expect(api.hitungRute).toHaveBeenCalledTimes(1);
  fireEvent.click(tombol);
  await waitFor(() => expect(screen.getByTestId("rute").textContent).toBe("baru"));
  expect(api.hitungRute).toHaveBeenCalledTimes(2);
  expect(api.hitungRute.mock.calls[1][0]).toEqual(api.hitungRute.mock.calls[0][0]);
  expect(screen.queryByRole("alert")).toBeNull();
});

test("geser cepat hanya meminta jam terakhir dan tidak mengunduh geometri ulang", async () => {
  await mulai();
  await waitFor(() => expect(screen.getByTestId("rute").textContent).toBe("baru"));
  const slider = screen.getByRole("slider");
  fireEvent.keyDown(slider, { key: "ArrowRight" });
  fireEvent.keyDown(slider, { key: "ArrowRight" });
  fireEvent.keyDown(slider, { key: "ArrowRight" });
  expect(screen.getByTestId("rute").textContent).toBe("kosong");
  await waitFor(() => expect(screen.getByTestId("kondisi").textContent).toBe(jam[3].waktu_utc));
  expect(api.ambilKondisi).toHaveBeenCalledTimes(2);
  expect(api.hitungRute).toHaveBeenCalledTimes(2);
  expect(api.ambilJaringan).toHaveBeenCalledTimes(1);
});

test("hapus titik membatalkan request dan respons terlambat tidak tampil", async () => {
  let selesai;
  api.hitungRute.mockImplementationOnce(() => new Promise((resolve) => { selesai = resolve; }));
  await mulai();
  await waitFor(() => expect(api.hitungRute).toHaveBeenCalledTimes(1));
  const signal = api.hitungRute.mock.calls[0][1].signal;
  fireEvent.click(screen.getByRole("button", { name: "Hapus titik berangkat" }));
  expect(signal.aborted).toBe(true);
  await act(async () => { selesai(hasil("lama")); });
  expect(screen.getByTestId("rute").textContent).toBe("kosong");
  expect(screen.getByRole("button", { name: "Cari rute" }).disabled).toBe(true);
});

test("respons jam lama tidak menimpa hasil jam baru walaupun abort diabaikan server", async () => {
  let selesai;
  api.hitungRute.mockImplementationOnce(() => new Promise((resolve) => { selesai = resolve; }));
  await mulai();
  await waitFor(() => expect(api.hitungRute).toHaveBeenCalledTimes(1));
  const signal = api.hitungRute.mock.calls[0][1].signal;
  fireEvent.keyDown(screen.getByRole("slider"), { key: "End" });
  await waitFor(() => expect(screen.getByTestId("rute").textContent).toBe("baru"));
  expect(signal.aborted).toBe(true);
  await act(async () => { selesai(hasil("lama")); });
  expect(screen.getByTestId("rute").textContent).toBe("baru");
});

test("jam tanpa cakupan dilewati dan tidak ditampilkan sebagai jam kering", async () => {
  api.ambilJam.mockResolvedValue({ jam: jam.map((j,i) => i === 1 ? {
    ...j, tersedia: false, ruas_tergenang: null, tinggi_pasut_m: null } : j) });
  await mulai();
  await waitFor(() => expect(screen.getByTestId("rute").textContent).toBe("baru"));
  fireEvent.keyDown(screen.getByRole("slider"), { key: "ArrowRight" });
  await waitFor(() => expect(screen.getByTestId("kondisi").textContent).toBe(jam[2].waktu_utc));
  expect(api.ambilKondisi.mock.calls.some(([w]) => w === jam[1].waktu_utc)).toBe(false);
});

test("galat pemuatan peta dapat dicoba ulang dan hilang setelah pulih", async () => {
  api.ambilKondisi.mockRejectedValueOnce(Object.assign(new Error("sibuk"), { kode: "server_sibuk" }));
  render(<App />);
  await screen.findByRole("alert");
  fireEvent.click(screen.getByRole("button", { name: "Cari ulang" }));
  await waitFor(() => expect(screen.getByTestId("kondisi").textContent).toBe(jam[0].waktu_utc));
  expect(screen.queryByRole("alert")).toBeNull();
});

test("versi geometri berbeda tidak memicu loop unduhan dan bisa dipulihkan", async () => {
  api.ambilKondisi.mockImplementation(async (w) => ({ waktu_utc: w, versi_jaringan: "g2", ruas: [] }));
  render(<App />);
  await screen.findByRole("alert");
  expect(api.ambilJaringan).toHaveBeenCalledTimes(2);
  expect(screen.getByTestId("kondisi").textContent).toBe("kosong");
  api.ambilJaringan.mockResolvedValue({ type: "FeatureCollection", features: [], versi_jaringan: "g2" });
  fireEvent.click(screen.getByRole("button", { name: "Cari ulang" }));
  await waitFor(() => expect(screen.getByTestId("kondisi").textContent).toBe(jam[0].waktu_utc));
  expect(api.ambilJaringan).toHaveBeenCalledTimes(3);
  expect(screen.queryByRole("alert")).toBeNull();
});
