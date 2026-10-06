"""
NetMap - Network risk scoring.
"""

from typing import Any


HIGH_RISK_PORTS = {
    21,
    23,
    445,
    3389,
    5900,
}


def calculate_device_risk(
    device: dict[str, Any],
    anomalies: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Calculate a 0-100 risk score."""

    score = 0
    factors = []

    services = device.get(
        "services",
        [],
    )

    if not device.get("hostname"):
        score += 5
        factors.append(
            "Unknown hostname"
        )

    if not device.get("vendor"):
        score += 5
        factors.append(
            "Unknown vendor"
        )

    for service in services:

        port = service.get("port")

        if port in HIGH_RISK_PORTS:

            score += 15

            factors.append(
                f"Sensitive service exposed: "
                f"{port}"
            )

    for anomaly in anomalies or []:

        score += {
            "LOW": 5,
            "MEDIUM": 15,
            "HIGH": 25,
            "CRITICAL": 40,
        }.get(
            anomaly.get("severity"),
            5,
        )

        factors.append(
            anomaly.get(
                "message",
                "Network anomaly",
            )
        )

    score = min(
        score,
        100,
    )

    if score >= 80:
        level = "CRITICAL"
    elif score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    elif score > 0:
        level = "LOW"
    else:
        level = "INFO"

    return {
        "score": score,
        "level": level,
        "factors": factors,
    }


def calculate_network_risk(
    devices: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate aggregate network risk."""

    if not devices:
        return {
            "score": 0,
            "level": "INFO",
        }

    scores = [
        calculate_device_risk(
            device
        )["score"]
        for device in devices
    ]

    score = round(
        sum(scores) / len(scores)
    )

    if score >= 80:
        level = "CRITICAL"
    elif score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    elif score > 0:
        level = "LOW"
    else:
        level = "INFO"

    return {
        "score": score,
        "level": level,
    }
