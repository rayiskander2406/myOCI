# Caddy Reverse Proxy Setup for Monitoring Services

This guide will help you configure web access to Netdata and Grafana through Caddy reverse proxy with HTTPS and authentication.

---

## Prerequisites

- Caddy reverse proxy already running (✅ confirmed)
- Domain: `qubix.space` with DNS access
- Monitoring stack deployed (Netdata, Grafana, ntfy)
- Services connected to `infrastructure_files_netbird` network (✅ confirmed)

---

## Step 1: DNS Configuration

Add these DNS records to your domain (`qubix.space`):

| Subdomain | Type | Value | TTL |
|-----------|------|-------|-----|
| `monitor` | A | `159.54.162.114` | 300 |
| `grafana` | A | `159.54.162.114` | 300 |

**Result URLs:**
- Netdata: `https://monitor.qubix.space`
- Grafana: `https://grafana.qubix.space`
- ntfy: `https://notify.qubix.space` (already configured)

**DNS Propagation:** Wait 5-10 minutes after adding records. Verify with:
```bash
dig monitor.qubix.space +short
dig grafana.qubix.space +short
```

---

## Step 2: Generate Password Hash for Netdata

Netdata doesn't have built-in authentication, so we'll use Caddy's basicauth.

### Option A: Using Caddy (Recommended)
```bash
# SSH to your server (one time only for password generation)
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Generate password hash
docker exec infrastructure_files-caddy-1 caddy hash-password --plaintext YourSecurePassword

# Example output:
# $2a$14$Zkx19XLiW6VYouLHR6y6Wef6YFQV/Z1jL8r3KQNlhGfKZCeOF8P1m
```

### Option B: Using bcrypt Online (if SSH is not available)
- Visit: https://bcrypt-generator.com/
- Enter your password
- Copy the generated hash (starts with `$2a$`)

**Save this hash** - you'll need it in the next step.

---

## Step 3: Update Caddyfile on Server

### Locate Your Caddyfile

Your Caddy configuration is likely in one of these locations:
- `/home/ubuntu/infrastructure_files/Caddyfile`
- `/home/ubuntu/infrastructure_files/caddy/Caddyfile`
- Inside Caddy container: `/etc/caddy/Caddyfile`

### Add Monitoring Services Configuration

**You have 2 options:**

#### Option A: Import Separate Config File (Recommended - Clean)

1. Copy the configuration file to your server:
   ```bash
   # From your local machine
   scp -i ~/.ssh/sshkey-netbird-private.key \
       monitoring/caddy/monitoring-services.Caddyfile \
       ubuntu@159.54.162.114:~/infrastructure_files/caddy/
   ```

2. Edit the file on the server to replace the password hash:
   ```bash
   ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
   cd ~/infrastructure_files/caddy
   nano monitoring-services.Caddyfile

   # Replace: $2a$14$REPLACE_WITH_GENERATED_HASH
   # With your actual hash from Step 2
   ```

3. Import in your main Caddyfile:
   ```bash
   nano ~/infrastructure_files/Caddyfile
   ```

   Add this line at the end:
   ```
   import caddy/monitoring-services.Caddyfile
   ```

#### Option B: Add Directly to Main Caddyfile

Open your main Caddyfile and add these entries:

```caddyfile
# Netdata - Real-time Monitoring
monitor.qubix.space {
    basicauth {
        admin $2a$14$YOUR_GENERATED_HASH_HERE
    }

    reverse_proxy oci-netdata:19999 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}

        transport http {
            read_timeout 300s
            write_timeout 300s
        }
    }

    header {
        Strict-Transport-Security "max-age=31536000"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
    }

    log {
        output file /var/log/caddy/monitor.qubix.space.log
        format json
    }
}

# Grafana - Dashboards
grafana.qubix.space {
    reverse_proxy oci-grafana:3000 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-Host {host}

        transport http {
            read_timeout 300s
            write_timeout 300s
        }
    }

    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
    }

    log {
        output file /var/log/caddy/grafana.qubix.space.log
        format json
    }
}
```

---

## Step 4: Validate Caddyfile Syntax

Before reloading, validate the configuration:

```bash
# SSH to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Validate Caddyfile
docker exec infrastructure_files-caddy-1 caddy validate --config /etc/caddy/Caddyfile

# Expected output: "Valid configuration"
```

If you see errors, fix them before proceeding.

---

## Step 5: Reload Caddy Configuration

Apply the new configuration **without downtime**:

```bash
# Graceful reload (no interruption to existing connections)
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile

# Alternative: Restart the container (brief downtime)
cd ~/infrastructure_files
docker compose restart caddy
```

**Check Caddy logs** for any errors:
```bash
docker logs infrastructure_files-caddy-1 --tail 50
```

---

## Step 6: Verify SSL Certificates

Caddy will automatically obtain Let's Encrypt SSL certificates. Check the process:

```bash
# Watch Caddy logs for certificate issuance
docker logs infrastructure_files-caddy-1 -f

# Look for messages like:
# "certificate obtained successfully"
# "serving https://monitor.qubix.space"
```

This usually takes 10-30 seconds per domain.

---

## Step 7: Test Access

### Test Netdata

1. **Open browser:** https://monitor.qubix.space
2. **Login prompt:** Enter credentials
   - Username: `admin`
   - Password: `YourSecurePassword` (from Step 2)
3. **Expected result:** Netdata dashboard loads with real-time metrics

### Test Grafana

1. **Open browser:** https://grafana.qubix.space
2. **Grafana login:** (No Caddy auth if you didn't enable it)
   - Username: `admin`
   - Password: `admin` (change on first login)
3. **Expected result:** Grafana dashboard loads

### Verify HTTPS

Check SSL certificate:
```bash
# From your local machine
curl -I https://monitor.qubix.space
curl -I https://grafana.qubix.space

# Should show: HTTP/2 200 with valid SSL
```

---

## Step 8: Update Grafana Configuration (Optional)

If you want Grafana to use the proper domain in URLs:

```bash
# Edit Grafana configuration
cd ~/monitoring
nano docker-compose.yml
```

Update the Grafana environment variables:
```yaml
grafana:
  environment:
    - GF_SERVER_ROOT_URL=https://grafana.qubix.space
    - GF_SERVER_DOMAIN=grafana.qubix.space
```

Restart Grafana:
```bash
docker compose restart grafana
```

---

## Step 9: Update Netdata Configuration (Optional)

Enable Netdata to know it's behind a proxy:

```bash
cd ~/monitoring
nano netdata/config/netdata.conf
```

Add or update:
```ini
[web]
    bind to = *
    allow connections from = localhost 172.* 10.*
    allow dashboard from = localhost 172.* 10.*
```

Restart Netdata:
```bash
docker compose restart netdata
```

---

## Security Recommendations

### 1. Strong Passwords

- **Netdata (Caddy basicauth):** Use a strong unique password
- **Grafana:** Change default `admin/admin` immediately

### 2. Additional Caddy Security (Optional)

Add IP whitelisting for extra security:

```caddyfile
monitor.qubix.space {
    @blocked not remote_ip 1.2.3.4 5.6.7.8
    abort @blocked

    # ... rest of config
}
```

Replace `1.2.3.4` with your home/office IP.

### 3. Fail2ban Integration (Advanced)

Monitor Caddy logs for failed auth attempts:
```bash
tail -f /var/log/caddy/monitor.qubix.space.log | grep "401"
```

### 4. Two-Factor Authentication

Grafana supports 2FA. Enable it:
- Settings → Authentication → Two-Factor Auth

---

## Troubleshooting

### Issue: "Cannot connect to Netdata"

**Check container connectivity:**
```bash
# Verify Netdata is on the right network
docker inspect oci-netdata | grep -A 10 Networks

# Should show both:
# - monitoring
# - infrastructure_files_netbird
```

**Fix if network is missing:**
```bash
cd ~/monitoring
docker compose down
docker compose up -d
```

### Issue: "502 Bad Gateway"

**Verify service is running:**
```bash
docker ps | grep -E "(netdata|grafana)"
docker logs oci-netdata
docker logs oci-grafana
```

**Check container names:**
```bash
# Caddy uses these container names
docker ps --format "{{.Names}}" | grep -E "(netdata|grafana)"

# Expected:
# oci-netdata
# oci-grafana
```

### Issue: "DNS not resolving"

**Check DNS propagation:**
```bash
dig monitor.qubix.space +short
nslookup monitor.qubix.space
```

Wait 5-10 minutes if records were just added.

### Issue: "Certificate error"

**Check Caddy logs:**
```bash
docker logs infrastructure_files-caddy-1 2>&1 | grep -i certificate
```

**Common causes:**
- DNS not propagated yet → Wait 10 minutes
- Port 443 not open → Check firewall
- Rate limit hit → Wait 1 hour (Let's Encrypt limit)

### Issue: "Authentication not working"

**Verify hash format:**
```bash
# Hash should start with $2a$ or $2b$
echo '$2a$14$...' # This is correct format
```

**Test with curl:**
```bash
curl -u admin:YourPassword https://monitor.qubix.space
```

---

## Access Summary

After setup, you can access:

| Service | URL | Authentication |
|---------|-----|----------------|
| **Netdata** | https://monitor.qubix.space | Caddy BasicAuth (admin/YourPassword) |
| **Grafana** | https://grafana.qubix.space | Grafana Login (admin/admin - change) |
| **ntfy** | https://notify.qubix.space | None (already configured) |

---

## Maintenance

### Update Caddy Password

```bash
# Generate new hash
docker exec infrastructure_files-caddy-1 caddy hash-password --plaintext NewPassword

# Update Caddyfile with new hash
nano ~/infrastructure_files/Caddyfile

# Reload
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

### View Access Logs

```bash
# Netdata access logs
docker exec infrastructure_files-caddy-1 cat /var/log/caddy/monitor.qubix.space.log | tail -50

# Grafana access logs
docker exec infrastructure_files-caddy-1 cat /var/log/caddy/grafana.qubix.space.log | tail -50
```

### Certificate Renewal

Caddy automatically renews certificates 30 days before expiration. No action needed!

Check certificate expiry:
```bash
echo | openssl s_client -connect monitor.qubix.space:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Next Steps

After completing this setup:

1. ✅ Save your Netdata credentials in a password manager
2. ✅ Change Grafana default password
3. ✅ Create your first Grafana dashboard
4. ✅ Configure Netdata alert thresholds
5. ✅ Test the full monitoring stack end-to-end

**Reference Documentation:**
- Caddy Reverse Proxy: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Netdata: https://learn.netdata.cloud/
- Grafana: https://grafana.com/docs/grafana/latest/

---

**Setup Guide Version:** 1.0
**Last Updated:** November 23, 2025
**Estimated Setup Time:** 15-20 minutes
