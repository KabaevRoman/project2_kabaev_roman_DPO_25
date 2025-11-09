import copy
from typing import Any, NamedTuple, TypedDict

from src.primitive_db import constants
from src.primitive_db.exceptions import (
    InvalidTypeException,
    InvalidValueCountException,
    InvalidValueTypeException,
    TableExistsException,
    TableMissingException,
)
from src.primitive_db.types import ColumnType
from src.primitive_db.utils import load_table_data

SEQUENCE_PATH_TEMPLATE = "data/sequence_{table_name}"


class Column(NamedTuple):
    name: str
    type: ColumnType


class Table(TypedDict):
    columns: dict[str, ColumnType]


Metadata = dict[str, Table]


def parse_cols(*cols: str) -> dict[str, ColumnType]:
    parsed_columns = {}
    for col in cols:
        col_name, col_type = col.split(":")
        if col_type not in constants.VALID_TYPES:
            raise InvalidTypeException
        parsed_columns[col_name] = col_type
    return parsed_columns


def create_table(metadata: Metadata, table_name: str, *columns: str) -> Metadata:
    if metadata.get(table_name) is not None:
        raise TableExistsException

    parsed_cols = parse_cols("ID:int", *columns)
    metadata[table_name] = {"columns": parsed_cols}

    return metadata


def drop_table(metadata: Metadata, table_name: str) -> Metadata:
    table = metadata.get(table_name)
    if table is None:
        raise TableMissingException

    metadata.pop(table_name)

    return metadata


def validate_value_type(value, expected_type: ColumnType, column_name: str):
    """Валидирует тип значения."""
    if expected_type == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidValueTypeException(column_name, expected_type)
    elif expected_type == "str":
        if not isinstance(value, str):
            raise InvalidValueTypeException(column_name, expected_type)
    elif expected_type == "bool":
        if not isinstance(value, bool):
            raise InvalidValueTypeException(column_name, expected_type)


def _get_next_id(table_name: str) -> int:
    with open(SEQUENCE_PATH_TEMPLATE.format(table_name=table_name), mode="r+") as f:
        next_id_str = f.read()
        if next_id_str is None:
            next_id = "1"

        next_id = int(next_id_str)
        f.seek(0)
        f.truncate()
        f.write(str(next_id+1))

        return next_id


def insert(metadata: Metadata, table_name: str, values: list) -> list[dict]:
    """
    Вставляет новую запись в таблицу.

    Args:
        metadata: Метаданные базы данных
        table_name: Имя таблицы
        values: Список значений (без ID)

    Returns:
        Обновленные данные таблицы
    """
    table = metadata.get(table_name)
    if table is None:
        raise TableMissingException

    columns = copy.deepcopy(table["columns"])
    columns.pop("ID")

    if len(values) != len(columns):
        raise InvalidValueCountException

    table_data = load_table_data(table_name)
    new_id = _get_next_id(table_name)
    new_record = {"ID": new_id}

    for i, (col_name, col_type) in enumerate(columns.items()):
        validate_value_type(values[i], col_type, col_name)
        new_record[col_name] = values[i]

    table_data.append(new_record)

    return table_data


def select(table_data: list[dict], where_clause: dict[str, Any] | None = None) -> list[dict]:
    """
    Выбирает записи из таблицы.

    Args:
        table_data: Данные таблицы
        where_clause: Условие фильтрации (например, {'age': 28})

    Returns:
        Отфильтрованные записи
    """
    if where_clause is None or not where_clause:
        return table_data

    def clause(val: dict):
        return all(list(val.get(key) == value for key, value in where_clause.items()))

    return list(filter(clause, table_data))


def update(
    table_data: list[dict], set_clause: dict, where_clause: dict | None = None
) -> list[dict]:
    """
    Обновляет записи в таблице.

    Args:
        table_data: Данные таблицы
        set_clause: Словарь обновлений (например, {'age': 29})
        where_clause: Условие фильтрации

    Returns:
        Обновленные данные таблицы
    """
    for record in table_data:
        # Проверяем, подходит ли запись под условие
        match = True
        if where_clause:
            for key, value in where_clause.items():
                if record.get(key) != value:
                    match = False
                    break

        # Если подходит, обновляем
        if match:
            for key, value in set_clause.items():
                if key in record:  # Обновляем только существующие поля
                    record[key] = value

    return table_data


def delete(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """
    Удаляет записи из таблицы.

    Args:
        table_data: Данные таблицы
        where_clause: Условие фильтрации

    Returns:
        Обновленные данные таблицы
    """
    if where_clause is None or not where_clause:
        # Если условие не указано, удаляем все записи
        return []

    # Фильтруем записи, оставляя только те, что НЕ соответствуют условию
    result = []
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if record.get(key) != value:
                match = False
                break
        if not match:  # Оставляем записи, которые НЕ соответствуют условию
            result.append(record)

    return result
