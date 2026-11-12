"""Language registry: maps file extensions to analyzers."""
from pathlib import Path

import analyzer
import cpp_analyzer

LANGUAGES = {
    "python": {"label": "Python", "analyze": analyzer.analyze},
    "cpp": {"label": "C++", "analyze": cpp_analyzer.analyze},
}

EXTENSIONS = {
    ".py": "python",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".hpp": "cpp", ".hh": "cpp", ".h": "cpp",
}


def detect_language(path):
    """Language for a file path, or None if the extension isn't supported."""
    return EXTENSIONS.get(Path(path).suffix.lower())


def label(language):
    return LANGUAGES.get(language, {}).get("label", language)


def analyze(code, language="python"):
    if language not in LANGUAGES:
        return {"error": f"Unsupported language: {language}"}
    return LANGUAGES[language]["analyze"](code)
