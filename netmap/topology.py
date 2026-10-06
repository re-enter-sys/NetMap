"""
NetMap - Network topology engine.

Builds a graph representation of the discovered network.
"""

from typing import Any


def build_topology(
    interface: dict[str, Any],
    gateway: dict[str, Any] | None,
    devices: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build a network topology graph.

    The gateway acts as the central node.
    All discovered devices are connected to the gateway.
    """

    nodes = []
    edges = []

    local_ip = interface["ip"]
    gateway_ip = gateway["ip"] if gateway else None

    # ---------------------------------------------------------
    # Local host node
    # ---------------------------------------------------------

    nodes.append(
        {
            "id": local_ip,
            "label": interface.get("hostname", "Local Host"),
            "ip": local_ip,
            "role": "Local Host",
            "status": "up",
        }
    )

    # ---------------------------------------------------------
    # Gateway node
    # ---------------------------------------------------------

    if gateway_ip:
        nodes.append(
            {
                "id": gateway_ip,
                "label": "Gateway",
                "ip": gateway_ip,
                "role": "Gateway",
                "status": "up",
            }
        )

        edges.append(
            {
                "source": gateway_ip,
                "target": local_ip,
                "relationship": "gateway",
            }
        )

    # ---------------------------------------------------------
    # Device nodes
    # ---------------------------------------------------------

    for device in devices:

        ip_address = device["ip"]

        # Local host already exists.
        if ip_address == local_ip:
            continue

        # Gateway already exists.
        if ip_address == gateway_ip:
            continue

        nodes.append(
            {
                "id": ip_address,
                "label": device.get("hostname") or ip_address,
                "ip": ip_address,
                "role": device.get("role", "Device"),
                "status": device.get("status", "unknown"),
            }
        )

        # Connect devices to gateway when available.
        if gateway_ip:
            edges.append(
                {
                    "source": gateway_ip,
                    "target": ip_address,
                    "relationship": "network",
                }
            )

    return {
        "nodes": nodes,
        "edges": edges,
    }
