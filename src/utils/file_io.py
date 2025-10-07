import shutil
from pathlib import Path

def recreate_dir(path: str | Path) -> None:
    """
    Recreate a directory by deleting it if it exists and then creating it again.

    Args:
        path (str | Path): Path to the directory.

    Returns:
        None
    """
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
