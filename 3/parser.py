#!/usr/bin/env python3
import sys
import json
import re
from typing import Any, Dict, List, Union

class ConfigParser:
    def __init__(self):
        self.constants: Dict[str, Any] = {}
        self.current_line = 0
        self.lines: List[str] = []

    def parse_value(self, value: str) -> Union[int, List[Any]]:
        value = value.strip()
        # Try to parse as number
        try:
            return int(value)
        except ValueError:
            pass

        # Try to parse as array
        if value.startswith('{') and value.endswith('}'):
            array_content = value[1:-1].strip()
            if not array_content:
                return []
            elements = [elem.strip() for elem in array_content.split('.') if elem.strip()]
            return [self.parse_value(elem) for elem in elements]

        # Try to parse as constant expression
        if value.startswith('$(') and value.endswith(')'):
            return self.evaluate_expression(value[2:-1].strip())

        # Try to get constant value
        if value.isalpha() and value.isupper():
            if value not in self.constants:
                raise SyntaxError(f"Undefined constant: {value}")
            return self.constants[value]

        raise SyntaxError(f"Invalid value format: {value}")

    def evaluate_expression(self, expr: str) -> int:
        tokens = expr.split()
        if not tokens:
            raise SyntaxError("Empty expression")

        operator = tokens[0]
        operands = tokens[1:]

        if len(operands) != 2:
            raise SyntaxError(f"Expression requires exactly 2 operands: {expr}")

        # Evaluate operands
        values = []
        for operand in operands:
            if operand.isalpha() and operand.isupper():
                if operand not in self.constants:
                    raise SyntaxError(f"Undefined constant: {operand}")
                values.append(self.constants[operand])
            else:
                try:
                    values.append(int(operand))
                except ValueError:
                    raise SyntaxError(f"Invalid operand: {operand}")

        # Apply operator
        if operator == '+':
            return values[0] + values[1]
        elif operator == '-':
            return values[0] - values[1]
        elif operator == '*':
            return values[0] * values[1]
        elif operator == 'mod':
            if values[1] == 0:
                raise ValueError("Division by zero in mod operation")
            return values[0] % values[1]
        else:
            raise SyntaxError(f"Unknown operator: {operator}")

    def parse_line(self, line: str) -> Dict[str, Any]:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            return {}

        # Parse constant declaration
        if '->' in line:
            value_str, name = map(str.strip, line.split('->'))
            if not name.isalpha() or not name.isupper():
                raise SyntaxError(f"Invalid constant name: {name}")
            value = self.parse_value(value_str)
            self.constants[name] = value
            return {'type': 'constant_declaration', 'name': name, 'value': value}

        # Parse value
        try:
            value = self.parse_value(line)
            return {'type': 'value', 'value': value}
        except SyntaxError as e:
            raise SyntaxError(f"Line {self.current_line + 1}: {str(e)}")

    def parse(self, text: str) -> List[Dict[str, Any]]:
        self.lines = text.splitlines()
        result = []
        
        for i, line in enumerate(self.lines):
            self.current_line = i
            try:
                parsed = self.parse_line(line)
                if parsed:
                    result.append(parsed)
            except (SyntaxError, ValueError) as e:
                print(f"Error on line {i + 1}: {str(e)}", file=sys.stderr)
                sys.exit(1)
        
        return result

def main():
    # Read from stdin
    input_text = sys.stdin.read()
    
    # Parse the input
    parser = ConfigParser()
    try:
        result = parser.parse(input_text)
        # Output JSON to stdout
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
