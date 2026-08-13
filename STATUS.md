# ✅ Jira Monitor Bot - Setup Complete!

Your Jira monitoring bot is now running 24/7 on GitHub Actions!

## What's Working

✅ **GitHub Workflow**: Runs every 5 minutes automatically
✅ **Jira API Integration**: Fetches tickets from your board
✅ **Duplicate Detection**: Only notifies for NEW tickets
✅ **Slack Notifications**: Sends alerts to your configured channel
✅ **State Persistence**: Remembers 100 tickets tracked
✅ **Zero Cost**: Runs on free GitHub Actions minutes

## Current Status

- **Repository**: https://github.com/sonatype-docs/jira-monitor
- **Board**: SDS Board #298
- **Filter**: #1866
- **Tickets Tracked**: 100 issues
- **Check Interval**: Every 5 minutes
- **Last Run**: 2026-08-13 09:34:52 UTC

## Monitor Workflow

```
Every 5 minutes:
1. ✅ Fetches issues from Jira API
2. ✅ Compares with known_issues.json
3. ✅ Detects new tickets
4. ✅ Sends Slack notification (if new)
5. ✅ Commits updated known_issues.json
```

## Test Results

**Run 1**: ✅ Found 100 new tickets → Sent Slack notification
**Run 2**: ✅ No new issues → No notification (correct!)
**Run 3**: ✅ No new issues → Monitoring continues

## How to Monitor

### Check Workflow Status
```bash
gh run list --workflow=jira-monitor.yml --limit 5
```

### View Live Logs
```bash
gh run watch
```

### Check Known Issues
```bash
# View the tracked issues on GitHub
open https://github.com/sonatype-docs/jira-monitor/blob/main/data/known_issues.json

# Or fetch via API
gh api repos/sonatype-docs/jira-monitor/contents/data/known_issues.json --jq '.download_url' | xargs curl -s | jq '.issues | length'
```

### Manual Trigger
```bash
gh workflow run jira-monitor.yml
```

### View Recent Commits
```bash
gh api repos/sonatype-docs/jira-monitor/commits --jq '.[0:5] | .[] | .commit.message'
```

## Slack Notifications

When a new ticket is detected, you'll receive a Slack message like:

```
🎉 1 New Jira Ticket(s) Detected!
📅 2026-08-13 09:35:00 UTC | Board: SDS

SDS-12345: Fix documentation bug
Priority: High | Status: Open | Type: Bug
[Open Ticket] button
```

## Management

### Stop Monitoring
```bash
gh workflow disable jira-monitor.yml
```

### Resume Monitoring
```bash
gh workflow enable jira-monitor.yml
```

### Reset Known Issues
1. Edit `data/known_issues.json` on GitHub
2. Set `"issues": []`
3. Commit the change

### Change Poll Interval
Edit `.github/workflows/jira-monitor.yml`:
```yaml
schedule:
  - cron: '*/10 * * * *'  # Every 10 minutes instead
```

### Change Board/Filter
Edit `jira_check.py`:
```python
BOARD_ID = 298
CUSTOM_FILTER_ID = 1866
```

## Monitoring Costs

- **Public repo**: FREE unlimited minutes ✅
- **Private repo**: Uses 2000 free minutes/month
- **Current usage**: ~1 minute per run × 288 runs/day = ~288 minutes/day
- **Monthly estimate**: ~8,640 minutes (within free tier)

## Troubleshooting

### No notifications?
1. Check Slack webhook: `gh secret list`
2. Test workflow manually: `gh workflow run test-monitor.yml`
3. View logs: `gh run watch`

### Workflow not running?
```bash
# Check workflow status
gh workflow list

# View recent runs
gh run list --limit 10
```

### Duplicate notifications?
This shouldn't happen. If it does:
1. Check `data/known_issues.json` was committed
2. Verify latest run committed changes
3. Check `.gitignore` doesn't block known_issues.json

## Next Steps

1. ✅ Monitor is running automatically
2. ⏳ Wait for new tickets to appear
3. 📱 You'll get Slack notifications
4. 🎉 No need to keep your laptop on!

Your Jira monitor is now live and running 24/7 on GitHub's infrastructure! 🚀
