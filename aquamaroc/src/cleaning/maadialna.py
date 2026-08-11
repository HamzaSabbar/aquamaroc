import json
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "maadialna"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def get_latest_raw_file():
    files = sorted(RAW_DIR.glob("barrages_*.json"))

    if not files:
        raise FileNotFoundError("Aucun fichier Maadialna trouvé.")

    return files[-1]


def extract_number(pattern, text):
    match = re.search(pattern, text)

    if match:
        return float(match.group(1))

    return None


def parse_barrages(html, bassin, bassin_id, date):
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for ul in soup.select(".modal-body ul"):
        previous_p = ul.find_previous_sibling("p")

        if previous_p is None:
            continue

        strong = previous_p.find("strong")

        if strong is None:
            continue

        barrage = strong.get_text(" ", strip=True)

        values = [
            li.get_text(" ", strip=True)
            for li in ul.find_all("li")
        ]

        taux = None
        taux_annee_precedente = None
        volume = None

        for value in values:
            if value.startswith("اليوم"):
                taux = extract_number(
                    r"(\d+(?:\.\d+)?)%",
                    value
                )

            elif "السنة الماضية" in value:
                taux_annee_precedente = extract_number(
                    r"(\d+(?:\.\d+)?)%",
                    value
                )

            elif "الحجم" in value:
                volume = extract_number(
                    r"الحجم\s*(\d+(?:\.\d+)?)",
                    value
                )

        rows.append({
            "date": date,
            "bassin": bassin.strip(),
            "bassin_id": bassin_id,
            "barrage": barrage,
            "taux_remplissage": taux,
            "taux_annee_precedente": taux_annee_precedente,
            "volume_millions_m3": volume
        })

    return rows


def clean_maadialna():
    filepath = get_latest_raw_file()

    date = filepath.stem.replace("barrages_", "")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for bassin_data in data:
        bassin = bassin_data["title"]
        bassin_id = bassin_data["field_id_region_hydraulique"]
        html = bassin_data["field_modal_content_barrage"]

        barrages = parse_barrages(
            html,
            bassin,
            bassin_id,
            date
        )

        rows.extend(barrages)

    df = pd.DataFrame(rows)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output = PROCESSED_DIR / "barrages_daily.csv"

    if output.exists():
        old_df = pd.read_csv(output)

        df = pd.concat(
            [old_df, df],
            ignore_index=True
        )

        df = df.drop_duplicates(
            subset=["date", "barrage"],
            keep="last"
        )

    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(df)
    print(f"\nDonnées propres sauvegardées : {output}")


if __name__ == "__main__":
    clean_maadialna()