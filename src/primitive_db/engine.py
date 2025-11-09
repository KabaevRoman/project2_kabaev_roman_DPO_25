#!/usr/bin/env python3

import pprint
import shlex
from pathlib import Path

import prompt
from prettytable import PrettyTable

from src.primitive_db.core import create_table, delete, drop_table, insert, select, update
from src.primitive_db.exceptions import (
    InvalidValueCountException,
    InvalidValueTypeException,
    TableExistsException,
    TableMissingException,
)
from src.primitive_db.parser import parse_set_clause, parse_where_clause
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_PATH = Path("metadata.json")


def help():
    print(
        """
***Процесс работы с таблицей***
Функции управления таблицами:
  create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
  list_tables - показать список всех таблиц
  drop_table <имя_таблицы> - удалить таблицу

CRUD-операции:
  insert <имя_таблицы> <значение1> <значение2> ... - вставить запись
    Пример: insert users "John" 28 true
  
  select <имя_таблицы> [where <условие>] - выбрать записи
    Пример: select users
    Пример: select users where age = 28
    Пример: select users where name = "John" AND age = 28
  
  update <имя_таблицы> set <изменения> [where <условие>] - обновить записи
    Пример: update users set age = 29 where name = "John"
    Пример: update users set age = 30, active = false where ID = 1
  
  delete <имя_таблицы> [where <условие>] - удалить записи
    Пример: delete users where age = 28
    Пример: delete users where name = "John"

Другие команды:
  exit - выход из программы
  help - справочная информация

Примечание: Строковые значения должны быть в кавычках ("John" или 'John')
    """
    )


def display_table(data: list[dict], table_name: str = "Results"):
    """Отображает данные в виде таблицы с использованием prettytable."""
    if not data:
        print(f"No records found in {table_name}")
        return
    
    # Создаем таблицу
    table = PrettyTable()
    
    # Получаем имена столбцов из первой записи
    columns = list(data[0].keys())
    table.field_names = columns
    
    # Добавляем строки
    for record in data:
        table.add_row([record.get(col, "") for col in columns])
    
    print(table)


def run():
    print("Simple database shell")
    help()

    while True:
        metadata = load_metadata(METADATA_PATH)
        command = prompt.string("Введите команду: ")

        if command is None:
            print("Invalid command provided")
            continue

        cmd = shlex.split(command)
        match cmd:
            case "create_table", name, *cols:
                try:
                    metadata = create_table(metadata, name, *cols)
                except TableExistsException as err:
                    print(err.message)
                    continue
                print("table created")
                save_metadata(METADATA_PATH, metadata)
                
            case "drop_table", name:
                try:
                    metadata = drop_table(metadata, name)
                except TableMissingException as err:
                    print(err.message)
                    continue
                print("table dropped")
                save_metadata(METADATA_PATH, metadata)
                # Удаляем файл с данными таблицы
                try:
                    Path(f"{name}.json").unlink()
                except FileNotFoundError:
                    pass
                    
            case ("list_tables",):
                pprint.pprint(metadata)
                
            case "insert", table_name, *values:
                try:
                    # Парсим значения
                    from src.primitive_db.parser import parse_value
                    parsed_values = [parse_value(v) for v in values]
                    
                    # Вставляем запись
                    table_data = insert(metadata, table_name, parsed_values)
                    save_table_data(table_name, table_data)
                    print(f"Record inserted with ID = {table_data[-1]['ID']}")
                except TableMissingException as err:
                    print(err.message)
                except InvalidValueCountException as err:
                    print(err.message)
                except InvalidValueTypeException as err:
                    print(err.message)
                    
            case "select", table_name, *rest:
                try:
                    table_data = load_table_data(table_name)
                    
                    # Проверяем наличие WHERE
                    where_clause = None
                    if rest and rest[0] == "where":
                        # Объединяем все части после "where"
                        where_str = " ".join(rest[1:])
                        where_clause = parse_where_clause(where_str)
                    
                    # Выполняем выборку
                    results = select(table_data, where_clause)
                    display_table(results, table_name)
                except Exception as err:
                    print(f"Error: {err}")
                    
            case "update", table_name, "set", *rest:
                try:
                    table_data = load_table_data(table_name)
                    
                    # Ищем позицию "where"
                    where_index = -1
                    for i, token in enumerate(rest):
                        if token == "where":
                            where_index = i
                            break
                    
                    # Парсим SET и WHERE
                    if where_index > 0:
                        set_str = " ".join(rest[:where_index])
                        where_str = " ".join(rest[where_index + 1:])
                        where_clause = parse_where_clause(where_str)
                    else:
                        set_str = " ".join(rest)
                        where_clause = None
                    
                    set_clause = parse_set_clause(set_str)
                    
                    # Выполняем обновление
                    updated_data = update(table_data, set_clause, where_clause)
                    save_table_data(table_name, updated_data)
                    print("Records updated")
                except Exception as err:
                    print(f"Error: {err}")
                    
            case "delete", table_name, *rest:
                try:
                    table_data = load_table_data(table_name)
                    
                    # Проверяем наличие WHERE
                    where_clause = None
                    if rest and rest[0] == "where":
                        where_str = " ".join(rest[1:])
                        where_clause = parse_where_clause(where_str)
                    
                    # Выполняем удаление
                    updated_data = delete(table_data, where_clause)
                    save_table_data(table_name, updated_data)
                    
                    deleted_count = len(table_data) - len(updated_data)
                    print(f"{deleted_count} record(s) deleted")
                except Exception as err:
                    print(f"Error: {err}")
                    
            case ("exit",):
                break
                
            case ("help",):
                help()
                
            case _:
                print("Команда с данными аргументами не существует")
                continue
