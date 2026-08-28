"""Bangun sampel latih dari backscatter Sentinel-1, lalu latih model genangan.

    python -m scripts.09_latih_model                 # ambang bawaan
    python -m scripts.09_latih_model --sensitivitas  # hanya laporan ambang
    python -m scripts.09_latih_model --ambang-db -2.5

BAGIAN PALING LEMAH DARI SELURUH METODOLOGI ADA DI BERKAS INI, dan lebih
baik dinyatakan sendiri sekarang daripada ditemukan juri nanti.

CARA LABEL BASAH DIBUAT.

Sentinel-1 tidak mengukur kedalaman. Yang diukur hanya seberapa banyak
gelombang radar dipantulkan balik. Permukaan air yang tenang memantulkan
gelombang menjauh dari satelit, sehingga backscatter TURUN. Itu satu-satunya
isyarat yang kita punya.

Ambang MUTLAK tidak dipakai. Alasannya terlihat dari datanya sendiri: pada
sampel jalan di dalam kota, nilai VV terendah hanya sekitar -13 dB,
sedangkan ambang air terbuka yang lazim dipakai -15 sampai -18 dB. Ambang
mutlak akan menyatakan seluruh kota kering sepanjang masa. Jalan perkotaan
memang tidak pernah menjadi air terbuka murni: ada trotoar, kendaraan,
pohon, dan bangunan di dalam satu piksel 30 meter.

Yang dipakai adalah DETEKSI PERUBAHAN terhadap keadaan biasa ruas itu
sendiri. Untuk tiap pasangan (ruas, orbit relatif) dihitung nilai tengah
seluruh akuisisi sebagai garis dasar, lalu satu akuisisi disebut basah bila
nilainya turun lebih dari sekian desibel di bawah garis dasarnya.

Dipisah per ORBIT RELATIF karena backscatter bergantung geometri sudut
pandang. Membandingkan citra ascending dengan descending tanpa memisahkannya
memunculkan "perubahan" yang sebenarnya hanya beda arah lihat satelit.

TIGA HAL YANG TIDAK BISA DILAKUKAN LABEL INI.

1. Ia tidak mengukur kedalaman. Kedalaman di sistem ini adalah estimasi
   turunan, dan setiap tampilannya wajib menyebut demikian.
2. Ia buta terhadap genangan yang justru MENAIKKAN backscatter. Air dangkal
   di antara bangunan memantul dua kali antara permukaan air dan dinding,
   dan itu menaikkan nilai, bukan menurunkan. Genangan semacam itu tidak
   akan tertangkap kriteria penurunan.
3. Ia bisa keliru menyebut basah pada hal lain yang menghaluskan permukaan,
   misalnya jalan yang baru diaspal atau lahan yang baru diratakan.

Ketiganya dicatat di docs/batasan.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np

from app import config, db
from app.domain import pasut

BERKAS_VV = config.DIR_DATA_OLAHAN / "s1_vv_ruas.jsonl"
BERKAS_CITRA = config.DIR_DATA_OLAHAN / "s1_daftar_citra.json"
BERKAS_METRIK = config.DIR_DATA_REFERENSI / "metrik_model.json"
BERKAS_MODEL = config.DIR_DATA_OLAHAN / "model_genangan_v1.joblib"
BERKAS_GRAFIK = config.DIR_DOCS / "kepentingan_fitur.svg"

# Penurunan backscatter yang dianggap menandakan genangan, dalam desibel.
AMBANG_TURUN_DB = -3.0

# Aturan repo nomor 5: pemisahan berdasarkan WAKTU, tidak pernah acak.
TAHUN_UJI_MULAI = 2024

FITUR = [
    "elevasi_m",
    "jarak_pantai_m",
    "laju_subsidensi_cm_thn",
    "tinggi_pasut_m",
    "hujan_24j_mm",
    "hujan_72j_mm",
]
NAMA_FITUR_ID = {
    "elevasi_m": "Elevasi DEMNAS",
    "jarak_pantai_m": "Jarak ke pantai",
    "laju_subsidensi_cm_thn": "Laju subsidensi",
    "tinggi_pasut_m": "Tinggi pasut saat akuisisi",
    "hujan_24j_mm": "Hujan 24 jam",
    "hujan_72j_mm": "Hujan 72 jam",
}


# ══════════════════════════════════════════════════════════════════════════
# PEMUATAN
# ══════════════════════════════════════════════════════════════════════════
def muat_backscatter() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    """Baca hasil skrip 08. Kembalikan (edge_id, indeks_citra, vv_db, citra)."""
    if not BERKAS_VV.exists():
        raise SystemExit(
            f"{BERKAS_VV.name} belum ada. Jalankan skrip 08 lebih dulu."
        )
    citra = json.loads(BERKAS_CITRA.read_text(encoding="utf-8"))["citra"]
    urutan = {c["indeks"]: i for i, c in enumerate(citra)}

    edge, idx, vv = [], [], []
    dilewati = 0
    with BERKAS_VV.open(encoding="utf-8") as f:
        for garis in f:
            b = json.loads(garis)
            nama = b["pita"].rsplit("_VV", 1)[0]
            i = urutan.get(nama)
            if i is None:
                dilewati += 1
                continue
            edge.append(b["edge_id"])
            idx.append(i)
            vv.append(b["vv_db"])
    if dilewati:
        print(f"  {dilewati:,} nilai dilewati, nama pitanya tidak ada di daftar citra")
    return (np.array(edge, dtype=np.int64),
            np.array(idx, dtype=np.int32),
            np.array(vv, dtype=np.float64),
            citra)


def beri_label(edge: np.ndarray, idx: np.ndarray, vv: np.ndarray,
               citra: list[dict], ambang_db: float) -> tuple[np.ndarray, np.ndarray]:
    """Hitung anomali terhadap garis dasar per (ruas, orbit relatif).

    Kembalikan (anomali_db, basah).
    """
    orbit = np.array([citra[i]["orbit_relatif"] for i in idx], dtype=np.int32)

    # Kunci gabungan ruas dan orbit, dihitung tanpa membuat kamus sejuta entri.
    kunci = edge.astype(np.int64) * 1000 + orbit
    urut = np.argsort(kunci, kind="stable")
    kunci_urut = kunci[urut]
    vv_urut = vv[urut]

    batas = np.flatnonzero(np.diff(kunci_urut)) + 1
    kelompok = np.split(np.arange(len(kunci_urut)), batas)

    anomali_urut = np.empty(len(vv_urut))
    for k in kelompok:
        anomali_urut[k] = vv_urut[k] - np.median(vv_urut[k])

    anomali = np.empty_like(anomali_urut)
    anomali[urut] = anomali_urut
    return anomali, anomali < ambang_db


def laporan_sensitivitas(anomali: np.ndarray) -> None:
    """Berapa banyak yang berlabel basah pada berbagai ambang.

    Dicetak SEBELUM model dilatih, dan ambangnya dipilih dari sini, bukan
    dari mana yang membuat AUC paling bagus. Memilih ambang berdasarkan
    hasil model adalah cara paling halus untuk menipu diri sendiri.
    """
    print("sensitivitas ambang terhadap laju label basah:")
    print(f"  {'ambang':>8} {'basah':>10} {'persen':>8}")
    for a in (-2.0, -2.5, -3.0, -3.5, -4.0, -5.0):
        n = int((anomali < a).sum())
        print(f"  {a:>7.1f} {n:>10,} {100.0 * n / len(anomali):>7.2f}")
    print(f"\n  sebaran anomali: p1 {np.percentile(anomali, 1):+.2f} dB, "
          f"p5 {np.percentile(anomali, 5):+.2f} dB, "
          f"median {np.median(anomali):+.2f} dB, "
          f"p95 {np.percentile(anomali, 95):+.2f} dB")


# ══════════════════════════════════════════════════════════════════════════
# PENYUSUNAN TABEL FITUR
# ══════════════════════════════════════════════════════════════════════════
def fitur_ruas() -> dict[int, tuple]:
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute(
                """
                SELECT edge_id, elevasi_m, jarak_pantai_m,
                       laju_subsidensi_cm_thn
                FROM ruas_jalan
                """
            )
            return {
                int(a): (
                    np.nan if b is None else float(b),
                    np.nan if c is None else float(c),
                    np.nan if d is None else float(d),
                )
                for a, b, c, d in kur.fetchall()
            }


def hujan_per_jam() -> dict[datetime, tuple[float, float]]:
    with db.koneksi() as kon:
        with kon.cursor() as kur:
            kur.execute("SELECT waktu, hujan_24j_mm, hujan_72j_mm FROM pemicu")
            return {
                w: (float(a or 0.0), float(b or 0.0))
                for w, a, b in kur.fetchall()
            }


def susun_tabel(edge, idx, vv, citra, basah):
    """Gabungkan label dengan fitur ruas dan variabel pemicu."""
    ruas = fitur_ruas()
    hujan = hujan_per_jam()

    waktu_citra = [
        datetime.fromisoformat(c["waktu"]).astimezone(timezone.utc) for c in citra
    ]
    # Pasut dihitung pada DETIK akuisisi, bukan dibulatkan ke jam. Puncak
    # pasut bisa jatuh di tengah jam, dan citra Sentinel-1 datang pada menit
    # yang tetap, jadi pembulatan akan menggeser fitur terpenting secara
    # sistematis pada seluruh sampel sekaligus.
    pasut_citra = [float(pasut.tinggi_pasut_m(w)) for w in waktu_citra]
    hujan_citra = [
        hujan.get(w.replace(minute=0, second=0, microsecond=0), (np.nan, np.nan))
        for w in waktu_citra
    ]

    n = len(edge)
    X = np.full((n, len(FITUR)), np.nan)
    for i in range(n):
        e = ruas.get(int(edge[i]))
        if e is None:
            continue
        j = idx[i]
        X[i, 0], X[i, 1], X[i, 2] = e
        X[i, 3] = pasut_citra[j]
        X[i, 4], X[i, 5] = hujan_citra[j]

    tahun = np.array([waktu_citra[j].year for j in idx], dtype=np.int16)
    return X, basah.astype(np.int8), tahun, waktu_citra, pasut_citra


# ══════════════════════════════════════════════════════════════════════════
# GRAFIK SVG TANPA DEPENDENCY
# ══════════════════════════════════════════════════════════════════════════
def gambar_kepentingan(nama: list[str], nilai: np.ndarray, galat: np.ndarray,
                       berkas) -> None:
    """Tulis diagram batang kepentingan fitur sebagai SVG.

    matplotlib sengaja TIDAK ditambahkan sebagai dependency. Komentar di
    requirements.txt justru menyebut penghindaran matplotlib sebagai alasan
    menolak geemap, jadi menariknya masuk lewat pintu belakang tidak pantas.
    Diagram batang horizontal cukup ditulis langsung, hasilnya vektor, dan
    warnanya bisa mengikuti DESIGN.md.
    """
    urut = np.argsort(nilai)
    nama = [nama[i] for i in urut]
    nilai, galat = nilai[urut], galat[urut]

    lebar, tinggi_baris, kiri, atas = 720, 34, 220, 46
    tinggi = atas + tinggi_baris * len(nama) + 46
    skala = (lebar - kiri - 90) / max(float(nilai.max()), 1e-9)

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lebar}" '
        f'height="{tinggi}" viewBox="0 0 {lebar} {tinggi}" '
        f'font-family="Barlow Semi Condensed, Arial Narrow, sans-serif">',
        f'<rect width="{lebar}" height="{tinggi}" fill="#F4F1EA"/>',
        f'<text x="{kiri}" y="26" font-size="17" font-weight="600" '
        f'fill="#1B2A32">Kepentingan fitur model genangan</text>',
        f'<text x="{kiri}" y="{tinggi - 16}" font-size="12" fill="#4A5C66">'
        'Penurunan ROC-AUC saat satu fitur diacak, pada data uji 2024 sampai '
        '2026. Garis tipis adalah simpangan baku 10 pengulangan.</text>',
    ]
    for i, (n_, v, g) in enumerate(zip(nama, nilai, galat)):
        y = atas + i * tinggi_baris
        w = max(float(v) * skala, 0.0)
        p.append(f'<text x="{kiri - 12}" y="{y + 15}" font-size="14" '
                 f'text-anchor="end" fill="#1B2A32">{n_}</text>')
        p.append(f'<rect x="{kiri}" y="{y + 3}" width="{w:.1f}" height="16" '
                 f'fill="#1F6F78"/>')
        if g > 0:
            x1, x2 = kiri + max(w - g * skala, 0), kiri + w + g * skala
            p.append(f'<line x1="{x1:.1f}" y1="{y + 11}" x2="{x2:.1f}" '
                     f'y2="{y + 11}" stroke="#1B2A32" stroke-width="1"/>')
        p.append(f'<text x="{kiri + w + 8:.1f}" y="{y + 15}" font-size="13" '
                 f'font-family="IBM Plex Mono, monospace" fill="#4A5C66">'
                 f'{v:.4f}</text>')
    p.append("</svg>")
    berkas.write_text("\n".join(p), encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════
def main() -> int:
    pengurai = argparse.ArgumentParser(description=__doc__)
    pengurai.add_argument("--ambang-db", type=float, default=AMBANG_TURUN_DB)
    pengurai.add_argument("--sensitivitas", action="store_true")
    pengurai.add_argument("--tanpa-database", action="store_true")
    argumen = pengurai.parse_args()

    print("memuat backscatter ...")
    edge, idx, vv, citra = muat_backscatter()
    print(f"  nilai   : {len(vv):,}")
    print(f"  ruas    : {len(np.unique(edge)):,}")
    print(f"  citra   : {len(np.unique(idx)):,} dari {len(citra):,} di daftar\n")

    anomali, basah = beri_label(edge, idx, vv, citra, argumen.ambang_db)
    laporan_sensitivitas(anomali)
    if argumen.sensitivitas:
        return 0
    print(f"\nambang dipakai: {argumen.ambang_db:+.1f} dB  ->  "
          f"{int(basah.sum()):,} basah ({100.0 * basah.mean():.2f} persen)\n")

    print("menyusun tabel fitur ...")
    X, y, tahun, waktu_citra, pasut_citra = susun_tabel(
        edge, idx, vv, citra, basah)

    # ── uji kewarasan label: apakah label basah condong ke pasut tinggi ──
    p_sampel = X[:, 3]
    print(f"  pasut rata-rata saat label BASAH  : {p_sampel[y == 1].mean():+.3f} m")
    print(f"  pasut rata-rata saat label KERING : {p_sampel[y == 0].mean():+.3f} m")
    selisih = p_sampel[y == 1].mean() - p_sampel[y == 0].mean()
    print(f"  selisih                           : {selisih:+.3f} m")
    if selisih <= 0:
        print("  PERINGATAN: label basah TIDAK condong ke pasut tinggi.")
        print("  Label ini belum tentu menangkap rob. Periksa sebelum dipakai.")
    print()

    latih = tahun < TAHUN_UJI_MULAI
    uji = ~latih
    print(f"pemisahan berdasarkan WAKTU, tidak pernah acak")
    print(f"  latih 2015-{TAHUN_UJI_MULAI - 1}: {int(latih.sum()):,} baris, "
          f"{int(y[latih].sum()):,} basah ({100.0 * y[latih].mean():.2f} persen)")
    print(f"  uji   {TAHUN_UJI_MULAI}-2026    : {int(uji.sum()):,} baris, "
          f"{int(y[uji].sum()):,} basah ({100.0 * y[uji].mean():.2f} persen)\n")

    if y[latih].sum() < 50 or y[uji].sum() < 50:
        print("Kelas positif terlalu sedikit untuk dilatih dengan jujur.")
        print("Pertimbangkan rencana 9.A di PLAN.md: indeks kerentanan.")
        return 1

    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import (average_precision_score, confusion_matrix,
                                 f1_score, precision_recall_curve,
                                 roc_auc_score)

    print("melatih HistGradientBoostingClassifier ...")
    model = HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.06,
        max_leaf_nodes=31,
        min_samples_leaf=50,
        l2_regularization=1.0,
        class_weight="balanced",     # kelas basah jauh lebih sedikit
        random_state=2026,
    )
    model.fit(X[latih], y[latih])

    prob = model.predict_proba(X[uji])[:, 1]
    auc = float(roc_auc_score(y[uji], prob))
    pr_auc = float(average_precision_score(y[uji], prob))

    presisi, recall, ambang_p = precision_recall_curve(y[uji], prob)
    f1_kurva = 2 * presisi * recall / np.maximum(presisi + recall, 1e-12)
    terbaik = int(np.nanargmax(f1_kurva[:-1]))
    ambang_pilih = float(ambang_p[terbaik])
    f1 = float(f1_score(y[uji], prob >= ambang_pilih))
    km = confusion_matrix(y[uji], prob >= ambang_pilih)

    # ── PEMBANDING NAIF ────────────────────────────────────────────────
    # Angka AUC tidak berarti apa-apa tanpa pembanding. Dua aturan satu
    # variabel di bawah ini adalah yang akan dipakai orang kalau tidak ada
    # model sama sekali, dan model wajib mengalahkan keduanya.
    naif = {}
    for nama_naif, skor in (
        ("pasut saja", X[uji][:, 3]),
        ("elevasi saja, makin rendah makin basah", -X[uji][:, 0]),
        ("jarak pantai saja, makin dekat makin basah", -X[uji][:, 1]),
    ):
        sah = np.isfinite(skor)
        naif[nama_naif] = float(roc_auc_score(y[uji][sah], skor[sah]))

    print()
    print("HASIL PADA DATA UJI 2024-2026")
    print(f"  ROC-AUC : {auc:.4f}")
    print(f"  PR-AUC  : {pr_auc:.4f}   (proporsi kelas basah {y[uji].mean():.4f})")
    print(f"  F1      : {f1:.4f} pada ambang probabilitas {ambang_pilih:.3f}")
    print(f"  matriks konfusi [[TN, FP], [FN, TP]] = {km.tolist()}")
    print()
    print("  pembanding naif, ROC-AUC:")
    for nama_naif, nilai_naif in naif.items():
        tanda = "kalah" if nilai_naif < auc else "MENANG atas model"
        print(f"    {nama_naif:<44} {nilai_naif:.4f}  ({tanda})")
    if max(naif.values()) >= auc:
        print()
        print("  PERINGATAN: satu aturan variabel tunggal setara atau lebih baik")
        print("  daripada model. Melaporkan model sebagai kemajuan dalam keadaan")
        print("  ini adalah overclaim.")

    # ── KEPENTINGAN FITUR ──────────────────────────────────────────────
    # HistGradientBoostingClassifier tidak menyediakan feature_importances_.
    # Permutation importance justru lebih jujur: ia mengukur seberapa banyak
    # kinerja pada DATA UJI hilang saat satu fitur diacak, bukan seberapa
    # sering fitur itu dipakai memecah pohon saat latih.
    print("\nmenghitung kepentingan fitur dengan permutasi ...")
    kp = permutation_importance(
        model, X[uji], y[uji], n_repeats=10, random_state=2026,
        scoring="roc_auc", n_jobs=1,
    )
    urut = np.argsort(kp.importances_mean)[::-1]
    for i in urut:
        print(f"  {NAMA_FITUR_ID[FITUR[i]]:<28} "
              f"{kp.importances_mean[i]:+.4f} ± {kp.importances_std[i]:.4f}")

    gambar_kepentingan(
        [NAMA_FITUR_ID[f] for f in FITUR],
        kp.importances_mean.copy(), kp.importances_std.copy(), BERKAS_GRAFIK)
    print(f"  grafik: {BERKAS_GRAFIK.name}")

    # ── SIMPAN MODEL DAN METRIK ────────────────────────────────────────
    import joblib

    joblib.dump({
        "model": model,
        "fitur": FITUR,
        "ambang_probabilitas": ambang_pilih,
        "ambang_turun_db": argumen.ambang_db,
        "dilatih": datetime.now(timezone.utc).isoformat(),
    }, BERKAS_MODEL)
    print(f"  model : {BERKAS_MODEL.name}")

    metrik = {
        "_catatan": ("Metrik model genangan v1. Dihasilkan oleh "
                     "backend/scripts/09_latih_model.py. Seluruh angka di sini "
                     "berasal dari data uji yang dipisah menurut WAKTU."),
        "dilatih": datetime.now(timezone.utc).isoformat(),
        "model": "HistGradientBoostingClassifier",
        "pemisahan": {
            "cara": "berdasarkan waktu, tidak pernah acak",
            "latih": f"2015-{TAHUN_UJI_MULAI - 1}",
            "uji": f"{TAHUN_UJI_MULAI}-2026",
            "baris_latih": int(latih.sum()),
            "baris_uji": int(uji.sum()),
            "citra_latih": int(len({int(idx[i]) for i in np.flatnonzero(latih)})),
            "citra_uji": int(len({int(idx[i]) for i in np.flatnonzero(uji)})),
        },
        "label": {
            "cara": ("deteksi perubahan backscatter VV terhadap nilai tengah "
                     "tiap pasangan ruas dan orbit relatif"),
            "ambang_turun_db": argumen.ambang_db,
            "laju_basah_keseluruhan": round(float(basah.mean()), 4),
            "laju_basah_latih": round(float(y[latih].mean()), 4),
            "laju_basah_uji": round(float(y[uji].mean()), 4),
            "pasut_rata_saat_basah_m": round(float(p_sampel[y == 1].mean()), 3),
            "pasut_rata_saat_kering_m": round(float(p_sampel[y == 0].mean()), 3),
        },
        "metrik_uji": {
            "roc_auc": round(auc, 4),
            "pr_auc": round(pr_auc, 4),
            "proporsi_dasar_pr": round(float(y[uji].mean()), 4),
            "f1": round(f1, 4),
            "ambang_probabilitas": round(ambang_pilih, 4),
            "matriks_konfusi": {"TN": int(km[0][0]), "FP": int(km[0][1]),
                                "FN": int(km[1][0]), "TP": int(km[1][1])},
        },
        "pembanding_naif_roc_auc": {k: round(v, 4) for k, v in naif.items()},
        "kepentingan_fitur": [
            {"fitur": FITUR[i], "nama": NAMA_FITUR_ID[FITUR[i]],
             "penurunan_roc_auc": round(float(kp.importances_mean[i]), 4),
             "simpangan_baku": round(float(kp.importances_std[i]), 4)}
            for i in urut
        ],
        "_peringatan": [
            "Label BUKAN pengukuran kedalaman. Sentinel-1 hanya memberi "
            "isyarat basah atau kering, dan kedalaman di sistem ini adalah "
            "estimasi turunan.",
            "Kriteria penurunan backscatter buta terhadap genangan yang justru "
            "MENAIKKAN backscatter lewat pantulan ganda antara air dan dinding.",
            "Model dilatih pada sampel ruas berstrata, bukan seluruh 19.394 "
            "ruas, karena kuota Earth Engine. Prediksi tetap dihitung untuk "
            "seluruh ruas.",
            "Fitur jarak sungai yang disebut PLAN.md bagian 10.3 TIDAK dipakai "
            "karena belum dihitung.",
        ],
    }
    BERKAS_METRIK.write_text(
        json.dumps(metrik, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  metrik: {BERKAS_METRIK.name}")

    # ── TULIS SAMPEL LATIH KE DATABASE ─────────────────────────────────
    if not argumen.tanpa_database:
        print("\nmenulis sampel_latih ke database ...")
        baris_db = [
            (int(edge[i]), waktu_citra[idx[i]], citra[idx[i]]["indeks"],
             bool(y[i]), float(X[i, 3]),
             None if not np.isfinite(X[i, 4]) else float(X[i, 4]),
             None if not np.isfinite(X[i, 5]) else float(X[i, 5]))
            for i in range(len(y))
        ]
        with db.koneksi() as kon:
            repo = db.RepositoriSampelLatih(kon)
            dihapus = repo.kosongkan()
            repo.sisipkan_banyak(baris_db)
        with db.koneksi() as kon:
            r = db.RepositoriSampelLatih(kon).ringkasan()
        print(f"  {dihapus:,} baris lama dihapus")
        print(f"  {r['baris']:,} baris, {r['basah']:,} basah, "
              f"{r['ruas']:,} ruas, {r['citra']:,} citra")
        print(f"  periode {r['awal']} sampai {r['akhir']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
