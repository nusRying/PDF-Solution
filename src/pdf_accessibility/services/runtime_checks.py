from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from pdf_accessibility.core.settings import Settings


def _candidate_paths(tool_name: str, configured_path: str | None) -> list[Path]:
    candidates: list[Path] = []

    if configured_path:
        candidates.append(Path(configured_path))

    if tool_name == "tesseract":
        candidates.extend(
            [
                Path(sys.prefix) / "Library" / "bin" / "tesseract.exe",
                Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            ]
        )
    elif tool_name == "qpdf":
        candidates.extend(
            [
                Path(sys.prefix) / "Library" / "bin" / "qpdf.exe",
                Path(sys.prefix) / "Scripts" / "qpdf.exe",
            ]
        )

    return candidates


def resolve_executable(tool_name: str, configured_path: str | None) -> str | None:
    on_path = shutil.which(configured_path or tool_name)
    if on_path:
        return on_path

    for candidate in _candidate_paths(tool_name, configured_path):
        if candidate.exists():
            return str(candidate)

    return None


def _candidate_tessdata_paths(settings: Settings, tesseract_path: str | None) -> list[Path]:
    candidates: list[Path] = []

    if tesseract_path:
        tesseract_parent = Path(tesseract_path).resolve().parent
        candidates.append(tesseract_parent / "tessdata")
        candidates.append(tesseract_parent.parent / "tessdata")

    candidates.append(settings.tessdata_prefix)

    candidates.extend(
        [
            Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
            Path(sys.prefix) / "share" / "tessdata",
        ]
    )

    unique_candidates: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate).lower()
        if key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)

    return unique_candidates


def resolve_tessdata_prefix(settings: Settings, tesseract_path: str | None = None) -> Path | None:
    for candidate in _candidate_tessdata_paths(settings, tesseract_path):
        if candidate.exists() and (candidate / f"{settings.default_ocr_language}.traineddata").exists():
            return candidate
    return None


def _get_version(executable: str, args: list[str]) -> tuple[bool, str | None, str | None]:
    try:
        completed = subprocess.run(
            [executable, *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, None, str(exc)
    except subprocess.CalledProcessError as exc:
        error_text = (exc.stderr or exc.stdout or "").strip() or str(exc)
        return False, None, error_text

    output = (completed.stdout or completed.stderr).strip()
    first_line = output.splitlines()[0] if output else None
    return True, first_line, None


def build_runtime_status(settings: Settings) -> dict:
    tesseract_path = resolve_executable("tesseract", settings.tesseract_exe)
    qpdf_path = resolve_executable("qpdf", settings.qpdf_exe)
    tessdata_prefix = resolve_tessdata_prefix(settings, tesseract_path)

    tesseract_ok, tesseract_version, tesseract_error = (
        _get_version(tesseract_path, ["--version"])
        if tesseract_path
        else (False, None, "Not found")
    )
    qpdf_ok, qpdf_version, qpdf_error = (
        _get_version(qpdf_path, ["--version"])
        if qpdf_path
        else (False, None, "Not found")
    )

    tessdata_exists = tessdata_prefix is not None
    ready = all([tesseract_ok, qpdf_ok, tessdata_exists])

    return {
        "ready": ready,
        "tools": {
            "tesseract": {
                "configured_path": settings.tesseract_exe,
                "resolved_path": tesseract_path,
                "available": tesseract_ok,
                "version": tesseract_version,
                "error": tesseract_error,
            },
            "qpdf": {
                "configured_path": settings.qpdf_exe,
                "resolved_path": qpdf_path,
                "available": qpdf_ok,
                "version": qpdf_version,
                "error": qpdf_error,
            },
        },
        "paths": {
            "data_root": str(settings.data_root),
            "tessdata_prefix": str(tessdata_prefix) if tessdata_prefix else None,
            "tessdata_exists": tessdata_exists,
        },
        "ocr": {
            "default_language": settings.default_ocr_language,
        },
    }
