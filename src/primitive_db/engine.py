import shlex

import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import (
    HELP_LINES,
    ID_COLUMN,
    META_FILE,
    PROMPT_TEXT,
    WHERE_KEYWORD,
)
from primitive_db.parser import (
    find_outside_quotes,
    parse_set,
    parse_values,
    parse_where,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Печатает справочную информацию."""
    for line in HELP_LINES:
        print(line)


def print_invalid_value(value):
    """Сообщает о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def format_columns(columns):
    """Форматирует схему таблицы как 'ID:int, name:str'."""
    return ", ".join(f"{name}:{column_type}" for name, column_type in columns.items())


def print_records(columns, records):
    """Печатает записи в виде таблицы prettytable."""
    if not records:
        print("Записи не найдены.")
        return
    table = PrettyTable()
    table.field_names = list(columns)
    for record in records:
        table.add_row([record[column] for column in columns])
    print(table)


def handle_create_table(metadata, args):
    """Обрабатывает create_table."""
    if len(args) < 3:
        print_invalid_value(" ".join(args))
        return
    table_name = args[1]
    updated = core.create_table(metadata, table_name, args[2:])
    if updated is None or updated == metadata:
        return
    save_metadata(META_FILE, updated)
    columns = format_columns(updated[table_name])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns}')


def handle_drop_table(metadata, args):
    """Обрабатывает drop_table."""
    if len(args) != 2:
        print_invalid_value(" ".join(args))
        return
    table_name = args[1]
    if not core.table_exists(metadata, table_name):
        return
    updated = core.drop_table(metadata, table_name)
    if updated is None or updated == metadata:
        return
    save_metadata(META_FILE, updated)
    delete_table_data(table_name)
    print(f'Таблица "{table_name}" успешно удалена.')


def handle_list_tables(metadata):
    """Обрабатывает list_tables."""
    if not metadata:
        print("Таблиц пока нет.")
    for table_name in metadata:
        print(f"- {table_name}")


def handle_info(metadata, args):
    """Обрабатывает info."""
    if len(args) != 2:
        print_invalid_value(" ".join(args))
        return
    table_name = args[1]
    if not core.table_exists(metadata, table_name):
        return
    count = len(load_table_data(table_name))
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {format_columns(metadata[table_name])}")
    print(f"Количество записей: {count}")


def handle_insert(metadata, user_input):
    """Обрабатывает insert into <таблица> values (...)."""
    parts = user_input.split(maxsplit=4)
    if len(parts) != 5 or parts[1] != "into" or parts[3] != "values":
        print_invalid_value(user_input)
        return
    table_name = parts[2]
    values = parse_values(parts[4])
    if not core.table_exists(metadata, table_name):
        return
    new_data = core.insert(metadata, table_name, values, load_table_data(table_name))
    if new_data is None:
        return
    save_table_data(table_name, new_data)
    new_id = new_data[-1][ID_COLUMN]
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


def handle_select(metadata, user_input):
    """Обрабатывает select from <таблица> [where ...]."""
    parts = user_input.split(maxsplit=4)
    if len(parts) not in (3, 5) or parts[1] != "from":
        print_invalid_value(user_input)
        return
    where_clause = None
    if len(parts) == 5:
        if parts[3] != "where":
            print_invalid_value(user_input)
            return
        where_clause = parse_where(parts[4])
    table_name = parts[2]
    if not core.table_exists(metadata, table_name):
        return
    if where_clause and not core.validate_clause(metadata, table_name, where_clause):
        return
    records = core.select(load_table_data(table_name), where_clause)
    if records is not None:
        print_records(metadata[table_name], records)


def handle_update(metadata, user_input):
    """Обрабатывает update <таблица> set ... where ..."""
    parts = user_input.split(maxsplit=3)
    if len(parts) != 4 or parts[2] != "set":
        print_invalid_value(user_input)
        return
    position = find_outside_quotes(parts[3], WHERE_KEYWORD)
    if position == -1:
        print_invalid_value(user_input)
        return
    set_clause = parse_set(parts[3][:position])
    where_clause = parse_where(parts[3][position + len(WHERE_KEYWORD):])
    table_name = parts[1]
    if not core.table_exists(metadata, table_name):
        return
    if not core.validate_clause(metadata, table_name, where_clause):
        return
    if not core.validate_clause(metadata, table_name, set_clause, forbid_id=True):
        return
    table_data = load_table_data(table_name)
    targets = core.find_records(table_data, where_clause)
    if not targets:
        print("Записи, подходящие под условие, не найдены.")
        return
    save_table_data(table_name, core.update(table_data, set_clause, where_clause))
    for record in targets:
        print(f'Запись с ID={record[ID_COLUMN]} в таблице "{table_name}" '
              "успешно обновлена.")


def handle_delete(metadata, user_input):
    """Обрабатывает delete from <таблица> where ..."""
    parts = user_input.split(maxsplit=4)
    if len(parts) != 5 or parts[1] != "from" or parts[3] != "where":
        print_invalid_value(user_input)
        return
    table_name = parts[2]
    where_clause = parse_where(parts[4])
    if not core.table_exists(metadata, table_name):
        return
    if not core.validate_clause(metadata, table_name, where_clause):
        return
    table_data = load_table_data(table_name)
    targets = core.find_records(table_data, where_clause)
    if not targets:
        print("Записи, подходящие под условие, не найдены.")
        return
    new_data = core.delete(table_data, where_clause)
    if new_data is None or len(new_data) == len(table_data):
        return
    save_table_data(table_name, new_data)
    for record in targets:
        print(f'Запись с ID={record[ID_COLUMN]} успешно удалена '
              f'из таблицы "{table_name}".')


def execute(metadata, user_input):
    """Выполняет одну команду. Возвращает False, если нужно выйти."""
    args = shlex.split(user_input)
    if not args:
        return True
    match args[0]:
        case "exit":
            return False
        case "help":
            print_help()
        case "create_table":
            handle_create_table(metadata, args)
        case "drop_table":
            handle_drop_table(metadata, args)
        case "list_tables":
            handle_list_tables(metadata)
        case "info":
            handle_info(metadata, args)
        case "insert":
            handle_insert(metadata, user_input)
        case "select":
            handle_select(metadata, user_input)
        case "update":
            handle_update(metadata, user_input)
        case "delete":
            handle_delete(metadata, user_input)
        case _:
            print(f"Функции {args[0]} нет. Попробуйте снова.")
    return True


def run():
    """Главный цикл: читает команды, пока пользователь не введет exit."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = prompt.string(PROMPT_TEXT)
            if not execute(metadata, user_input):
                break
        except ValueError as error:
            print_invalid_value(error)
        except (EOFError, KeyboardInterrupt):
            print()
            break