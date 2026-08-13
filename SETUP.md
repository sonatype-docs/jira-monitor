# Setup Guide for GitHub Actions Deployment

## Step-by-Step Instructions

### Step 1: Create GitHub Repository

```bash
# Navigate to your project
cd /Users/jagadishbondada/Desktop/jira-notifier

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Jira monitor bot"

# Create GitHub repo (choose ONE option)

# Option A: Public repo (UNLIMITED free minutes)
gh repo create jira-monitor --public --source=. --push

# Option B: Private repo (2000 free minutes/month)
gh repo create jira-monitor --private --source=. --push
```

> **💡 Recommendation**: Use a **public repo** for unlimited free GitHub Actions minutes. Your secrets (API tokens, webhooks) are still private and encrypted.

### Step 2: Get Credentials

#### Jira API Token
1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Label: `jira-monitor-bot`
4. **Copy the token** (you won't see it again!)

#### Slack Webhook (Optional)
1. Visit: https://api.slack.com/apps
2. **Create New App** → **From scratch**
3. Name it `jira-monitor`, select your workspace
4. Go to **Incoming Webhooks** → Enable → **Add New Webhook to Workspace**
5. Select the channel where you want notifications
6. **Copy the webhook URL** (looks like: `https://hooks.slack.com/services/T00/B00/XXX`)

### Step 3: Add GitHub Secrets

```bash
# Option A: Using GitHub CLI (recommended)
gh secret set JIRA_EMAIL -b"your-email@example.com"
gh secret set JIRA_API_TOKEN -b"ATATT3xFfGF0..."
gh secret set SLACK_WEBHOOK_URL -b"https://hooks.slack.com/services/T00/B00/XXX"

# Option B: Using GitHub website
# 1. Go to your repo: https://github.com/YOUR_USERNAME/jira-monitor
# 2. Settings → Secrets and variables → Actions
# 3. Click "New repository secret" for each:
#    - JIRA_EMAIL
#    - JIRA_API_TOKEN
#    - SLACK_WEBHOOK_URL (optional)
```

### Step 4: Test the Setup

```bash
# Trigger the test workflow
gh workflow run test-monitor.yml

# Or via website: Actions → "Test Jira Monitor" → "Run workflow"

# Watch the logs
gh run watch
```

### Step 5: Verify Automation

After pushing, the main workflow will run **every 5 minutes automatically**.

Check status:
```bash
# View recent runs
gh run list --workflow=jira-monitor.yml --limit 5

# View live logs
gh run watch
```

## How It Runs 24/7

```
┌─────────────────────────────────────────────────┐
│     GitHub Actions Cloud (runs 24/7/365)       │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Every 5 minutes:                        │   │
│  │                                           │   │
│  │  1. Spin up Ubuntu container             │   │
│  │  2. Checkout your repo                   │   │
│  │  3. Install Python + dependencies        │   │
│  │  4. Run jira_check.py                    │   │
│  │  5. Send Slack notification (new ticket) │   │
│  │  6. Commit known_issues.json back        │   │
│  │  7. Terminate container                  │   │
│  │                                           │   │
│  │  Total time: ~30 seconds per run         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Your laptop can be OFF - this runs in cloud   │
│                                                 │
│  Cost: $0 (free tier) if public repo           │
└─────────────────────────────────────────────────┘
```

## Monitoring

### View All Runs
```bash
# Via CLI
gh run list --workflow=jira-monitor.yml

# Via website
# https://github.com/YOUR_USERNAME/jira-monitor/actions
```

### Check Known Issues
```bash
# The bot maintains a file with all known issues
# View it: data/known_issues.json

cat data/known_issues.json
```

### Stop the Bot
```bash
# Disable the workflow
gh workflow disable jira-monitor.yml

# Re-enable later
gh workflow enable jira-monitor.yml
```

## Troubleshooting

### No tickets detected
Run the test workflow first to verify:
```bash
gh workflow run test-monitor.yml
```

### Can't access filter/board
If you see 403 errors in logs:
1. Open the filter in Jira: https://sonatype.atlassian.net/jira/software/c/projects/SDS/boards/298/backlog?customFilter=1866
2. Make sure you can view it in browser
3. Your API token must have same permissions as your account

### Workflow not running
1. Check Actions tab for errors
2. Verify secrets are set correctly
3. Make sure workflow file is on main branch

## Advanced: Reduce Usage

If using private repo (2000 min/month limit):

```yaml
# Change schedule in .github/workflows/jira-monitor.yml
schedule:
  # - cron: '*/5 * * * *'  # Every 5 min (12,000 min/month)
  - cron: '*/15 * * * *'   # Every 15 min (4,000 min/month)
  # - cron: '0 * * * *'    # Every hour (1,000 min/month)
```

## Next Steps

1. ✅ Push to GitHub
2. ✅ Add secrets
3. ✅ Test with manual run
4. ✅ Wait for automatic runs (every 5 min)
5. ✅ Monitor Slack for new ticket notifications

Your Jira monitor will run 24/7 on GitHub's infrastructure, even when your laptop is off! 🎉
