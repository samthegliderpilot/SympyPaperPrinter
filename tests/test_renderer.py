import sympy as sp
import sympy_paper_printer as spp
import sympy_paper_printer.render as render


def test_md_prints_in_script_mode(monkeypatch, capsys):
    monkeypatch.setattr(render, "is_interactive", lambda: False)

    spp.configure(silent=False)
    spp.md("Hello **markdown**")
    out = capsys.readouterr().out
    assert "Hello **markdown**" in out


def test_eq_prints_in_script_mode(monkeypatch, capsys):
    monkeypatch.setattr(render, "is_interactive", lambda: False)

    x = sp.Symbol("x")
    spp.eq("x", sp.sin(x), clean=False)

    out = capsys.readouterr().out
    assert "Eq(" in out or "==" in out or "x" in out  # sympy prints vary a bit


def test_eq_respects_silent(monkeypatch, capsys):
    monkeypatch.setattr(render, "is_interactive", lambda: False)

    spp.configure(silent=True)
    x = sp.Symbol("x")
    spp.eq("x", sp.sin(x), clean=False)

    out = capsys.readouterr().out
    assert out == ""
