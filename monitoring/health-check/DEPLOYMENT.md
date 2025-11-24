# Health Check Deployment Guide

**Quick reference for deploying the health check system**

## Quick Deploy (TL;DR)

```bash
cd /Users/rayiskander/myOCI/monitoring
docker compose up -d health-check
docker logs -f oci-health-check
```

Wait ~30 seconds, check Telegram for the first heartbeat! 🎉

---

## Full Deployment Process

### Prerequisites

✅ Monitoring stack deployed (ntfy, Grafana, Loki, Promtail, Netdata)
✅ Telegram bot configured with working notifications
✅ Docker and docker-compose installed

### Step 1: Review Configuration

Edit `health-check/config.yml` if needed to customize:
- Container priorities and penalties
- Resource thresholds (CPU, memory, disk)
- Score ranges
- Notification settings

**Default config is production-ready** - you can deploy as-is!

### Step 2: Build and Deploy

```bash
cd /Users/rayiskander/myOCI/monitoring

# Build the health-check image
docker compose build health-check

# Start the service
docker compose up -d health-check

# Verify it's running
docker ps | grep health-check
```

**Expected output:**
```
oci-health-check   Up 5 seconds
```

### Step 3: Monitor First Run

```bash
docker logs -f oci-health-check
```

**Expected log output (first 30 seconds):**
```
2025-11-24 15:50:00: Running infrastructure health check...
Starting infrastructure health check...
Checking containers...
Checking system resources...
Checking service responses...

Health check complete. Score: 92/100
Issues found: 2
Health report sent successfully (Score: 92)
2025-11-24 15:50:05: Health check complete. Sleeping for 12 hours...
```

### Step 4: Verify Telegram Message

Check your Telegram for a message that looks like:

```
🟢 Infrastructure Health Report

Health Score: 92/100 (Excellent)
Period: Last 12 hours
Time: 2025-11-24 15:50:00 EET

📊 System Overview
CPU: 45.2%
Memory: 62.8%
Disk: 71.3%

✅ No Issues Detected
All systems operational
```

### Step 5: Verify 12-Hour Schedule

The next heartbeat will arrive in exactly 12 hours. You can verify the schedule in the logs:

```bash
docker logs oci-health-check | grep "Sleeping for 12 hours"
```

---

## Configuration Changes

To update configuration after deployment:

```bash
# 1. Edit config file
nano /Users/rayiskander/myOCI/monitoring/health-check/config.yml

# 2. Rebuild and restart
cd /Users/rayiskander/myOCI/monitoring
docker compose build health-check
docker compose restart health-check
```

**Note**: Configuration changes require rebuild since config.yml is baked into the image.

---

## Health Check Commands

### View logs
```bash
docker logs oci-health-check
docker logs -f oci-health-check  # Follow mode
docker logs --tail 50 oci-health-check  # Last 50 lines
```

### Restart (triggers immediate check)
```bash
docker compose restart health-check
```

### Stop
```bash
docker compose stop health-check
```

### Remove
```bash
docker compose rm -f health-check
```

### Rebuild after code changes
```bash
docker compose build --no-cache health-check
docker compose up -d health-check
```

---

## Troubleshooting Deployment

### Container won't start
```bash
# Check logs
docker logs oci-health-check

# Common causes:
# - Missing dependencies in requirements.txt
# - Syntax errors in health_checker.py
# - Invalid YAML in config.yml
```

### Container crashes immediately
```bash
# Check entrypoint script permissions
docker compose run --rm health-check ls -la /app/entrypoint.sh

# Should show: -rwxr-xr-x (executable)
```

### No access to Docker socket
```bash
# Verify socket is mounted
docker inspect oci-health-check | grep -A5 "Mounts"

# Should show:
# "/var/run/docker.sock:/var/run/docker.sock:ro"
```

### Cannot reach ntfy
```bash
# Test from within container
docker compose exec health-check wget -O- http://oci-ntfy/v1/health

# Should return: {"healthy":true}
```

### Health check runs but no Telegram message
```bash
# 1. Check ntfy is running
docker ps | grep ntfy

# 2. Check telegram-forwarder is running
docker ps | grep telegram

# 3. Test ntfy → Telegram manually
curl -d "Test from deployment" http://localhost:8765/oci-info

# 4. Check forwarder logs
docker logs oci-telegram-forwarder
```

---

## Integration with Monitoring Stack

The health-check service integrates with:

1. **Docker Daemon**: Reads container status via `/var/run/docker.sock`
2. **ntfy**: Sends notifications to `oci-info` topic
3. **Monitoring Network**: Can reach all services for response time checks
4. **System Resources**: Reads CPU, memory, disk from host

### Network Topology

```
┌─────────────────────────────────────┐
│   Monitoring Network (Docker)       │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ health-check │──│   ntfy      │ │
│  └──────┬───────┘  └─────────────┘ │
│         │                           │
│         ├─── oci-netdata            │
│         ├─── oci-grafana            │
│         ├─── oci-loki               │
│         └─── oci-promtail           │
│                                     │
└─────────────────────────────────────┘
```

---

## Monitoring the Health Checker

### Add to Promtail (Optional - Future Enhancement)

Monitor health-check logs via Loki:

```yaml
# In promtail/config.yml
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      # ... existing configs ...
```

Health check logs will automatically be collected since Promtail monitors all Docker containers.

### Grafana Dashboard (Optional - Future Enhancement)

Create a panel to track health scores over time:
- Log query: `{container_name="oci-health-check"} |= "Score:"`
- Parse scores from logs
- Graph trend over days/weeks

---

## Backup and Recovery

### Backup Configuration
```bash
cp monitoring/health-check/config.yml monitoring/health-check/config.yml.backup
```

### Restore Configuration
```bash
cp monitoring/health-check/config.yml.backup monitoring/health-check/config.yml
docker compose build health-check
docker compose restart health-check
```

### Export Health Check History
Health checks don't persist history by default. To track history:
1. Parse logs: `docker logs oci-health-check | grep "Score:"`
2. Store in database (future enhancement)
3. Use Loki to query historical scores

---

## Production Checklist

- [ ] Health check container running
- [ ] Logs show successful execution
- [ ] First Telegram heartbeat received
- [ ] Score calculation verified
- [ ] All containers detected
- [ ] System resources monitored
- [ ] Service endpoints responding
- [ ] 12-hour schedule confirmed
- [ ] Monitoring stack integration working
- [ ] Configuration backed up

---

## Next Steps After Deployment

1. **Monitor first 24 hours**: Ensure two heartbeats arrive on schedule
2. **Review scoring**: Adjust config.yml if scores seem off
3. **Customize thresholds**: Fine-tune based on your infrastructure
4. **Document baselines**: Record typical scores for reference
5. **Set expectations**: Know what "normal" looks like for your stack

---

## Rollback

If you need to remove the health check:

```bash
cd /Users/rayiskander/myOCI/monitoring
docker compose stop health-check
docker compose rm -f health-check

# Optional: Remove from docker-compose.yml
# (Comment out the health-check service section)
```

---

**Deployment Status**: Ready for production ✅
**Last Updated**: 2025-11-24
**Version**: 1.0 MVP
