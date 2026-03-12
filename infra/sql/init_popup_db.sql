CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS popup_stores (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    source_url TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    popularity INTEGER NOT NULL DEFAULT 100,
    dedupe_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS popup_stores_geom_gix
    ON popup_stores
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS popup_stores_active_dates_idx
    ON popup_stores (start_date, end_date);

