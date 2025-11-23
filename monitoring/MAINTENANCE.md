# Monitoring Stack Maintenance

Automated maintenance for the OCI monitoring infrastructure.

## Overview

The `maintenance.sh` script performs routine cleanup and health checks to keep the monitoring stack running efficiently.

## What It Does

1. **Docker Cleanup**
   - Removes stopped containers older than 24 hours
   - Removes dangling images older than 24 hours
   - Removes unused volumes
   - Removes build cache older than 7 days

2. **Health Checks**
   - Verifies all critical services are running
   - Reports Docker disk usage
   - Checks monitoring data volume sizes

3. **Log Management**
   - Maintains maintenance logs
   - Keeps last 10 log files for historical reference

## Automated Schedule

The script runs automatically every **Sunday at 2:00 AM EET** via cron.

```bash
# View current cron schedule
crontab -l

# Cron entry:
# 0 2 * * 0 cd /home/ubuntu/monitoring && ./maintenance.sh >> /home/ubuntu/monitoring/maintenance.log 2>&1
```

## Manual Execution

You can run maintenance manually at any time:

```bash
# SSH into the server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Navigate to monitoring directory
cd ~/monitoring

# Run maintenance script
./maintenance.sh
```

## Logs

Maintenance logs are stored in:
- **Current log:** `~/monitoring/maintenance.log`
- **Archive logs:** `~/monitoring/maintenance.log.YYYYMMDD-HHMMSS`

View recent maintenance activity:
```bash
tail -f ~/monitoring/maintenance.log
```

View all maintenance runs:
```bash
ls -lh ~/monitoring/maintenance.log.*
```

## Critical Services Monitored

The script verifies these services are running:
- `oci-netdata` - Real-time monitoring
- `oci-loki` - Log aggregation
- `oci-promtail` - Log collection
- `oci-ntfy` - Notification server
- `oci-telegram-forwarder` - Telegram integration

If any service is down, the script exits with an error code.

## Disk Space Management

### Expected Cleanup Results

Typical maintenance run frees:
- **Images:** 1-3 GB (dangling images from builds)
- **Containers:** 10-100 MB (stopped containers)
- **Build cache:** 50-200 MB (old build layers)
- **Volumes:** Minimal (only truly unused volumes)

### Monitoring Data Growth

Netdata and Loki data volumes grow over time:
- **Netdata:** ~100-500 MB per week (metrics retention: configurable)
- **Loki:** ~50-200 MB per week (log retention: 12 hours by default)

If volumes grow too large, adjust retention settings in:
- Netdata: `netdata/config/netdata.conf`
- Loki: `loki/config.yml`

## Customization

### Change Schedule

Edit the crontab:
```bash
crontab -e
```

Example schedules:
```bash
# Daily at 3 AM
0 3 * * * cd /home/ubuntu/monitoring && ./maintenance.sh

# Every Sunday at 1 AM
0 1 * * 0 cd /home/ubuntu/monitoring && ./maintenance.sh

# First day of month at 2 AM
0 2 1 * * cd /home/ubuntu/monitoring && ./maintenance.sh
```

### Adjust Cleanup Aggressiveness

Edit `maintenance.sh` and modify these filters:

**More aggressive** (remove older images):
```bash
# Remove images older than 7 days instead of 24h
docker image prune -f --filter "until=168h"
```

**Less aggressive** (keep images longer):
```bash
# Remove images older than 7 days
docker image prune -f --filter "until=168h"
```

## Troubleshooting

### Script Not Running

Check cron status:
```bash
systemctl status cron
```

Check cron logs:
```bash
grep CRON /var/log/syslog | tail -20
```

### Service Health Check Failures

If maintenance reports services are down:
```bash
# Check container status
docker ps -a

# View specific container logs
docker logs oci-netdata
docker logs oci-telegram-forwarder

# Restart monitoring stack
cd ~/monitoring
docker compose restart
```

### Disk Space Still High

After maintenance, if disk usage is still high:

1. Check what's using space:
```bash
docker system df -v
```

2. Manual aggressive cleanup (USE WITH CAUTION):
```bash
# Remove ALL unused images (not just dangling)
docker image prune -a -f

# Remove all build cache
docker builder prune -a -f
```

3. Check host filesystem:
```bash
df -h
du -sh /var/lib/docker/*
```

## Safety Notes

- The script only removes **unused** resources
- Running containers and their images are NEVER removed
- Active volumes are NEVER removed
- Build cache older than 7 days is safe to remove
- The script uses `--filter "until=24h"` to avoid removing fresh builds

## Integration with Alerts

Future enhancement: Configure the script to send a Telegram notification if:
- Maintenance completes successfully
- Services are found to be down
- Disk cleanup exceeds a threshold

To enable notifications, modify the script to use the existing ntfy integration.
