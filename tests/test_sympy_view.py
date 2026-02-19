import sympy as sp
from sympy_paper_printer.sympy_view import clean_undefined_function_args, dotify_time_derivatives


def test_clean_undefined_function_args_remove_all():
    x, t = sp.Symbol("x"), sp.Symbol("t")
    g = sp.Function("g")(x, t)
    expr = g + sp.cos(x)

    out = clean_undefined_function_args(expr, remove=None)

    # g(x,t) should become Symbol('g') for display
    assert out.has(sp.Symbol("g"))
    assert not out.has(sp.Function("g")(x, t))


def test_clean_undefined_function_args_remove_specific_symbol():
    x, t = sp.Symbol("x"), sp.Symbol("t")
    g = sp.Function("g")(x, t)
    expr = g + sp.cos(x)

    out = clean_undefined_function_args(expr, remove=[t])

    # keep x, remove t => g(x)
    assert out.has(sp.Function("g")(x))
    assert not out.has(sp.Function("g")(x, t))


def test_dotify_value_first_and_second_derivatives():
    t = sp.Symbol("t")
    q = sp.Function("q")(t)

    expr = sp.Derivative(q, t) + 2 * sp.Derivative(q, t, t) + q

    out = dotify_time_derivatives(expr, t)

    # Should contain dot and ddot symbols
    assert out.has(sp.Symbol(r"\dot{q}"))
    assert out.has(sp.Symbol(r"\ddot{q}"))

    # Should replace q(t) with Symbol('q') for display
    assert out.has(sp.Symbol("q"))
    assert not out.has(q)


def test_dotify_ignores_other_variables():
    t = sp.Symbol("t")
    x = sp.Symbol("x")
    q = sp.Function("q")(x)

    expr = sp.Derivative(q, x)
    out = dotify_time_derivatives(expr, t)

    # No changes expected
    assert out == expr
