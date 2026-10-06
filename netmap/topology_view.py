"""
NetMap - Interactive topology visualization.

Generates a standalone HTML network topology viewer.
"""

import json
from pathlib import Path
from typing import Any


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>NetMap - Network Topology</title>

<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        background: #0b1020;
        color: #e5e7eb;
        font-family: Arial, Helvetica, sans-serif;
        overflow: hidden;
    }

    header {
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
        background: #111827;
        border-bottom: 1px solid #263244;
    }

    header h1 {
        margin: 0;
        font-size: 22px;
    }

    header span {
        color: #9ca3af;
        font-size: 13px;
    }

    #canvas {
        position: relative;
        width: 100vw;
        height: calc(100vh - 70px);
        overflow: hidden;
    }

    svg {
        width: 100%;
        height: 100%;
        cursor: grab;
    }

    svg:active {
        cursor: grabbing;
    }

    .edge {
        stroke: #64748b;
        stroke-width: 2;
        opacity: 0.7;
    }

    .node {
        cursor: pointer;
    }

    .node-circle {
        stroke: #e5e7eb;
        stroke-width: 2;
    }

    .gateway {
        fill: #2563eb;
    }

    .local {
        fill: #16a34a;
    }

    .device {
        fill: #6b7280;
    }

    .node-label {
        fill: #f9fafb;
        font-size: 13px;
        text-anchor: middle;
        pointer-events: none;
    }

    .node-ip {
        fill: #9ca3af;
        font-size: 11px;
        text-anchor: middle;
        pointer-events: none;
    }

    #legend {
        position: absolute;
        top: 18px;
        left: 18px;
        background: rgba(17, 24, 39, 0.94);
        border: 1px solid #263244;
        border-radius: 10px;
        padding: 14px;
        min-width: 150px;
    }

    #legend h3 {
        margin: 0 0 10px;
        font-size: 13px;
    }

    .legend-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 7px 0;
        font-size: 12px;
        color: #cbd5e1;
    }

    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }

    .dot.gateway {
        background: #2563eb;
    }

    .dot.local {
        background: #16a34a;
    }

    .dot.device {
        background: #6b7280;
    }

    #info {
        position: absolute;
        right: 18px;
        top: 18px;
        width: 250px;
        background: rgba(17, 24, 39, 0.96);
        border: 1px solid #263244;
        border-radius: 10px;
        padding: 16px;
        display: none;
    }

    #info h3 {
        margin-top: 0;
    }

    #info p {
        margin: 7px 0;
        font-size: 12px;
        color: #cbd5e1;
    }
</style>
</head>

<body>

<header>
    <h1>NetMap — Network Topology</h1>
    <span>Interactive Network Discovery</span>
</header>

<div id="canvas">

    <div id="legend">
        <h3>Legend</h3>

        <div class="legend-row">
            <div class="dot gateway"></div>
            Gateway
        </div>

        <div class="legend-row">
            <div class="dot local"></div>
            Local Host
        </div>

        <div class="legend-row">
            <div class="dot device"></div>
            Device
        </div>
    </div>

    <div id="info">
        <h3 id="info-title">Device</h3>
        <p id="info-ip"></p>
        <p id="info-role"></p>
        <p id="info-status"></p>
    </div>

    <svg id="topology"></svg>

</div>

<script>
const topology = TOPOLOGY_DATA;

const svg = document.getElementById("topology");
const info = document.getElementById("info");

const width = window.innerWidth;
const height = window.innerHeight - 70;

const centerX = width / 2;
const centerY = height / 2;

const gateway = topology.nodes.find(
    node => node.role === "Gateway"
);

const otherNodes = topology.nodes.filter(
    node => node.role !== "Gateway"
);

const positions = {};

if (gateway) {
    positions[gateway.id] = {
        x: centerX,
        y: centerY
    };
}

const radius = Math.min(width, height) * 0.28;

otherNodes.forEach((node, index) => {

    const angle =
        (Math.PI * 2 * index) /
        Math.max(otherNodes.length, 1);

    positions[node.id] = {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius
    };
});

function createElement(tag, attributes) {

    const element =
        document.createElementNS(
            "http://www.w3.org/2000/svg",
            tag
        );

    for (const [key, value] of Object.entries(attributes)) {
        element.setAttribute(key, value);
    }

    return element;
}

function nodeClass(role) {

    if (role === "Gateway") {
        return "gateway";
    }

    if (role === "Local Host") {
        return "local";
    }

    return "device";
}

function showInfo(node) {

    document.getElementById("info-title").textContent =
        node.label || node.ip;

    document.getElementById("info-ip").textContent =
        "IP: " + node.ip;

    document.getElementById("info-role").textContent =
        "Role: " + node.role;

    document.getElementById("info-status").textContent =
        "Status: " + node.status;

    info.style.display = "block";
}

function draw() {

    svg.innerHTML = "";

    // Draw edges first.
    topology.edges.forEach(edge => {

        const source = positions[edge.source];
        const target = positions[edge.target];

        if (!source || !target) {
            return;
        }

        const line = createElement("line", {
            x1: source.x,
            y1: source.y,
            x2: target.x,
            y2: target.y,
            class: "edge"
        });

        svg.appendChild(line);
    });

    // Draw nodes.
    topology.nodes.forEach(node => {

        const position = positions[node.id];

        if (!position) {
            return;
        }

        const group = createElement("g", {
            class: "node"
        });

        const circle = createElement("circle", {
            cx: position.x,
            cy: position.y,
            r: 25,
            class: "node-circle " + nodeClass(node.role)
        });

        circle.addEventListener(
            "click",
            () => showInfo(node)
        );

        const label = createElement("text", {
            x: position.x,
            y: position.y + 48,
            class: "node-label"
        });

        label.textContent =
            node.label || node.ip;

        const ip = createElement("text", {
            x: position.x,
            y: position.y + 64,
            class: "node-ip"
        });

        ip.textContent = node.ip;

        group.appendChild(circle);
        group.appendChild(label);
        group.appendChild(ip);

        svg.appendChild(group);
    });
}

draw();

window.addEventListener(
    "resize",
    () => location.reload()
);
</script>

</body>
</html>
"""


def generate_topology_html(
    topology: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """
    Generate a standalone HTML topology visualization.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    topology_json = json.dumps(topology)

    html = HTML_TEMPLATE.replace(
        "TOPOLOGY_DATA",
        topology_json,
    )

    path.write_text(
        html,
        encoding="utf-8",
    )

    return path
