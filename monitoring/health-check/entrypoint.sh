#!/bin/sh
# Health Check Entrypoint
# Runs health check every 12 hours

while true; do
    echo "$(date): Running infrastructure health check..."
    python3 /app/health_checker.py

    echo "$(date): Health check complete. Sleeping for 12 hours..."
    sleep 43200  # 12 hours in seconds
done
