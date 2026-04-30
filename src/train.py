import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error
from pathlib import Path
from preprocess import preprocess


path = "./data/yellow_tripdata_2026-02.parquet"

df = preprocess(path)

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




file_stem = Path(path).stem
name_suffix = file_stem.split("_")[-1]

joblib.dump(best_model, f"models/demand_model_{name_suffix}.pkl")