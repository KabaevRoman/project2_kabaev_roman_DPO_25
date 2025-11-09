#!/usr/bin/env python3

import pprint
import shlex
from pathlib import Path

import prompt

from src.primitive_db.exceptions import TableExistsException, TableMissingException
from src.primitive_db.core import create_table, drop_table
from src.primitive_db.utils import load_metadata, save_metadata

METADATA_PATH = Path("metadata.json")


def help():
    print(
        """
***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> exit - выход из программы
<command> help - справочная информация 
    """
    )


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
            case "drop_table", name:
                try:
                    metadata = drop_table(metadata, name)
                except TableMissingException as err:
                    print(err.message)
                    continue
                print("table dropped")
            case ("list_tables",):
                pprint.pprint(metadata)
            case ("exit",):
                break
            case ("help",):
                help()
            case _:
                print("Команда с данными аргументами не существует")
                continue

        save_metadata(METADATA_PATH, metadata)
