# TODO - Release v0.2.0 - Dependency Management System

## Overview
This TODO list contains actionable tasks to build a comprehensive dependency management system for the myOCI infrastructure project. This release adds version tracking, update procedures, compatibility documentation, and automation scripts to ensure predictable, safe updates across all infrastructure components.

**Strategic Context**: v0.2.0 is the foundation for Phase 3 (auto-healing with Watchtower). Without robust dependency management, automated updates would be risky. This release establishes the processes and tools needed for confident, controlled updates.

**Link to Strategy**: See `.claude/PLANNING.md` for complete release plan, risk analysis, and deployment strategy.

## Current Focus
**Start with these tasks in order (Week 1 prep):**
1. [PRE-1] Check current production versions (Netdata, ntfy)
2. [PRE-2] Decide scope boundaries (monitoring vs full infrastructure)
3. [PRE-3] Verify prerequisites (jq, SSH access, Docker API)

**After 1-week v0.1.0 validation, begin implementation:**
4. [BLOCKER-1] Create DEPENDENCIES.md baseline documentation
5. [BLOCKER-2] Create UPDATE_POLICY.md procedures

---

## Pre-Implementation Tasks (Before Dec 1)

### [PRE-1] Check current production versions

**Priority**: High (Blocker for implementation)
**Estimated Effort**: Small (15 minutes)
**Dependencies**: None
**Risk Level**: Low

#### Context
Before pinning Docker image versions, we need to know what versions are currently running in production. This ensures we pin to known-stable versions, not randomly selected ones.

#### Acceptance Criteria
- [ ] Current Netdata version identified and documented
- [ ] Current ntfy version identified and documented
- [ ] Version information recorded in notes for use in DEPENDENCIES.md
- [ ] Verified versions are available in Docker registries

#### Implementation Notes
**SSH to production server and run:**
```bash
# Check Netdata version
docker inspect oci-netdata --format '{{.Config.Image}}'
docker inspect oci-netdata | jq -r '.[0].Config.Labels["org.opencontainers.image.version"]' || echo "Version label not found"

# Check ntfy version
docker inspect oci-ntfy --format '{{.Config.Image}}'
docker inspect oci-ntfy | jq -r '.[0].Config.Labels["version"]' || echo "Version label not found"

# Alternative: Check via container logs/version commands
docker exec oci-netdata netdata -V 2>/dev/null || echo "Command not found"
docker exec oci-ntfy ntfy --version 2>/dev/null || echo "Command not found"
```

**Document findings:**
- Record exact image tags currently in use
- Record any version labels or metadata
- If using `:latest`, record the actual SHA or version it resolves to
- Note when versions were checked (date/time)

#### Testing Requirements
- Verify Docker Hub shows these versions exist and are downloadable
- Check release notes for any known issues with these versions

#### Definition of Done
- [ ] Netdata version documented (format: `vX.Y.Z` or specific tag)
- [ ] ntfy version documented (format: `vX.Y.Z` or specific tag)
- [ ] Notes saved for reference during DEPENDENCIES.md creation
- [ ] Verified versions are publicly available in registries

---

### [PRE-2] Decide scope boundaries for v0.2.0

**Priority**: High (Blocker for documentation)
**Estimated Effort**: Small (30 minutes)
**Dependencies**: None
**Risk Level**: Low

#### Context
PLANNING.md Open Question Q8: Should v0.2.0 document monitoring stack only, or extend to broader infrastructure (NetBird, Caddy, Zitadel, PostgreSQL)?

**Recommendation from planning**: Monitoring stack + critical dependencies (Docker, Docker Compose, Caddy)

#### Acceptance Criteria
- [ ] Scope decision made and documented
- [ ] Components list finalized for DEPENDENCIES.md
- [ ] Effort estimate adjusted if scope changes
- [ ] Documented in PLANNING.md (update Q8 with decision)

#### Implementation Notes
**Options to decide between:**
- **Option A**: Monitoring stack only (Netdata, Loki, Promtail, Grafana, ntfy, Telegram forwarder)
- **Option B**: Monitoring + critical deps (above + Docker, Docker Compose, Caddy)
- **Option C**: Full infrastructure (above + NetBird, Zitadel, PostgreSQL)

**Recommended**: Option B (monitoring + critical deps)

**Rationale**:
- Focus on v0.2.0 scope (monitoring dependency management)
- Include dependencies monitoring needs to function (Caddy reverse proxy, Docker runtime)
- Defer broader infrastructure to v0.2.1 (incremental expansion)
- Keeps initial effort manageable (15-20 hours vs 25-30 hours)

#### Testing Requirements
- Review components list with stakeholder (if applicable)
- Verify no critical missing dependencies

#### Definition of Done
- [ ] Scope decision documented in PLANNING.md
- [ ] Components list written down for reference
- [ ] If deviating from recommendation, rationale documented
- [ ] Committed decision to git (update PLANNING.md)

---

### [PRE-3] Verify prerequisites and setup

**Priority**: Medium
**Estimated Effort**: Small (15 minutes)
**Dependencies**: None
**Risk Level**: Low

#### Context
Scripts and documentation require certain tools and access. Verify these before starting implementation to avoid interruptions.

#### Acceptance Criteria
- [ ] `jq` installed on development machine (for JSON parsing)
- [ ] SSH access to production server verified
- [ ] Docker socket access confirmed (for scripts)
- [ ] Git repository clean and up to date
- [ ] Working directory prepared (`scripts/` directory ready to create)

#### Implementation Notes
**Check jq installation:**
```bash
which jq
jq --version
# If not installed: brew install jq (macOS) or apt-get install jq (Linux)
```

**Verify SSH access:**
```bash
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 'echo "SSH access confirmed"'
```

**Check Docker API access (local):**
```bash
docker ps
docker version
```

**Verify git status:**
```bash
cd ~/myOCI
git status
git pull origin main
```

**Create directories if needed:**
```bash
mkdir -p ~/myOCI/scripts
ls -la ~/myOCI/scripts
```

#### Testing Requirements
- All commands execute without errors
- Can read/write to all necessary locations

#### Definition of Done
- [ ] All prerequisites verified working
- [ ] Any missing tools installed
- [ ] SSH access confirmed
- [ ] Scripts directory created and accessible
- [ ] Ready to begin implementation

---

## High Priority Tasks (Blockers - Must Complete for v0.2.0)

### [BLOCKER-1] Create DEPENDENCIES.md baseline documentation

**Priority**: High (Release Blocker)
**Estimated Effort**: Large (3-4 hours)
**Dependencies**: PRE-1 (need version info), PRE-2 (need scope decision)
**Risk Level**: Low

#### Context
DEPENDENCIES.md is the central source of truth for all infrastructure component versions. This is the foundation document for dependency management - all other tools and processes reference it.

**From PLANNING.md**: Primary deliverable, ~100-200 lines, comprehensive version tracking

#### Acceptance Criteria
- [ ] Complete monitoring stack documentation with current versions
- [ ] Python dependencies documented (from requirements.txt)
- [ ] System dependencies documented (Docker, Docker Compose)
- [ ] Last verified dates included for each component
- [ ] Links to upstream changelogs included
- [ ] Known vulnerabilities section created (empty if none currently known)
- [ ] Update history section created with initial baseline entry
- [ ] Cross-referenced with docker-compose.yml versions for accuracy

#### Implementation Notes

**File Location**: `/Users/rayiskander/myOCI/DEPENDENCIES.md`

**Document Structure**:
```markdown
# Infrastructure Dependencies

Last Updated: [Date]
Version: 1.0

## Overview
This document tracks all infrastructure component versions for the myOCI project. It serves as the central source of truth for dependency management, update planning, and compatibility verification.

**Purpose**:
- Track current versions of all infrastructure components
- Document known vulnerabilities and remediation status
- Provide update history and compatibility notes
- Support automated version checking (scripts/check-versions.sh)

**Update Frequency**: Review and update this document:
- After any component update (immediate)
- During monthly maintenance reviews (first Sunday of month)
- When security vulnerabilities are discovered (immediate)

---

## Docker Images - Monitoring Stack

| Component | Image | Current Version | Registry | Last Updated | Status | Notes |
|-----------|-------|-----------------|----------|--------------|--------|-------|
| Netdata | netdata/netdata | [from PRE-1] | Docker Hub | YYYY-MM-DD | ✅ Current | Real-time monitoring |
| Loki | grafana/loki | 3.0.0 | Docker Hub | 2025-11-23 | ✅ Current | Log aggregation |
| Promtail | grafana/promtail | 3.0.0 | Docker Hub | 2025-11-23 | ✅ Current | Log collection |
| Grafana | grafana/grafana | 11.0.0 | Docker Hub | 2025-11-23 | ✅ Current | Visualization |
| ntfy | binwiederhier/ntfy | [from PRE-1] | Docker Hub | YYYY-MM-DD | ✅ Current | Notifications |
| Telegram Forwarder | python:3.11-alpine | 3.11-alpine | Docker Hub | 2025-11-23 | ✅ Current | Base image for custom forwarder |

**Changelog Links**:
- Netdata: https://github.com/netdata/netdata/releases
- Loki: https://github.com/grafana/loki/releases
- Promtail: https://github.com/grafana/loki/releases (same project)
- Grafana: https://github.com/grafana/grafana/releases
- ntfy: https://github.com/binwiederhier/ntfy/releases
- Python: https://www.python.org/downloads/

---

## Python Dependencies

**Telegram Forwarder** (`monitoring/telegram-forwarder/requirements.txt`):
| Package | Version | Purpose | Last Updated | Security Status |
|---------|---------|---------|--------------|-----------------|
| requests | 2.31.0 | HTTP client for Telegram API | 2025-11-23 | ✅ No known CVEs |

**Security Notes**:
- requests 2.31.0 is the latest stable version as of Nov 2023
- No known vulnerabilities affecting our usage
- Monitor: https://github.com/psf/requests/security/advisories

---

## System Dependencies

| Component | Version | Purpose | Verification Command |
|-----------|---------|---------|----------------------|
| Docker Engine | 24.0+ | Container runtime | `docker --version` |
| Docker Compose | 2.20+ | Multi-container orchestration | `docker-compose --version` |
| Bash | 4.0+ | Script execution | `bash --version` |
| jq | 1.6+ | JSON parsing in scripts | `jq --version` |

**Installation Requirements**:
- Docker Engine 20.10+ minimum, 24.0+ recommended
- Docker Compose v2 syntax required (using `docker-compose` or `docker compose`)
- jq required for version check scripts

---

## Infrastructure Dependencies (Critical)

| Component | Version | Purpose | Location | Update Frequency |
|-----------|---------|---------|----------|------------------|
| Caddy | [TBD] | Reverse proxy for web access | infrastructure_files | As needed |
| NetBird Network | [TBD] | VPN overlay network | infrastructure_files | As needed |

**Note**: Full infrastructure dependencies (NetBird, Zitadel, PostgreSQL) to be documented in v0.2.1. Current scope focuses on monitoring stack and critical dependencies.

---

## Known Vulnerabilities

**Current Status**: ✅ No known vulnerabilities affecting deployed versions

**Monitoring Sources**:
- GitHub Security Advisories for each component
- Docker Hub security scanning results
- CVE databases (NVD, CVE.org)
- Vendor security mailing lists

**Last Checked**: YYYY-MM-DD

**Process**: See UPDATE_POLICY.md for vulnerability response procedures.

---

## Update History

### 2025-11-24 - v0.2.0 Baseline
- **Action**: Initial dependency documentation created
- **Changes**: Established baseline for all monitoring stack components
- **Versions Pinned**:
  - Netdata: latest → [specific version from PRE-1]
  - ntfy: latest → [specific version from PRE-1]
- **Reason**: Establishing dependency management foundation
- **Risk**: Low - documenting existing production state
- **Outcome**: Baseline established successfully

### 2025-11-23 - v0.1.0 Initial Deployment
- **Action**: Monitoring stack deployed to production
- **Components**: Netdata, Loki 3.0.0, Promtail 3.0.0, Grafana 11.0.0, ntfy, Telegram forwarder
- **Note**: Netdata and ntfy deployed with `:latest` tags (to be pinned in v0.2.0)

---

## Compatibility Notes

### Loki + Promtail
- **Requirement**: Loki and Promtail versions MUST match
- **Current**: Both at 3.0.0 (compatible)
- **Reason**: Same codebase, API compatibility guaranteed within same version

### Grafana + Loki
- **Requirement**: Grafana 11.x compatible with Loki 3.x
- **Current**: Grafana 11.0.0 + Loki 3.0.0 (compatible)
- **Reference**: https://grafana.com/docs/loki/latest/setup/upgrade/

### Python + requests
- **Requirement**: Python 3.11+ for requests 2.31.0
- **Current**: Python 3.11-alpine (compatible)

See COMPATIBILITY_MATRIX.md for comprehensive version compatibility matrix.

---

## Version Check Automation

This document is used by `scripts/check-versions.sh` to compare running versions against documented baseline.

**Run version check:**
```bash
cd ~/myOCI
bash scripts/check-versions.sh
```

**Expected Output**: Report showing current vs baseline versions, flagging any mismatches.

---

## Contributing Updates

When updating component versions:

1. **Test Update First**: Follow UPDATE_POLICY.md testing procedures
2. **Update This Document**: Modify version numbers and dates
3. **Add Update History Entry**: Document what changed and why
4. **Update COMPATIBILITY_MATRIX.md**: If compatibility changes
5. **Update CHANGELOG.md**: For release notes
6. **Commit Changes**: `git commit -m "Update [component] from vX to vY"`

---

## References

- **Update Procedures**: UPDATE_POLICY.md
- **Compatibility Matrix**: COMPATIBILITY_MATRIX.md
- **Security Hardening**: monitoring/SECURITY.md
- **Backup Procedures**: monitoring/BACKUP.md
- **Version Check Script**: scripts/check-versions.sh

---

**Document Version**: 1.0
**Created**: 2025-11-24 (v0.2.0)
**Last Updated**: 2025-11-24
**Next Review**: 2025-12-24 (monthly review)
```

**Files to reference while writing**:
- `monitoring/docker-compose.yml` - Current image definitions
- `monitoring/telegram-forwarder/requirements.txt` - Python dependencies
- Notes from PRE-1 - Production version info
- Scope decision from PRE-2 - What to include

#### Testing Requirements
- Cross-check all version numbers against docker-compose.yml
- Verify all upstream changelog links work
- Verify document renders correctly in Markdown viewer
- Check for typos and formatting errors

#### Definition of Done
- [ ] Complete document created with all sections
- [ ] All monitoring stack versions documented accurately
- [ ] Python dependencies documented
- [ ] System dependencies listed
- [ ] Changelog links verified working
- [ ] Update history includes v0.2.0 baseline entry
- [ ] File created at correct path
- [ ] Markdown formatting correct (no rendering errors)
- [ ] Cross-referenced with docker-compose.yml (versions match)
- [ ] Committed to git with message: "Add DEPENDENCIES.md - v0.2.0 baseline"

---

### [BLOCKER-2] Create UPDATE_POLICY.md procedures

**Priority**: High (Release Blocker)
**Estimated Effort**: Large (2-3 hours)
**Dependencies**: None (can work in parallel with BLOCKER-1)
**Risk Level**: Low

#### Context
UPDATE_POLICY.md formalizes update strategy and procedures. Critical for safe updates, especially before enabling Watchtower auto-updates in v0.3.0.

**From PLANNING.md**: Primary deliverable, ~150-250 lines, policy and procedures

#### Acceptance Criteria
- [ ] Update frequency guidelines defined (security vs feature)
- [ ] Risk classification system documented (Critical/High/Medium/Low)
- [ ] Pre-update testing checklist created
- [ ] Staged rollout procedures documented
- [ ] Rollback procedures documented with clear criteria
- [ ] Maintenance window scheduling policy defined
- [ ] Stakeholder communication templates included
- [ ] Security vulnerability tracking process documented
- [ ] Response SLAs defined (Critical: 24h, High: 7d, Medium: 30d)

#### Implementation Notes

**File Location**: `/Users/rayiskander/myOCI/UPDATE_POLICY.md`

**Document Structure**:
```markdown
# Update Policy & Procedures

Version: 1.0
Last Updated: 2025-11-24
Status: Active

## Overview

This document defines policies and procedures for updating infrastructure components in the myOCI project. It ensures updates are performed safely, predictably, and with minimal risk to production services.

**Scope**: All infrastructure components documented in DEPENDENCIES.md

**Objectives**:
- Maintain security through timely patching
- Minimize disruption through careful planning
- Enable rapid rollback if issues occur
- Provide clear communication to stakeholders

---

## Update Frequency Guidelines

### Security Updates
**Frequency**: As soon as possible after verification
**Maximum Delay**: Based on severity (see SLAs below)
**Rationale**: Security vulnerabilities pose immediate risk

**Process**:
1. Security advisory received/discovered
2. Assess severity and impact (see Risk Classification below)
3. Test update in non-production (if possible)
4. Deploy within SLA window
5. Monitor for 24-48 hours
6. Document in DEPENDENCIES.md

### Feature Updates
**Frequency**: Monthly review cycle (first Sunday of month)
**Exceptions**: Critical bug fixes may be expedited
**Rationale**: Balance new features with stability

**Process**:
1. Review available updates during monthly maintenance
2. Assess value vs risk
3. Schedule for next maintenance window
4. Test thoroughly before production
5. Deploy during scheduled window
6. Monitor for 1 week

### Patch Updates
**Frequency**: Quarterly or as needed
**Exceptions**: If patch addresses bugs affecting our use case
**Rationale**: Lower risk, lower urgency

**Process**:
1. Accumulate patch updates over quarter
2. Review and batch during quarterly maintenance
3. Test combined updates
4. Deploy during scheduled window

---

## Risk Classification

### Critical (Immediate Action)
**Characteristics**:
- Actively exploited vulnerability (CVE CVSS 9.0+)
- Data loss or corruption risk
- Service unavailability affecting critical functions
- Public disclosure of zero-day vulnerability

**Response SLA**: 24 hours
**Approval**: System administrator (expedited process)
**Testing**: Minimal - verify service starts and basic functionality
**Communication**: Immediate notification to all stakeholders

**Example**: Remote code execution vulnerability in Grafana with active exploits

---

### High (Urgent)
**Characteristics**:
- Security vulnerability (CVE CVSS 7.0-8.9)
- Major bug fix addressing service instability
- Performance issue causing degradation
- Dependency with known security issue

**Response SLA**: 7 days
**Approval**: System administrator
**Testing**: Standard testing checklist (see below)
**Communication**: Notify stakeholders 48 hours before deployment

**Example**: Authentication bypass vulnerability, no active exploits yet

---

### Medium (Planned)
**Characteristics**:
- Minor security issue (CVE CVSS 4.0-6.9)
- Feature updates with useful enhancements
- Bug fixes for non-critical issues
- Dependency updates for maintenance

**Response SLA**: 30 days
**Approval**: System administrator + team review
**Testing**: Full testing including compatibility checks
**Communication**: Include in monthly update communication

**Example**: New dashboard features in Grafana, optional UI improvements

---

### Low (Opportunistic)
**Characteristics**:
- Minor improvements or cosmetic changes
- Dependency updates with no functional changes
- Documentation updates
- Optional feature additions

**Response SLA**: 90 days or next major release
**Approval**: Standard review process
**Testing**: Full testing suite
**Communication**: Include in quarterly planning

**Example**: Updated logo, minor UI polish, dependency version bumps

---

## Pre-Update Testing Checklist

### Phase 1: Pre-Deployment Research
- [ ] **Review Changelog**: Read upstream release notes thoroughly
- [ ] **Check Breaking Changes**: Identify any breaking changes or migrations
- [ ] **Verify Compatibility**: Check COMPATIBILITY_MATRIX.md for known issues
- [ ] **Assess Risk**: Classify update using Risk Classification above
- [ ] **Check Dependencies**: Ensure dependent components are compatible
- [ ] **Review Issues**: Check GitHub issues for reports of problems with new version

### Phase 2: Local/Staging Testing (If Available)
- [ ] **Backup Configuration**: Create backup of current config
- [ ] **Pull New Image**: `docker pull <image>:<new-version>`
- [ ] **Update Config**: Modify docker-compose.yml with new version
- [ ] **Test Startup**: Verify container starts without errors
- [ ] **Check Logs**: Review logs for warnings or errors
- [ ] **Test Functionality**: Verify key features work (dashboards, alerts, logging)
- [ ] **Check Resource Usage**: Monitor CPU, memory, disk usage
- [ ] **Test Integration**: Verify communication with dependent services
- [ ] **Document Findings**: Note any issues or changes in behavior

### Phase 3: Production Deployment Preparation
- [ ] **Schedule Maintenance Window**: Coordinate with stakeholders (if needed)
- [ ] **Prepare Rollback Plan**: Ensure quick rollback possible (see Rollback section)
- [ ] **Backup Production State**: Backup configs, volumes (see BACKUP.md)
- [ ] **Notify Stakeholders**: Send deployment notification (see Communication section)
- [ ] **Prepare Monitoring**: Set up extra monitoring during deployment
- [ ] **Document Procedure**: Have step-by-step deployment plan ready

### Phase 4: Production Deployment
- [ ] **Apply Update**: Follow deployment procedure
- [ ] **Monitor Startup**: Watch logs during startup (5-10 minutes)
- [ ] **Run Health Checks**: Execute health check script
- [ ] **Verify Functionality**: Test critical paths (dashboards, logs, alerts)
- [ ] **Monitor Performance**: Watch resource usage for 1 hour
- [ ] **Check Integrations**: Verify all dependent services working
- [ ] **Document Outcome**: Record success or issues in DEPENDENCIES.md

### Phase 5: Post-Deployment Validation
- [ ] **24-Hour Monitoring**: Watch for issues over first day
- [ ] **1-Week Review**: Verify stability over extended period
- [ ] **Update Documentation**: Update DEPENDENCIES.md, CHANGELOG.md
- [ ] **Communicate Success**: Send completion notification
- [ ] **Archive Backups**: Move backups to long-term storage

---

## Staged Rollout Procedures

For high-risk updates, consider staged rollout:

### Stage 1: Non-Critical Service (Optional)
If multiple instances available, update least-critical first.

**Example**: Update monitoring stack on development server before production

### Stage 2: Single Component
Update one component, monitor, then proceed to others.

**Process**:
1. Update component A
2. Monitor for 24-48 hours
3. If stable, update component B
4. Continue pattern

**Example**: Update Loki, wait, then update Promtail

### Stage 3: Off-Peak Deployment
Deploy during low-usage periods to minimize impact.

**Recommended Windows**:
- **Weekdays**: Tuesday-Thursday, 2-4 AM EET (Cairo time)
- **Avoid**: Friday-Monday (weekend issues harder to address)
- **Avoid**: During known high-usage periods

### Stage 4: Canary Deployment (Future)
For future multi-instance deployments, consider canary pattern:
- Deploy to 10% of instances
- Monitor for issues
- Gradually increase to 100%

**Note**: Current single-server deployment doesn't support canary, but document for future scaling

---

## Rollback Procedures

### When to Rollback

**Immediate Rollback Triggers**:
- Service fails to start after update
- Critical functionality broken (dashboards, alerting, logging)
- Data loss or corruption detected
- Performance degradation >50%
- Security issue introduced by update
- Cascade failures affecting other services

**Evaluation Period**:
- First 1 hour: High sensitivity - rollback quickly
- First 24 hours: Medium sensitivity - evaluate carefully
- After 1 week: Low sensitivity - update considered stable

### Rollback Procedure

#### Step 1: Assess Situation
```bash
# Check service status
docker ps --filter name=oci-
docker-compose ps

# Check logs for errors
docker-compose logs --tail=100 <service-name>

# Check resource usage
docker stats --no-stream

# Test critical functionality
curl -I http://localhost:19999  # Netdata
curl -I http://localhost:3000   # Grafana
curl http://localhost:8765/v1/health  # ntfy
```

#### Step 2: Decide Rollback or Fix-Forward
**Rollback if**:
- Critical functionality broken
- Can't identify root cause quickly (>30 minutes)
- Fix would take significant time
- Multiple failures or cascading issues

**Fix-Forward if**:
- Minor issue with known fix
- Can resolve in <15 minutes
- Rollback would be more disruptive
- Issue is cosmetic or non-critical

#### Step 3: Execute Rollback
```bash
cd ~/myOCI/monitoring

# Restore previous docker-compose.yml
cp docker-compose.backup.yml docker-compose.yml

# Recreate containers with old version
docker-compose down
docker-compose up -d

# Monitor startup
docker-compose logs -f --tail=50

# Verify services healthy
docker-compose ps
bash ~/myOCI/scripts/check-versions.sh
```

#### Step 4: Verify Rollback Success
```bash
# Check all services running
docker ps --filter name=oci-

# Test functionality
curl http://localhost:19999
curl http://localhost:3000
curl http://localhost:8765/v1/health

# Send test notification
curl -d "Rollback verification test" http://localhost:8765/oci-info
```

#### Step 5: Post-Rollback Actions
- [ ] Document what went wrong in incident log
- [ ] Update DEPENDENCIES.md with rollback event
- [ ] Notify stakeholders of rollback
- [ ] File issue with upstream project (if bug)
- [ ] Schedule investigation and retry (if appropriate)
- [ ] Review and improve testing procedures to catch issue earlier

### Recovery Time Objectives

| Scenario | Target RTO | Notes |
|----------|-----------|-------|
| Version pin rollback | < 5 minutes | Simple docker-compose.yml restore |
| Configuration rollback | < 10 minutes | Restore config files + restart |
| Data corruption | < 1 hour | Restore from backup (see BACKUP.md) |
| Complete rebuild | < 4 hours | Worst case: rebuild from scratch |

---

## Maintenance Window Scheduling

### Regular Maintenance Windows

**Monthly Maintenance**: First Sunday of month, 2-4 AM EET
**Purpose**: Feature updates, non-critical patches, system cleanup
**Duration**: Up to 2 hours
**Notification**: 1 week advance notice

**Quarterly Maintenance**: First Sunday of Q1/Q2/Q3/Q4, 2-6 AM EET
**Purpose**: Major updates, accumulated patches, system audits
**Duration**: Up to 4 hours
**Notification**: 2 weeks advance notice

### Emergency Maintenance Windows

**Critical Security Updates**: Within 24 hours of discovery
**Purpose**: Address critical vulnerabilities
**Duration**: As needed
**Notification**: Best effort (may be <2 hours)

### Maintenance Window Procedures

#### Before Window Opens
- [ ] Review planned changes
- [ ] Verify backups current
- [ ] Prepare rollback plans
- [ ] Test procedures in non-production (if possible)
- [ ] Send reminder notification 24 hours before

#### During Window
- [ ] Record start time
- [ ] Execute changes following checklist
- [ ] Document all actions taken
- [ ] Test after each change
- [ ] Monitor for issues

#### After Window Closes
- [ ] Verify all services operational
- [ ] Send completion notification
- [ ] Update documentation
- [ ] Schedule follow-up monitoring
- [ ] Review what went well / what to improve

---

## Stakeholder Communication

### Communication Templates

#### Pre-Deployment Notification (1 week before)

**Subject**: myOCI Maintenance Window - [Date] - [Component] Update

**Body**:
```
Hello,

A maintenance window is scheduled for the myOCI monitoring infrastructure:

**Date**: [Day], [Date] [Month] 2025
**Time**: [Start] - [End] EET (Cairo time)
**Duration**: Approximately [X] hours
**Impact**: [None expected / Brief interruptions / Service unavailable]

**Changes Planned**:
- Update [Component] from vX.Y.Z to vA.B.C
- Reason: [Security fix / Feature update / Bug fix]
- Risk Level: [Low / Medium / High]

**Expected Impact**:
- [Service Name]: [Impact description]
- Dashboards: [May reload / Will remain available / Brief downtime]
- Alerting: [Unaffected / May have delays / Will be unavailable]

**Rollback Plan**:
[Brief description of rollback procedure and estimated time]

**Testing**:
[Summary of pre-deployment testing completed]

If you have concerns or conflicts, please reply by [Date - 48 hours before].

Thank you,
[Your Name]
Infrastructure Team
```

#### Deployment Completion Notification

**Subject**: myOCI Maintenance Complete - [Component] Update Successful

**Body**:
```
Hello,

The scheduled maintenance for myOCI monitoring infrastructure has been completed successfully.

**Completed**: [Date] at [Time] EET
**Duration**: [Actual time taken]
**Status**: ✅ Successful

**Changes Applied**:
- Updated [Component] from vX.Y.Z to vA.B.C
- [Any other changes]

**Verification**:
- All services operational
- Dashboards accessible
- Alerting functional
- No errors detected

**Monitoring**:
We will continue monitoring the system closely for the next 24-48 hours.

**Documentation Updated**:
- DEPENDENCIES.md: Version numbers updated
- CHANGELOG.md: Changes recorded

If you notice any issues, please report immediately to [contact].

Thank you for your patience.

[Your Name]
Infrastructure Team
```

#### Emergency Update Notification

**Subject**: [URGENT] myOCI Security Update - [Component]

**Body**:
```
Hello,

An urgent security update is required for the myOCI monitoring infrastructure:

**Component**: [Component Name]
**Vulnerability**: [CVE ID or description]
**Severity**: [Critical / High]
**Deployment**: [Date/Time - within 24 hours]

**Risk if Not Updated**:
[Brief description of security risk]

**Expected Impact**:
[Brief description of deployment impact - typically <5 minutes]

**Update will be performed**:
[Date] at [Time] EET

Due to the critical nature, this update cannot be delayed. Rollback plan is in place if issues occur.

More details: [Link to advisory]

Questions or concerns: [Contact]

[Your Name]
Infrastructure Team
```

---

## Security Vulnerability Tracking

### Vulnerability Sources

**Monitor these sources regularly**:

1. **GitHub Security Advisories**
   - Watch repositories for all components
   - Enable security alerts on GitHub
   - Check: https://github.com/[org]/[repo]/security/advisories

2. **Docker Hub Security Scanning**
   - Review scan results for images
   - Check: https://hub.docker.com/r/[image]/tags

3. **CVE Databases**
   - National Vulnerability Database: https://nvd.nist.gov/
   - CVE.org: https://cve.org/
   - Search for: component name + version

4. **Vendor Security Mailing Lists**
   - Subscribe to security announcements for each component
   - Grafana Labs Security: security@grafana.com
   - Netdata Security: security@netdata.cloud

5. **Security News**
   - Hacker News security posts
   - Reddit r/netsec
   - Security-focused newsletters

### Vulnerability Assessment

When vulnerability discovered:

1. **Identify Affected Components**
   - Which versions are vulnerable?
   - Are we running affected version? (check DEPENDENCIES.md)
   - What functionality is affected?

2. **Assess Severity**
   - CVSS score (if available)
   - Exploitability (are there known exploits?)
   - Impact on our deployment
   - Network exposure (internal only vs internet-facing)

3. **Determine Response**
   - Apply Risk Classification (Critical/High/Medium/Low)
   - Set response timeline based on SLA
   - Identify mitigation options (update, workaround, disable feature)

4. **Document Assessment**
   - Record in DEPENDENCIES.md "Known Vulnerabilities" section
   - Include: CVE ID, severity, affected versions, status, plan

### Response SLAs

| Severity | Assessment | Testing | Deployment | Total |
|----------|------------|---------|------------|-------|
| Critical (CVSS 9.0+) | 2 hours | 4 hours | 18 hours | 24 hours |
| High (CVSS 7.0-8.9) | 24 hours | 48 hours | 72 hours | 7 days |
| Medium (CVSS 4.0-6.9) | 1 week | 2 weeks | 1 week | 30 days |
| Low (CVSS <4.0) | As needed | As needed | Next cycle | 90 days |

### Patching Process

1. **Evaluate Patch**
   - Read security advisory and patch notes
   - Understand what the patch fixes
   - Check for side effects or breaking changes

2. **Test Patch**
   - Follow Pre-Update Testing Checklist
   - Verify patch fixes vulnerability
   - Ensure no regressions

3. **Deploy Patch**
   - Follow appropriate update procedure based on severity
   - Use expedited process for Critical/High
   - Monitor closely after deployment

4. **Verify Patch**
   - Confirm vulnerability no longer exploitable
   - Run vulnerability scanner if available
   - Document patch success in DEPENDENCIES.md

5. **Communicate**
   - Notify stakeholders of patch deployment
   - Include: what was patched, why, impact
   - Reference CVE ID for tracking

---

## Version Pinning Policy

**Policy**: All Docker images MUST use specific version tags, not `:latest`

**Rationale**:
- Predictable behavior across restarts
- Controlled updates with testing
- Clear documentation of what's running
- Prerequisite for Watchtower auto-updates (v0.3.0)

**Implementation**:
- Current v0.2.0: Pin Netdata and ntfy (last two using `:latest`)
- Format: `image:vX.Y.Z` or `image:X.Y.Z` (follow upstream convention)
- Document in DEPENDENCIES.md

**Exceptions**: None - all images must be pinned

**Enforcement**: scripts/check-versions.sh will flag `:latest` tags

---

## Automation (Future Enhancements)

### v0.3.0: Watchtower Auto-Updates
**Plan**: Enable Watchtower for automated updates
**Preparation**: This update policy provides foundation
**Configuration**:
- Monitor-only mode initially
- Notification before updates
- Gradual rollout based on update risk classification

### v0.2.1+: Update Notifications
**Plan**: Automated weekly check for available updates
**Implementation**: Cron job running scripts/check-versions.sh
**Notification**: Telegram message if updates available
**Action**: Review and schedule during next maintenance window

---

## References

- **Dependency Documentation**: DEPENDENCIES.md
- **Compatibility Matrix**: COMPATIBILITY_MATRIX.md
- **Backup Procedures**: monitoring/BACKUP.md
- **Security Hardening**: monitoring/SECURITY.md
- **Version Check Script**: scripts/check-versions.sh
- **Maintenance Automation**: monitoring/maintenance.sh

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-24 | Claude Code | Initial release (v0.2.0) |

**Next Review**: 2025-12-24 (1 month)
**Review Frequency**: Quarterly or after major updates
```

#### Testing Requirements
- Review procedures for completeness
- Verify communication templates are clear
- Check risk classification makes sense
- Ensure SLAs are realistic

#### Definition of Done
- [ ] Complete document created with all sections
- [ ] Update frequency guidelines clear
- [ ] Risk classification well-defined
- [ ] Pre-update testing checklist comprehensive
- [ ] Rollback procedures detailed and actionable
- [ ] Communication templates ready to use
- [ ] Security vulnerability tracking documented
- [ ] Response SLAs defined clearly
- [ ] File created at correct path
- [ ] Markdown formatting correct
- [ ] Committed to git with message: "Add UPDATE_POLICY.md - formalized update procedures"

---

### [BLOCKER-3] Create COMPATIBILITY_MATRIX.md

**Priority**: High (Release Blocker)
**Estimated Effort**: Medium (2-3 hours)
**Dependencies**: BLOCKER-1 (need version info from DEPENDENCIES.md)
**Risk Level**: Low

#### Context
COMPATIBILITY_MATRIX.md documents which versions work together. Critical for preventing incompatible combinations, especially for tightly coupled components like Loki + Promtail.

**From PLANNING.md**: ~100-150 lines, version compatibility documentation

#### Acceptance Criteria
- [ ] Current baseline documented as "Tested Combination"
- [ ] Known incompatibilities documented (if any)
- [ ] Major version upgrade paths documented
- [ ] Loki + Promtail version relationship clearly stated
- [ ] Grafana + Loki compatibility noted
- [ ] Python + requests compatibility noted
- [ ] Cross-references to upstream docs included
- [ ] Breaking changes between major versions documented

#### Implementation Notes

**File Location**: `/Users/rayiskander/myOCI/COMPATIBILITY_MATRIX.md`

**Research needed**:
- Check Loki documentation for Promtail compatibility requirements
- Check Grafana documentation for Loki datasource compatibility
- Review upstream docs for known incompatibilities
- Document current baseline as "known good" configuration

**Document Structure**:
```markdown
# Compatibility Matrix

Version: 1.0
Last Updated: 2025-11-24
Last Tested: 2025-11-24

## Overview

This document tracks version compatibility for infrastructure components. Use this matrix when planning updates to ensure compatible version combinations.

**Purpose**:
- Prevent incompatible version combinations
- Document tested configurations
- Provide upgrade paths for major versions
- Reference breaking changes

**Update When**:
- After testing new version combinations
- When upstream documents incompatibilities
- After major version upgrades
- During quarterly compatibility reviews

---

## Tested Configurations

### Current Production Baseline (v0.2.0)

✅ **Fully Tested and Working**

| Component | Version | Notes |
|-----------|---------|-------|
| Netdata | [from DEPENDENCIES.md] | Real-time monitoring |
| Loki | 3.0.0 | Log aggregation |
| Promtail | 3.0.0 | MUST match Loki version |
| Grafana | 11.0.0 | Compatible with Loki 3.x |
| ntfy | [from DEPENDENCIES.md] | Notification server |
| Python | 3.11-alpine | Base for Telegram forwarder |
| requests | 2.31.0 | Requires Python 3.7+ |
| Docker | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | v2 syntax required |

**Test Date**: 2025-11-23 (v0.1.0) and 2025-11-24 (v0.2.0)
**Stability**: ✅ Stable in production
**Issues**: None known
**Recommendation**: Safe baseline for future updates

---

## Component Compatibility Rules

### Loki + Promtail (CRITICAL)

**Rule**: Loki and Promtail versions MUST be identical

**Rationale**: Same codebase, tightly coupled API

**Compatible Pairs**:
| Loki Version | Promtail Version | Status |
|--------------|------------------|--------|
| 3.0.0 | 3.0.0 | ✅ Current (tested) |
| 2.9.x | 2.9.x | ✅ Previous stable |
| 2.8.x | 2.8.x | ✅ Older stable |

**Incompatible Pairs**:
| Loki Version | Promtail Version | Issue |
|--------------|------------------|-------|
| 3.x | 2.x | ❌ API incompatibility |
| 2.x | 3.x | ❌ Protocol mismatch |
| Different minor versions | Different minor versions | ⚠️ May work but unsupported |

**Upgrade Path**:
1. Plan Loki + Promtail upgrade together
2. Test new version pair in staging
3. Deploy both simultaneously
4. Never run mismatched versions in production

**References**:
- https://grafana.com/docs/loki/latest/setup/upgrade/
- https://grafana.com/docs/loki/latest/send-data/promtail/

---

### Grafana + Loki

**Rule**: Grafana 11.x compatible with Loki 3.x

**Rationale**: Loki datasource plugin compatibility

**Compatible Pairs**:
| Grafana Version | Loki Version | Status |
|-----------------|--------------|--------|
| 11.0.0 | 3.0.0 | ✅ Current (tested) |
| 11.x | 3.x | ✅ Expected compatible |
| 10.x | 2.9.x | ✅ Previous stable |
| 9.x | 2.8.x | ✅ Older stable |

**Incompatible Pairs**:
| Grafana Version | Loki Version | Issue |
|-----------------|--------------|-------|
| <9.0 | 3.x | ❌ Datasource plugin too old |
| 11.x | <2.8 | ⚠️ May work but deprecated |

**Upgrade Path**:
- Loki upgrades generally don't require Grafana upgrade
- Grafana upgrades maintain backwards compatibility with older Loki
- Recommended: Keep Grafana relatively current for best experience

**References**:
- https://grafana.com/docs/grafana/latest/datasources/loki/
- https://grafana.com/docs/loki/latest/operations/grafana/

---

### Python + requests

**Rule**: requests 2.31.0 requires Python 3.7+

**Rationale**: requests library uses Python 3.7+ features

**Compatible Pairs**:
| Python Version | requests Version | Status |
|----------------|------------------|--------|
| 3.11-alpine | 2.31.0 | ✅ Current (tested) |
| 3.10+ | 2.31.0 | ✅ Compatible |
| 3.7-3.9 | 2.31.0 | ✅ Compatible (older Python) |

**Incompatible Pairs**:
| Python Version | requests Version | Issue |
|----------------|------------------|-------|
| <3.7 | 2.31.0 | ❌ Syntax/feature incompatibility |
| Any | <2.28 | ⚠️ Security vulnerabilities |

**Upgrade Path**:
- Keep Python on latest stable minor version (currently 3.11)
- Keep requests on latest stable version (currently 2.31.0)
- Update Python minor version with testing

**References**:
- https://requests.readthedocs.io/en/latest/
- https://pypi.org/project/requests/

---

### Docker + Docker Compose

**Rule**: Docker 20.10+ and Docker Compose v2 required

**Rationale**: Modern Docker features, v2 compose syntax

**Compatible Pairs**:
| Docker Version | Docker Compose Version | Status |
|----------------|------------------------|--------|
| 24.0+ | 2.20+ | ✅ Current recommended |
| 23.0+ | 2.10+ | ✅ Compatible |
| 20.10+ | 2.0+ | ✅ Minimum supported |

**Incompatible Pairs**:
| Docker Version | Docker Compose Version | Issue |
|----------------|------------------------|-------|
| <20.10 | Any v2 | ❌ Missing features |
| Any | v1.x | ❌ Deprecated syntax |

**Upgrade Path**:
- Use Docker Desktop (bundled) or install separately
- Migrate from docker-compose v1 to v2 if needed
- Test compose files with `docker-compose config` after upgrade

**References**:
- https://docs.docker.com/compose/
- https://docs.docker.com/engine/release-notes/

---

## Breaking Changes by Version

### Loki 3.0.0 (From 2.x)

**Breaking Changes**:
- Schema change: TSDB (v13) is default
- Configuration changes: Some fields removed/renamed
- API changes: Some endpoints deprecated

**Migration Path**:
1. Backup Loki data (or accept data loss for logs)
2. Update Loki configuration for v3.0 syntax
3. Update Promtail to matching 3.0.0 version
4. Test configuration: `docker-compose config`
5. Deploy with monitoring
6. Verify log ingestion working

**References**:
- https://grafana.com/docs/loki/latest/setup/upgrade/upgrade-to-3.0/

**Our Experience** (v0.1.0 deployment):
- ✅ TSDB schema (v13) works well
- ✅ 24-hour retention policy performs well
- ⚠️ Had to update config syntax (delete_request_store)
- ⚠️ Previous data not migrated (accepted for new deployment)

---

### Grafana 11.0.0 (From 10.x)

**Breaking Changes**:
- Some panel types deprecated
- AngularJS plugins no longer supported
- Some configuration options changed

**Migration Path**:
1. Review Grafana upgrade guide
2. Check dashboards for deprecated panels
3. Test dashboards after upgrade
4. Update dashboards if needed

**References**:
- https://grafana.com/docs/grafana/latest/whatsnew/
- https://grafana.com/docs/grafana/latest/setup-grafana/upgrade-grafana/

**Our Experience** (v0.1.0 deployment):
- ✅ Deployed directly on 11.0.0 (no upgrade needed)
- ✅ Dashboard provisioning works well
- ✅ Loki datasource compatible

---

### Python 3.11 (From 3.10)

**Breaking Changes**:
- Minimal for most code
- Some standard library changes
- Performance improvements

**Migration Path**:
- Generally smooth upgrade from 3.10
- Test application after upgrade
- Check for deprecation warnings

**Our Experience**:
- ✅ Telegram forwarder works on 3.11-alpine
- ✅ requests library fully compatible
- ✅ No issues encountered

---

## Upgrade Strategies

### Conservative (Recommended for Production)

1. **Stay on Stable Versions**
   - Wait 30 days after major version release
   - Use X.Y.Z versions, not .0 releases
   - Example: Wait for 11.0.1 instead of 11.0.0

2. **One Component at a Time**
   - Update single component
   - Monitor for 1 week
   - Proceed to next component

3. **Test Before Production**
   - Test in development/staging if available
   - Run full testing checklist
   - Verify rollback procedure ready

### Aggressive (For Development/Non-Critical)

1. **Early Adoption**
   - Deploy .0 releases shortly after release
   - Test new features early
   - Report issues to upstream

2. **Batch Updates**
   - Update multiple components together
   - Faster iteration
   - Higher risk of issues

3. **Latest Stable**
   - Always run latest minor version
   - Get features and fixes faster
   - Requires more frequent testing

### Security-Driven (For Critical Vulnerabilities)

1. **Immediate Patching**
   - Apply security updates within SLA (24h-7d)
   - Minimal testing acceptable for Critical
   - Monitor closely after deployment

2. **Version Jumping**
   - May skip intermediate versions
   - Jump directly to patched version
   - Test thoroughly if major version jump

---

## Testing New Combinations

### Testing Checklist

When testing new version combination:

- [ ] **Research**: Read changelogs and upgrade guides
- [ ] **Compatibility Check**: Consult this matrix and upstream docs
- [ ] **Backup**: Create backup before testing
- [ ] **Configuration**: Update configs for new version if needed
- [ ] **Deployment**: Deploy in test environment if available
- [ ] **Functionality**: Test all critical features
- [ ] **Performance**: Monitor resource usage
- [ ] **Integration**: Verify all services communicate correctly
- [ ] **Duration**: Run for 24-48 hours minimum
- [ ] **Issues**: Document any problems encountered
- [ ] **Rollback Test**: Verify rollback works if issues found
- [ ] **Documentation**: Update this matrix with findings

### Recording Test Results

Add tested combinations to "Tested Configurations" section:

```markdown
### [Version Combination Name] - Tested YYYY-MM-DD

✅/⚠️/❌ **Status**

| Component | Version | Notes |
|-----------|---------|-------|
| ... | ... | ... |

**Test Date**: YYYY-MM-DD
**Stability**: [Stable / Issues / Unstable]
**Issues**: [List any issues]
**Recommendation**: [Safe / Use with caution / Not recommended]
```

---

## Known Issues

### Current Baseline (v0.2.0)

**No known issues** with current version combination.

### Previous Issues (Historical Reference)

#### Issue: Loki 3.0 Configuration Syntax
**Affected Versions**: Loki 3.0.0 initial deployment
**Issue**: Invalid config fields from Loki 2.x syntax
**Resolution**: Updated config to Loki 3.0 syntax
**Workaround**: Use configuration from monitoring/loki/config.yml
**Reference**: Commit e97318c (2025-11-23)

#### Issue: Grafana Dashboard Timeout
**Affected Versions**: Grafana 11.0.0 initial deployment
**Issue**: Dashboards loading perpetually due to missing Loki retention
**Resolution**: Implemented 24-hour retention policy, optimized dashboard time ranges
**Workaround**: Use short time ranges (<1 hour) in dashboards
**Reference**: Commits from 2025-11-23

---

## Future Considerations

### Planned Updates (v0.3.0+)

**Watchtower Integration**:
- Will automate version updates
- Requires version pinning (completed in v0.2.0)
- Will respect compatibility rules from this matrix
- Configuration: Monitor-only initially, then gradual automation

**Component Additions**:
- Docker Autoheal: Automatic container restart on failure
- Additional monitoring: Future expansions
- Infrastructure-wide: NetBird, Zitadel, PostgreSQL (v0.2.1+)

---

## References

- **Dependency Versions**: DEPENDENCIES.md
- **Update Procedures**: UPDATE_POLICY.md
- **Official Docs**:
  - Loki: https://grafana.com/docs/loki/
  - Grafana: https://grafana.com/docs/grafana/
  - Netdata: https://learn.netdata.cloud/
  - ntfy: https://docs.ntfy.sh/
  - Docker: https://docs.docker.com/

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-24 | Claude Code | Initial release (v0.2.0) |

**Next Review**: 2025-12-24 (1 month) or after major version upgrade
**Review Trigger**: New major version adoption, compatibility issues discovered
```

#### Testing Requirements
- Verify Loki + Promtail compatibility requirement is accurate
- Check Grafana documentation for Loki compatibility claims
- Validate Python + requests version requirements
- Ensure all references link correctly

#### Definition of Done
- [ ] Complete document created with all sections
- [ ] Current baseline documented as tested configuration
- [ ] Loki + Promtail compatibility clearly stated
- [ ] Grafana + Loki compatibility documented
- [ ] Breaking changes for major versions documented
- [ ] Upgrade strategies provided
- [ ] Testing checklist included
- [ ] File created at correct path
- [ ] Markdown formatting correct
- [ ] All upstream documentation links working
- [ ] Committed to git with message: "Add COMPATIBILITY_MATRIX.md - version compatibility documentation"

---

### [BLOCKER-4] Create version check script

**Priority**: High (Release Blocker)
**Estimated Effort**: Large (3-4 hours)
**Dependencies**: BLOCKER-1 (DEPENDENCIES.md provides baseline)
**Risk Level**: Medium

#### Context
scripts/check-versions.sh automates version checking. Essential for ongoing maintenance and prerequisite for Watchtower (v0.3.0).

**From PLANNING.md**: ~200-300 lines bash, includes documentation header

#### Acceptance Criteria
- [ ] Script checks current running versions via docker inspect
- [ ] Script compares against docker-compose.yml definitions
- [ ] Script generates human-readable report
- [ ] Script exits with appropriate codes (0=up to date, 1=updates available, 2=error)
- [ ] Script has comprehensive documentation in header
- [ ] Script handles errors gracefully (missing containers, Docker not running)
- [ ] Optional: Script can query Docker Hub for available updates (flag-based)

#### Implementation Notes

**File Location**: `/Users/rayiskander/myOCI/scripts/check-versions.sh`

**Script Design**:

```bash
#!/usr/bin/env bash
#
# check-versions.sh - Infrastructure Version Checker
#
# Purpose:
#   Checks current running Docker container versions against expected versions
#   in docker-compose.yml. Generates report showing current vs expected versions
#   and flags any mismatches.
#
# Usage:
#   ./check-versions.sh [OPTIONS]
#
# Options:
#   -h, --help           Show this help message
#   -v, --verbose        Verbose output (show all checks)
#   -q, --quiet          Quiet mode (only show issues)
#   --check-updates      Query Docker Hub for available updates (requires internet)
#   --json               Output in JSON format (for machine parsing)
#   --compose-file PATH  Path to docker-compose.yml (default: ../monitoring/docker-compose.yml)
#
# Exit Codes:
#   0 - All versions match expected, up to date
#   1 - Version mismatches found or updates available
#   2 - Error (Docker not available, files not found, etc.)
#
# Examples:
#   ./check-versions.sh                    # Basic check
#   ./check-versions.sh --check-updates    # Check for available updates
#   ./check-versions.sh --json             # Machine-readable output
#
# Requirements:
#   - Docker (docker command available)
#   - jq (for JSON parsing)
#   - Access to docker socket (for docker inspect)
#   - curl (optional, for --check-updates)
#
# Author: Claude Code
# Version: 1.0
# Last Updated: 2025-11-24 (v0.2.0)
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Color codes for output (disable if not a TTY)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# Default configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/monitoring/docker-compose.yml"
VERBOSE=false
QUIET=false
CHECK_UPDATES=false
JSON_OUTPUT=false

# Container name prefix (for filtering)
CONTAINER_PREFIX="oci-"

# Exit codes
EXIT_OK=0
EXIT_MISMATCH=1
EXIT_ERROR=2

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                grep '^#' "$0" | sed 's/^# \?//'
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                QUIET=true
                shift
                ;;
            --check-updates)
                CHECK_UPDATES=true
                shift
                ;;
            --json)
                JSON_OUTPUT=true
                shift
                ;;
            --compose-file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1" >&2
                echo "Use --help for usage information" >&2
                exit $EXIT_ERROR
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    local missing_deps=()

    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi

    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo -e "${RED}ERROR: Missing required dependencies: ${missing_deps[*]}${NC}" >&2
        echo "Please install missing dependencies and try again." >&2
        exit $EXIT_ERROR
    fi

    # Check Docker is running
    if ! docker ps &> /dev/null; then
        echo -e "${RED}ERROR: Docker is not running or not accessible${NC}" >&2
        exit $EXIT_ERROR
    fi

    # Check compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        echo -e "${RED}ERROR: Compose file not found: $COMPOSE_FILE${NC}" >&2
        exit $EXIT_ERROR
    fi
}

# Get running container version
get_running_version() {
    local container_name=$1

    # Check if container exists and is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        echo "NOT_RUNNING"
        return
    fi

    # Get image with tag
    docker inspect "$container_name" --format '{{.Config.Image}}' 2>/dev/null || echo "ERROR"
}

# Get expected version from docker-compose.yml
get_expected_version() {
    local service_name=$1

    # Extract image from docker-compose.yml using yq or manual parsing
    # Note: This assumes docker-compose v2 format
    docker-compose -f "$COMPOSE_FILE" config | \
        grep -A 5 "^  ${service_name}:" | \
        grep "image:" | \
        awk '{print $2}' | \
        tr -d "'" | \
        head -1
}

# Compare versions
compare_versions() {
    local service=$1
    local container=$2
    local running=$3
    local expected=$4

    if [[ "$running" == "NOT_RUNNING" ]]; then
        echo -e "${YELLOW}⚠${NC}  ${service}: Container not running (expected: ${expected})"
        return 1
    elif [[ "$running" == "ERROR" ]]; then
        echo -e "${RED}✗${NC}  ${service}: Error getting version"
        return 1
    elif [[ "$running" != "$expected" ]]; then
        echo -e "${YELLOW}⚠${NC}  ${service}: Version mismatch"
        echo "     Running:  $running"
        echo "     Expected: $expected"
        return 1
    else
        if [[ "$VERBOSE" == true ]] || [[ "$QUIET" == false ]]; then
            echo -e "${GREEN}✓${NC}  ${service}: $running"
        fi
        return 0
    fi
}

# Main check function
check_versions() {
    echo "Infrastructure Version Report - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================================="
    echo ""
    echo "MONITORING STACK:"
    echo ""

    local mismatch_count=0

    # Define services to check (service_name:container_name)
    local services=(
        "netdata:oci-netdata"
        "loki:oci-loki"
        "promtail:oci-promtail"
        "grafana:oci-grafana"
        "ntfy:oci-ntfy"
        "telegram-forwarder:oci-telegram-forwarder"
    )

    for service_def in "${services[@]}"; do
        local service_name="${service_def%%:*}"
        local container_name="${service_def##*:}"

        local running_version=$(get_running_version "$container_name")
        local expected_version=$(get_expected_version "$service_name")

        if ! compare_versions "$service_name" "$container_name" "$running_version" "$expected_version"; then
            ((mismatch_count++))
        fi
    done

    echo ""
    echo "SUMMARY:"
    if [[ $mismatch_count -eq 0 ]]; then
        echo -e "${GREEN}✓ All versions match expected configuration${NC}"
        echo ""
        return $EXIT_OK
    else
        echo -e "${YELLOW}⚠ Found $mismatch_count version mismatch(es)${NC}"
        echo ""
        echo "RECOMMENDATIONS:"
        echo "- Review mismatches and determine if updates needed"
        echo "- Consult DEPENDENCIES.md for current versions"
        echo "- Follow UPDATE_POLICY.md for update procedures"
        echo ""
        return $EXIT_MISMATCH
    fi
}

# Main execution
main() {
    parse_args "$@"
    check_prerequisites
    check_versions
    exit $?
}

main "$@"
```

**Features to implement**:
- Basic version checking (running vs expected)
- Human-readable output with colors
- Error handling for missing containers
- Exit codes for automation
- Verbose and quiet modes
- Help documentation in header

**Optional features (can add later)**:
- JSON output mode (for machine parsing)
- Check Docker Hub for available updates
- Integration with DEPENDENCIES.md parsing

#### Testing Requirements
- Test with all containers running
- Test with some containers stopped
- Test with Docker not running
- Test with missing docker-compose.yml
- Test verbose and quiet modes
- Verify exit codes correct
- Test on actual production system

#### Definition of Done
- [ ] Script created at scripts/check-versions.sh
- [ ] Execute permission set: `chmod +x scripts/check-versions.sh`
- [ ] Comprehensive header documentation
- [ ] Basic version checking implemented
- [ ] Human-readable output with colors
- [ ] Error handling implemented
- [ ] Exit codes working correctly
- [ ] --help flag works
- [ ] --verbose flag works
- [ ] Tested locally
- [ ] Tested on production server (if accessible)
- [ ] Committed to git with message: "Add scripts/check-versions.sh - automated version checking"

---

### [BLOCKER-5] Pin Docker image versions

**Priority**: High (Release Blocker)
**Estimated Effort**: Small (1 hour)
**Dependencies**: PRE-1 (need current versions), BLOCKER-1 (document in DEPENDENCIES.md)
**Risk Level**: Low

#### Context
Currently Netdata and ntfy use `:latest` tags. Must pin to specific versions for predictability and dependency management.

**From TODO.md (v0.1.0)**: Task FEATURE-1, previously Low priority, now elevated to blocker for v0.2.0.

#### Acceptance Criteria
- [ ] Netdata version pinned in docker-compose.yml
- [ ] ntfy version pinned in docker-compose.yml
- [ ] Versions match what's currently running in production (from PRE-1)
- [ ] docker-compose config validates successfully
- [ ] Changes documented in DEPENDENCIES.md
- [ ] Update entry added to DEPENDENCIES.md update history
- [ ] CHANGELOG.md updated with version pinning

#### Implementation Notes

**Files to Modify**:
1. `monitoring/docker-compose.yml` - Update image tags
2. `DEPENDENCIES.md` - Update versions table
3. `CHANGELOG.md` - Add entry for v0.2.0

**Steps**:

1. **Get versions from PRE-1 notes**
   - Netdata version: [recorded in PRE-1]
   - ntfy version: [recorded in PRE-1]

2. **Update docker-compose.yml**:
   ```yaml
   # Before:
   services:
     netdata:
       image: netdata/netdata:latest

   # After:
   services:
     netdata:
       image: netdata/netdata:v1.45.0  # Use actual version from PRE-1

   # Before:
   services:
     ntfy:
       image: binwiederhier/ntfy:latest

   # After:
   services:
     ntfy:
       image: binwiederhier/ntfy:v2.8.0  # Use actual version from PRE-1
   ```

3. **Validate configuration**:
   ```bash
   cd ~/myOCI/monitoring
   docker-compose config  # Should succeed without errors
   ```

4. **Update DEPENDENCIES.md**:
   - Update Netdata version in Docker Images table
   - Update ntfy version in Docker Images table
   - Update "Last Updated" date
   - Add entry to Update History section

5. **Update CHANGELOG.md**:
   - Add to v0.2.0 "Changed" section
   - Document version pinning with rationale

#### Testing Requirements
- [ ] Validate docker-compose config succeeds
- [ ] Verify specified versions exist in Docker Hub
- [ ] Test locally: `docker pull netdata/netdata:vX.Y.Z`
- [ ] Test locally: `docker pull binwiederhier/ntfy:vX.Y.Z`

#### Definition of Done
- [ ] docker-compose.yml updated with specific versions
- [ ] Configuration validated successfully
- [ ] DEPENDENCIES.md updated
- [ ] CHANGELOG.md updated
- [ ] All files committed to git
- [ ] Commit message: "Pin Netdata and ntfy versions for v0.2.0"
- [ ] Ready for deployment (will happen in DEPLOY-1)

---

## Medium Priority Tasks (Should Have)

### [DOCS-1] Update monitoring/README.md with dependency management

**Priority**: Medium
**Estimated Effort**: Small (30 minutes)
**Dependencies**: BLOCKER-1, BLOCKER-2, BLOCKER-4 (need files to link to)
**Risk Level**: Low

#### Context
monitoring/README.md needs section on dependency management to help users understand new tools and documentation.

#### Acceptance Criteria
- [ ] New "Dependency Management" section added
- [ ] Links to DEPENDENCIES.md, UPDATE_POLICY.md, COMPATIBILITY_MATRIX.md
- [ ] Brief explanation of version check script usage
- [ ] Cross-references to related documentation
- [ ] Section placed logically in document structure

#### Implementation Notes

**Add section after "Maintenance" or "Troubleshooting" section**:

```markdown
## Dependency Management

### Version Tracking

All infrastructure component versions are tracked in `DEPENDENCIES.md` at the project root. This document serves as the source of truth for:

- Current versions of all Docker images
- Python package versions
- System requirements
- Known vulnerabilities
- Update history

**View current versions**: See [DEPENDENCIES.md](../DEPENDENCIES.md)

### Update Procedures

Follow formalized update procedures documented in `UPDATE_POLICY.md`:

- Update frequency guidelines (security vs feature)
- Risk classification system
- Pre-update testing checklists
- Rollback procedures
- Maintenance window scheduling

**Update procedures**: See [UPDATE_POLICY.md](../UPDATE_POLICY.md)

### Version Compatibility

Version compatibility is documented in `COMPATIBILITY_MATRIX.md`:

- Tested configurations
- Known incompatibilities
- Upgrade paths for major versions
- Breaking changes between versions

**Compatibility info**: See [COMPATIBILITY_MATRIX.md](../COMPATIBILITY_MATRIX.md)

### Automated Version Checking

Check current versions against expected versions:

```bash
cd ~/myOCI
bash scripts/check-versions.sh
```

**Output**: Report showing current vs expected versions, flagging any mismatches.

**Options**:
- `--help`: Show usage information
- `--verbose`: Show all checks
- `--quiet`: Only show issues

### Related Documentation

- **Version Tracking**: [DEPENDENCIES.md](../DEPENDENCIES.md)
- **Update Procedures**: [UPDATE_POLICY.md](../UPDATE_POLICY.md)
- **Compatibility**: [COMPATIBILITY_MATRIX.md](../COMPATIBILITY_MATRIX.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Backup**: [BACKUP.md](BACKUP.md)
- **Maintenance**: [MAINTENANCE.md](MAINTENANCE.md)
```

#### Testing Requirements
- Verify all links work
- Check markdown renders correctly
- Ensure commands are accurate

#### Definition of Done
- [ ] Section added to monitoring/README.md
- [ ] All links verified working
- [ ] Markdown formatting correct
- [ ] Committed to git with message: "Update monitoring/README.md with dependency management section"

---

### [DOCS-2] Update CHANGELOG.md for v0.2.0

**Priority**: Medium
**Estimated Effort**: Small (30 minutes)
**Dependencies**: BLOCKER-1 through BLOCKER-5 (need to know what's included)
**Risk Level**: Low

#### Context
CHANGELOG.md needs v0.2.0 entry documenting all changes in this release.

**Template provided in PLANNING.md** - Use that as starting point.

#### Acceptance Criteria
- [ ] v0.2.0 section added to CHANGELOG.md
- [ ] All new features documented
- [ ] Version pinning changes documented
- [ ] Security enhancements documented
- [ ] Follows Keep a Changelog format
- [ ] Date filled in (or TBD for pre-release)

#### Implementation Notes

**Add to CHANGELOG.md before v0.1.0 section**:

Use template from PLANNING.md section "Documentation & Communication > Changelog Entries"

**Key items to include**:
- DEPENDENCIES.md creation
- UPDATE_POLICY.md creation
- COMPATIBILITY_MATRIX.md creation
- scripts/check-versions.sh creation
- Netdata version pinning
- ntfy version pinning
- Security vulnerability tracking process

**Update release date once deployed**

#### Testing Requirements
- Verify follows Keep a Changelog format
- Check all items accurate
- Ensure no typos

#### Definition of Done
- [ ] v0.2.0 section added to CHANGELOG.md
- [ ] All features documented
- [ ] Follows proper format
- [ ] Committed to git with message: "Update CHANGELOG.md for v0.2.0"

---

### [DOCS-3] Update monitoring/SECURITY.md cross-reference

**Priority**: Medium
**Estimated Effort**: Small (15 minutes)
**Dependencies**: BLOCKER-2 (UPDATE_POLICY.md with vulnerability tracking)
**Risk Level**: Low

#### Context
monitoring/SECURITY.md should reference new vulnerability tracking process in UPDATE_POLICY.md.

#### Acceptance Criteria
- [ ] Cross-reference added to Security section
- [ ] Link to UPDATE_POLICY.md added
- [ ] Brief mention of vulnerability tracking process
- [ ] Integrated naturally into existing content

#### Implementation Notes

**Add to monitoring/SECURITY.md** in appropriate section (likely near security hardening or vulnerability sections):

```markdown
## Security Vulnerability Tracking

Infrastructure component vulnerabilities are tracked and managed according to procedures defined in UPDATE_POLICY.md.

**Process**:
- Regular monitoring of security advisories
- Vulnerability assessment and severity classification
- Response SLAs based on criticality
- Patching procedures with testing

**See**: [UPDATE_POLICY.md](../UPDATE_POLICY.md#security-vulnerability-tracking) for complete vulnerability tracking procedures.

**Current Status**: See [DEPENDENCIES.md](../DEPENDENCIES.md#known-vulnerabilities) for known vulnerabilities affecting deployed versions.
```

#### Testing Requirements
- Verify links work
- Ensure fits naturally in document flow

#### Definition of Done
- [ ] Cross-reference added to SECURITY.md
- [ ] Links verified
- [ ] Committed to git with message: "Add vulnerability tracking cross-reference to SECURITY.md"

---

### [DOCS-4] Update monitoring/MAINTENANCE.md with version checking

**Priority**: Medium
**Estimated Effort**: Small (15 minutes)
**Dependencies**: BLOCKER-4 (check-versions.sh)
**Risk Level**: Low

#### Context
monitoring/MAINTENANCE.md should include version checking in maintenance procedures.

#### Acceptance Criteria
- [ ] Version checking added to maintenance procedures
- [ ] Reference to check-versions.sh script
- [ ] Added to monthly maintenance checklist
- [ ] Link to UPDATE_POLICY.md for update procedures

#### Implementation Notes

**Add to monitoring/MAINTENANCE.md** maintenance checklist:

```markdown
### Monthly Maintenance Checklist

...existing items...

#### Version Management
- [ ] **Check for available updates**
  ```bash
  cd ~/myOCI
  bash scripts/check-versions.sh
  ```
- [ ] **Review update recommendations**: If updates available, consult UPDATE_POLICY.md
- [ ] **Schedule updates**: Plan updates for next maintenance window if needed
- [ ] **Update DEPENDENCIES.md**: If versions changed, update documentation

**Reference**: See [UPDATE_POLICY.md](../UPDATE_POLICY.md) for update procedures.
```

#### Testing Requirements
- Verify script path correct
- Ensure commands accurate

#### Definition of Done
- [ ] Section added to MAINTENANCE.md
- [ ] Commands tested and verified
- [ ] Committed to git with message: "Add version checking to maintenance procedures"

---

### [DOCS-5] Update .gitignore for backup files

**Priority**: Medium
**Estimated Effort**: Small (10 minutes)
**Dependencies**: None
**Risk Level**: Low

#### Context
Ensure backup files created during updates are not committed to git.

#### Acceptance Criteria
- [ ] *.backup.yml added to .gitignore
- [ ] *.backup.txt added to .gitignore
- [ ] scripts/*.log added (if scripts generate logs)
- [ ] Verified existing entries still appropriate

#### Implementation Notes

**Add to .gitignore**:

```
# Backup files (from update procedures)
*.backup.yml
*.backup.txt
*.backup

# Script output
scripts/*.log
scripts/version-check-*.json
scripts/version-check-*.txt

# Version check temporary files
.version-check-cache
```

**Check existing .gitignore**:
- Ensure .env still ignored
- Ensure *.key still ignored (SSH keys)
- Ensure Docker volumes not tracked

#### Testing Requirements
- Verify .gitignore syntax correct
- Test that backup files are ignored: create dummy file, check git status

#### Definition of Done
- [ ] .gitignore updated
- [ ] Tested with dummy backup file
- [ ] Committed to git with message: "Update .gitignore for backup files and script output"

---

### [OPTIONAL-1] Create update testing script

**Priority**: Low (Optional for v0.2.0)
**Estimated Effort**: Large (3-4 hours)
**Dependencies**: BLOCKER-2 (UPDATE_POLICY.md defines process)
**Risk Level**: Medium

#### Context
scripts/test-update.sh automates update testing. Nice to have but manual testing acceptable for v0.2.0. Can defer to v0.2.1.

**From PLANNING.md**: IMPORTANT-2, optional for v0.2.0 release.

#### Acceptance Criteria
- [ ] Script accepts component name and version as parameters
- [ ] Script creates backup of current state
- [ ] Script updates specified component
- [ ] Script runs health checks
- [ ] Script generates pass/fail report
- [ ] Script can rollback on failure

#### Implementation Notes

**File Location**: `/Users/rayiskander/myOCI/scripts/test-update.sh`

**Basic structure**:
```bash
#!/usr/bin/env bash
# test-update.sh - Automated update testing
# Usage: ./test-update.sh <service-name> <new-version>

set -euo pipefail

SERVICE=$1
NEW_VERSION=$2

# 1. Backup current state
# 2. Update docker-compose.yml
# 3. Pull new image
# 4. Deploy update
# 5. Run health checks
# 6. Report results
# 7. Rollback if issues
```

**Can defer to v0.2.1** if time constrained.

#### Definition of Done
- [ ] Script created (or explicitly deferred to v0.2.1)
- [ ] If created: All acceptance criteria met
- [ ] If deferred: Noted in PLANNING.md and v0.2.1 planning

---

## Deployment Tasks

### [DEPLOY-1] Deploy v0.2.0 to production

**Priority**: High (Final step)
**Estimated Effort**: Medium (1-2 hours including verification)
**Dependencies**: All BLOCKER tasks complete, PRE-3 (prerequisites verified)
**Risk Level**: Low-Medium

#### Context
Deploy v0.2.0 to production server. Follows deployment strategy from PLANNING.md.

**Timing**: After 1-week v0.1.0 validation period (around Dec 1-8, 2025)

#### Acceptance Criteria
- [ ] All documentation files deployed to server
- [ ] Scripts deployed with execute permissions
- [ ] docker-compose.yml updated with pinned versions
- [ ] All services restarted successfully (if needed)
- [ ] Version check script runs successfully
- [ ] All health checks passing
- [ ] Git tag v0.2.0 created
- [ ] Tag pushed to remote

#### Implementation Notes

**Follow deployment procedure from PLANNING.md "Deployment Steps"**

**Phase 1: Documentation Deployment** (zero downtime):
```bash
# On production server
cd ~/myOCI
git fetch origin
git checkout v0.2.0  # or main if not tagged yet
ls -l DEPENDENCIES.md UPDATE_POLICY.md COMPATIBILITY_MATRIX.md
ls -l scripts/check-versions.sh

# Install jq if needed
which jq || sudo apt-get install -y jq

# Test version check script
bash scripts/check-versions.sh
```

**Phase 2: Version Pinning Deployment** (potential brief restart):
```bash
cd ~/myOCI/monitoring

# Backup current state
docker-compose config > docker-compose.backup.yml
docker ps > containers.backup.txt

# Pull updated code (includes docker-compose.yml changes)
cd ~/myOCI
git pull origin main  # or v0.2.0

# Verify changes
cd monitoring
diff docker-compose.backup.yml docker-compose.yml

# Apply changes
docker-compose up -d
# Note: May cause brief container recreation if versions differ

# Monitor startup
docker-compose ps
docker-compose logs -f --tail=50

# Verify services
curl -I http://localhost:19999  # Netdata
curl http://localhost:8765/v1/health  # ntfy
curl -I http://localhost:3000  # Grafana

# Test Telegram
curl -d "v0.2.0 deployment verification" http://localhost:8765/oci-info
```

**Phase 3: Verification**:
```bash
# Run version check
cd ~/myOCI
bash scripts/check-versions.sh

# Verify all containers healthy
docker ps | grep oci-

# Check dashboard access
# Visit: https://monitor.qubix.space
# Visit: https://grafana.qubix.space

# Verify logging still working
# Check Grafana Explore for recent logs
```

**Phase 4: Git Tagging**:
```bash
cd ~/myOCI

# Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0: Dependency Management System

Comprehensive dependency management infrastructure for predictable, safe updates.

## Features Added
- DEPENDENCIES.md: Centralized version tracking
- UPDATE_POLICY.md: Formalized update procedures
- COMPATIBILITY_MATRIX.md: Version compatibility documentation
- scripts/check-versions.sh: Automated version checking

## Changes
- Pinned Netdata version (latest → vX.Y.Z)
- Pinned ntfy version (latest → vX.Y.Z)

## Infrastructure
- Foundation for Phase 3 auto-healing (Watchtower in v0.3.0)
- Security vulnerability tracking process established
- Update testing procedures documented

See CHANGELOG.md for complete details.
See PLANNING.md for release strategy."

# Push tag
git push origin main --tags
```

#### Testing Requirements
- Follow all verification steps from PLANNING.md "Post-Deployment Verification"
- Monitor for first 24 hours
- Check logs for any errors
- Verify dashboards loading
- Verify Telegram notifications working

#### Definition of Done
- [ ] Phase 1 (docs) deployed successfully
- [ ] Phase 2 (version pinning) deployed successfully
- [ ] All immediate verification checks passed
- [ ] Version check script working
- [ ] Git tag v0.2.0 created
- [ ] Tag pushed to remote
- [ ] No errors in logs
- [ ] All services healthy
- [ ] 24-hour monitoring scheduled

---

### [DEPLOY-2] Post-deployment verification

**Priority**: High
**Estimated Effort**: Small (30-60 minutes over 24 hours)
**Dependencies**: DEPLOY-1 (deployment complete)
**Risk Level**: Low

#### Context
Extended validation after deployment to ensure stability.

**From PLANNING.md**: 24-hour validation and 1-week validation checklists.

#### Acceptance Criteria
- [ ] All immediate checks passed (within 5 minutes)
- [ ] Extended validation completed (within 1 hour)
- [ ] 24-hour validation completed
- [ ] Documentation review completed (within 1 week)
- [ ] Any issues documented and addressed

#### Implementation Notes

**Execute checklists from PLANNING.md "Post-Deployment Verification"**

**Immediate Checks (within 5 minutes):**
- [ ] All monitoring containers running
- [ ] Netdata dashboard accessible
- [ ] Grafana dashboard accessible
- [ ] ntfy health check passing
- [ ] Telegram notifications working
- [ ] Loki receiving logs

**Extended Validation (within 1 hour):**
- [ ] Run version check script
- [ ] Verify script output matches DEPENDENCIES.md
- [ ] Check for error logs
- [ ] Verify dashboards loading data
- [ ] Verify log retention still working

**24-Hour Validation:**
- [ ] No unexpected container restarts
- [ ] No memory leaks or resource issues
- [ ] Maintenance script still works (if scheduled)
- [ ] All alerting channels functional

**Documentation Review (within 1 week):**
- [ ] Review DEPENDENCIES.md accuracy
- [ ] Update any gaps or errors discovered
- [ ] Add lessons learned to UPDATE_POLICY.md
- [ ] Update COMPATIBILITY_MATRIX.md if issues found

#### Testing Requirements
- Execute all checklists
- Document any anomalies
- Compare against v0.1.0 baseline

#### Definition of Done
- [ ] All immediate checks passed
- [ ] Extended validation passed
- [ ] 24-hour validation passed
- [ ] Documentation reviewed and updated if needed
- [ ] Verification documented in notes
- [ ] v0.2.0 declared stable (or issues identified and addressed)

---

## Low Priority Tasks (Nice to Have - Can Defer)

### [OPTIONAL-2] Document infrastructure-wide dependencies

**Priority**: Low (Deferred to v0.2.1)
**Estimated Effort**: Medium (2-3 hours)
**Dependencies**: BLOCKER-1 (DEPENDENCIES.md structure established)
**Risk Level**: Low

#### Context
Extend DEPENDENCIES.md to include broader infrastructure (NetBird, Zitadel, PostgreSQL, etc.)

**From PLANNING.md**: IMPORTANT-3, can release without, add in v0.2.1.

**Decision from PRE-2**: If scope limited to monitoring + critical deps, this task deferred.

#### Acceptance Criteria
- [ ] NetBird component versions identified and documented
- [ ] Caddy version and modules documented
- [ ] Zitadel version documented
- [ ] PostgreSQL version documented
- [ ] Added to DEPENDENCIES.md or separate INFRASTRUCTURE_DEPENDENCIES.md

#### Implementation Notes
**Defer to v0.2.1** unless scope decision (PRE-2) includes full infrastructure.

If implementing:
- SSH to server and identify versions
- Add new section to DEPENDENCIES.md
- Document inter-dependencies
- Update COMPATIBILITY_MATRIX.md if relevant

#### Definition of Done
- [ ] Explicitly deferred to v0.2.1 (update PLANNING.md)
- OR [ ] Implemented and documented (if scope changed)

---

### [OPTIONAL-3] Integrate GitHub Dependabot

**Priority**: Low (Deferred to v0.2.1+)
**Estimated Effort**: Small (1 hour)
**Dependencies**: None
**Risk Level**: Low

#### Context
GitHub Dependabot can create automated PRs for dependency updates.

**From PLANNING.md**: OPTIONAL-1, defer to v0.2.1 or later.

#### Acceptance Criteria
- [ ] .github/dependabot.yml created
- [ ] Configured for Docker images
- [ ] Configured for Python requirements.txt
- [ ] Tested (PR created successfully)

#### Implementation Notes
**Explicitly defer to v0.2.1 or later**.

Core dependency management must be proven stable before enabling automation.

#### Definition of Done
- [ ] Explicitly deferred (note in PLANNING.md for v0.2.1)

---

### [OPTIONAL-4] Create version dashboard webpage

**Priority**: Low (Deferred to v0.3.0)
**Estimated Effort**: Medium (3-4 hours)
**Dependencies**: BLOCKER-4 (version check script)
**Risk Level**: Low

#### Context
Visual dashboard showing version status at a glance.

**From PLANNING.md**: OPTIONAL-2, defer to v0.3.0 (visualization enhancements).

#### Implementation Notes
**Explicitly defer to v0.3.0**.

Focus v0.2.0 on core dependency management, visualization later.

#### Definition of Done
- [ ] Explicitly deferred (note for v0.3.0 planning)

---

### [OPTIONAL-5] Automated update notifications via Telegram

**Priority**: Low (Deferred to v0.2.1)
**Estimated Effort**: Small (2 hours)
**Dependencies**: BLOCKER-4 (version check script), existing Telegram integration
**Risk Level**: Low

#### Context
Weekly cron job to check versions and notify via Telegram if updates available.

**From PLANNING.md**: OPTIONAL-3, defer to v0.2.1 (after core proven).

#### Implementation Notes
**Defer to v0.2.1** after core dependency management proven stable.

Would require:
- Cron job setup
- Script modification to send Telegram notifications
- Configuration for update priorities

#### Definition of Done
- [ ] Explicitly deferred (note in PLANNING.md for v0.2.1)

---

## Task Statistics

**Total Tasks**: 24

**By Priority**:
- **Pre-Implementation**: 3 tasks (must complete before Dec 1)
- **High Priority (Blockers)**: 5 tasks (must complete for v0.2.0)
- **Medium Priority**: 6 tasks (should complete for v0.2.0)
- **Low Priority (Deferred)**: 5 tasks (explicitly deferred to future releases)
- **Deployment**: 2 tasks (final deployment and verification)
- **Optional**: 3 tasks (can skip or defer)

**By Estimated Effort**:
- **Small (15-45 min)**: 10 tasks
- **Medium (1-3 hours)**: 6 tasks
- **Large (3-4 hours)**: 8 tasks

**Total Estimated Effort**:
- **High Priority (Blockers)**: ~10-15 hours
- **Medium Priority**: ~3-4 hours
- **Pre-Implementation**: ~1 hour
- **Deployment**: ~2-3 hours
- **Total for v0.2.0**: ~16-23 hours

**Estimated Timeline** (working 3-4 hours/day):
- **Pre-Implementation (Nov 24-30)**: 1 day (complete before Dec 1)
- **High Priority (Dec 1-5)**: 4-5 days
- **Medium Priority (Dec 6-7)**: 1-2 days
- **Deployment (Dec 8)**: 1 day
- **Total**: 7-9 days

**Work Pattern**:
- **Week 1 Prep (Nov 24-30)**: Complete PRE tasks (3 tasks, 1 hour)
- **Week 2 Implementation (Dec 1-7)**: Complete BLOCKER and DOCS tasks (11 tasks, ~16-19 hours)
- **Week 3 Deployment (Dec 8)**: Deploy and verify (2 tasks, ~2-3 hours)

---

## Progress Tracking

**Update this section as work progresses:**

**Completed**: 0/24 (0%)
**In Progress**: 0/24
**Blocked**: 0/24

**Current Sprint**: Pre-Implementation (Nov 24-30)
**Next Sprint**: Implementation (Dec 1-7)

**Last Updated**: 2025-11-24

---

## Notes

### Open Questions Status
- **Q1** (PRE-1): Current production versions - NEEDS RESOLUTION
- **Q2** (BLOCKER-4): Script remote registry queries - DECIDE DURING IMPLEMENTATION (recommended: optional flag)
- **Q3** (BLOCKER-1): Single vs multiple docs - RECOMMEND SINGLE FILE
- **Q4** (Scripts location): RECOMMEND TOP-LEVEL scripts/
- **Q5** (Timeline): RECOMMEND 1 WEEK WAIT (Dec 1 start)
- **Q6** (Release candidate): RECOMMEND NO MANDATORY RC
- **Q7** (Update approval): DEFINE IN UPDATE_POLICY.md (recommended: security auto, features manual)
- **Q8** (PRE-2): Scope boundaries - NEEDS DECISION (recommended: monitoring + critical)

### Risks to Monitor
- **Version pinning**: Ensure versions from PRE-1 are currently deployed versions (mitigate by pinning exactly what's running)
- **Script Docker access**: May need testing on production server (mitigate with read-only access, already granted)
- **Documentation accuracy**: Cross-check all version numbers (mitigate with thorough review)
- **Deployment timing**: Ensure v0.1.0 stable for 1 week first (mitigate by waiting until Dec 1)

### Success Criteria
- [ ] All BLOCKER tasks completed
- [ ] All DOCS tasks completed
- [ ] Deployment successful with zero downtime (documentation phase)
- [ ] Brief downtime acceptable for version pinning (<5 minutes)
- [ ] Version check script working on production
- [ ] All documentation accurate and complete
- [ ] Git tag v0.2.0 created and pushed
- [ ] 24-hour stability validation passed

---

**TODO Document Version**: 1.0
**Created**: 2025-11-24
**For Release**: v0.2.0 (Dependency Management System)
**Strategic Plan**: .claude/PLANNING.md
**Target Start**: December 1, 2025
**Target Completion**: December 8, 2025
