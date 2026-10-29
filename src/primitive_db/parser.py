from primitive_db.constants import FALSE_WORD, QUOTES, TRUE_WORD


def find_outside_quotes(text, target, start=0):
    """Ищет target в тексте вне кавычек. Возвращает индекс или -1."""
    quote = None
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if char == quote:
                quote = None
        elif char in QUOTES:
            quote = char
        elif text.startswith(target, index):
            return index
    return -1


def split_outside_quotes(text, separator):
    """Делит текст по разделителю, игнорируя разделители внутри кавычек."""
    parts = []
    start = 0
    position = find_outside_quotes(text, separator, start)
    while position != -1:
        parts.append(text[start:position])
        start = position + len(separator)
        position = find_outside_quotes(text, separator, start)
    parts.append(text[start:])
    return parts


def parse_value(raw_value):
    """Превращает строку в str (в кавычках), bool или int."""
    text = raw_value.strip()
    if len(text) >= 2 and text[0] in QUOTES and text[-1] == text[0]:
        return text[1:-1]
    if text.lower() == TRUE_WORD:
        return True
    if text.lower() == FALSE_WORD:
        return False
    try:
        return int(text)
    except ValueError:
        raise ValueError(text) from None


def parse_values(text):
    """Разбирает строку вида '("Sergei", 28, true)' в список значений."""
    text = text.strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError(text)
    parts = split_outside_quotes(text[1:-1], ",")
    return [parse_value(part) for part in parts]


def parse_condition(text):
    """Разбирает 'age = 28' в пару (столбец, значение)."""
    position = find_outside_quotes(text, "=")
    column = text[:position].strip() if position != -1 else ""
    if not column:
        raise ValueError(text.strip())
    return column, parse_value(text[position + 1:])


def parse_where(text):
    """Разбирает условие where в словарь {столбец: значение}."""
    column, value = parse_condition(text)
    return {column: value}


def parse_set(text):
    """Разбирает 'a = 1, b = "x"' в словарь {столбец: значение}."""
    clause = {}
    for part in split_outside_quotes(text, ","):
        column, value = parse_condition(part)
        clause[column] = value
    return clause