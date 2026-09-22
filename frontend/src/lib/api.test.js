import { afterEach, expect, test, vi } from 'vitest';
import { ambilJam } from './api.js';

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

function jaringanMenggantung() {
  vi.stubGlobal('fetch', vi.fn((_, opsi) => new Promise((resolve, reject) => {
    opsi.signal.addEventListener('abort', () => reject(opsi.signal.reason), { once: true });
  })));
}

test('permintaan menggantung berakhir agar pengguna bisa mencoba ulang', async () => {
  vi.useFakeTimers();
  jaringanMenggantung();
  const selesai = vi.fn();
  const p = ambilJam().catch(selesai);
  await vi.advanceTimersByTimeAsync(20001);
  expect(selesai).toHaveBeenCalledTimes(1);
  expect(selesai.mock.calls[0][0].kode).toBe('batas_waktu');
  await p;
});

test('pembatalan oleh pengguna tetap dibedakan dari batas waktu', async () => {
  jaringanMenggantung();
  const c = new AbortController();
  const p = ambilJam({ signal: c.signal });
  c.abort();
  await expect(p).rejects.toMatchObject({ name: 'AbortError' });
});
