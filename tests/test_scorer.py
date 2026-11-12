from analyzer import analyze
from scorer import penalties, score


def test_clean_function_scores_100():
    assert score(analyze("def f(x):\n    return x + 1\n")) == 100


def test_nested_loops_score_lower_than_single_loop():
    single = analyze("def f(a):\n    for i in a:\n        pass\n")
    nested = analyze("def f(a):\n    for i in a:\n        for j in a:\n            pass\n")
    assert score(nested) < score(single) < 100


def test_separate_loops_not_punished_as_nesting():
    m = analyze("def f(a):\n    for i in a:\n        pass\n    for j in a:\n        pass\n")
    assert "loop nesting" not in penalties(m)


def test_many_small_functions_cannot_hide_nested_loops():
    code = "def a():\n    pass\n" * 5 + "for i in x:\n    for j in x:\n        pass\n"
    assert score(analyze(code)) < 100


def test_high_complexity_and_long_function_penalized():
    body = "".join(f"    if x == {i}:\n        pass\n" for i in range(30))
    m = analyze("def f(x):\n" + body)
    assert {"function complexity", "function length"} <= set(penalties(m))


def test_no_functions_penalty():
    assert penalties(analyze("x = 1\n")) == {"no functions": 10}


def test_score_is_clamped_to_0_100():
    assert score({"loops": 100, "max_loop_depth": 50, "functions": 0,
                  "max_complexity": 500, "longest_function": 9999}) == 0
    assert score({}) == 90  # missing keys default to 0; no functions -> -10


def test_raw_memory_penalty_is_capped():
    assert penalties({"functions": 1, "raw_memory_ops": 1}) == {"raw new/delete": 2}
    assert penalties({"functions": 1, "raw_memory_ops": 50}) == {"raw new/delete": 10}
