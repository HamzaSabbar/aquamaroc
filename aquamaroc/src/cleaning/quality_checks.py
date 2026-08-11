from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "processed" / "barrages_daily.csv"


def run_quality_checks():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    errors = []
    warnings = []

    # 1. Le fichier ne doit pas être vide
    if df.empty:
        errors.append("Le fichier ne contient aucune donnée.")

    # 2. Vérification des colonnes obligatoires
    required_columns = [
        "date",
        "bassin",
        "bassin_id",
        "barrage",
        "taux_remplissage",
        "taux_annee_precedente",
        "volume_millions_m3",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Colonnes manquantes : {missing_columns}"
        )

    if errors:
        print("❌ Contrôle qualité échoué")
        for error in errors:
            print(f"- {error}")
        return False

    # 3. Date valide
    invalid_dates = pd.to_datetime(
        df["date"],
        errors="coerce"
    ).isna()

    if invalid_dates.any():
        errors.append(
            f"{invalid_dates.sum()} date(s) invalide(s)."
        )

    # 4. Champs obligatoires non vides
    for column in ["bassin", "bassin_id", "barrage"]:
        missing = df[column].isna() | (
            df[column].astype(str).str.strip() == ""
        )

        if missing.any():
            errors.append(
                f"{missing.sum()} valeur(s) vide(s) dans '{column}'."
            )

    # 5. Pas de doublon barrage + date
    duplicates = df.duplicated(
        subset=["date", "barrage"],
        keep=False
    )

    if duplicates.any():
        errors.append(
            f"{duplicates.sum()} ligne(s) dupliquée(s) "
            "pour le même barrage et la même date."
        )

    # 6. Taux actuel entre 0 et 100
    invalid_rates = (
        df["taux_remplissage"].isna()
        | (df["taux_remplissage"] < 0)
        | (df["taux_remplissage"] > 100)
    )

    if invalid_rates.any():
        errors.append(
            f"{invalid_rates.sum()} taux de remplissage invalide(s)."
        )

    # 7. Volume positif ou nul
    invalid_volumes = (
        df["volume_millions_m3"].isna()
        | (df["volume_millions_m3"] < 0)
    )

    if invalid_volumes.any():
        errors.append(
            f"{invalid_volumes.sum()} volume(s) invalide(s)."
        )

    # 8. Taux année précédente :
    # peut manquer sur Maadialna, donc seulement warning
    missing_previous = df[
        "taux_annee_precedente"
    ].isna().sum()

    if missing_previous > 0:
        warnings.append(
            f"{missing_previous} taux de l'année précédente manquant(s)."
        )

    # Résultat
    if warnings:
        print("\n⚠️ Avertissements :")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("\n❌ Contrôle qualité échoué :")
        for error in errors:
            print(f"- {error}")

        return False

    print(
        f"\n✅ Contrôle qualité réussi : "
        f"{len(df)} lignes vérifiées."
    )

    return True


if __name__ == "__main__":
    success = run_quality_checks()

    if not success:
        raise SystemExit(1)