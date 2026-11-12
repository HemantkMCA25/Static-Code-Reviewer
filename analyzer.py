"""AST-based static analysis for Python source code."""
import ast

_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_BRANCHES = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While,
             ast.ExceptHandler, ast.comprehension)


def _complexity(func):
    """Cyclomatic complexity of one function (nested functions are skipped,
    they are reported separately)."""
    total = 1
    stack = list(ast.iter_child_nodes(func))
    while stack:
        node = stack.pop()
        if isinstance(node, _FUNCTIONS + (ast.Lambda,)):
            continue
        if isinstance(node, _BRANCHES):
            total += 1
        elif isinstance(node, ast.BoolOp):  # each and/or adds a path
            total += len(node.values) - 1
        stack.extend(ast.iter_child_nodes(node))
    return total


class _Visitor(ast.NodeVisitor):
    def __init__(self):
        self.loops = 0
        self.max_loop_depth = 0
        self.functions = []
        self._depth = 0

    def _visit_loop(self, node):
        self.loops += 1
        self._depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self._depth)
        self.generic_visit(node)
        self._depth -= 1

    visit_For = visit_AsyncFor = visit_While = _visit_loop

    def _visit_function(self, node):
        self.functions.append({
            "name": node.name,
            "length": node.end_lineno - node.lineno + 1,
            "complexity": _complexity(node),
        })
        saved, self._depth = self._depth, 0  # loop depth restarts per function
        self.generic_visit(node)
        self._depth = saved

    visit_FunctionDef = visit_AsyncFunctionDef = _visit_function


def analyze(code):
    """Return structural metrics for `code`, or {"error": ...} if it can't be parsed."""
    if not isinstance(code, str):
        return {"error": "Code must be a string"}

    visitor = _Visitor()
    try:
        visitor.visit(ast.parse(code))
    except SyntaxError as e:
        return {"error": f"Invalid Python code (syntax error: {e.msg}, line {e.lineno})"}
    except (ValueError, RecursionError, MemoryError):
        return {"error": "Code could not be parsed"}

    details = visitor.functions
    return {
        "loops": visitor.loops,
        "max_loop_depth": visitor.max_loop_depth,
        "functions": len(details),
        "max_complexity": max((f["complexity"] for f in details), default=0),
        "longest_function": max((f["length"] for f in details), default=0),
        "function_details": details,
    }