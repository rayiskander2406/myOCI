# OCI Server Monitoring Stack - Week 1

Lightweight, battle-tested monitoring stack for OCI server in Cairo, Egypt.

## Components

- **Netdata** (v3.0): Real-time monitoring with 1-second granularity
- **Loki** (v3.0.0): Log aggregation system
- **Promtail** (v3.0.0): Log collection agent

## Quick Start

### 1. Deploy to Server

```bash
# Copy monitoring directory to server
scp -i ~/.ssh/sshkey-netbird-private.key -r monitoring ubuntu@159.54.162.114:~/

# SSH into server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Navigate to monitoring directory
cd ~/monitoring

# Start the stack
docker compose up -d
```

### 2. Access Dashboards

- **Netdata:** http://159.54.162.114:19999
- **Loki:** http://159.54.162.114:3100 (API only, no UI)

### 3. Verify Services

```bash
# Check containers are running
docker compose ps

# Check Netdata logs
docker compose logs netdata

# Check Loki is receiving logs
docker compose logs promtail
```

## Configuration

### Monitored Services (Priority 1 - Critical)
- NetBird VPN (management, dashboard, relay, signal)
- Zitadel authentication
- Caddy reverse proxy

### Monitored Services (Priority 2 - High)
- PostgreSQL database
- Coturn TURN/STUN server

### Log Retention
- **Loki:** 7 days
- **Netdata:** 14 days (configurable)

### Alerts
Netdata will alert when critical containers are down for >1 minute.

## Next Steps (Week 2)

1. Deploy ntfy notification server
2. Configure Telegram bot integration
3. Connect Netdata alerts to ntfy
4. Set up alert routing (critical/warning/info)

## Troubleshooting

### Netdata not showing Docker containers
```bash
# Verify Docker socket permissions
ls -la /var/run/docker.sock

# Restart Netdata
docker compose restart netdata
```

### Loki not receiving logs
```bash
# Check Promtail can access Docker socket
docker compose exec promtail ls -la /var/run/docker.sock

# Test Loki API
curl http://localhost:3100/ready
```

### Containers not starting
```bash
# Check logs
docker compose logs

# Verify network connectivity
docker network ls | grep monitoring
docker network ls | grep infrastructure
```

## Resource Usage

Expected overhead on OCI server:
- CPU: 5-8%
- Memory: ~372 MB
- Disk: ~1.5 GB/day (with 7-day retention = ~10GB)

## Maintenance

```bash
# Stop stack
docker compose down

# Update images
docker compose pull
docker compose up -d

# View logs
docker compose logs -f

# Remove old data
docker volume rm monitoring_loki-data
```

## Architecture

```
┌─────────────────────────────────────┐
│  Netdata (Port 19999)               │
│  - Monitors host system             │
│  - Monitors Docker containers       │
│  - Real-time metrics (1s interval)  │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  Docker Containers                  │
│  - NetBird (management, dashboard)  │
│  - Caddy, Zitadel, PostgreSQL      │
│  - Coturn, LMS Canvas              │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  Promtail                           │
│  - Collects Docker logs             │
│  - Labels by priority/service       │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  Loki (Port 3100)                   │
│  - Stores logs (7 days)             │
│  - Query with LogQL                 │
└─────────────────────────────────────┘
```

## Security Notes

- Netdata dashboard currently exposed on port 19999
- Week 2 will add Caddy reverse proxy with authentication
- Loki only accessible internally (no external port)
- All data stays on your server (no external services)
