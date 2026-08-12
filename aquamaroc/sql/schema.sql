CREATE TABLE IF NOT EXISTS dim_bassin (
    bassin_id VARCHAR(20) PRIMARY KEY,
    nom VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_barrage (
    barrage_id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    bassin_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (bassin_id) REFERENCES dim_bassin(bassin_id),
    UNIQUE (nom, bassin_id)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id DATE PRIMARY KEY,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    jour INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fct_remplissage_jour (
    date_id DATE NOT NULL,
    barrage_id INTEGER NOT NULL,
    taux_remplissage NUMERIC(5,2),
    taux_annee_precedente NUMERIC(5,2),
    volume_millions_m3 NUMERIC(12,2),

    PRIMARY KEY (date_id, barrage_id),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    FOREIGN KEY (barrage_id)
        REFERENCES dim_barrage(barrage_id)
);