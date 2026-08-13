from pathlib import Path

import pandas as pd
import psycopg


BASE_DIR = Path(__file__).resolve().parents[2]
CSV_FILE = BASE_DIR / "data" / "processed" / "barrages_daily.csv"


import os
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv(
        "AQUAMAROC_DB_HOST",
        os.getenv("DB_HOST", "localhost")
    ),
    "port": int(os.getenv("DB_PORT", 5432)),
}

def load_data():
    df = pd.read_csv(CSV_FILE)

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            for _, row in df.iterrows():

                # 1. Bassin
                cur.execute(
                    """
                    INSERT INTO dim_bassin (bassin_id, nom)
                    VALUES (%s, %s)
                    ON CONFLICT (bassin_id) DO NOTHING
                    """,
                    (row["bassin_id"], row["bassin"]),
                )

                # 2. Barrage
                cur.execute(
                    """
                    INSERT INTO dim_barrage (nom, bassin_id)
                    VALUES (%s, %s)
                    ON CONFLICT (nom, bassin_id) DO NOTHING
                    """,
                    (row["barrage"], row["bassin_id"]),
                )

                # Récupérer l'ID du barrage
                cur.execute(
                    """
                    SELECT barrage_id
                    FROM dim_barrage
                    WHERE nom = %s AND bassin_id = %s
                    """,
                    (row["barrage"], row["bassin_id"]),
                )

                barrage_id = cur.fetchone()[0]

                # 3. Date
                date = pd.to_datetime(row["date"])

                cur.execute(
                    """
                    INSERT INTO dim_date (date_id, annee, mois, jour)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (date_id) DO NOTHING
                    """,
                    (
                        date.date(),
                        date.year,
                        date.month,
                        date.day,
                    ),
                )

                # 4. Mesures quotidiennes
                cur.execute(
                    """
                    INSERT INTO fct_remplissage_jour (
                        date_id,
                        barrage_id,
                        taux_remplissage,
                        taux_annee_precedente,
                        volume_millions_m3
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date_id, barrage_id)
                    DO UPDATE SET
                        taux_remplissage = EXCLUDED.taux_remplissage,
                        taux_annee_precedente =
                            EXCLUDED.taux_annee_precedente,
                        volume_millions_m3 =
                            EXCLUDED.volume_millions_m3
                    """,
                    (
                        date.date(),
                        barrage_id,
                        row["taux_remplissage"],
                        None
                        if pd.isna(row["taux_annee_precedente"])
                        else row["taux_annee_precedente"],
                        row["volume_millions_m3"],
                    ),
                )

    print("✅ Données chargées dans PostgreSQL.")


if __name__ == "__main__":
    load_data()
    
def load_weather_data():
    weather_file = BASE_DIR / "data" / "processed" / "weather_daily.csv"

    df = pd.read_csv(weather_file)

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            for _, row in df.iterrows():

                date = pd.to_datetime(row["date"])

                # S'assurer que la date existe dans dim_date
                cur.execute("""
                    INSERT INTO dim_date (date_id, annee, mois, jour)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (date_id) DO NOTHING
                """, (
                    date.date(),
                    date.year,
                    date.month,
                    date.day
                ))

                # Retrouver l'identifiant du barrage
                cur.execute("""
                    SELECT barrage_id
                    FROM dim_barrage
                    WHERE nom = %s
                    AND bassin_id = %s
                """, (
                    row["barrage"],
                    row["bassin_id"]
                ))

                result = cur.fetchone()

                if result is None:
                    print(f"⚠️ Barrage introuvable : {row['barrage']}")
                    continue

                barrage_id = result[0]

                # Charger la météo
                cur.execute("""
                    INSERT INTO fct_meteo_jour (
                        date_id,
                        barrage_id,
                        temperature_moyenne,
                        precipitation_mm,
                        et0_mm
                    )
                    VALUES (%s, %s, %s, %s, %s)

                    ON CONFLICT (date_id, barrage_id)
                    DO UPDATE SET
                        temperature_moyenne = EXCLUDED.temperature_moyenne,
                        precipitation_mm = EXCLUDED.precipitation_mm,
                        et0_mm = EXCLUDED.et0_mm
                """, (
                    date.date(),
                    barrage_id,
                    row["temperature_moyenne"],
                    row["precipitation_mm"],
                    row["et0_mm"],
                ))

    print("✅ Données météo chargées dans PostgreSQL.")
    
if __name__ == "__main__":
    load_weather_data()