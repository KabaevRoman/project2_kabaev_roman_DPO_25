from typing import NamedTuple, TypedDict

from primitive_db import constants
from primitive_db.exceptions import InvalidTypeException, TableExistsException
from primitive_db.types import ColumnType


class Column(NamedTuple):
    name: str
    type: ColumnType


class Table(TypedDict):
    columns: dict[str, ColumnType]


Metadata = dict[str, Table]


def parse_cols(cols: set[str]) -> set[Column]:
    parsed_cols = set()
    for col in cols:
        col_name, col_type = col.split(":")
        if col_type not in constants.VALID_TYPES:
            raise InvalidTypeException
        parsed_cols.add(Column(col_name, col_type))
    return parsed_cols


def create_table(metadata: Metadata, table_name: str, columns: set[str]) -> dict:
    if metadata.get(table_name) is not None:
        raise TableExistsException

    columns.add("ID:int")
    parsed_cols = parse_cols(columns)
    metadata[] = parsed_cols

    return metadata


# def drop_table(metadata: Metadata)
