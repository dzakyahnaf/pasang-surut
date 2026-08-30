"""Uji menyeluruh seluruh endpoint: jalur normal, jalur galat, dan kasus tepi.

    python -m scripts.23_uji_menyeluruh                 # terhadap produksi
    python -m scripts.23_uji_menyeluruh --alamat http://127.0.0.1:8010

KENAPA SKRIP INI ADA, DAN KENAPA IA BUKAN PYTEST.

`pytest` di repo ini menguji fungsi murni: perutean, kerentanan, genangan,
konfigurasi. Yang TIDAK diujinya adalah lapisan HTTP pada layanan yang
sungguhan berjalan — CORS, bentuk balasan, penanganan masukan buruk, dan
perilaku saat titik yang diminta berada di luar wilayah kerja.

Justru di lapisan itulah dua cacat paling merugikan sesi ini ditemukan:
lencana yang hilang karena satu endpoint mengembalikan string alih-alih list,
dan Pita Pasut yang tersandera unduhan 6,6 MB. Keduanya lolos dari pytest
karena keduanya bukan soal logika, melainkan soal kontrak.

CARA MEMBACA HASILNYA.

    LULUS   perilaku sesuai harapan
    GAGAL   perilaku menyimpang, dan itu bug
    CATAT   perilaku sah tetapi layak diketahui, misalnya balasan lambat

Uji ini TIDAK mengubah apa pun. Seluruhnya baca, kecuali `/api/rute` yang
memakai POST tetapi tidak menulis data.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ASAL = "https://pasang-surut.vercel.app"
BAKU = "https://pasang-surut-api.onrender.com"

hasil: list[tuple[str, str, str]] = []


def catat(status: str, nama: str, ket: str = "") -> None:
    hasil.append((status, nama, ket))
    warna = {"LULUS": "LULUS", "GAGAL": "GAGAL", "CATAT": "CATAT"}[status]
    print(f"  {warna}  {nama}" + (f"  — {ket}" if ket else ""))


def panggil(alamat: str, jalur: str, muatan=None, asal: str = ASAL, batas: int = 240):
    """Kembalikan (kode, badan, detik). Kode 0 berarti gagal tersambung."""
    kepala = {"Content-Type": "application/json"}
    if asal:
        kepala["Origin"] = asal
    data = json.dumps(muatan).encode() if muatan is not None else None
    req = urllib.request.Request(alamat + jalur, data=data, headers=kepala)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=batas) as r:
            return r.status, r.read().decode("utf-8", "replace"), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), time.time() - t0
    except Exception as e:                      # noqa: BLE001
        return 0, str(e), time.time() - t0


# ── Jalur normal ────────────────────────────────────────────────────────
def uji_kesehatan(a: str) -> dict:
    kode, badan, dtk = panggil(a, "/api/kesehatan")
    if kode != 200:
        catat("GAGAL", "kesehatan menjawab", f"HTTP {kode}")
        return {}
    d = json.loads(badan)
    catat("LULUS", "kesehatan menjawab", f"{dtk:.1f}s")
    for kunci in ("status", "versi", "aoi", "database", "jumlah_ruas",
                  "sumber_data", "prediksi_mulai_utc", "prediksi_selesai_utc"):
        if kunci not in d:
            catat("GAGAL", f"kesehatan memuat '{kunci}'")
    if not isinstance(d.get("sumber_data"), list):
        catat("GAGAL", "sumber_data berupa list",
              f"malah {type(d.get('sumber_data')).__name__} — bug lencana kembali")
    else:
        catat("LULUS", "sumber_data berupa list")
    if d.get("jumlah_ruas", 0) < 19000:
        catat("GAGAL", "jumlah ruas wajar", str(d.get("jumlah_ruas")))
    else:
        catat("LULUS", "jumlah ruas wajar", f"{d['jumlah_ruas']:,}".replace(",", "."))
    return d


def uji_jam(a: str) -> list:
    kode, badan, dtk = panggil(a, "/api/jam")
    if kode != 200:
        catat("GAGAL", "jam menjawab", f"HTTP {kode}")
        return []
    jam = json.loads(badan).get("jam", [])
    catat("LULUS", "jam menjawab", f"{len(jam)} jam, {dtk:.1f}s")
    if len(jam) != 72:
        catat("CATAT", "jendela 72 jam", f"malah {len(jam)}")
    kunci = {"waktu_utc", "ruas_tergenang", "kedalaman_maks_cm", "tinggi_pasut_m"}
    if jam and not kunci.issubset(jam[0]):
        catat("GAGAL", "bentuk baris jam", f"kurang {kunci - set(jam[0])}")
    else:
        catat("LULUS", "bentuk baris jam")
    if jam and all(x["ruas_tergenang"] == 0 for x in jam):
        catat("GAGAL", "ada jam tergenang di jendela",
              "seluruh 72 jam kering — Pita Pasut akan tampak kosong")
    else:
        catat("LULUS", "ada jam tergenang di jendela",
              f"maks {max(x['ruas_tergenang'] for x in jam)} ruas")
    naik = [x["tinggi_pasut_m"] for x in jam]
    if len(set(naik)) < 10:
        catat("GAGAL", "pasut bervariasi", "nilainya nyaris tetap")
    else:
        catat("LULUS", "pasut bervariasi", f"{min(naik):+.2f} .. {max(naik):+.2f} m")
    return jam


def uji_ruas_dan_genangan(a: str, waktu: str) -> None:
    q = urllib.parse.quote(waktu)
    kode, badan, dtk = panggil(a, f"/api/ruas?waktu={q}")
    if kode != 200:
        catat("GAGAL", "ruas menjawab", f"HTTP {kode}")
        return
    d = json.loads(badan)
    n = len(d.get("features", []))
    mb = len(badan) / 1048576
    catat("LULUS", "ruas menjawab", f"{n} fitur, {mb:.1f} MB, {dtk:.1f}s")
    if mb > 8:
        catat("CATAT", "ukuran muatan ruas",
              f"{mb:.1f} MB berat untuk jaringan seluler")
    f = d["features"][0] if n else {}
    if f and "osm_u" not in json.dumps(f):
        catat("CATAT", "ruas membawa simpul graf", "periksa bila perutean aneh")

    kode, badan, dtk = panggil(a, f"/api/genangan?waktu={q}")
    if kode != 200:
        catat("GAGAL", "genangan menjawab", f"HTTP {kode}")
        return
    g = json.loads(badan)
    catat("LULUS", "genangan menjawab",
          f"{g.get('jumlah_tergenang')} tergenang, {dtk:.1f}s")
    if len(g.get("features", [])) != g.get("jumlah_tergenang"):
        catat("GAGAL", "jumlah genangan konsisten dengan fitur")
    else:
        catat("LULUS", "jumlah genangan konsisten dengan fitur")


def uji_tujuan(a: str) -> list:
    kode, badan, _ = panggil(a, "/api/tujuan-cepat")
    if kode != 200:
        catat("GAGAL", "tujuan-cepat menjawab", f"HTTP {kode}")
        return []
    t = json.loads(badan).get("tujuan", [])
    if len(t) < 2:
        catat("GAGAL", "tujuan cepat terisi", f"hanya {len(t)}")
    else:
        catat("LULUS", "tujuan cepat terisi", f"{len(t)} titik")
    for x in t:
        if not {"kunci", "label", "lon", "lat"}.issubset(x):
            catat("GAGAL", "bentuk tujuan cepat")
            break
    else:
        catat("LULUS", "bentuk tujuan cepat")
    return t


def uji_validasi(a: str) -> None:
    kode, badan, _ = panggil(a, "/api/validasi")
    if kode != 200:
        catat("GAGAL", "validasi menjawab", f"HTTP {kode}")
        return
    d = json.loads(badan)
    catat("LULUS", "validasi menjawab")
    # Aturan repo nomor 1: metrik yang belum ada dikembalikan null, tidak dikarang.
    if d.get("tersedia") and d.get("roc_auc") is None:
        catat("GAGAL", "metrik terisi saat tersedia")
    elif d.get("tersedia"):
        catat("LULUS", "metrik model apa adanya", f"ROC-AUC {d['roc_auc']}")
    if d.get("tersedia") and not d.get("alasan_ditolak"):
        catat("CATAT", "alasan penolakan tercantum", "kosong")


# ── Perutean: normal dan tepi ───────────────────────────────────────────
def uji_rute(a: str, tujuan: list, waktu: str) -> None:
    if len(tujuan) < 2:
        catat("CATAT", "perutean dilewati", "tujuan cepat kurang")
        return
    p1, p2 = tujuan[0], tujuan[1]
    A, B = [p1["lon"], p1["lat"]], [p2["lon"], p2["lat"]]

    for moda in ("motor", "mobil"):
        kode, badan, dtk = panggil(
            a, "/api/rute", {"asal": A, "tujuan": B, "moda": moda, "waktu": waktu})
        if kode != 200:
            catat("GAGAL", f"rute {moda}", f"HTTP {kode}: {badan[:90]}")
            continue
        d = json.loads(badan)
        catat("LULUS", f"rute {moda}", f"{dtk:.1f}s")
        sd = d.get("sumber_data")
        if not isinstance(sd, list):
            catat("GAGAL", f"rute {moda}: sumber_data list",
                  f"malah {type(sd).__name__} — LENCANA AKAN HILANG")
        else:
            catat("LULUS", f"rute {moda}: sumber_data list")
        if not d.get("rute", {}).get("features"):
            catat("GAGAL", f"rute {moda} menghasilkan geometri")
        else:
            catat("LULUS", f"rute {moda} menghasilkan geometri",
                  f"{len(d['rute']['features'])} jalur")
        if "selisih" not in d:
            catat("GAGAL", f"rute {moda} membawa selisih")

    # Asal sama dengan tujuan.
    kode, badan, _ = panggil(a, "/api/rute",
                             {"asal": A, "tujuan": A, "moda": "motor", "waktu": waktu})
    if kode in (200, 400, 422):
        catat("LULUS", "asal sama dengan tujuan ditangani", f"HTTP {kode}")
    else:
        catat("GAGAL", "asal sama dengan tujuan ditangani", f"HTTP {kode}")

    # Titik jauh di luar AOI.
    kode, badan, _ = panggil(a, "/api/rute",
                             {"asal": [106.8, -6.2], "tujuan": B,
                              "moda": "motor", "waktu": waktu})
    if kode == 200:
        catat("CATAT", "titik di luar AOI", "dijawab 200, dipatok ke simpul terdekat")
    elif kode in (400, 404, 422):
        catat("LULUS", "titik di luar AOI ditolak rapi", f"HTTP {kode}")
    else:
        catat("GAGAL", "titik di luar AOI", f"HTTP {kode}")

    # Masukan cacat.
    for nama, muatan in (
        ("moda tidak dikenal", {"asal": A, "tujuan": B, "moda": "pesawat", "waktu": waktu}),
        ("koordinat kurang", {"asal": [110.4], "tujuan": B, "moda": "motor"}),
        ("koordinat bukan angka", {"asal": ["x", "y"], "tujuan": B, "moda": "motor"}),
        ("bidang wajib hilang", {"asal": A}),
        ("waktu ngawur", {"asal": A, "tujuan": B, "moda": "motor", "waktu": "kemarin"}),
        ("lintang mustahil", {"asal": [110.4, -999], "tujuan": B, "moda": "motor"}),
    ):
        kode, badan, _ = panggil(a, "/api/rute", muatan)
        if kode in (400, 422):
            catat("LULUS", f"tolak {nama}", f"HTTP {kode}")
        elif kode == 500:
            catat("GAGAL", f"tolak {nama}", "HTTP 500 — galat tak tertangani")
        else:
            catat("CATAT", f"tolak {nama}", f"HTTP {kode}")


# ── Parameter dan galat pada endpoint baca ──────────────────────────────
def uji_parameter(a: str) -> None:
    for jalur, nama in (("/api/genangan?waktu=bukan-tanggal", "genangan waktu ngawur"),
                        ("/api/ruas?waktu=2099-01-01T00:00:00Z", "ruas waktu di luar jendela"),
                        ("/api/genangan?waktu=2099-01-01T00:00:00Z", "genangan di luar jendela")):
        kode, badan, _ = panggil(a, jalur)
        if kode == 500:
            catat("GAGAL", nama, "HTTP 500 — galat tak tertangani")
        elif kode in (200, 400, 404, 422):
            n = ""
            if kode == 200:
                try:
                    n = f"{len(json.loads(badan).get('features', []))} fitur"
                except Exception:                     # noqa: BLE001
                    pass
            catat("LULUS", nama, f"HTTP {kode} {n}".strip())
        else:
            catat("CATAT", nama, f"HTTP {kode}")

    kode, _, _ = panggil(a, "/api/tidak-ada")
    catat("LULUS" if kode == 404 else "GAGAL", "jalur tak dikenal 404", f"HTTP {kode}")


def uji_cors(a: str) -> None:
    kode, _, _ = panggil(a, "/api/kesehatan", asal=ASAL)
    catat("LULUS" if kode == 200 else "GAGAL", "CORS meloloskan asal resmi")
    req = urllib.request.Request(a + "/api/kesehatan",
                                 headers={"Origin": "https://jahat.example"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            izin = r.headers.get("access-control-allow-origin")
        if izin in (None, ""):
            catat("LULUS", "CORS menolak asal asing")
        elif izin == "*":
            catat("GAGAL", "CORS menolak asal asing", "malah membuka untuk semua")
        else:
            catat("LULUS", "CORS menolak asal asing", f"balas {izin}")
    except Exception as e:                            # noqa: BLE001
        catat("CATAT", "CORS asal asing", str(e)[:60])


def uji_beban(a: str) -> None:
    """Enam permintaan serentak. Kolam koneksi maksimum lima."""
    def sekali(_):
        return panggil(a, "/api/jam")[0]
    with ThreadPoolExecutor(max_workers=6) as ex:
        kode = list(ex.map(sekali, range(6)))
    if all(k == 200 for k in kode):
        catat("LULUS", "enam permintaan serentak", "semua 200")
    else:
        catat("GAGAL", "enam permintaan serentak", f"kode {kode}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--alamat", default=BAKU)
    a = p.parse_args().alamat.rstrip("/")

    print(f"UJI MENYELURUH — {a}\n")
    print("Kesehatan dan sumbu waktu")
    sehat = uji_kesehatan(a)
    jam = uji_jam(a)
    waktu = max(jam, key=lambda x: x["ruas_tergenang"])["waktu_utc"] if jam else None

    if waktu:
        print("\nLapisan peta")
        uji_ruas_dan_genangan(a, waktu)

    print("\nTujuan cepat dan validasi")
    tujuan = uji_tujuan(a)
    uji_validasi(a)

    if waktu:
        print("\nPerutean")
        uji_rute(a, tujuan, waktu)

    print("\nParameter dan galat")
    uji_parameter(a)

    print("\nCORS")
    uji_cors(a)

    print("\nBeban")
    uji_beban(a)

    lulus = sum(1 for s, _, _ in hasil if s == "LULUS")
    gagal = [x for x in hasil if x[0] == "GAGAL"]
    catatan = [x for x in hasil if x[0] == "CATAT"]
    print("\n" + "=" * 64)
    print(f"LULUS {lulus}   GAGAL {len(gagal)}   CATAT {len(catatan)}")
    if gagal:
        print("\nYANG GAGAL:")
        for _, nama, ket in gagal:
            print(f"  - {nama}" + (f" — {ket}" if ket else ""))
    if catatan:
        print("\nYANG PERLU DIKETAHUI:")
        for _, nama, ket in catatan:
            print(f"  - {nama}" + (f" — {ket}" if ket else ""))
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
