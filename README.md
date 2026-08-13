# Jira Board Monitor Bot 🤖

Automated Jira board monitoring that runs 24/7 on GitHub Actions - no laptop required!

## Features

- ✅ **Runs 24/7 on GitHub Actions** - No need to keep your laptop on
- 🔍 **Checks every 5 minutes** - Configurable schedule
- 🆕 **Detects new tickets** - Tracks known issues to avoid duplicates
- 💬 **Slack notifications** - Get instant alerts when new tickets arrive
- 🔄 **Automatic state persistence** - Saves known issues to the repo
- ⚡ **Zero cost** - Uses free GitHub Actions minutes

## Quick Start

### 1. Get Your Credentials

#### Jira API Token
1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Label it "Jira Monitor Bot"
4. Copy the token

#### Slack Webhook (Optional but Recommended)
1. Go to https://api.slack.com/apps
2. Create a new app → "Incoming Webhooks"
3. Add a webhook to your desired channel
4. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T000/B000/XXXX`)

### 2. Create GitHub Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Jira monitor bot"

# Create repo on GitHub and push
# Option A: Using GitHub CLI
gh repo create jira-monitor --private --source=. --push

# Option B: Manual
# Go to github.com, create new repo, then:
git remote add origin https://github.com/YOUR_USERNAME/jira-monitor.git
git push -u origin main
```

### 3. Add GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `JIRA_EMAIL` | Your Atlassian email | `you@company.com` |
| `JIRA_API_TOKEN` | Your API token | `ATATT3xFfGF0...` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL (optional) | `https://hooks.slack.com/services/...` |

### 4. Enable GitHub Actions

The workflow will automatically run every 5 minutes once pushed.

To test immediately:
1. Go to **Actions** tab in your repo
2. Click **"Test Jira Monitor"** → **"Run workflow"** → **"Run workflow"**
3. Check the logs to verify it works

## Local Testing

Test before pushing to GitHub:

```bash
# Set credentials
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"

# Run setup script
chmod +x setup-local.sh
./setup-local.sh
```

Or manually:

```bash
# Install dependencies
pip install requests python-dotenv

# Create data directory
mkdir -p data

# Run check
python3 jira_check.py
```

## How It Works

```
┌─────────────────────────────────────────────┐
│          GitHub Actions (24/7)              │
│                                             │
│  Every 5 minutes:                           │
│  1. Fetch issues from Jira API              │
│  2. Compare with known_issues.json          │
│  3. Identify new tickets                    │
│  4. Send Slack notification                 │
│  5. Commit updated known_issues.json        │
│                                             │
└─────────────────────────────────────────────┘
           │
           ├─────> Jira API (your board)
           │
           └─────> Slack (notifications)
```

## Configuration

### Change Polling Interval

Edit `.github/workflows/jira-monitor.yml`:

```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes
  # - cron: '*/10 * * * *'  # Every 10 minutes
  # - cron: '0 * * * *'  # Every hour
```

### Change Board or Filter

Edit `jira_check.py`:

```python
JIRA_BASE_URL = "https://sonatype.atlassian.net"
BOARD_ID = 298
PROJECT_KEY = "SDS"
CUSTOM_FILTER_ID = 1866
```

## File Structure

```
jira-notifier/
├── .github/
│   └── workflows/
│       ├── jira-monitor.yml      # Main 5-minute schedule
│       └── test-monitor.yml      # Manual test workflow
├── data/
│   └── known_issues.json         # Tracked issues (auto-updated)
├── jira_check.py                 # Main monitoring script
├── jira_monitor.py               # Local continuous monitor
├── requirements.txt
├── setup-local.sh                # Local testing script
└── .env.example                  # Credentials template
```

## Troubleshooting

### No notifications appearing

1. Check GitHub Actions logs for errors
2. Verify secrets are set correctly
3. Test API connection with the test workflow

### Authentication failed

- Verify email matches your Atlassian account
- Regenerate API token if needed
- Check token hasn't been revoked

### "Resource not found" errors

- Verify BOARD_ID and CUSTOM_FILTER_ID are correct
- Ensure your account has access to the board/filter
- Check project permissions in Jira

### Slack notifications not working

- Verify webhook URL is correct
- Test webhook manually: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' YOUR_WEBHOOK_URL`
- Ensure the Slack app has permissions

## Costs

- **GitHub Actions**: Free for public repos, 2000 minutes/month for private repos
- **Usage**: ~2-3 minutes per run × 288 runs/day = ~600-900 minutes/day
- **Recommendation**: Use a **public repo** for unlimited free minutes (secrets are still private)

## Security

- Secrets are encrypted and never exposed in logs
- API tokens can be revoked at any time
- `.gitignore` prevents committing sensitive files
- Repository can be private

## Advanced

### Add More Notification Channels

Edit `jira_check.py` to add:
- Discord webhooks
- Microsoft Teams
- Email via SendGrid
- SMS via Twilio
- Custom webhooks

### Filter Notifications

Only notify for specific priorities:

```python
# In detect_new_issues(), add:
ALLOWED_PRIORITIES = ["Highest", "High"]
if fields.get("priority", {}).get("name") not in ALLOWED_PRIORITIES:
    continue
```

### Multiple Boards

Create multiple workflow files for different boards:

```yaml
# .github/workflows/jira-monitor-board-123.yml
env:
  BOARD_ID: 123
```

## Resources

- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Slack Webhooks](https://api.slack.com/messaging/webhooks)
- [Atlassian API Tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

## License

MIT
