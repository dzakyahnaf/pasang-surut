// Pratinjau laptop memakai API VPS melalui proxy same-origin.
import { createServer } from "vite";
import { fileURLToPath } from "node:url";

process.env.VITE_API_URL = "";
const root = fileURLToPath(new URL("../", import.meta.url));
const server = await createServer({ root,
  server: { host: "127.0.0.1", port: 5175, strictPort: true,
    proxy: { "/api": { target: "http://38.103.171.82:18080", changeOrigin: true } } },
});
await server.listen();
server.printUrls();
