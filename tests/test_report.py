from pathlib import Path
import pytest

from sympy_paper_printer.report import ReportBuildError, _remove_single_percent_lines, build_report
import sympy_paper_printer.report as report_mod


def test_remove_single_percent_lines(tmp_path: Path):
    md = tmp_path / "x.md"
    md.write_text("a\n%\nb\n%\n", encoding="utf-8")

    _remove_single_percent_lines(md)

    assert md.read_text(encoding="utf-8") == "a\nb\n"


def test_build_report_errors_if_tools_missing(monkeypatch, tmp_path: Path):
    # Create a fake python file
    py = tmp_path / "demo.py"
    py.write_text("#%%\nprint('hi')\n", encoding="utf-8")

    # Make all tools "missing"
    monkeypatch.setattr(report_mod.shutil, "which", lambda name: None)

    with pytest.raises(ReportBuildError) as exc:
        build_report(py, fmt="pdf", keep_directory_clean=True)

    assert "Required external tool not found" in str(exc.value)
