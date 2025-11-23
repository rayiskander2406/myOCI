# Step-by-Step: Test Telegram Notifications

Follow these exact steps to test your Telegram notification integration.

---

## 📱 Preparation

### Before You Start

1. **Have your Telegram app open** on your phone or desktop
2. **Have a terminal ready** (Terminal on Mac/Linux, PowerShell/CMD on Windows)
3. **Your SSH key ready** at: `~/.ssh/sshkey-netbird-private.key`

**Estimated time:** 2-3 minutes

---

## 🎯 Step 1: Open Your Terminal

### On Mac
1. Press `Cmd + Space`
2. Type `terminal`
3. Press `Enter`

### On Windows
1. Press `Windows + R`
2. Type `powershell`
3. Press `Enter`

### On Linux
1. Press `Ctrl + Alt + T`
   (or use your preferred terminal)

---

## 🔐 Step 2: Connect to Your OCI Server

**Copy this command** and paste it into your terminal:

```bash
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
```

**Press Enter**

### What You'll See:

```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-1049-oracle x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

Last login: Sat Nov 23 XX:XX:XX 2025 from XXX.XXX.XXX.XXX
ubuntu@oci-server-cairo:~$
```

✅ **Success indicator:** You see `ubuntu@oci-server-cairo:~$` prompt

❌ **If you see an error:**
- `Permission denied` → Check your SSH key path
- `Connection refused` → Check server IP address
- `Host key verification failed` → Type `yes` and press Enter when asked

---

## 📂 Step 3: Navigate to Monitoring Directory

**Type this command:**

```bash
cd ~/monitoring
```

**Press Enter**

### Verify You're in the Right Place:

**Type:**
```bash
pwd
```

**Expected output:**
```
/home/ubuntu/monitoring
```

**Type:**
```bash
ls
```

**You should see:**
```
docker-compose.yml
netdata/
loki/
promtail/
ntfy/
grafana/
telegram-forwarder/
maintenance.sh
```

✅ **If you see these files, you're good to go!**

---

## 🚀 Step 4: Send Test Notification

Now for the fun part! **Copy this entire command** (it's multiple lines):

```bash
curl -H "Title: 🤖 Test from Claude Code" \
     -H "Priority: urgent" \
     -H "Tags: test,robot" \
     -d "🎉 Telegram Integration Test

Server: OCI Cairo
Time: $(date '+%Y-%m-%d %H:%M:%S EET')
Status: All systems operational

If you receive this message on Telegram, your notification pipeline is working perfectly! ✅

Sent from: OCI monitoring stack
Test ID: $(date +%s)" \
     http://localhost:8765/oci-critical
```

**Paste it into your terminal and press Enter**

### What Happens Next:

1. **Command sends** - You'll see a brief pause (1-2 seconds)
2. **ntfy receives** - The notification server gets the message
3. **Forwarder processes** - Telegram forwarder adds formatting and emojis
4. **Telegram delivers** - Your phone/app gets a push notification

### Expected Terminal Output:

```json
{"id":"abc123xyz","time":1700000000,"event":"message","topic":"oci-critical","message":"..."}
```

✅ **This means the message was sent successfully to ntfy!**

---

## 📱 Step 5: Check Your Telegram

**Within 5 seconds**, you should receive a Telegram message that looks like this:

```
🔴 Priority: URGENT

🤖 Test from Claude Code

🎉 Telegram Integration Test

Server: OCI Cairo
Time: 2025-11-23 18:XX:XX EET
Status: All systems operational

If you receive this message on Telegram, your notification pipeline is working perfectly! ✅

Sent from: OCI monitoring stack
Test ID: 1700XXXXXX

Topic: oci-critical
Time: 2025-11-23 18:XX:XX EET
```

---

## ✅ Step 6: Verify Success

### If You Received the Message:

🎉 **Congratulations!** Your Telegram integration is working perfectly!

You can now:
- Send different priority levels
- Test different topics
- Monitor your server remotely

### If You Did NOT Receive the Message:

Don't worry! Let's troubleshoot. Continue to Step 7.

---

## 🔧 Step 7: Troubleshooting (If Needed)

### Check 1: Is the Telegram Forwarder Running?

**Type:**
```bash
docker ps | grep telegram
```

**Expected output:**
```
oci-telegram-forwarder   Up X minutes
```

✅ **If you see this, forwarder is running**

❌ **If nothing appears:**
```bash
cd ~/monitoring
docker compose up -d telegram-forwarder
```

Wait 10 seconds, then try the test again (Step 4).

---

### Check 2: View Forwarder Logs

**Type:**
```bash
docker logs oci-telegram-forwarder --tail 20
```

**Look for these messages:**

✅ **Good signs:**
```
[INFO] Telegram test message sent successfully
[INFO] Subscribed to topic: oci-critical
[INFO] Received notification: {...}
[INFO] Telegram message sent successfully
```

❌ **Bad signs:**
```
[ERROR] Failed to send to Telegram
[ERROR] Connection refused
[ERROR] Invalid token
```

---

### Check 3: Verify Environment Variables

**Type:**
```bash
docker exec oci-telegram-forwarder env | grep TELEGRAM
```

**Expected output:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

❌ **If these are missing or look wrong:**

The environment variables aren't set properly. You'll need to create a `.env` file:

```bash
cd ~/monitoring
nano .env
```

Add these lines (replace with your actual values):
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Save: `Ctrl + X`, then `Y`, then `Enter`

Restart the forwarder:
```bash
docker compose restart telegram-forwarder
```

Wait 10 seconds, then try the test again (Step 4).

---

### Check 4: Test ntfy Server Directly

**Type:**
```bash
curl http://localhost:8765/v1/health
```

**Expected output:**
```json
{"healthy":true}
```

✅ **ntfy is healthy**

❌ **If you get an error:**
```bash
docker compose restart ntfy
```

---

### Check 5: Test Telegram Bot Directly

**Type this command** (replace `YOUR_BOT_TOKEN` with your actual token):

```bash
TELEGRAM_BOT_TOKEN="your_bot_token_here"
TELEGRAM_CHAT_ID="your_chat_id_here"

curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
     -d "chat_id=${TELEGRAM_CHAT_ID}" \
     -d "text=Direct API test - if you receive this, your bot credentials are correct"
```

**Did you receive this message on Telegram?**

✅ **Yes** → Bot credentials are correct, issue is with the forwarder
❌ **No** → Bot token or chat ID is incorrect

---

## 🎨 Step 8: Test Different Priority Levels (Optional)

Now that it's working, let's test all priority levels!

### Test 1: Info (Low Priority)

```bash
curl -d "ℹ️ This is an INFO level message - lowest priority" \
     http://localhost:8765/oci-info
```

**Expected emoji:** ⚪ or 🟢

---

### Test 2: Warning (Medium Priority)

```bash
curl -H "Priority: high" \
     -d "⚠️ This is a WARNING level message" \
     http://localhost:8765/oci-warning
```

**Expected emoji:** 🟠

---

### Test 3: Critical (Highest Priority)

```bash
curl -H "Priority: urgent" \
     -d "🚨 This is a CRITICAL level message - highest priority" \
     http://localhost:8765/oci-critical
```

**Expected emoji:** 🔴

---

## 🎯 Step 9: Test With Custom Formatting

**Try this fancy message:**

```bash
curl -X POST http://localhost:8765/oci-warning \
     -H "Title: 📊 System Health Check" \
     -H "Priority: high" \
     -H "Tags: health,monitoring,success" \
     -d "✅ All Services Operational

📦 Docker Containers:
  • Netdata: Running
  • Grafana: Running
  • Loki: Running
  • Promtail: Running
  • ntfy: Running
  • Telegram Forwarder: Running

💾 Resources:
  • Memory: 61% used
  • Disk: 31% used
  • CPU: <10% (monitoring overhead)

🌐 Network: Connected
⏰ Last Check: $(date '+%Y-%m-%d %H:%M:%S EET')

Everything is running smoothly! 🚀"
```

**You should receive a nicely formatted status report!**

---

## 🏁 Step 10: Clean Up and Exit

### Exit SSH Connection

**Type:**
```bash
exit
```

**Press Enter**

You'll return to your local terminal.

---

## 📊 What You've Accomplished

✅ Successfully tested Telegram notification integration
✅ Verified ntfy server is running
✅ Confirmed Telegram forwarder is working
✅ Tested different priority levels
✅ Learned how to send custom formatted messages
✅ Know how to troubleshoot common issues

---

## 🎯 Next Steps

Now that Telegram notifications are working, you can:

### 1. Set Up Web Access (Recommended Next)
- Follow `CADDY_SETUP.md` to configure HTTPS access
- Access Netdata and Grafana from anywhere
- Enable remote notifications

### 2. Configure Real Alerts
- Set up Netdata health alerts
- Connect alerts to ntfy topics
- Receive real monitoring alerts on your phone

### 3. Deploy Auto-Healing (Phase 3)
- Automatic container restarts
- Self-healing infrastructure
- Notifications when healing occurs

---

## 📞 Quick Reference Card

Save these commands for future testing:

```bash
# Connect to server
ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114

# Quick test
curl -d "Test" http://localhost:8765/oci-info

# Check forwarder logs
docker logs oci-telegram-forwarder --tail 20

# Restart forwarder
docker compose restart telegram-forwarder

# Check all containers
docker ps

# Exit SSH
exit
```

---

## 🎉 Success Message

**If you received the Telegram notification:**

Your monitoring stack is now fully operational with:
- ✅ Real-time metrics collection (Netdata)
- ✅ Log aggregation (Loki + Promtail)
- ✅ Push notifications (ntfy)
- ✅ Telegram integration (Forwarder)
- ✅ Visualization ready (Grafana)

**You're ready to monitor your OCI server like a pro!** 🚀

---

**Walkthrough Version:** 1.0
**Estimated Time:** 2-5 minutes
**Difficulty:** Beginner-friendly
**Support:** See `TEST_NOTIFICATIONS.md` for advanced testing

**Questions?** Review the troubleshooting section or check the detailed test guide.
