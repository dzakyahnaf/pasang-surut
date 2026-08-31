"""Nomori ulang bagian, gambar, dan tabel proposal mengikuti gaya rujukan.

    python -m scripts.26_nomori_ulang

Gaya yang dituju, mengikuti proposal rujukan ITC 2026:

    Bagian utama   angka Romawi, judul huruf besar   I. JUDUL KARYA
    Sub-bagian     tetap angka biasa                 3.1, 3.2, ...
    Gambar         nomor bagian titik urutan         Gambar 8.1
    Tabel          nomor bagian titik urutan         Tabel 9.3

KENAPA DIHITUNG SKRIP, BUKAN DIKETIK TANGAN.

Nomor gambar dan tabel bergantung pada bagian tempat ia berada dan urutannya
di dalam bagian itu. Menyisipkan satu tabel di tengah dokumen menggeser semua
nomor sesudahnya. Dikerjakan tangan, cepat atau lambat akan ada yang meleset,
dan yang meleset itu justru muncul di daftar gambar.

Skrip ini membaca ulang seluruh berkas tiap kali dijalankan, jadi aman
dijalankan berkali-kali. Ia juga menerima berkas yang sudah bernomor gaya
baru, sehingga bisa dipakai lagi setelah ada penyisipan.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[2]
SUMBER = AKAR / "docs" / "proposal_draft.md"

ROMAWI = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
          "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


def _judul_bagian(baris: str) -> tuple[int, str] | None:
    """Kenali judul bagian utama, baik gaya angka maupun gaya Romawi."""
    m = re.match(r"^## (\d+)\.\s+(.*)$", baris)
    if m:
        return int(m.group(1)), m.group(2).strip()
    m = re.match(r"^## ([IVX]+)\.\s+(.*)$", baris)
    if m and m.group(1) in ROMAWI:
        return ROMAWI.index(m.group(1)), m.group(2).strip()
    return None


def main() -> int:
    teks = SUMBER.read_text(encoding="utf-8")
    kepala, penutup = "## 1. Judul Karya", None
    for j in ("## Jumlah halaman", "## Perkiraan halaman"):
        if j in teks:
            penutup = j
            break
    if kepala not in teks:
        kepala = next(b for b in teks.split("\n") if _judul_bagian(b))
    awal = teks.index(kepala)
    akhir = teks.index(penutup)
    badan, ekor = teks[awal:akhir], teks[akhir:]
    depan = teks[:awal]

    baris = badan.split("\n")
    keluar = []
    bagian = 0
    n_gambar = n_tabel = 0
    ubah_gambar = ubah_tabel = ubah_bagian = 0

    for b in baris:
        info = _judul_bagian(b)
        if info:
            bagian, judul = info
            n_gambar = n_tabel = 0
            baru = f"## {ROMAWI[bagian]}. {judul.upper()}"
            if baru != b:
                ubah_bagian += 1
            keluar.append(baru)
            continue

        m = re.match(r"^\*\*Gambar [\d.]+\*\*(.*)$", b)
        if m:
            n_gambar += 1
            keluar.append(f"**Gambar {bagian}.{n_gambar}**{m.group(1)}")
            ubah_gambar += 1
            continue

        m = re.match(r"^\*\*Tabel [\d.]+\*\*(.*)$", b)
        if m:
            n_tabel += 1
            keluar.append(f"**Tabel {bagian}.{n_tabel}**{m.group(1)}")
            ubah_tabel += 1
            continue

        keluar.append(b)

    SUMBER.write_text(depan + "\n".join(keluar) + ekor, encoding="utf-8")

    hasil = "\n".join(keluar)
    print(f"bagian dinomori Romawi : {ubah_bagian}")
    print(f"gambar dinomori ulang  : {ubah_gambar}")
    print(f"tabel dinomori ulang   : {ubah_tabel}")
    print()
    print("GAMBAR :", ", ".join(re.findall(r"\*\*Gambar ([\d.]+)\*\*", hasil)))
    print("TABEL  :", ", ".join(re.findall(r"\*\*Tabel ([\d.]+)\*\*", hasil)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
