"""
NetMap - Gateway detection.
"""

import re
import subprocess
from typing import Any


def get_default_gateway() -> dict[str, Any] | None:
    """
    Detect the default IPv4 gateway using the Linux routing table.
    """

    result = subprocess.run(
        ["ip", "route", "show", "default"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return None

    match = re.search(
        r"default via (\d+\.\d+\.\d+\.\d+) dev (\S+)",
        result.stdout,
    )

    if not match:
        return None

    return {
        "ip": match.group(1),
        "interface": match.group(2),
    }
