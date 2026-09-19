from pathlib import Path
import boto3
from datetime import datetime
import tempfile
import os

WINDOW_DATA_DIR = Path(os.environ.get("PIPELINE_TEMP_DIR", tempfile.gettempdir())) / "windowData"
WINDOW_DATA_DIR.mkdir(parents=True, exist_ok=True)

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin"),
    aws_secret_access_key=os.environ.get(
        "AWS_SECRET_ACCESS_KEY", "change-me-root-minio"
    )
)

WINDOW_SIZE = 3
BUCKET_NAME = os.environ.get("MINIO_BUCKET_RAW", "taxi-raw")

# currentDate = datetime.now()
currentDate = datetime(2026, 4, 1)

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
            BUCKET_NAME,
            filename,
            str(local_path)
        )

        latest_files.append(local_path)

        print(f"Downloaded {filename}")

    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print(f"\nWindow updated with {len(latest_files)} file(s)")
print(f"Saved in: {WINDOW_DATA_DIR}")

if not latest_files:
    raise RuntimeError(
        f"No Parquet files were downloaded from s3://{BUCKET_NAME}. "
        "Upload the expected monthly files before running preprocessing."
    )