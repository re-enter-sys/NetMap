"""
NetMap - Network topology engine.

Builds a security-aware graph representation of the
discovered network.

The topology is intentionally simple and reliable:
the default gateway acts as the central network node,
with the local host and discovered devices connected
to it.
"""

from typing import Any


def _node_from_device(
    device: dict[str, Any],
    *,
    role: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """Convert a discovered device into a topology node."""

    ip = device.get("ip")

    services = device.get("services") or []

    risk_score = device.get(
        "risk_score",
        device.get("risk", 0),
    )

    risk_level = device.get(
        "risk_level",
        "LOW",
    )

    alert = bool(
        device.get("alert")
        or device.get("has_alert")
        or device.get("alerting")
    )

    return {
        "id": ip,
        "label": (
            device.get("hostname")
            or device.get("label")
            or ip
        ),
        "ip": ip,
        "hostname": device.get("hostname"),
        "mac": device.get("mac"),
        "vendor": device.get("vendor"),
        "role": role or device.get("role", "Device"),
        "status": status or device.get("status", "up"),
        "os": device.get("os"),
        "os_confidence": device.get(
            "os_confidence"
        ),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "services": services,
        "service_count": len(services),
        "alert": alert,
        "has_alert": alert,
        "last_seen": device.get(
            "last_seen"
        ),
    }


def build_topology(
    interface: dict[str, Any],
    gateway: dict[str, Any] | None,
    devices: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the network topology graph.

    Structure:

        Gateway
        ├── Local Host
        ├── Device
        ├── Device
        └── Device

    The gateway remains the central node because the
    scanner discovers devices on the local network but
    does not have reliable layer-2 switch-port topology.
    """

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    local_ip = interface["ip"]

    gateway_ip = (
        gateway.get("ip")
        if gateway
        else None
    )

    # ==============================================================
    # Local host
    # ==============================================================

    local_device = {
        "ip": local_ip,
        "hostname": interface.get(
            "hostname",
            "Local Host",
        ),
        "mac": interface.get("mac"),
        "vendor": "Local",
        "role": "Local Host",
        "status": "up",
    }

    nodes.append(
        _node_from_device(
            local_device,
            role="Local Host",
            status="up",
        )
    )

    # ==============================================================
    # Gateway
    # ==============================================================

    if gateway_ip:

        gateway_device = {
            **gateway,
            "ip": gateway_ip,
            "hostname": gateway.get(
                "hostname",
                "Gateway",
            ),
            "role": "Gateway",
            "status": "up",
        }

        gateway_node = _node_from_device(
            gateway_device,
            role="Gateway",
            status="up",
        )

        nodes.append(
            gateway_node
        )

        edges.append(
            {
                "source": gateway_ip,
                "target": local_ip,
                "relationship": "gateway",
            }
        )

    # ==============================================================
    # Discovered devices
    # ==============================================================

    for device in devices:

        ip_address = device.get("ip")

        if not ip_address:
            continue

        # Avoid duplicate local node.
        if ip_address == local_ip:
            continue

        # Avoid duplicate gateway node.
        if ip_address == gateway_ip:
            continue

        node = _node_from_device(
            device
        )

        nodes.append(
            node
        )

        # ----------------------------------------------------------
        # Current network discovery cannot reliably determine
        # physical switch-port relationships.
        #
        # Therefore discovered hosts are connected to the gateway.
        # ----------------------------------------------------------

        if gateway_ip:

            edges.append(
                {
                    "source": gateway_ip,
                    "target": ip_address,
                    "relationship": "network",
                }
            )

    # ==============================================================
    # Remove duplicate nodes
    # ==============================================================

    unique_nodes: dict[str, dict[str, Any]] = {}

    for node in nodes:

        node_id = node.get("id")

        if node_id:
            unique_nodes[node_id] = node

    nodes = list(
        unique_nodes.values()
    )

    # ==============================================================
    # Remove duplicate edges
    # ==============================================================

    unique_edges: dict[
        tuple[str, str, str],
        dict[str, Any],
    ] = {}

    for edge in edges:

        key = (
            edge.get("source"),
            edge.get("target"),
            edge.get("relationship", ""),
        )

        unique_edges[key] = edge

    edges = list(
        unique_edges.values()
    )

    # ==============================================================
    # Final topology object
    # ==============================================================

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }
