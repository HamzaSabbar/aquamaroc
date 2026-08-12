from pathlib import Path
import time

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[2]
FILE = BASE_DIR / "data" / "reference" / "barrages.csv"

URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "AquaMaroc/1.0"
}


ALIASES = {
    "الحسن الثاني": "Hassan II Dam",
    "محمد الخامس": "Mohammed V Dam",
    "الشريف الإدريسي": "Charif Al Idrissi Dam",
    "دار خروفة": "Dar Khrofa Dam",
    "وادي المخازن": "Oued El Makhazine Dam",
    "أسفالو": "Asfalou Dam",
    "إدريس الأول": "Idriss Ier Dam",
    "الوحدة": "Al Wahda Dam",
    "حسن الداخل": "Hassan Addakhil Dam",
    "قدوسة": "Kaddoussa Dam",
    "تيداس": "Tiddas Dam",
    "سيدي محمد بن عبد الله": "Sidi Mohammed Ben Abdellah Dam",
    "أحمد الحنصالي": "Ahmed El Hansali Dam",
    "المسيرة": "Al Massira Dam",
    "بين الويدان": "Bin El Ouidane Dam",
    "مولاي عبد الرحمان": "Moulay Abderrahmane Dam",
    "يعقوب المنصور": "Yacoub El Mansour Dam",
    "عبد المومن": "Abdelmoumen Dam",
    "مولاي عبد الله": "Moulay Abdellah Dam",
    "يوسف بن تاشفين": "Youssef Ben Tachfine Dam",
    "السلطان مولاي علي الشريف": "Moulay Ali Cherif Dam",
    "منصور الذهبي": "Mansour Eddahbi Dam",
}


def search_dam(query):
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 10,
        "countrycodes": "ma",
    }

    response = requests.get(
        URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    results = response.json()

    # On n'accepte QUE les vrais barrages OSM
    for result in results:
        if (
            result.get("category") == "waterway"
            and result.get("type") == "dam"
        ):
            return result

    return None


def get_coordinates(arabic_name):
    queries = [
        f"سد {arabic_name}",
        arabic_name,
    ]

    alias = ALIASES.get(arabic_name)

    if alias:
        queries.append(alias)

    for query in queries:
        print(f"   → {query}")

        result = search_dam(query)

        # Nominatim public : max environ 1 requête/seconde
        time.sleep(1.1)

        if result:
            return {
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "query": query,
                "display_name": result.get("display_name"),
            }

    return None


def enrich_coordinates():
    df = pd.read_csv(FILE)

    # On supprime les anciennes coordonnées non fiables
    df["latitude"] = pd.NA
    df["longitude"] = pd.NA
    df["coord_query"] = pd.NA
    df["coord_display_name"] = pd.NA
    df["coord_status"] = "not_found"

    for index, row in df.iterrows():

        barrage = row["barrage"]

        print(f"\nRecherche : {barrage}")

        result = get_coordinates(barrage)

        if result:
            df.loc[index, "latitude"] = result["latitude"]
            df.loc[index, "longitude"] = result["longitude"]
            df.loc[index, "coord_query"] = result["query"]
            df.loc[index, "coord_display_name"] = result["display_name"]
            df.loc[index, "coord_status"] = "osm_dam"

            print(
                f"✅ {result['latitude']}, "
                f"{result['longitude']}"
            )

        else:
            print("❌ Barrage non trouvé")

    df.to_csv(
        FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== RÉSULTAT ==========")

    print(
        df[
            [
                "barrage",
                "latitude",
                "longitude",
                "coord_status"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    enrich_coordinates()
    
MANUAL_COORDINATES = {
    "إدريس الأول": (34.16161, -4.74939),
    "يعقوب المنصور": (31.1899, -8.0882),
    "السلطان مولاي علي الشريف": (30.935143, -7.245131),
}