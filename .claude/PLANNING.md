# Release Planning - 2025-11-25

## Release Overview
- **Proposed Version**: 0.1.1
- **Release Type**: Patch (Security Hardening)
- **Target Date**: Immediate (security fixes)
- **Risk Level**: Low (configuration changes only, no code changes)

## Context

This release addresses security vulnerabilities identified in a comprehensive security review. All items are configuration hardening - no application code changes required. The existing v0.1.0 infrastructure is functionally complete; this release focuses on securing it for production use.

**Supersedes**: Previous v0.2.0 planning (dependency management) - deferred until security hardening complete.

## Changes Since Last Release (v0.1.0)

### Commits Since v0.1.0
```
ef23a9c Deploy infrastructure health check with 12-hour Telegram heartbeat
b300007 Add Security section to monitoring README
b46918a Add comprehensive security hardening documentation
b888807 Add Backup & Recovery section to monitoring README
339b30f Add comprehensive backup and recovery documentation
ec45860 Add /review-progress command for comprehensive release progress analysis
64d0ca9 Fix Netdata restart loop by removing read-only flag on config volume
432493c Add /next-task command for systematic task execution
```

### Breaking Changes
- None

### New Features (Already Committed)
- Infrastructure health check with 12-hour Telegram heartbeat
- Comprehensive security documentation (SECURITY.md)
- Backup and recovery documentation (BACKUP.md)
- Developer workflow commands (/review-progress, /next-task)

### Bug Fixes (Already Committed)
- Fixed Netdata restart loop (read-only config volume issue)

### Documentation Added (Already Committed)
- SECURITY.md - Complete security hardening guide
- BACKUP.md - Backup and recovery procedures
- Security section in README

---

## Security Hardening Items (Ranked by Risk)

### CRITICAL (Must Fix Before Release)

#### 1. SSH Key Permissions (Local Development Machine)
| Attribute | Value |
|-----------|-------|
| **Current State** | `sshkey-netbird-private.key` has permissions 644 (world-readable) |
| **Risk** | Anyone with local machine access can read the key |
| **Impact** | Complete server compromise |
| **Fix** | `chmod 600 sshkey-netbird-private.key` |
| **Effort** | 1 minute |
| **Status** | [ ] Not started |

#### 2. SSH Key Not in .gitignore (Root Level)
| Attribute | Value |
|-----------|-------|
| **Current State** | No root-level `.gitignore` exists; key shows as untracked |
| **Risk** | Accidental commit would expose key permanently |
| **Impact** | Key leaked to any repository viewers |
| **Fix** | Create root `.gitignore` with `*.key` and `*.pem` patterns |
| **Effort** | 2 minutes |
| **Status** | [ ] Not started |

---

### HIGH (Should Fix in This Release)

#### 3. Grafana Default Credentials
| Attribute | Value |
|-----------|-------|
| **Current State** | `admin/admin` default password in docker-compose.yml:143 |
| **Risk** | Anyone discovering URL can log in |
| **Impact** | Full access to dashboards, data sources, alert modification |
| **Fix** | Set strong `GRAFANA_ADMIN_PASSWORD` in server's `.env` |
| **Effort** | 5 minutes |
| **Status** | [ ] Not started |

#### 4. Root Container with Docker Socket Access
| Attribute | Value |
|-----------|-------|
| **Current State** | `health-check` runs as `user: "0"` with Docker socket access |
| **Risk** | Container escape = full root access to host |
| **Impact** | Complete host compromise if container breached |
| **Mitigation Options** | A: Docker socket proxy, B: Accept with monitoring |
| **Effort** | 30 min (A) or N/A (B) |
| **Status** | [ ] Needs decision |
| **Recommendation** | Accept risk for v0.1.1; implement proxy in v0.2.0 |

#### 5. Netdata Elevated Capabilities
| Attribute | Value |
|-----------|-------|
| **Current State** | SYS_PTRACE, SYS_ADMIN capabilities + apparmor:unconfined |
| **Risk** | Near-root access if Netdata compromised |
| **Impact** | Process inspection, container escape potential |
| **Mitigation** | Required for Netdata functionality - keep updated + auth |
| **Effort** | N/A (inherent to Netdata) |
| **Status** | [x] Accepted risk (documented) |

---

### MEDIUM-HIGH (Important for Security)

#### 6. No Netdata Authentication
| Attribute | Value |
|-----------|-------|
| **Current State** | Netdata dashboard has no built-in auth |
| **Risk** | Anyone bypassing Caddy can access system metrics |
| **Impact** | Information disclosure (processes, network, system config) |
| **Fix** | Configure Caddy BasicAuth (documented in SECURITY.md) |
| **Effort** | 10 minutes |
| **Status** | [ ] Not started |

---

### MEDIUM (Should Address)

#### 7. Secrets in Plain Text .env
| Attribute | Value |
|-----------|-------|
| **Current State** | Telegram tokens in plain text file |
| **Risk** | File access = credential access |
| **Impact** | Bot hijacking, unauthorized message sending |
| **Fix** | Migrate to Docker secrets |
| **Effort** | 1 hour |
| **Status** | [ ] **Defer to v0.2.0** |

#### 8. No ntfy ACLs
| Attribute | Value |
|-----------|-------|
| **Current State** | Open topics without authentication |
| **Risk** | Anyone on network can publish/subscribe |
| **Impact** | Alert spoofing, information disclosure |
| **Fix** | Enable ntfy ACLs (documented in SECURITY.md) |
| **Effort** | 30 minutes |
| **Status** | [ ] **Defer to v0.2.0** |

#### 9. Loki Port Exposed on Host
| Attribute | Value |
|-----------|-------|
| **Current State** | Port 3100 bound to all interfaces (`"3100:3100"`) |
| **Risk** | Direct access if firewall misconfigured |
| **Impact** | Log injection, data exfiltration |
| **Fix** | Bind to localhost only: `"127.0.0.1:3100:3100"` |
| **Effort** | 5 minutes |
| **Status** | [ ] Not started |

#### 10. No Rate Limiting / Fail2ban
| Attribute | Value |
|-----------|-------|
| **Current State** | No brute force protection |
| **Risk** | Credential stuffing against Grafana |
| **Impact** | Account compromise through repeated attempts |
| **Fix** | Implement fail2ban |
| **Effort** | 1 hour |
| **Status** | [ ] **Defer to v0.2.0** |

---

## Release Requirements

### Must Have (Blockers for v0.1.1)
- [ ] Fix SSH key permissions (`chmod 600`)
- [ ] Create root `.gitignore` to protect sensitive files
- [ ] Change Grafana admin password on server
- [ ] Configure Caddy BasicAuth for Netdata
- [ ] Bind Loki to localhost only

### Should Have (Important but not blocking)
- [ ] Document accepted risks (Docker socket, Netdata capabilities)
- [ ] Update CHANGELOG.md with security fixes

### Deferred to v0.2.0
- [ ] Docker secrets migration
- [ ] ntfy ACLs
- [ ] Docker socket proxy
- [ ] Fail2ban integration
- [ ] Rate limiting
- [ ] Dependency management system (original v0.2.0 plan)

---

## Risk Analysis

### High Risk Items
| Item | Risk | Mitigation |
|------|------|------------|
| SSH key permissions | Complete server compromise | Fix immediately (`chmod 600`) |
| Grafana default password | Unauthorized dashboard access | Change password before release |
| Docker socket access | Container escape to root | Accept for v0.1.1; proxy in v0.2.0 |

### Medium Risk Items
| Item | Risk | Mitigation |
|------|------|------------|
| Loki port exposure | Log data access | Bind to localhost |
| No Netdata auth | Metrics disclosure | Caddy BasicAuth |
| Plain text secrets | Credential theft | Docker secrets in v0.2.0 |

### Accepted Risks (Documented)
1. **Netdata capabilities**: Required for monitoring functionality. Mitigated by keeping Netdata updated and behind authentication.
2. **Health-check root access**: Required for Docker API. Mitigated by read-only socket mount and isolated network.

---

## Deployment Strategy

### Pre-Deployment Checklist
- [ ] Backup current server configuration
- [ ] Generate strong Grafana password (use `openssl rand -base64 24`)
- [ ] Generate Caddy BasicAuth password hash
- [ ] Prepare updated docker-compose.yml locally

### Deployment Steps

#### Phase 1: Local Machine (Development)
```bash
# 1. Fix SSH key permissions
chmod 600 sshkey-netbird-private.key

# 2. Create root .gitignore
cat > .gitignore << 'EOF'
# Private keys - NEVER commit
*.key
*.pem
sshkey-*

# Environment files with secrets
.env
.env.*
!.env.example

# OS files
.DS_Store
Thumbs.db
EOF

# 3. Commit .gitignore
git add .gitignore
git commit -m "Add root .gitignore to protect sensitive files"
```

#### Phase 2: Server (via SSH)
```bash
# 1. SSH to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# 2. Backup current config
cd ~/monitoring
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup

# 3. Generate and set Grafana password
GRAFANA_PASS=$(openssl rand -base64 24)
echo "GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASS" >> .env
echo "Save this password: $GRAFANA_PASS"

# 4. Update docker-compose.yml - bind Loki to localhost
# Change: "3100:3100" to "127.0.0.1:3100:3100"
sed -i 's/"3100:3100"/"127.0.0.1:3100:3100"/' docker-compose.yml

# 5. Restart services
docker compose down
docker compose up -d

# 6. Verify services
docker compose ps
```

#### Phase 3: Caddy BasicAuth for Netdata
```bash
# 1. Generate bcrypt password hash
docker exec infrastructure_files-caddy-1 caddy hash-password
# Enter password when prompted, save the hash

# 2. Edit Caddyfile (location may vary)
# Add basicauth block to monitor.qubix.space section:
#   basicauth {
#       admin $2a$14$<your-bcrypt-hash>
#   }

# 3. Reload Caddy
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

### Post-Deployment Verification
- [ ] Verify SSH key has 600 permissions locally
- [ ] Verify `.gitignore` committed and working
- [ ] Verify Grafana login with new password at https://grafana.qubix.space
- [ ] Verify Netdata requires BasicAuth at https://monitor.qubix.space
- [ ] Verify Loki not accessible externally (`curl http://<server-ip>:3100` should fail)
- [ ] Verify Telegram alerts still working (send test notification)
- [ ] Verify health check heartbeat received

### Rollback Plan
```bash
# If issues occur on server:
cd ~/monitoring
docker compose down
cp docker-compose.yml.backup docker-compose.yml
cp .env.backup .env
docker compose up -d

# Verify services restored
docker compose ps
```

---

## Documentation & Communication

### Changelog Entries for v0.1.1
```markdown
## [0.1.1] - 2025-11-25

### Security
- Fixed SSH private key file permissions on development machine (644 → 600)
- Added root `.gitignore` to prevent accidental commit of keys and secrets
- Changed Grafana default admin password to strong random password
- Added Caddy BasicAuth protection for Netdata dashboard
- Bound Loki API port to localhost only (prevents external access)
- Documented accepted security risks (Netdata capabilities, health-check Docker access)

### Added
- Infrastructure health check with 12-hour Telegram heartbeat
- Comprehensive security documentation (SECURITY.md)
- Backup and recovery documentation (BACKUP.md)
- Developer workflow commands (/review-progress, /next-task, /upgrade-netbird)

### Fixed
- Netdata restart loop caused by read-only config volume

### Known Limitations
- ntfy topics remain open (ACLs planned for v0.2.0)
- Secrets stored in plain text .env (Docker secrets planned for v0.2.0)
- No fail2ban/rate limiting (planned for v0.2.0)
```

### Documentation Updates Needed
- [x] SECURITY.md - Already comprehensive
- [x] BACKUP.md - Already exists
- [ ] Update CHANGELOG.md with v0.1.1 changes
- [ ] Optionally update monitoring/README.md security section

---

## Open Questions

1. **Docker socket proxy timing**: Implement in v0.1.1 or v0.2.0?
   - **Recommendation**: Defer to v0.2.0 - current read-only mount is acceptable

2. **Caddy configuration location**: Where is the Caddyfile on the server?
   - **Likely**: `/home/ubuntu/netbird/infrastructure_files/Caddyfile`
   - **Action**: Verify during deployment

3. **Grafana password storage**: Store in password manager after generation?
   - **Recommendation**: Yes, immediately store generated password securely

---

## Next Steps

### Immediate (Today)
1. Fix SSH key permissions locally: `chmod 600 sshkey-netbird-private.key`
2. Create and commit root `.gitignore`
3. SSH to server and change Grafana password
4. Configure Caddy BasicAuth for Netdata
5. Bind Loki to localhost

### After Deployment
1. Update CHANGELOG.md with v0.1.1 entries
2. Create git tag `v0.1.1`
3. Verify all services working for 24 hours
4. Resume v0.2.0 planning (dependency management)

---

## Version Justification

**v0.1.1 (Patch)** is appropriate because:
- No breaking changes
- No new user-facing features (only security hardening)
- Configuration-only changes
- All fixes are backwards compatible
- Existing dashboards/integrations unaffected

This follows semantic versioning: PATCH version for backwards-compatible bug fixes and security patches.

---

## Project Readiness Assessment

### Ready for Implementation: YES

**No blockers identified.** All changes are:
- Configuration-only (no code changes)
- Low risk (easily reversible)
- Well-documented (procedures in SECURITY.md)
- Quick to implement (~30 minutes total)

**Key Risks:**
1. SSH key permissions - CRITICAL but 1-minute fix
2. Grafana password - HIGH but 5-minute fix
3. Docker socket access - HIGH but accepted for v0.1.1

**Recommendation**: Proceed immediately with security hardening.

---

**Planning Document Version:** 1.0
**Created:** November 25, 2025
**Author:** Claude Code
**Status:** Ready for implementation
