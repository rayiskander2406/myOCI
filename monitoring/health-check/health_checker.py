#!/usr/bin/env python3
"""
Infrastructure Health Checker
Calculates health score and sends heartbeat to Telegram via ntfy

Author: Claude Code
Version: 1.0 MVP
Created: 2025-11-24
"""

import docker
import yaml
import requests
import time
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class HealthChecker:
    def __init__(self, config_path: str = "config.yml"):
        """Initialize health checker with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.docker_client = docker.from_env()
        self.score = 100
        self.issues = []
        self.details = {}

    def check_containers(self) -> None:
        """Check container health status"""
        all_containers = {**{c['name']: ('critical', c) for c in self.config['containers']['critical']},
                         **{c['name']: ('standard', c) for c in self.config['containers']['standard']}}

        for container_name, (priority, container_config) in all_containers.items():
            try:
                container = self.docker_client.containers.get(container_name)

                # Check if container is running
                if container.status != 'running':
                    penalty = container_config['penalty_down']
                    self.score -= penalty
                    self.issues.append({
                        'severity': 'critical',
                        'component': container_config['display'],
                        'issue': f"Container not running (status: {container.status})",
                        'penalty': penalty
                    })

                # Check for recent restarts
                if self.config['restart_detection']['enabled']:
                    self._check_container_restarts(container, container_config)

            except docker.errors.NotFound:
                penalty = container_config['penalty_down']
                self.score -= penalty
                self.issues.append({
                    'severity': 'critical',
                    'component': container_config['display'],
                    'issue': "Container not found",
                    'penalty': penalty
                })

    def _check_container_restarts(self, container, container_config) -> None:
        """Check for container restarts in configured time windows"""
        try:
            # Get container start time
            started_at = container.attrs['State']['StartedAt']
            # Parse ISO 8601 format
            started_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            now = datetime.now(started_time.tzinfo)

            # Calculate how long container has been running
            uptime_seconds = (now - started_time).total_seconds()

            recent_window = self.config['restart_detection']['recent_window']
            old_window = self.config['restart_detection']['old_window']

            # Check restart count from container stats
            restart_count = container.attrs['RestartCount']

            # If container was restarted recently (uptime < window), it counts as a restart
            if uptime_seconds < recent_window and restart_count > 0:
                penalty = self.config['restart_detection']['recent_penalty']
                self.score -= penalty
                self.issues.append({
                    'severity': 'medium',
                    'component': container_config['display'],
                    'issue': f"Restarted recently ({int(uptime_seconds/3600)}h ago)",
                    'penalty': penalty
                })
            elif uptime_seconds < old_window and restart_count > 0:
                penalty = self.config['restart_detection']['old_penalty']
                self.score -= penalty
                self.issues.append({
                    'severity': 'minor',
                    'component': container_config['display'],
                    'issue': f"Restarted in last 24h ({int(uptime_seconds/3600)}h ago)",
                    'penalty': penalty
                })
        except Exception as e:
            print(f"Warning: Could not check restart for {container_config['display']}: {e}")

    def _get_cpu_percent(self) -> float:
        """Get CPU usage percentage using shell commands"""
        try:
            # Use top to get CPU usage
            result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'Cpu(s)' in line or '%Cpu' in line:
                    # Extract idle percentage and calculate usage
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'id' in part or 'idle' in part:
                            try:
                                idle = float(parts[i-1].rstrip(','))
                                return 100.0 - idle
                            except (ValueError, IndexError):
                                pass
            return 0.0
        except Exception:
            return 0.0

    def _get_memory_percent(self) -> float:
        """Get memory usage percentage using shell commands"""
        try:
            result = subprocess.run(['free'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('Mem:'):
                    parts = line.split()
                    total = float(parts[1])
                    used = float(parts[2])
                    return (used / total) * 100.0
            return 0.0
        except Exception:
            return 0.0

    def _get_disk_percent(self, path: str) -> float:
        """Get disk usage percentage using shell commands"""
        try:
            result = subprocess.run(['df', path], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                percent_str = parts[4].rstrip('%')
                return float(percent_str)
            return 0.0
        except Exception:
            return 0.0

    def check_system_resources(self) -> None:
        """Check system resource usage"""
        # CPU check
        cpu_percent = self._get_cpu_percent()
        cpu_config = self.config['resources']['cpu']

        if cpu_percent >= cpu_config['critical_threshold']:
            penalty = cpu_config['critical_penalty']
            self.score -= penalty
            self.issues.append({
                'severity': 'critical',
                'component': 'System CPU',
                'issue': f"High CPU usage ({cpu_percent:.1f}%)",
                'penalty': penalty
            })
        elif cpu_percent >= cpu_config['warning_threshold']:
            penalty = cpu_config['warning_penalty']
            self.score -= penalty
            self.issues.append({
                'severity': 'medium',
                'component': 'System CPU',
                'issue': f"Elevated CPU usage ({cpu_percent:.1f}%)",
                'penalty': penalty
            })

        self.details['cpu_percent'] = cpu_percent

        # Memory check
        memory_percent = self._get_memory_percent()
        memory_config = self.config['resources']['memory']

        if memory_percent >= memory_config['critical_threshold']:
            penalty = memory_config['critical_penalty']
            self.score -= penalty
            self.issues.append({
                'severity': 'critical',
                'component': 'System Memory',
                'issue': f"High memory usage ({memory_percent:.1f}%)",
                'penalty': penalty
            })
        elif memory_percent >= memory_config['warning_threshold']:
            penalty = memory_config['warning_penalty']
            self.score -= penalty
            self.issues.append({
                'severity': 'medium',
                'component': 'System Memory',
                'issue': f"Elevated memory usage ({memory_percent:.1f}%)",
                'penalty': penalty
            })

        self.details['memory_percent'] = memory_percent

        # Disk check
        disk_percent = self._get_disk_percent(self.config['resources']['disk']['path'])
        disk_config = self.config['resources']['disk']

        if disk_percent >= disk_config['critical_threshold']:
            penalty = disk_config['critical_penalty']
            self.score -= penalty
            self.issues.append({
                'severity': 'critical',
                'component': 'System Disk',
                'issue': f"High disk usage ({disk_percent:.1f}%)",
                'penalty': penalty
            })
        elif disk_percent >= disk_config['warning_threshold']:
            penalty = disk_config['warning_penalty']
            self.score -= penalty
            self.issues.append({
                'severity': 'medium',
                'component': 'System Disk',
                'issue': f"Warning disk usage ({disk_percent:.1f}%)",
                'penalty': penalty
            })

        self.details['disk_percent'] = disk_percent

    def check_service_responses(self) -> None:
        """Check if services respond within acceptable time"""
        if not self.config['service_checks']['enabled']:
            return

        timeout = self.config['service_checks']['timeout']
        penalty = self.config['service_checks']['slow_response_penalty']

        for endpoint in self.config['service_checks']['endpoints']:
            try:
                start_time = time.time()
                response = requests.get(
                    endpoint['url'],
                    timeout=timeout + 1  # Give slight buffer
                )
                response_time = time.time() - start_time

                if response_time > timeout:
                    self.score -= penalty
                    self.issues.append({
                        'severity': 'minor',
                        'component': endpoint['name'],
                        'issue': f"Slow response ({response_time:.2f}s)",
                        'penalty': penalty
                    })

                # Store response time for details
                self.details[f"{endpoint['name']}_response_time"] = response_time

            except requests.exceptions.Timeout:
                self.score -= penalty * 2  # Double penalty for timeout
                self.issues.append({
                    'severity': 'medium',
                    'component': endpoint['name'],
                    'issue': f"Response timeout (>{timeout}s)",
                    'penalty': penalty * 2
                })
            except Exception as e:
                # Service might be down (already caught by container check)
                self.details[f"{endpoint['name']}_response_time"] = None

    def get_score_range(self) -> Tuple[str, str, str]:
        """Get score range info (emoji, label, range_name)"""
        score = max(0, min(100, self.score))  # Clamp to 0-100

        ranges = self.config['score_ranges']
        for range_name in ['excellent', 'good', 'fair', 'poor', 'critical']:
            if score >= ranges[range_name]['min']:
                return (
                    ranges[range_name]['emoji'],
                    ranges[range_name]['label'],
                    range_name
                )

        return ranges['critical']['emoji'], ranges['critical']['label'], 'critical'

    def format_message(self) -> str:
        """Format health score message for Telegram"""
        emoji, label, range_name = self.get_score_range()
        score = max(0, min(100, self.score))  # Clamp to 0-100

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S EET")

        # Build message
        message = f"<b>{emoji} Infrastructure Health Report</b>\n\n"
        message += f"<b>Health Score:</b> {score}/100 ({label})\n"
        message += f"<b>Period:</b> Last 12 hours\n"
        message += f"<b>Time:</b> {timestamp}\n\n"

        # System overview
        message += "<b>📊 System Overview</b>\n"
        message += f"CPU: {self.details.get('cpu_percent', 0):.1f}%\n"
        message += f"Memory: {self.details.get('memory_percent', 0):.1f}%\n"
        message += f"Disk: {self.details.get('disk_percent', 0):.1f}%\n"

        # Issues section (if any)
        if self.issues:
            message += f"\n<b>⚠️ Issues Detected ({len(self.issues)})</b>\n"

            # Sort by severity
            severity_order = {'critical': 0, 'medium': 1, 'minor': 2}
            sorted_issues = sorted(
                self.issues,
                key=lambda x: (severity_order.get(x['severity'], 3), -x['penalty'])
            )

            # Limit to max items
            max_items = self.config['notification']['max_detail_items']
            display_issues = sorted_issues[:max_items]

            for issue in display_issues:
                severity_emoji = {
                    'critical': '🔴',
                    'medium': '🟡',
                    'minor': '⚪'
                }.get(issue['severity'], '⚪')

                message += f"{severity_emoji} {issue['component']}: {issue['issue']} (-{issue['penalty']}pts)\n"

            if len(sorted_issues) > max_items:
                remaining = len(sorted_issues) - max_items
                message += f"... and {remaining} more issue(s)\n"
        else:
            message += "\n<b>✅ No Issues Detected</b>\n"
            message += "All systems operational\n"

        # Response times (if available)
        response_times = {k: v for k, v in self.details.items() if k.endswith('_response_time') and v is not None}
        if response_times and self.config['service_checks']['enabled']:
            message += "\n<b>⚡ Service Response Times</b>\n"
            for key, response_time in response_times.items():
                service_name = key.replace('_response_time', '')
                message += f"{service_name}: {response_time:.3f}s\n"

        return message

    def send_notification(self, message: str) -> None:
        """Send notification to Telegram via ntfy"""
        if not self.config['notification']['enabled']:
            print("Notifications disabled, skipping send")
            return

        try:
            ntfy_url = self.config['notification']['ntfy_url']
            ntfy_topic = self.config['notification']['ntfy_topic']

            _, label, _ = self.get_score_range()

            response = requests.post(
                f"{ntfy_url}/{ntfy_topic}",
                data=message.encode('utf-8'),
                headers={
                    'Title': f'Infrastructure Health: {label}',
                    'Priority': 'default',
                    'Tags': 'health,heartbeat'
                }
            )

            if response.status_code == 200:
                print(f"Health report sent successfully (Score: {max(0, min(100, self.score))})")
            else:
                print(f"Failed to send notification: {response.status_code}")

        except Exception as e:
            print(f"Error sending notification: {e}")

    def run_health_check(self) -> int:
        """Run complete health check and return final score"""
        print("Starting infrastructure health check...")

        try:
            print("Checking containers...")
            self.check_containers()

            print("Checking system resources...")
            self.check_system_resources()

            print("Checking service responses...")
            self.check_service_responses()

            final_score = max(0, min(100, self.score))
            print(f"\nHealth check complete. Score: {final_score}/100")
            print(f"Issues found: {len(self.issues)}")

            return final_score

        except Exception as e:
            print(f"Error during health check: {e}")
            raise

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Infrastructure Health Checker')
    parser.add_argument('--config', default='config.yml', help='Path to config file')
    parser.add_argument('--dry-run', action='store_true', help='Run checks but do not send notification')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        checker = HealthChecker(config_path=args.config)
        score = checker.run_health_check()

        message = checker.format_message()

        if args.verbose or args.dry_run:
            print("\n" + "="*50)
            print("FORMATTED MESSAGE:")
            print("="*50)
            # Print without HTML tags for readability
            import re
            clean_message = re.sub('<[^<]+?>', '', message)
            print(clean_message)
            print("="*50)

        if not args.dry_run:
            checker.send_notification(message)
        else:
            print("\nDry run - notification not sent")

        # Exit with status based on score
        if score >= 75:
            sys.exit(0)  # Good health
        elif score >= 40:
            sys.exit(1)  # Warning
        else:
            sys.exit(2)  # Critical

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(2)

if __name__ == '__main__':
    main()
