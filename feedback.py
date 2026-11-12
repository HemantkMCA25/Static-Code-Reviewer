"""Turns metrics into plain-English feedback (no external services needed)."""
from scorer import COMPLEXITY_LIMIT, LENGTH_LIMIT


def get_feedback(metrics):
    """Return a list of feedback messages for the given metrics."""
    messages = []

    # 1. Loops
    depth = metrics.get("max_loop_depth", 0)
    if depth == 0:
        messages.append("No loops detected. Good efficiency.")
    elif depth == 1:
        messages.append("Loops are not nested. Complexity is likely O(n) or less.")
    elif depth == 2:
        messages.append("Nested loops detected (depth 2). Complexity may be O(n^2). "
                        "Consider optimization.")
    else:
        messages.append(f"Deeply nested loops (depth {depth}). Check whether the "
                        "inner loops can be simplified.")

    # 2. Functions
    if metrics.get("functions", 0) == 0:
        messages.append("No functions used. Code is not modular.")
    else:
        found_problem = False
        for fn in metrics.get("function_details", []):
            if fn["complexity"] > COMPLEXITY_LIMIT:
                found_problem = True
                messages.append(f"Function `{fn['name']}` has complexity {fn['complexity']} "
                                f"(limit {COMPLEXITY_LIMIT}). Consider splitting it.")
            if fn["length"] > LENGTH_LIMIT:
                found_problem = True
                messages.append(f"Function `{fn['name']}` is {fn['length']} lines long "
                                f"(limit {LENGTH_LIMIT}). Consider splitting it.")
        if not found_problem:
            messages.append("Functions are reasonably small and simple.")

    # 3. C++ only: manual memory management
    raw_ops = metrics.get("raw_memory_ops", 0)
    if raw_ops:
        messages.append(f"Found {raw_ops} raw new/delete operation(s). Prefer smart "
                        "pointers (std::unique_ptr) or containers (std::vector).")

    return messages
