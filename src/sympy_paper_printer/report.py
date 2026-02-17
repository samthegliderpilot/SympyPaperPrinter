from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


class ReportBuildError(RuntimeError):
    pass


def build_report(
    python_file: str | Path,
    *,
    output: Optional[str | Path] = None,
    fmt: str = "pdf",
    bib: Optional[str | Path] = None,
    csl: Optional[str | Path] = None,
    keep_directory_clean: bool = True,
    execute: bool = True,
) -> Path:
    """
    Convert a #%%-cell Python script into an executed markdown report and then pandoc it to fmt.

    Requires external tools available on PATH:
      - p2j
      - jupyter (nbconvert)
      - pandoc

    Returns output path.
    """
    py = Path(python_file).resolve()
    if not py.is_file():
        raise FileNotFoundError(py)

    _require_tool("p2j")
    _require_tool("jupyter")
    _require_tool("pandoc")

    out = Path(output).resolve() if output is not None else py.with_suffix(f".{fmt}")
    directory = py.parent

    ipynb = py.with_suffix(".ipynb")
    md = py.with_suffix(".md")

    bib_path, csl_path = _resolve_bib_csl(directory, bib=bib, csl=csl)

    # Cleanups: delete only files created during the build, not “everything new in dir”.
    # This is safer than a blanket directory diff.
    created_files: list[Path] = []

    try:
        # 1) p2j
        _run(["p2j", str(py), "-o"], cwd=directory)
        created_files.append(ipynb)

        # 2) nbconvert -> markdown
        nbconvert_cmd = ["jupyter", "nbconvert"]
        if execute:
            nbconvert_cmd += ["--execute"]
        nbconvert_cmd += ["--to", "markdown", "--no-input", str(ipynb)]
        _run(nbconvert_cmd, cwd=directory)
        created_files.append(md)

        _remove_single_percent_lines(md)

        # 3) pandoc
        pandoc_cmd = ["pandoc", str(md), "-s", "-N", "-o", str(out)]
        if bib_path and csl_path:
            pandoc_cmd += ["--citeproc", f"--bibliography={bib_path}", f"--csl={csl_path}"]
        _run(pandoc_cmd, cwd=directory)

        if not out.is_file():
            raise ReportBuildError(f"Expected output was not created: {out}")

        return out

    finally:
        if keep_directory_clean:
            # Remove intermediate build artifacts we know we created.
            for p in created_files:
                try:
                    if p.is_file():
                        p.unlink()
                except Exception:
                    pass


def _resolve_bib_csl(directory: Path, *, bib: Optional[str | Path], csl: Optional[str | Path]) -> tuple[Optional[Path], Optional[Path]]:
    bib_path = Path(bib).resolve() if bib is not None else None
    csl_path = Path(csl).resolve() if csl is not None else None

    if bib_path is None:
        found = sorted(directory.glob("*.bib"))
        bib_path = found[0].resolve() if found else None

    if csl_path is None:
        found = sorted(directory.glob("*.csl"))
        csl_path = found[0].resolve() if found else None

    # If one is present but the other isn't, be explicit.
    if (bib_path is None) ^ (csl_path is None):
        raise ReportBuildError(
            "Citation config incomplete: need both .bib and .csl (or neither). "
            f"Resolved bib={bib_path} csl={csl_path}"
        )

    return bib_path, csl_path


def _remove_single_percent_lines(md_path: Path) -> None:
    # p2j leaves a '%' line per #%% cell; strip them.
    if not md_path.exists():
        return
    lines = md_path.read_text(encoding="utf-8").splitlines(True)
    filtered = [ln for ln in lines if ln.strip("\n") != "%"]
    md_path.write_text("".join(filtered), encoding="utf-8")


def _require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise ReportBuildError(f"Required external tool not found on PATH: {name}")


def _run(cmd: Sequence[str], *, cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        raise ReportBuildError(
            "Command failed:\n"
            f"  cmd: {' '.join(cmd)}\n"
            f"  cwd: {cwd}\n"
            f"  stdout:\n{result.stdout}\n"
            f"  stderr:\n{result.stderr}\n"
        )
