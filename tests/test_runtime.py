import sympy_paper_printer.runtime as rt


def test_runtime_environment_returns_valid_value():
    env = rt.runtime_environment()
    assert env in ("script", "ipython", "jupyter", "vscode", "unknown")


def test_is_jupyter_like(monkeypatch):
    monkeypatch.setattr(rt, "runtime_environment", lambda: "jupyter")
    assert rt.is_jupyter_like() is True

    monkeypatch.setattr(rt, "runtime_environment", lambda: "vscode")
    assert rt.is_jupyter_like() is True

    monkeypatch.setattr(rt, "runtime_environment", lambda: "script")
    assert rt.is_jupyter_like() is False
