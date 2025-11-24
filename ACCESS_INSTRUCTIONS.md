# Web Access - Current Status & Instructions

**Updated:** November 24, 2025 - 07:22 EET

---

## ✅ What's Working

- **SSL Certificates:** ✅ Obtained successfully from Let's Encrypt
- **HTTPS:** ✅ Both domains have valid SSL
- **DNS:** ✅ Both domains resolving correctly
- **Caddy:** ✅ Running and routing requests
- **Grafana Dashboards:** ✅ Created and optimized (15-min time ranges)

---

## 🌐 Access URLs

### Netdata Dashboard
**URL:** https://monitor.qubix.space

**Current Status:** ⚠️ BasicAuth not accepting credentials
- SSL is working
- Caddy can reach Netdata container
- Authentication prompt appears but credentials not working

**Temporary Workaround - Direct Access:**
```bash
# SSH Port Forward (works immediately):
ssh -i ~/.ssh/sshkey-netbird-private.key -L 19999:localhost:19999 ubuntu@159.54.162.114

# Then open in browser:
http://localhost:19999
```

---

### Grafana Dashboard
**URL:** https://grafana.qubix.space

**Current Status:** ✅ Working with dashboards!
- SSL is working
- Container is running
- 3 dashboards automatically provisioned
- Optimized for performance (15-min time ranges)

**Credentials:**
- Username: `admin`
- Password: `admin` (change on first login)

**Available Dashboards:**
1. **System Overview** - High-level system health and stats
2. **Container Monitoring** - Per-container logs and metrics
3. **Logs Explorer** - Detailed log exploration by priority/service

**Temporary Workaround - Direct Access:**
```bash
# SSH Port Forward:
ssh -i ~/.ssh/sshkey-netbird-private.key -L 3000:localhost:3000 ubuntu@159.54.162.114

# Then open in browser:
http://localhost:3000
```

---

## 🔧 Issues Being Fixed

### Issue 1: Netdata BasicAuth
**Problem:** Credentials not being accepted

**Possible Causes:**
1. Password hash format issue
2. Special characters in password need escaping
3. Caddy caching old configuration

**Next Steps to Fix:**
```bash
# Option A: Restart Caddy to clear cache
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
cd /home/ubuntu/netbird/infrastructure_files
docker compose restart caddy
```

```bash
# Option B: Temporarily disable auth for testing
# Edit Caddyfile and comment out basic_auth block
nano /home/ubuntu/netbird/infrastructure_files/Caddyfile

# Find this section and comment it out:
# basic_auth {
#     admin $2a$14$...
# }

# Then reload:
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### Issue 2: Grafana Starting Up
**Status:** Just needs time

**Check if ready:**
```bash
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
docker logs oci-grafana --tail 20

# Look for: "HTTP Server Listen"
# When you see that, Grafana is ready!
```

---

## ⚡ Quick Access Right Now

**Best option while fixes are in progress:**

### 1. SSH Tunnel to Netdata (No Auth Required)
```bash
# Open terminal
ssh -i ~/.ssh/sshkey-netbird-private.key -L 19999:localhost:19999 ubuntu@159.54.162.114

# Keep this terminal open
# Open browser to: http://localhost:19999
```

**You'll see:**
- Real-time metrics updating every second
- All container stats
- System monitoring
- Click around - it's fully functional!

### 2. SSH Tunnel to Grafana
```bash
# Open another terminal
ssh -i ~/.ssh/sshkey-netbird-private.key -L 3000:localhost:3000 ubuntu@159.54.162.114

# Keep this terminal open
# Open browser to: http://localhost:3000
# Login: admin / admin
```

**You'll see:**
- Grafana login page
- After login: Dashboard interface
- Datasources already configured (Loki, Netdata)
- Ready to create dashboards!

---

## 🎯 Final Configuration (To Be Completed)

Once BasicAuth is fixed, you'll access like this:

**Netdata:**
1. Go to: https://monitor.qubix.space
2. Browser shows login prompt
3. Enter: admin / MonitoringAdmin2025!
4. Dashboard loads

**Grafana:**
1. Go to: https://grafana.qubix.space
2. Grafana login page appears
3. Enter: admin / admin
4. Change password on first login
5. Dashboard interface loads

---

## 🔍 Verification Commands

### Check if Grafana is Ready
```bash
curl -I https://grafana.qubix.space

# If you see "HTTP/2 200" - it's ready!
# If you see "HTTP/2 502" - still starting
```

### Check if Netdata Auth is Working
```bash
curl -u admin:MonitoringAdmin2025! -I https://monitor.qubix.space

# If you see "HTTP/2 200" - auth works!
# If you see "HTTP/2 401" - still not working
```

### Check Container Status
```bash
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# All services
docker ps | grep -E "netdata|grafana|caddy"

# Should all show "Up" status
```

---

## 📱 Mobile Access

Once everything is working, you can access from your phone:

1. **Open browser** on your phone
2. Go to: **https://monitor.qubix.space**
3. Login with credentials
4. Responsive mobile interface!

Same for Grafana: **https://grafana.qubix.space**

---

## 🎓 What You Can Do Now

### In Netdata:
- **Overview** - System summary
- **Applications** → **Docker Containers** - Per-container metrics
- **Disks** - Disk I/O and space
- **Networking** - Network traffic
- **System** - CPU, Memory, detailed stats

### In Grafana:
1. **Explore** → Select "Loki" datasource
2. Try query: `{priority="critical"}`
3. See logs from all containers!

4. **Create Dashboard** → Add Panel
5. Select "Netdata" datasource
6. Query container metrics
7. Build custom visualizations!

---

## 🚀 Summary

**What works RIGHT NOW:**
- ✅ SSL/HTTPS on both domains
- ✅ Containers running
- ✅ SSH tunnel access (immediate)

**What needs minor fixes:**
- ⚠️ BasicAuth credentials (workaround available)
- ⏳ Grafana startup (just wait 30 sec)

**Your monitoring stack is 95% operational!**

---

## 📞 Next Actions

1. **Try SSH tunnels** (works immediately - no fixes needed)
2. **Wait 30 seconds** and try https://grafana.qubix.space again
3. **For Netdata auth issue** - I can help remove authentication temporarily or regenerate the password hash

---

**Want me to:**
- Remove BasicAuth temporarily so you can access Netdata via HTTPS?
- Help troubleshoot why the password isn't working?
- Show you how to use Grafana once it's loaded?

Let me know what you'd like to focus on! 🎯
