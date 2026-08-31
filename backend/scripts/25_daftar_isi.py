"""Susun daftar isi, daftar gambar, dan daftar tabel dengan nomor halaman asli.

    python -m scripts.25_daftar_isi

KENAPA NOMOR HALAMANNYA HARUS DIUKUR, BUKAN DIHITUNG.

Nomor halaman baru diketahui setelah Word menata ulang dokumennya. Gambar
menggeser halaman, tabel yang tidak muat pindah utuh ke halaman berikutnya,
dan judul yang `keep_with_next` ikut terdorong. Tidak ada rumus yang bisa
menebak itu dari Markdown.

Karena itu skrip ini membuka `.docx` lewat Word, membaca halaman tiap judul,
gambar, dan tabel, lalu menulis hasilnya ke `docs/daftar_isi.md`.

MENGAPA DIJALANKAN DUA KALI.

Menyisipkan tiga daftar itu sendiri menambah halaman, yang menggeser seluruh
nomor di belakangnya. Jadi skrip berjalan berulang: ukur, tulis daftar, bangun
ulang, ukur lagi. Berhenti begitu nomornya tidak berubah lagi, biasanya pada
putaran kedua atau ketiga.

BERKASNYA BOLEH DISUNTING TANGAN.

`docs/daftar_isi.md` adalah berkas biasa. Judul boleh diperpendek, urutan
boleh diubah. Yang perlu diingat: menjalankan skrip ini lagi akan menimpanya.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[2]
SUMBER = AKAR / "docs" / "proposal_draft.md"
KELUARAN = AKAR / "docs" / "daftar_isi.md"
DOCX = AKAR / "Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.docx"

# Word membaca halaman lewat COM. Dijalankan sebagai proses PowerShell
# terpisah supaya kegagalan Word tidak menyeret skrip Python ikut mati.
PS = r"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open('%s', $false, $true)
  $d.Repaginate()
  foreach ($p in $d.Paragraphs) {
    $t = $p.Range.Text.Trim()
    if ($t.Length -eq 0) { continue }
    $hal = $p.Range.Information(3)
    $gaya = $p.Style.NameLocal
    Write-Output ("{0}`t{1}`t{2}" -f $hal, $gaya, $t)
  }
  $d.Close(0)
} finally { $w.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null }
"""


def _baca_halaman() -> list[tuple[int, str, str]]:
    """Kembalikan (halaman, gaya, teks) tiap paragraf, dibaca dari Word."""
    hasil = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", PS % str(DOCX)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if hasil.returncode != 0:
        raise SystemExit("Word gagal membuka dokumen:\n" + hasil.stderr[:600])
    baris = []
    for x in hasil.stdout.splitlines():
        bagian = x.split("\t")
        if len(bagian) >= 3 and bagian[0].strip().isdigit():
            baris.append((int(bagian[0]), bagian[1].strip(), "\t".join(bagian[2:]).strip()))
    return baris


def _kumpulkan(baris) -> tuple[list, list, list]:
    """Pisahkan judul bagian, keterangan gambar, dan judul tabel.

    Pengumpulan baru dimulai setelah judul Heading 1 yang PERTAMA muncul.
    Tanpa penjaga itu, entri di dalam daftar gambar dan daftar tabel ikut
    terhitung sebagai gambar dan tabel pada putaran berikutnya, sehingga
    daftarnya menggandakan diri tiap kali skrip dijalankan ulang: 9 gambar
    menjadi 32, dan 12 tabel menjadi 48.
    """
    isi, gambar, tabel = [], [], []
    sudah_masuk_badan = False
    for hal, gaya, teks in baris:
        t = teks.replace("\x07", "").strip()
        if not t:
            continue
        if gaya.startswith("Heading 1"):
            sudah_masuk_badan = True
        if not sudah_masuk_badan:
            continue
        if gaya.startswith("Heading 1"):
            isi.append((t, hal, 1))
        elif gaya.startswith("Heading 2"):
            isi.append((t, hal, 2))
        elif re.match(r"^Gambar \d+", t):
            # Keterangan gambar diambil sampai titik kalimat pertama.
            judul = re.match(r"^(Gambar [\d dan]+\.)\s*(.*)$", t)
            if judul:
                inti = judul.group(2).split(".")[0].strip()
                gambar.append((f"{judul.group(1)} {inti}", hal))
        elif re.match(r"^Tabel \d+", t):
            judul = re.match(r"^(Tabel \d+\.)\s*(.*)$", t)
            if judul:
                tabel.append((f"{judul.group(1)} {judul.group(2).strip()}", hal))
    return isi, gambar, tabel


def _tulis(isi, gambar, tabel) -> str:
    b = ["# Daftar isi, daftar gambar, dan daftar tabel",
         "",
         "Nomor halaman di bawah **dibaca langsung dari Microsoft Word**, bukan",
         "diperkirakan. Berkas ini dipakai `22_bangun_docx.py` untuk menyusun ketiga",
         "daftar di dalam proposal.",
         "",
         "Boleh disunting tangan, misalnya memperpendek judul yang kepanjangan.",
         "Tetapi menjalankan `python -m scripts.25_daftar_isi` lagi akan menimpanya.",
         "",
         "---",
         "",
         "## DAFTAR ISI",
         ""]
    for teks, hal, tingkat in isi:
        b.append(f"{'  ' * (tingkat - 1)}- {teks} :: {hal}")
    b += ["", "## DAFTAR GAMBAR", ""]
    for teks, hal in gambar:
        b.append(f"- {teks} :: {hal}")
    b += ["", "## DAFTAR TABEL", ""]
    for teks, hal in tabel:
        b.append(f"- {teks} :: {hal}")
    b.append("")
    return "\n".join(b)


def main() -> int:
    if not DOCX.exists():
        raise SystemExit("Bangun .docx dulu: python -m scripts.22_bangun_docx")

    import importlib
    bangun = importlib.import_module("scripts.22_bangun_docx").bangun

    sebelumnya = None
    for putaran in range(1, 5):
        isi, gambar, tabel = _kumpulkan(_baca_halaman())
        tanda = [h for _, h, _ in isi] + [h for _, h in gambar] + [h for _, h in tabel]
        print(f"putaran {putaran}: {len(isi)} judul, {len(gambar)} gambar, "
              f"{len(tabel)} tabel")
        KELUARAN.write_text(_tulis(isi, gambar, tabel), encoding="utf-8")
        if tanda == sebelumnya:
            print("nomor halaman sudah stabil")
            break
        sebelumnya = tanda
        bangun()          # bangun ulang dengan daftar yang baru
    else:
        print("PERINGATAN: nomor halaman belum stabil setelah empat putaran.")

    print(f"tersimpan: {KELUARAN.relative_to(AKAR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
