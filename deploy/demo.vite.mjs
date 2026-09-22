// Demo lokal memakai satu origin; pilihan VITE_API_URL dari .env.local diabaikan.
import base from '../frontend/vite.config.js';
export default {
  ...base,
  define: { 'import.meta.env.VITE_API_URL': '""' },
  server: {
    host: '127.0.0.1', port: 5182, strictPort: true,
    proxy: { '/api': 'http://127.0.0.1:8012' },
  },
};
