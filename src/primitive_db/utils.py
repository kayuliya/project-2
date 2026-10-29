import json


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла или возвращает пустой словарь."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}