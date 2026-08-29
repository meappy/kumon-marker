"""Printing service — sends marked worksheets, reports and score cards to CUPS.

Uses the ``lp`` command, so it works with any printer the host already has
configured (the Brother MFC on a home LAN, for example). In a container the
host's CUPS socket needs to be reachable for this to do anything.
"""

import shutil
import subprocess
from pathlib import Path

from app.core.config import get_effective_setting


class PrintError(RuntimeError):
    """Raised when a print job could not be submitted."""


def printing_available() -> bool:
    """Whether the lp/lpstat tools are present at all."""
    return shutil.which("lp") is not None and shutil.which("lpstat") is not None


def _run(args: list[str], timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as e:
        raise PrintError("CUPS tools (lp/lpstat) are not installed") from e
    except subprocess.TimeoutExpired as e:
        raise PrintError(f"{args[0]} timed out") from e

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise PrintError(message or f"{args[0]} failed with code {result.returncode}")
    return result.stdout


def list_printers() -> list[dict]:
    """List configured printers and which one is the default."""
    if not printing_available():
        return []

    try:
        output = _run(["lpstat", "-p", "-d"])
    except PrintError as e:
        print(f"Could not list printers: {e}")
        return []

    printers: list[dict] = []
    default_name = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("printer "):
            parts = line.split()
            if len(parts) >= 2:
                name = parts[1]
                state = (
                    "idle"
                    if " is idle" in line
                    else ("printing" if "now printing" in line else "unknown")
                )
                enabled = "disabled since" not in line
                printers.append(
                    {
                        "name": name,
                        "state": state,
                        "enabled": enabled,
                        "is_default": False,
                    }
                )
        elif line.startswith("system default destination:"):
            default_name = line.split(":", 1)[1].strip()

    configured = get_effective_setting("printer_name", "") or default_name
    for printer in printers:
        printer["is_default"] = printer["name"] == configured

    return printers


def get_default_printer() -> str | None:
    """The configured printer, falling back to the system default."""
    configured = get_effective_setting("printer_name", "")
    if configured:
        return configured
    for printer in list_printers():
        if printer["is_default"]:
            return printer["name"]
    return None


def print_pdf(
    path: Path,
    printer: str | None = None,
    copies: int = 1,
    title: str | None = None,
) -> str:
    """Send a PDF to a printer and return the CUPS job id.

    Worksheets are not A4 — they are roughly square — so jobs are scaled to
    fit the paper rather than cropped.
    """
    if not get_effective_setting("print_enabled", True):
        raise PrintError("Printing is disabled in settings")
    if not path.exists():
        raise PrintError(f"File not found: {path.name}")

    destination = printer or get_default_printer()
    args = ["lp"]
    if destination:
        args += ["-d", destination]
    args += ["-o", "fit-to-page", "-n", str(max(1, copies))]
    if title:
        args += ["-t", title]
    args.append(str(path))

    output = _run(args, timeout=60)

    # "request id is Brother_MFC_L8900CDW_series-63 (1 file(s))"
    for token in output.split():
        if "-" in token and token[-1].isdigit():
            return token
    return output.strip()


def cancel_all(printer: str | None = None) -> None:
    """Cancel queued jobs, for when a print run turns out to be a mistake."""
    destination = printer or get_default_printer()
    args = ["cancel", "-a"]
    if destination:
        args.append(destination)
    _run(args)
