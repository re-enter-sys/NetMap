"""
NetMap - Live monitoring dashboard API.

Provides a lightweight Flask API for displaying
current network state, monitoring events, security
alerts, and live monitor health.
"""

from datetime import datetime
import json
from pathlib import Path

from flask import Flask, jsonify, render_template


app = Flask(__name__)


REPORT_PATH = Path(
    "reports/netmap_report.json"
)

TOPOLOGY_PATH = Path(
    "reports/netmap_topology.json"
)

EVENT_LOG = Path(
    "reports/netmap_events.log"
)

HEARTBEAT_FILE = Path(
    "reports/netmap_heartbeat.json"
)

ALERT_FILE = Path(
    "reports/netmap_alerts.json"
)


def read_json(path: Path):
    """Read a JSON file safely."""

    if not path.exists():
        return {}

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):

        return {}


def read_events() -> list[str]:
    """Read monitoring events."""

    if not EVENT_LOG.exists():
        return []

    try:

        with EVENT_LOG.open(
            "r",
            encoding="utf-8",
        ) as file:

            return [
                line.strip()
                for line in file
                if line.strip()
            ]

    except OSError:

        return []


def get_monitor_status() -> dict:
    """Determine live monitor health from heartbeat."""

    heartbeat = read_json(
        HEARTBEAT_FILE
    )

    if not heartbeat:

        return {
            "status": "offline",
            "last_seen": None,
            "age_seconds": None,
        }

    timestamp = heartbeat.get(
        "timestamp"
    )

    if not timestamp:

        return {
            "status": "offline",
            "last_seen": None,
            "age_seconds": None,
        }

    try:

        heartbeat_time = datetime.fromisoformat(
            timestamp
        )

        now = datetime.now()

        age_seconds = (
            now - heartbeat_time
        ).total_seconds()

    except (
        ValueError,
        TypeError,
    ):

        return {
            "status": "offline",
            "last_seen": timestamp,
            "age_seconds": None,
        }

    if age_seconds <= 30:

        status = "running"

    elif age_seconds <= 90:

        status = "stale"

    else:

        status = "offline"

    return {
        "status": status,
        "last_seen": timestamp,
        "age_seconds": round(
            age_seconds,
            1,
        ),
    }


@app.get("/api/status")
def status():
    """Return current NetMap status."""

    report = read_json(
        REPORT_PATH
    )

    topology = read_json(
        TOPOLOGY_PATH
    )

    events = read_events()

    alerts = read_json(
        ALERT_FILE
    )

    if not isinstance(alerts, list):
        alerts = []

    monitor = get_monitor_status()

    return jsonify(
        {
            "project": "NetMap",

            "network":
                report.get(
                    "network",
                    {},
                ),

            "summary":
                report.get(
                    "summary",
                    {},
                ),

            "devices":
                report.get(
                    "devices",
                    [],
                ),

            "topology":
                topology,

            "events":
                events[-50:],

            "last_event":
                events[-1]
                if events
                else None,

            "alerts":
                alerts[-50:],

            "monitor":
                monitor,
        }
    )


@app.get("/api/health")
def health():
    """Health check endpoint."""

    return jsonify(
        {
            "status": "ok",
            "service": "NetMap Dashboard API",
        }
    )


@app.get("/")
def dashboard():
    """Serve the NetMap dashboard."""

    return render_template(
        "dashboard.html"
    )


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
    )
