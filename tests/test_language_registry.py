import pytest

import language_registry as languages


@pytest.mark.parametrize("path,expected", [
    ("a.py", "python"), ("a.PY", "python"),
    ("a.cpp", "cpp"), ("a.cc", "cpp"), ("a.cxx", "cpp"),
    ("a.hpp", "cpp"), ("a.h", "cpp"), ("dir/b.CPP", "cpp"),
    ("notes.txt", None), ("Makefile", None),
])
def test_detect_language(path, expected):
    assert languages.detect_language(path) == expected


def test_analyze_dispatches_by_language():
    assert languages.analyze("def f():\n    pass\n", "python")["functions"] == 1
    assert languages.analyze("int f() { return 0; }", "cpp")["functions"] == 1


def test_unsupported_language_returns_error():
    assert "Unsupported language" in languages.analyze("x", "ruby")["error"]


def test_python_code_is_rejected_by_cpp_analyzer():
    assert "error" in languages.analyze("def f(:\n    pass", "cpp")
