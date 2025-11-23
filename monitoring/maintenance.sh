#!/bin/bash
#
# OCI Monitoring Stack Maintenance Script
# Performs routine cleanup and maintenance tasks
#
# Usage: ./maintenance.sh
# Recommended: Run weekly via cron
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/maintenance.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Starting monitoring stack maintenance"
log "========================================="

# 1. Docker System Cleanup
log "Cleaning up Docker resources..."

# Remove unused containers (stopped for more than 24 hours)
log "  - Removing stopped containers older than 24h"
docker container prune -f --filter "until=24h" 2>&1 | tee -a "$LOG_FILE"

# Remove unused images (not used by any container, older than 24 hours)
log "  - Removing dangling images older than 24h"
docker image prune -f --filter "until=24h" 2>&1 | tee -a "$LOG_FILE"

# Remove unused volumes (not used by any container)
log "  - Removing unused volumes"
docker volume prune -f 2>&1 | tee -a "$LOG_FILE"

# Remove build cache older than 7 days
log "  - Removing build cache older than 7 days"
docker builder prune -f --filter "until=168h" 2>&1 | tee -a "$LOG_FILE"

# 2. Show current disk usage
log "Current Docker disk usage:"
docker system df 2>&1 | tee -a "$LOG_FILE"

# 3. Check container health
log "Checking container health status..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}" 2>&1 | tee -a "$LOG_FILE"

# 4. Rotate old maintenance logs (keep last 10)
log "Rotating maintenance logs..."
if [ -f "$LOG_FILE" ]; then
    LOG_COUNT=$(ls -1 ${SCRIPT_DIR}/maintenance.log.* 2>/dev/null | wc -l)
    if [ "$LOG_COUNT" -ge 10 ]; then
        log "  - Removing old log files"
        ls -1t ${SCRIPT_DIR}/maintenance.log.* | tail -n +11 | xargs rm -f
    fi
    # Archive current log
    cp "$LOG_FILE" "${LOG_FILE}.$(date '+%Y%m%d-%H%M%S')"
fi

# 5. Check monitoring data volumes size
log "Monitoring data volumes disk usage:"
docker exec oci-netdata du -sh /var/cache/netdata /var/lib/netdata 2>&1 | tee -a "$LOG_FILE" || log "  - Could not check Netdata volumes"
docker exec oci-loki du -sh /loki 2>&1 | tee -a "$LOG_FILE" || log "  - Could not check Loki volumes"

# 6. Verify critical services are running
log "Verifying critical services..."
CRITICAL_SERVICES=("oci-netdata" "oci-loki" "oci-promtail" "oci-ntfy" "oci-telegram-forwarder")
ALL_RUNNING=true

for service in "${CRITICAL_SERVICES[@]}"; do
    if docker ps --filter "name=${service}" --filter "status=running" | grep -q "${service}"; then
        log "  ✓ ${service} is running"
    else
        log "  ✗ ${service} is NOT running - ALERT!"
        ALL_RUNNING=false
    fi
done

# 7. Summary
log "========================================="
if [ "$ALL_RUNNING" = true ]; then
    log "Maintenance completed successfully"
else
    log "Maintenance completed with WARNINGS - some services are not running"
fi
log "========================================="

# Exit with error if services are down
if [ "$ALL_RUNNING" = false ]; then
    exit 1
fi

exit 0
