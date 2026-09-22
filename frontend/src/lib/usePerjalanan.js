import { useEffect, useState } from "react";
import { ambilJam, ambilJaringan, ambilKondisi, hitungRute } from "./api.js";
import { t } from "./teks.js";

export function pesanGalat(e) {
  if (["asal_jauh_dari_jalan", "tujuan_jauh_dari_jalan"].includes(e?.kode)) return t("galat.titikTerlaluJauhDariJalan");
  if (["waktu_di_luar_cakupan", "data_tidak_tersedia"].includes(e?.kode)) return t("galat.dataTidakTersedia");
  if (e?.kode === "server_sibuk") return t("galat.serverSibuk");
  if ([400, 422].includes(e?.status)) return t("galat.ruteGagal");
  return t("galat.serverTidakMerespons");
}

export function usePerjalanan(asal, tujuan, moda) {
  const [jam, setJam] = useState([]);
  const [infoJam, setInfoJam] = useState(null);
  const [indeksJam, setIndeksJam] = useState(0);
  const [indeksKomit, setIndeksKomit] = useState(0);
  const [geojson, setGeojson] = useState(null);
  const [kondisi, setKondisi] = useState(null);
  const [hasil, setHasil] = useState(null);
  const [memuatJam, setMemuatJam] = useState(true);
  const [memuat, setMemuat] = useState(true);
  const [sedangMencari, setSedangMencari] = useState(false);
  const [galatJam, setGalatJam] = useState(null);
  const [galatJaringan, setGalatJaringan] = useState(null);
  const [galatMuat, setGalatMuat] = useState(null);
  const [galatRute, setGalatRute] = useState(null);
  const [ulangData, setUlangData] = useState(0);
  const [ulangRute, setUlangRute] = useState(0);

  useEffect(() => {
    const c = new AbortController();
    setMemuatJam(true);
    setGalatJam(null);
    ambilJam({ signal: c.signal }).then((data) => {
      if (c.signal.aborted) return;
      setJam(data.jam ?? []);
      setInfoJam(data);
      const pertama = Math.max(0, (data.jam ?? []).findIndex((j) => j.tersedia));
      setIndeksJam(pertama);
      setIndeksKomit(pertama);
      if (!(data.jam ?? []).some((j) => j.tersedia)) setGalatJam(t("galat.dataTidakTersedia"));
    }).catch((e) => {
      if (!c.signal.aborted) { setGalatJam(pesanGalat(e)); setJam([]); }
    }).finally(() => { if (!c.signal.aborted) setMemuatJam(false); });
    return () => c.abort();
  }, [ulangData]);

  // Geometri dimuat terpisah: pita tidak menunggu berkas besar selesai.
  useEffect(() => {
    const c = new AbortController();
    setGalatJaringan(null);
    ambilJaringan({ signal: c.signal }).then((data) => {
      if (!c.signal.aborted) setGeojson(data);
    }).catch((e) => { if (!c.signal.aborted) setGalatJaringan(pesanGalat(e)); });
    return () => c.abort();
  }, [ulangData]);

  useEffect(() => {
    const timer = setTimeout(() => setIndeksKomit(indeksJam), 300);
    return () => clearTimeout(timer);
  }, [indeksJam]);

  const waktuAktif = jam[indeksKomit]?.waktu_utc ?? null;
  const waktuTersedia = Boolean(jam[indeksKomit]?.tersedia);
  const menungguJam = indeksJam !== indeksKomit;
  const kunciRute = JSON.stringify([waktuAktif, asal, tujuan, moda]);
  const versiKondisi = kondisi?.versi_jaringan;
  const versiGeometri = geojson?.versi_jaringan;

  useEffect(() => {
    if (!waktuAktif || !waktuTersedia) {
      setKondisi(null);
      setMemuat(false);
      return;
    }
    const c = new AbortController();
    setMemuat(true);
    setGalatMuat(null);
    setKondisi(null);
    ambilKondisi(waktuAktif, { signal: c.signal }).then((data) => {
      if (!c.signal.aborted) setKondisi(data);
    }).catch((e) => { if (!c.signal.aborted) setGalatMuat(pesanGalat(e)); })
      .finally(() => { if (!c.signal.aborted) setMemuat(false); });
    return () => c.abort();
  }, [waktuAktif, waktuTersedia, ulangData]);

  useEffect(() => {
    if (!versiKondisi || !versiGeometri || versiKondisi === versiGeometri) return;
    const c = new AbortController();
    ambilJaringan({ signal: c.signal }).then((data) => {
      if (c.signal.aborted) return;
      // Publikasi data yang berganti lagi tidak boleh membuat loop unduhan.
      if (data.versi_jaringan !== versiKondisi) {
        setGalatJaringan(t("galat.dataTidakTersedia"));
        return;
      }
      setGeojson(data);
      setGalatJaringan(null);
    }).catch((e) => { if (!c.signal.aborted) setGalatJaringan(pesanGalat(e)); });
    return () => c.abort();
  }, [versiKondisi, versiGeometri]);

  useEffect(() => {
    setHasil(null);
    setGalatRute(null);
    if (!waktuAktif || !waktuTersedia || !asal || !tujuan) {
      setSedangMencari(false);
      return;
    }
    const c = new AbortController();
    setSedangMencari(true);
    hitungRute({ asal, tujuan, waktu: waktuAktif, moda }, { signal: c.signal })
      .then((data) => { if (!c.signal.aborted) setHasil({ kunci: kunciRute, data }); })
      .catch((e) => {
        if (!c.signal.aborted) { setHasil(null); setGalatRute(pesanGalat(e)); }
      }).finally(() => { if (!c.signal.aborted) setSedangMencari(false); });
    return () => c.abort();
  }, [waktuAktif, waktuTersedia, asal, tujuan, moda, ulangRute, ulangData, kunciRute]);

  const kondisiAktif = !menungguJam && !memuat && kondisi?.waktu_utc === waktuAktif
    && kondisi?.versi_jaringan === geojson?.versi_jaringan;
  const hasilAktif = !menungguJam && !sedangMencari && hasil?.kunci === kunciRute;
  const bedaVersi = kondisiAktif && (kondisi.versi_data !== infoJam?.versi_data
    || (hasilAktif && (hasil.data.versi_data !== kondisi.versi_data
      || hasil.data.versi_jaringan !== geojson?.versi_jaringan)));
  const galatPeta = galatJam || galatJaringan || galatMuat || (bedaVersi ? t('galat.dataBerubah') : null);
  return {
    jam, infoJam, indeksJam, setIndeksJam, waktuAktif, waktuTersedia,
    geojson, kondisi: kondisiAktif && !galatPeta ? kondisi : null,
    hasil: hasilAktif && kondisiAktif && !galatPeta ? hasil.data : null,
    memuatJam, memuat: menungguJam || memuat || memuatJam || (!geojson && !galatPeta),
    sedangMencari: sedangMencari || menungguJam, galatMuat: galatPeta, galatRute,
    cariUlang: () => galatPeta ? setUlangData((n) => n + 1) : setUlangRute((n) => n + 1),
    muatUlang: () => setUlangData((n) => n + 1),
  };
}
