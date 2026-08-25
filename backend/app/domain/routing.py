"""Perutean sadar genangan — Dijkstra yang sadar waktu.

INTI YANG MEMBEDAKAN MODUL INI DARI ROUTING BIASA.

Routing biasa menghitung bobot sekali di awal lalu mencari lintasan
termurah. Itu salah untuk rob. Genangan berubah tiap jam, dan sebuah ruas
yang kering saat pengguna berangkat bisa sudah terendam ketika ia benar-benar
sampai di sana empat puluh menit kemudian.

Karena itu bobot tiap ruas di sini dihitung pada **perkiraan waktu tiba di
ruas itu**, bukan pada waktu berangkat. Dijkstra tetap sah dipakai selama
fungsi waktu tempuhnya tidak pernah membuat orang tiba lebih awal dengan
berangkat lebih lambat, dan pada rentang 72 jam dengan resolusi satu jam
syarat itu terpenuhi.

Dua rute dihitung untuk setiap permintaan:

    rute_abai_rob   Mengabaikan genangan sepenuhnya. Ini rute yang akan
                    diberikan aplikasi peta biasa. Fungsinya sebagai
                    pembanding, bukan sebagai saran.
    rute_sadar_rob  Menghindari genangan sesuai ambang moda.

Selisih keduanya adalah satu-satunya pijakan yang sah untuk angka dampak di
M5. Tanpa pembanding, klaim "menghemat sekian menit" tidak punya dasar.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# PENALTI GENANGAN
# ══════════════════════════════════════════════════════════════════════════
# Pengali waktu tempuh pada tiap ambang. ANGKA INI ASUMSI, bukan hasil
# pengukuran lapangan, dan wajib disebut demikian di docs/batasan.md.
#
# Bentuknya sengaja sederhana dan monoton supaya bisa dijelaskan ke juri
# dalam satu kalimat: di bawah ambang lambat kendaraan berjalan normal, lalu
# melambat makin dalam air, dan berhenti sama sekali di ambang tidak bisa
# lewat.
#
#   kedalaman <= lambat_cm            -> 1,0  (tidak melambat)
#   lambat_cm .. berisiko_cm          -> 1,0 sampai 2,5
#   berisiko_cm .. tidak_bisa_lewat   -> 2,5 sampai 8,0
#   >= tidak_bisa_lewat_cm            -> ruas dibuang dari graf
PENALTI_DI_AMBANG_LAMBAT = 1.0
PENALTI_DI_AMBANG_BERISIKO = 2.5
PENALTI_MENJELANG_TIDAK_BISA_LEWAT = 8.0

# Kecepatan cadangan bila data kecepatan hilang. Sama dengan bawaan kolom
# kecepatan_kmh di schema.sql.
KECEPATAN_CADANGAN_KMH = 30.0

# Batas jarak antara titik yang diketuk pengguna dan simpul jalan terdekat.
# Lebih jauh dari ini berarti pengguna mengetuk laut, sawah, atau wilayah
# di luar AOI, dan itu galat yang perlu dijelaskan, bukan ditebak.
JARAK_MAKS_KE_JALAN_M = 500.0


def penalti_genangan(kedalaman_cm: float, ambang: dict) -> float:
    """Pengali waktu tempuh akibat genangan. Mengembalikan inf bila tak terlewati.

    `ambang` adalah satu baris dari tabel ambang_moda. Angkanya TIDAK PERNAH
    ditulis tetap di dalam kode ini — kalau tim mengoreksi ambang di
    database, mesin routing langsung ikut berubah tanpa perlu deploy ulang.
    """
    if kedalaman_cm <= 0:
        return 1.0

    lambat = ambang["lambat_cm"]
    berisiko = ambang["berisiko_cm"]
    mentok = ambang["tidak_bisa_lewat_cm"]

    if kedalaman_cm >= mentok:
        return math.inf
    if kedalaman_cm <= lambat:
        return PENALTI_DI_AMBANG_LAMBAT

    if kedalaman_cm <= berisiko:
        bagian = (kedalaman_cm - lambat) / max(berisiko - lambat, 1e-9)
        return PENALTI_DI_AMBANG_LAMBAT + bagian * (
            PENALTI_DI_AMBANG_BERISIKO - PENALTI_DI_AMBANG_LAMBAT
        )

    bagian = (kedalaman_cm - berisiko) / max(mentok - berisiko, 1e-9)
    return PENALTI_DI_AMBANG_BERISIKO + bagian * (
        PENALTI_MENJELANG_TIDAK_BISA_LEWAT - PENALTI_DI_AMBANG_BERISIKO
    )


# ══════════════════════════════════════════════════════════════════════════
# GRAF
# ══════════════════════════════════════════════════════════════════════════
@dataclass
class Sisi:
    """Satu ruas jalan sebagai sisi berarah pada graf."""
    edge_id: int
    dari: int
    ke: int
    nama: str | None
    panjang_m: float
    kecepatan_kmh: float
    koordinat: list           # [[bujur, lintang], ...] searah dari -> ke
    detik_dasar: float = field(init=False)

    def __post_init__(self) -> None:
        kecepatan = self.kecepatan_kmh or KECEPATAN_CADANGAN_KMH
        # km/jam menjadi meter/detik: bagi 3,6.
        self.detik_dasar = self.panjang_m / (kecepatan / 3.6)


class GrafJalan:
    """Graf jalan berarah, dibangun dari baris tabel ruas_jalan.

    Dibangun sekali lalu disimpan di memori. Membangunnya ulang tiap
    permintaan berarti membaca 19 ribu baris dari database setiap kali
    pengguna menggeser Pita Pasut.
    """

    def __init__(self, ruas: list[dict]) -> None:
        self.keluar: dict[int, list[Sisi]] = {}
        self.sisi_per_id: dict[int, Sisi] = {}
        koordinat_simpul: dict[int, tuple[float, float]] = {}

        for r in ruas:
            u, v = r["osm_u"], r["osm_v"]

            # Gelang, yaitu ruas yang berawal dan berakhir di simpul yang
            # sama. Ada 12 di AOI ini, umumnya bundaran kecil hasil
            # penyederhanaan OSMnx. Tidak berguna untuk routing dan hanya
            # menambah beban, jadi dilewati.
            if u == v:
                continue

            koordinat = r["koordinat"]
            if len(koordinat) < 2:
                continue
            koordinat_simpul.setdefault(u, tuple(koordinat[0]))
            koordinat_simpul.setdefault(v, tuple(koordinat[-1]))

            maju = Sisi(
                edge_id=r["edge_id"], dari=u, ke=v, nama=r.get("nama"),
                panjang_m=r["panjang_m"], kecepatan_kmh=r["kecepatan_kmh"],
                koordinat=koordinat,
            )
            self.keluar.setdefault(u, []).append(maju)
            self.sisi_per_id[r["edge_id"]] = maju

            if not r["satu_arah"]:
                # Ruas dua arah disimpan satu baris di database, jadi arah
                # baliknya dibuat di sini dengan geometri yang dibalik.
                # Keduanya memakai edge_id yang sama, karena prediksi
                # genangan memang berlaku untuk aspal yang sama.
                balik = Sisi(
                    edge_id=r["edge_id"], dari=v, ke=u, nama=r.get("nama"),
                    panjang_m=r["panjang_m"], kecepatan_kmh=r["kecepatan_kmh"],
                    koordinat=list(reversed(koordinat)),
                )
                self.keluar.setdefault(v, []).append(balik)

        self.simpul = list(koordinat_simpul.keys())
        self._koordinat = np.array(
            [koordinat_simpul[n] for n in self.simpul], dtype=np.float64
        )
        self._id_simpul = np.array(self.simpul, dtype=np.int64)

    @property
    def jumlah_simpul(self) -> int:
        return len(self.simpul)

    @property
    def jumlah_sisi(self) -> int:
        return sum(len(v) for v in self.keluar.values())

    def simpul_terdekat(self, bujur: float, lintang: float) -> tuple[int, float]:
        """Cari simpul jalan terdekat dari satu titik, beserta jaraknya (meter).

        KENAPA TIDAK MENGHITUNG JARAK LANGSUNG DI DERAJAT. Satu derajat bujur
        dan satu derajat lintang tidak sama panjang, jadi selisih koordinat
        mentah bukan jarak. Di sini dipakai pendekatan bidang datar lokal:
        selisih lintang dikali panjang satu derajat lintang, selisih bujur
        dikali panjang satu derajat bujur PADA lintang tersebut, yaitu
        dikoreksi dengan kosinus lintang.

        Pendekatan ini cukup karena AOI hanya selebar belasan kilometer.
        Untuk jarak yang benar-benar dipakai sebagai angka hasil, panjang
        ruas sudah dihitung di EPSG:32749 saat data dimasukkan.
        """
        METER_PER_DERAJAT_LINTANG = 110_574.0
        METER_PER_DERAJAT_BUJUR = 111_320.0 * math.cos(math.radians(lintang))

        d_bujur = (self._koordinat[:, 0] - bujur) * METER_PER_DERAJAT_BUJUR
        d_lintang = (self._koordinat[:, 1] - lintang) * METER_PER_DERAJAT_LINTANG
        jarak = np.hypot(d_bujur, d_lintang)

        i = int(np.argmin(jarak))
        return int(self._id_simpul[i]), float(jarak[i])


# ══════════════════════════════════════════════════════════════════════════
# HASIL
# ══════════════════════════════════════════════════════════════════════════
@dataclass
class HasilRute:
    ditemukan: bool
    alasan: str | None = None
    edge_ids: list[int] = field(default_factory=list)
    koordinat: list = field(default_factory=list)
    detik: float = 0.0
    jarak_m: float = 0.0
    waktu_tiba: datetime | None = None
    ruas_tergenang: int = 0
    kedalaman_maks_cm: float = 0.0
    nama_jalan: list[str] = field(default_factory=list)


def _jam_bulat(waktu: datetime) -> datetime:
    if waktu.tzinfo is None:
        waktu = waktu.replace(tzinfo=timezone.utc)
    return waktu.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def _kedalaman_pada(peta_kedalaman: dict, waktu: datetime, edge_id: int) -> float:
    """Kedalaman satu ruas pada satu waktu. Ruas tanpa baris berarti kering."""
    per_jam = peta_kedalaman.get(_jam_bulat(waktu))
    if not per_jam:
        return 0.0
    nilai = per_jam.get(edge_id)
    return nilai[0] if nilai else 0.0


def cari_rute(
    graf: GrafJalan,
    simpul_asal: int,
    simpul_tujuan: int,
    waktu_berangkat: datetime,
    ambang: dict,
    peta_kedalaman: dict,
    sadar_rob: bool = True,
) -> HasilRute:
    """Dijkstra sadar waktu dari simpul asal ke simpul tujuan.

    Jarak yang dilonggarkan adalah WAKTU TEMPUH DALAM DETIK sejak berangkat,
    bukan meter. Itu yang membuat waktu tiba di tiap simpul diketahui
    sepanjang penelusuran, dan karena itu kedalaman genangan bisa dibaca
    pada jam yang benar.

    Bila sadar_rob bernilai False, genangan diabaikan sepenuhnya dan
    hasilnya adalah rute terpendek biasa. Itulah pembanding yang dipakai
    untuk menghitung dampak.
    """
    if simpul_asal == simpul_tujuan:
        return HasilRute(
            ditemukan=True,
            edge_ids=[],
            koordinat=[],
            detik=0.0,
            jarak_m=0.0,
            waktu_tiba=waktu_berangkat,
        )

    # detik_terbaik[simpul] = waktu tempuh terkecil yang diketahui menuju simpul
    detik_terbaik: dict[int, float] = {simpul_asal: 0.0}
    asal_sisi: dict[int, Sisi] = {}
    selesai: set[int] = set()

    antrean: list[tuple[float, int]] = [(0.0, simpul_asal)]

    while antrean:
        detik_kini, simpul = heapq.heappop(antrean)
        if simpul in selesai:
            continue
        selesai.add(simpul)

        if simpul == simpul_tujuan:
            break

        # Inilah bagian yang membuatnya sadar waktu: jam yang dipakai untuk
        # membaca genangan adalah jam saat pengguna diperkirakan TIBA di
        # simpul ini, bukan jam ia berangkat dari rumah.
        waktu_di_simpul = waktu_berangkat + timedelta(seconds=detik_kini)

        for sisi in graf.keluar.get(simpul, ()):
            if sisi.ke in selesai:
                continue

            if sadar_rob:
                kedalaman = _kedalaman_pada(
                    peta_kedalaman, waktu_di_simpul, sisi.edge_id
                )
                pengali = penalti_genangan(kedalaman, ambang)
                if not math.isfinite(pengali):
                    # Kedalaman di atas ambang tidak bisa lewat. Ruas ini
                    # dibuang dari graf untuk moda ini, pada jam ini.
                    continue
            else:
                pengali = 1.0

            calon = detik_kini + sisi.detik_dasar * pengali
            if calon < detik_terbaik.get(sisi.ke, math.inf):
                detik_terbaik[sisi.ke] = calon
                asal_sisi[sisi.ke] = sisi
                heapq.heappush(antrean, (calon, sisi.ke))

    if simpul_tujuan not in detik_terbaik:
        return HasilRute(
            ditemukan=False,
            alasan=(
                "tidak_terhubung" if not sadar_rob
                else "seluruh_jalur_tergenang"
            ),
        )

    # Runut balik dari tujuan ke asal.
    jalur: list[Sisi] = []
    simpul = simpul_tujuan
    while simpul != simpul_asal:
        sisi = asal_sisi[simpul]
        jalur.append(sisi)
        simpul = sisi.dari
    jalur.reverse()

    # Susun geometri, dan hitung ulang genangan di sepanjang jalur pada
    # waktu tiba yang sebenarnya, untuk dilaporkan ke pengguna.
    koordinat: list = []
    nama_jalan: list[str] = []
    tergenang = 0
    kedalaman_maks = 0.0
    berjalan = 0.0

    for sisi in jalur:
        titik = sisi.koordinat
        if koordinat and titik and koordinat[-1] == titik[0]:
            koordinat.extend(titik[1:])
        else:
            koordinat.extend(titik)

        waktu_tiba_di_sisi = waktu_berangkat + timedelta(seconds=berjalan)
        kedalaman = _kedalaman_pada(
            peta_kedalaman, waktu_tiba_di_sisi, sisi.edge_id
        )
        if kedalaman > 0:
            tergenang += 1
            kedalaman_maks = max(kedalaman_maks, kedalaman)

        pengali = penalti_genangan(kedalaman, ambang) if sadar_rob else 1.0
        if not math.isfinite(pengali):
            pengali = PENALTI_MENJELANG_TIDAK_BISA_LEWAT
        berjalan += sisi.detik_dasar * pengali

        if sisi.nama and (not nama_jalan or nama_jalan[-1] != sisi.nama):
            nama_jalan.append(sisi.nama)

    return HasilRute(
        ditemukan=True,
        edge_ids=[s.edge_id for s in jalur],
        koordinat=koordinat,
        detik=detik_terbaik[simpul_tujuan],
        jarak_m=sum(s.panjang_m for s in jalur),
        waktu_tiba=waktu_berangkat + timedelta(seconds=detik_terbaik[simpul_tujuan]),
        ruas_tergenang=tergenang,
        kedalaman_maks_cm=kedalaman_maks,
        nama_jalan=nama_jalan,
    )


def dua_rute(
    graf: GrafJalan,
    asal: tuple[float, float],
    tujuan: tuple[float, float],
    waktu_berangkat: datetime,
    ambang: dict,
    peta_kedalaman: dict,
) -> dict:
    """Hitung rute pembanding dan rute sadar rob sekaligus.

    Keduanya berangkat dari simpul yang sama pada jam yang sama, sehingga
    selisihnya benar-benar disebabkan oleh genangan dan bukan oleh titik
    awal yang berbeda.
    """
    simpul_asal, jarak_asal = graf.simpul_terdekat(*asal)
    simpul_tujuan, jarak_tujuan = graf.simpul_terdekat(*tujuan)

    if jarak_asal > JARAK_MAKS_KE_JALAN_M:
        return {"galat": "asal_jauh_dari_jalan", "jarak_m": jarak_asal}
    if jarak_tujuan > JARAK_MAKS_KE_JALAN_M:
        return {"galat": "tujuan_jauh_dari_jalan", "jarak_m": jarak_tujuan}

    abai = cari_rute(
        graf, simpul_asal, simpul_tujuan, waktu_berangkat,
        ambang, peta_kedalaman, sadar_rob=False,
    )
    sadar = cari_rute(
        graf, simpul_asal, simpul_tujuan, waktu_berangkat,
        ambang, peta_kedalaman, sadar_rob=True,
    )

    return {
        "simpul_asal": simpul_asal,
        "simpul_tujuan": simpul_tujuan,
        "jarak_jepret_asal_m": jarak_asal,
        "jarak_jepret_tujuan_m": jarak_tujuan,
        "rute_abai_rob": abai,
        "rute_sadar_rob": sadar,
    }
