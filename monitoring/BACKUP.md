# Backup Strategy - Monitoring Stack

## What to Backup

### Critical (Must backup)
- Grafana dashboards and configuration
- Docker compose files and service configs
- Environment variables (.env)
- Loki configuration
- Promtail configuration
- Netdata configuration (custom plugins and settings)

### Optional (Nice to have)
- Grafana database (user settings, annotations)
- Maintenance logs
- Historical metrics (if long-term retention needed)

## Backup Procedures

### Manual Backup

**1. Grafana Dashboards:**
```bash
# From local machine
scp -i ~/.ssh/sshkey-netbird-private.key \
    ubuntu@159.54.162.114:~/monitoring/grafana/dashboards/*.json \
    ~/backups/monitoring/grafana-dashboards-$(date +%Y%m%d)/
```

**2. Configuration Files:**
```bash
# Backup entire monitoring directory (configs only, no data)
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && tar czf ~/monitoring-configs-$(date +%Y%m%d).tar.gz \
    --exclude="*.log" --exclude="grafana-data" --exclude="loki-data" \
    *.yml *.yaml *.conf *.sh *.md grafana/ loki/ promtail/ netdata/config/ ntfy/ telegram-forwarder/'

# Download backup
scp -i ~/.ssh/sshkey-netbird-private.key \
    ubuntu@159.54.162.114:~/monitoring-configs-$(date +%Y%m%d).tar.gz \
    ~/backups/monitoring/
```

**3. Environment Variables (encrypted):**
```bash
# Create encrypted backup of .env
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && gpg -c .env'

# Download encrypted .env
scp -i ~/.ssh/sshkey-netbird-private.key \
    ubuntu@159.54.162.114:~/monitoring/.env.gpg \
    ~/backups/monitoring/secrets/

# Clean up encrypted file on server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'rm ~/monitoring/.env.gpg'
```

**4. Grafana Database (Optional):**
```bash
# Backup Grafana persistent volume
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose stop grafana && \
    docker run --rm -v monitoring_grafana-data:/data -v $(pwd):/backup \
    alpine tar czf /backup/grafana-data-$(date +%Y%m%d).tar.gz -C /data . && \
    docker compose start grafana'

# Download backup
scp -i ~/.ssh/sshkey-netbird-private.key \
    ubuntu@159.54.162.114:~/monitoring/grafana-data-$(date +%Y%m%d).tar.gz \
    ~/backups/monitoring/
```

**5. Complete Backup Script:**
```bash
#!/bin/bash
# backup-monitoring.sh - Complete monitoring stack backup

BACKUP_DATE=$(date +%Y%m%d)
BACKUP_DIR=~/backups/monitoring/$BACKUP_DATE
SERVER="ubuntu@159.54.162.114"
SSH_KEY="~/.ssh/sshkey-netbird-private.key"

echo "Creating backup directory: $BACKUP_DIR"
mkdir -p $BACKUP_DIR/configs
mkdir -p $BACKUP_DIR/dashboards
mkdir -p $BACKUP_DIR/secrets

echo "1. Backing up Grafana dashboards..."
scp -i $SSH_KEY $SERVER:~/monitoring/grafana/dashboards/*.json $BACKUP_DIR/dashboards/

echo "2. Backing up configuration files..."
ssh -i $SSH_KEY $SERVER 'cd ~/monitoring && tar czf ~/monitoring-configs-'$BACKUP_DATE'.tar.gz \
    --exclude="*.log" --exclude="grafana-data" --exclude="loki-data" \
    *.yml *.yaml *.sh *.md grafana/ loki/ promtail/ netdata/config/ ntfy/ telegram-forwarder/'
scp -i $SSH_KEY $SERVER:~/monitoring-configs-$BACKUP_DATE.tar.gz $BACKUP_DIR/configs/
ssh -i $SSH_KEY $SERVER 'rm ~/monitoring-configs-'$BACKUP_DATE'.tar.gz'

echo "3. Backing up .env (encrypted)..."
ssh -i $SSH_KEY $SERVER 'cd ~/monitoring && gpg -c --batch --yes --passphrase-file /dev/stdin .env <<< "YourStrongPassphrase"'
scp -i $SSH_KEY $SERVER:~/monitoring/.env.gpg $BACKUP_DIR/secrets/
ssh -i $SSH_KEY $SERVER 'rm ~/monitoring/.env.gpg'

echo "4. Creating backup manifest..."
cat > $BACKUP_DIR/MANIFEST.txt <<EOF
Monitoring Stack Backup
Date: $(date)
Backup ID: $BACKUP_DATE

Contents:
- Grafana dashboards: $(ls $BACKUP_DIR/dashboards/*.json 2>/dev/null | wc -l) files
- Configuration archive: monitoring-configs-$BACKUP_DATE.tar.gz
- Encrypted .env: .env.gpg

Restore Instructions: See BACKUP.md in repository
EOF

echo "Backup completed: $BACKUP_DIR"
ls -lh $BACKUP_DIR
```

### Automated Backup (Future Enhancement - v0.2.0)

**Planned features:**
- Weekly automated backups via cron
- Encrypted off-server storage (S3, BackBlaze B2, or rsync.net)
- 30-day retention with rotation
- Backup verification and integrity checks
- Notifications on backup success/failure

## Recovery Procedures

### Restore Grafana Dashboards

```bash
# Upload dashboards to server
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/dashboards/*.json \
    ubuntu@159.54.162.114:~/monitoring/grafana/dashboards/

# Set correct permissions
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'chmod 644 ~/monitoring/grafana/dashboards/*.json'

# Restart Grafana to reload dashboards
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose restart grafana'

# Verify dashboards loaded
# Visit: https://grafana.qubix.space
```

### Restore Configuration Files

```bash
# Upload configuration backup
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/configs/monitoring-configs-YYYYMMDD.tar.gz \
    ubuntu@159.54.162.114:~/

# Extract backup
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~ && tar xzf monitoring-configs-YYYYMMDD.tar.gz && rm monitoring-configs-YYYYMMDD.tar.gz'

# Restart services to apply new configuration
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose down && docker compose up -d'

# Verify services started
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'docker ps | grep -E "loki|grafana|promtail|netdata|ntfy|telegram"'
```

### Restore Environment Variables

```bash
# Upload encrypted .env
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/secrets/.env.gpg \
    ubuntu@159.54.162.114:~/monitoring/

# Decrypt .env (you'll be prompted for passphrase)
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && gpg -d .env.gpg > .env && rm .env.gpg'

# Set correct permissions
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'chmod 600 ~/monitoring/.env'

# Restart services that use .env
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose restart telegram-forwarder grafana'
```

### Restore Grafana Database (Optional)

```bash
# Upload database backup
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/grafana-data-YYYYMMDD.tar.gz \
    ubuntu@159.54.162.114:~/monitoring/

# Stop Grafana
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose stop grafana'

# Restore volume data
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker run --rm -v monitoring_grafana-data:/data -v $(pwd):/backup \
    alpine sh -c "cd /data && rm -rf * && tar xzf /backup/grafana-data-YYYYMMDD.tar.gz"'

# Start Grafana
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose start grafana'

# Verify Grafana running
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'docker ps | grep grafana && curl -s http://localhost:3000/api/health'
```

### Full Disaster Recovery

**Scenario:** Complete server loss, need to restore monitoring stack from scratch.

**Prerequisites:**
- Fresh Ubuntu server with Docker and Docker Compose installed
- SSH access to new server
- Git repository access
- Backup files available locally

**Steps:**

```bash
# 1. Clone repository on new server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@NEW_SERVER_IP \
    'git clone https://github.com/rayiskander2406/myOCI.git && cd myOCI/monitoring'

# 2. Upload configuration backup
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/configs/monitoring-configs-YYYYMMDD.tar.gz \
    ubuntu@NEW_SERVER_IP:~/myOCI/monitoring/

# 3. Extract configurations
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@NEW_SERVER_IP \
    'cd ~/myOCI/monitoring && tar xzf monitoring-configs-YYYYMMDD.tar.gz --strip-components=1'

# 4. Restore .env (decrypt)
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/secrets/.env.gpg \
    ubuntu@NEW_SERVER_IP:~/myOCI/monitoring/
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@NEW_SERVER_IP \
    'cd ~/myOCI/monitoring && gpg -d .env.gpg > .env && rm .env.gpg && chmod 600 .env'

# 5. Restore Grafana dashboards
scp -i ~/.ssh/sshkey-netbird-private.key \
    ~/backups/monitoring/YYYYMMDD/dashboards/*.json \
    ubuntu@NEW_SERVER_IP:~/myOCI/monitoring/grafana/dashboards/

# 6. Deploy monitoring stack
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@NEW_SERVER_IP \
    'cd ~/myOCI/monitoring && docker compose up -d'

# 7. Wait for services to start (60 seconds)
sleep 60

# 8. Verify all services running
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@NEW_SERVER_IP \
    'docker ps | grep -E "netdata|loki|promtail|grafana|ntfy|telegram"'

# 9. Test critical endpoints
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@NEW_SERVER_IP \
    'curl -s http://localhost:3100/ready && \
     curl -s http://localhost:3000/api/health && \
     curl -s http://localhost:8765/v1/health'

# 10. Verify dashboards accessible via web
# Visit: https://monitor.qubix.space (Netdata)
# Visit: https://grafana.qubix.space (Grafana)
# Visit: https://notify.qubix.space (ntfy)
```

## Backup Schedule

| Item | Frequency | Retention | Method | Priority |
|------|-----------|-----------|--------|----------|
| Grafana Dashboards | On change | Indefinite | Git + Manual backup | Critical |
| Configurations | On change | Indefinite | Git repository | Critical |
| .env (encrypted) | Weekly | 4 weeks | Manual backup | High |
| Grafana database | Weekly | 4 weeks | Docker volume backup | Medium |
| Maintenance logs | Monthly | 3 months | Manual archive | Low |

**Recommended Schedule:**
- **Daily**: Git commits for configuration changes (automated or manual)
- **Weekly**: Full configuration + .env backup (Sunday 3 AM, after maintenance)
- **Monthly**: Verification of backup integrity and test restore

## Backup Verification

### Monthly Verification Checklist

**First Sunday of each month:**

```bash
# 1. Verify backup files exist
ls -lh ~/backups/monitoring/$(date +%Y%m)*/

# 2. Verify backup files not corrupted
cd ~/backups/monitoring/LATEST_BACKUP/
tar tzf configs/monitoring-configs-*.tar.gz > /dev/null && echo "✓ Config archive OK"
gpg --list-packets secrets/.env.gpg > /dev/null 2>&1 && echo "✓ Encrypted .env OK"
ls dashboards/*.json | wc -l && echo "dashboard files found"

# 3. Test decryption (without actually decrypting)
gpg --dry-run -d secrets/.env.gpg && echo "✓ Can decrypt .env"

# 4. Verify git repository has latest configs
cd ~/myOCI
git log --oneline -5
git status

# 5. Document verification results
cat >> ~/backups/VERIFICATION_LOG.txt <<EOF
$(date): Backup verification completed
- Config archive: OK
- Encrypted .env: OK
- Dashboard files: $(ls dashboards/*.json 2>/dev/null | wc -l)
- Git repository: Up to date
EOF
```

**Quarterly Full Restore Test** (every 3 months):
- Spin up local Docker environment
- Perform full restore from backup
- Verify all services start correctly
- Verify dashboards load with correct data sources
- Verify notifications work
- Document any issues and update procedures

## Backup Storage Recommendations

### Primary Backup Location
- **Local machine**: `~/backups/monitoring/`
- **Retention**: Keep last 12 weekly backups (3 months)
- **Encryption**: .env files encrypted, configs in plain text
- **Access**: Restricted to user account only (`chmod 700 ~/backups`)

### Secondary Backup Location (Recommended)
- **External drive**: Weekly copy to encrypted external drive
- **Cloud storage**: Encrypted upload to S3/BackBlaze B2 (future)
- **Off-site**: Physical backup at different location (monthly)

### Backup Security
```bash
# Set restrictive permissions on backup directory
chmod 700 ~/backups/monitoring
chmod 600 ~/backups/monitoring/*/secrets/.env.gpg

# Use strong GPG passphrase for .env encryption
# Store passphrase in password manager (1Password, Bitwarden, etc.)

# Verify no sensitive data in unencrypted backups
grep -r "TELEGRAM_BOT_TOKEN\|TELEGRAM_CHAT_ID" ~/backups/monitoring/*/configs/ && echo "⚠️  LEAK DETECTED"
```

## Important Notes

### What Gets Backed Up
✅ All configuration files (docker-compose.yml, Loki config, Promtail config, etc.)
✅ Grafana dashboards (JSON files)
✅ Environment variables (encrypted)
✅ Custom scripts (maintenance.sh, etc.)
✅ Documentation files

### What Does NOT Get Backed Up
❌ Monitoring data (metrics, logs) - ephemeral with 24h retention
❌ Docker images - pulled from Docker Hub on restore
❌ Docker volumes (except Grafana database if needed)
❌ Temporary files, cache, logs

### Key Principles
1. **Git is the primary backup** for all configurations
2. Monitoring data (metrics, logs) is ephemeral (24-hour retention)
3. Focus backups on configurations, not data
4. Keep encrypted .env backups separate from configs
5. Test restore procedures quarterly
6. Never commit .env or secrets to git
7. Always verify backups after creation

### Backup Before Major Changes
Always create a backup before:
- Upgrading Docker images
- Changing Loki/Promtail configurations
- Modifying docker-compose.yml
- Updating Grafana dashboards
- Rotating credentials

### Recovery Time Objectives (RTO)
- **Grafana dashboards**: < 5 minutes
- **Configuration files**: < 10 minutes
- **Full stack restore**: < 30 minutes
- **Complete disaster recovery**: < 2 hours (excluding server setup)

## Troubleshooting

### Backup Issues

**Issue: gpg encryption fails**
```bash
# Check gpg installed
which gpg

# Test encryption with simple file
echo "test" | gpg -c > test.gpg && echo "✓ GPG works"
```

**Issue: scp transfer fails**
```bash
# Test SSH connection first
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 'echo "SSH OK"'

# Check file permissions on server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 'ls -la ~/monitoring/.env'
```

**Issue: Tar archive corrupted**
```bash
# Test archive integrity
tar tzf monitoring-configs-YYYYMMDD.tar.gz > /dev/null

# Re-create archive if corrupted
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && tar czf ~/monitoring-configs-$(date +%Y%m%d).tar.gz *.yml *.yaml'
```

### Restore Issues

**Issue: Grafana dashboards not loading after restore**
```bash
# Check file permissions
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'ls -la ~/monitoring/grafana/dashboards/'

# Should be readable by all: -rw-r--r--
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'chmod 644 ~/monitoring/grafana/dashboards/*.json'

# Check Grafana logs for provisioning errors
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'docker logs oci-grafana | grep -i "provisioning\|dashboard"'
```

**Issue: .env decryption fails**
```bash
# Ensure you're using the correct passphrase
# Try decrypting to stdout first
gpg -d .env.gpg

# If successful, then decrypt to file
gpg -d .env.gpg > .env
```

**Issue: Services fail to start after restore**
```bash
# Check docker compose configuration is valid
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose config'

# Check service logs
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && docker compose logs'

# Verify .env file is present and has correct values
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 \
    'cd ~/monitoring && grep -E "TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID" .env | wc -l'
# Should output: 2
```

## Future Enhancements (v0.2.0)

### Automated Backup Script
- Scheduled via cron (Sunday 3 AM, after maintenance)
- Uploads to encrypted cloud storage (S3, BackBlaze B2)
- Sends notification on completion/failure
- Automatic retention management (keep last 12 backups)

### Backup Monitoring
- Track backup size over time
- Alert if backup fails
- Alert if backup size changes significantly
- Dashboard showing backup status

### Advanced Recovery
- Automated restore script
- Terraform/Ansible for infrastructure-as-code
- Blue-green deployment for zero-downtime updates
- Database replication for high availability
