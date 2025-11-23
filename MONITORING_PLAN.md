# OCI Server Monitoring Plan - Comprehensive Architecture

## Executive Summary

This plan implements a **lightweight, battle-tested, open-source monitoring stack** for the OCI server infrastructure, focusing on real-time monitoring, automated healing, and minimal resource overhead.

## Research-Backed Tool Selection

### Core Monitoring: **Netdata** ✓
**Why Netdata over Prometheus:**
- **Most energy-efficient** for Docker monitoring (University of Amsterdam study)
- **Per-second metrics** vs Prometheus's typical 15-second intervals
- **Zero configuration** - auto-discovers all services
- **Lightweight**: 1-3% CPU, ~100MB RAM vs Prometheus's much higher overhead
- **Built-in dashboard** - no separate Grafana needed
- **Handles 4.6M metrics/sec** with lower resource usage than Prometheus
- **Instant startup** vs Prometheus's 44-minute restart time at scale

**Source:** [Netdata vs Prometheus 2025 Analysis](https://www.netdata.cloud/blog/netdata-vs-prometheus-2025/)

### Auto-Healing: **Docker Autoheal** + **Watchtower** ✓
**Docker Autoheal (tmknight/docker-autoheal):**
- Written in **Rust** - OS agnostic, performant
- Monitors container health checks and auto-restarts unhealthy containers
- Concurrent and multi-threaded for large environments
- **Battle-tested** since Docker healthcheck feature introduction

**Watchtower:**
- Automates Docker image updates
- Perfect for **homelabs and small self-hosted stacks** (maintainer-recommended use case)
- Preserves original container run options
- Configurable update intervals

**Source:** [Docker Autoheal GitHub](https://github.com/tmknight/docker-autoheal), [Watchtower Guide 2025](https://betterstack.com/community/guides/scaling-docker/watchtower-docker/)

### Notifications: **ntfy** ✓
**Why ntfy over Gotify:**
- **More advanced and complete** feature set
- **Fine-grained ACL** permissions
- **No database required** - ultra lightweight
- **Multi-server topic access**
- **HTTP-based pub-sub** - works from any script/API
- **10-minute Docker setup**
- **Active integrations** with Alertmanager, monitoring tools

**Alternative:** Apprise (supports 90+ notification services as unified API)

**Sources:** [ntfy vs Gotify Comparison](https://blog.vezpi.com/en/post/notification-system-gotify-vs-ntfy/), [ntfy.sh](https://ntfy.sh/)

### Log Aggregation: **Loki + Promtail** ✓
**Why Loki:**
- **"Like Prometheus, but for logs"** - same efficient design philosophy
- **Indexes metadata, not content** - extremely lightweight
- **Native Grafana integration** (but Netdata can also integrate)
- **Multi-tenant** capable
- **Cost-effective** for self-hosting
- Works with Docker json logs natively

**Promtail:**
- **Lightweight agent** for log shipping
- **Docker-native** log collection
- Auto-discovers containers

**Sources:** [Grafana Loki](https://github.com/grafana/loki), [Docker Logs to Loki Guide Oct 2025](https://medium.com/@MetricFire/easiest-way-to-ship-docker-nginx-logs-to-loki-with-promtail-620954937a58)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     OCI Server (159.54.162.114)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Netdata    │    │  Autoheal    │    │  Watchtower  │  │
│  │  (Monitoring)│    │ (Healing)    │    │  (Updates)   │  │
│  │  Port: 19999 │    │              │    │              │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         │                   │                   │           │
│  ┌──────▼────────────────────▼───────────────────▼───────┐  │
│  │          Docker Containers (NetBird, Caddy, etc.)     │  │
│  │  - NetBird Dashboard, Management, Signal, Relay       │  │
│  │  - Caddy Reverse Proxy                                │  │
│  │  - Zitadel Auth                                       │  │
│  │  - PostgreSQL                                         │  │
│  │  - LMS Canvas                                         │  │
│  └──────┬─────────────────────────────────────────────────┘  │
│         │                                                    │
│  ┌──────▼───────┐    ┌──────────────┐                       │
│  │  Promtail    │───▶│     Loki     │                       │
│  │ (Log Agent)  │    │ (Log Store)  │                       │
│  └──────────────┘    └──────┬───────┘                       │
│                             │                               │
│         ┌───────────────────┘                               │
│         │                                                   │
│  ┌──────▼───────┐    ┌──────────────┐                      │
│  │ Alertmanager │───▶│     ntfy     │──────┐               │
│  │  (Routing)   │    │(Notifications)│      │               │
│  └──────────────┘    └──────────────┘      │               │
│                                             │               │
└─────────────────────────────────────────────┼───────────────┘
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │  Your Phone/   │
                                     │  Desktop Apps  │
                                     └────────────────┘
```

---

## Implementation Phases

### **Phase 1: Monitoring Foundation (Week 1)**
**Goal:** Real-time visibility with zero manual configuration

#### 1.1 Deploy Netdata (Day 1-2)
```bash
# Docker Compose deployment
# Auto-discovers all containers, services, hardware metrics
# Built-in anomaly detection with ML
```

**What it monitors automatically:**
- ✓ CPU, Memory, Disk, Network per container
- ✓ Docker container states
- ✓ Nginx metrics (requests, connections, status codes)
- ✓ PostgreSQL metrics
- ✓ System services
- ✓ Disk I/O, latency
- ✓ Network connections, bandwidth

**Metrics Collection:**
- 1-second granularity
- Unlimited metrics (not charged per metric like SaaS)
- 14-day retention by default (configurable)

#### 1.2 Deploy Loki + Promtail (Day 3-4)
```bash
# Centralized log aggregation
# Query logs like metrics with LogQL
```

**Logs Collected:**
- Docker container stdout/stderr
- Nginx access/error logs
- System journals
- Application logs

#### 1.3 Initial Dashboard Setup (Day 5)
- Access Netdata dashboard: `http://159.54.162.114:19999`
- Configure retention policies
- Set up log queries in Loki

**Deliverable:** Real-time monitoring dashboard with 7 days of history

---

### **Phase 2: Alerting & Notifications (Week 2)**
**Goal:** Know when things go wrong, with smart routing

#### 2.1 Deploy ntfy (Day 1)
```bash
# Self-hosted notification service
# HTTP endpoints for push notifications
```

**Setup:**
- ntfy server as Docker container
- Mobile app on your phone
- Desktop app (optional)
- Subscribe to topics: `oci-critical`, `oci-warning`, `oci-info`

#### 2.2 Configure Netdata Alerts (Day 2-3)
**Pre-configured alerts include:**
- Container down/unhealthy
- High CPU (>80% for 5min)
- High memory (>90%)
- Disk space critical (<10% free)
- High disk I/O latency
- Network errors

**Custom alerts for your infrastructure:**
- Caddy not responding
- NetBird management API down
- PostgreSQL connection failures
- LMS Canvas service degraded

#### 2.3 Alert Routing & Escalation (Day 4-5)
```yaml
# Alert severity levels
CRITICAL → ntfy (immediate push notification)
WARNING  → ntfy (batched every 5min)
INFO     → Log only (ntfy daily digest)
```

**Smart routing:**
- Critical: Sound + vibration
- Warning: Silent notification
- Info: Morning summary

**Deliverable:** Receive alerts on your phone within 30 seconds of issues

---

### **Phase 3: Auto-Healing (Week 3)**
**Goal:** Fix problems automatically before you wake up

#### 3.1 Container Health Checks (Day 1-2)
Add HEALTHCHECK to all Docker containers:

```dockerfile
# Example for Caddy
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1
```

**Health checks to add:**
- Caddy: HTTP 200 on health endpoint
- NetBird Dashboard: HTTP response
- PostgreSQL: pg_isready
- Zitadel: HTTP health check
- LMS Canvas: HTTP 200

#### 3.2 Deploy Autoheal (Day 3)
```bash
# Monitors container health
# Auto-restarts unhealthy containers
# Configurable restart policies
```

**Configuration:**
- Check interval: 10 seconds
- Restart unhealthy containers automatically
- Alert on restart (via ntfy)
- Max restarts before giving up: 3
- Cooldown period: 5 minutes

#### 3.3 Deploy Watchtower (Day 4-5)
```bash
# Automated image updates
# Configurable schedule
```

**Configuration:**
- Update check: Weekly (Sunday 3 AM your timezone)
- Auto-update only: security patches
- Requires approval for: major versions
- Cleanup old images: Yes
- Alert before/after updates

**Safety features:**
- Label-based inclusion/exclusion
- Test mode (alerts only, no updates)
- Rollback on failure

**Deliverable:** Self-healing infrastructure with 95%+ automated recovery

---

### **Phase 4: Advanced Monitoring (Week 4)**
**Goal:** Deep insights and predictive monitoring

#### 4.1 Anomaly Detection
**Netdata ML features:**
- Automatic baseline learning
- Anomaly rate scoring
- Predictive alerts (before problems occur)

**Enabled for:**
- Memory trends (detect leaks)
- Disk space growth (predict out-of-space)
- CPU patterns (detect crypto miners)
- Network traffic (detect DDoS)

#### 4.2 Custom Metrics
**Business metrics:**
- NetBird active connections count
- LMS Canvas API response times
- TOTAL-FIX presentation page views
- Caddy request rates by endpoint

#### 4.3 SLA Monitoring
**Track uptime:**
- NetBird dashboard: 99.9% target
- Caddy reverse proxy: 99.95% target
- Overall system: 99.5% target

**Monthly reports:**
- Uptime percentage
- MTTR (Mean Time To Recovery)
- Incident count by severity
- Auto-healing success rate

**Deliverable:** Comprehensive monitoring with trend analysis

---

### **Phase 5: Maintenance Automation (Week 5)**
**Goal:** Hands-off maintenance during your sleep

#### 5.1 Scheduled Tasks
```bash
# Cron-based automation
# Systemd timers (more reliable)
```

**Daily (3:00 AM EET / Cairo time):**
- Docker system prune (remove unused images)
- Log rotation
- Backup health check
- Security scan

**Weekly (Sunday 3:00 AM EET):**
- System updates check
- Container image updates (Watchtower)
- Disk space cleanup
- Certificate renewal check

**Monthly (1st Sunday 3:00 AM EET):**
- Full system reboot (if no issues in past 7 days)
- Backup verification
- Security audit
- Metrics cleanup (old data)

#### 5.2 Pre-Reboot Safety Checks
```bash
# Only reboot if ALL pass:
✓ No critical alerts in past 7 days
✓ All containers healthy
✓ Disk space >20%
✓ No scheduled events (you can configure blackout dates)
✓ Time window: 2:00-5:00 AM EET (Cairo time)
```

**Reboot process:**
1. Alert you 1 hour before
2. Drain connections gracefully
3. Stop non-critical services first
4. Reboot
5. Verify all services restart
6. Send success/failure alert

#### 5.3 Backup Integration
**Automated backups:**
- Docker volume backups (daily)
- Configuration backups (on change)
- Database dumps (daily)
- Off-server storage (encrypted)

**Backup monitoring:**
- Alert if backup fails
- Alert if no backup in 36 hours
- Monthly backup restore test

**Deliverable:** Fully automated maintenance with safety checks

---

## Resource Requirements

### Estimated Overhead (All Monitoring Components)

| Component      | CPU (avg) | Memory  | Disk (logs) | Network      |
|----------------|-----------|---------|-------------|--------------|
| Netdata        | 2-3%      | 100 MB  | 500 MB/day  | 1-2 Mbps     |
| Loki           | 1-2%      | 128 MB  | 1 GB/day    | <1 Mbps      |
| Promtail       | <1%       | 64 MB   | -           | <1 Mbps      |
| ntfy           | <1%       | 32 MB   | 10 MB/day   | <1 Mbps      |
| Autoheal       | <1%       | 16 MB   | 1 MB/day    | Negligible   |
| Watchtower     | <1%       | 32 MB   | 5 MB/day    | Variable     |
| **TOTAL**      | **5-8%**  | **372MB**| **1.5GB/day** | **2-4 Mbps** |

**Your current server:** 51% memory used, 29% disk used
- ✓ Plenty of headroom for monitoring stack
- ✓ Estimated final usage: 56% memory, 32% disk (1 week retention)

---

## Alert Configuration

### Critical Alerts (Immediate ntfy push)
- Any container down >1 minute
- Caddy unreachable
- Disk space <5%
- Memory >95%
- Zitadel auth service down
- PostgreSQL down

### Warning Alerts (Batched every 5min)
- Container restarted
- Disk space <15%
- Memory >85%
- High CPU >80% for 5min
- SSL cert expires in <30 days
- Failed login attempts >10/min

### Info Alerts (Daily digest)
- Container updated
- Scheduled reboot completed
- Backup completed
- Weekly uptime summary

---

## Security Considerations

### Access Control
- Netdata dashboard: Reverse proxy auth (through Caddy)
- ntfy topics: ACL with passwords
- Loki: No external access (internal only)

### Data Privacy
- All monitoring data stays on your server
- No phone-home to vendors
- Encrypted backups
- Minimal log retention (GDPR-friendly)

### Hardening
- Rate limiting on notification endpoints
- Fail2ban integration for repeated failures
- Audit logs for all administrative actions

---

## Cost Analysis

### Current SaaS Alternatives (Monthly Cost)
- Datadog: ~$31-45/host + $0.10/GB logs = **$50-100/mo**
- New Relic: ~$25-100/mo
- Prometheus Cloud: ~$30-60/mo
- PagerDuty: ~$21/user/mo

### This Solution
- **$0/mo** (self-hosted, open source)
- Only cost: Server resources (already paid for)
- **ROI: Immediate** - saves $600-1200/year

---

## Maintenance Overhead

### Initial Setup: ~40 hours (5 weeks × 8 hours)
- Week 1: 8 hours
- Week 2: 8 hours
- Week 3: 8 hours
- Week 4: 8 hours
- Week 5: 8 hours

### Ongoing Maintenance: ~1-2 hours/month
- Review alerts/incidents: 30 min
- Update configurations: 30 min
- Review metrics/trends: 30 min
- Tune alert thresholds: 15 min

**Automation reduces manual work by 90%+**

---

## Success Metrics

### Week 1 (Monitoring)
- ✓ Can see all container metrics in real-time
- ✓ Historical data for past 7 days
- ✓ Log search working for all containers

### Week 2 (Alerting)
- ✓ Receive test alerts on phone
- ✓ Alert routing working correctly
- ✓ No false positives for 48 hours

### Week 3 (Auto-Healing)
- ✓ Autoheal restarts unhealthy container
- ✓ Alert received when healing happens
- ✓ No manual intervention needed for common issues

### Week 4 (Advanced)
- ✓ Anomaly detection identifying patterns
- ✓ Custom metrics tracking business KPIs
- ✓ Uptime >99.5% for the week

### Week 5 (Automation)
- ✓ Automated maintenance completing successfully
- ✓ No unexpected reboots
- ✓ All backups verified

---

## Rollback Plan

### If Monitoring Causes Issues
1. Stop all monitoring containers
2. Remove Docker network integration
3. Clear monitoring data
4. Server returns to original state

**Each phase is independent** - can roll back individually

### Data Retention
- Keep 7 days minimum for troubleshooting
- Archive monthly summaries
- Delete raw data after 30 days

---

## Configuration Summary

### User Preferences (Configured)
- **Timezone:** Cairo, Egypt (EET, UTC+2)
- **Notifications:** ntfy + Telegram integration
- **Alert Sensitivity:** Balanced (standard thresholds, occasional warnings)
- **Scheduled Reboot:** Monthly (1st Sunday, 3:00 AM EET)

### Service Priority (Critical to Standard)
**Priority 1 - Critical (immediate alerts):**
1. NetBird VPN infrastructure (management, dashboard, relay, signal)
2. Zitadel authentication service
3. Caddy reverse proxy

**Priority 2 - High (5-minute batched alerts):**
4. TOTAL-FIX presentation site
5. PostgreSQL database
6. Coturn (TURN/STUN server)

**Priority 3 - Standard (monitoring only, no auto-restart):**
7. LMS Canvas platform (excluded from critical monitoring)

### Alert Routing Configuration
```yaml
CRITICAL (Priority 1 services down):
  - ntfy topic: oci-critical
  - Telegram: Immediate message
  - Sound: Enabled
  - Retry: 3 attempts, 1 min apart

WARNING (High resource usage, restarts):
  - ntfy topic: oci-warning
  - Telegram: Batched every 5 minutes
  - Sound: Disabled

INFO (Updates, maintenance):
  - ntfy topic: oci-info
  - Telegram: Daily digest (8:00 AM EET)
  - Sound: Disabled
```

## Next Steps

1. ✅ **Plan reviewed and approved**
2. ✅ **Configuration completed**
3. **Ready to start Week 1 implementation** (Netdata + Loki)
4. **Iterate based on real-world observations**

---

## References & Sources

### Monitoring Research
- [Netdata vs Prometheus 2025 Performance Analysis](https://www.netdata.cloud/blog/netdata-vs-prometheus-2025/)
- [Best Open Source Monitoring Tools 2025](https://devopscube.com/best-opensource-monitoring-tools/)
- [Docker Monitoring Tools Comparison](https://betterstack.com/community/comparisons/docker-monitoring-addons/)

### Notification Systems
- [ntfy vs Gotify Testing Comparison](https://blog.vezpi.com/en/post/notification-system-gotify-vs-ntfy/)
- [ntfy.sh Official Documentation](https://ntfy.sh/)
- [Apprise vs ntfy Comparison](https://www.xda-developers.com/reasons-use-apprise-instead-of-ntfy-gotify/)

### Auto-Healing & Updates
- [docker-autoheal GitHub (Rust version)](https://github.com/tmknight/docker-autoheal)
- [Watchtower Docker Guide 2025](https://betterstack.com/community/guides/scaling-docker/watchtower-docker/)
- [Docker Container Auto-Healing Best Practices](https://www.amishbhadeshia.co.uk/posts/docker-container-autonomy/)

### Log Aggregation
- [Grafana Loki GitHub](https://github.com/grafana/loki)
- [Docker Logs to Loki Guide (Oct 2025)](https://medium.com/@MetricFire/easiest-way-to-ship-docker-nginx-logs-to-loki-with-promtail-620954937a58)
- [Promtail Docker Compose Setup](https://docs.techdox.nz/loki/)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-23
**Author:** Claude Code (with extensive research)
**Review Status:** Pending approval
