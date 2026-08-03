from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def run_pipeline():
    print("Running Employee Analytics Pipeline")

with DAG(
    dag_id="employee_pipeline",
    start_date=datetime(2026,1,1),
    schedule="@daily",
    catchup=False
) as dag:

    pipeline = PythonOperator(
        task_id="employee_pipeline",
        python_callable=run_pipeline
    )
