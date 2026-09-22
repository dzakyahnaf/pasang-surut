"""Jalankan model genangan untuk 72 jam ke depan, tulis ke prediksi_genangan.

    python -m scripts.10_prediksi                    # 72 jam sejak jam ini
    python -m scripts.10_prediksi --mulai 2026-05-18 # jendela tertentu
    python -m scripts.10_prediksi --pertahankan-dummy

INI LANGKAH YANG MENGGANTI DATA CONTOH DENGAN MODEL ASLI.

Aturan repo nomor 2: baris `sumber = 'dummy'` membuat antarmuka menampilkan
lencana DATA CONTOH, dan lencana itu hilang sendiri begitu isinya berganti
`model_v1`. Tidak ada satu baris kode antarmuka pun yang perlu disentuh —
memang begitu kontraknya dirancang sejak M2.

Skrip ini karena itu MENGHAPUS baris dummy setelah baris model masuk, kecuali
diminta sebaliknya lewat --pertahankan-dummy.

KENAPA HANYA RUAS TERGENANG YANG DISIMPAN.

Tabel `prediksi_genangan` tidak menyimpan baris untuk ruas kering; ruas tanpa
baris terbaca kering lewat LEFT JOIN. Itu keputusan lama yang tercatat di
docs/batasan.md bagian 5.4, dan konsekuensinya sistem tidak bisa membedakan
"diprediksi kering" dari "belum ada prediksi". Untuk 19.394 ruas kali 72 jam,
menyimpan semuanya berarti 1,4 juta baris yang 98 persennya nol.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

from app import config, db
from app.domain import genangan

BERKAS_MODEL = config.DIR_DATA_OLAHAN / "model_genangan_v1.joblib"
JAM_KE_DEPAN = 72
SUMBER = "model_v1"


def acuan_pasut() -> tuple[float, float]:
    """Ambil acuan bawah dan puncak pasut dari sebaran rekonstruksi sendiri.

    Bawah adalah nilai tengah seluruh jam; puncak adalah persentil ke-99,9.
    Persentil, bukan maksimum, supaya satu jam ekstrem tidak menentukan skala
    seluruh sistem.
    """
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT percentile_cont(0.5)   WITHIN GROUP (ORDER BY tinggi_pasut_m),
                       percentile_cont(0.999) WITHIN GROUP (ORDER BY tinggi_pasut_m)
                FROM pemicu
                """
            )
            a, b = kur.fetchone()
    return float(a), float(b)


def fitur_statis() -> tuple[np.ndarray, np.ndarray]:
    """(edge_id, matriks 3 kolom: elevasi, jarak pantai, subsidensi)."""
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT edge_id, elevasi_m, jarak_pantai_m, laju_subsidensi_cm_thn
                FROM ruas_jalan ORDER BY edge_id
                """
            )
            baris = kur.fetchall()
    edge = np.array([b[0] for b in baris], dtype=np.int64)
    X = np.array([[np.nan if v is None else float(v) for v in b[1:]]
                  for b in baris], dtype=np.float64)
    return edge, X


def pemicu_jendela(mulai: datetime, jam: int):
    """(waktu, pasut, hujan24, hujan72) untuk tiap jam pada jendela."""
    selesai = mulai + timedelta(hours=jam - 1)
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT waktu, tinggi_pasut_m, hujan_24j_mm, hujan_72j_mm
                FROM pemicu WHERE waktu BETWEEN %s AND %s ORDER BY waktu
                """,
                (mulai, selesai),
            )
            baris = kur.fetchall()
    if len(baris) < jam:
        raise SystemExit(
            f"Tabel pemicu hanya punya {len(baris)} dari {jam} jam yang diminta "
            f"({mulai:%Y-%m-%d %H:%M} sampai {selesai:%Y-%m-%d %H:%M}).\n"
            "Jalankan `python -m scripts.06_isi_pemicu --prakiraan` lebih dulu."
        )
    return baris


def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--mulai", default=None,
                          help="YYYY-MM-DD, bawaan: jam bulat sekarang")
    pengurai.add_argument("--jam", type=int, default=JAM_KE_DEPAN)
    pengurai.add_argument("--pertahankan-dummy", action="store_true")
    argumen = pengurai.parse_args()

    if not BERKAS_MODEL.exists():
        raise SystemExit(
            f"{BERKAS_MODEL.name} belum ada. Jalankan skrip 09 lebih dulu."
        )

    import joblib

    bundel = joblib.load(BERKAS_MODEL)
    model = bundel["model"]
    ambang_p = float(bundel["ambang_probabilitas"])
    print(f"model dilatih {bundel['dilatih']}")
    print(f"ambang probabilitas: {ambang_p:.3f}")
    print(f"fitur: {', '.join(bundel['fitur'])}\n")

    if argumen.mulai:
        mulai = datetime.fromisoformat(argumen.mulai).replace(tzinfo=timezone.utc)
    else:
        mulai = datetime.now(timezone.utc).replace(
            minute=0, second=0, microsecond=0)

    baris_pemicu = pemicu_jendela(mulai, argumen.jam)
    edge, statis = fitur_statis()
    bawah, puncak = acuan_pasut()

    print(f"jendela : {mulai:%Y-%m-%d %H:%M} UTC, {argumen.jam} jam")
    print(f"ruas    : {len(edge):,}")
    print(f"acuan pasut: bawah {bawah:+.3f} m, puncak {puncak:+.3f} m\n")

    hasil = []
    ringkas = []
    for waktu, pasut_m, h24, h72 in baris_pemicu:
        X = np.column_stack([
            statis,
            np.full(len(edge), float(pasut_m)),
            np.full(len(edge), float(h24 or 0.0)),
            np.full(len(edge), float(h72 or 0.0)),
        ])
        prob = model.predict_proba(X)[:, 1]
        dalam = genangan.kedalaman_cm(prob, float(pasut_m), ambang_p,
                                      bawah, puncak)
        pilih = np.flatnonzero(prob >= ambang_p)
        for i in pilih:
            hasil.append((int(edge[i]), waktu, round(float(dalam[i]), 1),
                          round(float(prob[i]), 4), SUMBER))
        ringkas.append((waktu, float(pasut_m), len(pilih),
                        float(dalam.max()) if len(pilih) else 0.0))

    print(f"{'waktu WIB':<17} {'pasut':>8} {'tergenang':>10} {'maks cm':>8}")
    for waktu, pasut_m, n, maks in ringkas[::6]:
        wib = waktu.astimezone(config.ZONA_WAKTU_LOKAL)
        print(f"{wib:%Y-%m-%d %H:%M}  {pasut_m:+7.3f} {n:>10,} {maks:>8.1f}")

    n_jam_bergenang = sum(1 for _, _, n, _ in ringkas if n)
    print()
    print(f"baris prediksi   : {len(hasil):,}")
    print(f"jam dengan genangan: {n_jam_bergenang} dari {len(ringkas)}")
    if ringkas:
        print(f"puncak ruas tergenang: {max(n for _, _, n, _ in ringkas):,} "
              f"dari {len(edge):,} "
              f"({100.0 * max(n for _, _, n, _ in ringkas) / len(edge):.1f} persen)")

    print("\nmenulis ke database ...")
    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        repo.publikasikan(hasil, [w for w, *_ in ringkas], SUMBER)
        if not argumen.pertahankan_dummy:
            n_dummy = repo.kosongkan_sumber("dummy")
            print(f"  {n_dummy:,} baris dummy dihapus")

    with db.koneksi() as kon:
        repo = db.RepositoriGenangan(kon)
        print(f"  total baris: {repo.hitung():,}")
        print(f"  sumber di tabel: {repo.sumber_yang_ada()}")
        awal, akhir = repo.rentang_waktu()
        print(f"  periode: {awal} sampai {akhir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
