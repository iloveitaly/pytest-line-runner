import ast
from bisect import bisect_right
from pathlib import Path


def resolve_line_to_node_id(file_path: Path, target_line: int) -> str | None:
    source = file_path.read_text()
    tree = ast.parse(source)

    entities = _collect_test_entities(tree)
    if not entities:
        return None

    return _find_nearest_entity(entities, target_line)


def _collect_test_entities(tree: ast.Module) -> list[tuple[int, str]]:
    entities = []

    def _walk_body(body: list[ast.stmt], parent_name: str = ""):
        for node in body:
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                class_line = _effective_start_line(node)
                class_name = f"{parent_name}{node.name}" if parent_name else node.name
                entities.append((class_line, class_name))

                _walk_body(node.body, f"{class_name}::")

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    func_line = _effective_start_line(node)
                    func_name = f"{parent_name}{node.name}" if parent_name else node.name
                    entities.append((func_line, func_name))

    _walk_body(tree.body)
    return sorted(entities, key=lambda x: x[0])


def _effective_start_line(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> int:
    if node.decorator_list:
        return node.decorator_list[0].lineno
    return node.lineno


def _find_nearest_entity(entities: list[tuple[int, str]], target_line: int) -> str | None:
    if not entities:
        return None

    lines = [line for line, _ in entities]
    idx = bisect_right(lines, target_line)

    if idx == 0:
        return entities[0][1]

    return entities[idx - 1][1]
