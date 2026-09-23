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
    versi_data: 'v1', versi_jaringan: 'g1',
    sumber_data: ["kerentanan_v1"], selisih: { tersedia: false } };
}
beforeEach(() => {
  // Buang juga antrean mock *Once bila tes sebelumnya gagal sebelum request.
  vi.resetAllMocks();
  vi.stubGlobal("ResizeObserver", class { observe() {} disconnect() {} });
  api.ambilJam.mockResolvedValue({ jam, versi_data: 'v1', asal_jaringan: "potret" });
  api.ambilJaringan.mockResolvedValue({ type: "FeatureCollection", features: [], versi_jaringan: "g1" });
  api.ambilKondisi.mockImplementation(async (w) => ({ waktu_utc: w, versi_data: 'v1', versi_jaringan: "g1", ruas: [] }));
  api.ambilTujuanCepat.mockResolvedValue({ tujuan: [] });
  api.hitungRute.mockResolvedValue(hasil());
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

async function mulai() {
  // Selesaikan efek awal berbasis Promise sebelum mulai menunggu kondisi.
  await act(async () => { render(<App />); });
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
  api.ambilJam.mockResolvedValue({ versi_data: 'v1', jam: jam.map((j,i) => i === 1 ? {
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
  api.ambilKondisi.mockImplementation(async (w) => ({ waktu_utc: w, versi_data: 'v1', versi_jaringan: "g2", ruas: [] }));
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

test('versi rute berbeda dari kondisi disembunyikan dan bisa diselaraskan', async () => {
  api.hitungRute.mockResolvedValueOnce({ ...hasil('kedaluwarsa'), versi_data: 'v0' });
  await mulai();
  await screen.findByText(/Versi data berubah/);
  expect(screen.getByTestId('rute').textContent).toBe('kosong');
  expect(screen.getByTestId('kondisi').textContent).toBe('kosong');
  fireEvent.click(screen.getAllByRole('button', { name: 'Cari ulang' })[0]);
  await waitFor(() => expect(screen.getByTestId('rute').textContent).toBe('baru'));
  expect(screen.queryByRole('alert')).toBeNull();
});

test('hasil rute menunggu kondisi peta dan tidak menampilkan lapisan lama', async () => {
  await mulai();
  await waitFor(() => expect(screen.getByTestId('rute').textContent).toBe('baru'));
  api.ambilKondisi.mockRejectedValueOnce(new Error('putus'));
  fireEvent.keyDown(screen.getByRole('slider'), { key: 'End' });
  await screen.findByRole('alert');
  expect(screen.getByTestId('rute').textContent).toBe('kosong');
  expect(screen.getByTestId('kondisi').textContent).toBe('kosong');
});

test('daftar tujuan yang gagal dapat dimuat ulang tanpa memuat ulang halaman', async () => {
  api.ambilTujuanCepat.mockRejectedValueOnce(new Error('putus'));
  render(<App />);
  fireEvent.click(await screen.findByRole('button', { name: 'Muat ulang tujuan' }));
  await waitFor(() => expect(api.ambilTujuanCepat).toHaveBeenCalledTimes(2));
  await waitFor(() => expect(screen.queryByRole('alert')).toBeNull());
});

test('saran di luar pita tetap berupa informasi tanpa tombol yang tidak bekerja', async () => {
  api.hitungRute.mockResolvedValue({ ...hasil(),
    waktu_berangkat_utc: jam[0].waktu_utc,
    paparan: { menembus: true, kedalaman_maks_cm: 22 },
    jam_lebih_aman: { waktu_utc: '2026-09-27T00:00:00+00:00', kedalaman_maks_cm: 10 },
  });
  await mulai();
  await screen.findByText(/di luar rentang Pita Pasut/);
  expect(screen.queryByRole('button', { name: /genangan turun/ })).toBeNull();
  expect(screen.getByText(/Estimasi kedalaman maksimum 22 cm/)).toBeTruthy();
});

test('rute terputus tidak menuduh semua jalur tergenang', async () => {
  const h = hasil();
  h.rute.features[0].properties = { jenis: 'rute_sadar_rob', ditemukan: false, alasan: 'tidak_terhubung' };
  h.dampak = null;
  api.hitungRute.mockResolvedValue(h);
  await mulai();
  await screen.findByText('Jaringan jalan tidak terhubung');
  expect(screen.queryByText('Semua jalur tergenang')).toBeNull();
  expect(screen.queryByText('Tidak ada selisih')).toBeNull();
});

test('kedua panel paparan menyebut maksimum rute tanpa menebak jalan pertama', async () => {
  const h = hasil();
  h.waktu_berangkat_utc = jam[0].waktu_utc;
  h.waktu_berangkat_wib = '2026-09-26T07:00:00+07:00';
  h.paparan = { menembus: true, kedalaman_maks_cm: 24.8 };
  Object.assign(h.rute.features[0].properties, {
    ruas_tergenang: 2, kedalaman_maks_cm: 24.8, nama_jalan: ['Jalan Pertama'],
  });
  api.hitungRute.mockResolvedValue(h);
  await mulai();
  await waitFor(() => expect(screen.getAllByText(/Estimasi kedalaman maksimum 25 cm pada rute ini/)).toHaveLength(2));
  expect(screen.queryByText(/di Jalan Pertama/)).toBeNull();
  expect(screen.getAllByText(/Estimasi kedalaman maksimum/).every(el => el.textContent.includes('WIB'))).toBe(true);
});
