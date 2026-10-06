# Changelog

All notable changes to NetMap are documented here.

## [2.0.0] - 2026-10-06

### Added

#### Network Intelligence
- Advanced device fingerprinting
- MAC and vendor identification
- Device role classification
- Device type identification
- Operating system detection
- Port and service discovery
- Service version detection
- Gateway discovery

#### Historical Intelligence
- SQLite-based device inventory
- Historical service records
- Historical monitoring events
- Historical topology snapshots
- Device history API
- Topology history API
- Device observation tracking

#### Security Monitoring
- Continuous live network monitoring
- New-device detection
- Device removal detection
- MAC address change detection
- New-port detection
- Closed-port detection
- Operating system change detection
- Security anomaly engine
- Persistent security alerts
- Alert severity classification
- Alert acknowledgement
- Alert resolution
- Alert filtering

#### Risk Analysis
- Per-device risk scoring
- Network-wide risk scoring
- Risk factors based on exposed services
- Risk factors based on anomalies
- Severity-aware risk levels

#### Security Operations Dashboard
- Authenticated SOC-style dashboard
- Live device inventory
- Service inventory
- Security alert table
- Severity filtering
- Status filtering
- Alert acknowledgement controls
- Alert resolution controls
- Network risk indicator
- Security analytics
- Device role statistics
- Operating system statistics
- Service statistics
- Monitoring event viewer
- Historical topology viewer
- Security report generation

#### Reporting
- JSON network reports
- CSV device reports
- JSON security reports
- Standalone HTML security reports
- Interactive topology HTML
- Persistent monitoring event logs
- Monitoring heartbeat

#### API
- Dashboard health endpoint
- Network status endpoint
- Device inventory endpoint
- Device history endpoint
- Service inventory endpoint
- Event endpoint
- Alert endpoint
- Alert acknowledgement endpoint
- Alert resolution endpoint
- Analytics endpoint
- Historical topology endpoint
- Security report endpoint

#### Authentication
- Dashboard login
- Session-based authentication
- Configurable administrator username
- Configurable administrator password
- Password hashing with Werkzeug
- Protected dashboard API endpoints
- Logout functionality

#### Testing
- Expanded unit test suite
- Network detection tests
- Scanner tests
- Gateway tests
- Classification tests
- Reporter tests
- Topology tests
- Monitoring tests
- Alert tests
- Risk analysis tests
- Anomaly detection tests
- Fingerprinting tests
- Database tests

### Improved

- Database persistence architecture
- Alert persistence architecture
- Live monitoring integration
- Dashboard API structure
- Security report generation
- Error handling
- Runtime logging
- Historical data handling
- Dashboard authentication
- API protection
- Project organization

### Security

- Runtime database files excluded from Git
- Runtime logs excluded from Git
- Generated reports excluded from Git
- Python cache files excluded from Git
- Development environment files excluded from Git
- Dashboard API authentication enforced
- Security report values HTML-escaped before rendering

### Validation

NetMap 2.0.0 was validated with:

- Python compilation checks
- Pytest automated test suite
- 24 passing tests
- Live network monitoring
- SQLite persistence
- Dashboard API
- Authenticated dashboard
- Service discovery
- Security alert persistence

### Known Limitations

- OS detection depends on Nmap fingerprinting quality and scan privileges.
- Network discovery is intended for authorized networks.
- Docker deployment is not part of the 2.0.0 release.
- Dashboard credentials should be configured through environment variables for production deployments.

### Roadmap

Planned future improvements:

- Docker deployment
- CI/CD hardening
- Improved OS fingerprinting
- Advanced dashboard charts
- Historical device timeline visualization
- More advanced behavioral anomaly detection
- Expanded MITRE ATT&CK mapping
- Improved authentication configuration
- Exportable SOC investigation reports
- Additional network protocols
- Performance optimization for larger networks

## [1.0.0] - 2026-10-06

Initial stable NetMap release.

### Added

- Network interface detection
- Nmap host discovery
- Gateway detection
- Device classification
- JSON reporting
- CSV reporting
- Network topology generation
- Interactive topology HTML
- Live monitoring
- Device change detection
- Heartbeat monitoring
- Security alerts
- Alert persistence
- Flask dashboard
- Automated tests
- Project documentation

