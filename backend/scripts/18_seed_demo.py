"""Bekukan satu potret lengkap ke berkas, supaya demo tidak bisa mati.

    python -m scripts.18_seed_demo                # 72 jam sejak jam ini
    python -m scripts.18_seed_demo --mulai 2026-05-18
    python -m scripts.18_seed_demo --periksa      # hanya memeriksa berkas

CATATAN PENOMORAN. Brief M6 menyebut berkas ini `08_seed_demo.py`, tetapi
nomor 08 sudah dipakai `08_ekstrak_s1.py` sejak M4. Memakai nomor yang sama
dua kali akan membuat urutan pipeline tidak bisa dibaca dari daftar berkas,
dan itu justru satu-satunya guna penomorannya. Dipakai 18.

APA YANG DIBEKUKAN, DAN KENAPA.

Aplikasi ini akan dipakai juri di ruangan yang wifi-nya tidak kita kendalikan,
menghubungi database di Sydney yang tiap kuerinya memakan ratusan milidetik.
Dua hal bisa gagal: jaringan acara, dan database. Keduanya di luar kendali
kita, dan keduanya jatuh tepat saat penilaian berlangsung.

Berkas ini memuat SELURUH yang dibutuhkan aplikasi untuk berjalan tanpa
database sama sekali:

    ruas          19.394 ruas beserta geometri dan atributnya
    jam           sumbu waktu 72 jam beserta tinggi pasut
    genangan      kedalaman tiap ruas pada tiap jam
    ambang_moda   ambang kelayakan tiap moda

Lapisan API sudah punya jalur cadangan berkas untuk jaringan jalan sejak M2.
Yang ditambahkan sekarang adalah prediksinya, sehingga cadangannya lengkap,
bukan setengah.

YANG TIDAK DIBEKUKAN, DAN KENAPA TIDAK.

Perutean TIDAK dibekukan. Membekukan hasil rute berarti menyiapkan jawaban
untuk pasangan titik yang sudah kita pilih sendiri, dan juri yang mengetuk
titik lain akan menemukan aplikasinya diam. Graf routing dibangun dari
`ruas` di berkas ini, jadi perutean tetap hidup dan tetap menghitung
sungguhan tanpa database.

BATAS KEJUJURAN. Potret ini punya tanggal. Bila dipakai di luar jendela
waktunya, aplikasi menampilkan prediksi yang sudah lewat — dan itu lebih
berbahaya daripada layar kosong untuk sistem yang menyarankan kapan orang
boleh menembus air. Karena itu berkasnya membawa `berlaku_sampai`, dan
lapisan API menolak memakainya setelah lewat.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

from app import config, db

BERKAS = config.DIR_DATA_OLAHAN / "potret_demo.json"
JAM = 72


def bekukan(mulai: datetime, jam: int) -> dict:
    selesai = mulai + timedelta(hours=jam - 1)

    with db.koneksi() as kon:
        repo_ruas = db.RepositoriRuas(kon)
        ruas = repo_ruas.geojson()
        ambang = repo_ruas.ambang_moda()

        # SIMPUL UJUNG WAJIB IKUT. `geojson()` sengaja tidak memuat osm_u dan
        # osm_v karena frontend tidak membutuhkannya. Tetapi mesin routing
        # membangun grafnya dari pasangan simpul itu, dan tanpa keduanya
        # seluruh ruas akan tersambung ke simpul yang sama — grafnya menjadi
        # satu titik, dan perutean gagal dengan galat yang tidak menyebut
        # sebabnya sama sekali.
        with kon.cursor() as kur:
            kur.execute("SELECT edge_id, osm_u, osm_v FROM ruas_jalan")
            simpul = {int(a_): (int(b_), int(c_)) for a_, b_, c_ in kur.fetchall()}
    for f in ruas["features"]:
        u, v = simpul.get(int(f["properties"]["edge_id"]), (0, 0))
        f["properties"]["osm_u"], f["properties"]["osm_v"] = u, v

    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT waktu, tinggi_pasut_m FROM pemicu
                WHERE waktu BETWEEN %s AND %s ORDER BY waktu
                """,
                (mulai, selesai),
            )
            pemicu = [(w, float(t)) for w, t in kur.fetchall()]

            kur.execute(
                """
                SELECT waktu, edge_id, kedalaman_cm, probabilitas, sumber
                FROM prediksi_genangan
                WHERE waktu BETWEEN %s AND %s
                ORDER BY waktu, edge_id
                """,
                (mulai, selesai),
            )
            baris = kur.fetchall()

    # Genangan disusun per jam. Ruas kering TIDAK disimpan, sama seperti di
    # database: ruas tanpa entri berarti kering. Menyimpan 19.394 nol untuk
    # tiap jam akan melipatgandakan ukuran berkas tanpa menambah satu pun
    # keterangan.
    per_jam: dict[str, dict] = {}
    sumber = set()
    for waktu, edge_id, kedalaman, probabilitas, s in baris:
        kunci = waktu.isoformat()
        per_jam.setdefault(kunci, {})[str(int(edge_id))] = [
            round(float(kedalaman), 1), round(float(probabilitas), 4)
        ]
        sumber.add(s)

    return {
        "_catatan": (
            "Potret beku untuk demo. Dipakai lapisan API hanya bila database "
            "tidak bisa dihubungi. Dibuat oleh backend/scripts/18_seed_demo.py."
        ),
        "dibuat": datetime.now(timezone.utc).isoformat(),
        "mulai": mulai.isoformat(),
        "selesai": selesai.isoformat(),
        # Setelah jam ini potret dianggap basi dan TIDAK dipakai.
        "berlaku_sampai": selesai.isoformat(),
        "sumber_data": sorted(sumber),
        "jam": [
            {"waktu_utc": w.isoformat(), "tinggi_pasut_m": round(t, 4),
             "ruas_tergenang": len(per_jam.get(w.isoformat(), {})),
             "kedalaman_maks_cm": round(
                 max((v[0] for v in per_jam.get(w.isoformat(), {}).values()),
                     default=0.0), 1)}
            for w, t in pemicu
        ],
        "ambang_moda": ambang,
        "genangan": per_jam,
        "ruas": ruas,
    }


def periksa() -> int:
    if not BERKAS.exists():
        print(f"{BERKAS.name} belum ada.")
        return 1
    d = json.loads(BERKAS.read_text(encoding="utf-8"))
    sampai = datetime.fromisoformat(d["berlaku_sampai"])
    sisa = sampai - datetime.now(timezone.utc)
    print(f"dibuat        : {d['dibuat']}")
    print(f"periode       : {d['mulai']} sampai {d['selesai']}")
    print(f"sumber data   : {', '.join(d['sumber_data'])}")
    print(f"ruas          : {len(d['ruas']['features']):,}")
    print(f"jam           : {len(d['jam'])}")
    print(f"jam bergenangan: {sum(1 for j in d['jam'] if j['ruas_tergenang'])}")
    print(f"ukuran        : {BERKAS.stat().st_size / 1e6:.1f} MB")
    if sisa.total_seconds() <= 0:
        print(f"\nPOTRET SUDAH BASI, lewat {-sisa.days} hari.")
        print("Jalankan ulang sebelum demo, atau API akan menolak memakainya.")
        return 1
    print(f"\nmasih berlaku {sisa.days} hari {sisa.seconds // 3600} jam")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mulai", default=None)
    p.add_argument("--jam", type=int, default=JAM)
    p.add_argument("--periksa", action="store_true")
    a = p.parse_args()

    if a.periksa:
        return periksa()

    mulai = (datetime.fromisoformat(a.mulai).replace(tzinfo=timezone.utc)
             if a.mulai else
             datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0))

    print(f"membekukan {a.jam} jam sejak {mulai:%Y-%m-%d %H:%M} UTC ...")
    potret = bekukan(mulai, a.jam)
    if not potret["jam"]:
        raise SystemExit(
            "Tabel pemicu tidak memuat jendela itu. Jalankan "
            "`python -m scripts.06_isi_pemicu --prakiraan` lebih dulu.")

    BERKAS.write_text(json.dumps(potret, ensure_ascii=False,
                                 separators=(",", ":")), encoding="utf-8")
    print()
    return periksa()


if __name__ == "__main__":
    sys.exit(main())
