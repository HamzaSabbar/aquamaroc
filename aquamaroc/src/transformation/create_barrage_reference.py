from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE = BASE_DIR / "data" / "processed" / "barrages_daily.csv"
OUTPUT = BASE_DIR / "data" / "reference" / "barrages.csv"


def create_reference():
    df = pd.read_csv(SOURCE)

    reference = (
        df[["barrage", "bassin_id", "bassin"]]
        .drop_duplicates()
        .sort_values(["bassin_id", "barrage"])
    )

    reference["latitude"] = None
    reference["longitude"] = None

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    reference.to_csv(
        OUTPUT,
        index=False,
        encoding="utf-8-sig",
    )

    print(reference)
    print(f"\n✅ Référentiel créé : {OUTPUT}")


if __name__ == "__main__":
    create_reference()