# Kontainer API PASANG SURUT.
#
# Dibuat setipis mungkin dengan sengaja. Yang di-deploy hanya lapisan API dan
# data yang dibacanya saat berjalan; seluruh skrip pipeline, model, dan
# berkas analisis TIDAK ikut karena tidak satu pun dipanggil saat aplikasi
# melayani permintaan.
#
# Berlaku untuk Render, Railway, maupun Fly.io. Ketiganya membaca Dockerfile.

FROM python:3.11.8-slim

# psycopg2-binary sudah membawa pustaka kliennya sendiri, jadi tidak perlu
# libpq-dev. numpy dan fastapi murni roda biner. Tidak ada paket sistem yang
# perlu dipasang, dan itu memang tujuannya.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Requirement disalin lebih dulu supaya lapisan pip di-cache dan tidak
# dipasang ulang tiap kali kode berubah.
COPY backend/requirements-runtime.txt ./backend/requirements-runtime.txt
RUN pip install --no-cache-dir -r backend/requirements-runtime.txt

# HANYA yang dibaca saat runtime.
#   app/            lapisan API dan domain
#   data/aoi/       batas wilayah kerja
#   data/processed/ potret demo, jaringan jalan cadangan, tujuan cepat
#   data/referensi/ konstanta pasut, metrik model, faktor emisi
#
# scripts/ sengaja TIDAK disalin. Seluruhnya menyentuh Earth Engine, OSM,
# atau Open-Meteo, dan tidak satu pun boleh terpanggil dari server yang
# sedang melayani. Meninggalkannya di luar kontainer membuat aturan itu
# ditegakkan oleh susunan berkas, bukan oleh niat baik.
COPY backend/app ./backend/app
COPY data/aoi ./data/aoi
COPY data/processed ./data/processed
COPY data/referensi ./data/referensi

# Model gradient boosting tidak dipakai saat melayani permintaan; yang
# dipakai indeks kerentanan yang sudah masuk potret. Dibuang supaya citra
# tidak membawa satu megabyte yang tidak pernah dibuka.
RUN rm -f data/processed/model_genangan_v1.joblib \
          data/processed/s1_daftar_citra.json \
          data/processed/ruas_sampel_latih.json

WORKDIR /app/backend

# Render dan Railway menyuntikkan PORT. Bawaan 8000 untuk menjalankan lokal.
ENV PORT=8000
EXPOSE 8000

# Satu pekerja saja, dan itu disengaja. Graf 19.394 ruas dipegang di memori
# tiap proses; dua pekerja berarti dua salinan graf dan dua kali koneksi
# database, sementara beban yang diharapkan hanya beberapa juri sekaligus.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
