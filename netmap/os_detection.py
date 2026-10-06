"""
NetMap - Operating system detection.

Uses Nmap OS fingerprinting where supported.
"""

import re
import subprocess
from typing import Any


def detect_os(
    ip_address: str,
) -> dict[str, Any]:
    """Detect the operating system using Nmap."""

    command = [
        "nmap",
        "-O",
        "--osscan-guess",
        ip_address,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return {
            "os": None,
            "confidence": None,
        }

    output = result.stdout

    match = re.search(
        r"OS details:\s*(.+)",
        output,
    )

    if match:
        return {
            "os": match.group(1).strip(),
            "confidence": None,
        }

    match = re.search(
        r"Running:\s*(.+)",
        output,
    )

    if match:
        return {
            "os": match.group(1).strip(),
            "confidence": None,
        }

    return {
        "os": None,
        "confidence": None,
    }
