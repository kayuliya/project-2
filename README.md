## Управление таблицами

Команды:
- `create_table <имя> <столбец:тип> ...` — создать таблицу (типы: int, str, bool; столбец ID:int добавляется автоматически)
- `list_tables` — список таблиц
- `drop_table <имя>` — удалить таблицу
- `help`, `exit`

Демонстрация:

[![asciicast](https://asciinema.org/a/H6QNdV4KBG4p2NKl.svg)](https://asciinema.org/a/H6QNdV4KBG4p2NKl)

## CRUD-операции

- `insert into <таблица> values (<значение1>, <значение2>, ...)` — создать запись (ID задается автоматически, строки в кавычках)
- `select from <таблица>` — вывести все записи
- `select from <таблица> where <столбец> = <значение>` — вывести записи по условию
- `update <таблица> set <столбец> = <значение> where <столбец> = <значение>` — обновить записи
- `delete from <таблица> where <столбец> = <значение>` — удалить записи
- `info <таблица>` — информация о таблице

Пример:

    insert into users values ("Sergei", 28, true)
    select from users where age = 28
    update users set age = 29 where name = "Sergei"
    delete from users where ID = 1
    info users