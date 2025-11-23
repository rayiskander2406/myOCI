# myOCI

Server Health Monitoring and Management System for OCI (Oracle Cloud Infrastructure) instances.

## Overview

This project provides automated health monitoring, alerting, and maintenance scripts for managing OCI server infrastructure.

## Features

- **Health Monitoring**: Track server metrics, Docker containers, and service availability
- **Auto-Remediation**: Automated corrective actions for common issues
- **Scheduled Maintenance**: Smart reboot scheduling during low-usage periods
- **Alerting**: Notifications for critical issues

## Server Infrastructure

Current server setup includes:
- **NetBird VPN Platform**: Mesh VPN network with management dashboard
- **Caddy Reverse Proxy**: HTTP/HTTPS routing and SSL termination
- **LMS Canvas**: Canvas-compatible LMS platform
- **Static Site Hosting**: TOTAL-FIX presentation and other static content

## Monitoring Phases

### Phase 1: Monitoring & Alerting (Current)
- Monitor key metrics without automatic actions
- Track Docker container health
- Monitor disk space, memory, and CPU usage
- Service responsiveness checks

### Phase 2: Safe Auto-Remediation (Planned)
- Restart failed Docker containers
- Clear logs when disk space is critical
- Restart unresponsive services

### Phase 3: Scheduled Maintenance (Planned)
- Automated scheduled reboots during off-hours
- Security patch management
- Log rotation and cleanup

## Getting Started

(Coming soon)

## Configuration

(Coming soon)

## License

(To be determined)
