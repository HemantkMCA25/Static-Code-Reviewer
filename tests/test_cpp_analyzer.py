from pathlib import Path

import cpp_analyzer
from cpp_analyzer import analyze

SAMPLE = Path(__file__).parent / "samples" / "matrix_ops.cpp"


def test_no_loops():
    m = analyze("int f() { return 1; }")
    assert (m["loops"], m["max_loop_depth"], m["functions"]) == (0, 0, 1)
    assert m["max_complexity"] == 1


def test_all_loop_kinds_counted():
    code = """
    void f(std::vector<int>& v, int n) {
        for (int i = 0; i < n; i++) {}
        for (auto x : v) {}
        while (n > 0) { n--; }
        do { n++; } while (n < 3);
    }"""
    m = analyze(code)
    assert (m["loops"], m["max_loop_depth"]) == (4, 1)


def test_nested_loops_depth():
    m = analyze("void f(int n) { for (int i=0;i<n;i++) { while (n) { for (auto x : v) {} } } }")
    assert (m["loops"], m["max_loop_depth"]) == (3, 3)


def test_loop_depth_resets_per_function():
    code = "void a(int n) { for (;;) { } }\nvoid b(int n) { for (;;) { } }"
    assert analyze(code)["max_loop_depth"] == 1


def test_complexity_counts_branches_and_logical_operators():
    code = """
    int f(int x, int y) {
        if (x > 0 && y > 0 || x == y) {   // if +1, && +1, || +1
            return 1;
        }
        switch (x) { case 1: break; case 2: break; default: break; }  // 2 cases
        try { } catch (const std::exception& e) { }                   // catch +1
        return x > y ? x : y;                                         // ternary +1
    }"""
    assert analyze(code)["function_details"][0]["complexity"] == 1 + 3 + 2 + 1 + 1


def test_function_names_for_methods_and_constructors():
    code = """
    class Foo { public: Foo() {} ~Foo() {} int get() const { return x; } int x; };
    int* Foo::make(int n) { return nullptr; }
    int main() { return 0; }"""
    names = [f["name"] for f in analyze(code)["function_details"]]
    assert names == ["Foo", "~Foo", "get", "Foo::make", "main"]


def test_lambda_body_counts_toward_enclosing_function():
    m = analyze("void f() { auto g = [](int q) { while (q) q--; }; }")
    assert m["functions"] == 1
    assert m["loops"] == 1
    assert m["function_details"][0]["complexity"] == 2


def test_function_length_and_longest():
    m = analyze("int a() {\n return 1;\n}\nint b() {\n int x = 1;\n int y = 2;\n return x + y;\n}\n")
    assert m["longest_function"] == 5


def test_raw_new_and_delete_counted():
    m = analyze("void f() { int* p = new int(1); delete p; }")
    assert m["raw_memory_ops"] == 2


def test_empty_code_is_valid():
    m = analyze("")
    assert "error" not in m
    assert m["functions"] == 0


def test_syntax_error_reports_line():
    err = analyze("int main() {\n  int x = ;\n  return 0;\n}\n")["error"]
    assert "Invalid C++ code" in err
    assert "line 2" in err


def test_non_string_input():
    assert "error" in analyze(None)


def test_missing_dependency_gives_install_hint(monkeypatch):
    def no_parser():
        raise ImportError("tree_sitter missing")
    monkeypatch.setattr(cpp_analyzer, "_get_parser", no_parser)
    assert "pip install" in analyze("int x;")["error"]


def test_too_deep_input_is_reported_not_raised(monkeypatch):
    def boom(self, *a, **k):
        raise RecursionError("deep")
    monkeypatch.setattr(cpp_analyzer._Counter, "visit", boom)
    assert analyze("int f() { return 1; }") == {"error": "Code could not be parsed"}


def test_sample_file():
    m = analyze(SAMPLE.read_text())
    assert m["functions"] == 2
    assert m["max_loop_depth"] == 2
    assert m["raw_memory_ops"] == 2
    names = {f["name"]: f["complexity"] for f in m["function_details"]}
    assert names == {"make_table": 5, "main": 1}
