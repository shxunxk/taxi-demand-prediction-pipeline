from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="taxi_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@monthly",
    catchup=False
) as dag:

    ingest = BashOperator(
        task_id="update_window_data",
        bash_command="python /opt/airflow/src/ingest.py"
    )

    train = BashOperator(
        task_id="preprocess_data",
        bash_command="python /opt/airflow/src/preprocess.py"
    )

    train = BashOperator(
        task_id="train_model",
        bash_command="python /opt/airflow/src/train.py"
    )

    ingest >> train