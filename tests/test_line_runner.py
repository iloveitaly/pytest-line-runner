import ast

from pytest_line_runner.resolver import (
    _collect_test_entities,
    _effective_start_line,
    _find_nearest_entity,
    resolve_line_to_node_id,
)


def test_line_on_function_def(pytester):
    pytester.makepyfile(
        """
        def test_first():
            assert True

        def test_second():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_line_on_function_def.py:2")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_first*"])


def test_line_inside_function_body(pytester):
    pytester.makepyfile(
        """
        def test_first():
            assert True
            assert 1 == 1

        def test_second():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_line_inside_function_body.py:4")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_first*"])


def test_line_between_tests_selects_previous(pytester):
    pytester.makepyfile(
        """
        def test_first():
            assert True

        def test_second():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_line_between_tests_selects_previous.py:3")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_first*"])


def test_line_before_first_test_selects_first(pytester):
    pytester.makepyfile(
        """
        import pytest

        def test_first():
            assert True

        def test_second():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_line_before_first_test_selects_first.py:1")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_first*"])


def test_line_after_last_test_selects_last(pytester):
    pytester.makepyfile(
        """
        def test_first():
            assert True

        def test_second():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_line_after_last_test_selects_last.py:10")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_second*"])


def test_class_method_by_line(pytester):
    pytester.makepyfile(
        """
        class TestFoo:
            def test_first(self):
                assert True

            def test_second(self):
                assert True
        """
    )

    result = pytester.runpytest("-v", "test_class_method_by_line.py:3")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*TestFoo::test_first*"])


def test_class_definition_line_runs_all_tests(pytester):
    pytester.makepyfile(
        """
        class TestFoo:
            def test_first(self):
                assert True

            def test_second(self):
                assert True
        """
    )

    result = pytester.runpytest("-v", "test_class_definition_line_runs_all_tests.py:1")
    result.assert_outcomes(passed=2)


def test_decorated_function(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.skip
        def test_skipped():
            assert False

        def test_normal():
            assert True
        """
    )

    result = pytester.runpytest("test_decorated_function.py:4")
    result.assert_outcomes(skipped=1)


def test_parametrized_test_runs_all_variants(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.parametrize("value", [1, 2, 3])
        def test_param(value):
            assert value > 0
        """
    )

    result = pytester.runpytest("test_parametrized_test_runs_all_variants.py:5")
    result.assert_outcomes(passed=3)


def test_async_function(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.asyncio
        async def test_async():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_async_function.py:5")
    result.assert_outcomes(passed=1)


def test_normal_syntax_still_works(pytester):
    pytester.makepyfile(
        """
        def test_first():
            assert True

        def test_second():
            assert True
        """
    )

    result = pytester.runpytest("-v", "test_normal_syntax_still_works.py::test_second")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_second*"])


def test_nonexistent_file_passes_through(pytester):
    result = pytester.runpytest("nonexistent.py:10")
    assert result.ret != 0


def test_mixed_args(pytester):
    pytester.makepyfile(
        test_file1="""
        def test_one():
            assert True
        """,
        test_file2="""
        def test_two():
            assert True
        """,
    )

    result = pytester.runpytest("test_file1.py:2", "test_file2.py")
    result.assert_outcomes(passed=2)


def test_resolve_line_to_node_id_function():
    source = """
def test_first():
    assert True

def test_second():
    assert True
"""
    tree = ast.parse(source)
    entities = _collect_test_entities(tree)

    assert entities == [(2, "test_first"), (5, "test_second")]
    assert _find_nearest_entity(entities, 2) == "test_first"
    assert _find_nearest_entity(entities, 3) == "test_first"
    assert _find_nearest_entity(entities, 5) == "test_second"
    assert _find_nearest_entity(entities, 1) == "test_first"


def test_collect_test_entities_with_class():
    source = """
class TestFoo:
    def test_first(self):
        assert True

    def test_second(self):
        assert True
"""
    tree = ast.parse(source)
    entities = _collect_test_entities(tree)

    assert entities == [
        (2, "TestFoo"),
        (3, "TestFoo::test_first"),
        (6, "TestFoo::test_second"),
    ]


def test_effective_start_line_with_decorator():
    source = """
@pytest.mark.skip
def test_decorated():
    assert False
"""
    tree = ast.parse(source)
    func_node = tree.body[0]
    assert _effective_start_line(func_node) == 2


def test_effective_start_line_without_decorator():
    source = """
def test_normal():
    assert True
"""
    tree = ast.parse(source)
    func_node = tree.body[0]
    assert _effective_start_line(func_node) == 2


def test_resolve_line_to_node_id_integration(tmp_path):
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        """
def test_first():
    assert True

def test_second():
    assert True
"""
    )

    assert resolve_line_to_node_id(test_file, 2) == "test_first"
    assert resolve_line_to_node_id(test_file, 3) == "test_first"
    assert resolve_line_to_node_id(test_file, 5) == "test_second"
    assert resolve_line_to_node_id(test_file, 1) == "test_first"


def test_nested_class():
    source = """
class TestOuter:
    class TestInner:
        def test_nested(self):
            assert True
"""
    tree = ast.parse(source)
    entities = _collect_test_entities(tree)

    assert entities == [
        (2, "TestOuter"),
        (3, "TestOuter::TestInner"),
        (4, "TestOuter::TestInner::test_nested"),
    ]
