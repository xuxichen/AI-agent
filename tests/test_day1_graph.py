"""Tests for day1/01_first_graph.py.

The example file is named `01_first_graph.py`, which is not a valid Python
module name, so the module is loaded by file path instead of imported.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLE = Path(__file__).resolve().parents[1] / "day1" / "01_first_graph.py"


@pytest.fixture(scope="module")
def example():
    spec = importlib.util.spec_from_file_location("day1_first_graph", EXAMPLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_graph_doubles_then_adds_ten(example):
    result = example.graph.invoke({"count": 3, "log": []})
    assert result == {"count": 16, "log": ["double", "add_ten"]}


def test_nodes_run_in_declared_order(example):
    assert example.graph.invoke({"count": 1, "log": []})["log"] == ["double", "add_ten"]


def test_example_runs_as_documented_script():
    """Guards the Quickstart command in README: `python day1/01_first_graph.py`."""
    proc = subprocess.run(
        [sys.executable, str(EXAMPLE)], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK: langgraph 已跑通" in proc.stdout
