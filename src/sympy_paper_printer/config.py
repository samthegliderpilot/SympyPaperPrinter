from __future__ import annotations

from dataclasses import dataclass, replace
from contextlib import contextmanager
from typing import Iterator, Optional


@dataclass(frozen=True)
class Config:
    silent: bool = False
    clean_equations: bool = True
    dotify_time_symbol: str = "t"
    # When cleaning arguments from undefined functions, which symbols to remove by default:
    clean_args_remove: Optional[tuple[str, ...]] = None  # None => remove all args (display-only)


_CONFIG = Config()


def get_config() -> Config:
    return _CONFIG


def configure(**kwargs) -> None:
    """
    Mutate the module-level config (global-ish).
    Example: configure(silent=True, clean_equations=False)
    """
    global _CONFIG
    _CONFIG = replace(_CONFIG, **kwargs)


@contextmanager
def configured(**kwargs) -> Iterator[None]:
    """
    Temporarily override config within a scope.

    with configured(clean_equations=False):
        ...
    """
    global _CONFIG
    old = _CONFIG
    _CONFIG = replace(_CONFIG, **kwargs)
    try:
        yield
    finally:
        _CONFIG = old
