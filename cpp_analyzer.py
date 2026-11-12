"""Tree-sitter based static analysis for C++ source code.

Returns the same metrics as analyzer.py (Python), so scoring and feedback
works unchanged for both languages.
"""
from functools import lru_cache

LOOPS = {"for_statement", "for_range_loop", "while_statement", "do_statement"}
BRANCHES = {"if_statement", "catch_clause", "conditional_expression"}
LOGICAL_OPERATORS = {"&&", "||", "and", "or"}
NAME_TYPES = {"identifier", "field_identifier", "qualified_identifier",
              "destructor_name", "operator_name"}
INSTALL_HINT = "C++ support needs: pip install tree-sitter tree-sitter-cpp"


@lru_cache(maxsize=1)
def _get_parser():
    import tree_sitter_cpp
    from tree_sitter import Language, Parser
    return Parser(Language(tree_sitter_cpp.language()))


def _function_name(node):
    """Name of a function_definition: the first name-like node in its declarator."""
    declarator = node.child_by_field_name("declarator")
    stack = [declarator] if declarator else []
    while stack:
        current = stack.pop()
        if current.type in NAME_TYPES:
            return current.text.decode("utf-8", errors="replace")
        stack.extend(reversed(current.children))  # keep left-to-right order
    return "<anonymous>"


def _first_error_line(root):
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type == "ERROR" or node.is_missing:
            return node.start_point[0] + 1
        stack.extend(reversed(node.children))
    return "?"


def _is_branch(node):
    """True if this node adds a decision path to the function's complexity."""
    if node.type in BRANCHES:
        return True
    if node.type == "case_statement":
        return node.child_by_field_name("value") is not None  # `default:` doesn't count
    if node.type == "binary_expression":
        operator = node.child_by_field_name("operator")
        return operator is not None and operator.type in LOGICAL_OPERATORS
    return False


class _Counter:
    """Walks the syntax tree once, collecting loop, function and memory counts."""

    def __init__(self):
        self.loops = 0
        self.max_loop_depth = 0
        self.raw_memory_ops = 0
        self.functions = []

    def visit(self, node, depth=0, current=None):
        # `depth` = how many loops we are inside; `current` = function being measured
        if node.type == "function_definition":
            current = {
                "name": _function_name(node),
                "length": node.end_point[0] - node.start_point[0] + 1,
                "complexity": 1,
            }
            self.functions.append(current)
            depth = 0  # loop depth restarts inside each function
        elif node.type in LOOPS:
            self.loops += 1
            depth += 1
            self.max_loop_depth = max(self.max_loop_depth, depth)
            if current:
                current["complexity"] += 1
        elif node.type in ("new_expression", "delete_expression"):
            self.raw_memory_ops += 1
        elif current and _is_branch(node):
            current["complexity"] += 1

        for child in node.children:
            self.visit(child, depth, current)


def analyze(code):
    """Return structural metrics for C++ `code`, or {"error": ...}."""
    if not isinstance(code, str):
        return {"error": "Code must be a string"}

    try:
        parser = _get_parser()
    except ImportError:
        return {"error": INSTALL_HINT}

    try:
        root = parser.parse(code.encode("utf-8")).root_node
        if root.has_error:
            return {"error": f"Invalid C++ code (syntax error near line {_first_error_line(root)})"}
        counter = _Counter()
        counter.visit(root)
    except (RecursionError, MemoryError):
        return {"error": "Code could not be parsed"}

    details = counter.functions
    return {
        "loops": counter.loops,
        "max_loop_depth": counter.max_loop_depth,
        "functions": len(details),
        "max_complexity": max((f["complexity"] for f in details), default=0),
        "longest_function": max((f["length"] for f in details), default=0),
        "raw_memory_ops": counter.raw_memory_ops,
        "function_details": details,
    }
