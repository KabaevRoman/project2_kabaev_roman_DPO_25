def parse_value(value_str: str):
    """Преобразует строковое значение в соответствующий тип Python."""
    value_str = value_str.strip()
    
    # Проверяем, является ли значение строкой в кавычках
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]  # Убираем кавычки
    
    # Проверяем на булево значение
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False
    
    # Пробуем преобразовать в число
    try:
        if "." in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        # Если не число, возвращаем как строку
        return value_str


def parse_where_clause(where_str: str) -> dict:
    """
    Парсит WHERE условие и возвращает словарь.
    Пример: "age = 28" -> {'age': 28}
    Пример: "name = 'John'" -> {'name': 'John'}
    """
    if not where_str:
        return {}
    
    conditions = {}
    # Разбиваем по AND (простая версия)
    parts = where_str.split(" AND ")
    
    for part in parts:
        part = part.strip()
        if " = " in part:
            key, value = part.split(" = ", 1)
            key = key.strip()
            value = value.strip()
            conditions[key] = parse_value(value)
    
    return conditions


def parse_set_clause(set_str: str) -> dict:
    """
    Парсит SET условие и возвращает словарь.
    Пример: "age = 29" -> {'age': 29}
    Пример: "name = 'Jane', age = 30" -> {'name': 'Jane', 'age': 30}
    """
    if not set_str:
        return {}
    
    updates = {}
    # Разбиваем по запятым
    parts = set_str.split(",")
    
    for part in parts:
        part = part.strip()
        if " = " in part:
            key, value = part.split(" = ", 1)
            key = key.strip()
            value = value.strip()
            updates[key] = parse_value(value)
    
    return updates
