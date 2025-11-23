# Web Access Setup Status & Next Steps

**Date:** November 23, 2025
**Status:** ⚠️ **Configuration Complete, SSL Issue**

---

## ✅ What's Been Configured

### 1. Caddy Configuration
- ✅ **Caddyfile updated** with monitor.qubix.space and grafana.qubix.space
- ✅ **BasicAuth added** for Netdata (admin/MonitoringAdmin2025!)
- ✅ **Reverse proxy** configured for both services
- ✅ **Security headers** applied
- ✅ **Logging** enabled

### 2. DNS Configuration
- ✅ **DNS records resolving correctly**
  - monitor.qubix.space → 159.54.162.114
  - grafana.qubix.space → 159.54.162.114

### 3. Grafana Configuration
- ✅ **Root URL updated** to https://grafana.qubix.space
- ✅ **Container restarted** and running

### 4. Services Status
- ✅ **Netdata:** Running (healthy)
- ✅ **Grafana:** Running
- ✅ **Caddy:** Running

---

## ❌ Current Issue: SSL Certificate Problem

**Error:** `ERR_SSL_PROTOCOL_ERROR`

**Root Cause:** Caddy is not obtaining SSL certificates for the new domains.

### Investigation Results

1. **DNS Resolution:** ✅ Working correctly
2. **Caddy Configuration:** ✅ Syntax valid
3. **Certificate Issuance:** ❌ Not happening
4. **Logs show:** `"no certificate available for 'monitor.qubix.space'"`

---

## 🔍 Possible Causes

### 1. ACME Configuration Issue
- Caddy logs show it's using staging ACME server: `acme-staging-v02.api.letsencrypt.org`
- Staging certificates aren't trusted by browsers
- May need to configure production ACME server

### 2. Missing Email Configuration
- Let's Encrypt requires an email address
- May need to add to Caddyfile global block:
  ```
  {
      email your@email.com
  }
  ```

### 3. Rate Limiting
- Let's Encrypt has rate limits
- Might have hit limit from previous attempts
- Staging server: 30,000 registrations per IP per 3 hours
- Production: 50 certificates per registered domain per week

### 4. Docker Network Issues
- Certificates obtained inside container need proper persistence
- Check if `/root/.local/share/caddy` volume is mounted

---

## 🛠️ Recommended Next Steps

### Option 1: Add Email and Force Production ACME (Recommended)

```bash
# SSH to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Edit Caddyfile
cd /home/ubuntu/netbird/infrastructure_files
nano Caddyfile
```

**Add at the top (in global block):**
```
{
  debug
  email your@email.com  # Add this line
  servers :80,:443 {
    protocols h1 h2c h2 h3
  }
}
```

**Then restart Caddy:**
```bash
docker compose restart caddy
sleep 30
docker logs infrastructure_files-caddy-1 --tail 100 | grep -i certificate
```

### Option 2: Use Existing Working Pattern

Since `n8n.quarkos.ai` works, copy its exact pattern:

```bash
# Check how n8n certificate was obtained
docker exec infrastructure_files-caddy-1 ls -la /data/caddy/certificates/

# Compare with your new domains
docker exec infrastructure_files-caddy-1 ls -la /data/caddy/certificates/ | grep qubix
```

### Option 3: Temporary HTTP Access (Testing Only)

For immediate testing without SSL:

```bash
# Add HTTP-only blocks (temporary)
http://monitor.qubix.space {
    import security_headers
    basicauth {
        admin $2a$14$E0yNfuFAbrlvsPm67cG22.aiEgFQAnzfas8cjHaMaT/cDpvOmMCWC
    }
    reverse_proxy oci-netdata:19999
}
```

**Warning:** Not secure, only for testing!

---

## 📋 Detailed Troubleshooting Commands

### Check Current Certificates
```bash
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# List all certificates
docker exec infrastructure_files-caddy-1 ls -la /data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/

# Check certificate renewal logs
docker logs infrastructure_files-caddy-1 2>&1 | grep -i "certificate\|acme\|tls"

# Test ACME connectivity
docker exec infrastructure_files-caddy-1 wget -O- https://acme-v02.api.letsencrypt.org/directory
```

### Force Certificate Renewal
```bash
# Stop Caddy
docker compose stop caddy

# Remove certificate cache
docker exec infrastructure_files-caddy-1 rm -rf /data/caddy/certificates/*

# Start Caddy (will re-obtain all certificates)
docker compose up -d caddy

# Watch logs
docker logs infrastructure_files-caddy-1 -f
```

### Verify Caddy Configuration
```bash
# Validate Caddyfile
docker exec infrastructure_files-caddy-1 caddy validate --config /etc/caddy/Caddyfile

# Format Caddyfile
docker exec infrastructure_files-caddy-1 caddy fmt --overwrite /etc/caddy/Caddyfile

# Reload configuration
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

---

## 🎯 Working Alternatives (Right Now)

### Access via Port Forwarding
If you have SSH access, you can access the services immediately:

```bash
# On your local machine

# Netdata
ssh -i ~/.ssh/sshkey-netbird-private.key -L 19999:localhost:19999 ubuntu@159.54.162.114
# Then open: http://localhost:19999

# Grafana
ssh -i ~/.ssh/sshkey-netbird-private.key -L 3000:localhost:3000 ubuntu@159.54.162.114
# Then open: http://localhost:3000
```

### Access via NetBird VPN
If NetBird is running:

```bash
# Direct container access
http://oci-netdata:19999  # Netdata
http://oci-grafana:3000   # Grafana
```

---

## 📞 Support Information

### Files Modified
- `/home/ubuntu/netbird/infrastructure_files/Caddyfile` - Added monitor/grafana blocks
- `/home/ubuntu/monitoring/docker-compose.yml` - Updated Grafana URL

### Backup Created
- `/home/ubuntu/netbird/infrastructure_files/Caddyfile.backup.20251123-182023`

### Credentials
- **Netdata:** admin / MonitoringAdmin2025!
- **Grafana:** admin / admin (change on first login)

---

## 🚀 Expected Final Result

Once SSL is working:

**Netdata:** https://monitor.qubix.space
- Login with BasicAuth
- Real-time metrics
- 1-second updates

**Grafana:** https://grafana.qubix.space
- Grafana login page
- Datasources: Loki (logs), Netdata (metrics)
- Create custom dashboards

---

## 📝 Notes

- All configuration is correct
- Only SSL certificate issuance needs troubleshooting
- This is a common Let's Encrypt/ACME issue
- Usually resolved by adding email or waiting for rate limits

---

**Document Created:** November 23, 2025
**Last Updated:** 19:15 EET
**Next Action:** Add email to Caddyfile global block and restart
