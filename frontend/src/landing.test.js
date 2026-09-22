import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { afterEach, expect, test, vi } from 'vitest';
const kode = readFileSync(resolve(process.cwd(), '../dashboard/app.js'), 'utf8');
afterEach(() => { vi.unstubAllGlobals(); document.body.innerHTML = ''; });

test.each([
  ['?dashboard=javascript%3Aalert(1)', 'https://uji.example/app'],
  ['?dashboard=data%3Atext%2Fhtml%2Ctest', 'https://uji.example/app'],
  ['?dashboard=', 'https://uji.example/app'],
  ['?dashboard=%2Fapp', 'https://uji.example/app'],
  ['?dashboard=https%3A%2F%2Fdemo.example%2Fapp', 'https://demo.example/app'],
])('CTA memvalidasi protokol dan tetap menuju aplikasi: %s', (search, hasil) => {
  document.body.innerHTML = '<a class="js-dashboard"></a>';
  vi.stubGlobal('window', { location: { href: 'https://uji.example/' + search, hostname: 'uji.example', search } });
  // Jalankan kode landing apa adanya; masukan parameter dikendalikan fixture.
  new Function(kode)();
  expect(document.querySelector('a').getAttribute('href')).toBe(hasil);
});
