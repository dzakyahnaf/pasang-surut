"""Hitung ulang potret lokal dari indeks tersimpan; tidak menulis database.

    python -m scripts.27_potret_dari_indeks --bawah NILAI --puncak NILAI

Acuan pasut harus berasal dari pipeline yang didokumentasikan. Setiap jam,
termasuk jam kering, benar-benar dihitung sebelum metadata diterbitkan.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import numpy as np
from app import config
from app.domain import pasut, genangan


def hitung(d, indeks, bawah, puncak):
    if not np.isfinite([bawah, puncak]).all() or puncak <= bawah:
        raise ValueError("Acuan pasut tidak sah")
    edge = [int(f["properties"]["edge_id"]) for f in d["ruas"]["features"]]
    if not edge or any(str(e) not in indeks for e in edge):
        raise ValueError("Indeks harus tersedia untuk seluruh ruas potret")
    skor = np.array([indeks[str(e)] for e in edge])
    if not np.isfinite(skor).all() or np.any((skor < 0) | (skor > 1)):
        raise ValueError("Nilai indeks tidak sah")
    jam = [datetime.fromisoformat(j["waktu_utc"]) for j in d["jam"]]
    if not jam or any(b-a != timedelta(hours=1) for a,b in zip(jam,jam[1:])):
        raise ValueError("Jam potret tidak berurutan")
    per_jam, ringkas = {}, []
    for w in jam:
        tinggi = float(pasut.tinggi_pasut_m(w))
        proporsi = 0.10 * float(np.clip((tinggi-bawah)/(puncak-bawah), 0, 1))
        nilai = {}
        if proporsi > 0:
            potong = float(np.quantile(skor, 1-proporsi))
            kedalaman = genangan.kedalaman_cm(skor, tinggi, potong, bawah, puncak)
            nilai = {str(edge[i]): [round(float(kedalaman[i]), 1), round(float(skor[i]), 4)]
                     for i in np.flatnonzero(kedalaman > 0)}
        per_jam[w.isoformat()] = nilai
        ringkas.append({"waktu_utc": w.isoformat(), "tinggi_pasut_m": round(tinggi, 4),
                        "ruas_tergenang": sum(v[0] > 0 for v in nilai.values()),
                        "kedalaman_maks_cm": max((v[0] for v in nilai.values()), default=0.0)})
    d.update({"dibuat": datetime.now(timezone.utc).isoformat(),
        "berlaku_sampai": (jam[-1]+timedelta(hours=1)).isoformat(),
        "sumber_data": ["kerentanan_v1"], "jam": ringkas, "genangan": per_jam,
        "cakupan": {"versi": str(uuid4()), "jam_lengkap": [w.isoformat() for w in jam]},
        "rekonstruksi_potret": {"indeks": "indeks_kerentanan.json (presisi tersimpan)",
                                "acuan_bawah": bawah, "acuan_puncak": puncak,
                                "proporsi_puncak_asumsi": 0.10}})
    return d


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--bawah", type=float, required=True)
    arg.add_argument("--puncak", type=float, required=True)
    args = arg.parse_args()
    path = config.DIR_DATA_OLAHAN / "potret_demo.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    indeks = json.loads((config.DIR_DATA_OLAHAN / "indeks_kerentanan.json").read_text(encoding="utf-8"))["indeks"]
    d = hitung(d, indeks, args.bawah, args.puncak)
    sementara = path.with_suffix(".tmp")
    sementara.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    sementara.replace(path)
    print(f"Potret dihitung: {len(d['jam'])} jam lengkap; akhir {d['berlaku_sampai']}")


if __name__ == "__main__":
    main()
