# Telegram Bot Setup Guide

Follow these steps to create a Telegram bot and get your credentials for the monitoring alerting system.

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather
3. Send the command: `/newbot`
4. Follow the prompts:
   - **Bot name**: Choose a display name (e.g., "OCI Monitoring Bot")
   - **Bot username**: Choose a unique username ending in 'bot' (e.g., "oci_cairo_monitor_bot")

5. BotFather will respond with your **bot token**. It looks like this:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   ```
   **IMPORTANT**: Save this token securely! You'll need it in Step 3.

## Step 2: Get Your Chat ID

There are two options depending on where you want to receive notifications:

### Option A: Personal Chat (Recommended)

1. Search for `@userinfobot` in Telegram
2. Start a chat and send any message
3. The bot will reply with your user information, including your **Chat ID**
4. It looks like a number: `123456789` (or negative for groups)
5. Save this Chat ID

### Option B: Group Chat

1. Create a new Telegram group
2. Add your bot to the group (search for your bot's username)
3. Make the bot an admin (optional but recommended)
4. Add `@userinfobot` to the group temporarily
5. The bot will show the group Chat ID (it will be negative, like `-987654321`)
6. Save this Chat ID
7. Remove `@userinfobot` from the group

## Step 3: Configure the Monitoring Stack

1. SSH into your server:
   ```bash
   ssh -i ~/.ssh/sshkey-netbird-private.key ubuntu@159.54.162.114
   ```

2. Navigate to the monitoring directory:
   ```bash
   cd ~/monitoring
   ```

3. Create a `.env` file with your credentials:
   ```bash
   cat > .env << 'EOF'
   TELEGRAM_BOT_TOKEN=your_bot_token_from_step_1
   TELEGRAM_CHAT_ID=your_chat_id_from_step_2
   NTFY_TOPICS=monitoring-alerts
   EOF
   ```

4. Replace `your_bot_token_from_step_1` and `your_chat_id_from_step_2` with your actual values

5. Set secure permissions on the .env file:
   ```bash
   chmod 600 .env
   ```

## Step 4: Deploy the Telegram Forwarder

The forwarder will be automatically deployed when you run:
```bash
docker compose up -d telegram-forwarder
```

Check the logs to verify it's working:
```bash
docker compose logs -f telegram-forwarder
```

You should see:
- "Starting ntfy-Telegram forwarder"
- "Telegram connection test successful"
- A test message in your Telegram chat

## Step 5: Test the Integration

Send a test notification:
```bash
curl -d "This is a test alert from OCI monitoring" \
  -H "Title: Test Alert" \
  -H "Priority: high" \
  -H "Tags: test,success" \
  http://localhost:8765/monitoring-alerts
```

You should receive this message in Telegram within seconds!

## Troubleshooting

### Bot token invalid
- Make sure you copied the entire token from BotFather
- Check for extra spaces or line breaks
- Create a new bot if needed

### Not receiving messages
1. Check that you started a chat with your bot (send `/start` to your bot)
2. If using a group, ensure the bot is a member and has permission to read messages
3. Verify Chat ID is correct (use `@userinfobot` again)
4. Check forwarder logs: `docker compose logs telegram-forwarder`

### Connection errors
- Ensure server has internet access to api.telegram.org
- Check firewall settings
- Verify DNS resolution: `ping api.telegram.org`

## Security Notes

- **Never share your bot token** - it provides full control of your bot
- Keep the `.env` file secure (it's git-ignored)
- Consider using a dedicated bot for monitoring (not shared with other services)
- Regularly rotate bot tokens for security
- For groups, make the bot admin to prevent users from removing it

## Next Steps

Once Telegram is working, proceed to configure Netdata alerts to send notifications through ntfy, which will automatically forward to Telegram!
