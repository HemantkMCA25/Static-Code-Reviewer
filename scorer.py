"""Quality score: start at 100 and subtract penalties (all limits are tunable)."""

LOOP_COUNT_PENALTY = 3        # per loop ...
LOOP_COUNT_PENALTY_CAP = 15   # ... up to this much
NESTING_PENALTY = 15          # per loop-nesting level beyond 1
COMPLEXITY_LIMIT = 10         # cyclomatic complexity allowed per function
COMPLEXITY_PENALTY = 2        # per point over the limit
COMPLEXITY_PENALTY_CAP = 30
LENGTH_LIMIT = 50             # lines allowed per function
LENGTH_PENALTY_CAP = 20       # 1 point per 5 lines over the limit
NO_FUNCTIONS_PENALTY = 10
RAW_MEMORY_PENALTY = 2        # per raw new/delete (C++ only)
RAW_MEMORY_PENALTY_CAP = 10


def penalties(metrics):
    """Return {reason: points_lost} for the non-zero penalties."""
    loops = metrics.get("loops", 0)
    depth = metrics.get("max_loop_depth", 0)
    functions = metrics.get("functions", 0)
    complexity = metrics.get("max_complexity", 0)
    longest = metrics.get("longest_function", 0)
    raw_memory = metrics.get("raw_memory_ops", 0)

    found = {
        "loop count": min(loops * LOOP_COUNT_PENALTY, LOOP_COUNT_PENALTY_CAP),
        "loop nesting": max(0, depth - 1) * NESTING_PENALTY,
        "function complexity": min(max(0, complexity - COMPLEXITY_LIMIT) * COMPLEXITY_PENALTY,
                                   COMPLEXITY_PENALTY_CAP),
        "function length": min(max(0, longest - LENGTH_LIMIT) // 5, LENGTH_PENALTY_CAP),
        "no functions": NO_FUNCTIONS_PENALTY if functions == 0 else 0,
        "raw new/delete": min(raw_memory * RAW_MEMORY_PENALTY, RAW_MEMORY_PENALTY_CAP),
    }
    return {reason: points for reason, points in found.items() if points}


def score(metrics):
    """Final score, clamped to 0-100."""
    return max(0, min(100, 100 - sum(penalties(metrics).values())))
