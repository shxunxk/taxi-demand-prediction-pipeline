from pathlib import Path
import shutil
import boto3
from datetime import datetime

from paths import RAW_DATA_DIR, WINDOW_DATA_DIR


s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="change-me-root-minio"
)

WINDOW_SIZE = 3
BUCKET_NAME = "taxi-raw"

currentDate = datetime.now()

month = currentDate.month
year = currentDate.year

# Clear old window files
for f in WINDOW_DATA_DIR.glob("*.parquet"):
    f.unlink()

latest_files = []

for i in range(WINDOW_SIZE):

    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1

    filename = f"{year}-{month:02d}.parquet"

    try:

        local_path = WINDOW_DATA_DIR / filename

        s3.download_file(
            BUCKET_NAME,     # bucket
            filename,        # object key
            str(local_path)  # local destination
        )

        latest_files.append(local_path)

        print(f"Downloaded {filename}")

    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print(f"\nWindow updated with {len(latest_files)} file(s)")
print(f"Saved in: {WINDOW_DATA_DIR}")