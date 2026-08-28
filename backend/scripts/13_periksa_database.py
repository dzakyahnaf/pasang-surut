"""Periksa dan siapkan koneksi database, tanpa pernah mencetak kata sandi.

    python -m scripts.13_periksa_database              # hanya memeriksa
    python -m scripts.13_periksa_database --perbaiki   # persen-encode sandi
    python -m scripts.13_periksa_database --pasang-skema

KENAPA SKRIP INI ADA.

Pindah dari PostGIS lokal ke Supabase gagal dengan pesan yang menyesatkan:

    connection to server on socket "@db.xxx.supabase.co/.s.PGSQL.5432"
    failed: Invalid argument

Pesan itu menyebut SOCKET, seolah-olah masalahnya server lokal, padahal
host-nya jelas Supabase. Penyebab sebenarnya ada di URL: kata sandi memuat
karakter yang punya arti khusus di dalam URL, paling sering '@'. Pengurai URL
memotong di '@' TERAKHIR, sehingga sisa kata sandi ikut terbaca sebagai nama
host, dan psycopg2 menyerah lalu mencoba socket lokal.

Skrip ini menemukan hal itu tanpa pernah menampilkan kata sandinya, dan bila
diminta akan memperbaikinya dengan persen-encoding.

KARAKTER YANG WAJIB DI-ENCODE DI DALAM KATA SANDI URL:

    @ -> %40    : -> %3A    / -> %2F    ? -> %3F
    # -> %23    [ -> %5B    ] -> %5D    % -> %25
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from urllib.parse import quote, urlsplit

from app import config

BERKAS_ENV = config.AKAR_REPO / ".env"

# Karakter yang mengubah arti URL bila muncul mentah di dalam kata sandi.
BERBAHAYA = "@:/?#[]%"


def bagi_url(url: str) -> tuple[str, str, str, str] | None:
    """Pecah URL jadi (awalan, pengguna, sandi, sisa) tanpa mengurai penuh.

    Tidak memakai urlsplit untuk bagian ini, justru karena urlsplit-lah yang
    salah menguraikannya ketika sandinya memuat karakter khusus. Yang dipakai
    adalah aturan yang benar menurut spesifikasi: bagian otoritas berakhir di
    '@' TERAKHIR sebelum host.
    """
    m = re.match(r"^(postgres(?:ql)?://)(.*)$", url)
    if not m:
        return None
    awalan, sisa = m.group(1), m.group(2)
    if "@" not in sisa:
        return None
    otoritas, host = sisa.rsplit("@", 1)
    if ":" not in otoritas:
        return None
    pengguna, sandi = otoritas.split(":", 1)
    return awalan, pengguna, sandi, host


def periksa(url: str) -> list[str]:
    """Kembalikan daftar masalah. Tidak pernah memuat kata sandi."""
    masalah = []
    bagian = bagi_url(url)
    if bagian is None:
        return ["URL tidak berbentuk postgresql://pengguna:sandi@host:port/basis"]

    _, pengguna, sandi, host = bagian
    ditemukan = sorted({c for c in sandi if c in BERBAHAYA})
    if ditemukan:
        masalah.append(
            "kata sandi memuat karakter yang wajib di-encode: "
            + " ".join(ditemukan)
            + "  (jalankan ulang dengan --perbaiki)"
        )
    if not host:
        masalah.append("bagian host kosong")
    if "supabase" in host and ":5432" in host and "pooler" not in host:
        masalah.append(
            "memakai koneksi LANGSUNG port 5432. Supabase menyajikannya lewat "
            "IPv6, dan banyak jaringan rumah serta platform deploy masih "
            "IPv4-saja. Untuk deploy pakai Session atau Transaction pooler "
            "dari dasbor Supabase (host berakhiran pooler.supabase.com)."
        )
    return masalah


def perbaiki(url: str) -> str | None:
    """Kembalikan URL dengan kata sandi ter-persen-encode, atau None."""
    bagian = bagi_url(url)
    if bagian is None:
        return None
    awalan, pengguna, sandi, host = bagian
    if not any(c in BERBAHAYA for c in sandi):
        return None
    return f"{awalan}{quote(pengguna, safe='')}:{quote(sandi, safe='')}@{host}"


def tulis_env(url_baru: str) -> None:
    """Ganti baris DATABASE_URL di .env, sisanya tidak disentuh."""
    cadangan = BERKAS_ENV.with_suffix(".env.cadangan")
    shutil.copy2(BERKAS_ENV, cadangan)
    baris = BERKAS_ENV.read_text(encoding="utf-8").split("\n")
    ketemu = False
    for i, b in enumerate(baris):
        if b.startswith("DATABASE_URL="):
            baris[i] = f"DATABASE_URL={url_baru}"
            ketemu = True
            break
    if not ketemu:
        raise SystemExit("Baris DATABASE_URL tidak ada di .env")
    BERKAS_ENV.write_text("\n".join(baris), encoding="utf-8")
    print(f"  .env diperbarui, salinan lama di {cadangan.name}")


def samarkan(url: str) -> str:
    bagian = bagi_url(url)
    if bagian is None:
        return "(bentuk tidak dikenali)"
    awalan, pengguna, _, host = bagian
    return f"{awalan}{pengguna}:***@{host}"


def uji_koneksi() -> bool:
    from app import db

    try:
        with db.koneksi() as kon:
            with kon.cursor() as kur:
                kur.execute("SELECT current_database(), current_user")
                nama, pengguna = kur.fetchone()
                print(f"  tersambung: basis '{nama}', pengguna '{pengguna}'")
                kur.execute("SELECT extname FROM pg_extension ORDER BY extname")
                ekstensi = [x[0] for x in kur.fetchall()]
                print(f"  ekstensi  : {', '.join(ekstensi)}")
                if "postgis" not in ekstensi:
                    print("  PERINGATAN: PostGIS belum aktif. Di Supabase, "
                          "aktifkan lewat Database > Extensions, atau jalankan "
                          "CREATE EXTENSION postgis;")
                kur.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public' "
                    "ORDER BY tablename")
                tabel = [x[0] for x in kur.fetchall()]
                print(f"  tabel     : {', '.join(tabel) if tabel else '(kosong)'}")
        return True
    except Exception as e:
        print(f"  GAGAL: {type(e).__name__}")
        print(f"  {str(e).strip()[:300]}")
        return False


def pasang_skema() -> int:
    from app import db

    berkas = config.DIR_DB / "schema.sql"
    if not berkas.exists():
        raise SystemExit(f"{berkas} tidak ada")
    isi = berkas.read_text(encoding="utf-8")
    print(f"menjalankan {berkas.name} ({len(isi):,} karakter) ...")
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(isi)
    print("  selesai")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--perbaiki", action="store_true",
                   help="persen-encode kata sandi di .env")
    p.add_argument("--pasang-skema", action="store_true",
                   help="jalankan db/schema.sql di database yang aktif")
    a = p.parse_args()

    url = config.DATABASE_URL
    if not url:
        raise SystemExit("DATABASE_URL kosong. Salin .env.example jadi .env.")

    print(f"URL: {samarkan(url)}\n")
    daftar = periksa(url)
    if daftar:
        print("masalah yang ditemukan:")
        for m in daftar:
            print(f"  - {m}")
    else:
        print("bentuk URL: tidak ada masalah")
    print()

    if a.perbaiki:
        baru = perbaiki(url)
        if baru is None:
            print("tidak ada yang perlu di-encode.")
        else:
            print("memperbaiki persen-encoding kata sandi ...")
            tulis_env(baru)
            print("  jalankan ulang skrip ini untuk menguji sambungannya")
            return 0

    print("menguji sambungan ...")
    ok = uji_koneksi()
    if ok and a.pasang_skema:
        print()
        return pasang_skema()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
