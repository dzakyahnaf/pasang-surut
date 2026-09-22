-- Jalankan sekali sebelum pipeline prediksi baru. Tidak menebak cakupan
-- dari baris basah yang lama; terbitkan ulang dataset melalui pipeline.
CREATE TABLE IF NOT EXISTS cakupan_prediksi (
    id SMALLINT PRIMARY KEY CHECK (id = 1),
    versi TEXT NOT NULL,
    sumber TEXT NOT NULL,
    jam_lengkap TIMESTAMPTZ[] NOT NULL CHECK (cardinality(jam_lengkap) > 0),
    akhir_eksklusif TIMESTAMPTZ NOT NULL,
    diterbitkan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
