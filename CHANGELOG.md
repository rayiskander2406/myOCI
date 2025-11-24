# Changelog

All notable changes to the myOCI monitoring infrastructure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-24

### Added

#### Monitoring Foundation
- **Netdata** real-time system monitoring with dashboard at https://monitor.qubix.space
  - System metrics: CPU, RAM, disk, network
  - Container monitoring for all services
  - Reverse proxy access via Caddy
  - Authentication-protected web interface

- **Loki** centralized log aggregation system
  - 24-hour log retention policy for optimal performance
  - 10-minute compaction interval
  - v2.9.3 with TSDB schema (v13)
  - Efficient log storage and querying

- **Promtail** log collection agent
  - Docker container log collection
  - System log collection (/var/log)
  - Enhanced label schema: container, service, project, priority
  - Priority-based tagging for critical services

#### Visualization & Dashboards
- **Grafana 11.0.0** visualization platform at https://grafana.qubix.space
  - Automated Loki datasource provisioning
  - Dashboard file provisioning from `monitoring/grafana/dashboards/`
  - Secure HTTPS access via Caddy reverse proxy

- **6 Pre-configured Dashboards**:
  1. **System Health** - High-level container and log monitoring with 1-minute refresh
  2. **Container Details** - Deep dive into individual container logs and metrics
  3. **Error Tracking** - System-wide error monitoring and analysis
  4. **System Overview** - Comprehensive system status
  5. **Logs Explorer** - Interactive log exploration interface
  6. **Container Monitoring** - Multi-container performance tracking

#### Alerting & Notifications
- **ntfy** notification server at https://notify.qubix.space
  - Topic-based notification system
  - Mobile app integration support
  - REST API for alert delivery

- **Telegram Integration**
  - Automated alert forwarding to Telegram
  - Priority-based filtering (critical/high/standard)
  - HTML-formatted messages with emojis
  - Configurable via TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID

#### Web Access & Security
- **Caddy Reverse Proxy** integration
  - monitor.qubix.space → Netdata
  - grafana.qubix.space → Grafana
  - notify.qubix.space → ntfy
  - Automatic HTTPS with Let's Encrypt
  - Secure authentication for monitoring endpoints

#### Documentation
- `monitoring/DASHBOARDS_GUIDE.md` - Comprehensive guide to Grafana dashboards
- `monitoring/GRAFANA_EXPLORE_GUIDE.md` - LogQL query tutorial and Explore mode usage
- `ACCESS_INSTRUCTIONS.md` - Updated with Grafana and monitoring access details
- Release planning infrastructure (`.claude/PLANNING.md`, `.claude/TODO.md`)

#### Developer Tools
- `/plan-release` command - Strategic release planning tool
- `/generate-tasks` command - Task decomposition automation
- Structured release workflow with PLANNING.md → TODO.md pipeline

### Fixed

#### Telegram Forwarder
- HTML formatting in Telegram messages now renders correctly
- Priority field handling improved for alert categorization
- Duplicate alert suppression

#### Loki Configuration
- Optimized retention settings (24 hours) to prevent data accumulation
- Fixed compaction interval (10 minutes) for consistent cleanup
- TSDB schema (v13) for better performance

#### Promtail Labels
- Enhanced label schema with container, service, project dimensions
- Fixed priority labels for critical services (caddy, postgres, etc.)
- Improved Docker container name parsing

#### Grafana Dashboards
- Optimized query time ranges (10 minutes default) to prevent timeouts
- Reduced refresh intervals (1 minute) for better performance
- Fixed datasource UID references (P8E80F9AEF21F6940)

### Technical Details

#### Services Added
```yaml
- netdata:19999 → https://monitor.qubix.space
- loki:3100 (internal)
- promtail (log collector)
- grafana:3000 → https://grafana.qubix.space
- ntfy:80 → https://notify.qubix.space
- telegram-forwarder (Python)
```

#### Docker Images
- grafana/grafana:11.0.0
- grafana/loki:2.9.3
- grafana/promtail:2.9.3
- netdata/netdata:latest
- binwiederhier/ntfy:latest
- python:3.9-slim (telegram-forwarder)

#### Configuration Files Modified
- `monitoring/docker-compose.yml` - Added Grafana service
- `monitoring/loki/config.yml` - 24-hour retention configuration
- `monitoring/promtail/config.yml` - Enhanced label schema
- `monitoring/telegram-forwarder/forwarder.py` - HTML formatting fix

#### Storage & Retention
- **Loki**: 24-hour rolling retention, 10-minute compaction
- **Grafana**: Persistent volume for dashboards and settings
- **Netdata**: In-memory with configurable history

### Security

#### Environment Variables Required
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**⚠️ SECURITY WARNING**: Never commit these values to git. Store in `.env` file or use secure secret management.

#### Access Control
- Netdata: Authentication required (via Caddy)
- Grafana: Login required (default: admin/admin - change immediately)
- ntfy: Public endpoint (use topic secrets for sensitive alerts)

### Known Limitations

1. **Log Retention**: Only 24 hours of logs retained. For longer retention, adjust `monitoring/loki/config.yml` (may impact performance).

2. **Dashboard Performance**: Time ranges beyond 6 hours may cause slow queries or timeouts with current 24-hour retention.

3. **No Alert Rules**: Grafana alerting not yet configured. Alerts currently rely on Netdata + Telegram integration.

4. **Manual Deployment**: No automated deployment pipeline. Changes require manual `docker compose up -d`.

5. **Backup Strategy**: Not yet implemented. Dashboards and configs exist in git, but Grafana settings/users are not backed up.

### Upgrade Notes

#### First-Time Setup
1. Deploy monitoring stack: `cd ~/monitoring && docker compose up -d`
2. Configure Telegram credentials in `.env` file
3. Access Grafana at https://grafana.qubix.space
4. Change default admin password
5. Verify dashboards loaded correctly

#### From Previous Monitoring Setup
If you had a previous monitoring setup, this release introduces breaking changes:
- Loki data will be cleared due to new retention policy
- Promtail labels have changed (re-index required)
- Grafana dashboards require manual import if not using file provisioning

### Migration Guide

#### Migrating Existing Logs
Existing logs before v0.1.0 deployment will not be automatically imported. The 24-hour retention starts fresh from deployment time.

#### Dashboard Backup
```bash
# Backup existing dashboards
scp -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114:~/monitoring/grafana/dashboards/*.json ~/dashboard-backups/
```

### Contributors
- Ray Iskander (@rayiskander)
- Claude Code (AI Assistant)

---

## [Unreleased]

### Planned for v0.2.0
- Grafana alerting rule configuration
- Auto-healing implementation (Phase 3)
- Netdata alert integration with Grafana
- Automated backup strategy
- Pinned Docker image versions

### Planned for v0.3.0
- Automated testing suite
- CI/CD pipeline integration
- Multi-environment support (dev/staging/prod)

---

[0.1.0]: https://github.com/yourusername/myOCI/releases/tag/v0.1.0
