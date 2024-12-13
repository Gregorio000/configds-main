# Educational Configuration Language Parser

This tool converts a custom configuration language to JSON format. It supports various features including constants, arrays, and arithmetic expressions.

## Features

- Single-line comments with `//`
- Arrays in format `{ value1. value2. value3. }`
- Constant declarations: `value -> NAME`
- Arithmetic expressions: `$(operator arg1 arg2)`
- Supported operations: `+`, `-`, `*`, `mod`
- Error detection and reporting

## Installation

```bash
pip install -r requirements.txt
```

## Usage

The tool reads from standard input and outputs JSON to standard output:

```bash
python parser.py < input.txt > output.json
```

## Example Input

```
// Define a constant
42 -> ANSWER

// Use it in an expression
$(+ ANSWER 1)

// Create arrays
{ 1. 2. 3. }

// Nested arrays
{ { 1. 2. }. { 3. 4. } }
```

## Testing

Run the tests using pytest:

```bash
pytest test_parser.py
```

## Example Configurations

Check the `examples` directory for sample configurations:
- `game_config.txt`: Game settings example
- `network_config.txt`: Network configuration example
