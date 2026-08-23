-- PASANG SURUT — skema database
-- Jalankan di Supabase: SQL Editor -> New query -> tempel -> Run
--
-- ATURAN MAIN:
-- Tabel prediksi_genangan adalah KONTRAK antara Orang A (model) dan Orang B (routing).
-- Selama bentuk tabel ini tidak berubah, A dan B bisa bekerja paralel tanpa saling menunggu.
-- Perubahan kolom di tabel itu WAJIB diumumkan ke seluruh tim.

CREATE EXTENSION IF NOT EXISTS postgis;

-- ---------------------------------------------------------------
-- 1. Ruas jalan (diisi Orang B dari OSM lewat OSMnx)
-- ---------------------------------------------------------------
CREATE TABLE ruas_jalan (
    edge_id                BIGSERIAL PRIMARY KEY,
    osm_u                  BIGINT NOT NULL,
    osm_v                  BIGINT NOT NULL,
    nama                   TEXT,
    jenis                  TEXT,                      -- highway=* dari OSM
    panjang_m              DOUBLE PRECISION NOT NULL,
    kecepatan_kmh          DOUBLE PRECISION DEFAULT 30,
    satu_arah              BOOLEAN DEFAULT FALSE,

    -- fitur untuk model (diisi Orang A)
    elevasi_m              DOUBLE PRECISION,          -- dari DEMNAS
    laju_subsidensi_cm_thn DOUBLE PRECISION,          -- dari literatur
    jarak_pantai_m         DOUBLE PRECISION,
    jarak_sungai_m         DOUBLE PRECISION,

    geom                   GEOMETRY(LineString, 4326) NOT NULL
);

CREATE INDEX idx_ruas_geom ON ruas_jalan USING GIST (geom);
CREATE INDEX idx_ruas_uv   ON ruas_jalan (osm_u, osm_v);

-- ---------------------------------------------------------------
-- 2. Variabel pemicu per jam (diisi Orang A)
-- ---------------------------------------------------------------
CREATE TABLE pemicu (
    waktu            TIMESTAMPTZ PRIMARY KEY,
    tinggi_pasut_m   DOUBLE PRECISION NOT NULL,       -- rekonstruksi harmonik
    hujan_24j_mm     DOUBLE PRECISION DEFAULT 0,
    hujan_72j_mm     DOUBLE PRECISION DEFAULT 0,
    sumber_hujan     TEXT DEFAULT 'open-meteo'
);

-- ---------------------------------------------------------------
-- 3. KONTRAK — prediksi genangan per ruas per jam
--    Orang A menulis ke sini. Orang B hanya membaca.
--    Hari 1-3 Orang B isi sendiri dengan angka dummy supaya routing bisa dibangun.
-- ---------------------------------------------------------------
CREATE TABLE prediksi_genangan (
    edge_id       BIGINT NOT NULL REFERENCES ruas_jalan(edge_id) ON DELETE CASCADE,
    waktu         TIMESTAMPTZ NOT NULL,
    kedalaman_cm  DOUBLE PRECISION NOT NULL DEFAULT 0,
    probabilitas  DOUBLE PRECISION NOT NULL DEFAULT 0
                  CHECK (probabilitas >= 0 AND probabilitas <= 1),
    sumber        TEXT NOT NULL DEFAULT 'model_v1',   -- 'dummy' selama hari 1-3
    PRIMARY KEY (edge_id, waktu)
);

CREATE INDEX idx_pred_waktu ON prediksi_genangan (waktu);

-- ---------------------------------------------------------------
-- 4. Sampel latih dari Sentinel-1 (diisi Orang A)
--    Satu baris = satu ruas pada satu waktu akuisisi citra.
--    Ingat: SETIAP citra jadi sampel, bukan hanya citra saat rob.
-- ---------------------------------------------------------------
CREATE TABLE sampel_latih (
    id                BIGSERIAL PRIMARY KEY,
    edge_id           BIGINT NOT NULL REFERENCES ruas_jalan(edge_id),
    waktu_akuisisi    TIMESTAMPTZ NOT NULL,
    s1_scene_id       TEXT,
    basah             BOOLEAN NOT NULL,               -- label dari Sentinel-1
    tinggi_pasut_m    DOUBLE PRECISION NOT NULL,
    hujan_24j_mm      DOUBLE PRECISION,
    hujan_72j_mm      DOUBLE PRECISION
);

CREATE INDEX idx_sampel_waktu ON sampel_latih (waktu_akuisisi);

-- ---------------------------------------------------------------
-- 5. Ambang kelayakan per moda (dipakai mesin routing)
--    Angka awal ini ASUMSI. Cari rujukannya, lalu koreksi dan
--    cantumkan sumbernya di bagian Batasan Perangkat Lunak.
-- ---------------------------------------------------------------
CREATE TABLE ambang_moda (
    moda                 TEXT PRIMARY KEY,
    lambat_cm            DOUBLE PRECISION NOT NULL,   -- mulai melambat
    berisiko_cm          DOUBLE PRECISION NOT NULL,   -- beri peringatan
    tidak_bisa_lewat_cm  DOUBLE PRECISION NOT NULL,
    konsumsi_l_per_km    DOUBLE PRECISION NOT NULL,
    faktor_emisi_kg_per_l DOUBLE PRECISION NOT NULL
);

INSERT INTO ambang_moda VALUES
  ('motor', 10, 20, 30, 0.020, 2.31),
  ('mobil', 15, 30, 50, 0.090, 2.31),
  ('truk',  20, 40, 70, 0.250, 2.68);

-- ---------------------------------------------------------------
-- 6. View siap pakai untuk mesin routing
-- ---------------------------------------------------------------
CREATE VIEW v_bobot_ruas AS
SELECT
    r.edge_id,
    r.osm_u,
    r.osm_v,
    r.panjang_m,
    r.kecepatan_kmh,
    p.waktu,
    COALESCE(p.kedalaman_cm, 0)  AS kedalaman_cm,
    COALESCE(p.probabilitas, 0)  AS probabilitas,
    r.geom
FROM ruas_jalan r
LEFT JOIN prediksi_genangan p ON p.edge_id = r.edge_id;
