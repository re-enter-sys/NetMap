"""
NetMap - Security report generation.
"""

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from netmap.analytics import (
    dashboard_analytics,
)

from netmap.database import (
    list_alerts,
    list_devices,
)


REPORT_DIRECTORY = Path(
    "reports"
)


def safe(
    value: Any,
) -> str:
    """HTML-escape report values."""

    return html.escape(
        str(value or "")
    )


def build_security_report() -> dict[str, Any]:
    """Build a security assessment report."""

    devices = list_devices()

    alerts = list_alerts()

    analytics = dashboard_analytics()

    high_alerts = [
        alert
        for alert in alerts
        if alert.get("severity")
        in {
            "HIGH",
            "CRITICAL",
        }
    ]

    return {
        "project": "NetMap",

        "generated_at":
            datetime.now().isoformat(),

        "summary": {
            "devices":
                len(devices),

            "alerts":
                len(alerts),

            "high_risk_alerts":
                len(high_alerts),
        },

        "analytics":
            analytics,

        "devices":
            devices,

        "alerts":
            alerts,
    }


def generate_json_report() -> Path:
    """Generate JSON security report."""

    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_security_report()

    path = (
        REPORT_DIRECTORY
        / "security_report.json"
    )

    path.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )

    return path


def generate_html_report() -> Path:
    """Generate a standalone HTML security report."""

    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_security_report()

    summary = report[
        "summary"
    ]

    html_output = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>NetMap Security Report</title>

<style>

body {{
    font-family:
        Arial,
        sans-serif;

    background:
        #111;

    color:
        #eee;

    margin:
        40px;
}}

.card {{
    display:
        inline-block;

    padding:
        20px;

    margin:
        10px;

    background:
        #222;

    border-radius:
        8px;
}}

table {{
    width:
        100%;

    border-collapse:
        collapse;

    margin-top:
        30px;
}}

th,
td {{
    padding:
        10px;

    border-bottom:
        1px solid #333;

    text-align:
        left;
}}

</style>

</head>

<body>

<h1>
NetMap Security Report
</h1>

<p>
Generated:
{safe(report["generated_at"])}
</p>

<div class="card">
<h2>
{safe(summary["devices"])}
</h2>
<p>
Devices
</p>
</div>

<div class="card">
<h2>
{safe(summary["alerts"])}
</h2>
<p>
Alerts
</p>
</div>

<div class="card">
<h2>
{safe(summary["high_risk_alerts"])}
</h2>
<p>
High/Critical Alerts
</p>
</div>

<h2>
Security Analytics
</h2>

<pre>
{safe(json.dumps(
    report["analytics"],
    indent=4,
))}
</pre>

<h2>
Devices
</h2>

<table>

<tr>
<th>IP</th>
<th>Hostname</th>
<th>Role</th>
<th>OS</th>
<th>Last Seen</th>
</tr>
"""

    for device in report[
        "devices"
    ]:

        html_output += f"""
<tr>

<td>
{safe(device.get("ip"))}
</td>

<td>
{safe(device.get("hostname"))}
</td>

<td>
{safe(device.get("role"))}
</td>

<td>
{safe(device.get("os"))}
</td>

<td>
{safe(device.get("last_seen"))}
</td>

</tr>
"""

    html_output += """
</table>

<h2>
Alerts
</h2>

<table>

<tr>
<th>ID</th>
<th>Severity</th>
<th>Title</th>
<th>Status</th>
<th>IP</th>
<th>Timestamp</th>
</tr>
"""

    for alert in report[
        "alerts"
    ]:

        html_output += f"""
<tr>

<td>
{safe(alert.get("id"))}
</td>

<td>
{safe(alert.get("severity"))}
</td>

<td>
{safe(alert.get("title"))}
</td>

<td>
{safe(alert.get("status"))}
</td>

<td>
{safe(alert.get("ip"))}
</td>

<td>
{safe(alert.get("timestamp"))}
</td>

</tr>
"""

    html_output += """
</table>

</body>
</html>
"""

    path = (
        REPORT_DIRECTORY
        / "security_report.html"
    )

    path.write_text(
        html_output,
        encoding="utf-8",
    )

    return path
