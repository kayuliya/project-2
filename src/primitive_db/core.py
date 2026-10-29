from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def table_exists(metadata, table_name):
    """Проверяет наличие таблицы; при отсутствии печатает ошибку."""
    if table_name in metadata:
        return True
    print(f'Ошибка: Таблица "{table_name}" не существует.')
    return False

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

def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает обновленные метаданные."""
    if not table_exists(metadata, table_name):
        return metadata
    updated = dict(metadata)
    del updated[table_name]
    return updated