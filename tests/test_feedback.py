from analyzer import analyze
from feedback import get_feedback


def text(code):
    return " ".join(get_feedback(analyze(code)))


def test_loop_depth_messages():
    assert "No loops" in text("def f():\n    return 1\n")
    assert "not nested" in text("def f(a):\n    for i in a:\n        pass\n")
    assert "Nested loops" in text("def f(a):\n    for i in a:\n        for j in a:\n            pass\n")
    deep = "def f(a):\n    for i in a:\n        for j in a:\n            for k in a:\n                pass\n"
    assert "depth 3" in text(deep)


def test_names_complex_function():
    body = "".join(f"    if x == {i}:\n        pass\n" for i in range(15))
    result = text("def big(x):\n" + body)
    assert "`big`" in result
    assert "complexity" in result


def test_long_function_flagged():
    assert "lines long" in text("def f():\n" + "    x = 1\n" * 60)


def test_no_functions_message():
    assert "not modular" in text("x = 1\n")


def test_good_code_gets_positive_message():
    assert "reasonably small" in text("def f(x):\n    return x\n")


def test_raw_memory_message_for_cpp():
    messages = get_feedback({"functions": 1, "raw_memory_ops": 3})
    assert any("smart pointers" in m for m in messages)
