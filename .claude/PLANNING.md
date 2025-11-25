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
| **Current State** | ~~`sshkey-netbird-private.key` has permissions 644~~ → Fixed + unused key deleted |
| **Risk** | ~~Anyone with local machine access can read the key~~ → Resolved |
| **Impact** | ~~Complete server compromise~~ → Mitigated |
| **Fix** | `chmod 600` applied, unused key in myOCI/ deleted |
| **Effort** | 1 minute |
| **Status** | [x] **COMPLETED** (2025-11-25) |

#### 2. SSH Key Not in .gitignore (Root Level)
| Attribute | Value |
|-----------|-------|
| **Current State** | ~~No root-level `.gitignore` exists~~ → Created |
| **Risk** | ~~Accidental commit would expose key permanently~~ → Protected |
| **Impact** | ~~Key leaked to any repository viewers~~ → Mitigated |
| **Fix** | Created `.gitignore` with `*.key`, `*.pem`, `.env` patterns |
| **Effort** | 2 minutes |
| **Status** | [x] **COMPLETED** (2025-11-25, commit 547c41b) |

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
- [x] Fix SSH key permissions (`chmod 600`) - **DONE**
- [x] Create root `.gitignore` to protect sensitive files - **DONE** (commit 547c41b)
- [x] Delete unused SSH key from myOCI/ directory - **DONE**
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

---

# v0.2.0 Planning - Advanced Security & DDoS Protection

## Release Overview
- **Proposed Version**: 0.2.0
- **Release Type**: Minor (Security Features + Infrastructure Hardening)
- **Target Date**: After v0.1.1 stabilization (1 week)
- **Risk Level**: Medium (infrastructure changes, external service integration)

## Scope

v0.2.0 focuses on:
1. **SSH Login Security** - Telegram notifications + 2FA (NEW)
2. **DDoS Protection** - Cloudflare + Fail2ban
3. **Deferred v0.1.1 items** - Docker secrets, ntfy ACLs, fail2ban
4. **Dependency management** - Originally planned for v0.2.0

---

## SSH Login Security (NEW)

### Overview

Implement multi-layer SSH authentication security:
1. **Telegram Notifications** - Instant alerts on any login attempt
2. **TOTP 2FA** - Time-based one-time passwords (Google Authenticator / KeePass)
3. **Telegram Interactive Approval** - Approve/Deny logins via Telegram (v0.3.0)

---

### 1. SSH Login Telegram Notifications (Must Have)

| Attribute | Value |
|-----------|-------|
| **Feasibility** | HIGH |
| **Effort** | 1-2 hours |
| **Dependencies** | Existing Telegram bot, PAM |
| **Risk** | LOW - notification only, doesn't block login |

**Implementation via PAM:**

```bash
# 1. Create notification script
sudo tee /usr/local/bin/ssh-notify.sh << 'EOF'
#!/bin/bash
# SSH Login Notification to Telegram via ntfy

if [ "$PAM_TYPE" = "open_session" ]; then
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
  HOSTNAME=$(hostname)

  # Get geolocation (optional, requires curl)
  GEO=$(curl -s "http://ip-api.com/line/$PAM_RHOST?fields=country,city" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')

  MESSAGE="🔐 *SSH Login Alert*

Host: \`$HOSTNAME\`
User: \`$PAM_USER\`
From: \`$PAM_RHOST\`
Location: $GEO
Time: $TIMESTAMP
TTY: \`$PAM_TTY\`"

  # Send via ntfy (which forwards to Telegram)
  curl -s -X POST "http://localhost:8765/monitoring-alerts" \
    -H "Title: SSH Login: $PAM_USER" \
    -H "Priority: high" \
    -H "Tags: key,warning" \
    -d "$MESSAGE" > /dev/null 2>&1 &
fi
EOF

# 2. Make executable
sudo chmod +x /usr/local/bin/ssh-notify.sh

# 3. Add to PAM configuration
sudo tee -a /etc/pam.d/sshd << 'EOF'

# SSH Login Telegram Notifications
session optional pam_exec.so seteuid /usr/local/bin/ssh-notify.sh
EOF

# 4. Test (no restart needed - PAM reads config on each auth)
ssh localhost
```

**Notification Content:**
```
🔐 SSH Login Alert

Host: oci-server
User: ubuntu
From: 203.0.113.45
Location: Cairo, Egypt
Time: 2025-11-25 14:30:00 EET
TTY: pts/0
```

**Failed Login Notifications (Optional):**
```bash
# Add to /etc/pam.d/sshd for failed attempts
auth optional pam_exec.so seteuid /usr/local/bin/ssh-notify-failed.sh
```

---

### 2. TOTP Two-Factor Authentication (Must Have)

| Attribute | Value |
|-----------|-------|
| **Feasibility** | HIGH |
| **Effort** | 1-2 hours |
| **Dependencies** | libpam-google-authenticator |
| **Risk** | MEDIUM - can lock yourself out if misconfigured |

**Implementation:**

```bash
# 1. Install Google Authenticator PAM module
sudo apt-get update
sudo apt-get install -y libpam-google-authenticator

# 2. Configure for your user
google-authenticator
# Answer prompts:
#   - Time-based tokens: y
#   - Update .google_authenticator: y
#   - Disallow reuse: y
#   - Rate limiting: y

# IMPORTANT: Save the secret key, QR code, and emergency codes!

# 3. Add to KeePass (if using KeePass for TOTP)
#    - Create new entry for "OCI Server SSH"
#    - Add TOTP field with the secret key
#    - KeePass will generate 6-digit codes

# 4. Configure PAM
sudo tee -a /etc/pam.d/sshd << 'EOF'

# Two-Factor Authentication
auth required pam_google_authenticator.so nullok
EOF

# 5. Configure SSH daemon
sudo sed -i 's/^#*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#*KbdInteractiveAuthentication.*/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config

# For key + TOTP (most secure):
echo "AuthenticationMethods publickey,keyboard-interactive" | sudo tee -a /etc/ssh/sshd_config

# 6. Restart SSH
sudo systemctl restart sshd

# 7. TEST IN A NEW TERMINAL BEFORE CLOSING CURRENT SESSION!
```

**Login Flow After Setup:**
```
$ ssh ubuntu@159.54.162.114
Verification code: ******    <- Enter TOTP from phone/KeePass
Welcome to Ubuntu...
```

**Emergency Recovery:**
- Keep emergency scratch codes in password manager
- Have console access via OCI dashboard as backup
- Consider adding a backup SSH key without 2FA for emergencies

---

### 3. Telegram Interactive Approval (Nice to Have - v0.3.0)

| Attribute | Value |
|-----------|-------|
| **Feasibility** | MEDIUM |
| **Effort** | 4-8 hours |
| **Dependencies** | Custom bot, Redis/file state, PAM module |
| **Risk** | HIGH - can lock yourself out |

**Architecture:**
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ SSH Login   │────▶│ PAM Module   │────▶│ Auth Bot    │
│ Attempt     │     │ (blocking)   │     │ Service     │
└─────────────┘     └──────────────┘     └──────┬──────┘
                           │                     │
                           │ polls               │ sends
                           ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │ Redis/File   │◀────│ Telegram    │
                    │ State Store  │     │ (buttons)   │
                    └──────────────┘     └─────────────┘
```

**Telegram Message:**
```
🔐 SSH Login Request

User: ubuntu
From: 203.0.113.45 (Cairo, Egypt)
Time: 2025-11-25 14:30:00

[✅ Approve]  [❌ Deny]

⏱️ Auto-deny in 60 seconds
```

**Implementation Components:**

1. **telegram-ssh-auth service** (Python)
```python
# telegram_ssh_auth.py
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler

PENDING_AUTHS = {}  # session_id -> {"approved": None, "expires": timestamp}

async def handle_auth_request(session_id, user, ip):
    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{session_id}"),
        InlineKeyboardButton("❌ Deny", callback_data=f"deny:{session_id}")
    ]]
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"🔐 *SSH Login Request*\n\nUser: `{user}`\nFrom: `{ip}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    PENDING_AUTHS[session_id] = {"approved": None, "expires": time.time() + 60}

async def button_callback(update: Update, context):
    query = update.callback_query
    action, session_id = query.data.split(":")

    if session_id in PENDING_AUTHS:
        PENDING_AUTHS[session_id]["approved"] = (action == "approve")
        await query.edit_message_text(
            f"{'✅ Approved' if action == 'approve' else '❌ Denied'} by {query.from_user.first_name}"
        )
```

2. **PAM Module** (bash wrapper)
```bash
#!/bin/bash
# /usr/local/bin/ssh-telegram-auth.sh

SESSION_ID=$(uuidgen)
curl -X POST "http://localhost:8766/auth-request" \
  -d "session_id=$SESSION_ID&user=$PAM_USER&ip=$PAM_RHOST"

# Poll for approval (max 60 seconds)
for i in {1..60}; do
  RESULT=$(curl -s "http://localhost:8766/auth-status/$SESSION_ID")
  if [ "$RESULT" = "approved" ]; then
    exit 0  # Allow login
  elif [ "$RESULT" = "denied" ]; then
    exit 1  # Deny login
  fi
  sleep 1
done

exit 1  # Timeout = deny
```

**Safety Measures (CRITICAL):**
```bash
# ALWAYS keep an emergency bypass!

# Option 1: Whitelist your home IP
# /etc/pam.d/sshd
auth [success=done default=ignore] pam_access.so accessfile=/etc/security/access-bypass.conf
auth required pam_exec.so /usr/local/bin/ssh-telegram-auth.sh

# /etc/security/access-bypass.conf
+ : ALL : 192.168.1.0/24    # Your home network
+ : ALL : 10.0.0.0/8        # VPN network
- : ALL : ALL

# Option 2: Separate SSH port without Telegram auth
# Port 22 = Telegram approval required
# Port 2222 = Key-only, no Telegram (emergency)
```

**Defer to v0.3.0 because:**
- Requires custom development
- High risk of lockout
- Need robust testing
- TOTP provides similar security with less complexity

---

### SSH Security Summary

| Feature | Priority | Version | Effort | Risk |
|---------|----------|---------|--------|------|
| Telegram notifications | Must Have | v0.2.0 | 1-2 hrs | Low |
| TOTP 2FA | Must Have | v0.2.0 | 1-2 hrs | Medium |
| Telegram approval | Nice to Have | v0.3.0 | 4-8 hrs | High |

**v0.2.0 Total SSH Security Effort: 2-4 hours**

---

## DDoS Protection

### Current State Assessment

| Layer | Current Protection | Risk Level |
|-------|-------------------|------------|
| Network (L3/L4) | OCI default only | HIGH |
| Protocol (SYN flood) | None | HIGH |
| Application (L7) | ntfy: 100 req/10s only | HIGH |
| Slowloris | None | MEDIUM |
| Brute Force | None | HIGH |

### DDoS Mitigation Strategy

#### Option A: Cloudflare (Recommended)
| Attribute | Value |
|-----------|-------|
| **Effort** | 30-60 minutes |
| **Cost** | Free tier available |
| **Protection** | L3/L4/L7 DDoS, WAF, bot mitigation |
| **Impact** | All public endpoints protected |

**Implementation Steps:**
1. Create Cloudflare account (free)
2. Add domain `qubix.space` to Cloudflare
3. Update DNS nameservers at registrar
4. Configure SSL mode: Full (Strict)
5. Enable "Under Attack" mode toggle for emergencies
6. Configure Page Rules for caching static content

**Cloudflare Settings:**
```
SSL/TLS: Full (Strict)
Always Use HTTPS: On
Minimum TLS Version: 1.2
Auto Minify: Off (monitoring dashboards)
Brotli: On
HTTP/3: On
0-RTT: On
WebSockets: On (required for Grafana live)
```

**Firewall Rules (Free Tier):**
```
# Block known bad bots
(cf.client.bot) -> Block

# Rate limit API endpoints
(http.request.uri.path contains "/api/") -> Rate Limit: 100 req/min

# Challenge suspicious traffic
(cf.threat_score gt 14) -> Managed Challenge
```

---

#### Option B: Caddy Rate Limiting (Minimum)
| Attribute | Value |
|-----------|-------|
| **Effort** | 1-2 hours |
| **Cost** | Free |
| **Protection** | L7 rate limiting only |
| **Impact** | Application layer only |

**Caddyfile Configuration:**
```caddyfile
# Global rate limit snippet
(rate_limit) {
    rate_limit {
        zone dynamic {
            key {remote_host}
            events 100
            window 1m
        }
    }
}

# Apply to all monitoring endpoints
monitor.qubix.space {
    import rate_limit
    basicauth {
        admin $2a$14$...
    }
    reverse_proxy oci-netdata:19999
}

grafana.qubix.space {
    import rate_limit
    reverse_proxy oci-grafana:3000
}

notify.qubix.space {
    import rate_limit
    reverse_proxy oci-ntfy:80
}
```

**Note:** Requires Caddy `rate-limit` plugin. Check if installed:
```bash
docker exec infrastructure_files-caddy-1 caddy list-modules | grep rate
```

---

#### Option C: Fail2ban (Brute Force Protection)
| Attribute | Value |
|-----------|-------|
| **Effort** | 1 hour |
| **Cost** | Free |
| **Protection** | Brute force, repeated failures |
| **Impact** | SSH, Grafana login |

**Installation:**
```bash
# On server
sudo apt-get update && sudo apt-get install -y fail2ban

# Create Grafana jail
sudo tee /etc/fail2ban/jail.d/grafana.conf << 'EOF'
[grafana]
enabled = true
port = http,https
filter = grafana
logpath = /var/lib/docker/volumes/monitoring_grafana-data/_data/log/grafana.log
maxretry = 5
findtime = 600
bantime = 3600
action = iptables-allports[name=grafana]
EOF

# Create Grafana filter
sudo tee /etc/fail2ban/filter.d/grafana.conf << 'EOF'
[Definition]
failregex = ^.*Failed login attempt.*client_ip=<HOST>.*$
            ^.*Invalid username or password.*remote_addr=<HOST>.*$
ignoreregex =
EOF

# Restart fail2ban
sudo systemctl restart fail2ban
sudo fail2ban-client status grafana
```

---

### Recommended Approach

**Phase 1 (v0.2.0):** Cloudflare + Fail2ban
- Cloudflare handles volumetric and application DDoS
- Fail2ban handles brute force against SSH and Grafana
- Caddy rate limiting as backup (if Cloudflare bypassed)

**Phase 2 (v0.3.0):** Enhanced monitoring
- DDoS attack alerting via Telegram
- Grafana dashboard for attack metrics
- Automated "Under Attack" mode trigger

---

## Deferred Items from v0.1.1

### 1. Docker Secrets Migration
| Attribute | Value |
|-----------|-------|
| **Current** | Telegram tokens in plain `.env` |
| **Target** | Docker secrets (encrypted at rest) |
| **Effort** | 1 hour |
| **Priority** | HIGH |

### 2. ntfy ACLs
| Attribute | Value |
|-----------|-------|
| **Current** | Open topics |
| **Target** | Authenticated publish/subscribe |
| **Effort** | 30 minutes |
| **Priority** | MEDIUM |

### 3. Docker Socket Proxy
| Attribute | Value |
|-----------|-------|
| **Current** | Direct socket mount (read-only) |
| **Target** | tecnativa/docker-socket-proxy |
| **Effort** | 30 minutes |
| **Priority** | MEDIUM |

### 4. Fail2ban
| Attribute | Value |
|-----------|-------|
| **Current** | None |
| **Target** | Protect SSH + Grafana |
| **Effort** | 1 hour |
| **Priority** | HIGH (part of DDoS strategy) |

---

## Dependency Management (Original v0.2.0)

### Pin Docker Image Versions
| Service | Current | Action |
|---------|---------|--------|
| Netdata | `:latest` | Pin to current version |
| ntfy | `:latest` | Pin to current version |
| Loki | `3.0.0` | Already pinned |
| Promtail | `3.0.0` | Already pinned |
| Grafana | `11.0.0` | Already pinned |

### Create DEPENDENCIES.md
- Document all versions
- Update procedures
- Compatibility matrix

---

## v0.2.0 Release Requirements

### Must Have (Blockers)
- [ ] **SSH Telegram notifications** - Instant alerts on login attempts
- [ ] **SSH TOTP 2FA** - Two-factor authentication with Google Authenticator/KeePass
- [ ] Cloudflare integration (or Caddy rate limiting minimum)
- [ ] Fail2ban installation and configuration
- [ ] Docker secrets for Telegram credentials
- [ ] Pin Netdata and ntfy versions

### Should Have
- [ ] SSH failed login notifications
- [ ] ntfy ACLs enabled
- [ ] Docker socket proxy
- [ ] DEPENDENCIES.md documentation
- [ ] Caddy rate limiting (as Cloudflare backup)

### Nice to Have (Defer to v0.3.0)
- [ ] **Telegram interactive SSH approval** (Approve/Deny buttons)
- [ ] DDoS monitoring dashboard in Grafana
- [ ] Automated attack alerting via Telegram
- [ ] UPDATE_POLICY.md documentation

---

## v0.2.0 Deployment Strategy

### Pre-Deployment
1. Create Cloudflare account and configure domain
2. Test DNS propagation
3. Generate Docker secrets
4. Prepare updated docker-compose.yml
5. Backup all current configurations
6. **Save TOTP emergency codes in password manager**
7. **Verify OCI console access (backup if SSH fails)**

### Deployment Order
1. **SSH Telegram notifications** (low risk, test first)
2. **Cloudflare** (can be done independently, DNS propagation: 24-48h)
3. **Fail2ban** (independent, no downtime)
4. **SSH TOTP 2FA** (CRITICAL: Test in new terminal before closing session!)
5. **Docker secrets** (requires container restart)
6. **Version pinning** (may require image pull)
7. **ntfy ACLs** (requires ntfy restart)
8. **Docker socket proxy** (requires health-check restart)

### Rollback Plan
- **SSH TOTP**: Remove lines from `/etc/pam.d/sshd`, restart sshd
- **SSH notifications**: Remove PAM exec line (non-blocking, safe)
- Cloudflare: Switch DNS back to direct (instant via "pause")
- Fail2ban: `sudo systemctl stop fail2ban`
- Docker secrets: Revert to `.env` environment variables
- Other: Restore from backup docker-compose.yml

**TOTP Emergency Recovery:**
```bash
# If locked out:
# 1. Access via OCI Console (web-based terminal)
# 2. Remove TOTP requirement:
sudo sed -i '/pam_google_authenticator/d' /etc/pam.d/sshd
sudo sed -i '/AuthenticationMethods/d' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

## v0.2.0 Timeline Estimate

| Task | Effort | Dependencies |
|------|--------|--------------|
| **SSH Telegram notifications** | 1-2 hours | None |
| **SSH TOTP 2FA** | 1-2 hours | None |
| Cloudflare setup | 1 hour | None |
| DNS propagation | 24-48 hours | Cloudflare |
| Fail2ban | 1 hour | None |
| Docker secrets | 1 hour | None |
| Version pinning | 30 min | None |
| ntfy ACLs | 30 min | None |
| Docker socket proxy | 30 min | None |
| Documentation | 2 hours | All above |
| **Total** | **~10-12 hours** | + DNS wait |

**Target**: 1 week after v0.1.1 release

---

**Planning Document Version:** 4.0
**Created:** November 25, 2025
**Updated:** November 25, 2025 (v0.1.1 progress + v0.3.0 passive income planning)
**Author:** Claude Code
**Status:** v0.1.1 in progress (3/6 complete), v0.2.0 planned, v0.3.0 planned

---

## v0.3.0 Planning - Passive Income & Advanced Features

### Release Overview
- **Proposed Version**: 0.3.0
- **Release Type**: Minor (New Features)
- **Target Date**: After v0.2.0 stabilization
- **Risk Level**: Low (optional services, isolated from core infrastructure)

### Scope

v0.3.0 focuses on:
1. **Passive Income Services** - Bandwidth sharing for passive revenue
2. **Deferred v0.2.0 items** - Telegram SSH approval, advanced monitoring
3. **Infrastructure optimization** - Resource monitoring for income services

---

### Passive Income Services (NEW)

#### Server Resource Assessment (Actual)
| Resource | Total | Used | Available |
|----------|-------|------|-----------|
| **CPU** | 2 vCPU (AMD EPYC) | ~10% | ~90% |
| **RAM** | 956 MB | 619 MB (65%) | **337 MB** |
| **Disk** | 45 GB | 13 GB (28%) | **32 GB** |
| **Bandwidth** | 480 Mbps | Variable | Available |

#### Recommended Services (Resource-Appropriate)

| Service | RAM | CPU | Expected Income | Priority |
|---------|-----|-----|-----------------|----------|
| **Grass.io** | ~20 MB | ~0% | $5-20/month | Must Have |
| **Honeygain** | ~30 MB | ~0% | $1-10/month | Must Have |
| **PacketStream** | ~20 MB | ~0% | $1-5/month | Must Have |
| **Combined** | **~70 MB** | **~1%** | **$7-35/month** | - |

**Post-deployment available RAM**: 337 - 70 = **267 MB** ✅

#### Services NOT Recommended (Insufficient Resources)

| Service | Requirement | Status |
|---------|-------------|--------|
| Flux Nodes | 4+ GB RAM | ❌ Insufficient RAM |
| Storj | 200+ MB RAM | ⚠️ Too tight |
| Crypto Mining | 100% CPU | ❌ Not viable on 2 vCPU |
| Akash Provider | 2+ GB RAM | ❌ Insufficient RAM |

#### Implementation

**docker-compose.passive-income.yml:**
```yaml
version: '3.8'

services:
  # Grass.io - AI data network (~$5-20/month)
  grass:
    image: grassio/grass-node:latest
    container_name: passive-grass
    restart: unless-stopped
    environment:
      - GRASS_USER=${GRASS_EMAIL}
      - GRASS_PASS=${GRASS_PASS}
    mem_limit: 50m
    cpus: 0.1
    networks:
      - passive-income

  # Honeygain - bandwidth sharing (~$1-10/month)
  honeygain:
    image: honeygain/honeygain:latest
    container_name: passive-honeygain
    restart: unless-stopped
    command: -tou-accept -email ${HG_EMAIL} -pass ${HG_PASS} -device oci-cairo
    mem_limit: 50m
    cpus: 0.1
    networks:
      - passive-income

  # PacketStream - bandwidth marketplace (~$1-5/month)
  packetstream:
    image: packetstream/psclient:latest
    container_name: passive-packetstream
    restart: unless-stopped
    environment:
      - CID=${PACKETSTREAM_CID}
    mem_limit: 50m
    cpus: 0.1
    networks:
      - passive-income

networks:
  passive-income:
    name: passive-income
```

**Environment Variables (.env):**
```bash
# Grass.io
GRASS_EMAIL=your@email.com
GRASS_PASS=your_password

# Honeygain
HG_EMAIL=your@email.com
HG_PASS=your_password

# PacketStream
PACKETSTREAM_CID=your_cid
```

#### Deployment Steps

1. Sign up for accounts:
   - Grass.io: https://app.getgrass.io/
   - Honeygain: https://honeygain.com/
   - PacketStream: https://packetstream.io/

2. Create docker-compose file on server
3. Configure environment variables
4. Deploy: `docker compose -f docker-compose.passive-income.yml up -d`
5. Monitor resource usage for 24-48 hours
6. Add to health check monitoring

#### Monitoring Integration

Add to existing health check:
```yaml
# config.yml addition
containers:
  passive-grass:
    priority: low
    restart_threshold: 5
  passive-honeygain:
    priority: low
    restart_threshold: 5
  passive-packetstream:
    priority: low
    restart_threshold: 5
```

---

### Deferred Features from v0.2.0

- **Telegram interactive SSH approval** (Approve/Deny buttons with timeout)
- DDoS monitoring dashboard in Grafana
- Automated "Under Attack" mode trigger
- Enhanced security event monitoring

---

### v0.3.0 Release Requirements

#### Must Have
- [ ] Grass.io container deployment
- [ ] Honeygain container deployment
- [ ] PacketStream container deployment
- [ ] Resource usage monitoring for 48 hours
- [ ] Documentation for passive income setup

#### Should Have
- [ ] Add passive services to health check
- [ ] Grafana dashboard for passive income containers
- [ ] Telegram SSH interactive approval

#### Nice to Have
- [ ] Income tracking/reporting
- [ ] Automated service restart on low earnings
- [ ] DDoS monitoring dashboard

---

### v0.3.0 Timeline Estimate

| Task | Effort | Dependencies |
|------|--------|--------------|
| Account signups | 30 min | None |
| Docker compose creation | 30 min | Accounts |
| Deployment | 15 min | Compose file |
| 48-hour monitoring | 48 hours | Deployment |
| Health check integration | 1 hour | Monitoring |
| Documentation | 1 hour | All above |
| Telegram SSH approval | 4-8 hours | None |
| **Total** | **~8-12 hours** | + 48hr wait |

**Target**: 2 weeks after v0.2.0 release
