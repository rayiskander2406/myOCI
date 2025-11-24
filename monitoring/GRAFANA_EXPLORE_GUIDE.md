# Grafana Explore Mode - Quick Guide

**Updated:** November 24, 2025

Now that dashboards are removed and Loki has 24-hour retention configured, use **Explore mode** for on-demand log viewing.

---

## How to Access

1. Go to: **https://grafana.qubix.space**
2. Login: `admin` / `admin`
3. Click the **Explore icon** (compass) in the left sidebar
4. Select **"Loki"** from the datasource dropdown at the top

---

## Basic Queries

###  All Docker Logs
```
{job="docker"} | json
```
Shows all container logs with JSON parsing.

### Specific Container
```
{container="oci-grafana"} | json
```
Replace `oci-grafana` with any container name.

### By Priority
```
{priority="critical"} | json
```
Options: `critical`, `high`, `standard`

### Error Logs Only
```
{job="docker"} |= "error" | json
```
The `|=` filters for lines containing "error".

### Multiple Filters
```
{job="docker", container="oci-loki"} |= "level=error" | json
```
Combines label filters and text search.

---

## Time Range

Use the time picker in the top-right:
- **Last 5 minutes** - Best for real-time debugging
- **Last 1 hour** - Good for recent issues
- **Last 6 hours** - Max recommended range
- **Custom** - Pick specific start/end times

---

## Useful Features

### Live Tail
Click the **"Live"** button in the top-right to stream logs in real-time (like `tail -f`).

### Log Context
Click any log line to see:
- Full JSON fields
- Surrounding log lines
- Copy log content

### Export
Click "Inspector" → "Data" → "Download CSV" to save results.

---

## Common Use Cases

### Debug a Container Restart
```
{container="oci-loki"} | json | line_format "{{.level}} {{.msg}}"
```
Then set time range to when the restart happened.

### Find All Errors Across System
```
{job="docker"} |~ "(?i)(error|fail|exception)" | json
```
Case-insensitive regex search for error patterns.

### Monitor Critical Services
```
{priority="critical"} | json | line_format "[{{.container}}] {{.msg}}"
```
Shows all critical priority logs formatted nicely.

---

## Why This is Better Than Dashboards

1. **On-Demand** - Only queries when you need it (not perpetually loading)
2. **Flexible** - Adjust queries and time ranges instantly
3. **Performant** - Loki handles small targeted queries much better
4. **No Overhead** - Doesn't keep Loki busy with background queries

---

## Configuration Summary

Your Loki setup now has:
- **24-hour retention** - Logs older than 24h are automatically deleted
- **Compaction enabled** - Old data cleaned up every 10 minutes
- **Query limits** - Prevents overwhelming Loki with huge queries
- **Fresh start** - All old bloated data removed

This sustainable setup will perform well indefinitely!
