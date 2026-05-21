import os
from pathlib import Path

# Code lives in the git checkout (ml-repo). Data/models/metadata live on the Airflow host.
PIPELINE_DATA_DIR = Path(os.environ.get("PIPELINE_DATA_DIR", Path(__file__).resolve().parent.parent))
ML_REPO_DIR = Path(os.environ.get("ML_REPO_DIR", PIPELINE_DATA_DIR))

WINDOW_DATA_DIR = PIPELINE_DATA_DIR / "windowData"
MODELS_DIR = PIPELINE_DATA_DIR / "models"
METADATA_DIR = PIPELINE_DATA_DIR / "metadata"
RUN_ID_FILE = METADATA_DIR / "current_run_id.txt"
