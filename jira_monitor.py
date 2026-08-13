#!/usr/bin/env python3
"""
Jira Board Monitor Bot
Monitors a Jira board backlog for new tickets and sends notifications.
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Optional, Set, List, Dict, Any
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# Configuration
JIRA_BASE_URL = "https://sonatype.atlassian.net"
BOARD_ID = 298
PROJECT_KEY = "SDS"
CUSTOM_FILTER_ID = 1866
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL", "300"))  # Default: 5 minutes

# Storage file for known issues
KNOWN_ISSUES_FILE = Path(__file__).parent / "known_issues.json"


class JiraMonitor:
    def __init__(self, email: str, api_token: str):
        self.email = email
        self.api_token = api_token
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
        with open(KNOWN_ISSUES_FILE, "w") as f:
            json.dump({
                "issues": list(self.known_issues),
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)

    def get_issues_from_filter(self) -> List[Dict[str, Any]]:
        """
        Fetch issues using the custom filter.
        Uses Jira's search API to get issues matching the filter criteria.
        """
        # Approach 1: Use the filter directly
        # GET /rest/api/3/filter/{id} gives us the JQL, then we execute it
        filter_url = f"{JIRA_BASE_URL}/rest/api/3/filter/{CUSTOM_FILTER_ID}"

        try:
            # First, get the filter to retrieve the JQL query
            filter_response = self.session.get(filter_url)

            if filter_response.status_code == 200:
                filter_data = filter_response.json()
                jql = filter_data.get("jql", "")
                print(f"[{datetime.now()}] Using filter JQL: {jql}")

                # Now search using the JQL
                search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
                params = {
                    "jql": jql,
                    "fields": "key,summary,status,priority,assignee,created,updated,issuetype",
                    "maxResults": 100
                }
                search_response = self.session.get(search_url, params=params)

                if search_response.status_code == 200:
                    return search_response.json().get("issues", [])
                else:
                    print(f"[{datetime.now()}] Search failed: {search_response.status_code} - {search_response.text}")
            else:
                print(f"[{datetime.now()}] Could not fetch filter: {filter_response.status_code}")

        except Exception as e:
            print(f"[{datetime.now()}] Error fetching issues: {e}")

        return []

    def get_issues_from_board(self) -> List[Dict[str, Any]]:
        """
        Alternative: Fetch issues directly from the board using Agile API.
        """
        # Using the Agile/Software API for board issues
        url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{BOARD_ID}/issue"
        params = {
            "fields": "key,summary,status,priority,assignee,created,updated,issuetype",
            "maxResults": 100
        }

        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("issues", [])
            else:
                print(f"[{datetime.now()}] Board API failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[{datetime.now()}] Error fetching board issues: {e}")

        return []

    def detect_new_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare with known issues and return only new ones."""
        new_issues = []

        for issue in issues:
            issue_key = issue.get("key")
            if issue_key and issue_key not in self.known_issues:
                new_issues.append(issue)
                self.known_issues.add(issue_key)

        if new_issues:
            self._save_known_issues()

        return new_issues

    def send_notification(self, new_issues: List[Dict[str, Any]]) -> None:
        """Send notification about new issues."""
        count = len(new_issues)
        print(f"\n{'='*60}")
        print(f"[{datetime.now()}] 🎉 {count} NEW TICKET(S) DETECTED!")
        print(f"{'='*60}")

        for issue in new_issues:
            key = issue.get("key", "Unknown")
            fields = issue.get("fields", {})
            summary = fields.get("summary", "No summary")
            status = fields.get("status", {}).get("name", "Unknown")
            priority = fields.get("priority", {}).get("name", "Unknown")
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            assignee = fields.get("assignee")
            assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

            print(f"\n📋 {key}: {summary}")
            print(f"   Type: {issue_type} | Status: {status} | Priority: {priority}")
            print(f"   Assignee: {assignee_name}")
            print(f"   Link: {JIRA_BASE_URL}/browse/{key}")

        print(f"\n{'='*60}\n")

        # You can extend this to send emails, Slack messages, etc.
        # See notification methods below

    def send_email_notification(
        self,
        new_issues: List[Dict[str, Any]],
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_email: str
    ) -> None:
        """Send email notification about new issues."""
        if not new_issues:
            return

        subject = f"[Jira Monitor] {len(new_issues)} new ticket(s) detected"

        # Build email body
        body_lines = [
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New tickets detected:\n"
        ]

        for issue in new_issues:
            key = issue.get("key", "Unknown")
            fields = issue.get("fields", {})
            summary = fields.get("summary", "No summary")
            status = fields.get("status", {}).get("name", "Unknown")
            priority = fields.get("priority", {}).get("name", "Unknown")

            body_lines.append(f"\n{key}: {summary}")
            body_lines.append(f"  Status: {status} | Priority: {priority}")
            body_lines.append(f"  Link: {JIRA_BASE_URL}/browse/{key}")

        body = "\n".join(body_lines)

        # Create email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"[{datetime.now()}] 📧 Email notification sent to {recipient_email}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Failed to send email: {e}")

    def run(self, use_filter: bool = True) -> None:
        """Main monitoring loop."""
        print(f"\n{'='*60}")
        print("Jira Board Monitor Started")
        print(f"{'='*60}")
        print(f"Board ID: {BOARD_ID}")
        print(f"Project: {PROJECT_KEY}")
        print(f"Custom Filter ID: {CUSTOM_FILTER_ID}")
        print(f"Poll Interval: {POLL_INTERVAL_SECONDS} seconds")
        print(f"Known Issues: {len(self.known_issues)}")
        print(f"{'='*60}\n")

        # Initial fetch - populate known issues without notification
        print(f"[{datetime.now()}] Performing initial fetch...")
        issues = self.get_issues_from_filter() if use_filter else self.get_issues_from_board()

        if issues:
            print(f"[{datetime.now()}] Found {len(issues)} existing issues")
            for issue in issues:
                self.known_issues.add(issue.get("key"))
            self._save_known_issues()
        else:
            print(f"[{datetime.now()}] No issues found or API error. Check credentials and permissions.")

        print(f"[{datetime.now()}] Starting monitoring loop...")

        while True:
            try:
                # Fetch current issues
                issues = self.get_issues_from_filter() if use_filter else self.get_issues_from_board()

                # Detect new ones
                new_issues = self.detect_new_issues(issues)

                # Notify if there are new issues
                if new_issues:
                    self.send_notification(new_issues)
                    # Uncomment to enable email notifications:
                    # self.send_email_notification(new_issues, smtp_server, smtp_port, sender_email, sender_password, recipient_email)
                else:
                    print(f"[{datetime.now()}] No new issues ({len(issues)} total monitored)")

            except KeyboardInterrupt:
                print(f"\n[{datetime.now()}] Monitor stopped by user")
                break
            except Exception as e:
                print(f"[{datetime.now()}] Error in monitoring loop: {e}")

            # Wait for next poll
            time.sleep(POLL_INTERVAL_SECONDS)


def main():
    """Entry point for the Jira monitor."""
    # Get credentials from environment variables
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")

    if not jira_email or not jira_api_token:
        print("❌ Error: Missing credentials!")
        print("\nPlease set the following environment variables:")
        print("  export JIRA_EMAIL='your-email@example.com'")
        print("  export JIRA_API_TOKEN='your-api-token'")
        print("\nGenerate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens")
        return

    # Create and run monitor
    monitor = JiraMonitor(jira_email, jira_api_token)

    # Use filter-based approach (recommended for custom filters)
    # Set to False to use board-based approach instead
    monitor.run(use_filter=True)


if __name__ == "__main__":
    main()
