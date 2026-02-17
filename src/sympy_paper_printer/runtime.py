from __future__ import annotations

import os
import sys
from typing import Literal


RuntimeEnv = Literal["script", "ipython", "jupyter", "vscode", "unknown"]


def _get_ipython_shell_name() -> str | None:
    try:
        from IPython import get_ipython  # type: ignore
        ip = get_ipython()
        if ip is None:
            return None
        return ip.__class__.__name__
    except Exception:
        return None


def runtime_environment() -> RuntimeEnv:
    """
    Best-effort classification:
    - 'jupyter' => ipykernel / notebook/lab
    - 'vscode'  => VS Code interactive/Jupyter extension
    - 'ipython' => terminal IPython (no kernel)
    - 'script'  => normal python execution
    """
    shell = _get_ipython_shell_name()

    # VS Code hints
    if os.environ.get("VSCODE_PID") or os.environ.get("VSCODE_CWD"):
        # VS Code can run both kernel and non-kernel contexts;
        # classify as vscode if we detect VS Code at all.
        return "vscode"

    if shell is None:
        return "script"

    # Common Jupyter kernel shell class
    if shell == "ZMQInteractiveShell":
        return "jupyter"

    # Terminal IPython
    if shell == "TerminalInteractiveShell":
        return "ipython"

    return "unknown"


def is_interactive() -> bool:
    # Covers IPython and some REPL contexts; stable fallback:
    return hasattr(sys, "ps1") or runtime_environment() in ("ipython", "jupyter", "vscode")


def is_jupyter_like() -> bool:
    """
    True for actual Jupyter kernel and VS Code notebook/interactive contexts.
    """
    return runtime_environment() in ("jupyter", "vscode")
