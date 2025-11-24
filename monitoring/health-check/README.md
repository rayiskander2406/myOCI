# Infrastructure Health Check System

**Version**: 1.0 MVP
**Created**: 2025-11-24
**Author**: Claude Code

## Overview

The Infrastructure Health Check system provides a **12-hour heartbeat** to Telegram with a comprehensive health score (0-100) that evaluates your infrastructure's operational status.

### Key Features

- **Configuration-Driven**: All scoring, thresholds, and penalties defined in YAML
- **Deduction-Based Scoring**: Starts at 100, deducts points for issues
- **Multi-Layer Checks**: Containers, system resources, service responses
- **Telegram Integration**: HTML-formatted messages via ntfy
- **Continuous Customization**: Edit config.yml without code changes
- **Production Ready**: Containerized, automated, fault-tolerant

## Health Score System

### Scoring Formula

```
Health Score = 100 - (Sum of all penalties)
Final Score = max(0, min(100, calculated_score))
```

### Score Ranges

| Score Range | Emoji | Label | Meaning |
|------------|-------|-------|---------|
| 90-100 | 🟢 | Excellent | All systems optimal |
| 75-89 | 🟡 | Good | Minor issues, acceptable |
| 60-74 | 🟠 | Fair | Some problems, needs attention |
| 40-59 | 🔴 | Poor | Significant issues |
| 0-39 | 🚨 | Critical | Major infrastructure problems |

## What Gets Checked

### 1. Container Health (60 points max penalty)

**Critical Containers** (20 points each):
- Loki (log aggregation)
- Grafana (visualization)
- ntfy (notifications)

**Standard Containers** (10 points each):
- Netdata (monitoring)
- Promtail (log collection)
- Telegram Forwarder

**Checks Performed**:
- ✓ Container running status
- ✓ Recent restarts (last 12 hours: -5pts, last 24 hours: -2pts)
- ✓ Container existence

### 2. System Resources (40 points max penalty)

**CPU Usage**:
- ≥80%: -10 points (critical)
- ≥60%: -5 points (warning)

**Memory Usage**:
- ≥85%: -10 points (critical)
- ≥70%: -5 points (warning)

**Disk Usage (/ filesystem)**:
- ≥90%: -15 points (critical)
- ≥80%: -5 points (warning)

### 3. Service Response Times (optional, ~8 points max penalty)

Tests HTTP endpoints for:
- Netdata (http://localhost:19999)
- Grafana (http://localhost:3000/api/health)
- ntfy (http://localhost:8765/v1/health)
- Loki (http://localhost:3100/ready)

**Penalties**:
- Slow response (>2s): -2 points
- Timeout: -4 points

## Configuration

All settings are in `config.yml`. Edit this file to customize the health check behavior.

### Example Customizations

**Increase CPU warning threshold:**
```yaml
resources:
  cpu:
    warning_threshold: 70  # Changed from 60
```

**Add new container to monitor:**
```yaml
containers:
  standard:
    - name: my-new-service
      display: My Service
      penalty_down: 15
      penalty_restart: 5
```

**Adjust score ranges:**
```yaml
score_ranges:
  excellent:
    min: 95  # Changed from 90 - stricter
```

**Disable service response checks:**
```yaml
service_checks:
  enabled: false
```

## Usage

### Running Locally (Testing)

**Dry run** (no notification sent):
```bash
cd monitoring/health-check
python3 health_checker.py --dry-run --verbose
```

**With config file:**
```bash
python3 health_checker.py --config custom-config.yml
```

**Production run:**
```bash
python3 health_checker.py
```

### Exit Codes

The script returns different exit codes for automation:

- `0`: Good health (score ≥75)
- `1`: Warning (score 40-74)
- `2`: Critical (score <40)

### Docker Deployment

The health checker runs automatically every 12 hours as part of the monitoring stack:

```bash
cd monitoring
docker compose up -d health-check
```

**View logs:**
```bash
docker logs -f oci-health-check
```

**Manual trigger:**
```bash
docker compose restart health-check
```

## Message Format

The Telegram message includes:

1. **Header**: Emoji + Health Score + Label
2. **Period**: "Last 12 hours"
3. **Timestamp**: Current time (EET timezone)
4. **System Overview**: CPU, Memory, Disk percentages
5. **Issues Detected**: Sorted by severity (critical → medium → minor)
   - Shows top 10 issues by default
   - Each issue includes component, description, penalty
6. **Service Response Times**: If service checks enabled

**Example Message:**
```
🟢 Infrastructure Health Report

Health Score: 92/100 (Excellent)
Period: Last 12 hours
Time: 2025-11-24 14:30:00 EET

📊 System Overview
CPU: 45.2%
Memory: 62.8%
Disk: 71.3%

✅ No Issues Detected
All systems operational

⚡ Service Response Times
Netdata: 0.123s
Grafana: 0.089s
ntfy: 0.067s
Loki: 0.145s
```

## Dependencies

- **Python 3.11+**
- **docker** (7.0.0): Docker API client
- **PyYAML** (6.0.1): Configuration parsing
- **requests** (2.31.0): HTTP requests
- **psutil** (5.9.6): System resource monitoring

## Architecture

```
┌─────────────────────────────────────────┐
│     Health Checker Container            │
│  ┌───────────────────────────────────┐  │
│  │   health_checker.py               │  │
│  │   - Reads config.yml              │  │
│  │   - Calculates score (100 base)  │  │
│  │   - Formats HTML message          │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│  ┌───────────────▼───────────────────┐  │
│  │   Checks (every 12 hours)         │  │
│  │   ├─ Docker containers (API)      │  │
│  │   ├─ System resources (psutil)    │  │
│  │   └─ Service responses (HTTP)     │  │
│  └───────────────┬───────────────────┘  │
└──────────────────┼───────────────────────┘
                   │
                   ▼
           ┌───────────────┐
           │  ntfy Server  │
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │   Telegram    │
           │   (via bot)   │
           └───────────────┘
```

## Troubleshooting

### No messages received

1. Check container logs:
   ```bash
   docker logs oci-health-check
   ```

2. Verify ntfy is running:
   ```bash
   docker ps | grep ntfy
   ```

3. Test manually:
   ```bash
   docker exec -it oci-health-check python3 /app/health_checker.py --dry-run --verbose
   ```

### Incorrect scores

1. Review config.yml penalties
2. Check which checks are triggering:
   ```bash
   docker exec -it oci-health-check python3 /app/health_checker.py --dry-run --verbose
   ```

### Container restarts not detected

Container restart detection uses Docker API `RestartCount` and `StartedAt` timestamp. Verify containers have restart policies set.

### Permission errors

The health checker needs read access to:
- Docker socket (`/var/run/docker.sock`)
- Root filesystem (for disk check)

## Customization Examples

### Scenario: Stricter CPU monitoring

```yaml
resources:
  cpu:
    critical_threshold: 70  # Down from 80
    warning_threshold: 50   # Down from 60
    critical_penalty: 15    # Up from 10
    warning_penalty: 8      # Up from 5
```

### Scenario: Add custom service check

```yaml
service_checks:
  enabled: true
  endpoints:
    - name: MyAPI
      url: http://localhost:8080/health
      method: GET
```

### Scenario: Change notification topic

```yaml
notification:
  ntfy_topic: oci-heartbeat  # Custom topic
```

### Scenario: Less verbose messages

```yaml
notification:
  max_detail_items: 5  # Show fewer issues (default: 10)
```

## Future Enhancements

Placeholders in config.yml for future versions:

- **log_analysis**: Parse Loki logs for error patterns
- **network_checks**: External connectivity tests
- **Custom metrics**: User-defined health indicators
- **Trend analysis**: Score history and degradation detection
- **Smart alerting**: Only notify on score drops

## Files

```
monitoring/health-check/
├── health_checker.py    # Main health check script (380 lines)
├── config.yml           # Configuration (all thresholds and penalties)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
├── entrypoint.sh        # 12-hour loop wrapper
└── README.md            # This file
```

## Support

- **Test**: Always use `--dry-run --verbose` before production changes
- **Logs**: `docker logs oci-health-check`
- **Config**: Edit `config.yml` and restart: `docker compose restart health-check`
- **Version**: Check script header for version info

---

**Status**: MVP Complete ✅
**Last Updated**: 2025-11-24
