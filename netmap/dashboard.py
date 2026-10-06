"""
NetMap - Security Operations Dashboard.

Provides:
- Authentication
- Device inventory
- Service inventory
- Alerts
- Analytics
- Risk scoring
- Historical information
- Historical topology
- Security reports
- REST API
"""

import json
import os
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from netmap.alerts import (
    acknowledge_alert,
    list_alerts,
    resolve_alert,
)

from netmap.analytics import (
    dashboard_analytics,
)

from netmap.auth import (
    authenticate,
)

from netmap.database import (
    init_database,
    list_devices,
    list_events,
    list_services,
)

from netmap.history import (
    device_history,
    topology_history,
)

from netmap.security_report import (
    generate_html_report,
    generate_json_report,
)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "NETMAP_SECRET_KEY",
    "CHANGE_THIS_SECRET_KEY",
)


REPORT_PATH = Path(
    "reports/netmap_report.json"
)

TOPOLOGY_PATH = Path(
    "reports/netmap_topology.json"
)

HEARTBEAT_PATH = Path(
    "reports/netmap_heartbeat.json"
)


init_database()


# ============================================================================
# Helpers
# ============================================================================

def authenticated():
    """Return whether the current session is authenticated."""

    return bool(
        session.get(
            "authenticated"
        )
    )


def read_json(
    path: Path,
):
    """Read JSON safely."""

    if not path.exists():
        return {}

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
    ):

        return {}


def protected_response():
    """Return an authentication error response."""

    return jsonify(
        {
            "error":
                "Authentication required"
        }
    ), 401


# ============================================================================
# Authentication
# ============================================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST",
    ],
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        )

        password = request.form.get(
            "password",
            "",
        )

        if authenticate(
            username,
            password,
        ):

            session.clear()

            session[
                "authenticated"
            ] = True

            session[
                "username"
            ] = username

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        return render_template(
            "login.html",
            error="Invalid credentials",
        )

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================================
# Dashboard
# ============================================================================

@app.route("/")
def dashboard():

    if not authenticated():

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html",
        username=session.get(
            "username",
            "admin",
        ),
    )


# ============================================================================
# Health
# ============================================================================

@app.route("/api/health")
def health():

    return jsonify(
        {
            "status": "ok",
            "service":
                "NetMap Dashboard API",
        }
    )


# ============================================================================
# Main dashboard status
# ============================================================================

@app.route("/api/status")
def status():

    if not authenticated():
        return protected_response()

    report = read_json(
        REPORT_PATH
    )

    topology = read_json(
        TOPOLOGY_PATH
    )

    heartbeat = read_json(
        HEARTBEAT_PATH
    )

    devices = list_devices()

    alerts = list_alerts(
        limit=500
    )

    events = list_events(
        limit=100
    )

    analytics = dashboard_analytics()

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

            "heartbeat":
                heartbeat,

            "devices":
                devices,

            "topology":
                topology,

            "events":
                events,

            "alerts":
                alerts,

            "analytics":
                analytics,
        }
    )


# ============================================================================
# Devices
# ============================================================================

@app.route("/api/devices")
def devices():

    if not authenticated():
        return protected_response()

    return jsonify(
        list_devices()
    )


@app.route(
    "/api/devices/<path:ip>"
)
def api_device_history(
    ip: str,
):

    if not authenticated():
        return protected_response()

    return jsonify(
        device_history(ip)
    )


# ============================================================================
# Services
# ============================================================================

@app.route("/api/services")
def api_services():

    if not authenticated():
        return protected_response()

    device_id = request.args.get(
        "device_id",
        type=int,
    )

    return jsonify(
        list_services(
            device_id=device_id
        )
    )


# ============================================================================
# Events
# ============================================================================

@app.route("/api/events")
def api_events():

    if not authenticated():
        return protected_response()

    limit = request.args.get(
        "limit",
        default=100,
        type=int,
    )

    severity = request.args.get(
        "severity"
    )

    event_type = request.args.get(
        "event_type"
    )

    return jsonify(
        list_events(
            limit=max(
                1,
                min(limit, 500),
            ),
            severity=severity,
            event_type=event_type,
        )
    )


# ============================================================================
# Alerts
# ============================================================================

@app.route("/api/alerts")
def alerts():

    if not authenticated():
        return protected_response()

    status_filter = request.args.get(
        "status"
    )

    severity_filter = request.args.get(
        "severity"
    )

    alert_type = request.args.get(
        "alert_type"
    )

    limit = request.args.get(
        "limit",
        default=500,
        type=int,
    )

    return jsonify(
        list_alerts(
            status=status_filter,
            severity=severity_filter,
            alert_type=alert_type,
            limit=max(
                1,
                min(limit, 500),
            ),
        )
    )


@app.route(
    "/api/alerts/<int:alert_id>/acknowledge",
    methods=["POST"],
)
def api_acknowledge(
    alert_id: int,
):

    if not authenticated():
        return protected_response()

    username = session.get(
        "username",
        "admin",
    )

    success = acknowledge_alert(
        alert_id,
        username,
    )

    return jsonify(
        {
            "success":
                success,
            "alert_id":
                alert_id,
        }
    )


@app.route(
    "/api/alerts/<int:alert_id>/resolve",
    methods=["POST"],
)
def api_resolve(
    alert_id: int,
):

    if not authenticated():
        return protected_response()

    success = resolve_alert(
        alert_id
    )

    return jsonify(
        {
            "success":
                success,
            "alert_id":
                alert_id,
        }
    )


# ============================================================================
# Historical topology
# ============================================================================

@app.route(
    "/api/topology/history"
)
def api_topology_history():

    if not authenticated():
        return protected_response()

    limit = request.args.get(
        "limit",
        default=50,
        type=int,
    )

    return jsonify(
        topology_history(
            limit=max(
                1,
                min(limit, 100),
            )
        )
    )


# ============================================================================
# Analytics
# ============================================================================

@app.route(
    "/api/analytics"
)
def api_analytics():

    if not authenticated():
        return protected_response()

    return jsonify(
        dashboard_analytics()
    )


# ============================================================================
# Security reports
# ============================================================================

@app.route(
    "/api/reports/security"
)
def security_report():

    if not authenticated():
        return protected_response()

    json_path = (
        generate_json_report()
    )

    html_path = (
        generate_html_report()
    )

    return jsonify(
        {
            "json":
                str(json_path),

            "html":
                str(html_path),
        }
    )


# ============================================================================
# Application entrypoint
# ============================================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
    )
