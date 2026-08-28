"""Akuntansi dampak: selisih waktu, jarak, bahan bakar, dan emisi antar rute.

Yang dihitung di sini adalah HARGA yang dibayar untuk menghindari rob:
berapa menit lebih lama, berapa kilometer lebih jauh, berapa liter bahan
bakar lebih banyak, dan berapa kilogram CO2 ekuivalen lebih besar, bila
dibandingkan dengan rute yang mengabaikan genangan.

KENAPA SELALU TERHADAP PEMBANDING, TIDAK PERNAH BERDIRI SENDIRI.

Menyajikan "rute ini menghemat sekian menit" tanpa menyebut dibandingkan apa
adalah klaim kosong. Modul ini karena itu hanya menerima DUA rute sekaligus
dan menolak menghitung apa pun bila salah satunya tidak ditemukan.

KENAPA RENTANG, BUKAN ANGKA TUNGGAL.

Konsumsi bahan bakar per kilometer bergantung pada kendaraan, muatan, gaya
mengemudi, dan kepadatan lalu lintas. Angka di tabel `ambang_moda` adalah
satu nilai wakil, dan menyajikannya sebagai satu angka pasti akan menyesatkan
sampai dua digit di belakang koma.

Yang disajikan karena itu rentang. Lebar rentangnya sendiri sebuah asumsi,
dinyatakan sekali di KETIDAKPASTIAN_KONSUMSI, dan dicatat di docs/batasan.md.

SUMBER TIAP FAKTOR.

Seluruh faktor dibaca dari tabel `ambang_moda`, tidak satu pun ditulis tetap
di dalam kode ini. Asal-usulnya:

    konsumsi_l_per_km       motor 0,020 · mobil 0,090 · truk 0,250
                            Setara 50 · 11,1 · 4,0 km per liter. Angka ini
                            masih berstatus ASUMSI menurut komentar di
                            db/schema.sql dan BELUM punya sitasi. Tercatat
                            sebagai pekerjaan terbuka di docs/batasan.md.

    faktor_emisi_kg_per_l   bensin 2,31 · solar 2,68 kg CO2 per liter
                            Ini nilai baku pembakaran bahan bakar yang lazim
                            dipakai inventarisasi emisi. Sitasi resminya
                            BELUM dimasukkan ke repo; data/referensi/
                            faktor_emisi.json masih null. Sampai sitasinya
                            ada, angka ini wajib disebut sebagai faktor baku,
                            bukan sebagai hasil pengukuran tim.

Aturan repo nomor 1 berlaku penuh: tidak ada satu pun angka di sini yang
dikarang, dan yang belum bersitasi dinyatakan demikian, bukan disembunyikan.
"""

from __future__ import annotations

from dataclasses import dataclass

# Lebar rentang di sekitar konsumsi nominal. ASUMSI, bukan hasil pengukuran.
# Dinyatakan sekali di sini supaya ada satu tempat untuk mengoreksinya saat
# ada data konsumsi yang sebenarnya.
KETIDAKPASTIAN_KONSUMSI = 0.30

# Batas bawah agar selisih yang tidak berarti tidak disajikan sebagai temuan.
# Selisih di bawah ini muncul dari pembulatan geometri ruas, bukan dari
# pilihan rute yang berbeda.
AMBANG_SELISIH_MENIT = 0.5
AMBANG_SELISIH_KM = 0.05


@dataclass(frozen=True)
class Rentang:
    """Nilai dengan batas bawah dan atas. Bukan nilai tunggal."""

    bawah: float
    atas: float

    @property
    def tengah(self) -> float:
        return (self.bawah + self.atas) / 2.0

    def sebagai_dict(self, desimal: int = 2) -> dict:
        return {
            "bawah": round(self.bawah, desimal),
            "atas": round(self.atas, desimal),
            "tengah": round(self.tengah, desimal),
        }


def _rentang_konsumsi(km: float, konsumsi_l_per_km: float) -> Rentang:
    """Liter bahan bakar untuk jarak tertentu, sebagai rentang."""
    nominal = km * konsumsi_l_per_km
    return Rentang(nominal * (1.0 - KETIDAKPASTIAN_KONSUMSI),
                   nominal * (1.0 + KETIDAKPASTIAN_KONSUMSI))


def hitung(selisih_menit: float, selisih_km: float, ambang_moda: dict) -> dict:
    """Ubah selisih waktu dan jarak menjadi angka dampak.

    `ambang_moda` adalah satu baris tabel ambang_moda untuk moda yang dipakai.
    Fungsi ini TIDAK membaca database; pemanggilnya yang bertanggung jawab.

    Selisih negatif berarti rute sadar rob justru lebih pendek atau lebih
    cepat, dan itu mungkin terjadi bila rute pembanding menembus ruas yang
    memperlambat. Tanda dipertahankan apa adanya, tidak dimutlakkan.
    """
    konsumsi = float(ambang_moda["konsumsi_l_per_km"])
    faktor = float(ambang_moda["faktor_emisi_kg_per_l"])

    liter = _rentang_konsumsi(selisih_km, konsumsi)
    # Faktor emisi dikalikan pada kedua ujung rentang liter. Faktornya sendiri
    # tidak diberi rentang karena ia sifat bahan bakar, bukan sifat perjalanan.
    emisi = Rentang(liter.bawah * faktor, liter.atas * faktor)

    berarti = (abs(selisih_menit) >= AMBANG_SELISIH_MENIT
               or abs(selisih_km) >= AMBANG_SELISIH_KM)

    return {
        "berarti": berarti,
        "menit": round(selisih_menit, 1),
        "km": round(selisih_km, 2),
        "liter": liter.sebagai_dict(3),
        "kg_co2e": emisi.sebagai_dict(3),
        "faktor": {
            "konsumsi_l_per_km": konsumsi,
            "faktor_emisi_kg_per_l": faktor,
            "ketidakpastian_konsumsi": KETIDAKPASTIAN_KONSUMSI,
            "_sumber": (
                "Kedua faktor dibaca dari tabel ambang_moda. Konsumsi masih "
                "berstatus asumsi tanpa sitasi; faktor emisi adalah nilai "
                "baku pembakaran bahan bakar yang sitasinya belum dimasukkan "
                "ke repo. Lihat docs/batasan.md."
            ),
        },
    }


def paparan(kedalaman_terlewati_cm: list[float], ambang_moda: dict) -> dict:
    """Periksa apakah rute sadar rob TETAP menembus genangan berisiko.

    Rute sadar rob menghindari genangan sebisanya, tetapi tidak selalu bisa.
    Bila seluruh jalan keluar dari suatu kawasan tergenang, mesin routing akan
    memilih yang paling ringan — dan pengguna berhak tahu bahwa ia tetap akan
    menembus air.

    Ambang `berisiko_cm` dibaca dari tabel, tidak ditulis tetap di sini.
    """
    berisiko = float(ambang_moda["berisiko_cm"])
    tidak_bisa = float(ambang_moda["tidak_bisa_lewat_cm"])

    di_atas = [d for d in kedalaman_terlewati_cm if d >= berisiko]
    maks = max(kedalaman_terlewati_cm) if kedalaman_terlewati_cm else 0.0

    return {
        "menembus": bool(di_atas),
        "ruas_berisiko": len(di_atas),
        "kedalaman_maks_cm": round(maks, 1),
        "ambang_berisiko_cm": berisiko,
        "ambang_tidak_bisa_lewat_cm": tidak_bisa,
    }
