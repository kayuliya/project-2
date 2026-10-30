from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

PYTHON_TYPES = {"int": int, "str": str, "bool": bool}
cache_result = create_cacher()

def table_exists(metadata, table_name):
    """Проверяет наличие таблицы; при отсутствии печатает ошибку."""
    if table_name in metadata:
        return True
    print(f'Ошибка: Таблица "{table_name}" не существует.')
    return False


def is_valid_type(value, column_type):
    """Проверяет, что значение соответствует типу столбца."""
    if column_type == "int" and isinstance(value, bool):
        return False
    return isinstance(value, PYTHON_TYPES[column_type])


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие."""
    return all(record[column] == value for column, value in where_clause.items())


def find_records(table_data, where_clause=None):
    """Возвращает записи, подходящие под условие (все, если условия нет)."""
    if where_clause is None:
        return list(table_data)
    return [record for record in table_data if matches(record, where_clause)]

@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает таблицу, добавляя столбец ID:int, и возвращает метаданные."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    table_columns = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, separator, column_type = column.partition(":")
        if not separator or not name or name in table_columns:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata
        if column_type not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata
        table_columns[name] = column_type
    updated = dict(metadata)
    updated[table_name] = table_columns
    return updated

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает обновленные метаданные."""
    if not table_exists(metadata, table_name):
        return metadata
    updated = dict(metadata)
    del updated[table_name]
    return updated

@handle_db_errors
def validate_clause(metadata, table_name, clause, forbid_id=False):
    """Проверяет столбцы и типы значений условия. Возвращает True при успехе."""
    schema = metadata[table_name]
    for column, value in clause.items():
        column_type = schema[column]
        if forbid_id and column == ID_COLUMN:
            raise ValueError("столбец ID изменять нельзя")
        if not is_valid_type(value, column_type):
            raise ValueError(f"значение {value!r} не подходит для {column}")
    return True

@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавляет запись с новым ID и возвращает обновленные данные таблицы."""
    columns = [
        (name, column_type)
        for name, column_type in metadata[table_name].items()
        if name != ID_COLUMN
    ]
    if len(values) != len(columns):
        raise ValueError(f"ожидалось значений: {len(columns)}, получено: {len(values)}")
    last_id = max((record[ID_COLUMN] for record in table_data), default=0)
    record = {ID_COLUMN: last_id + 1}
    for (name, column_type), value in zip(columns, values):
        if not is_valid_type(value, column_type):
            raise ValueError(f"значение {value!r} не подходит для {name}:{column_type}")
        record[name] = value
    return table_data + [record]

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи по условию; одинаковые запросы берутся из кэша."""
    key = str((table_data, where_clause))
    return cache_result(key, lambda: find_records(table_data, where_clause))


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет поля у подходящих записей и возвращает данные таблицы."""
    return [
        {**record, **set_clause} if matches(record, where_clause) else record
        for record in table_data
    ]

@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет подходящие записи и возвращает данные таблицы."""
    return [record for record in table_data if not matches(record, where_clause)]