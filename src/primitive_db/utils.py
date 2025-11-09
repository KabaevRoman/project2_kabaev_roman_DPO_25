import json
from pathlib import Path


def load_metadata(path: Path) -> dict:
    try:
        with open(path, mode="r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_metadata(path: Path, data: dict) -> None:
    with open(path, mode="w+") as f:
        json.dump(data, f)
        f.write(json.dumps(data))


def load_table_data(table_name: str) -> list[dict]:
    """Загружает данные таблицы из файла."""
    path = Path(f"{table_name}.json")
    try:
        with open(path, mode="r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет данные таблицы в файл."""
    path = Path(f"{table_name}.json")
    with open(path, mode="w+") as f:
        json.dump(data, f)
