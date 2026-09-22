import React from 'react';
import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import Peta from './Peta.jsx';

vi.mock('maplibre-gl', () => ({ setWorkerUrl: vi.fn(), Map: class { constructor() { throw new Error('WebGL disabled'); } } }));
afterEach(cleanup);

test('WebGL tidak tersedia menampilkan galat tanpa menjatuhkan seluruh aplikasi', () => {
  expect(() => render(<Peta />)).not.toThrow();
  expect(screen.getByRole('alert').textContent).toContain('Peta tidak dapat digambar');
});
