import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error
from pathlib import Path
from preprocess import preprocess
import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "windowData"

files = sorted(DATA_DIR.glob("*.parquet"))

processed_list = []

for i in files:
    df = pd.read_parquet(i, columns=["tpep_pickup_datetime", "PULocationID", "passenger_count", "trip_distance"])
    df = preprocess(df)
    processed_list.append(df)

df = pd.concat(processed_list, ignore_index=True)

# sort for safety
df = df.sort_values("date")

split_date = df["date"].quantile(0.8)

train = df[df["date"] <= split_date]
test = df[df["date"] > split_date]

X_train = train.drop(columns=["demand", "date"])
y_train = train["demand"]

X_test = test.drop(columns=["demand", "date"])
y_test = test["demand"]




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

print("Ratio:", mae / y_test.mean())




year, month = map(int, files[-1].stem.split("_")[-1].split('.')[0].split('-'))

if month == 12:
    year += 1
    month = 1
else:
    month += 1

joblib.dump(best_model, f"models/demand_model_{year}-{month:02d}.pkl")