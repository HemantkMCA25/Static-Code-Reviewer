import json
from pathlib import Path

from cli import main

CLEAN = "def f(x):\n    return x\n"
NESTED = "def f(a):\n    for i in a:\n        for j in a:\n            for k in a:\n                pass\n"


def test_clean_file_passes(tmp_path, capsys):
    f = tmp_path / "ok.py"
    f.write_text(CLEAN)
    assert main([str(f), "--fail-under", "90"]) == 0
    assert "100/100" in capsys.readouterr().out


def test_low_score_fails_threshold(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text(NESTED)
    assert main([str(f), "--fail-under", "90"]) == 1
    assert main([str(f)]) == 0  # no threshold -> never fails


def test_directory_scan_skips_ignored_folders(tmp_path, capsys):
    (tmp_path / "a.py").write_text(CLEAN)
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "lib.py").write_text(CLEAN)
    main([str(tmp_path), "--format", "json"])
    files = [r["file"] for r in json.loads(capsys.readouterr().out)]
    assert len(files) == 1 and files[0].endswith("a.py")


def test_missing_path_returns_2(tmp_path):
    assert main([str(tmp_path / "nope.py")]) == 2


def test_unreadable_file_scores_zero(tmp_path, monkeypatch, capsys):
    f = tmp_path / "x.py"
    f.write_text(CLEAN)

    def fail(*a, **k):
        raise OSError("denied")
    monkeypatch.setattr("cli.Path.read_text", fail)
    assert main([str(f), "--fail-under", "1"]) == 1
    assert "Could not read file" in capsys.readouterr().out


CPP_NESTED = "int f(int n) { for (;;) { for (;;) { for (;;) { } } } return 0; }"


def test_cpp_file_is_reviewed(tmp_path, capsys):
    f = tmp_path / "engine.cpp"
    f.write_text(CPP_NESTED)
    assert main([str(f), "--fail-under", "90"]) == 1
    assert "engine.cpp" in capsys.readouterr().out


def test_directory_scan_picks_python_and_cpp_only(tmp_path, capsys):
    (tmp_path / "a.py").write_text(CLEAN)
    (tmp_path / "b.cpp").write_text("int f() { return 0; }")
    (tmp_path / "c.h").write_text("int g() { return 0; }")
    (tmp_path / "notes.txt").write_text("ignore me")
    main([str(tmp_path), "--format", "json"])
    files = sorted(Path(r["file"]).name for r in json.loads(capsys.readouterr().out))
    assert files == ["a.py", "b.cpp", "c.h"]


def test_unsupported_explicit_file_fails_threshold(tmp_path, capsys):
    f = tmp_path / "notes.txt"
    f.write_text("hello")
    assert main([str(f), "--fail-under", "1"]) == 1
    assert "Unsupported file type" in capsys.readouterr().out
