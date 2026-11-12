"""Command-line interface for reviewing Python and C++ files.

Examples:
    python cli.py my_file.py
    python cli.py engine.cpp
    python cli.py src/ --fail-under 70      (exit code 1 if any file scores below 70 for example)
    python cli.py src/ --format json
"""
import argparse
import json
import sys
from pathlib import Path

from language_registry import EXTENSIONS, detect_language
from review import run_review

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "build"}


def collect_files(path):
    """Return the list of supported source files at `path` (a file or a folder)."""
    p = Path(path)
    if p.is_file():
        return [p]
    if p.is_dir():
        return sorted(f for f in p.rglob("*")
                      if f.is_file() and f.suffix.lower() in EXTENSIONS
                      and not SKIP_DIRS.intersection(f.relative_to(p).parts))
    return []


def review_file(path):
    language = detect_language(path)
    if language is None:
        return {"score": 0, "metrics": {},
                "feedback": [f"Unsupported file type: {path.suffix or path.name}"]}
    try:
        code = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"score": 0, "metrics": {}, "feedback": [f"Could not read file: {e}"]}
    return run_review(code, language)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Review Python and C++ code quality.")
    parser.add_argument("paths", nargs="+", help="files or folders to review")
    parser.add_argument("--fail-under", type=int, default=0,
                        help="exit with code 1 if any file scores below this value")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    files = [f for p in args.paths for f in collect_files(p)]
    if not files:
        print("No Python or C++ files found.", file=sys.stderr)
        return 2

    results = []
    for f in files:
        result = review_file(f)
        result["file"] = str(f)
        results.append(result)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['file']}: {r['score']}/100")
            for line in r["feedback"]:
                print(f"    {line}")

    return 1 if any(r["score"] < args.fail_under for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())