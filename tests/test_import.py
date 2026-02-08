"""Test pytest-line-runner."""

import pytest_line_runner


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(pytest_line_runner.__name__, str)