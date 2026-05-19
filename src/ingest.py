from pathlib import Path
import shutil

RAW_DIR = Path("data")
WINDOW_DIR = Path("windowData")
WINDOW_SIZE = 3

files = sorted(RAW_DIR.glob("*.parquet"))

latest_files = files[-WINDOW_SIZE:]

for f in WINDOW_DIR.glob("*.parquet"):
    f.unlink()

for f in latest_files:
    shutil.copy(f, WINDOW_DIR / f.name)