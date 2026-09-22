"""Batasi JSON sebelum parser membuat objek Python yang menghabiskan RAM."""
import asyncio

from starlette.responses import JSONResponse


class BatasIsi:
    def __init__(self, app, maksimum=16384, detik=10):
        self.app, self.maksimum, self.detik = app, maksimum, detik

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope.get('path') != '/api/rute' or scope.get('method') != 'POST':
            return await self.app(scope, receive, send)

        async def tolak(status, kode):
            await JSONResponse({'detail': {'kode': kode}}, status_code=status)(scope, receive, send)

        try:
            panjang = int(dict(scope.get('headers', [])).get(b'content-length', b'0'))
        except ValueError:
            return await tolak(400, 'panjang_isi_tidak_sah')
        if panjang < 0:
            return await tolak(400, 'panjang_isi_tidak_sah')
        if panjang > self.maksimum:
            return await tolak(413, 'isi_terlalu_besar')

        isi = bytearray()

        async def baca():
            while True:
                pesan = await receive()
                if pesan['type'] == 'http.disconnect':
                    return 'putus'
                bagian = pesan.get('body', b'')
                if len(isi) + len(bagian) > self.maksimum:
                    return 'besar'
                isi.extend(bagian)
                if not pesan.get('more_body', False):
                    return 'selesai'

        try:
            status = await asyncio.wait_for(baca(), timeout=self.detik)
        except TimeoutError:
            return await tolak(408, 'batas_waktu_isi')
        if status == 'besar':
            return await tolak(413, 'isi_terlalu_besar')
        if status == 'putus':
            return
        terkirim = False

        async def baca_ulang():
            nonlocal terkirim
            if terkirim:
                return await receive()
            terkirim = True
            return {'type': 'http.request', 'body': bytes(isi), 'more_body': False}

        await self.app(scope, baca_ulang, send)
