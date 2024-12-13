import pytest
from parser import ConfigParser

def test_comments():
    parser = ConfigParser()
    result = parser.parse("// This is a comment\n42")
    assert len(result) == 1
    assert result[0] == {'type': 'value', 'value': 42}

def test_arrays():
    parser = ConfigParser()
    result = parser.parse("{ 1. 2. 3. }")
    assert result[0] == {'type': 'value', 'value': [1, 2, 3]}

def test_nested_arrays():
    parser = ConfigParser()
    result = parser.parse("{ 1. { 2. 3. }. 4. }")
    assert result[0] == {'type': 'value', 'value': [1, [2, 3], 4]}

def test_constants():
    parser = ConfigParser()
    result = parser.parse("42 -> ANSWER\nANSWER")
    assert len(result) == 2
    assert result[0] == {'type': 'constant_declaration', 'name': 'ANSWER', 'value': 42}
    assert result[1] == {'type': 'value', 'value': 42}

def test_expressions():
    parser = ConfigParser()
    input_text = """
    10 -> X
    20 -> Y
    $(+ X Y)
    $(- Y X)
    $(* X 2)
    $(mod Y 3)
    """
    result = parser.parse(input_text)
    assert result[2]['value'] == 30  # X + Y
    assert result[3]['value'] == 10  # Y - X
    assert result[4]['value'] == 20  # X * 2
    assert result[5]['value'] == 2   # Y mod 3

def test_invalid_constant():
    parser = ConfigParser()
    with pytest.raises(SystemExit):
        parser.parse("UNDEFINED_CONSTANT")

def test_invalid_expression():
    parser = ConfigParser()
    with pytest.raises(SystemExit):
        parser.parse("$(invalid X Y)")

def test_invalid_mod():
    parser = ConfigParser()
    with pytest.raises(SystemExit):
        parser.parse("$(mod 10 0)")

def test_complex_config():
    parser = ConfigParser()
    input_text = """
    // Define base values
    10 -> BASE
    { 1. 2. 3. } -> ARRAY
    // Compute derived values
    $(+ BASE 5) -> DERIVED
    { ARRAY. $(* BASE 2). }
    """
    result = parser.parse(input_text)
    assert len(result) == 4
    assert result[2]['value'] == 15  # DERIVED = BASE + 5
    assert result[3]['value'] == [[1, 2, 3], 20]  # [ARRAY, BASE * 2]
