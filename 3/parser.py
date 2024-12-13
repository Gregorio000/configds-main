import json
import re

class ParsingError(Exception):
    pass

def parse(input_text):
    # Удаление комментариев
    input_text = re.sub(r'//.*', '', input_text).strip()
    
    # Проверка на пустой ввод
    if not input_text:
        raise ParsingError("Input is empty")

    # Разбор массивов
    arrays = re.findall(r'\{(.*?)\}', input_text)
    parsed_arrays = [parse_array(arr) for arr in arrays]

    # Разбор значений и констант
    values = []
    for line in input_text.splitlines():
        line = line.strip()
        if '->' in line:
            name, value = line.split('->', 1)
            values.append((name.strip(), value.strip()))
        else:
            values.extend(re.split(r'\s+', line))

    # Преобразование в JSON
    result = {
        "arrays": parsed_arrays,
        "values": values
    }
    
    return json.dumps(result, indent=4)

def parse_array(array_text):
    # Разделение значений массива по точкам
    items = [item.strip() for item in array_text.split('.') if item.strip()]
    return items

def evaluate_expression(expression):
    # Простой парсер для вычисления выражений в префиксной форме
    tokens = expression.split()
    if not tokens:
        raise ParsingError("Empty expression")

    operator = tokens[0]
    if operator == '+':
        return sum(evaluate_expression(token) for token in tokens[1:])
    elif operator == '-':
        return evaluate_expression(tokens[1]) - sum(evaluate_expression(token) for token in tokens[2:])
    elif operator == '*':
        result = 1
        for token in tokens[1:]:
            result *= evaluate_expression(token)
        return result
    elif operator == 'mod':
        return evaluate_expression(tokens[1]) % evaluate_expression(tokens[2])
    else:
        # Проверка на константы
        return evaluate_constant(operator)

def evaluate_constant(name):
    # Здесь вы можете добавить логику для получения значения константы
    constants = {'A': 10, 'B': 15}  # Пример значений констант
    return constants.get(name, 0)

# Пример использования
if __name__ == "__main__":
    input_text = """
    // Пример конфигурации
    { 1. 2. 3. }
    A -> 10
    B -> $(+ A 5)
    """
    try:
        output_json = parse(input_text)
        print(output_json)
    except ParsingError as e:
        print(f"Error: {e}")