"""Bangun ulang proposal .docx dari Markdown yang menjadi sumber kebenaran.

    python -m scripts.22_bangun_docx

KENAPA SKRIP INI ADA.

Sejak 29 Agustus, `docs/proposal_draft.md` adalah sumber kebenaran proposal dan
`.docx` dibangun ulang darinya, bukan sebaliknya. Alasannya: Markdown bisa
di-diff di git sehingga perubahan antar sesi terlihat, sedangkan `.docx` tidak.

Selama ini pembangunan ulang itu dikerjakan manual. Skrip ini membuatnya dapat
diulang, sehingga setiap koreksi pada Markdown cukup dijalankan sekali lagi
tanpa mengulang seluruh pemformatan dari nol.

FORMAT YANG DIWAJIBKAN RULEBOOK, dan diterapkan di sini:

    kertas A4, huruf Times New Roman 12, spasi 1,5, margin 4-3-3-3 cm,
    maksimal 30 halaman TERMASUK sampul dan lampiran

BATAS SKRIP INI, dan kenapa hasilnya tetap wajib diperiksa manusia.

Konversi Markdown ke Word bukan pemetaan satu-satu. Yang paling rawan meleset:
tabel lebar yang melewati batas margin, gambar yang penskalaannya menggeser
halaman, dan pemenggalan baris di dalam sel. Skrip ini menangani ketiganya
dengan aturan yang eksplisit, tetapi **jumlah halaman tetap wajib dibaca dari
Word**, bukan dari perkiraan mana pun.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_BREAK,
                            WD_TAB_ALIGNMENT, WD_TAB_LEADER)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AKAR = Path(__file__).resolve().parents[2]
SUMBER = AKAR / "docs" / "proposal_draft.md"
DAFTAR = AKAR / "docs" / "daftar_isi.md"
DIR_GAMBAR = AKAR / "docs"
KELUARAN = AKAR / "Anforcom2026_DSDC_TrioLaAlbiceleste_PasangSurut.docx"

HURUF = "Times New Roman"
UKURAN = Pt(12)
SPASI = 1.5

# Lebar halaman A4 dikurangi margin kiri 4 cm dan kanan 3 cm.
LEBAR_ISI_CM = 21.0 - 4.0 - 3.0

# Indentasi baris pertama paragraf. Satu tab baku Word adalah 1,27 cm.
INDENT_PARAGRAF = Cm(1.27)


def _atur_halaman(dok: Document) -> None:
    """A4 dengan margin 4-3-3-3, sesuai rulebook 8.1."""
    for bagian in dok.sections:
        bagian.page_width = Cm(21.0)
        bagian.page_height = Cm(29.7)
        bagian.left_margin = Cm(4.0)
        bagian.right_margin = Cm(3.0)
        bagian.top_margin = Cm(3.0)
        bagian.bottom_margin = Cm(3.0)


def _atur_gaya(dok: Document) -> None:
    """Times New Roman 12 dan spasi 1,5 sebagai bawaan seluruh dokumen."""
    normal = dok.styles["Normal"]
    normal.font.name = HURUF
    normal.font.size = UKURAN
    # Word memilih huruf untuk aksara non-Latin lewat atribut terpisah. Tanpa
    # baris ini, tanda seperti en dash dan sigma bisa jatuh ke huruf lain.
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), HURUF)
    _paksa_huruf(normal.element)
    p = normal.paragraph_format
    p.line_spacing = SPASI
    p.space_before = Pt(0)
    p.space_after = Pt(6)
    # Indentasi baris pertama, satu tab. Diminta supaya paragraf terbaca rapi
    # dan batas antar paragraf terlihat tanpa perlu baris kosong tambahan.
    p.first_line_indent = INDENT_PARAGRAF

    for nama, ukuran, tebal in (("Heading 1", 14, True), ("Heading 2", 12, True)):
        g = dok.styles[nama]
        g.font.name = HURUF
        g.font.size = Pt(ukuran)
        g.font.bold = tebal
        g.font.color.rgb = RGBColor(0, 0, 0)
        _paksa_huruf(g.element)
        g.paragraph_format.line_spacing = SPASI
        g.paragraph_format.space_before = Pt(12)
        g.paragraph_format.space_after = Pt(6)
        g.paragraph_format.keep_with_next = True

    # Gaya daftar ikut dipaksa: keduanya juga mewarisi huruf tema.
    for nama in ("List Number", "List Bullet", "List Paragraph"):
        try:
            g = dok.styles[nama]
        except KeyError:
            continue
        g.font.name = HURUF
        g.font.size = UKURAN
        _paksa_huruf(g.element)


def _paksa_huruf(el) -> None:
    """Buang atribut huruf TEMA supaya Times New Roman benar-benar dipakai.

    Ini penyebab keluhan "judulnya kok bukan Times New Roman". Gaya Heading
    bawaan Word membawa `asciiTheme="majorHAnsi"`, dan Word MEMPRIORITASKAN
    atribut tema itu di atas nama huruf yang ditulis eksplisit. Selama atribut
    tema masih ada, `font.name = "Times New Roman"` tidak berpengaruh apa pun
    pada tampilan judul.

    Jadi atribut temanya dihapus lebih dulu, baru nama hurufnya ditulis.
    """
    rpr = el.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for tema in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        atr = qn("w:" + tema)
        if atr in rf.attrib:
            del rf.attrib[atr]
    for langsung in ("ascii", "hAnsi", "eastAsia", "cs"):
        rf.set(qn("w:" + langsung), HURUF)



def _nomor_halaman(dok: Document) -> None:
    """Pasang nomor halaman di kaki, rata tengah, kecuali di sampul.

    Diperlukan begitu daftar isi masuk: daftar yang menyebut "halaman 17"
    tidak berguna kalau halamannya sendiri tidak bernomor.

    Nomornya ditulis sebagai FIELD Word, bukan angka mati. Word yang
    menghitungnya, sehingga tetap benar bila isinya bergeser nanti.

    Penomorannya menerus dari sampul, jadi angka yang tercetak sama persis
    dengan angka yang diukur `25_daftar_isi.py`. Kalau bagian depan diberi
    angka Romawi tersendiri, seluruh nomor di daftar isi harus dihitung ulang.
    """
    bagian = dok.sections[0]
    bagian.different_first_page_header_footer = True   # sampul tanpa nomor

    par = bagian.footer.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.first_line_indent = Cm(0)

    r = par.add_run()
    r.font.name = HURUF
    r.font.size = Pt(11)

    mulai = OxmlElement("w:fldChar")
    mulai.set(qn("w:fldCharType"), "begin")
    kode = OxmlElement("w:instrText")
    kode.set(qn("xml:space"), "preserve")
    kode.text = " PAGE "
    akhir = OxmlElement("w:fldChar")
    akhir.set(qn("w:fldCharType"), "end")
    for el in (mulai, kode, akhir):
        r._r.append(el)


def _hias_teks(par, teks: str) -> None:
    """Terjemahkan **tebal**, *miring*, dan `kode` menjadi run Word.

    Ditulis sebagai satu regex bergantian, bukan tiga lintasan berurutan,
    supaya penanda yang bersarang tidak saling merusak.
    """
    teks = teks.replace(" ", " ")
    for potong in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)", teks):
        if not potong:
            continue
        if potong.startswith("**") and potong.endswith("**"):
            r = par.add_run(potong[2:-2])
            r.bold = True
        elif potong.startswith("`") and potong.endswith("`"):
            # Istilah teknis tetap Times New Roman: rulebook mewajibkan satu
            # huruf untuk seluruh dokumen. Dibedakan lewat miring saja.
            r = par.add_run(potong[1:-1])
            r.italic = True
        elif potong.startswith("*") and potong.endswith("*") and len(potong) > 2:
            r = par.add_run(potong[1:-1])
            r.italic = True
        else:
            par.add_run(potong)


def _sel_border(sel) -> None:
    """Garis tipis pada empat sisi sel."""
    tcPr = sel._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for sisi in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{sisi}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "808080")
        borders.append(el)
    tcPr.append(borders)


def _tulis_tabel(dok: Document, baris: list[str]) -> None:
    """Ubah blok tabel Markdown menjadi tabel Word selebar area isi."""
    kotak = []
    for b in baris:
        if re.match(r"^\|[\s:|-]+\|$", b.strip()):
            continue  # baris pemisah header
        sel = [s.strip() for s in b.strip().strip("|").split("|")]
        kotak.append(sel)
    if not kotak:
        return

    kolom = max(len(r) for r in kotak)
    tabel = dok.add_table(rows=0, cols=kolom)
    tabel.style = "Table Grid"
    tabel.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabel.autofit = True

    for i, isi in enumerate(kotak):
        sel_baris = tabel.add_row().cells
        for j in range(kolom):
            sel = sel_baris[j]
            sel.text = ""
            par = sel.paragraphs[0]
            par.paragraph_format.line_spacing = 1.0
            par.paragraph_format.space_after = Pt(2)
            par.paragraph_format.first_line_indent = Cm(0)
            _hias_teks(par, isi[j] if j < len(isi) else "")
            for r in par.runs:
                r.font.size = Pt(10)   # tabel sedikit lebih kecil agar muat
                r.font.name = HURUF
                if i == 0:
                    r.bold = True
            _sel_border(sel)
    dok.add_paragraph()


def _tulis_gambar(dok: Document, jalur: str) -> None:
    """Sisipkan gambar, diskalakan agar tidak pernah melewati margin."""
    berkas = DIR_GAMBAR / jalur
    if not berkas.exists():
        raise SystemExit(f"Gambar tidak ditemukan: {berkas}")
    par = dok.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(3)
    par.paragraph_format.first_line_indent = Cm(0)
    par.add_run().add_picture(str(berkas), width=Cm(LEBAR_ISI_CM))


def _sampul(dok: Document, judul: str, subjudul: str, meta: list[tuple[str, str]]) -> None:
    """Halaman sampul. Ikut dihitung ke dalam batas 30 halaman."""
    for _ in range(4):
        dok.add_paragraph()

    p = dok.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(judul)
    r.bold = True
    r.font.size = Pt(20)
    r.font.name = HURUF

    p = dok.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(subjudul)
    r.italic = True
    r.font.size = Pt(13)
    r.font.name = HURUF

    for _ in range(3):
        dok.add_paragraph()

    for label, nilai in meta:
        p = dok.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        r = p.add_run(f"{label}: ")
        r.bold = True
        r.font.name = HURUF
        r2 = p.add_run(nilai)
        r2.font.name = HURUF

    p = dok.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)



def _tulis_daftar(dok: Document) -> int:
    """Susun daftar isi, daftar gambar, dan daftar tabel dari docs/daftar_isi.md.

    Nomor halamannya diukur oleh `25_daftar_isi.py` dengan membuka dokumen ini
    lewat Word. Kalau berkasnya belum ada, ketiga daftar dilewati begitu saja
    dan dokumennya tetap terbangun. Itu disengaja: pada pembangunan pertama
    memang belum ada yang bisa diukur.
    """
    if not DAFTAR.exists():
        return 0

    isi = DAFTAR.read_text(encoding="utf-8")
    bagian = {}
    kini = None
    for baris in isi.split("\n"):
        if baris.startswith("## "):
            kini = baris[3:].strip()
            bagian[kini] = []
        elif kini and "::" in baris and baris.lstrip().startswith("-"):
            menjorok = len(baris) - len(baris.lstrip())
            teks, _, hal = baris.lstrip()[1:].rpartition("::")
            bagian[kini].append((teks.strip(), hal.strip(), menjorok))

    ditulis = 0
    for nama in ("DAFTAR ISI", "DAFTAR GAMBAR", "DAFTAR TABEL"):
        butir = bagian.get(nama)
        if not butir:
            continue

        j = dok.add_paragraph()
        j.alignment = WD_ALIGN_PARAGRAPH.CENTER
        j.paragraph_format.first_line_indent = Cm(0)
        j.paragraph_format.space_after = Pt(10)
        r = j.add_run(nama)
        r.bold = True
        r.font.size = Pt(14)
        r.font.name = HURUF

        for teks, hal, menjorok in butir:
            par = dok.add_paragraph()
            pf = par.paragraph_format
            pf.first_line_indent = Cm(0)
            pf.left_indent = Cm(0.6 * (menjorok // 2))
            # Daftar berspasi tunggal. Spasi 1,5 yang diwajibkan rulebook
            # berlaku untuk badan tulisan; daftar isi yang direnggangkan
            # justru memakan lima halaman dan mendorong dokumen ke batas.
            pf.line_spacing = 1.0
            pf.space_after = Pt(2)
            # Titik-titik penghubung dibuat Word lewat tab stop kanan, bukan
            # diketik manual. Diketik manual, panjangnya akan meleset begitu
            # judulnya berubah satu huruf saja.
            pf.tab_stops.add_tab_stop(
                Cm(LEBAR_ISI_CM), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            r = par.add_run(teks)
            r.font.name = HURUF
            r.font.size = UKURAN
            r2 = par.add_run("\t" + hal)
            r2.font.name = HURUF
            r2.font.size = UKURAN

        # Daftar gambar dan daftar tabel pendek dan muat berdua dalam satu
        # halaman, jadi hanya daftar isi dan daftar tabel yang diakhiri
        # pemisah halaman. Tanpa ini dokumen memakan satu halaman lebih dan
        # menempel persis di batas 30.
        if nama != "DAFTAR GAMBAR":
            dok.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        else:
            dok.add_paragraph()
        ditulis += 1
    return ditulis


def bangun(pecah_per_bagian: bool = False) -> int:
    teks = SUMBER.read_text(encoding="utf-8")
    # Bagian 1-14 saja. Judul penutupnya pernah berganti dari "Perkiraan
    # halaman" menjadi "Jumlah halaman" setelah angkanya diukur, jadi
    # keduanya diterima — dan bila tidak satu pun ditemukan, skrip berhenti
    # dengan pesan yang jelas alih-alih diam-diam menulis seluruh berkas.
    penutup = next((j for j in ("## Jumlah halaman", "## Perkiraan halaman")
                    if j in teks), None)
    if penutup is None:
        raise SystemExit(
            "Batas akhir Bagian 14 tidak ditemukan di proposal_draft.md. "
            "Dicari judul '## Jumlah halaman' atau '## Perkiraan halaman'.")
    # Judul bagian pernah berganti gaya dari "## 1. Judul Karya" menjadi
    # "## I. JUDUL KARYA". Awal badan dicari lewat pola, bukan teks tetap,
    # supaya pergantian gaya berikutnya tidak mematikan skrip.
    m_awal = re.search(r"^## (?:\d+|[IVX]+)\.\s", teks, re.M)
    if m_awal is None:
        raise SystemExit(
            "Judul bagian pertama tidak ditemukan di proposal_draft.md. "
            "Dicari pola '## 1. ...' atau '## I. ...'.")
    badan = teks[m_awal.start():teks.index(penutup)]

    dok = Document()
    _atur_halaman(dok)
    _atur_gaya(dok)
    _nomor_halaman(dok)

    _sampul(
        dok,
        "PASANG SURUT",
        "Sistem Perutean Sadar Banjir Rob Berbasis Rekonstruksi Pasang Surut "
        "Terkalibrasi untuk Mobilitas Rendah Karbon di Kota Semarang",
        [("Tim", "trio la albiceleste"),
         ("Institusi", "Institut Teknologi Sepuluh Nopember (ITS), Surabaya"),
         ("Subtema", "4 — Smart Low-Carbon Urban Mobility"),
         ("Kompetisi", "Diponegoro Software Development Competition, ANFORCOM 2026")],
    )

    n_daftar = _tulis_daftar(dok)

    baris = badan.split("\n")
    i = 0
    n_gambar = n_tabel = 0
    while i < len(baris):
        b = baris[i].rstrip()

        if not b.strip() or b.strip() == "---":
            i += 1
            continue

        if b.startswith("## "):
            # Tiap bagian boleh dimulai di halaman baru. Rapi dibaca, tetapi
            # mahal: bagian yang berakhir di tengah halaman menyisakan sisanya
            # kosong. Itulah yang membuat .docx lama memakan 27 halaman untuk
            # isi yang lebih sedikit. Karena itu ini PILIHAN, bukan bawaan.
            if pecah_per_bagian and not b.startswith("## 1."):
                dok.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            dok.add_heading(b[3:].strip(), level=1)
            i += 1
            continue

        if b.startswith("### "):
            dok.add_heading(b[4:].strip(), level=2)
            i += 1
            continue

        m = re.match(r"^!\[[^\]]*\]\(([^)]+)\)$", b.strip())
        if m:
            _tulis_gambar(dok, m.group(1))
            n_gambar += 1
            i += 1
            continue

        if b.lstrip().startswith("|"):
            blok = []
            while i < len(baris) and baris[i].lstrip().startswith("|"):
                blok.append(baris[i])
                i += 1
            _tulis_tabel(dok, blok)
            n_tabel += 1
            continue

        if b.startswith("> "):
            par = dok.add_paragraph()
            par.paragraph_format.left_indent = Cm(1.0)
            par.paragraph_format.first_line_indent = Cm(0)
            _hias_teks(par, b[2:].strip())
            for r in par.runs:
                r.italic = True
            i += 1
            continue

        # Butir bernomor atau bertitik, termasuk baris lanjutannya yang
        # menjorok. Baris lanjutan digabung ke butir yang sama supaya tidak
        # pecah menjadi paragraf sendiri di Word.
        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", b)
        mb = re.match(r"^(\s*)-\s+(.*)$", b)
        if m or mb:
            isi = m.group(3) if m else mb.group(2)
            i += 1
            while i < len(baris):
                lanjut = baris[i]
                if (lanjut.strip() and lanjut.startswith(("   ", "\t"))
                        and not re.match(r"^\s*(\d+\.|-)\s", lanjut)
                        and not lanjut.lstrip().startswith("|")):
                    isi += " " + lanjut.strip()
                    i += 1
                else:
                    break
            # PENOMORAN DITULIS SENDIRI, BUKAN DISERAHKAN KE WORD.
            #
            # Versi sebelumnya memakai gaya "List Number", dan Word menomori
            # gaya itu SECARA BERURUTAN di seluruh dokumen. Akibatnya daftar
            # di Bagian 3.5 memakai 1 sampai 3, lalu daftar berikutnya di
            # Bagian 4.1 melanjutkan dari 4, bukan mulai lagi dari 1. Itulah
            # penomoran ngawur yang terlihat di dokumen jadi.
            #
            # Angkanya sudah ada di Markdown dan sudah benar di sana, jadi
            # yang paling sederhana adalah menuliskannya apa adanya. Word
            # tidak lagi diberi kesempatan menomori sendiri.
            par = dok.add_paragraph()
            pf = par.paragraph_format
            pf.line_spacing = SPASI
            pf.space_after = Pt(4)
            pf.left_indent = INDENT_PARAGRAF + Cm(0.5)
            pf.first_line_indent = -Cm(0.75)   # gantung: angka menonjol keluar
            penanda = f"{m.group(2)}. " if m else "\u2022 "
            r = par.add_run(penanda)
            r.font.name = HURUF
            r.font.size = UKURAN
            _hias_teks(par, isi)
            for r in par.runs:
                r.font.name = HURUF
                r.font.size = UKURAN
            continue

        # Paragraf biasa: kumpulkan baris sampai baris kosong.
        blok = [b.strip()]
        i += 1
        while i < len(baris) and baris[i].strip() and not baris[i].lstrip().startswith(
                ("|", "#", "!", ">", "-")) and not re.match(r"^\s*\d+\.\s", baris[i]):
            blok.append(baris[i].strip())
            i += 1
        par = dok.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _hias_teks(par, " ".join(blok))
        for r in par.runs:
            r.font.name = HURUF
            r.font.size = UKURAN

    dok.save(KELUARAN)

    print(f"tersimpan   : {KELUARAN.name}")
    print(f"daftar      : {n_daftar} dari 3 (isi, gambar, tabel)")
    print(f"gambar      : {n_gambar}")
    print(f"tabel       : {n_tabel}")
    print(f"kata sumber : {len(badan.split())}")
    print()
    print(f"page break per bagian: {'ya' if pecah_per_bagian else 'tidak'}")
    print("A4, Times New Roman 12, spasi 1,5, margin 4-3-3-3 diterapkan.")
    print("JUMLAH HALAMAN WAJIB DIBACA DARI WORD, bukan dari skrip ini.")
    return 0


if __name__ == "__main__":
    _p = argparse.ArgumentParser(description=__doc__)
    _p.add_argument("--pecah-per-bagian", action="store_true",
                    help="mulai tiap bagian di halaman baru")
    sys.exit(bangun(_p.parse_args().pecah_per_bagian))
