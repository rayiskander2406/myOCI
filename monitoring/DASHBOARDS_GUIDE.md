# Grafana Dashboards Guide

**Created:** November 24, 2025
**Status:** ✅ Working with 24-hour Loki retention

---

## Overview

You now have **3 optimized dashboards** designed to work efficiently with the 24-hour retention policy. These dashboards use short time ranges and efficient queries to prevent performance issues.

---

## Available Dashboards

### 1. System Health
**URL:** https://grafana.qubix.space/d/system-health

**Purpose:** High-level overview of system health and container activity

**Features:**
- **Active Containers** - Count of running containers
- **Critical Alerts (5m)** - Recent critical log count
- **Log Volume (5m)** - Total log activity
- **System Status** - Online/offline indicator
- **Container Log Rate** - Log rate per container over time
- **Critical Logs Stream** - Live feed of critical logs only
- **Recent Activity** - All container logs

**Refresh:** 1 minute
**Time Range:** Last 10 minutes

---

### 2. Container Details
**URL:** https://grafana.qubix.space/d/container-details

**Purpose:** Deep dive into individual container monitoring

**Features:**
- **Container Selector** - Dropdown to choose specific container
- **Log Volume (5m)** - Log count for selected container
- **Errors (5m)** - Error count with color thresholds
- **Log Rate Over Time** - Historical log rate graph
- **Container Logs** - Full log stream for selected container
- **Errors & Warnings** - Filtered view of problems only

**Refresh:** 1 minute
**Time Range:** Last 10 minutes

**Usage:**
1. Select a container from the dropdown at the top
2. All panels automatically filter to show only that container's data

---

### 3. Error Tracking
**URL:** https://grafana.qubix.space/d/error-tracking

**Purpose:** System-wide error monitoring and analysis

**Features:**
- **Total Errors (5m)** - Errors across all containers
- **Total Warnings (5m)** - Warnings across all containers
- **Error & Warning Rate** - Trend lines over time
- **Errors by Container** - Pie chart showing error distribution
- **Error Rate by Container** - Time series per container
- **Error Logs Stream** - Live feed of all errors

**Refresh:** 1 minute
**Time Range:** Last 10 minutes

**Usage:**
- Identify which containers are producing errors
- Track error trends over time
- Quickly view recent error messages

---

## Why These Dashboards Work

### Optimizations Applied:

1. **Short Time Ranges** (10 minutes instead of hours)
   - Reduces query load on Loki
   - Prevents timeouts
   - Provides recent, actionable data

2. **Efficient Refresh Intervals** (1 minute instead of 10 seconds)
   - Less frequent queries = better performance
   - Still provides near-real-time visibility

3. **Targeted Queries**
   - Use label filters (`{job="docker"}`, `{container="..."}`)
   - Avoid full log scans
   - Leverage Loki's indexing

4. **24-Hour Retention**
   - Prevents data accumulation
   - Keeps Loki database small and fast
   - Automatic cleanup every 10 minutes

5. **Query Aggregations**
   - `count_over_time()` for counts
   - `rate()` for rates
   - `sum by (container)` for per-container metrics

---

## Dashboard Performance Tips

### Best Practices:

1. **Use appropriate time ranges**
   - Last 5-10 minutes for troubleshooting
   - Last 1-2 hours for trend analysis
   - Avoid querying beyond 6 hours

2. **Filter early, aggregate late**
   - Always use label filters first
   - Then use text search if needed
   - Aggregate at the end

3. **Use Explore for ad-hoc queries**
   - Dashboards for continuous monitoring
   - Explore for investigative work
   - See `GRAFANA_EXPLORE_GUIDE.md`

4. **Monitor dashboard performance**
   - Watch for slow loading panels
   - Adjust time ranges if needed
   - Check Loki logs for query errors

---

## Common Use Cases

### Scenario 1: Container is Down
1. Go to **System Health** dashboard
2. Check "Active Containers" count
3. Look at "Critical Logs Stream"
4. Switch to **Container Details**
5. Select the affected container
6. Review error logs

### Scenario 2: High Error Rate
1. Go to **Error Tracking** dashboard
2. Check "Errors by Container" pie chart
3. Identify problematic container
4. View "Error Logs Stream"
5. Copy error messages
6. Switch to **Container Details** for full context

### Scenario 3: Performance Investigation
1. Go to **System Health** dashboard
2. Check "Container Log Rate" graph
3. Identify containers with unusual activity
4. Switch to **Container Details**
5. Select high-activity container
6. Analyze "Log Rate Over Time"

### Scenario 4: Real-time Monitoring
1. Go to **System Health** dashboard
2. Enable auto-refresh (already set to 1m)
3. Monitor "Critical Logs Stream"
4. Watch "System Status" indicator
5. Keep open on secondary monitor

---

## Troubleshooting

### Dashboard Shows "No Data"

**Possible Causes:**
- Loki is restarting
- Promtail not sending logs
- Time range has no data

**Solutions:**
```bash
# Check Loki is running
docker ps | grep loki

# Check Promtail is running
docker ps | grep promtail

# Verify logs are flowing
curl "http://localhost:3100/loki/api/v1/label/job/values"
# Should return: ["docker", "varlogs"]

# Check recent logs exist
curl "http://localhost:3100/loki/api/v1/query?query=%7Bjob%3D%22docker%22%7D&limit=1"
```

### Dashboard is Slow

**Possible Causes:**
- Time range too large
- Too many containers logging
- Loki under load

**Solutions:**
1. Reduce time range to 5 minutes
2. Use Container Details with filter
3. Check Loki logs for errors:
```bash
docker logs oci-loki --tail 50 | grep -i error
```

### Permission Errors in Logs

**If you see dashboard loading errors:**
```bash
# Fix dashboard file permissions
chmod 644 ~/monitoring/grafana/dashboards/*.json

# Restart Grafana
cd ~/monitoring && docker compose restart grafana
```

---

## Maintenance

### Regular Tasks:

**Daily:**
- Check System Health dashboard
- Verify all containers visible
- Review error counts

**Weekly:**
- Review Error Tracking trends
- Clean up old dashboard exports
- Check Loki disk usage:
```bash
docker exec oci-loki du -sh /tmp/loki
```

**Monthly:**
- Review dashboard effectiveness
- Adjust time ranges if needed
- Update thresholds for alerts

### Backup Dashboards:

```bash
# Backup all dashboards
scp -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114:~/monitoring/grafana/dashboards/*.json ~/dashboard-backups/

# Restore dashboards
scp -i ~/.ssh/sshkey-netbird-private.key ~/dashboard-backups/*.json ubuntu@159.54.162.114:~/monitoring/grafana/dashboards/

# Restart Grafana to load
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114 'cd ~/monitoring && docker compose restart grafana'
```

---

## Comparison: Dashboards vs Explore Mode

| Feature | Dashboards | Explore Mode |
|---------|-----------|--------------|
| **Use Case** | Continuous monitoring | Ad-hoc investigation |
| **Performance** | Optimized queries | Flexible queries |
| **Learning Curve** | Easy | Requires LogQL knowledge |
| **Customization** | Fixed panels | Fully flexible |
| **Sharing** | Easy (URL) | Manual (export query) |
| **Best For** | Operations team | DevOps/Debugging |

**Recommendation:** Use dashboards for daily monitoring, Explore for troubleshooting.

---

## Next Steps

1. **Access your dashboards:**
   - Go to https://grafana.qubix.space
   - Login: `admin` / `admin`
   - Browse Dashboards menu

2. **Explore the features:**
   - Try the container selector
   - Watch the live log streams
   - Adjust time ranges

3. **Set up alerts** (optional):
   - Configure Grafana alerting
   - Set thresholds for critical metrics
   - Connect to notification channels

4. **Customize** (optional):
   - Clone existing dashboards
   - Modify queries
   - Add custom panels
   - Save as new dashboard

---

## Support

**Documentation:**
- Loki Query Language: https://grafana.com/docs/loki/latest/logql/
- Grafana Dashboards: https://grafana.com/docs/grafana/latest/dashboards/

**Your Setup:**
- Loki Retention: 24 hours
- Compaction: Every 10 minutes
- Schema: v13 (TSDB)
- Datasource UID: `P8E80F9AEF21F6940`

**Files:**
- Dashboard JSONs: `/Users/rayiskander/myOCI/monitoring/grafana/dashboards/`
- Loki Config: `/Users/rayiskander/myOCI/monitoring/loki/config.yml`
- Explore Guide: `/Users/rayiskander/myOCI/monitoring/GRAFANA_EXPLORE_GUIDE.md`

---

**Your monitoring stack is now complete and optimized!**
