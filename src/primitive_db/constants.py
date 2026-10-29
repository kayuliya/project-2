META_FILE = "db_meta.json"
DATA_DIR = "data"

ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = ("int", "str", "bool")

PROMPT_TEXT = "Введите команду: "

CONFIRM_ANSWER = "y"

QUOTES = ('"', "'")
WHERE_KEYWORD = " where "
TRUE_WORD = "true"
FALSE_WORD = "false"

HELP_LINES = (
    "\n***Операции с данными***",
    "Функции:",
    "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу",
    "<command> list_tables - показать список всех таблиц",
    "<command> drop_table <имя_таблицы> - удалить таблицу",
    "<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись",
    "<command> select from <имя_таблицы> - прочитать все записи",
    "<command> select from <имя_таблицы> where <столбец> = <значение> - "
    "прочитать записи по условию",
    "<command> update <имя_таблицы> set <столбец> = <значение> "
    "where <столбец> = <значение> - обновить запись",
    "<command> delete from <имя_таблицы> where <столбец> = <значение> - "
    "удалить запись",
    "<command> info <имя_таблицы> - вывести информацию о таблице",
    "\nОбщие команды:",
    "<command> exit - выход из программы",
    "<command> help - справочная информация\n",
)