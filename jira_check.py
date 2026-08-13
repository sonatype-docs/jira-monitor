#!/usr/bin/env python3
"""
Jira Board Monitor - Single Check
Designed to run via GitHub Actions on a schedule.
Performs one check and notifies of new tickets.
"""

import os
import json
import requests
from datetime import datetime
from typing import Set, List, Dict, Any
from pathlib import Path

# Configuration
JIRA_BASE_URL = "https://sonatype.atlassian.net"
BOARD_ID = 298
PROJECT_KEY = "SDS"
CUSTOM_FILTER_ID = 1866

# File to store known issues (will be committed back to repo)
KNOWN_ISSUES_FILE = Path(__file__).parent / "data" / "known_issues.json"
DATA_DIR = Path(__file__).parent / "data"


class JiraMonitor:
    def __init__(self, email: str, api_token: str, slack_webhook: str = None):
        self.email = email
        self.api_token = api_token
        self.slack_webhook = slack_webhook
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.known_issues: Set[str] = self._load_known_issues()

    def _load_known_issues(self) -> Set[str]:
        """Load known issue keys from storage file."""
        if KNOWN_ISSUES_FILE.exists():
            with open(KNOWN_ISSUES_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("issues", []))
        return set()

    def _save_known_issues(self) -> None:
        """Save known issue keys to storage file."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(KNOWN_ISSUES_FILE, "w") as f:
            json.dump({
                "issues": list(self.known_issues),
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)

    def get_issues_from_filter(self) -> List[Dict[str, Any]]:
        """Fetch issues from the board backlog directly."""
        # Try board API first (more reliable)
        return self.get_issues_from_board()

    def get_issues_from_board(self) -> List[Dict[str, Any]]:
        """Fallback: Fetch issues from board using Agile API."""
        url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{BOARD_ID}/issue"
        params = {
            "fields": "key,summary,status,priority,assignee,created,updated,issuetype",
            "maxResults": 100
        }

        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("issues", [])
        except Exception as e:
            print(f"Error fetching board issues: {e}")

        return []

    def detect_new_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify new issues not in known_issues, filtered by allowed prefixes."""
        # Only monitor CLM-* and NEXUS-* tickets
        ALLOWED_PREFIXES = ("CLM-", "NEXUS-")

        new_issues = []
        filtered_issues = []

        # Filter issues by allowed prefixes
        for issue in issues:
            issue_key = issue.get("key", "")
            if issue_key.startswith(ALLOWED_PREFIXES):
                filtered_issues.append(issue)

        print(f"📊 Filtered: {len(filtered_issues)} CLM/NEXUS tickets out of {len(issues)} total")

        # First run ever - populate known issues without notification
        if not self.known_issues:
            print("🆕 First run - populating known issues without notification")
            for issue in filtered_issues:
                issue_key = issue.get("key")
                if issue_key:
                    self.known_issues.add(issue_key)
            if self.known_issues:
                self._save_known_issues()
            return []  # Return empty to avoid flooding notifications

        # Subsequent runs - detect truly new issues
        for issue in filtered_issues:
            issue_key = issue.get("key")
            if issue_key and issue_key not in self.known_issues:
                new_issues.append(issue)
                self.known_issues.add(issue_key)

        if new_issues:
            self._save_known_issues()

        return new_issues

    def send_slack_notification(self, new_issues: List[Dict[str, Any]]) -> bool:
        """Send notification to Slack."""
        if not self.slack_webhook or not new_issues:
            return False

        # Build Slack message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎉 {len(new_issues)} New Jira Ticket(s) Detected!",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Board: {PROJECT_KEY}"
                    }
                ]
            },
            {"type": "divider"}
        ]

        for issue in new_issues[:10]:  # Max 10 tickets per notification
            key = issue.get("key", "Unknown")
            fields = issue.get("fields", {})
            summary = fields.get("summary", "No summary")
            status = fields.get("status", {}).get("name", "Unknown")
            priority = fields.get("priority", {}).get("name", "Unknown")
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            assignee = fields.get("assignee")
            assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

            # Priority emoji
            priority_emoji = {
                "Highest": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢",
                "Lowest": "⚪"
            }.get(priority, "⚪")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{JIRA_BASE_URL}/browse/{key}|{key}>*\n{summary}"
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open Ticket"},
                    "url": f"{JIRA_BASE_URL}/browse/{key}"
                }
            })

            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"{priority_emoji} {priority} | 📊 {status} | 🏷️ {issue_type} | 👤 {assignee_name}"
                    }
                ]
            })

        if len(new_issues) > 10:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_...and {len(new_issues) - 10} more tickets_"
                    }
                ]
            })

        payload = {"blocks": blocks}

        try:
            response = requests.post(self.slack_webhook, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            return False

    def send_email_notification(self, new_issues: List[Dict[str, Any]]) -> bool:
        """Send notification via email (using a webhook service or SMTP)."""
        # This can be extended to use SendGrid, Mailgun, or other email services
        # For now, we'll just print for GitHub Actions logs
        if not new_issues:
            return False

        print(f"\n{'='*60}")
        print(f"NEW TICKETS DETECTED: {len(new_issues)}")
        print(f"{'='*60}\n")

        for issue in new_issues:
            key = issue.get("key", "Unknown")
            fields = issue.get("fields", {})
            summary = fields.get("summary", "No summary")
            print(f"  {key}: {summary}")
            print(f"  Link: {JIRA_BASE_URL}/browse/{key}\n")

        return True

    def run(self) -> Dict[str, Any]:
        """Execute a single monitoring check."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": 0,
            "new_issues_count": 0,
            "new_issues": [],
            "notified": False
        }

        try:
            # Fetch issues
            issues = self.get_issues_from_filter()
            result["total_issues"] = len(issues)

            if not issues:
                print("No issues found or API error")
                return result

            # Detect new issues
            new_issues = self.detect_new_issues(issues)
            result["new_issues_count"] = len(new_issues)
            result["new_issues"] = [
                {
                    "key": i.get("key"),
                    "summary": i.get("fields", {}).get("summary"),
                    "url": f"{JIRA_BASE_URL}/browse/{i.get('key')}"
                }
                for i in new_issues
            ]

            if new_issues:
                print(f"\n🎯 Found {len(new_issues)} new ticket(s)!")

                # Try Slack first
                if self.slack_webhook:
                    result["notified"] = self.send_slack_notification(new_issues)
                    if result["notified"]:
                        print("✅ Slack notification sent")
                    else:
                        print("❌ Slack notification failed")

                # Fallback to console/email
                self.send_email_notification(new_issues)

                # Save updated known issues
                self._save_known_issues()
            else:
                print(f"✓ No new issues (monitoring {len(self.known_issues)} known issues)")

        except Exception as e:
            print(f"Error: {e}")
            result["error"] = str(e)

        return result


def main():
    """Entry point for scheduled execution."""
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

    if not jira_email or not jira_api_token:
        print("❌ Error: JIRA_EMAIL and JIRA_API_TOKEN must be set")
        return 1

    print(f"\n{'='*60}")
    print(f"Jira Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}")

    monitor = JiraMonitor(jira_email, jira_api_token, slack_webhook)
    result = monitor.run()

    print(f"\n{'='*60}")
    print(f"Summary: {result['total_issues']} total | {result['new_issues_count']} new")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    exit(main())
