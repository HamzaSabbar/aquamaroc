import json
from datetime import datetime
from pathlib import Path

import requests


URL = "https://maadialna.ma/ar/get-bassin"

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "maadialna"


def fetch_maadialna():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    return response.json()


def save_raw_data(data):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d")

    filepath = RAW_DIR / f"barrages_{date}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Données sauvegardées : {filepath}")


if __name__ == "__main__":
    data = fetch_maadialna()
    save_raw_data(data)