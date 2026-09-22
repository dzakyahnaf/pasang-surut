"""Batasi request berat sampai serialisasi/pengiriman respons selesai."""
from starlette.responses import JSONResponse


class BatasBeban:
    def __init__(self, app, maksimum=2):
        self.app = app
        self.maksimum = maksimum
        self.aktif = 0

    async def __call__(self, scope, receive, send):
        berat = scope["type"] == "http" and scope.get("path") in {
            "/api/rute", "/api/ruas", "/api/genangan", "/api/jaringan",
        }
        if not berat:
            return await self.app(scope, receive, send)
        # Satu event loop per worker: pemeriksaan dan penambahan tanpa await
        # bersifat atomik. Request berlebih tidak menahan utas/antrean besar.
        if self.aktif >= self.maksimum:
            jawaban = JSONResponse(status_code=503,
                content={"detail": {"kode": "server_sibuk", "pesan": "Server sedang sibuk. Coba lagi sebentar."}},
                headers={"Retry-After": "1"})
            return await jawaban(scope, receive, send)
        self.aktif += 1
        try:
            await self.app(scope, receive, send)
        finally:
            self.aktif -= 1
