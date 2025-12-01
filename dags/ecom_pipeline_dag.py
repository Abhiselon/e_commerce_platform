from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from google.cloud import secretmanager

DBT_VENV = "/home/airflow/dbt_venv"   # writable path on worker
DBT_PROJECT_DIR = "/home/airflow/gcs/data/ecom"

# Define arguments
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

def fetch_secrets_to_xcom(**kwargs):
    """
    Fetches secrets from Secret Manager and returns them.
    Airflow automatically pushes the return value to XComs.
    """
    client = secretmanager.SecretManagerServiceClient()
    # Replace with your actual project number
    project_number = "164190133712" 
    
    def get_secret(name):
        secret_name = f"projects/{project_number}/secrets/{name}/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})
        return response.payload.data.decode("utf-8")

    print("Fetching secrets...")
    secrets = {
        "gemini_api_key": get_secret("gemini_api_key"),
        "service_account_json": get_secret("service_account_json")
    }
    return secrets

with DAG(
    dag_id="ecom_pipeline_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
) as dag:

    

    # Task 1: Fetch Secrets
    fetch_secrets = PythonOperator(
        task_id="fetch_secrets",
        python_callable=fetch_secrets_to_xcom,
    )

    # Task 2: Run Script (Landing/Extraction)
    generate_and_load_landing = BashOperator(
        task_id="generate_and_load_landing",
        env={
            "GEMINI_API_KEY": "{{ ti.xcom_pull(task_ids='fetch_secrets')['gemini_api_key'] }}",
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command="""
            set -e
            
            # 1. Write the Service Account JSON content to a file
            echo "$SA_JSON_CONTENT" > /tmp/sa_key.json
            
            # 2. Install dependencies 
            echo "Installing dependencies for landing script..."
            pwd
            pip install --user -r /home/airflow/gcs/dags/scripts/requirements.txt
            
            # 3. Run the Python script (cd and python combined using '&&')
            echo "Running landing pipeline script..."
            pwd
            cd /home/airflow/gcs/dags/scripts && python generate_and_load_landing.py
            
            # 4. Cleanup
            rm /tmp/sa_key.json
        """
    )

    # Task 3: Create virtual environment for dbt execution
    create_venv = BashOperator(
        task_id="create_venv",
        bash_command=f"""
        python3 -m venv {DBT_VENV}
        {DBT_VENV}/bin/python -m pip install --upgrade pip
        {DBT_VENV}/bin/pip install --no-cache-dir dbt-core dbt-bigquery
        """,
    )

    # Task 4: Run DBT Staging 
    run_staging = BashOperator(
        task_id="run_dbt_staging",
        env={
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command=f"""
        set -e
        SA_FILE="/tmp/sa_key.json"
        echo "$SA_JSON_CONTENT" > /tmp/sa_key.json

        source {DBT_VENV}/bin/activate
        cd {DBT_PROJECT_DIR}
        dbt run -s models/01_staging/*
        rm $SA_FILE
        """,
    )

    # Task 4b: Run DBT Staging Tests 
    run_staging_test = BashOperator(
        task_id="run_dbt_staging_test",
        env={
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command=f"""
        set -e
        SA_FILE="/tmp/sa_key.json"
        echo "$SA_JSON_CONTENT" > /tmp/sa_key.json
        source {DBT_VENV}/bin/activate
        cd {DBT_PROJECT_DIR}
        dbt test -s models/01_staging/*
        rm $SA_FILE
        """,
    )

    # Task 5: Run DBT Marts 
    run_marts = BashOperator(
        task_id="run_dbt_marts",
        env={
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command=f"""
        set -e
        SA_FILE="/tmp/sa_key.json"
        echo "$SA_JSON_CONTENT" > /tmp/sa_key.json
        source {DBT_VENV}/bin/activate
        cd {DBT_PROJECT_DIR}
        dbt run -s models/02_marts/*
        rm $SA_FILE
        """,
    )

    # Task 5b: Run DBT Marts Tests 
    run_marts_test = BashOperator(
        task_id="run_dbt_marts_test",
        env={
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command=f"""
        set -e
        SA_FILE="/tmp/sa_key.json"
        echo "$SA_JSON_CONTENT" > /tmp/sa_key.json
        source {DBT_VENV}/bin/activate
        cd {DBT_PROJECT_DIR}
        dbt test -s models/02_marts/*
        rm $SA_FILE
        """,
    )

    # Task 5: Run DBT Consumption 
    run_consumption = BashOperator(
        task_id="run_dbt_consumption",
        env={
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command=f"""
        set -e
        SA_FILE="/tmp/sa_key.json"
        echo "$SA_JSON_CONTENT" > /tmp/sa_key.json
        source {DBT_VENV}/bin/activate
        cd {DBT_PROJECT_DIR}
        dbt run -s models/03_consumption/*
        rm $SA_FILE
        """,
    )

    # Task 5b: Run DBT Consumption Tests
    run_consumption_test = BashOperator(
        task_id="run_dbt_consumption_test",
        env={
            "SA_JSON_CONTENT": "{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa_key.json"
        },
        bash_command=f"""
        set -e
        SA_FILE="/tmp/sa_key.json"
        echo "$SA_JSON_CONTENT" > /tmp/sa_key.json
        source {DBT_VENV}/bin/activate
        cd {DBT_PROJECT_DIR}
        dbt test -s models/03_consumption/*
        rm $SA_FILE
        """,
    )

    # Define Dependencies
    fetch_secrets >> generate_and_load_landing >> create_venv >> run_staging >> run_staging_test >> run_marts >> run_marts_test >> run_consumption >> run_consumption_test