#!/bin/bash
# Health Check Deployment Script
# Run this directly on your OCI server

set -e

echo "=== Health Check Deployment ==="
echo

# Navigate to health-check directory
cd "$(dirname "$0")"

echo "[1/5] Checking files..."
if [ ! -f "health_checker.py" ] || [ ! -f "config.yml" ] || [ ! -f "Dockerfile" ]; then
    echo "ERROR: Required files missing!"
    exit 1
fi
echo "✓ All files present"
echo

echo "[2/5] Building Docker image (this may take 1-2 minutes)..."
cd ..
if ! docker compose build health-check; then
    echo "ERROR: Build failed!"
    echo "Try running: docker builder prune -a -f"
    echo "Then run this script again"
    exit 1
fi
echo "✓ Build complete"
echo

echo "[3/5] Starting health-check service..."
docker compose up -d health-check
echo "✓ Service started"
echo

echo "[4/5] Waiting for first health check (30 seconds)..."
sleep 30
echo

echo "[5/5] Checking logs..."
docker logs --tail 20 oci-health-check
echo

echo "=== Deployment Complete ==="
echo
echo "Check your Telegram for the health report!"
echo
echo "Useful commands:"
echo "  - View logs: docker logs -f oci-health-check"
echo "  - Restart: docker compose restart health-check"
echo "  - Stop: docker compose stop health-check"
echo
