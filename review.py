"""Main pipeline: analyze -> score -> feedback."""
from feedback import get_feedback
from language_registry import analyze
from scorer import penalties, score


def run_review(code, language="python"):
    """Review `code` and return a dictionary with the results."""
    if not isinstance(code, str) or not code.strip():
        return _failed("No code provided.")

    metrics = analyze(code, language)
    if "error" in metrics:
        return _failed(metrics["error"])

    return {
        "score": score(metrics),
        "metrics": metrics,
        "penalties": penalties(metrics),
        "feedback": get_feedback(metrics),
    }


def _failed(message):
    return {"score": 0, "metrics": {"error": message}, "penalties": {}, "feedback": [message]}
