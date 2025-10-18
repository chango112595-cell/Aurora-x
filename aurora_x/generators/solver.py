"""
Aurora-X Universal Solver Module
Provides mathematical and physics solving capabilities
"""

import math
import re
from typing import Any


class SolveError(Exception):
    """Custom exception for solver errors"""
    pass


def _diff_poly(expression: str) -> str:
    """
    Differentiate a polynomial expression with respect to x

    Args:
        expression: Polynomial expression like "x^3 - 2x^2 + x"

    Returns:
        Differentiated expression as string

    Example:
        >>> _diff_poly("x^3 - 2x^2 + x")
        "3x^2 - 4x + 1"
    """
    # Clean the expression (remove extra spaces and quotes)
    expression = expression.strip().strip('"').strip("'")

    # Parse terms from the expression
    terms = []

    # Split by + or - while keeping the sign
    parts = re.split(r'([+-])', expression.replace(' ', ''))

    # Reconstruct terms with their signs
    current_term = ''
    for part in parts:
        if part in ['+', '-']:
            if current_term:
                terms.append(current_term)
            current_term = part
        else:
            current_term += part
    if current_term:
        terms.append(current_term)

    # Differentiate each term
    diff_terms = []
    for term in terms:
        # Extract coefficient and power
        if 'x^' in term:
            # Handle x^n terms
            match = re.match(r'([+-]?\d*\.?\d*)x\^(\d+)', term)
            if match:
                coeff_str = match.group(1)
                power = int(match.group(2))

                # Handle implicit coefficient
                if coeff_str in ['', '+']:
                    coeff = 1
                elif coeff_str == '-':
                    coeff = -1
                else:
                    coeff = float(coeff_str)

                # Apply power rule
                new_coeff = coeff * power
                new_power = power - 1

                if new_power == 0:
                    diff_terms.append(f"{new_coeff:g}")
                elif new_power == 1:
                    diff_terms.append(f"{new_coeff:g}x")
                else:
                    diff_terms.append(f"{new_coeff:g}x^{new_power}")
        elif 'x' in term:
            # Handle x terms (power = 1)
            match = re.match(r'([+-]?\d*\.?\d*)x', term)
            if match:
                coeff_str = match.group(1)

                # Handle implicit coefficient
                if coeff_str in ['', '+']:
                    coeff = 1
                elif coeff_str == '-':
                    coeff = -1
                else:
                    coeff = float(coeff_str)

                diff_terms.append(f"{coeff:g}")
        # Constants differentiate to 0, so we skip them

    if not diff_terms:
        return "0"

    # Join terms with proper signs
    result = diff_terms[0]
    for term in diff_terms[1:]:
        if term.startswith('-'):
            result += f" - {term[1:]}"
        else:
            result += f" + {term}"

    return result


def _safe_eval_arith(s: str) -> float:
    """
    Safely evaluate an arithmetic expression using AST parsing

    Args:
        s: Arithmetic expression like "2 + 3 * 4"

    Returns:
        Evaluated result as float

    Raises:
        SolveError: If expression contains unsafe operations

    Example:
        >>> _safe_eval_arith("2 + 3 * 4")
        14.0
    """
    import ast
    import operator

    # Define allowed operators
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos
    }

    def eval_(node):
        # Handle numbers
        if isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.Constant):  # Python >= 3.8
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise SolveError("Only numeric constants allowed")
        # Handle unary operations
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) in ops:
                return ops[type(node.op)](eval_(node.operand))
            else:
                raise SolveError(f"Unsupported unary operator: {type(node.op).__name__}")
        # Handle binary operations
        elif isinstance(node, ast.BinOp):
            if type(node.op) in ops:
                return ops[type(node.op)](eval_(node.left), eval_(node.right))
            else:
                raise SolveError(f"Unsupported binary operator: {type(node.op).__name__}")
        # Handle expression wrapper
        elif isinstance(node, ast.Expression):
            return eval_(node.body)
        else:
            raise SolveError(f"Disallowed expression type: {type(node).__name__}")

    try:
        tree = ast.parse(s, mode="eval")
        return float(eval_(tree))
    except (SyntaxError, ValueError) as e:
        raise SolveError(f"Invalid arithmetic expression: {str(e)}") from e
    except ZeroDivisionError as e:
        raise SolveError("Division by zero") from e
    except Exception as e:
        raise SolveError(f"Error evaluating expression: {str(e)}") from e


def solve_text(text: str) -> dict[str, Any]:
    """
    Universal solver that handles various mathematical and physics problems

    Args:
        text: Natural language or mathematical expression

    Returns:
        Dict with solution results
    """
    text = text.strip()

    # Check for differentiation requests
    if 'differentiate' in text.lower() or 'derivative' in text.lower():
        # Extract polynomial expression
        # Try to find expression after "differentiate" or in quotes
        patterns = [
            r'differentiate\s+(.+)',
            r'derivative\s+of\s+(.+)',
            r'"([^"]+)"',
            r'\'([^\']+)\''
        ]

        expression = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expression = match.group(1).strip()
                break

        if not expression:
            # Try to extract polynomial-like expression
            poly_match = re.search(r'([x\d\^\+\-\s\.]+)', text)
            if poly_match and 'x' in poly_match.group(1):
                expression = poly_match.group(1)

        if expression:
            try:
                result = _diff_poly(expression)
                return {
                    "ok": True,
                    "domain": "math",
                    "task": "differentiate",
                    "input": expression,
                    "result": result,
                    "explanation": f"The derivative of {expression} with respect to x is {result}"
                }
            except Exception as e:
                return {
                    "ok": False,
                    "domain": "math",
                    "task": "differentiate",
                    "error": str(e)
                }

    # Check for orbital period calculations
    if 'orbital' in text.lower() and 'period' in text.lower():
        # Extract parameters using regex
        params = {}

        # Look for semi-major axis (a)
        a_match = re.search(r'a\s*=\s*([\d\.e\+\-]+)', text, re.IGNORECASE)
        if a_match:
            params['a'] = float(a_match.group(1))

        # Look for mass (M)
        m_match = re.search(r'M\s*=\s*([\d\.e\+\-]+)', text, re.IGNORECASE)
        if m_match:
            params['M'] = float(m_match.group(1))

        if 'a' in params and 'M' in params:
            try:
                # Calculate orbital period using Kepler's Third Law
                # T = 2π√(a³/GM)
                G = 6.67430e-11  # Gravitational constant in m³/(kg·s²)
                a = params['a']
                M = params['M']

                T_seconds = 2 * math.pi * math.sqrt((a**3) / (G * M))
                T_days = T_seconds / 86400
                T_years = T_days / 365.25

                return {
                    "ok": True,
                    "domain": "physics",
                    "task": "orbital_period",
                    "input": {
                        "semi_major_axis_m": a,
                        "mass_central_kg": M
                    },
                    "result": {
                        "period_seconds": T_seconds,
                        "period_days": T_days,
                        "period_years": T_years
                    },
                    "explanation": f"Orbital period for a={a:.2e}m and M={M:.2e}kg is {T_days:.2f} days"
                }
            except Exception as e:
                return {
                    "ok": False,
                    "domain": "physics",
                    "task": "orbital_period",
                    "error": str(e)
                }

    # Try to evaluate as arithmetic expression
    # Check if it looks like an arithmetic expression
    if re.match(r'^[\d\s\+\-\*/\(\)\.]+$', text):
        try:
            result = _safe_eval_arith(text)
            return {
                "ok": True,
                "domain": "math",
                "task": "arithmetic",
                "input": text,
                "result": result,
                "explanation": f"{text} = {result}"
            }
        except SolveError as e:
            return {
                "ok": False,
                "domain": "math",
                "task": "arithmetic",
                "error": str(e)
            }

    # Default response for unrecognized inputs
    return {
        "ok": False,
        "error": "Could not recognize the problem type",
        "hint": "Try: arithmetic (2+3*4), differentiation (differentiate x^3-2x^2+x), or orbital period (orbital period a=7e6 M=5.972e24)"
    }
