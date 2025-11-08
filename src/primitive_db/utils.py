import json
from pathlib import Path


def load_metadata(path: Path) -> dict:
    try:
        with open(path, mode="r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(path: Path, data: dict) -> None:
    with open(path, mode="w+") as f:
        f.write(json.dumps(data))
