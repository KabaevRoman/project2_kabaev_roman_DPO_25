from typing import NamedTuple, TypedDict

from src.primitive_db import constants
from src.primitive_db.exceptions import (
    InvalidTypeException,
    TableExistsException,
    TableMissingException,
)
from src.primitive_db.types import ColumnType


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


# def drop_table(metadata: Metadata)
