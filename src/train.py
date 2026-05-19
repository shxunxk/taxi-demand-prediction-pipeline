import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error
from pathlib import Path
import pandas as pd
from pathlib import Path
import os
import sys
import mlflow
from datetime import datetime

RUN_ID_FILE = Path("metadata/current_run_id.txt")
def load_run_id() -> str:
    with open(RUN_ID_FILE, "r") as f:
        return f.read().strip()

id = load_run_id()

client = mlflow.tracking.MlflowClient()

train_path = client.download_artifacts(
    run_id=id,
    path="datasets/intermediate/trainData.parquet"
)

test_path = client.download_artifacts(
    run_id=id,
    path="datasets/intermediate/testData.parquet"
)

train = pd.read_parquet(train_path)
test = pd.read_parquet(test_path)

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
    "colsample_bytree": [0.8, 1.0]
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
    n_jobs=-1
)

search.fit(X_train, y_train)

best_model = search.best_estimator_

y_pred = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
print("MAE:", mae)

if(mae < req_accuracy):
    print(f"The model has low accuracy hence not saved")
    sys.exit(0)

print("Model accepted")

current_date = datetime.now()

year = current_date.year
month = current_date.month

if month == 12:
    year += 1
    month = 1
else:
    month += 1

OUTPUT_DIR = "models"
os.makedirs(OUTPUT_DIR, exist_ok=True)

joblib.dump(best_model, f"{OUTPUT_DIR}/demand_model_{year}-{month:02d}.pkl")

print("Model saved")