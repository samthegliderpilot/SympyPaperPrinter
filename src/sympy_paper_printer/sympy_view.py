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

    Only targets Derivative nodes w.r.t. exactly t.
    """
    replacements: dict[sp.Expr, sp.Expr] = {}

    # Replace 2nd order first so it doesn't get eaten by 1st order replace.
    for d in expr.atoms(sp.Derivative):
        if d.variables != (t,):
            continue
        inner = d.expr
        # First derivative: d/dt inner
        # Second derivative: if inner itself is Derivative(..., t)
        if isinstance(inner, sp.Derivative) and inner.variables == (t,):
            base = inner.expr
            base_name = _function_display_name(base)
            if base_name is None:
                continue
            replacements[d] = sp.Symbol(rf"\ddot{{{base_name}}}")
        else:
            base_name = _function_display_name(inner)
            if base_name is None:
                continue
            replacements[d] = sp.Symbol(rf"\dot{{{base_name}}}")

    # Now replace base f(t) -> f (symbol) for functions of t
    # We only do it for undefined functions called with t as an argument.
    for fcall in expr.atoms(AppliedUndef):
        if t in fcall.free_symbols and any(arg == t for arg in fcall.args):
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
