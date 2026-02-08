[![Release Notes](https://img.shields.io/github/release/iloveitaly/pytest-line-runner)](https://github.com/iloveitaly/pytest-line-runner/releases)
[![Downloads](https://static.pepy.tech/badge/pytest-line-runner/month)](https://pepy.tech/project/pytest-line-runner)
![GitHub CI Status](https://github.com/iloveitaly/pytest-line-runner/actions/workflows/build_and_publish.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Run Pytest Tests by Line Number

A pytest plugin that lets you run tests by specifying any line number within the test function or class, not just the exact definition line. This makes it easier to run specific tests from your editor or IDE without needing to navigate to the precise test definition.

## The Problem

Pytest natively supports running specific tests using the `file.py::test_name` syntax, but if you try to use `file.py:123` where line 123 is inside a test function (not the exact line where `def test_*` starts), pytest won't find the test.

This plugin solves that by automatically resolving line numbers to the nearest test function or class.

## Installation

```bash
uv add pytest-line-runner
```

## Usage

Simply pass a file path and line number to pytest:

```bash
pytest tests/test_example.py:42
```

The plugin will find the test function or class that contains line 42 and run it.

### Examples

```python
# tests/test_example.py
def test_addition():
    result = 1 + 1  # Line 3
    assert result == 2  # Line 4

class TestCalculator:  # Line 6
    def test_multiply(self):  # Line 7
        result = 2 * 3  # Line 8
        assert result == 6  # Line 9
```

All of these commands work:

```bash
pytest tests/test_example.py:2   # Runs test_addition (definition line)
pytest tests/test_example.py:3   # Runs test_addition (inside function)
pytest tests/test_example.py:4   # Runs test_addition (inside function)
pytest tests/test_example.py:6   # Runs TestCalculator (class line)
pytest tests/test_example.py:8   # Runs TestCalculator::test_multiply
pytest tests/test_example.py:9   # Runs TestCalculator::test_multiply
```

## Features

- Works with test functions (both sync and async)
- Works with test classes
- Handles decorators correctly (finds tests even when you specify a decorator line)
- Uses AST parsing for accurate test resolution
- Automatically falls back to pytest's default behavior if the file doesn't exist or no test is found

## License

[MIT](https://opensource.org/licenses/MIT)

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*