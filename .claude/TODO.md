# TODO - Security Hardening & Infrastructure Enhancement

## Overview
This TODO tracks tasks for v0.1.1 through v0.3.0 releases, focusing on security hardening, SSH protection, DDoS mitigation, encrypted secrets vault, and passive income services.

**Strategic Context**: Security vulnerabilities identified in comprehensive review (Nov 25, 2025). Dependency management (original v0.2.0) deferred to v0.4.0.

**Link to Strategy**: See `.claude/PLANNING.md` v5.0 for complete release plan.

---

## Current Focus: v0.1.1 Security Hardening

**Status**: 50% Complete (3/6 tasks done)
**Remaining Effort**: ~25 minutes on server

### Completed ✅
- [x] Fix SSH key permissions (`chmod 600`) - Local
- [x] Create root `.gitignore` - Commit 547c41b
- [x] Delete unused SSH key from myOCI/ - Deleted

### Pending (Server-Side)

#### [v0.1.1-1] Change Grafana admin password
**Priority**: CRITICAL
**Effort**: 5 minutes
**Risk**: HIGH - Default credentials exposed

```bash
# SSH to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Generate strong password
GRAFANA_PASS=$(openssl rand -base64 24)
echo "Save this password: $GRAFANA_PASS"

# Add to .env
cd ~/monitoring
echo "GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASS" >> .env

# Restart Grafana
docker compose restart grafana

# Verify login at https://grafana.qubix.space
```

**Definition of Done**:
- [ ] Strong password generated and saved in password manager
- [ ] .env updated with GRAFANA_ADMIN_PASSWORD
- [ ] Grafana restarted
- [ ] Login verified with new credentials

---

#### [v0.1.1-2] Configure Caddy BasicAuth for Netdata
**Priority**: HIGH
**Effort**: 10 minutes
**Risk**: MEDIUM-HIGH - Metrics exposed without auth

```bash
# Generate bcrypt password hash
docker exec infrastructure_files-caddy-1 caddy hash-password
# Enter password when prompted, save the hash

# Edit Caddyfile - add basicauth block to monitor.qubix.space:
# basicauth {
#     admin $2a$14$<your-bcrypt-hash>
# }

# Reload Caddy
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile

# Verify auth required at https://monitor.qubix.space
```

**Definition of Done**:
- [ ] Password hash generated
- [ ] Caddyfile updated with basicauth block
- [ ] Caddy reloaded
- [ ] Authentication required when accessing Netdata

---

#### [v0.1.1-3] Bind Loki to localhost only
**Priority**: MEDIUM
**Effort**: 5 minutes
**Risk**: MEDIUM - Log API exposed if firewall misconfigured

```bash
cd ~/monitoring

# Edit docker-compose.yml
# Change: "3100:3100"
# To:     "127.0.0.1:3100:3100"

# Apply change
docker compose up -d loki

# Verify not accessible externally
curl http://<server-public-ip>:3100  # Should fail
curl http://localhost:3100  # Should work (from server)
```

**Definition of Done**:
- [ ] docker-compose.yml updated
- [ ] Loki restarted
- [ ] External access blocked
- [ ] Internal access still works

---

#### [v0.1.1-4] Create v0.1.1 tag
**Priority**: HIGH
**Effort**: 5 minutes
**Dependencies**: v0.1.1-1, v0.1.1-2, v0.1.1-3

```bash
git tag -a v0.1.1 -m "$(cat <<'EOF'
Release v0.1.1 - Security Hardening

Security Fixes:
- Fixed SSH private key file permissions (644 → 600)
- Added root .gitignore to protect sensitive files
- Changed Grafana default admin password
- Added Caddy BasicAuth for Netdata dashboard
- Bound Loki API to localhost only

Documentation:
- Updated PLANNING.md with security roadmap
- Added progress review (REVIEW-2025-11-25.md)

See CHANGELOG.md for complete details.
EOF
)"

git push origin main --tags
```

---

## v0.2.0 - SSH Security + DDoS + Encrypted Vault

**Status**: Planned
**Estimated Effort**: 13-16 hours + DNS propagation
**Target**: 1 week after v0.1.1

### Must Have (Blockers)

#### [v0.2.0-1] Generate Age key pair
**Priority**: HIGH (Prerequisite for vault)
**Effort**: 15 minutes

```bash
# Install age
# macOS: brew install age
# Ubuntu: sudo apt install age

# Generate key
age-keygen -o ~/.config/sops/age/keys.txt

# Save public key for SOPS config
cat ~/.config/sops/age/keys.txt | grep "public key"

# Backup private key to password manager!
```

**Definition of Done**:
- [ ] Age installed on local machine and server
- [ ] Key pair generated
- [ ] Public key noted for .sops.yaml
- [ ] Private key backed up securely

---

#### [v0.2.0-2] Deploy Redis + Age Vault
**Priority**: HIGH
**Effort**: 2-3 hours
**Dependencies**: v0.2.0-1

Create `docker-compose.vault.yml` and vault-api service per PLANNING.md.

**Definition of Done**:
- [ ] docker-compose.vault.yml created
- [ ] vault-api Dockerfile and Python code created
- [ ] Vault deployed and running
- [ ] API accessible at localhost:8200
- [ ] Health check passing

---

#### [v0.2.0-3] Migrate secrets to vault
**Priority**: HIGH
**Effort**: 1 hour
**Dependencies**: v0.2.0-2

```bash
# Store secrets in vault
curl -X POST http://localhost:8200/v1/secret/telegram/bot_token \
  -H "Content-Type: application/json" \
  -d '{"value": "<token>"}'

curl -X POST http://localhost:8200/v1/secret/telegram/chat_id \
  -H "Content-Type: application/json" \
  -d '{"value": "<chat_id>"}'

curl -X POST http://localhost:8200/v1/secret/grafana/admin_password \
  -H "Content-Type: application/json" \
  -d '{"value": "<password>"}'
```

**Definition of Done**:
- [ ] Telegram bot token stored
- [ ] Telegram chat ID stored
- [ ] Grafana password stored
- [ ] Secrets retrievable via API

---

#### [v0.2.0-4] SSH Telegram notifications
**Priority**: HIGH
**Effort**: 1-2 hours

Create `/usr/local/bin/ssh-notify.sh` and add to `/etc/pam.d/sshd` per PLANNING.md.

**Definition of Done**:
- [ ] Notification script created
- [ ] PAM configured
- [ ] Test login sends Telegram message
- [ ] Message includes user, IP, timestamp, geolocation

---

#### [v0.2.0-5] SSH TOTP 2FA
**Priority**: HIGH
**Effort**: 1-2 hours
**Risk**: HIGH - Can lock yourself out

```bash
# Install
sudo apt install libpam-google-authenticator

# Configure
google-authenticator
# Save emergency codes in password manager!

# Update PAM and SSH config per PLANNING.md

# TEST IN NEW TERMINAL BEFORE CLOSING CURRENT SESSION!
```

**Definition of Done**:
- [ ] libpam-google-authenticator installed
- [ ] User configured with TOTP
- [ ] Emergency codes saved securely
- [ ] PAM and sshd configured
- [ ] Login requires TOTP code
- [ ] OCI Console access verified as backup

---

#### [v0.2.0-6] Cloudflare integration
**Priority**: HIGH
**Effort**: 1 hour + 24-48h DNS propagation

1. Create Cloudflare account
2. Add domain qubix.space
3. Update nameservers at registrar
4. Configure SSL: Full (Strict)
5. Enable basic security features

**Definition of Done**:
- [ ] Cloudflare account created
- [ ] Domain added
- [ ] Nameservers updated
- [ ] DNS propagated
- [ ] SSL working
- [ ] Basic protection active

---

#### [v0.2.0-7] Fail2ban installation
**Priority**: HIGH
**Effort**: 1 hour

```bash
sudo apt install fail2ban
# Configure jails for SSH and Grafana per PLANNING.md
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Definition of Done**:
- [ ] Fail2ban installed
- [ ] SSH jail configured
- [ ] Grafana jail configured (optional)
- [ ] Service running
- [ ] Test: Failed logins result in ban

---

#### [v0.2.0-8] Pin Netdata and ntfy versions
**Priority**: MEDIUM
**Effort**: 30 minutes

```bash
# Check current versions
docker inspect oci-netdata --format '{{.Config.Image}}'
docker inspect oci-ntfy --format '{{.Config.Image}}'

# Update docker-compose.yml with specific versions
# e.g., netdata/netdata:v1.45.0 instead of :latest
```

**Definition of Done**:
- [ ] Current versions identified
- [ ] docker-compose.yml updated
- [ ] Containers recreated with pinned versions
- [ ] Services verified working

---

### Should Have

#### [v0.2.0-9] SOPS + Age for .env encryption
**Priority**: MEDIUM
**Effort**: 30 minutes

```bash
# Create .sops.yaml
cat > .sops.yaml << 'EOF'
creation_rules:
  - path_regex: \.env$
    age: age1<your-public-key>
EOF

# Encrypt .env
sops --encrypt .env > .env.enc
```

---

#### [v0.2.0-10] ntfy ACLs
**Priority**: MEDIUM
**Effort**: 30 minutes

Enable authentication on ntfy topics per PLANNING.md.

---

#### [v0.2.0-11] Docker socket proxy
**Priority**: MEDIUM
**Effort**: 30 minutes

Deploy tecnativa/docker-socket-proxy to limit API access.

---

#### [v0.2.0-12] Create v0.2.0 tag
**Priority**: HIGH
**Effort**: 5 minutes
**Dependencies**: All v0.2.0 Must Have tasks

---

## v0.3.0 - Passive Income & Advanced Features

**Status**: Planned
**Estimated Effort**: 8-12 hours + 48h monitoring
**Target**: 2 weeks after v0.2.0

### Passive Income Services

#### [v0.3.0-1] Sign up for bandwidth sharing services
**Priority**: HIGH
**Effort**: 30 minutes

1. Grass.io: https://app.getgrass.io/
2. Honeygain: https://honeygain.com/
3. PacketStream: https://packetstream.io/

---

#### [v0.3.0-2] Deploy passive income containers
**Priority**: HIGH
**Effort**: 1 hour
**Dependencies**: v0.3.0-1

Create `docker-compose.passive-income.yml` per PLANNING.md:
- Grass.io (~20 MB RAM)
- Honeygain (~30 MB RAM)
- PacketStream (~20 MB RAM)

**Expected Income**: $7-35/month

---

#### [v0.3.0-3] Monitor resource usage
**Priority**: HIGH
**Effort**: 48 hours (monitoring period)

Verify services don't impact server performance.

---

#### [v0.3.0-4] Telegram SSH interactive approval
**Priority**: MEDIUM
**Effort**: 4-8 hours
**Risk**: HIGH - Can lock yourself out

Implement Approve/Deny buttons per PLANNING.md.
Requires emergency bypass IP configured.

---

## v0.4.0 - Dependency Management (Deferred)

**Status**: Deferred from original v0.2.0
**Reason**: Security prioritized over dependency management

Tasks moved from original TODO.md:
- DEPENDENCIES.md baseline documentation
- UPDATE_POLICY.md procedures
- COMPATIBILITY_MATRIX.md
- Version check script (scripts/check-versions.sh)
- Automated update notifications

---

## Progress Tracking

### v0.1.1 Progress
- **Completed**: 3/6 (50%)
- **Remaining**: 3 tasks (~25 min on server)

### v0.2.0 Progress
- **Completed**: 0/12 (0%)
- **Estimated**: 13-16 hours

### v0.3.0 Progress
- **Completed**: 0/4 (0%)
- **Estimated**: 8-12 hours

---

## Summary Statistics

| Release | Tasks | Hours | Status |
|---------|-------|-------|--------|
| v0.1.1 | 6 | ~1 hr | 50% Complete |
| v0.2.0 | 12 | 13-16 | Planned |
| v0.3.0 | 4 | 8-12 | Planned |
| v0.4.0 | 5+ | 16-23 | Deferred |

**Total Active Tasks**: 22
**Estimated Hours**: 22-29 hours

---

**TODO Document Version**: 2.0
**Created**: November 25, 2025
**Replaces**: v0.2.0 Dependency Management TODO
**Strategic Plan**: .claude/PLANNING.md v5.0
