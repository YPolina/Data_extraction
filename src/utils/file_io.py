import shutil
from pathlib import Path

def recreate_dir(path: str | Path):
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)   # remove the folder and everything inside
    path.mkdir(parents=True, exist_ok=True)  # create a fresh empty one
