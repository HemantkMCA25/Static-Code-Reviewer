# Code Reviewer

A simple code review tool for **Python and C++**. It analyzes code structure (Python's `ast` module for Python, [tree-sitter](https://tree-sitter.github.io/) for C++), computes a 0-100 quality score, and gives plain-English feedback. No API keys or internet connection needed.

## Features
- **Static analysis (AST):** loop count, loop nesting depth, function count, per-function length and cyclomatic complexity, for both Python and C++
- **C++ checks:** supports `for`, range-`for`, `while`, `do-while`, `if`, `switch`, `catch`, `?:`, `&&`/`||`; flags raw `new`/`delete`
- **Scoring engine:** starts at 100 and subtracts transparent penalties (see below)
- **Readable feedback:** simple rules that point to the exact function or loop to fix
- **Two interfaces:** Streamlit web app and a command-line tool (CI-friendly exit codes)
- **Tested:** pytest suite, run on every push with GitHub Actions

## Project structure
```
analyzer.py      Python metrics via ast (loops, nesting, complexity, function length)
cpp_analyzer.py  C++ metrics via tree-sitter (same metrics, plus raw new/delete)
language_registry.py     Language registry and file-extension detection
scorer.py        Score and penalty rules
feedback.py      Turns metrics into plain-English feedback
review.py        Pipeline: analyze -> score -> feedback
cli.py           Command-line interface
app.py           Streamlit UI
main.py          Launcher for the Streamlit app
tests/           pytest suite and sample inputs (Python and C++)
```

## Setup
```bash
git clone https://github.com/HemantkMCA25/AI-Code-Reviewer.git
cd AI-Code-Reviewer
pip install -r requirements.txt
```

## Usage

### Web app
```bash
streamlit run app.py
```
(On Windows you can also double-click `run.bat`.)

### Command line
```bash
python cli.py my_file.py                       # review one file
python cli.py engine.cpp                       # C++ works the same way (.cpp .cc .cxx .hpp .hh .h)
python cli.py src/ --fail-under 70             # review a folder (Python + C++ files); exit code 1 if any file scores < 70
python cli.py src/ --format json               # machine-readable output
```
Exit codes: `0` ok, `1` a file scored below `--fail-under`, `2` no supported files found.

## How the score works
| Check | Penalty |
|---|---|
| Each loop | -3 (max -15) |
| Each loop-nesting level beyond 1 | -15 |
| Function complexity above 10 | -2 per point (max -30) |
| Function longer than 50 lines | -1 per 5 extra lines (max -20) |
| No functions | -10 |
| Each raw `new`/`delete` (C++) | -2 (max -10) |

The limits live at the top of `scorer.py` and are easy to tune.

## Running the tests
```bash
pip install -r requirements-dev.txt
pytest --cov=. --cov-report=term-missing
```

## Limitations
- Supports Python and C++ only (`.c` files are not supported; `.h` headers are parsed as C++)
- C++ code with syntax errors is rejected rather than partially analyzed; the C++ parser does not run the preprocessor, so heavy macro use may be reported as a syntax error
- Loop depth counts loops only (Python comprehensions count toward complexity but not nesting depth); C++ lambdas count toward their enclosing function
- Rule-based feedback is a heuristic, not a proof of algorithmic complexity

## Roadmap
- More C++ checks (missing `const` references, pass-by-value of large parameters)
- Post results as comments on pull requests
- Support for more programming languages
