import prompt

from primitive_db.constants import CONFIRM_ANSWER


def copy_metadata(wrapper, func):
    """Переносит имя и описание исходной функции на обертку."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_db_errors(func):
    """Перехватывает типичные ошибки базы данных и печатает сообщение."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных "
                  "не инициализирована.")
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")

    return copy_metadata(wrapper, func)


def confirm_action(action_name):
    """Фабрика декораторов: просит подтвердить опасную операцию.

    При отказе возвращает первый аргумент без изменений.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            answer = prompt.string(question)
            if answer.strip().lower() == CONFIRM_ANSWER:
                return func(*args, **kwargs)
            print("Операция отменена.")
            return args[0] if args else None

        return copy_metadata(wrapper, func)

    return decorator