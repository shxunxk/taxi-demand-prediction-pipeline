import sys
from datetime import datetime
from pathlib import Path
import os
import tempfile
import shutil
import joblib
import mlflow
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from xgboost import XGBRegressor


INTERMEDIATE_DIR = Path(
    os.environ.get("PIPELINE_TEMP_DIR", tempfile.gettempdir())
) / "intermediate"

train = pd.read_csv(INTERMEDIATE_DIR / "train.csv")
test = pd.read_csv(INTERMEDIATE_DIR / "test.csv")

X_train = train.drop(columns=["demand", "date"])
y_train = train["demand"]

X_test = test.drop(columns=["demand", "date"])
y_test = test["demand"]

req_accuracy = 20

param_dist = {
    "n_estimators": [100, 200, 300],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

tscv = TimeSeriesSplit(n_splits=3)
model = XGBRegressor(random_state=42)

search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_dist,
    n_iter=10,
    cv=tscv,
    scoring="neg_mean_absolute_error",
    verbose=1,
    n_jobs=-1,
)

search.fit(X_train, y_train)
best_model = search.best_estimator_

y_pred = best_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print("MAE:", mae)

if mae < req_accuracy:
    print("The model has low accuracy hence not saved")
    sys.exit(0)

print("Model accepted")

current_date = datetime.now()
year = current_date.year
month = current_date.month

MODELS_DIR = Path(os.environ.get("PIPELINE_TEMP_DIR", tempfile.gettempdir())) / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(best_model, MODELS_DIR / f"demand_model_{year}-{month:02d}.pkl")

print(f"Model saved to {MODELS_DIR}")
WINDOW_DATA_DIR = Path(os.environ.get("PIPELINE_TEMP_DIR", tempfile.gettempdir())) / "windowData"

shutil.rmtree(INTERMEDIATE_DIR, ignore_errors=True)
shutil.rmtree(WINDOW_DATA_DIR, ignore_errors=True)