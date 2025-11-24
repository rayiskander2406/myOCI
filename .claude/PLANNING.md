# Release Planning - November 24, 2025

## Release Overview
- **Proposed Version**: v0.1.0
- **Release Type**: Minor (Initial Production Release)
- **Target Date**: November 25, 2025
- **Risk Level**: Medium

## Changes Since Last Release

**Note:** This is the FIRST release. No previous releases exist.

### Project Timeline
- **Started:** November 23, 2025 (23 hours ago)
- **Week 1 Completed:** November 23, 2025, 16:30 EET
- **Week 2 Completed:** November 23, 2025
- **Total Commits:** 18 commits over 24 hours
- **Total Implementation Time:** ~2.5 hours (Week 1) + deployment time (Week 2)

### Breaking Changes
None - this is the initial release.

### New Features

#### Phase 1 - Monitoring Foundation (Week 1)
- **Netdata v2.8.0** - Real-time monitoring with 1-second granularity
  - Auto-discovery of Docker containers
  - System metrics (CPU, memory, disk, network)
  - Built-in anomaly detection
  - Per-container resource monitoring
  - Web dashboard on port 19999

- **Loki 3.0.0** - Centralized log aggregation
  - 24-hour log retention policy (updated from 7 days)
  - Schema v13 (TSDB) for Loki 3.0 compatibility
  - Automatic compaction every 10 minutes
  - Filesystem-based storage
  - LogQL query language support

- **Promtail 3.0.0** - Log collection agent
  - Docker log collection via socket
  - Priority-based labeling (critical/high/standard)
  - Service name extraction from Docker labels
  - Auto-discovery of containers

#### Phase 2 - Alerting & Notifications (Week 2)
- **ntfy** - Self-hosted notification server
  - HTTP pub-sub architecture
  - Multiple topic support (oci-critical, oci-warning, oci-info)
  - Lightweight (32 MB RAM, no database)
  - Port 8765 web UI and API

- **Telegram Forwarder** - Custom Python service
  - Real-time alert forwarding to Telegram
  - Priority-based emoji enrichment (🔴🟠🟡🟢⚪)
  - HTML formatting (fixed from Markdown)
  - Timezone-aware timestamps (EET/Cairo)
  - Automatic reconnection on failures

- **Grafana 11.0.0** - Visualization platform
  - Loki datasource (default) for log queries
  - Netdata datasource for metrics
  - Dashboard provisioning enabled
  - 3 optimized dashboards created:
    - System Health (10-min range, high-level overview)
    - Container Details (per-container deep dive with dropdown)
    - Error Tracking (system-wide error monitoring)

- **Maintenance Automation**
  - Weekly maintenance script (Sunday 2 AM EET)
  - Docker resource cleanup
  - Container health verification
  - Disk usage reporting
  - Log rotation (last 10 runs)

#### Phase 3 - Web Access (Week 2)
- **Caddy Reverse Proxy Integration**
  - Netdata accessible via https://monitor.qubix.space
  - Grafana accessible via https://grafana.qubix.space
  - SSL/TLS termination
  - Authentication ready (to be configured)

### Bug Fixes
- **Telegram Markdown Formatting** (commit 3126def)
  - Fixed: Telegram API rejected Markdown bold syntax
  - Solution: Switched to HTML formatting (`<b>`, `<i>`)

- **Priority Handling** (commit 3126def)
  - Fixed: Inconsistent priority values (int vs string)
  - Solution: Added priority mapping and type checking

- **Loki Configuration** (Week 1)
  - Fixed: Missing `delete_request_store` for retention
  - Fixed: Invalid schema for Loki 3.0 (updated to v13/TSDB)
  - Fixed: Invalid config fields for Loki 3.0

- **Docker Network Discovery** (Week 1)
  - Fixed: Incorrect network name `infrastructure_files_default`
  - Solution: Changed to `infrastructure_files_netbird`

- **Promtail Configuration**
  - Fixed: Missing `job` label causing dashboard data issues
  - Fixed: Label mismatch (`container_name` vs `container`)

- **Grafana Dashboard Loading**
  - Fixed: Datasource UID mismatch
  - Fixed: Perpetually loading dashboards due to missing retention policy
  - Fixed: Permission errors on dashboard JSON files
  - Solution: Implemented 24-hour retention, optimized dashboards with short time ranges

### Dependencies
#### Core Docker Images
- `netdata/netdata:latest` - monitoring
- `grafana/loki:3.0.0` - log storage
- `grafana/promtail:3.0.0` - log collection
- `binwiederhier/ntfy:latest` - notifications
- `grafana/grafana:11.0.0` - visualization
- `python:3.12-slim` - Telegram forwarder base

#### Python Dependencies (Telegram Forwarder)
- `requests` - HTTP client
- `pytz` - Timezone handling

#### External Services
- Telegram Bot API (requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`)
- Existing NetBird infrastructure network (`infrastructure_files_netbird`)

## Release Requirements

### Must Have (Blockers)
- [x] All monitoring services deployed and running
- [x] Loki retention policy configured (24 hours)
- [x] Grafana dashboards working without timeout errors
- [x] Telegram notifications functional end-to-end
- [x] Week 1 and Week 2 implementation reports completed
- [x] Comprehensive documentation (README, guides, troubleshooting)
- [ ] Commit uncommitted changes (docker-compose.yml, telegram-forwarder, dashboards)
- [ ] Environment variable configuration documented
- [ ] Version tag created in git

### Should Have (Important)
- [x] Maintenance automation script tested
- [x] Dashboard provisioning working
- [x] Web access via Caddy configured
- [ ] Cron job for maintenance.sh verified on server
- [ ] Backup strategy documented
- [ ] Security hardening (authentication on web dashboards)

### Nice to Have (Optional)
- [ ] Phase 3 auto-healing (Docker Autoheal + Watchtower) - planned for next release
- [ ] Netdata alert integration with ntfy
- [ ] Grafana alerting rules configured
- [ ] API health check endpoints for critical services
- [ ] Automated testing suite

## Risk Analysis

### High Risk Items
**Risk:** Loki data accumulation without retention could cause performance degradation
- **Status:** MITIGATED
- **Mitigation:** 24-hour retention policy implemented, compaction every 10 minutes, previous 187GB data cleared

**Risk:** Telegram bot token exposure in environment variables
- **Status:** MEDIUM
- **Mitigation:** Using `.env.example` template, actual `.env` file in `.gitignore`
- **Recommendation:** Consider using Docker secrets or encrypted vault for production

**Risk:** No authentication on Netdata and Grafana dashboards
- **Status:** MEDIUM
- **Mitigation:** Behind Caddy reverse proxy, accessible only via VPN or specific domains
- **Recommendation:** Enable authentication in Grafana, configure Caddy auth for Netdata

### Medium Risk Items
**Risk:** Single point of failure - monitoring stack on same server as monitored services
- **Mitigation:** Lightweight stack (~500MB RAM), unlikely to affect host
- **Recommendation:** Consider external monitoring in future

**Risk:** Docker socket access for monitoring containers
- **Mitigation:** Read-only mounts (`:ro`) where possible
- **Recommendation:** Review security best practices for Docker socket access

**Risk:** No automated backups of Grafana dashboards and configurations
- **Mitigation:** All configurations in git repository
- **Recommendation:** Implement automated backup of Grafana database

### Dependencies on External Systems
**Dependency:** Telegram Bot API
- **Impact:** If Telegram API is down, notifications won't be delivered
- **Fallback:** ntfy web interface still accessible, logs still in Loki

**Dependency:** NetBird infrastructure network
- **Impact:** Monitoring stack requires `infrastructure_files_netbird` Docker network
- **Coordination:** Must be started after NetBird stack is running

**Dependency:** Caddy reverse proxy
- **Impact:** Web access requires Caddy running in NetBird infrastructure
- **Coordination:** Caddy configuration must include monitoring service entries

## Deployment Strategy

### Pre-Deployment
- [x] Test all services locally
- [x] Verify end-to-end notification pipeline
- [ ] Commit all uncommitted changes
- [ ] Create git tag v0.1.0
- [ ] Document deployment steps in monitoring/README.md
- [ ] Verify cron job configuration for maintenance.sh
- [ ] Backup existing `.env` file if exists

### Deployment Steps

**This is a documentation release** - services are already deployed and running. Steps below are for future deployments:

1. **Prepare Environment**
   ```bash
   cd ~/myOCI
   git pull origin main
   git checkout v0.1.0
   ```

2. **Configure Environment Variables**
   ```bash
   cd monitoring
   cp .env.example .env
   nano .env  # Fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
   ```

3. **Verify Dependencies**
   ```bash
   # Ensure NetBird infrastructure is running
   docker network ls | grep infrastructure_files_netbird
   ```

4. **Deploy Monitoring Stack**
   ```bash
   cd ~/monitoring
   docker compose up -d
   ```

5. **Verify Services**
   ```bash
   docker ps | grep -E "oci-netdata|oci-loki|oci-promtail|oci-ntfy|oci-telegram|oci-grafana"
   ```

6. **Test Notification Pipeline**
   ```bash
   curl -H "Priority: urgent" \
        -d "Test alert from OCI monitoring v0.1.0" \
        http://localhost:8765/oci-critical
   ```

7. **Configure Cron Job**
   ```bash
   crontab -e
   # Add: 0 2 * * 0 cd /home/ubuntu/monitoring && ./maintenance.sh >> /home/ubuntu/monitoring/maintenance.log 2>&1
   ```

### Post-Deployment
- [ ] Verify Netdata dashboard accessible: https://monitor.qubix.space
- [ ] Verify Grafana dashboard accessible: https://grafana.qubix.space
- [ ] Check all three Grafana dashboards load without errors
- [ ] Confirm Telegram notification received
- [ ] Check Loki retention working (query old logs should fail after 24h)
- [ ] Verify container health checks passing
- [ ] Document any issues in GitHub Issues

### Rollback Plan
**If critical issues occur:**

1. **Stop monitoring stack (does not affect main infrastructure)**
   ```bash
   cd ~/monitoring
   docker compose down
   ```

2. **Restore previous configuration (if needed)**
   ```bash
   git checkout <previous-commit>
   docker compose up -d
   ```

3. **Verify main infrastructure unaffected**
   ```bash
   docker ps | grep -E "caddy|netbird|zitadel|postgres"
   ```

**Important:** Stopping the monitoring stack does NOT affect NetBird, Caddy, or any other production services.

## Documentation & Communication

### Changelog Entries

**For CHANGELOG.md (to be created):**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-24

### Added
- Real-time monitoring with Netdata (1-second granularity)
- Centralized log aggregation with Loki + Promtail
- Self-hosted notification server (ntfy)
- Telegram integration for push notifications
- Grafana visualization with 3 optimized dashboards
- Automated maintenance system (weekly cleanup)
- Web access via Caddy reverse proxy
- Priority-based alert routing (critical/warning/info)
- Comprehensive documentation and troubleshooting guides

### Fixed
- Telegram HTML formatting (was: Markdown breaking)
- Loki retention policy (now: 24-hour cleanup)
- Dashboard performance (short time ranges, efficient queries)
- Promtail label configuration (job and container labels)

### Technical Details
- Docker Compose based deployment
- 6 containerized services
- 500MB RAM total overhead
- ~1.5GB/day log volume (24h retention)
- Cairo timezone (EET, UTC+2)
```

### Documentation Updates Needed
- [ ] Create root CHANGELOG.md
- [ ] Update main README.md with installation quick start
- [ ] Add monitoring/DEPLOYMENT.md with step-by-step instructions
- [ ] Create monitoring/TROUBLESHOOTING.md (comprehensive)
- [ ] Add monitoring/SECURITY.md (authentication, hardening)
- [ ] Document environment variables in monitoring/README.md
- [ ] Add architecture diagram to monitoring/README.md
- [ ] Create CONTRIBUTING.md for future contributors

### Stakeholder Communication
**Who needs to know:**
- System administrator (deployment, maintenance)
- Infrastructure team (Caddy configuration, DNS)
- Security team (review Docker socket access, authentication)

**What to communicate:**
- Monitoring stack is now operational
- Telegram notifications configured and tested
- Web dashboards accessible via VPN/authenticated access
- Weekly maintenance runs Sunday 2 AM EET
- Alert routing: Critical (immediate), Warning (5min batch), Info (daily digest)

**When to communicate:**
- Post-deployment announcement (after v0.1.0 tagged)
- Weekly status in first month (verify stability)
- Incident reports (if monitoring detects issues)

## Open Questions

### Configuration Decisions
- **Q:** Should we enable Grafana authentication immediately or wait for Phase 3?
  - **Recommendation:** Enable basic auth in v0.1.0 for security
  - **Impact:** Medium - requires setting `GF_SECURITY_ADMIN_PASSWORD` and Caddy auth

- **Q:** What is the long-term retention strategy for metrics beyond 24 hours?
  - **Options:**
    1. Keep 24h (current) - sufficient for operational monitoring
    2. Export to external storage (S3, NFS) for historical analysis
    3. Increase to 7 days but monitor disk usage
  - **Recommendation:** Start with 24h, evaluate in v0.2.0

- **Q:** Should ntfy topics be password-protected?
  - **Recommendation:** Yes, for v0.2.0 add ACL configuration
  - **Impact:** Low - internal network only currently

### Technical Clarifications
- **Q:** Is the Netdata claim token needed?
  - **Status:** Optional - for Netdata Cloud integration
  - **Current:** Using self-hosted only (no cloud)

- **Q:** Should we version-pin the `latest` tags (netdata, ntfy)?
  - **Recommendation:** Yes, for production stability
  - **Action:** Update docker-compose.yml to use specific versions

### Infrastructure Questions
- **Q:** What is the backup strategy for monitoring data?
  - **Current:** Configuration in git, data in Docker volumes
  - **Needed:** Backup policy for Grafana dashboards/settings

- **Q:** Who manages the Telegram bot and should we have a backup notification channel?
  - **Current:** Single bot, single chat ID
  - **Recommendation:** Document bot setup process, consider email as backup

## Next Steps

### Immediate (Before Release)
1. Commit uncommitted changes to git
   - `monitoring/docker-compose.yml` (modified)
   - `monitoring/telegram-forwarder/forwarder.py` (modified)
   - `monitoring/MAINTENANCE.md` (new)
   - `monitoring/grafana/dashboards/*.json` (new)
   - `monitoring/maintenance.sh` (new)

2. Create git tag v0.1.0
   ```bash
   git add -A
   git commit -m "Release v0.1.0: Initial monitoring stack deployment"
   git tag -a v0.1.0 -m "Initial production release - monitoring foundation complete"
   git push origin main --tags
   ```

3. Create CHANGELOG.md in root directory

4. Verify cron job on server
   ```bash
   ssh ubuntu@159.54.162.114 'crontab -l'
   ```

### Post-Release (v0.1.x Patch Releases)
- Enable Grafana authentication
- Pin Docker image versions
- Configure ntfy ACLs
- Add Netdata alert integration with ntfy
- Implement automated backup script
- Security hardening review

### Future Releases (v0.2.0+)
- **v0.2.0:** Phase 3 - Auto-Healing
  - Docker Autoheal (tmknight/docker-autoheal)
  - Watchtower for automated updates
  - Container health checks for all services

- **v0.3.0:** Advanced Monitoring
  - Anomaly detection tuning
  - Custom business metrics
  - SLA tracking and reporting
  - Predictive alerting

- **v0.4.0:** Maintenance Automation
  - Scheduled maintenance windows
  - Safe reboot automation
  - Backup integration
  - Security scanning

## Version Recommendation Justification

### Why v0.1.0 (Not v1.0.0)

**Reasons for v0.x (Pre-1.0):**

1. **Recent Development** - Project is 24 hours old
2. **Not Battle-Tested** - Hasn't run in production for extended period
3. **Incomplete Feature Set** - Phase 3 (auto-healing) not implemented
4. **Security Hardening Pending** - Authentication not fully configured
5. **Documentation In Progress** - Deployment guides need completion

**Stability Assessment:**
- ✅ Core functionality working (monitoring, logs, notifications)
- ✅ End-to-end tested successfully
- ⚠️ Needs production validation period
- ⚠️ Security hardening incomplete
- ⚠️ Backup/disaster recovery not fully defined

**Recommendation:**
- Release as v0.1.0 to indicate "production-ready but still maturing"
- Run in production for 2-4 weeks
- Address open questions and security items
- Implement Phase 3 auto-healing
- Release v1.0.0 when all 5 phases complete and proven stable

### Semantic Versioning Approach

For future releases:
- **MAJOR (1.0.0):** Breaking changes, API changes, architecture overhaul
- **MINOR (0.x.0):** New features, new monitoring components, new phases
- **PATCH (0.1.x):** Bug fixes, documentation, configuration tweaks

**Next version scenarios:**
- v0.1.1 - Fix Grafana auth, pin versions, documentation updates
- v0.2.0 - Add auto-healing (Phase 3)
- v0.3.0 - Add advanced monitoring (Phase 4)
- v1.0.0 - All phases complete, 30+ days stable production use

## Backwards Compatibility

**Not applicable** - this is the first release.

**For future releases, preserve:**
- Docker volume names (avoid data loss)
- Environment variable names
- Port mappings
- Network names
- Loki query syntax compatibility
- Grafana dashboard structure

## Project Readiness Assessment

### Ready for Release Planning: ✅ YES

**Strengths:**
- ✅ Comprehensive architecture and planning
- ✅ Week 1 and Week 2 objectives completed
- ✅ End-to-end testing performed
- ✅ Detailed documentation created
- ✅ Services deployed and operational
- ✅ Performance optimizations applied

**Areas Needing Attention:**
- ⚠️ Git repository hygiene (uncommitted changes)
- ⚠️ Security hardening (authentication configuration)
- ⚠️ Long-term data retention strategy
- ⚠️ Backup and disaster recovery procedures
- ⚠️ Production validation period needed

**Critical Blockers:** None

**Recommendation:** Proceed with v0.1.0 release after addressing "Must Have" items above.

---

**Planning Document Version:** 1.0
**Created:** November 24, 2025
**Author:** Claude Code
**Review Status:** Ready for review
**Next Review:** Post-deployment (v0.1.0)
