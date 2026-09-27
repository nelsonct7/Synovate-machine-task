"""Custom tool 3 - exact arithmetic.

Language models are unreliable at arithmetic, especially with large numbers or
several chained operations. Giving the agent a calculator and telling it to use one
is more reliable than asking it to try harder.
"""

import ast
import logging
import operator

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate(node: ast.AST) -> float:
    """Walk the parsed expression, allowing only numbers and arithmetic operators."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError("only numbers are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError(f"unsupported expression element: {type(node).__name__}")


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression exactly.

    Use this whenever the answer requires a number to be worked out - percentages,
    growth rates, totals, per-unit costs, unit conversions. Do not do arithmetic in
    your head; use this tool so the figure is exact and checkable.

    Args:
        expression: An arithmetic expression such as "(41.3 - 32.3) / 32.3 * 100".
            Supports + - * / // % ** and parentheses. No variables, no function calls.

    Returns:
        The expression and its result.
    """
    logger.info("[TOOL: calculator] expression=%r", expression)
    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
    except Exception as exc:
        return f"Could not evaluate {expression!r}: {exc}"
    return f"{expression} = {result}"
