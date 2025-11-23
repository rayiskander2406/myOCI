# Quick Reference - Monitoring Services Web Access

## 🌐 Service URLs (After Caddy Setup)

| Service | URL | Authentication | Purpose |
|---------|-----|----------------|---------|
| **Netdata** | https://monitor.qubix.space | Caddy BasicAuth | Real-time metrics, container monitoring |
| **Grafana** | https://grafana.qubix.space | Grafana Login | Dashboards, logs visualization |
| **ntfy** | https://notify.qubix.space | None | Push notifications |

---

## 🔐 Default Credentials

### Netdata (Caddy BasicAuth)
- Username: `admin`
- Password: *Set during Caddy configuration*

### Grafana
- Username: `admin`
- Password: `admin` (⚠️ **Change immediately on first login**)

---

## ⚡ Quick Setup (TL;DR)

### 1. Add DNS Records
```
monitor.qubix.space  →  159.54.162.114
grafana.qubix.space  →  159.54.162.114
```

### 2. Generate Password Hash
```bash
docker exec infrastructure_files-caddy-1 caddy hash-password --plaintext YourPassword
```

### 3. Add to Caddyfile
Copy `monitoring/caddy/monitoring-services.Caddyfile` to server and import it.

### 4. Reload Caddy
```bash
docker exec infrastructure_files-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

### 5. Access Services
- https://monitor.qubix.space
- https://grafana.qubix.space

**Full guide:** See `CADDY_SETUP.md`

---

## 🔧 Common Commands

### Check Service Status
```bash
docker ps | grep -E "(netdata|grafana|ntfy)"
```

### View Logs
```bash
# Netdata
docker logs oci-netdata --tail 50

# Grafana
docker logs oci-grafana --tail 50

# Caddy
docker logs infrastructure_files-caddy-1 --tail 50
```

### Restart Services
```bash
cd ~/monitoring
docker compose restart netdata
docker compose restart grafana
```

### Test Connectivity from Caddy
```bash
# Test if Caddy can reach Netdata
docker exec infrastructure_files-caddy-1 wget -qO- http://oci-netdata:19999/api/v1/info

# Test if Caddy can reach Grafana
docker exec infrastructure_files-caddy-1 wget -qO- http://oci-grafana:3000/api/health
```

---

## 🐛 Troubleshooting One-Liners

### DNS not resolving?
```bash
dig monitor.qubix.space +short  # Should show: 159.54.162.114
```

### 502 Bad Gateway?
```bash
docker ps | grep netdata  # Check if container is running
docker inspect oci-netdata | grep -A 5 "Networks"  # Verify network
```

### Certificate issues?
```bash
docker logs infrastructure_files-caddy-1 2>&1 | grep -i certificate
```

### Authentication not working?
```bash
# Verify hash in Caddyfile starts with $2a$ or $2b$
grep basicauth ~/infrastructure_files/Caddyfile
```

---

## 📊 What Each Service Shows

### Netdata (monitor.qubix.space)
- **Real-time metrics** - Updated every second
- **Container monitoring** - CPU, memory, network per container
- **System health** - CPU, disk, network for entire server
- **Alerts** - Pre-configured anomaly detection
- **Custom dashboards** - Built-in, no configuration needed

**Key Sections:**
- Overview → System summary
- Applications → Docker containers
- Disks → Disk I/O and space
- Networking → Network traffic

### Grafana (grafana.qubix.space)
- **Log queries** - Search logs with LogQL (Loki datasource)
- **Custom dashboards** - Create your own visualizations
- **Metric exploration** - Query Netdata metrics
- **Alerting** - Create custom alert rules

**Pre-configured Datasources:**
- Loki (logs) - Default
- Netdata (metrics) - Prometheus format

**First Steps in Grafana:**
1. Change admin password
2. Explore → Select Loki → Run log queries
3. Create Dashboard → Add panel → Select Netdata metrics

### ntfy (notify.qubix.space)
- **Push notifications** - Subscribe to topics
- **Web interface** - View message history
- **Mobile apps** - iOS/Android apps available

**Topics:**
- `oci-critical` - Critical system alerts
- `oci-warning` - Warning notifications
- `oci-info` - Informational messages

---

## 🔒 Security Checklist

- [ ] DNS records added and propagated
- [ ] Strong password generated for Netdata
- [ ] Caddy configuration added and reloaded
- [ ] SSL certificates obtained (automatic)
- [ ] Grafana default password changed
- [ ] Test access from external network (mobile data)
- [ ] Credentials saved in password manager
- [ ] Firewall allows ports 80, 443 (should already be open)

---

## 📱 Mobile Access

### Browser Bookmarks
Add these to your mobile browser for quick access:
- Netdata: https://monitor.qubix.space
- Grafana: https://grafana.qubix.space

### ntfy Mobile App
1. Install ntfy app (iOS/Android)
2. Add server: `https://notify.qubix.space`
3. Subscribe to topics: `oci-critical`, `oci-warning`, `oci-info`
4. Enable notifications for critical alerts

---

## 💡 Pro Tips

### Netdata
- **Fullscreen mode:** Click any chart → Press `F` key
- **Jump to section:** Use search box (top right)
- **Export metrics:** Click chart → Options → Export data
- **Mobile-friendly:** Responsive design, works great on phones

### Grafana
- **Dark theme:** User menu → Preferences → UI Theme
- **Share dashboards:** Dashboard settings → Share
- **Time range shortcuts:** Top right corner (Last 6h, Last 24h, etc.)
- **Variable filters:** Use dropdown filters to focus on specific containers

### Performance
- **Netdata loads slowly?** Reduce retention in `netdata.conf`
- **Grafana slow queries?** Add time range filters
- **High bandwidth?** Access via VPN instead of public internet

---

## 🚀 Next Steps After Setup

1. **Create your first Grafana dashboard:**
   - Log query: `{priority="critical"}`
   - Metric query: Container CPU usage
   - Save and share

2. **Configure Netdata alerts:**
   - Edit `monitoring/netdata/config/health.d/*.conf`
   - Set thresholds for your use case
   - Test with simulated failures

3. **Test notification pipeline:**
   ```bash
   # Send test alert to ntfy
   curl -d "Test alert" https://notify.qubix.space/oci-critical

   # Check Telegram
   # Should receive message within 5 seconds
   ```

4. **Bookmark on all devices:**
   - Desktop browser
   - Mobile browser
   - Tablet

---

## 📞 Getting Help

### Documentation
- **This project:** `CADDY_SETUP.md` (detailed setup guide)
- **Netdata:** https://learn.netdata.cloud/
- **Grafana:** https://grafana.com/docs/grafana/latest/
- **Caddy:** https://caddyserver.com/docs/

### Common Issues
See `CADDY_SETUP.md` → Troubleshooting section

---

**Quick Reference Version:** 1.0
**Last Updated:** November 23, 2025
