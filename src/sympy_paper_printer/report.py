from __future__ import annotations

import shutil
import subprocess
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
    build_dir: str | Path = "_build_spp",
) -> Path:
    """
    Build a report from a percent-format .py file using:
      1) jupytext:  .py -> .ipynb
      2) nbconvert: execute -> markdown (no input)
      3) pandoc:    markdown -> output (pdf/docx/etc.)

    External tools required on PATH:
      - jupytext (pip-installed; provides CLI)
      - jupyter  (pip-installed; provides nbconvert CLI)
      - pandoc   (system install usually)
      - for pdf: a LaTeX distribution (MiKTeX/TeX Live)

    Notes:
      - Uses a build directory by default to avoid polluting your source folder.
      - If citations are desired, provide both bib and csl (or place exactly one .bib and one .csl next to the script).

    Returns the output path.
    """
    py = Path(python_file).resolve()
    if not py.is_file():
        raise FileNotFoundError(py)

    _require_tool("jupytext")
    _require_tool("jupyter")
    _require_tool("pandoc")

    src_dir = py.parent

    out = Path(output).resolve() if output is not None else py.with_suffix(f".{fmt}")
    if out.suffix.lower() != f".{fmt.lower()}":
        # If user passes output with a different suffix, trust output.
        pass

    bib_path, csl_path = _resolve_bib_csl(src_dir, bib=bib, csl=csl)

    # Build directory (next to the script)
    build_root = (src_dir / build_dir).resolve()
    build_root.mkdir(parents=True, exist_ok=True)

    # Work on copies in build dir
    ipynb = build_root / f"{py.stem}.ipynb"
    md = build_root / f"{py.stem}.md"
    files_dir = build_root / f"{py.stem}_files"

    created_paths: list[Path] = []

    try:
        # 1) jupytext: py -> ipynb
        _run(
            ["jupytext", "--to", "ipynb", str(py), "--output", str(ipynb)],
            cwd=src_dir,
        )
        created_paths.append(ipynb)

        # 2) nbconvert: execute -> markdown (no input)
        nbconvert_cmd = ["jupyter", "nbconvert"]
        if execute:
            nbconvert_cmd += ["--execute"]
        nbconvert_cmd += ["--to", "markdown", "--no-input", str(ipynb)]

        # Important: run with cwd=build_root so markdown + *_files land in build dir
        _run(nbconvert_cmd, cwd=build_root)
        created_paths.append(md)
        if files_dir.exists():
            created_paths.append(files_dir)

        _sanitize_markdown(md)

        # 3) pandoc: md -> output
        pandoc_cmd = [
            "pandoc",
            str(md.name),
            "-s",
            "-N",
            "-o",
            str(out),
            "-V",
            "geometry:margin=1in",
        ]
        if bib_path and csl_path:
            pandoc_cmd += ["--citeproc", f"--bibliography={bib_path}", f"--csl={csl_path}"]

        _run(pandoc_cmd, cwd=build_root)

        if not out.is_file():
            raise ReportBuildError(f"Expected output was not created: {out}")

        return out

    finally:
        if keep_directory_clean:
            _cleanup_build_artifacts(created_paths)
            # If build dir is empty afterwards, remove it
            try:
                if build_root.exists() and build_root.is_dir() and not any(build_root.iterdir()):
                    build_root.rmdir()
            except Exception:
                pass


def _sanitize_markdown(md_path: Path) -> None:
    """
    Small, safe cleanup of nbconvert markdown output.

    - Removes p2j-style lone '%' lines (harmless if absent)
    - (Optionally extend this later if you find other consistent artifacts)
    """
    if not md_path.exists():
        return

    lines = md_path.read_text(encoding="utf-8").splitlines(True)
    lines = [ln for ln in lines if ln.strip("\n") != "%"]
    md_path.write_text("".join(lines), encoding="utf-8")


def _cleanup_build_artifacts(paths: Sequence[Path]) -> None:
    """
    Delete known intermediates we created. Works only inside build dir by design.
    """
    for p in paths:
        try:
            if p.is_dir():
                shutil.rmtree(p)
            elif p.is_file():
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
