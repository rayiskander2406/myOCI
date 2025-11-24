# Security Hardening - Monitoring Stack

## Current Security Posture

### Secured
- All services behind VPN (NetBird network)
- Web access via HTTPS (Caddy reverse proxy with Let's Encrypt)
- Docker socket mounted read-only where possible
- Sensitive credentials in .env (gitignored)
- Services isolated on dedicated Docker network
- No direct internet exposure (all access via reverse proxy)

### To Be Hardened
- Grafana has default credentials (admin/admin)
- Netdata has no authentication
- Environment variables in plain text .env file
- No rate limiting on notification endpoints
- ntfy server has open topics without ACLs

## Security Roadmap

### Phase 1 - Basic Authentication (v0.1.1)
1. Enable Grafana strong password authentication
2. Configure Caddy basic auth for Netdata
3. Change all default passwords
4. Rotate Telegram bot token

### Phase 2 - Secrets Management (v0.2.0)
1. Migrate to Docker secrets
2. Enable ntfy ACLs
3. Implement automated secret rotation
4. Add encrypted backup procedures

### Phase 3 - Advanced Security (v0.3.0)
1. Implement rate limiting
2. Add fail2ban integration
3. Enable audit logging
4. Add intrusion detection

## Implementation Guide

### 1. Enable Grafana Authentication

**Current state:** Default admin/admin credentials
**Risk:** Medium - accessible via VPN only, but no user auth
**Priority:** High

**Steps:**

```bash
# 1. Generate strong password
openssl rand -base64 32

# 2. Edit .env on server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
cd ~/monitoring
nano .env

# Add/update:
GRAFANA_ADMIN_PASSWORD=<your-strong-password-here>

# 3. Restart Grafana to apply new password
docker compose restart grafana

# 4. Test login
# Visit: https://grafana.qubix.space
# Login with: admin / <new-password>
```

**Disable anonymous access (if needed):**

Edit `monitoring/docker-compose.yml`:
```yaml
services:
  grafana:
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=false
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
```

**Enable OAuth (optional, future enhancement):**
- Configure Zitadel integration
- Single sign-on for all services
- Centralized user management

**Verification:**
```bash
# Test authentication required
curl -I https://grafana.qubix.space
# Should return 302 redirect to /login

# Test API access with credentials
curl -u admin:<password> http://localhost:3000/api/health
# Should return: {"database":"ok"}
```

### 2. Configure Netdata Authentication (Caddy)

**Current state:** No authentication on Netdata dashboard
**Risk:** Medium - accessible via VPN, but no user auth
**Priority:** Medium

**Steps:**

**Option A: Basic Authentication (Recommended)**

```bash
# 1. Generate bcrypt password hash
docker exec infrastructure_files-caddy-1 caddy hash-password
# Enter your password when prompted
# Copy the bcrypt hash

# 2. Edit Caddyfile on server
# Note: The actual Caddyfile location depends on your setup
# This is typically in /home/ubuntu/netbird/infrastructure_files/Caddyfile

ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
cd /home/ubuntu/netbird/infrastructure_files
nano Caddyfile

# Update the monitor.qubix.space block:
monitor.qubix.space {
    basicauth {
        admin $2a$14$<your-bcrypt-hash-here>
    }
    reverse_proxy oci-netdata:19999
}

# 3. Reload Caddy configuration
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile

# 4. Test authentication
curl -u admin:<password> https://monitor.qubix.space
```

**Option B: Forward Authentication with Zitadel (Advanced)**

```caddyfile
monitor.qubix.space {
    forward_auth zitadel:8080 {
        uri /oauth/v2/authorize
        copy_headers Authorization
    }
    reverse_proxy oci-netdata:19999
}
```

**Verification:**
```bash
# Without credentials - should fail
curl -I https://monitor.qubix.space
# Should return 401 Unauthorized

# With credentials - should succeed
curl -u admin:<password> -I https://monitor.qubix.space
# Should return 200 OK
```

### 3. Migrate to Docker Secrets

**Current state:** Credentials in .env file (plain text)
**Risk:** Medium - file access = credential access
**Priority:** High (v0.2.0)

**Why Docker Secrets:**
- Encrypted at rest
- Only accessible to authorized services
- Not stored in git or logs
- Automatic rotation support

**Steps:**

```bash
# 1. SSH to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
cd ~/monitoring

# 2. Create Docker secrets from current .env
# Read current values first
source .env

echo "$TELEGRAM_BOT_TOKEN" | docker secret create telegram_bot_token -
echo "$TELEGRAM_CHAT_ID" | docker secret create telegram_chat_id -

# Verify secrets created
docker secret ls

# 3. Update docker-compose.yml
nano docker-compose.yml
```

Update `telegram-forwarder` service:
```yaml
services:
  telegram-forwarder:
    build:
      context: ./telegram-forwarder
      dockerfile: Dockerfile
    container_name: oci-telegram-forwarder
    hostname: telegram-forwarder-cairo
    restart: unless-stopped
    secrets:
      - telegram_bot_token
      - telegram_chat_id
    environment:
      - TZ=Africa/Cairo
      - NTFY_URL=http://oci-ntfy
      - NTFY_TOPICS=${NTFY_TOPICS:-monitoring-alerts}
      # These point to the Docker secret files
      - TELEGRAM_BOT_TOKEN_FILE=/run/secrets/telegram_bot_token
      - TELEGRAM_CHAT_ID_FILE=/run/secrets/telegram_chat_id
    networks:
      - monitoring
    depends_on:
      ntfy:
        condition: service_healthy
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

secrets:
  telegram_bot_token:
    external: true
  telegram_chat_id:
    external: true
```

Update `telegram-forwarder/forwarder.py`:
```python
import os

def read_secret(secret_name, env_var_name):
    """Read from Docker secret or environment variable"""
    secret_file = os.getenv(f'{env_var_name}_FILE')
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()
    return os.getenv(env_var_name)

# Read from Docker secrets or fall back to env vars
BOT_TOKEN = read_secret('telegram_bot_token', 'TELEGRAM_BOT_TOKEN')
CHAT_ID = read_secret('telegram_chat_id', 'TELEGRAM_CHAT_ID')
```

```bash
# 4. Rebuild and restart telegram-forwarder
docker compose up -d --build telegram-forwarder

# 5. Verify forwarder is working
docker logs oci-telegram-forwarder --tail 20

# 6. Test notification delivery
curl -H "Priority: urgent" \
     -d "Docker secrets migration test" \
     http://localhost:8765/monitoring-alerts

# 7. If successful, remove secrets from .env
# Keep a backup copy before removing!
cp .env .env.backup
nano .env
# Remove TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID lines

# 8. Commit docker-compose.yml changes to git
git add docker-compose.yml telegram-forwarder/forwarder.py
git commit -m "Migrate Telegram credentials to Docker secrets"
```

### 4. Enable ntfy ACLs

**Current state:** Open topics, no authentication
**Risk:** Low - internal network only
**Priority:** Low (v0.2.0)

**Steps:**

```bash
# 1. Create ntfy server configuration
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
cd ~/monitoring
mkdir -p ntfy/config
nano ntfy/config/server.yml
```

Add configuration:
```yaml
# ntfy server configuration
base-url: http://oci-ntfy:80

# Authentication
auth:
  file: /var/lib/ntfy/user.db
  default-access: deny-all

# Access Control Lists
acl:
  # Critical alerts - only monitoring services can write
  - topic: monitoring-alerts
    write: monitoring-service
    read: admin, monitoring-team

  # Warning alerts
  - topic: monitoring-warnings
    write: monitoring-service
    read: admin, monitoring-team

  # Info alerts
  - topic: monitoring-info
    write: monitoring-service
    read: admin, monitoring-team

# Rate limiting
visitor-request-limit-burst: 100
visitor-request-limit-replenish: "10s"
```

```bash
# 2. Update docker-compose.yml to use config file
nano docker-compose.yml
```

Update ntfy service:
```yaml
services:
  ntfy:
    image: binwiederhier/ntfy:latest
    container_name: oci-ntfy
    hostname: ntfy-cairo
    restart: unless-stopped
    volumes:
      - ./ntfy/config:/etc/ntfy
      - ntfy-cache:/var/cache/ntfy
      - ntfy-data:/var/lib/ntfy
    command:
      - serve
      - --config
      - /etc/ntfy/server.yml  # Point to config file
    environment:
      - TZ=Africa/Cairo
    ports:
      - "8765:80"
    networks:
      - monitoring
      - infrastructure_files_netbird
    healthcheck:
      test: ["CMD-SHELL", "wget -q --tries=1 http://localhost:80/v1/health -O - | grep -Eo '\\\"healthy\\\"\\\\s*:\\\\s*true' || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
```

```bash
# 3. Restart ntfy to create user database
docker compose restart ntfy
sleep 10

# 4. Create users
docker exec -it oci-ntfy ntfy user add monitoring-service
# Enter password when prompted

docker exec -it oci-ntfy ntfy user add admin
# Enter password when prompted

# 5. List users to verify
docker exec -it oci-ntfy ntfy user list

# 6. Update forwarder to use authentication
nano telegram-forwarder/forwarder.py
```

Update forwarder:
```python
import os
import requests

NTFY_URL = os.getenv('NTFY_URL', 'http://oci-ntfy')
NTFY_USERNAME = read_secret('ntfy_username', 'NTFY_USERNAME')
NTFY_PASSWORD = read_secret('ntfy_password', 'NTFY_PASSWORD')

def send_to_ntfy(message, priority='default', topic='monitoring-alerts'):
    """Send notification to ntfy with authentication"""
    url = f'{NTFY_URL}/{topic}'
    headers = {
        'Priority': priority,
        'Authorization': f'Basic {base64.b64encode(f"{NTFY_USERNAME}:{NTFY_PASSWORD}".encode()).decode()}'
    }
    response = requests.post(url, data=message, headers=headers)
    return response.status_code == 200
```

```bash
# 7. Rebuild and restart forwarder
docker compose up -d --build telegram-forwarder

# 8. Test with authentication
curl -u monitoring-service:<password> \
     -H "Priority: urgent" \
     -d "ntfy ACL test" \
     http://localhost:8765/monitoring-alerts
```

### 5. Docker Socket Security

**Current state:** Docker socket mounted in monitoring containers
**Risk:** High - socket access = root access
**Mitigation:** Containers run with minimal permissions, socket mounted read-only where possible

**Best practices:**

```yaml
# Read-only mount (for monitoring/observability)
services:
  netdata:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro  # :ro = read-only

  promtail:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro  # :ro = read-only
```

**Additional hardening:**

```yaml
services:
  netdata:
    cap_drop:
      - ALL
    cap_add:
      - SYS_PTRACE  # Required for process monitoring
      - SYS_ADMIN   # Required for cgroup access
    security_opt:
      - no-new-privileges:true
    read_only: true  # Make container filesystem read-only
    tmpfs:
      - /tmp
      - /var/cache/netdata
```

**Docker API Proxy (future enhancement):**

Instead of mounting socket directly, use a proxy that filters API calls:
```yaml
services:
  docker-socket-proxy:
    image: tecnativa/docker-socket-proxy
    container_name: docker-socket-proxy
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - CONTAINERS=1
      - IMAGES=0
      - INFO=1
      - NETWORKS=0
      - VOLUMES=0
      - POST=0  # Disable write operations
    networks:
      - monitoring

  netdata:
    volumes:
      # Use proxy instead of direct socket
      - docker-socket-proxy:2375
```

**Verification:**
```bash
# Check socket mounts
docker inspect oci-netdata | grep -A 3 "docker.sock"
docker inspect oci-promtail | grep -A 3 "docker.sock"

# Verify read-only mounts (should show ":ro" or "RW": false)
# Expected output includes: "RW": false
```

### 6. Network Isolation

**Current state:** Monitoring network + NetBird network
**Security level:** Good - isolated from public networks

**Network Architecture:**

```
┌─────────────────────────────────────────┐
│ Internet                                │
└────────────────┬────────────────────────┘
                 │
                 │ HTTPS (Let's Encrypt)
                 ▼
┌─────────────────────────────────────────┐
│ Caddy Reverse Proxy                     │
│ - SSL/TLS termination                   │
│ - Authentication                        │
│ - Rate limiting                         │
└────────────────┬────────────────────────┘
                 │
                 │ infrastructure_files_netbird network
                 ▼
┌─────────────────────────────────────────┐
│ Monitoring Stack                        │
│ - Netdata (monitoring network)          │
│ - Grafana (monitoring + netbird)        │
│ - Loki (monitoring network)             │
│ - ntfy (monitoring + netbird)           │
└─────────────────────────────────────────┘
```

**Recommendations:**
- Keep monitoring on separate network
- Only join NetBird network for Caddy access
- No direct internet exposure
- All external access via Caddy (HTTPS)
- Internal services communicate via monitoring network

**Network Security Configuration:**

```yaml
networks:
  monitoring:
    driver: bridge
    internal: false  # Allows outbound connections (for updates, notifications)
    ipam:
      config:
        - subnet: 172.20.0.0/16
    driver_opts:
      com.docker.network.bridge.name: br-monitoring

  infrastructure_files_netbird:
    external: true  # Managed externally
```

### 7. Rate Limiting & Fail2ban

**Priority:** Low (v0.3.0)

**Rate limiting on ntfy (already configured above):**
```yaml
# ntfy config
visitor-request-limit-burst: 100
visitor-request-limit-replenish: "10s"
visitor-email-limit-burst: 20
visitor-email-limit-replenish: "1h"
```

**Rate limiting in Caddy:**
```caddyfile
monitor.qubix.space {
    # Limit to 100 requests per minute per IP
    rate_limit {
        zone monitor_zone {
            key {remote_host}
            events 100
            window 1m
        }
    }

    basicauth {
        admin $2a$14$<bcrypt-hash>
    }

    reverse_proxy oci-netdata:19999
}
```

**Fail2ban for Grafana (requires host installation):**

```bash
# 1. Install fail2ban on host
sudo apt-get install fail2ban

# 2. Create Grafana filter
sudo nano /etc/fail2ban/filter.d/grafana.conf
```

Add filter:
```ini
[Definition]
failregex = ^.*\[security\].*logger=context userId=<F-USER>\d+</F-USER> uname= error="Invalid username or password".*$
            ^.*\[auth\].*logger=.*Failed login attempt.*$
ignoreregex =
```

```bash
# 3. Create Grafana jail
sudo nano /etc/fail2ban/jail.d/grafana.conf
```

Add jail:
```ini
[grafana]
enabled = true
port = 3000,https
filter = grafana
logpath = /var/lib/docker/volumes/monitoring_grafana-data/_data/log/grafana.log
maxretry = 5
findtime = 600
bantime = 3600
action = iptables-allports[name=grafana]
```

```bash
# 4. Restart fail2ban
sudo systemctl restart fail2ban

# 5. Check status
sudo fail2ban-client status grafana
```

## Security Checklist

### Pre-Production
- [ ] Change default Grafana password
- [ ] Enable Grafana authentication (disable anonymous)
- [ ] Configure Caddy basic auth for Netdata
- [ ] Generate new Telegram bot token (if using default)
- [ ] Verify .env in .gitignore
- [ ] Review Docker socket permissions (read-only where possible)
- [ ] Verify all services restart policy is "unless-stopped"
- [ ] Check no sensitive data in docker-compose.yml
- [ ] Test backup and recovery procedures
- [ ] Document all credentials in password manager

### Post-Production (v0.1.1)
- [ ] Migrate to Docker secrets
- [ ] Enable ntfy ACLs
- [ ] Implement backup encryption with GPG
- [ ] Set up security monitoring
- [ ] Document incident response procedures
- [ ] Enable audit logging for authentication events
- [ ] Configure automated vulnerability scanning

### Ongoing (Monthly/Quarterly)
- [ ] Monthly security review
- [ ] Quarterly password rotation
- [ ] Review access logs for anomalies
- [ ] Update dependencies (docker-compose pull)
- [ ] Monitor security advisories (GitHub, Docker Hub)
- [ ] Test disaster recovery procedures
- [ ] Verify backup integrity

## Incident Response

### If Credentials Compromised

**Immediate actions (within 1 hour):**

1. **Rotate all affected credentials:**
```bash
# Grafana admin password
ssh ubuntu@159.54.162.114
cd ~/monitoring
nano .env
# Update GRAFANA_ADMIN_PASSWORD
docker compose restart grafana

# Telegram bot token
# Create new bot with @BotFather
# Update .env with new token
docker compose restart telegram-forwarder
```

2. **Review access logs:**
```bash
# Grafana login attempts
docker logs oci-grafana | grep -i "auth\|login"

# ntfy access logs
docker logs oci-ntfy | grep -E "POST|GET" | tail -100

# Caddy access logs
docker logs infrastructure_files-caddy-1 | grep -E "grafana|monitor|notify"
```

3. **Check for data exfiltration:**
```bash
# Check unusual network activity
docker stats --no-stream

# Check container logs for suspicious activity
docker compose logs --tail=1000 | grep -iE "error|unauthorized|forbidden|suspicious"
```

4. **Notify relevant parties:**
- Document the incident timeline
- Notify team members
- Update incident log

5. **Update security procedures:**
- Document lessons learned
- Update incident response playbook
- Implement additional monitoring if needed

### If Service Compromised

**Immediate actions:**

1. **Isolate affected container:**
```bash
# Stop the compromised container
docker stop <container-name>

# Disconnect from networks
docker network disconnect monitoring <container-name>
```

2. **Take forensic snapshot (if needed):**
```bash
# Export container filesystem
docker export <container-name> > container-forensics-$(date +%Y%m%d-%H%M%S).tar

# Save logs before removal
docker logs <container-name> > container-logs-$(date +%Y%m%d-%H%M%S).log
```

3. **Remove and rebuild:**
```bash
# Remove compromised container
docker rm -f <container-name>

# Pull fresh image
docker compose pull <service-name>

# Rebuild from source if custom image
cd ~/monitoring
docker compose build --no-cache <service-name>

# Recreate container
docker compose up -d <service-name>
```

4. **Review for IOCs (Indicators of Compromise):**
```bash
# Check for unusual processes
docker exec <container-name> ps aux

# Check for unusual network connections
docker exec <container-name> netstat -tuln

# Check for modified files
docker diff <container-name>
```

5. **Restore from backup if needed:**
```bash
# See BACKUP.md for full restore procedures
# Example: Restore Grafana from backup
scp ~/backups/monitoring/YYYYMMDD/grafana-data-*.tar.gz ubuntu@159.54.162.114:~/monitoring/
# Follow restore procedures in BACKUP.md
```

### Incident Severity Levels

**P0 - Critical (Immediate response)**
- Production system compromised
- Active data exfiltration
- Ransomware/destructive attack
- Response time: < 15 minutes

**P1 - High (Urgent response)**
- Credentials compromised
- Unauthorized access detected
- Service disruption affecting monitoring
- Response time: < 1 hour

**P2 - Medium (Scheduled response)**
- Vulnerability discovered (not exploited)
- Configuration drift detected
- Failed authentication attempts (potential brute force)
- Response time: < 24 hours

**P3 - Low (Normal response)**
- Security scan findings
- Certificate expiration warnings
- Non-critical updates available
- Response time: < 1 week

## Security Contacts

**Primary Contact:**
- Name: [Your Name]
- Email: [your.email@example.com]
- Phone: [Your phone]
- Telegram: [Your Telegram handle]

**Escalation:**
- Manager: [Manager Name]
- Email: [manager.email@example.com]
- Phone: [Manager phone]

**Vendor Support:**
- Grafana: https://grafana.com/support
- Netdata: https://www.netdata.cloud/support
- Docker: https://support.docker.com

## Security Monitoring

### Automated Monitoring (Future Enhancement)

**Metrics to monitor:**
- Failed authentication attempts (> 5 per hour)
- Unusual network traffic patterns
- Container restart frequency
- Disk space usage (potential log flooding)
- CPU spikes (potential cryptomining)

**Alerting rules (Grafana):**
```yaml
# Example Grafana alert rule
groups:
  - name: security_alerts
    interval: 1m
    rules:
      - alert: MultipleFailedLogins
        expr: rate(grafana_api_login_attempts_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Multiple failed login attempts detected"
          description: "{{ $value }} failed logins per second in the last 5 minutes"
```

**Log monitoring patterns:**
```bash
# Monitor for security events
docker logs oci-grafana -f | grep -i "unauthorized\|forbidden\|invalid\|failed"
docker logs oci-ntfy -f | grep -i "denied\|forbidden"
docker logs infrastructure_files-caddy-1 -f | grep "401\|403"
```

### Manual Security Audit (Monthly)

**Checklist:**

```bash
# 1. Check for exposed ports
sudo netstat -tuln | grep LISTEN
# Should only see: 22 (SSH), 443 (HTTPS), 80 (HTTP redirect)

# 2. Check running containers
docker ps
# Verify all expected containers running, no unexpected ones

# 3. Check Docker images for vulnerabilities
docker images
# Note versions, check for security advisories

# 4. Review user access
# Grafana users
docker exec oci-grafana grafana-cli admin users-list

# ntfy users (if ACLs enabled)
docker exec oci-ntfy ntfy user list

# 5. Check SSL certificate expiration
echo | openssl s_client -servername monitor.qubix.space -connect monitor.qubix.space:443 2>/dev/null | openssl x509 -noout -dates

# 6. Review logs for anomalies
docker compose logs --since 24h | grep -iE "error|warning|unauthorized|denied" | less

# 7. Verify backups are current
ls -lh ~/backups/monitoring/
# Check latest backup date

# 8. Test recovery procedures
# Follow BACKUP.md verification section
```

## Resources

### Official Documentation
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Grafana Security Documentation](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/)
- [Netdata Security](https://learn.netdata.cloud/docs/security-and-privacy)
- [Caddy Security](https://caddyserver.com/docs/security)
- [ntfy Security](https://ntfy.sh/docs/config/#security)

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Tools
- [Docker Bench Security](https://github.com/docker/docker-bench-security)
- [Trivy - Container Vulnerability Scanner](https://github.com/aquasecurity/trivy)
- [Lynis - Security Auditing Tool](https://cisofy.com/lynis/)

### Training
- [Docker Security Course](https://training.docker.com/docker-security)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

## Compliance Notes

### Data Privacy
- Monitoring data (metrics, logs) is ephemeral (24-hour retention)
- No personally identifiable information (PII) is collected
- All data stays on your server (no external services)
- Logs may contain IP addresses (consider anonymization)

### Access Control
- Principle of least privilege applied
- Docker socket access limited to read-only where possible
- Service accounts for automated systems only
- Regular access reviews (quarterly)

### Audit Requirements
- Authentication events logged (Grafana, ntfy)
- Access logs available (Caddy, containers)
- 24-hour log retention (extend if compliance required)
- Backup audit trail (see BACKUP.md)

### Encryption
- Data in transit: HTTPS/TLS for all external access
- Data at rest: Consider encrypting Docker volumes (future)
- Backups: GPG encryption for sensitive files (.env)
- Secrets: Migrate to Docker secrets (encrypted at rest)
