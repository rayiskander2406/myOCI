# Health Check Testing Guide

**Quick testing workflow before deploying to production**

## Prerequisites

Ensure you have Python 3.11+ installed locally:
```bash
python3 --version
```

## Step 1: Install Dependencies Locally

```bash
cd /Users/rayiskander/myOCI/monitoring/health-check
pip3 install -r requirements.txt
```

## Step 2: Dry Run Test (No Notification)

This will run all checks but NOT send to Telegram:

```bash
python3 health_checker.py --dry-run --verbose
```

**Expected Output:**
```
Starting infrastructure health check...
Checking containers...
Checking system resources...
Checking service responses...

Health check complete. Score: 92/100
Issues found: 2

==================================================
FORMATTED MESSAGE:
==================================================
🟢 Infrastructure Health Report

Health Score: 92/100 (Excellent)
Period: Last 12 hours
Time: 2025-11-24 15:50:00 EET

📊 System Overview
CPU: 45.2%
Memory: 62.8%
Disk: 71.3%

... (rest of message) ...
==================================================

Dry run - notification not sent
```

## Step 3: Validate Scoring Logic

Check if the score makes sense:

1. **All systems healthy**: Should see score 90-100
2. **If a container is down**: Score should drop by the configured penalty
3. **High resource usage**: Check if penalties are applied correctly

**Customize config.yml** if needed, then re-run:
```bash
python3 health_checker.py --dry-run --verbose
```

## Step 4: Test Notification Send (Optional)

If dry-run looks good, test actual notification:

```bash
python3 health_checker.py
```

Check your Telegram for the message!

## Step 5: Verify Docker Integration

Test that the Docker container can access the Docker socket:

```bash
cd /Users/rayiskander/myOCI/monitoring
docker compose build health-check
docker compose run --rm health-check python3 /app/health_checker.py --dry-run --verbose
```

**Expected**: Same output as Step 2, confirming container has proper access.

## Step 6: Deploy to Production

Once testing passes:

```bash
cd /Users/rayiskander/myOCI/monitoring
docker compose up -d health-check
```

## Step 7: Monitor First Heartbeat

The first heartbeat will arrive within ~30 seconds of deployment, then every 12 hours.

**Watch container logs:**
```bash
docker logs -f oci-health-check
```

**Expected log output:**
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

## Troubleshooting

### Error: "Module not found"
```bash
pip3 install --upgrade -r requirements.txt
```

### Error: "Cannot connect to Docker daemon"
Make sure Docker is running:
```bash
docker ps
```

### Error: "Permission denied: /var/run/docker.sock"
The container needs read access to the Docker socket. This is configured in docker-compose.yml:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Score seems wrong
1. Review penalties in config.yml
2. Run with `--verbose` to see detailed breakdown
3. Check which containers/resources are triggering penalties

### No Telegram message
1. Verify ntfy is running: `docker ps | grep ntfy`
2. Check Telegram forwarder is running: `docker ps | grep telegram`
3. Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
4. Test ntfy directly:
   ```bash
   curl -d "Test message" http://localhost:8765/oci-info
   ```

## Quick Validation Checklist

- [ ] Dry run completes without errors
- [ ] Score calculation matches expectations
- [ ] Message format looks correct
- [ ] All containers detected properly
- [ ] System resources read correctly
- [ ] Service response times measured
- [ ] Notification sent successfully
- [ ] Telegram message received
- [ ] Container deployed and running
- [ ] Logs show 12-hour sleep cycle

## Testing Different Scenarios

### Test with container down
```bash
# Stop a container
docker stop oci-promtail

# Run health check
python3 health_checker.py --dry-run --verbose

# Should see score reduced by 10 points
# Should see "Promtail: Container not running" in issues

# Restore
docker start oci-promtail
```

### Test with high resource usage
Simulate by adjusting thresholds temporarily in config.yml:
```yaml
resources:
  cpu:
    warning_threshold: 10  # Very low - will trigger
```

Then run health check to see penalty applied.

**Remember to revert config.yml after testing!**

---

**Status**: Ready for testing ✅
**Last Updated**: 2025-11-24
