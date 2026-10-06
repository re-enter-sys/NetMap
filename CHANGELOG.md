# Changelog

All notable changes to NetMap are documented in this file.

The project follows a simple release-based changelog format.

---

## [1.0.0] - 2026-10-06

### Added

- Linux network interface discovery
- IPv4 network and CIDR detection
- Local MAC address detection
- Nmap-based network device discovery
- Hostname detection
- MAC address and vendor detection
- Default gateway detection
- Automatic device role classification
- JSON network reporting
- CSV device reporting
- Network topology graph generation
- Interactive standalone topology HTML view
- Live network monitoring
- Device addition detection
- Device removal detection
- Timestamped monitoring event logging
- Monitor heartbeat mechanism
- Structured security alert engine
- New-device security alerts
- Device-removal security alerts
- Persistent security alert history
- Flask dashboard API
- Dashboard health endpoint
- Live network monitoring dashboard
- Device inventory table
- Network topology visualization
- Monitoring event visualization
- Security alert visualization
- Automatic dashboard refresh
- Monitor health status
- Automated pytest test suite

### Security Monitoring

NetMap now converts network changes into structured security events.

Example:

```text
New Device Detected
Severity: MEDIUM
Type: NETWORK_DEVICE_CHANGE
