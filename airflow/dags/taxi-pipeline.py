"""
Airflow orchestration only — lives in airflow/, separate from the ML codebase.

ML scripts are NOT mounted from disk. Each run clones the GitHub repo into
/opt/airflow/ml-repo (see dags/scripts/sync_ml_repo.sh).
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PIPELINE_DATA_DIR = "/opt/airflow"
ML_REPO_DIR = "/opt/airflow/ml-repo"
SYNC_SCRIPT = "/opt/airflow/dags/scripts/sync_ml_repo.sh"

PIPELINE_ENV = f"""
export PIPELINE_DATA_DIR={PIPELINE_DATA_DIR}
export ML_REPO_DIR={ML_REPO_DIR}
export MLFLOW_TRACKING_URI=${{MLFLOW_TRACKING_URI:-file:///opt/airflow/mlflow}}
"""

with DAG(
    dag_id="taxi_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["taxi", "github"],
    description="Pull ML code from GitHub, then ingest → preprocess → train",
) as dag:

    sync_code = BashOperator(
        task_id="sync_code_from_github",
        bash_command=f"""
            set -e
            {PIPELINE_ENV}
            bash {SYNC_SCRIPT}
        """,
    )

    ingest = BashOperator(
        task_id="update_window_data",
        bash_command=f"""
            set -e
            {PIPELINE_ENV}
            cd "$ML_REPO_DIR"
            python src/ingest.py
        """,
    )

    preprocess = BashOperator(
        task_id="preprocess_data",
        bash_command=f"""
            set -e
            {PIPELINE_ENV}
            cd "$ML_REPO_DIR"
            python src/preprocess.py
        """,
    )

    train = BashOperator(
        task_id="train_model",
        bash_command=f"""
            set -e
            {PIPELINE_ENV}
            cd "$ML_REPO_DIR"
            python src/train.py
        """,
    )

    sync_code >> ingest >> preprocess >> train
