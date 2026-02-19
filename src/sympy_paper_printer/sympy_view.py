from __future__ import annotations

import sympy as sp
from sympy.core.function import AppliedUndef
from typing import Iterable, Optional


def clean_undefined_function_args(expr: sp.Expr, *, remove: Optional[Iterable[sp.Symbol]] = None) -> sp.Expr:
    """
    Display-only: For undefined functions (AppliedUndef), remove certain arguments.

    remove=None => remove all args (turn f(x,t) -> f)
    remove=[t]  => remove only those symbols (turn f(x,t) -> f(x))
    """
    if remove is None:
        remove_set: set[sp.Symbol] | None = None
    else:
        remove_set = set(remove)

    replacements: dict[sp.Expr, sp.Expr] = {}

    for fcall in expr.atoms(AppliedUndef):
        # Keep original argument order but filter args
        if remove_set is None:
            kept_args = []
        else:
            kept_args = [a for a in fcall.args if not (isinstance(a, sp.Symbol) and a in remove_set)]

        if len(kept_args) == 0:
            replacements[fcall] = sp.Symbol(fcall.func.__name__)
        else:
            replacements[fcall] = sp.Function(fcall.func.__name__)(*kept_args)

    if not replacements:
        return expr

    # xreplace is fast and avoids unwanted simplify side-effects
    return expr.xreplace(replacements)


def dotify_time_derivatives(expr: sp.Expr, t: sp.Symbol) -> sp.Expr:
    """
    Display-only: Replace first/second time derivatives of f(t) with symbols \\dot{f}, \\ddot{f}.
    Also replace f(t) with f (symbol) so equations look like classical mechanics notation.

    Only targets Derivative nodes where all differentiation variables are exactly t.
    """
    replacements: dict[sp.Expr, sp.Expr] = {}

    for d in expr.atoms(sp.Derivative):
        # Count how many times we differentiate w.r.t. t
        vars_ = d.variables
        if not vars_:
            continue
        if any(v != t for v in vars_):
            continue

        order = len(vars_)
        base = d.expr
        base_name = _function_display_name(base)
        if base_name is None:
            continue

        if order == 1:
            replacements[d] = sp.Symbol(rf"\dot{{{base_name}}}")
        elif order == 2:
            replacements[d] = sp.Symbol(rf"\ddot{{{base_name}}}")
        else:
            # Optional: represent higher-order derivatives compactly.
            # If you prefer "leave as Derivative(...)" for order>2, just `continue` here.
            replacements[d] = sp.Symbol(rf"{base_name}^{{({order})}}")

    # Replace base f(t) -> f (symbol) for undefined functions called with t
    for fcall in expr.atoms(AppliedUndef):
        if any(arg == t for arg in fcall.args):
            replacements[fcall] = sp.Symbol(fcall.func.__name__)

    if not replacements:
        return expr

    return expr.xreplace(replacements)


def _function_display_name(e: sp.Expr) -> str | None:
    """
    For dotify: accept f(t) where f is undefined or a named function.
    """
    if isinstance(e, AppliedUndef):
        return e.func.__name__

    # If user uses something like Function('\\mu')(t) the __name__ is '\\mu'
    if isinstance(e, sp.Function):
        try:
            return e.__name__  # type: ignore[attr-defined]
        except Exception:
            return None

    return None
