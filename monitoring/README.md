# OCI Server Monitoring Stack - v0.1.0

Comprehensive monitoring, logging, and alerting stack for OCI server in Cairo, Egypt.

## Components

### Monitoring & Metrics
- **Netdata** (latest): Real-time monitoring with 1-second granularity
- **Grafana** (11.0.0): Visualization platform with pre-built dashboards

### Logging
- **Loki** (2.9.3): Log aggregation system with 24-hour retention
- **Promtail** (2.9.3): Log collection agent with priority-based labels

### Alerting & Notifications
- **ntfy** (latest): Notification delivery server
- **Telegram Forwarder** (Python 3.9): Automated alert forwarding to Telegram

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

###  2. Configure Environment Variables

**Required for Telegram Integration:**

Create a `.env` file in the `~/monitoring` directory on your server:

```bash
# On the server
cd ~/monitoring
nano .env
```

Add the following variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Getting Telegram Credentials:**

1. **Create a Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow the prompts
   - Copy the bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID:**
   - Start a chat with your new bot
   - Send any message to the bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your `chat_id` in the response (it's a number like `-1001234567890`)

3. **Secure the `.env` file:**
   ```bash
   chmod 600 .env
   ```

**Security Warning:** Never commit the `.env` file to git. The `.gitignore` should already exclude it.

### 3. Access Dashboards

- **Netdata:** https://monitor.qubix.space (HTTPS via Caddy, auth required)
- **Grafana:** https://grafana.qubix.space (HTTPS via Caddy, login: admin/admin)
- **ntfy:** https://notify.qubix.space (HTTPS via Caddy)
- **Loki:** http://localhost:3100 (Internal API only, no UI)

### 4. Verify Services

```bash
# Check all containers are running
docker compose ps

# Check Grafana is working
docker compose logs grafana

# Check Telegram forwarder is running
docker compose logs telegram-forwarder

# Verify Loki is receiving logs
docker compose logs promtail | grep "Successfully sent batch"
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
- **Loki:** 24 hours (optimized for performance)
- **Netdata:** 14 days (configurable)
- **Grafana Dashboards:** Optimized for 10-minute time ranges

### Grafana Dashboards
Six pre-configured dashboards available at https://grafana.qubix.space:
1. **System Health** - Container and log monitoring overview
2. **Container Details** - Deep dive into individual containers
3. **Error Tracking** - System-wide error analysis
4. **System Overview** - Comprehensive system status
5. **Logs Explorer** - Interactive log exploration
6. **Container Monitoring** - Multi-container performance

See `DASHBOARDS_GUIDE.md` for detailed usage instructions.

### Alerts & Notifications
- **Netdata** alerts on critical container failures (>1 minute downtime)
- **Telegram** forwarding for critical/high priority alerts
- **ntfy** server for notification delivery

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_CHAT_ID` | Yes | Your Telegram chat ID | `-1001234567890` |

**Important:** Store these in `~/monitoring/.env` file on the server. Never commit to git.

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
