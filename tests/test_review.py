from review import run_review


def test_valid_code_returns_full_result():
    r = run_review("def f(x):\n    return x\n")
    assert r["score"] == 100
    assert r["penalties"] == {}
    assert r["metrics"]["functions"] == 1
    assert isinstance(r["feedback"], list)


def test_syntax_error_scores_zero():
    r = run_review("def f(:\n")
    assert r["score"] == 0
    assert "syntax error" in r["feedback"][0].lower()


def test_empty_and_whitespace_input():
    assert run_review("")["score"] == 0
    assert run_review("   \n")["feedback"] == ["No code provided."]


def test_cpp_end_to_end():
    code = "int* make(int n) { int* a = new int[n]; for (int i=0;i<n;i++) { for (int j=0;j<n;j++) {} } return a; }"
    r = run_review(code, language="cpp")
    assert r["score"] < 100
    assert "raw new/delete" in r["penalties"]
    assert "loop nesting" in r["penalties"]
    assert any("smart pointers" in m for m in r["feedback"])


def test_unsupported_language_scores_zero():
    r = run_review("x", language="ruby")
    assert r["score"] == 0
    assert "Unsupported language" in r["feedback"][0]
