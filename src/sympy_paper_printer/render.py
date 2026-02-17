from __future__ import annotations

from typing import Any, Optional, Tuple, Union
import sympy as sp

from .config import get_config
from .runtime import is_interactive
from .sympy_view import clean_undefined_function_args, dotify_time_derivatives


def md(text: str) -> None:
    """
    Display markdown in notebook-like environments; print in scripts.
    """
    cfg = get_config()
    if cfg.silent:
        return

    if is_interactive():
        try:
            from IPython.display import Markdown, display  # type: ignore
            display(Markdown(text))
            return
        except Exception:
            pass

    print(text)


def eq(lhs_or_eq: Any, rhs: Any = None, *, clean: Optional[bool] = None, t: Optional[sp.Symbol] = None) -> None:
    """
    Display an equation. Accepts:
    - eq(Eq(...))
    - eq(lhs, rhs)
    - eq("x", expr)  -> creates Symbol('x') or MatrixSymbol if rhs is Matrix-like
    """
    cfg = get_config()
    if cfg.silent:
        return

    lhs, rhs2 = _normalize_equation(lhs_or_eq, rhs)

    do_clean = cfg.clean_equations if clean is None else clean
    if do_clean:
        lhs, rhs2 = _to_display(lhs, rhs2, t=t)

    # Display
    if is_interactive():
        try:
            from IPython.display import display  # type: ignore
            display(lhs if rhs2 is None else sp.Eq(lhs, rhs2))
            return
        except Exception:
            pass

    # Script fallback
    print(lhs if rhs2 is None else sp.Eq(lhs, rhs2))


# Alias if you want a more general “show object”
def show(obj: Any) -> None:
    cfg = get_config()
    if cfg.silent:
        return
    if is_interactive():
        try:
            from IPython.display import display  # type: ignore
            display(obj)
            return
        except Exception:
            pass
    print(obj)


def _normalize_equation(lhs_or_eq: Any, rhs: Any) -> Tuple[sp.Expr, Optional[sp.Expr]]:
    if isinstance(lhs_or_eq, sp.Equality):  # Eq
        return lhs_or_eq.lhs, lhs_or_eq.rhs

    lhs = lhs_or_eq
    rhs2 = rhs

    lhs = _coerce_side(lhs, other=rhs2, side="lhs")
    rhs2 = _coerce_side(rhs2, other=lhs, side="rhs") if rhs2 is not None else None

    return lhs, rhs2


def _coerce_side(value: Any, other: Any, *, side: str) -> sp.Expr:
    if isinstance(value, sp.Basic):
        return value
    if isinstance(value, (int, float)):
        return sp.Float(value)
    if isinstance(value, str):
        # Matrix symbol if the other side is matrix-like
        if isinstance(other, (sp.MatrixBase, sp.ImmutableMatrix)):
            rows, cols = other.shape
            return sp.MatrixSymbol(value, rows, cols)
        return sp.Symbol(value)
    raise TypeError(f"Unsupported {side} type: {type(value)!r}")


def _to_display(lhs: sp.Expr, rhs: Optional[sp.Expr], *, t: Optional[sp.Symbol]) -> Tuple[sp.Expr, Optional[sp.Expr]]:
    cfg = get_config()
    if t is None:
        t = sp.Symbol(cfg.dotify_time_symbol)

    def transform(e: sp.Expr) -> sp.Expr:
        out = e
        # dotify first so derivatives are preserved as symbols
        out = dotify_time_derivatives(out, t)

        # argument cleaning (display-only)
        if cfg.clean_args_remove is None:
            out = clean_undefined_function_args(out, remove=None)
        else:
            remove_syms = [sp.Symbol(s) for s in cfg.clean_args_remove]
            out = clean_undefined_function_args(out, remove=remove_syms)

        return out

    lhs2 = transform(lhs)
    rhs2 = transform(rhs) if rhs is not None else None
    return lhs2, rhs2
