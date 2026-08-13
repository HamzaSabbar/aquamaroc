from pathlib import Path

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[2]

BARRAGES_FILE = BASE_DIR / "data" / "reference" / "barrages.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "weather_daily.csv"

URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "et0_fao_evapotranspiration",
        ],
        "timezone": "Africa/Casablanca",
        "forecast_days": 1,
    }

    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def collect_weather():
    barrages = pd.read_csv(BARRAGES_FILE)

    # On garde seulement les barrages géolocalisés
    barrages = barrages.dropna(subset=["latitude", "longitude"])

    rows = []

    for _, barrage in barrages.iterrows():

        print(f"Météo : {barrage['barrage']}")

        data = fetch_weather(
            barrage["latitude"],
            barrage["longitude"],
        )

        daily = data["daily"]

        rows.append({
            "date": daily["time"][0],
            "barrage": barrage["barrage"],
            "bassin_id": barrage["bassin_id"],
            "latitude": barrage["latitude"],
            "longitude": barrage["longitude"],
            "temperature_moyenne": daily["temperature_2m_mean"][0],
            "precipitation_mm": daily["precipitation_sum"][0],
            "et0_mm": daily["et0_fao_evapotranspiration"][0],
        })

    df = pd.DataFrame(rows)

    if OUTPUT_FILE.exists():
        old_df = pd.read_csv(OUTPUT_FILE)

        df = pd.concat(
            [old_df, df],
            ignore_index=True,
        )

        df = df.drop_duplicates(
            subset=["date", "barrage"],
            keep="last",
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n✅ Données météo récupérées.")
    print(df.tail(20))


if __name__ == "__main__":
    collect_weather()