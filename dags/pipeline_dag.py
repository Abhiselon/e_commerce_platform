from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.secret_manager import SecretManagerSecretOperator
from datetime import datetime, timedelta
import os

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2)
}

with DAG(
    dag_id="ecommerce_full_pipeline",
    start_date=datetime(2025,1,1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
) as dag:

    # 1) Load secrets from Secret Manager → set them as env vars
    get_gemini_key = SecretManagerSecretOperator(
        task_id="get_gemini_key",
        project_id="modular-ground-478409-a3",
        secret_id="gemini_api_key",
        variable_name="GEMINI_API_KEY",
    )

    get_sa_json = SecretManagerSecretOperator(
        task_id="get_sa_json",
        project_id="modular-ground-478409-a3",
        secret_id="service_account_key_json",
        variable_name="GOOGLE_APPLICATION_CREDENTIALS_JSON",
    )

    # 2) Install requirements dynamically on Composer worker
    install_reqs = BashOperator(
        task_id="install_requirements",
        bash_command="""
        pip install pandas faker google-cloud-bigquery google-cloud-secret-manager
        pip install dbt-bigquery
        """,
    )

    # 3) Export SA JSON into a temporary file for GCP auth
    setup_credentials = BashOperator(
        task_id="setup_credentials",
        bash_command="""
        echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > /tmp/sa.json
        export GOOGLE_APPLICATION_CREDENTIALS=/tmp/sa.json
        """,
    )

    # 4) Run landing script
    run_landing = BashOperator(
        task_id="run_landing_script",
        bash_command="""
        export GOOGLE_APPLICATION_CREDENTIALS=/tmp/sa.json
        python /opt/airflow/dags/scripts/generate_and_load_landing.py
        """,
        env={
            "GEMINI_API_KEY": "{{ var.value.GEMINI_API_KEY }}",
        },
    )

    # 5) dbt run: staging
    dbt_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command="""
        cd /opt/airflow/dags/e_commerce_platform
        dbt run -m path:staging --profiles-dir /opt/airflow/dags/.dbt
        """,
    )

    # 6) dbt run: marts
    dbt_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command="""
        cd /opt/airflow/dags/e_commerce_platform
        dbt run -m path:marts --profiles-dir /opt/airflow/dags/.dbt
        """,
    )

    # 7) dbt run: consumption
    dbt_consumption = BashOperator(
        task_id="dbt_run_consumption",
        bash_command="""
        cd /opt/airflow/dags/e_commerce_platform
        dbt run -m path:consumption --profiles-dir /opt/airflow/dags/.dbt
        """,
    )

    [get_gemini_key, get_sa_json] >> install_reqs >> setup_credentials >> run_landing >> dbt_staging >> dbt_marts >> dbt_consumption
