from pathlib import Path

from analyzer import analyze

SAMPLE = Path(__file__).parent / "samples" / "three_sum.py"


def test_no_loops():
    m = analyze("def f():\n    return 1\n")
    assert m["loops"] == 0
    assert m["max_loop_depth"] == 0
    assert m["functions"] == 1


def test_single_loop():
    m = analyze("for i in range(3):\n    print(i)\n")
    assert (m["loops"], m["max_loop_depth"]) == (1, 1)


def test_two_separate_loops_are_not_nested():
    m = analyze("for i in a:\n    pass\nfor j in b:\n    pass\n")
    assert (m["loops"], m["max_loop_depth"]) == (2, 1)


def test_nested_loops_depth():
    m = analyze("for i in a:\n    while i:\n        for j in b:\n            pass\n")
    assert (m["loops"], m["max_loop_depth"]) == (3, 3)


def test_loop_depth_resets_inside_function():
    code = "for i in a:\n    def f():\n        for j in b:\n            pass\n"
    assert analyze(code)["max_loop_depth"] == 1


def test_async_function_and_async_for_counted():
    m = analyze("async def f(x):\n    async for i in x:\n        pass\n")
    assert m["functions"] == 1
    assert m["loops"] == 1


def test_complexity_counts_branches_and_boolean_operators():
    code = (
        "def f(x):\n"
        "    if x > 0 and x < 10:\n"   # if (+1), and (+1)
        "        for i in range(x):\n"  # for (+1)
        "            pass\n"
        "    return x\n"
    )
    assert analyze(code)["function_details"][0]["complexity"] == 4


def test_nested_function_not_double_counted():
    code = (
        "def outer(x):\n"
        "    def inner(y):\n"
        "        if y:\n"
        "            return 1\n"
        "        return 0\n"
        "    return inner(x)\n"
    )
    details = {f["name"]: f["complexity"] for f in analyze(code)["function_details"]}
    assert details == {"outer": 1, "inner": 2}


def test_function_length_and_longest():
    code = "def a():\n    pass\n\ndef b():\n    x = 1\n    y = 2\n    return x + y\n"
    m = analyze(code)
    assert m["longest_function"] == 4
    assert m["max_complexity"] == 1


def test_empty_code_is_valid():
    m = analyze("")
    assert "error" not in m
    assert m["functions"] == 0


def test_syntax_error_returns_error():
    assert "syntax error" in analyze("def f(:\n")["error"].lower()


def test_null_bytes_and_non_string_return_error():
    assert "error" in analyze("x = 1\x00")
    assert "error" in analyze(None)


def test_sample_three_sum():
    m = analyze(SAMPLE.read_text())
    assert m["functions"] == 1
    assert m["max_loop_depth"] == 3
    assert m["function_details"][0]["name"] == "three_sum"


def test_unparseable_input_is_reported_not_raised(monkeypatch):
    def boom(_code):
        raise RecursionError("too deep")
    monkeypatch.setattr("analyzer.ast.parse", boom)
    assert analyze("x = 1") == {"error": "Code could not be parsed"}
