# Testing Telegram Notifications

Quick guide to test the ntfy → Telegram forwarder integration.

---

## ⚡ Quick Test Commands

### From the OCI Server (via SSH)

SSH into your server and run these commands to test notifications:

```bash
# SSH to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Navigate to monitoring directory
cd ~/monitoring

# Test 1: Send a simple message
curl -d "Hello from ntfy!" http://localhost:8765/oci-info

# Test 2: Send with priority and title
curl -H "Title: Test Alert" \
     -H "Priority: high" \
     -d "This is a high-priority test message" \
     http://localhost:8765/oci-warning

# Test 3: Send critical alert (with emoji and tags)
curl -H "Title: Critical Test Alert" \
     -H "Priority: urgent" \
     -H "Tags: warning,test" \
     -d "🚨 This is a CRITICAL test alert from your OCI server!

Server: OCI Cairo
Time: $(date '+%Y-%m-%d %H:%M:%S EET')
Status: Testing notification pipeline

If you receive this on Telegram, the integration is working! ✅" \
     http://localhost:8765/oci-critical

# Test 4: Full featured message
curl -X POST http://localhost:8765/oci-warning \
     -H "Title: Monitoring Stack Health Check" \
     -H "Priority: high" \
     -H "Tags: health,monitoring,test" \
     -d "📊 Monitoring Stack Status Report

✅ Netdata: Running
✅ Grafana: Running
✅ Loki: Running
✅ Promtail: Running
✅ ntfy: Running
✅ Telegram Forwarder: Running

All systems operational at $(date '+%Y-%m-%d %H:%M:%S EET')

This is an automated test message."
```

---

## 🌐 From Anywhere (After Caddy Setup)

Once you've configured the Caddy reverse proxy (see `CADDY_SETUP.md`):

```bash
# From your local machine or anywhere with internet
curl -d "Remote test message" https://notify.qubix.space/oci-info

# With authentication (if configured)
curl -u username:password \
     -d "Authenticated test" \
     https://notify.qubix.space/oci-warning

# Full example
curl -X POST https://notify.qubix.space/oci-critical \
     -H "Title: Remote Alert Test" \
     -H "Priority: urgent" \
     -H "Tags: remote,test" \
     -d "🌍 This message was sent from a remote location!

Testing external access to notification system."
```

---

## 📱 Expected Results

### On Telegram

You should receive a message formatted like this:

```
🟠 Priority: HIGH

📊 Monitoring Stack Health Check

[Your message content here]

Topic: oci-warning
Time: 2025-11-23 18:15:42 EET
```

### Priority Emoji Legend

- 🔴 **urgent** - Critical alerts
- 🟠 **high** - High priority warnings
- 🟡 **default** - Standard notifications
- 🟢 **low** - Low priority info
- ⚪ **min** - Minimal/debug messages

### Tags

Tags appear as emoji if recognized:
- `warning` → ⚠️
- `rotating_light` → 🚨
- `fire` → 🔥
- `zap` → ⚡
- etc.

---

## 🔍 Troubleshooting

### No message received on Telegram?

#### 1. Check Telegram Forwarder Status
```bash
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
docker ps | grep telegram
docker logs oci-telegram-forwarder --tail 50
```

**Expected log output:**
```
[INFO] Testing Telegram connection...
[INFO] Telegram test message sent successfully
[INFO] Subscribed to topic: oci-critical
[INFO] Subscribed to topic: oci-warning
[INFO] Subscribed to topic: oci-info
```

#### 2. Check ntfy Server
```bash
# Verify ntfy is running
docker ps | grep ntfy

# Check ntfy logs
docker logs oci-ntfy --tail 50

# Test ntfy directly
curl http://localhost:8765/v1/health
# Should return: {"healthy":true}
```

#### 3. Test ntfy Web Interface
```bash
# From the server
curl http://localhost:8765

# Should return HTML page
```

#### 4. Verify Environment Variables
```bash
cd ~/monitoring
cat .env | grep TELEGRAM

# Should show:
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id
```

If missing, create `.env` file:
```bash
cat > ~/monitoring/.env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF
```

Then restart:
```bash
docker compose restart telegram-forwarder
```

#### 5. Test Telegram Bot Directly
```bash
# Get bot info
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

# Send test message directly
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage \
     -d "chat_id=<YOUR_CHAT_ID>" \
     -d "text=Direct Telegram API test"
```

### Message received but formatting is wrong?

Check the forwarder logs:
```bash
docker logs oci-telegram-forwarder -f
```

The forwarder should show:
```
[INFO] Received notification: {...}
[INFO] Formatted message for Telegram
[INFO] Telegram message sent successfully
```

---

## 🧪 Automated Test Script

Create this script for easy testing:

```bash
#!/bin/bash
# Save as: ~/monitoring/test-telegram.sh

echo "🧪 Testing Telegram Notification Integration"
echo "=============================================="
echo ""

# Test 1: Info level
echo "1️⃣ Sending INFO message..."
curl -s -d "Test message 1: Info level" http://localhost:8765/oci-info > /dev/null
sleep 2

# Test 2: Warning level
echo "2️⃣ Sending WARNING message..."
curl -s -H "Priority: high" -d "Test message 2: Warning level" http://localhost:8765/oci-warning > /dev/null
sleep 2

# Test 3: Critical level
echo "3️⃣ Sending CRITICAL message..."
curl -s -H "Priority: urgent" -H "Title: Critical Test" \
     -d "Test message 3: Critical level 🚨" http://localhost:8765/oci-critical > /dev/null
sleep 2

echo ""
echo "✅ All test messages sent!"
echo "📱 Check your Telegram for 3 messages"
echo ""
echo "If you didn't receive them, check logs:"
echo "  docker logs oci-telegram-forwarder --tail 50"
```

Make it executable and run:
```bash
chmod +x ~/monitoring/test-telegram.sh
./test-telegram.sh
```

---

## 📊 Testing Checklist

- [ ] SSH into OCI server
- [ ] Verify all containers running (`docker ps`)
- [ ] Send test message to `oci-info` topic
- [ ] Verify message received on Telegram
- [ ] Test high priority (`oci-warning`)
- [ ] Test critical priority (`oci-critical`)
- [ ] Check message formatting (HTML, emojis)
- [ ] Verify timestamps are in EET timezone
- [ ] Test with custom title and tags
- [ ] Check logs for any errors

---

## 🎯 Success Criteria

Your Telegram integration is working correctly if:

✅ Messages arrive within 5 seconds of sending
✅ Priority emojis are correct (🔴🟠🟡🟢⚪)
✅ HTML formatting displays properly (bold, italic)
✅ Timestamps show EET timezone
✅ Topics are displayed correctly
✅ No errors in forwarder logs
✅ All priority levels work (min, low, default, high, urgent)

---

## 🔧 Advanced Testing

### Simulate Real Alerts

```bash
# Simulate container down
curl -H "Title: Container Alert" \
     -H "Priority: urgent" \
     -H "Tags: warning,docker" \
     -d "🚨 ALERT: Container 'oci-netdata' is down!

Service: Netdata Monitoring
Status: Stopped
Time: $(date '+%Y-%m-%d %H:%M:%S EET')

Action Required: Investigate immediately" \
     http://localhost:8765/oci-critical

# Simulate disk space warning
curl -H "Title: Disk Space Warning" \
     -H "Priority: high" \
     -d "⚠️ WARNING: Disk space running low

Disk: /dev/sda1
Usage: 87%
Available: 2.1 GB

Recommendation: Clean up old Docker images" \
     http://localhost:8765/oci-warning

# Simulate high memory usage
curl -H "Title: Memory Alert" \
     -H "Priority: high" \
     -d "📊 High memory usage detected

Current: 78%
Container: oci-loki
Action: Monitoring" \
     http://localhost:8765/oci-warning
```

### Load Testing

Send multiple messages:
```bash
for i in {1..10}; do
  curl -s -d "Load test message #$i" http://localhost:8765/oci-info
  sleep 1
done
```

Check if all 10 messages arrive on Telegram.

---

## 📞 Getting Help

### Check Forwarder Logs
```bash
docker logs oci-telegram-forwarder --tail 100 -f
```

### Restart Services
```bash
cd ~/monitoring
docker compose restart ntfy telegram-forwarder
```

### Verify Network Connectivity
```bash
# Can forwarder reach ntfy?
docker exec oci-telegram-forwarder wget -qO- http://oci-ntfy:8765/v1/health

# Can reach Telegram API?
docker exec oci-telegram-forwarder ping -c 3 api.telegram.org
```

---

**Test Guide Version:** 1.0
**Last Updated:** November 23, 2025

**Next:** After confirming Telegram works, proceed to `CADDY_SETUP.md` for web access configuration.
