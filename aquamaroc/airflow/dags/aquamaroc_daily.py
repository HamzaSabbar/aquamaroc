import sys

import pendulum
from airflow.sdk import dag, task

# Permet à Airflow de trouver le dossier src/ d'AquaMaroc
sys.path.insert(0, "/opt/airflow/aquamaroc/src")


@dag(
    dag_id="aquamaroc_daily",
    schedule=None,  # manuel pour le moment
    start_date=pendulum.datetime(2026, 8, 12, tz="Africa/Casablanca"),
    catchup=False,
    tags=["aquamaroc"],
)
def aquamaroc_pipeline():

    @task
    def ingestion():
        from ingestion.maadialna import fetch_maadialna, save_raw_data

        data = fetch_maadialna()
        save_raw_data(data)

    @task
    def nettoyage():
        from cleaning.maadialna import clean_maadialna

        clean_maadialna()

    @task
    def controle_qualite():
        from cleaning.quality_checks import run_quality_checks

        quality_ok = run_quality_checks()

        if not quality_ok:
            raise ValueError("Contrôle qualité échoué")

    @task
    def chargement_postgres():
        from loading.postgres import load_data

        load_data()

    t1 = ingestion()
    t2 = nettoyage()
    t3 = controle_qualite()
    t4 = chargement_postgres()

    t1 >> t2 >> t3 >> t4


aquamaroc_pipeline()