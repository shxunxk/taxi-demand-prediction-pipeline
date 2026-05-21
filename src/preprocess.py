from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import boto3
from paths import METADATA_DIR, RUN_ID_FILE, WINDOW_DATA_DIR

def time_bucket(hour: int):
    if 0 <= hour <= 3:
        return 'latenight'
    elif 4 <= hour <= 6:
        return 'earlymorning'
    elif 7 <= hour <= 10:
        return 'morning'
    elif 11 <= hour <= 15:
        return 'afternoon'
    elif 16 <= hour <= 20:
        return 'evening'
    else:
        return 'night'

def preprocess(df):

    # datetime
    df["pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["hour"] = df["pickup_datetime"].dt.hour
    df["date"] = df["pickup_datetime"].dt.date

    df["time_bucket"] = df["hour"].apply(time_bucket)

    df.drop(columns=["hour", "pickup_datetime", "tpep_pickup_datetime"], inplace=True)

    # missing handling
    df.loc[df["passenger_count"] == 0.0, "passenger_count"] = np.nan
    df["passenger_count"] = df["passenger_count"].fillna(df["passenger_count"].median())

    df.loc[df["trip_distance"] == 0.0, "trip_distance"] = np.nan
    df["trip_distance"] = df["trip_distance"].fillna(df["trip_distance"].median())

    # aggregation
    agg_df = df.groupby(
        ["PULocationID", "date", "time_bucket"]
    ).agg(
        demand=("PULocationID", "size"),
        avg_passengers=("passenger_count", "mean"),
        avg_distance=("trip_distance", "mean")
    ).reset_index()

    agg_df["dayofweek"] = pd.to_datetime(agg_df["date"]).dt.dayofweek

    agg_df["loc_time"] = agg_df["PULocationID"].astype(str) + "_" + agg_df["time_bucket"]

    agg_df = agg_df.sort_values(["loc_time", "date"])

    # lag features
    agg_df["lag_1"] = agg_df.groupby("loc_time")["demand"].shift(1)
    agg_df["lag_2"] = agg_df.groupby("loc_time")["demand"].shift(2)
    agg_df["lag_7"] = agg_df.groupby("loc_time")["demand"].shift(7)

    # rolling
    agg_df["rolling_mean_3"] = agg_df.groupby("loc_time")["demand"].transform(
        lambda x: x.shift(1).rolling(3).mean()
    )

    agg_df["rolling_mean_7"] = agg_df.groupby("loc_time")["demand"].transform(
        lambda x: x.shift(1).rolling(7).mean()
    )

    agg_df["rolling_std_3"] = agg_df.groupby("loc_time")["demand"].transform(
        lambda x: x.shift(1).rolling(3).std()
    )

    agg_df["rolling_std_7"] = agg_df.groupby("loc_time")["demand"].transform(
        lambda x: x.shift(1).rolling(7).std()
    )

    agg_df = agg_df.dropna()

    agg_df["is_weekend"] = agg_df["dayofweek"].isin([5, 6]).astype(int)

    agg_df = pd.get_dummies(agg_df, columns=["time_bucket"], drop_first=True, dtype=int)

    freq = agg_df["PULocationID"].value_counts()
    agg_df["loc_freq"] = agg_df["PULocationID"].map(freq)

    agg_df = agg_df.drop(columns=["loc_time"])

    return agg_df

files = sorted(WINDOW_DATA_DIR.glob("*.parquet"))

if __name__ == "__main__":

    processed_list = []

    for i in files:
        df = pd.read_parquet(i, columns=["tpep_pickup_datetime", "PULocationID", "passenger_count", "trip_distance"])
        df = preprocess(df)
        processed_list.append(df)

    df = pd.concat(processed_list, ignore_index=True)
    df = df.sort_values("date")
    split_date = df["date"].quantile(0.8)

    train = df[df["date"] <= split_date]
    test = df[df["date"] > split_date]

    INTERMEDIATE_DIR = Path(os.environ.get("PIPELINE_TEMP_DIR", tempfile.gettempdir())) / "intermediate"

    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(INTERMEDIATE_DIR / "train.csv", index=False)
    test_df.to_csv(INTERMEDIATE_DIR / "test.csv", index=False)