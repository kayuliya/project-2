import shlex

import prompt

from primitive_db import core
from primitive_db.constants import META_FILE, PROMPT_TEXT
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_invalid_value(value):
    """Сообщает о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def format_columns(columns):
    """Форматирует схему таблицы как 'ID:int, name:str'."""
    return ", ".join(f"{name}:{column_type}" for name, column_type in columns.items())


def handle_create_table(metadata, args):
    """Обрабатывает create_table."""
    if len(args) < 3:
        print_invalid_value(" ".join(args))
        return
    table_name = args[1]
    updated = core.create_table(metadata, table_name, args[2:])
    if updated == metadata:
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
    save_metadata(META_FILE, updated)
    print(f'Таблица "{table_name}" успешно удалена.')


def handle_list_tables(metadata):
    """Обрабатывает list_tables."""
    if not metadata:
        print("Таблиц пока нет.")
    for table_name in metadata:
        print(f"- {table_name}")


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