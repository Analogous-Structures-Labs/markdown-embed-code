from pathlib import PosixPath

import pytest

from markdown_embed_code import Embed, render_markdown


@pytest.mark.parametrize(
    "extra,expected",
    [
        (
            "tests/src/sample.py[4:5]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 4, "end_at": 5},
        ),
        (
            "tests/src/sample.py [4:5]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 4, "end_at": 5},
        ),
        (
            "tests/src/sample.py      [4:5]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 4, "end_at": 5},
        ),
        (
            "tests/src/sample.py [ 4:5 ]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 4, "end_at": 5},
        ),
        (
            "tests/src/sample.py [ 4 : 5 ]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 4, "end_at": 5},
        ),
        (
            "tests/src/sample.py [4]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 4, "end_at": 5},
        ),
        (
            "tests/src/sample.py [4:]",
            {
                "file_path": PosixPath("tests/src/sample.py"),
                "start_at": 4,
                "end_at": None,
            },
        ),
        (
            "tests/src/sample.py [:5]",
            {"file_path": PosixPath("tests/src/sample.py"), "start_at": 1, "end_at": 5},
        ),
        (
            "tests/src/sample.py [0:]",
            {
                "file_path": PosixPath("tests/src/sample.py"),
                "start_at": 1,
                "end_at": None,
            },
        ),
        (
            "tests/src/sample.py [:]",
            {
                "file_path": PosixPath("tests/src/sample.py"),
                "start_at": 1,
                "end_at": None,
            },
        ),
        (
            "tests/src/sample.py []",
            {
                "file_path": PosixPath("tests/src/sample.py"),
                "start_at": 1,
                "end_at": None,
            },
        ),
        (
            "tests/src/sample.py [",
            {
                "file_path": PosixPath("tests/src/sample.py ["),
                "start_at": 1,
                "end_at": None,
            },
        ),
    ],
)
def test_embed_parsing(extra, expected):
    assert (
        Embed.parse_from_extra(extra).__dict__ == expected
    ), f"{extra} did not parse as expected"


def test_embed_entire_file():
    markdown = """```python tests/src/sample.py\n```\n"""
    assert render_markdown(markdown) == (
        "```python tests/src/sample.py\n"
        "def add(x, y):\n"
        "    return x + y\n"
        "\n"
        "\n"
        "def subtract(x, y):\n"
        "    return x - y\n"
        "\n"
        "\n"
        "def multiply(x, y):\n"
        "    return x + y\n"
        "```\n"
    ), "Code was not embedded correctly."


def test_embed_slice():
    markdown = """```python tests/src/sample.py [4:8]\n```\n"""
    assert render_markdown(markdown) == (
        "```python tests/src/sample.py [4:8]\n"
        "\n"
        "def subtract(x, y):\n"
        "    return x - y\n"
        "\n"
        "```\n"
    ), "Code was not embedded correctly."


def test_embed_slice_with_no_start():
    markdown = """```python tests/src/sample.py [:5]\n```\n"""
    assert render_markdown(markdown) == (
        "```python tests/src/sample.py [:5]\n"
        "def add(x, y):\n"
        "    return x + y\n"
        "\n"
        "\n"
        "```\n"
    ), "Code was not embedded correctly."


def test_embed_slice_with_no_end():
    markdown = """```python tests/src/sample.py [5:]\n```\n"""
    assert render_markdown(markdown) == (
        "```python tests/src/sample.py [5:]\n"
        "def subtract(x, y):\n"
        "    return x - y\n"
        "\n"
        "\n"
        "def multiply(x, y):\n"
        "    return x + y\n"
        "```\n"
    ), "Code was not embedded correctly."


def test_embed_single_line():
    markdown = """```python tests/src/sample.py [6]\n```\n"""
    assert render_markdown(markdown) == (
        "```python tests/src/sample.py [6]\n" "    return x - y\n" "```\n"
    ), "Code was not embedded correctly."


def test_override_existing_code():
    markdown = """```python tests/src/sample.py\nprint('code already exists')\n```\n"""
    assert render_markdown(markdown) == (
        "```python tests/src/sample.py\n"
        "def add(x, y):\n"
        "    return x + y\n"
        "\n"
        "\n"
        "def subtract(x, y):\n"
        "    return x - y\n"
        "\n"
        "\n"
        "def multiply(x, y):\n"
        "    return x + y\n"
        "```\n"
    ), "Code was not embedded correctly."


def test_ignore_no_filepath():
    markdown = """```python\n```\n"""
    assert render_markdown(markdown) == markdown, "Unintended embed."
