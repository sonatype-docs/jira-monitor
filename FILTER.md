# ✅ CLM & NEXUS Filter Active

## Filter Configuration

Your bot now **only monitors CLM-* and NEXUS-* tickets**.

```python
ALLOWED_PREFIXES = ("CLM-", "NEXUS-")
```

## Current Status

✅ **Filter Active**: Only CLM and NEXUS tickets monitored

✅ **Tickets Tracked**: 52 tickets
- CLM tickets: 15
- NEXUS tickets: 37
- Other tickets: 0 (ignored)

✅ **Workflow**: Running every 5 minutes

## How It Works

### Board Scan Process
```
1. Fetch 100 tickets from board
2. Filter: Extract CLM-* and NEXUS-* only
3. Result: 52 tickets to monitor
4. Compare with known issues
5. Notify if new CLM/NEXUS tickets found
```

### Example Log Output
```
📊 Filtered: 52 CLM/NEXUS tickets out of 100 total
✓ No new issues (monitoring 52 known issues)
```

## What Gets Tracked

| Ticket Type | Monitored | Example |
|-------------|-----------|---------|
| **CLM-*** | ✅ Yes | CLM-35883, CLM-29975 |
| **NEXUS-*** | ✅ Yes | NEXUS-51062, NEXUS-43856 |
| INT-* | ❌ No | Ignored |
| EI-* | ❌ No | Ignored |
| PRD-* | ❌ No | Ignored |
| GUIDE-* | ❌ No | Ignored |
| SDEV-* | ❌ No | Ignored |
| Other prefixes | ❌ No | Ignored |

## Test Results

### Run 1: Filter Applied
```
📊 Filtered: 52 CLM/NEXUS tickets out of 100 total
🆕 First run - populating known issues without notification
✓ 52 issues tracked (CLM/NEXUS only)
```

### Run 2: Ongoing Monitoring
```
📊 Filtered: 52 CLM/NEXUS tickets out of 100 total
✓ No new issues (monitoring 52 known issues)
```

### Future: New Ticket Arrives
```
📊 Filtered: 53 CLM/NEXUS tickets out of 101 total
🎯 Found 1 new ticket(s)!
✅ Slack notification sent

Ticket: CLM-12345 (new CLM ticket)
```

## What You'll See

### Slack Notification Example
```
🎉 1 New Jira Ticket(s) Detected!
📅 2026-08-13 10:00:00 UTC | Board: SDS

CLM-12345: Fix critical bug in IQ
🔴 High | 📊 Open | 🏷️ Bug | 👤 John Doe
[Open Ticket] button
```

## Adding/Removing Filters

To change which ticket types to monitor, edit `jira_check.py`:

```python
# Line 62 in detect_new_issues() method
ALLOWED_PREFIXES = ("CLM-", "NEXUS-")  # Current

# Add more prefixes:
# ALLOWED_PREFIXES = ("CLM-", "NEXUS-", "INT-", "EI-")

# Monitor only CLM:
# ALLOWED_PREFIXES = ("CLM-",)

# Monitor all tickets (remove filter):
# ALLOWED_PREFIXES = None  # Then remove the filter logic
```

After editing, commit and push:
```bash
git add jira_check.py
git commit -m "Update ticket filter"
git push
```

## Verification

Check current tracked tickets:
```bash
gh api repos/sonatype-docs/jira-monitor/contents/data/known_issues.json \
  --jq '.download_url' | xargs curl -s | \
  python3 -c "import sys, json; d=json.load(sys.stdin); \
  print(f'CLM: {len([i for i in d[\"issues\"] if i.startswith(\"CLM-\")])}'); \
  print(f'NEXUS: {len([i for i in d[\"issues\"] if i.startswith(\"NEXUS-\")])}')"
```

Monitor workflow runs:
```bash
gh run list --workflow=jira-monitor.yml --limit 3
```

## Summary

✅ **Active Filter**: CLM-* and NEXUS-* only
✅ **Ignoring**: All other ticket types (INT, EI, PRD, GUIDE, etc.)
✅ **Tracking**: 52 CLM/NEXUS tickets
✅ **Notifications**: Only for NEW CLM/NEXUS tickets

Your bot is now focused exclusively on the ticket types you care about! 🎯
