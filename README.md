# NetMap

### Linux Network Discovery • Device Intelligence • Live Monitoring • Security Operations

<p align="center">
  <strong>A Python-based network security monitoring platform for discovering devices, identifying services, tracking network changes, detecting anomalies, scoring risk, and investigating security events.</strong>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Linux](https://img.shields.io/badge/Platform-Linux-black?logo=linux)
![Nmap](https://img.shields.io/badge/Scanner-Nmap-4682B4)
![Flask](https://img.shields.io/badge/Dashboard-Flask-000000?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![Pytest](https://img.shields.io/badge/Tests-24%20passing-0A9EDC?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-2.0.0-orange)

</p>

---

# 📌 Overview

**NetMap** is a Linux-based network discovery and security monitoring platform written in Python.

It started as a lightweight network discovery and topology mapping tool and evolved into a security-focused monitoring platform capable of:

* discovering devices on an authorized network
* identifying MAC addresses and vendors
* classifying devices
* detecting open ports and services
* identifying service versions
* attempting operating system fingerprinting
* continuously monitoring network changes
* detecting new and removed devices
* detecting MAC, port, and OS changes
* generating security alerts
* calculating device and network risk
* storing historical network information
* maintaining topology history
* providing an authenticated SOC-style dashboard
* generating security reports
* exposing protected REST APIs

NetMap is designed as a **practical cybersecurity portfolio project** demonstrating concepts relevant to:

* Security Operations Centers
* Network Security
* Network Monitoring
* Threat Detection
* Alert Triage
* Security Investigation
* Incident Detection
* Linux Administration
* Python Automation
* REST API Development
* Security Analytics

> **⚠️ Authorized Use Only:** NetMap should only be used on networks and systems that you own or have explicit permission to monitor.

---

# 🎯 Project Goal

The primary goal of NetMap is to answer a simple security question:

> **"What devices are on my network, what are they exposing, and what changed?"**

Instead of performing a single network scan and throwing away the results, NetMap maintains an evolving view of the network.

```text
                    NETWORK
                       │
                       ▼
               ┌───────────────┐
               │   DISCOVERY   │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ IDENTIFICATION│
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │   ENRICHMENT  │
               └───────┬───────┘
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
         Services     OS      Fingerprint
             │         │         │
             └─────────┼─────────┘
                       ▼
               ┌───────────────┐
               │   BASELINE    │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ CHANGE /      │
               │ ANOMALY       │
               │ DETECTION     │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ RISK SCORING  │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ SECURITY      │
               │ ALERT         │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ INVESTIGATION │
               └───────────────┘
```

---

# 🚀 NetMap 2.0

NetMap 2.0 significantly expands the original network scanner into a persistent network security monitoring platform.

## Major capabilities

### 🔎 Network Discovery

* IPv4 interface discovery
* Automatic local network detection
* Gateway detection
* Nmap host discovery
* Active device discovery
* Hostname collection
* MAC address collection
* Vendor identification

### 🧠 Device Intelligence

* Device fingerprinting
* Device role classification
* Device type identification
* Local host identification
* Gateway identification
* Vendor analysis
* Device observation tracking

### 🔐 Service Discovery

* TCP service discovery
* Open-port detection
* Service identification
* Service version detection
* Historical service tracking
* New-port detection

### 🖥️ Operating System Detection

NetMap integrates Nmap OS fingerprinting to attempt operating system identification.

Example:

```text
Device
 ├── IP: 10.10.10.1
 ├── MAC: AA:BB:CC:DD:EE:01
 ├── Vendor: VMware
 ├── Role: Gateway
 └── OS: VMware Player virtual NAT device
```

OS detection depends on the target system, network conditions, Nmap fingerprint availability, and scan privileges.

### 📡 Live Monitoring

NetMap continuously scans the authorized network and compares the current state against previous observations.

It can detect:

* New devices
* Removed devices
* MAC address changes
* New ports
* Closed ports
* Operating system changes
* Network anomalies

### 🚨 Security Alerting

Alerts are generated from detected network changes and anomalies.

Supported severity levels:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Alerts support:

* persistence
* severity
* status
* acknowledgement
* resolution
* filtering
* historical investigation

### 📊 Risk Scoring

NetMap calculates:

* device-level risk
* network-level risk

Risk considers security-relevant characteristics such as exposed services and detected anomalies.

Example:

```text
Device Risk

Score: 72
Level: HIGH

Factors:
- Multiple exposed services
- Security anomaly detected
- Unexpected network change
```

### 🗄️ Historical Database

NetMap 2.0 uses SQLite to maintain persistent information about the network.

Stored information includes:

* devices
* services
* events
* alerts
* topology snapshots
* device observations
* historical state

### 🖥️ SOC Dashboard

The Flask dashboard provides a centralized security operations view.

Dashboard capabilities include:

* authenticated login
* network status
* device inventory
* service inventory
* alert management
* risk score
* analytics
* events
* topology history
* security reports

### 📄 Security Reports

NetMap can generate:

* JSON security reports
* HTML security reports
* JSON network reports
* CSV device reports
* topology HTML

---

# 🖼️ Screenshots

## Security Dashboard

The NetMap dashboard provides a centralized view of devices, services, alerts, risk, events, analytics, and network topology.

<p align="center">
  <img src="screenshots/dashboard.png" alt="NetMap 2.0 Security Dashboard" width="100%">
</p>

---

## Network Topology

NetMap generates an interactive topology representation of the discovered network.

<p align="center">
  <img src="screenshots/topology.png" alt="NetMap Network Topology" width="90%">
</p>

---

## Live Monitoring

The monitoring engine repeatedly scans the network and compares each scan against the previous network state.

<p align="center">
  <img src="screenshots/live-monitor.png" alt="NetMap Live Monitoring" width="90%">
</p>

---

## Network Discovery

Initial network discovery identifies active hosts and network information.

<p align="center">
  <img src="screenshots/network-scan.png" alt="NetMap Network Discovery" width="90%">
</p>

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │   Authorized LAN     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Network Discovery  │
                         │                      │
                         │  psutil + Nmap       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │      Device Intelligence     │
                    │                              │
                    │ Fingerprinting               │
                    │ Classification               │
                    │ Vendor Detection             │
                    │ Gateway Detection            │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
             ┌────────────┐ ┌────────────┐ ┌────────────┐
             │  Services  │ │ OS Detect  │ │   Device   │
             │  -sV       │ │    -O      │ │  Metadata  │
             └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                   │              │              │
                   └──────────────┼──────────────┘
                                  ▼
                         ┌──────────────────────┐
                         │ Historical Database  │
                         │       SQLite         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Security Engine      │
                         │                      │
                         │ Change Detection     │
                         │ Anomaly Detection    │
                         │ Risk Scoring         │
                         │ Alert Generation     │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
              ┌────────────┐ ┌────────────┐ ┌────────────┐
              │   Events   │ │   Alerts   │ │ Topology   │
              │   History  │ │   History  │ │  History   │
              └────────────┘ └────────────┘ └────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Flask Dashboard   │
                         │                      │
                         │ Devices              │
                         │ Services             │
                         │ Alerts               │
                         │ Risk                 │
                         │ Analytics             │
                         │ Events               │
                         │ Topology              │
                         │ Reports               │
                         └──────────────────────┘
```

---

# 🔐 Security Operations Workflow

NetMap follows a simplified SOC-style monitoring workflow.

```text
┌──────────────┐
│   DISCOVER   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  IDENTIFY    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ENRICH     │
│              │
│ Fingerprint  │
│ Services     │
│ OS           │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   COMPARE    │
│              │
│ New Device   │
│ Removed      │
│ MAC Change   │
│ New Port     │
│ OS Change    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ANALYZE    │
│              │
│ Anomalies    │
│ Risk         │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    ALERT     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ INVESTIGATE  │
│              │
│ History      │
│ Services     │
│ Events       │
│ Topology     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    RESPOND   │
│              │
│ Acknowledge  │
│ Resolve      │
└──────────────┘
```

---

# 🧩 Core Components

## `network.py`

Responsible for discovering the local network environment.

Capabilities:

* interface detection
* IPv4 detection
* subnet detection
* network calculation
* MAC address retrieval

---

## `scanner.py`

Responsible for Nmap host discovery.

Example command concept:

```bash
nmap -sn 10.10.10.0/24
```

The scanner extracts:

* IP address
* hostname
* MAC address
* vendor
* host status

---

## `gateway.py`

Detects the default gateway from the Linux routing table.

Example:

```bash
ip route show default
```

---

## `classifier.py`

Classifies discovered devices.

Example classifications:

```text
Local Host
Gateway
Device
Unknown
```

---

## `fingerprint.py`

Builds additional device intelligence from available network metadata.

Fingerprinting can include:

* vendor
* MAC prefix
* hostname
* device role
* observed services
* operating system information

---

## `services.py`

Performs service discovery using Nmap.

Conceptually:

```bash
nmap -sV --open -T3 <target>
```

Collected information includes:

```text
Port
Protocol
Service
Version
```

Example:

```text
53/tcp
service: domain
version: dnsmasq 2.83
```

---

## `os_detection.py`

Attempts operating system identification using Nmap.

Conceptually:

```bash
nmap -O --osscan-guess <target>
```

The result is stored with the device history when available.

---

## `database.py`

Provides the SQLite persistence layer.

The database stores:

```text
Devices
Services
Events
Alerts
Topology Snapshots
Baselines
```

This allows NetMap to retain historical context between monitoring cycles.

---

## `history.py`

Provides historical investigation functionality.

Capabilities include:

* device history
* device services
* device events
* device alerts
* topology history
* latest inventory

---

## `monitor.py`

Compares network states.

Conceptually:

```text
Previous Scan
      │
      ▼
Current Scan
      │
      ▼
┌─────────────────────┐
│ State Comparison    │
├─────────────────────┤
│ Added Devices       │
│ Removed Devices     │
│ Changed Devices     │
│ Unchanged Devices   │
└─────────────────────┘
```

---

## `anomaly.py`

Analyzes network changes and generates security-relevant anomalies.

Potential anomaly categories include:

* unexpected device
* unexpected service
* MAC address change
* operating system change
* unusual device state

---

## `risk.py`

Calculates security risk.

The system produces:

```text
Risk Score
Risk Level
Risk Factors
```

Example levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## `alerts.py`

Provides the alert engine.

Alert lifecycle:

```text
OPEN
 │
 ├── ACKNOWLEDGED
 │
 └── RESOLVED
```

Alerts can be filtered by:

* severity
* status
* alert type

---

## `analytics.py`

Provides dashboard analytics.

Analytics include:

* device counts
* service counts
* event counts
* alert counts
* severity distribution
* service distribution
* device roles
* operating systems
* network risk

---

## `topology.py`

Builds the logical network topology.

Example:

```text
                 Gateway
                    │
          ┌─────────┴─────────┐
          │                   │
       Local Host           Device
```

---

## `topology_view.py`

Generates a standalone HTML visualization of the network topology.

The topology view is designed to work without requiring an external frontend framework.

---

## `security_report.py`

Generates security reports in:

* JSON
* HTML

Reports include:

* network analytics
* devices
* services
* alerts
* risk information

---

## `auth.py`

Provides dashboard authentication.

Configuration is environment-variable based.

Supported settings:

```text
NETMAP_ADMIN_USER
NETMAP_ADMIN_PASSWORD
NETMAP_SECRET_KEY
```

For production environments, credentials should be configured securely rather than relying on development defaults.

---

## `dashboard.py`

Provides the Flask web dashboard and protected API.

Dashboard features include:

* authentication
* device inventory
* service inventory
* security alerts
* analytics
* risk score
* event history
* topology history
* report generation

---

# 📡 REST API

NetMap exposes a lightweight REST API through Flask.

## Health

```http
GET /api/health
```

Returns the application health state.

---

## Network Status

```http
GET /api/status
```

Returns current network monitoring information.

---

## Devices

```http
GET /api/devices
```

Returns the current device inventory.

---

## Device History

```http
GET /api/devices/<ip>
```

Returns historical information for a device.

---

## Services

```http
GET /api/services
```

Returns discovered network services.

---

## Events

```http
GET /api/events
```

Returns monitoring and security events.

---

## Alerts

```http
GET /api/alerts
```

Returns security alerts.

Optional filters include:

```text
status
severity
alert_type
```

---

## Acknowledge Alert

```http
POST /api/alerts/<id>/acknowledge
```

Marks an alert as acknowledged.

---

## Resolve Alert

```http
POST /api/alerts/<id>/resolve
```

Marks an alert as resolved.

---

## Analytics

```http
GET /api/analytics
```

Returns network security analytics.

---

## Historical Topology

```http
GET /api/topology/history
```

Returns stored topology snapshots.

---

## Security Report

```http
GET /api/reports/security
```

Generates or returns the security report.

---

# 📊 Dashboard

The NetMap dashboard provides a lightweight SOC-style interface.

The dashboard presents:

```text
┌─────────────────────────────────────────────────┐
│                 NETMAP SOC                      │
├─────────────────────────────────────────────────┤
│ Devices │ Services │ Alerts │ Risk │ Events     │
├─────────────────────────────────────────────────┤
│                                                 │
│             NETWORK STATUS                     │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│             TOPOLOGY VIEW                      │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│             SECURITY ALERTS                    │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│             DEVICE INVENTORY                   │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│             SERVICE INVENTORY                  │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│             ANALYTICS                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

# 🚨 Alert Lifecycle

NetMap alerts follow a simple analyst workflow.

```text
             Detection
                 │
                 ▼
              ┌─────┐
              │ OPEN│
              └──┬──┘
                 │
          Analyst Review
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐  ┌───────────────┐
│ ACKNOWLEDGED  │  │     OPEN      │
└───────┬───────┘  └───────────────┘
        │
        ▼
┌───────────────┐
│   RESOLVED    │
└───────────────┘
```

This models a simplified real-world SOC alert handling process.

---

# 🔍 Example Investigation

Suppose an unknown device appears on the network.

NetMap can process it as follows:

```text
New Device Detected
        │
        ▼
MAC / Vendor Collection
        │
        ▼
Device Fingerprinting
        │
        ▼
Service Discovery
        │
        ▼
OS Detection
        │
        ▼
Risk Calculation
        │
        ▼
Security Alert
        │
        ▼
SQLite Persistence
        │
        ▼
Dashboard
        │
        ▼
Analyst Investigation
```

The analyst can then inspect:

* IP address
* MAC address
* vendor
* hostname
* role
* open ports
* services
* operating system
* historical events
* alerts
* risk score
* topology context

---

# 🗄️ Historical Intelligence

NetMap 2.0 is designed around persistent network history.

## Device history

A device can be tracked over multiple monitoring cycles.

Example:

```text
Device: 10.10.10.1

Observation 1
  Vendor: VMware
  Role: Gateway

Observation 2
  Vendor: VMware
  Role: Gateway

Observation 3
  Vendor: VMware
  Role: Gateway
```

---

## Service history

Services are associated with devices and stored for historical analysis.

Example:

```text
Device
 └── 10.10.10.1
      └── TCP/53
           ├── domain
           └── dnsmasq 2.83
```

---

## Topology history

Every monitoring cycle can create a topology snapshot.

This enables investigation of how the network changed over time.

```text
Snapshot 1
    │
    ▼
Snapshot 2
    │
    ▼
Snapshot 3
    │
    ▼
Snapshot 4
```

---

# 🧮 Risk Scoring

NetMap provides a lightweight security risk model.

Risk is calculated from observable network characteristics.

Potential factors include:

* number of exposed services
* suspicious network changes
* detected anomalies
* device state
* service exposure

The result is represented as:

```text
Risk Score: 0-100

0 ─────────────────────────────── 100
│             │          │        │
LOW         MEDIUM      HIGH   CRITICAL
```

The scoring engine is intended for **security monitoring and prioritization**, not as a replacement for a full enterprise risk-management framework.

---

# 🧠 Anomaly Detection

NetMap compares the current network state with previously observed state.

Example:

```text
Previous State
10.10.10.20
    └── 22/tcp

Current State
10.10.10.20
    ├── 22/tcp
    └── 8080/tcp
```

The newly observed port can become a security-relevant change.

Other examples:

```text
New Device
    ↓
Anomaly

MAC Changed
    ↓
Anomaly

OS Changed
    ↓
Anomaly

New Service
    ↓
Anomaly
```

---

# 🧪 Testing

NetMap uses `pytest` for automated testing.

Current validation:

```text
24 passed
```

Run the test suite:

```bash
python -m pytest -q
```

Verbose mode:

```bash
python -m pytest -v
```

Expected result:

```text
........................
24 passed
```

Python compilation check:

```bash
python -m compileall -q netmap
```

---

# 🧰 Technology Stack

| Technology          | Purpose                                     |
| ------------------- | ------------------------------------------- |
| Python              | Core application                            |
| Linux               | Runtime platform                            |
| Nmap                | Network discovery, service and OS detection |
| psutil              | Network interface information               |
| Flask               | Dashboard and REST API                      |
| SQLite              | Historical persistence                      |
| Werkzeug            | Authentication/password hashing             |
| Pytest              | Automated testing                           |
| HTML/CSS/JavaScript | Dashboard UI                                |
| JSON                | Data exchange/reporting                     |
| CSV                 | Device reporting                            |

---

# 📁 Project Structure

```text
NetMap/
│
├── netmap/
│   │
│   ├── __init__.py
│   ├── cli.py
│   │
│   ├── network.py
│   ├── scanner.py
│   ├── gateway.py
│   ├── classifier.py
│   │
│   ├── fingerprint.py
│   ├── services.py
│   ├── os_detection.py
│   │
│   ├── monitor.py
│   ├── live.py
│   ├── anomaly.py
│   ├── risk.py
│   ├── alerts.py
│   │
│   ├── database.py
│   ├── history.py
│   ├── analytics.py
│   │
│   ├── topology.py
│   ├── topology_view.py
│   │
│   ├── reporter.py
│   ├── security_report.py
│   │
│   ├── auth.py
│   ├── dashboard.py
│   │
│   └── templates/
│       ├── dashboard.html
│       └── login.html
│
├── tests/
│   ├── test_alerts.py
│   ├── test_classifier.py
│   ├── testgateway.local.py
│   ├── test_monitor.py
│   ├── test_network.py
│   ├── test_reporter.py
│   ├── test_scanner.py
│   ├── test_topology.py
│   └── test_topology_view.py
│
├── reports/
│
├── screenshots/
│   ├── dashboard.png
│   ├── live-monitor.png
│   ├── network-scan.png
│   └── topology.png
│
├── requirements.txt
├── pytest.ini
├── .gitignore
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/re-enter-sys/NetMap.git
cd NetMap
```

Replace the repository URL with your fork or repository URL if necessary.

---

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

If your Linux environment requires system packages such as `psutil`, install them through the distribution package manager when appropriate.

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Requirements include:

```text
psutil
Flask
Werkzeug
pytest
```

Nmap must also be installed separately.

---

# 🔧 Nmap Installation

On Debian/Kali-based systems:

```bash
sudo apt update
sudo apt install nmap
```

Verify:

```bash
nmap --version
```

---

# ▶️ Running NetMap

## Network Discovery

Run the command-line discovery workflow:

```bash
python -m netmap.cli
```

---

# 📡 Live Monitoring

Start the continuous network monitor:

```bash
python -m netmap.live
```

NetMap will:

1. identify the local interface
2. determine the local network
3. identify the gateway
4. perform network discovery
5. fingerprint devices
6. discover services
7. attempt OS detection
8. compare network state
9. detect anomalies
10. calculate risk
11. generate alerts
12. store historical information
13. update topology
14. update dashboard data

---

# 🖥️ Dashboard

Start the dashboard:

```bash
python -m netmap.dashboard
```

The dashboard runs on:

```text
http://127.0.0.1:5001
```

The dashboard requires authentication.

Configure credentials before deployment:

```bash
export NETMAP_ADMIN_USER="admin"
export NETMAP_ADMIN_PASSWORD="change-this-password"
export NETMAP_SECRET_KEY="replace-with-a-random-secret"
```

Then start:

```bash
python -m netmap.dashboard
```

> Do not use weak or default credentials in a production environment.

---

# 🔑 Dashboard Authentication

The dashboard provides session-based authentication.

```text
Browser
   │
   ▼
Login
   │
   ▼
Credential Validation
   │
   ├── Failed ──► Login Error
   │
   └── Success
          │
          ▼
       Session
          │
          ▼
   Protected Dashboard
          │
          ▼
     Protected APIs
```

The dashboard protects security-sensitive API endpoints from unauthenticated access.

---

# 📄 Reports

NetMap can generate several types of reports.

## Network JSON

```text
reports/netmap_report.json
```

## Topology JSON

```text
reports/netmap_topology.json
```

## Topology HTML

```text
reports/netmap_topology.html
```

## Security JSON

```text
reports/security_report.json
```

## Security HTML

```text
reports/security_report.html
```

## Event Log

```text
reports/netmap_events.log
```

## Heartbeat

```text
reports/netmap_heartbeat.json
```

Runtime files are excluded from Git where appropriate.

---

# 🧭 Network Topology

NetMap builds a gateway-centered logical topology.

Example:

```text
                    ┌──────────────┐
                    │   Gateway    │
                    │ 192.168.x.x  │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ Local    │  │ Device 1 │  │ Device 2 │
       │ Host     │  │          │  │          │
       └──────────┘  └──────────┘  └──────────┘
```

The topology can be exported as standalone HTML.

---

# 🛡️ Security Considerations

NetMap is intended for defensive monitoring and authorized security testing.

## Authorized scope

Only scan networks where you have permission.

## Nmap privileges

Some Nmap features, particularly OS fingerprinting, may require elevated privileges.

## Dashboard credentials

Never expose the dashboard using weak credentials.

## Secret key

Set a strong `NETMAP_SECRET_KEY` before deploying outside a local development environment.

## Generated data

Network information may contain sensitive infrastructure details.

Do not commit:

* database files
* runtime logs
* generated security reports
* heartbeat state
* private network inventories

---

# 🔒 Data Handling

NetMap may collect:

* private IP addresses
* MAC addresses
* hostnames
* vendors
* open ports
* service information
* operating system information
* network topology
* security events

Treat generated reports as potentially sensitive.

---

# 🧪 Example Network

The development and validation environment used for this project included a Linux/Kali virtual machine and a VMware virtual network.

Example discovered network:

```text
Network:
10.10.10.0/24

Local Host:
10.10.10.10

Gateway:
10.10.10.1
```

Example discovered devices:

```text
10.10.10.10
    security-monitor.local
    Local Host

10.10.10.1
    gateway.local
    VMware
    Gateway

10.10.10.154
    VMware
    Device
```

These addresses are examples from the development environment and should not be assumed to exist on another system.

---

# 🔬 Example Security Scenario

Consider a network where a new system appears unexpectedly.

### Initial state

```text
Gateway
 ├── Workstation
 └── Server
```

### New scan

```text
Gateway
 ├── Workstation
 ├── Server
 └── Unknown Device
```

NetMap detects:

```text
NEW_DEVICE
```

The device is then enriched:

```text
IP
MAC
Vendor
Hostname
Services
OS
Device Type
Risk
```

If the device exposes unexpected services:

```text
Unknown Device
      │
      ├── TCP/22
      ├── TCP/80
      └── TCP/8080
             │
             ▼
       Risk Assessment
             │
             ▼
          Alert
```

The alert is persisted and becomes visible in the dashboard.

An analyst can then acknowledge or resolve the alert after investigation.

---

# 🧑‍💻 Skills Demonstrated

NetMap demonstrates practical experience across multiple cybersecurity and software engineering areas.

## Cybersecurity

* Network reconnaissance
* Network visibility
* Security monitoring
* Alert generation
* Alert triage
* Anomaly detection
* Risk assessment
* Service exposure analysis
* Security investigation
* Defensive security automation

## Networking

* IPv4 networking
* Subnet detection
* Routing
* Gateway identification
* MAC addresses
* ARP-related network visibility
* TCP services
* Network topology

## Linux

* Linux networking
* Shell environment
* Python execution
* Nmap
* Process/runtime management
* Virtualized network environments
* File permissions
* Environment variables

## Python

* Modular architecture
* Type hints
* Exception handling
* SQLite integration
* Flask
* JSON
* CSV
* subprocess execution
* REST APIs
* Automated testing

## Security Operations

* Alert lifecycle
* Severity classification
* Historical investigation
* Risk scoring
* Event monitoring
* Device baselining
* Security reporting
* SOC dashboard concepts

---

# 📈 Version History

## v2.0.0

NetMap 2.0 transforms the project from a network discovery tool into a persistent network security monitoring platform.

Major additions:

* Device fingerprinting
* Port and service discovery
* OS detection
* SQLite persistence
* Historical device tracking
* Historical topology
* Anomaly detection
* Risk scoring
* Alert acknowledgement
* Alert resolution
* Alert filtering
* Security analytics
* Security reports
* Authenticated dashboard
* Protected REST APIs

Validation:

```text
24 tests passed
Python compilation successful
Live monitoring validated
SQLite persistence validated
Dashboard validated
```

---

## v1.0.0

Initial stable release containing:

* network interface detection
* Nmap discovery
* gateway detection
* device classification
* topology generation
* live monitoring
* change detection
* alert generation
* Flask dashboard
* JSON/CSV reporting
* automated tests

---

# 🧭 Roadmap

NetMap 2.0 establishes the core monitoring and investigation platform.

Future improvements may include:

### Network Intelligence

* improved device fingerprinting
* expanded protocol support
* improved OS detection
* richer vendor intelligence
* passive network observation

### Detection

* more advanced behavioral baselines
* anomaly scoring
* configurable detection rules
* event correlation
* detection tuning

### Security

* expanded MITRE ATT&CK mapping
* improved risk models
* investigation timelines
* IOC support
* security event correlation

### Dashboard

* advanced charts
* interactive historical timelines
* improved topology visualization
* filtering and search
* customizable dashboards

### Deployment

* Docker deployment
* CI/CD hardening
* production deployment documentation
* configuration management
* deployment health checks

### Reporting

* exportable investigation reports
* scheduled reports
* richer security summaries
* analyst-focused reporting

---

# 🧱 Design Philosophy

NetMap intentionally focuses on a clear security workflow rather than attempting to become a full enterprise SIEM.

The architecture follows:

```text
Simple
   ↓
Modular
   ↓
Observable
   ↓
Testable
   ↓
Extensible
```

Each major capability is separated into its own module.

This makes the project easier to:

* test
* understand
* extend
* troubleshoot
* demonstrate during interviews

---

# 🧪 Development Validation

The current project has been validated using:

```bash
python -m pytest -q
```

Result:

```text
........................
24 passed
```

Python compilation:

```bash
python -m compileall -q netmap
```

No compilation errors were reported.

---

# 📋 Project Status

| Component                | Status  |
| ------------------------ | ------- |
| Network Discovery        | ✅       |
| Gateway Detection        | ✅       |
| Device Classification    | ✅       |
| Device Fingerprinting    | ✅       |
| Service Discovery        | ✅       |
| OS Detection             | ✅       |
| Live Monitoring          | ✅       |
| Change Detection         | ✅       |
| Anomaly Detection        | ✅       |
| Device Risk Scoring      | ✅       |
| Network Risk Scoring     | ✅       |
| Alert Generation         | ✅       |
| Alert Persistence        | ✅       |
| Alert Acknowledgement    | ✅       |
| Alert Resolution         | ✅       |
| Alert Filtering          | ✅       |
| Historical Database      | ✅       |
| Historical Device Data   | ✅       |
| Historical Topology      | ✅       |
| Dashboard Analytics      | ✅       |
| Security Reports         | ✅       |
| Dashboard Authentication | ✅       |
| Protected APIs           | ✅       |
| Automated Tests          | ✅       |
| Docker Deployment        | Planned |
| CI/CD Deployment         | Planned |
| Advanced MITRE Mapping   | Planned |

---

# 🏆 Why This Project Matters

NetMap was built to demonstrate how several individual cybersecurity concepts can be combined into a practical security monitoring workflow.

Instead of stopping at:

```text
Scan → Display Results
```

NetMap 2.0 extends the workflow to:

```text
Scan
 ↓
Identify
 ↓
Enrich
 ↓
Persist
 ↓
Compare
 ↓
Detect
 ↓
Score
 ↓
Alert
 ↓
Investigate
 ↓
Acknowledge
 ↓
Resolve
```

This architecture reflects the type of workflow used when building security monitoring and SOC-oriented tooling.

---

# 📚 Learning Outcomes

Building NetMap provided practical experience with:

* Linux networking
* Nmap automation
* Python network programming
* network topology modeling
* service enumeration
* OS fingerprinting
* persistent security data
* SQLite database design
* event-driven monitoring
* anomaly detection
* security risk scoring
* alert lifecycle management
* Flask API development
* dashboard authentication
* security reporting
* automated testing
* Git/GitHub project management

---

# ⚠️ Limitations

NetMap is a portfolio and learning project rather than a replacement for enterprise security products.

Current limitations include:

* OS detection depends on Nmap fingerprinting.
* Some Nmap functionality may require elevated privileges.
* Risk scoring is a lightweight heuristic model.
* Anomaly detection is not equivalent to a production ML-based detection platform.
* Network discovery performance depends on network size and scan configuration.
* Dashboard authentication requires secure configuration for production use.
* Docker deployment is not currently part of the stable release.
* Advanced enterprise integrations are outside the current scope.

---

# 🔮 Future Vision

The long-term goal is to evolve NetMap toward a more complete lightweight network security operations platform.

Potential future architecture:

```text
                    NETWORK
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       Active Discovery     Passive Monitoring
             │                   │
             └─────────┬─────────┘
                       ▼
                Device Intelligence
                       │
                       ▼
                 Event Pipeline
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Detection       Risk       Correlation
          │            │            │
          └────────────┼────────────┘
                       ▼
                 Alert Engine
                       │
                       ▼
                 SOC Dashboard
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          Alerts     History    Reports
```

---

# 🤝 Contributing

Contributions, ideas, bug reports, and improvements are welcome.

Suggested workflow:

```bash
git clone <repository>
cd NetMap

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m pytest -q
```

Create a feature branch:

```bash
git checkout -b feature/my-feature
```

Make your changes, test them, and submit a pull request.

---

# 📜 License

This project is licensed under the MIT License.

See:

```text
LICENSE
```

for the complete license text.

---

# 👤 Author

**Ch Viswa**

Cybersecurity-focused Computer Science graduate interested in:

* Security Operations
* SOC Analysis
* Network Security
* Vulnerability Assessment
* Penetration Testing
* Linux Security
* Security Automation
* Threat Detection

NetMap is part of a practical cybersecurity portfolio focused on building and documenting security tools rather than only studying theoretical concepts.

---

# ⭐ Project Highlights

```text
┌─────────────────────────────────────────────┐
│                 NETMAP 2.0                  │
├─────────────────────────────────────────────┤
│                                             │
│  🔎 Network Discovery                       │
│  🧠 Device Intelligence                    │
│  🔐 Service Discovery                      │
│  🖥️ OS Fingerprinting                      │
│  📡 Live Monitoring                        │
│  🚨 Security Alerts                        │
│  🧮 Risk Scoring                            │
│  🧠 Anomaly Detection                       │
│  🗄️ Historical Database                    │
│  🗺️ Historical Topology                    │
│  📊 Security Analytics                     │
│  🖥️ SOC Dashboard                          │
│  🔑 Dashboard Authentication               │
│  📄 Security Reports                       │
│  🔌 REST APIs                              │
│  🧪 Automated Testing                      │
│                                             │
└─────────────────────────────────────────────┘
```

---

# ⭐ If You Find This Project Useful

If NetMap is useful for learning or demonstrates something interesting to you, consider giving the repository a ⭐.

The project is intended as an evolving cybersecurity portfolio project focused on **practical network visibility, monitoring, detection, investigation, and security automation**.

---

## NetMap 2.0

**Discover. Identify. Monitor. Detect. Investigate. Respond.**
