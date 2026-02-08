import re
from pathlib import Path

from pytest_line_runner.resolver import resolve_line_to_node_id


def pytest_load_initial_conftests(early_config, parser, args):
    line_arg_pattern = re.compile(r"^(.+\.py):(\d+)$")

    for i, arg in enumerate(args):
        match = line_arg_pattern.match(arg)
        if not match:
            continue

        file_path_str, line_num_str = match.groups()
        file_path = Path(file_path_str)

        if not file_path.exists():
            continue

        target_line = int(line_num_str)
        node_id = resolve_line_to_node_id(file_path, target_line)

        if node_id:
            args[i] = f"{file_path_str}::{node_id}"
