from ingestion.maadialna import fetch_maadialna, save_raw_data
from cleaning.maadialna import clean_maadialna
from cleaning.quality_checks import run_quality_checks
from loading.postgres import load_data


def run_pipeline():
    print("1. Récupération Maadialna...")
    data = fetch_maadialna()
    save_raw_data(data)

    print("\n2. Nettoyage...")
    clean_maadialna()

    print("\n3. Contrôle qualité...")
    quality_ok = run_quality_checks()

    if not quality_ok:
        print("\n❌ Pipeline arrêté : données invalides.")
        return

    print("\n4. Chargement PostgreSQL...")
    load_data()

    print("\n✅ Pipeline AquaMaroc terminé avec succès.")


if __name__ == "__main__":
    run_pipeline()