# ✅ Last 7 Days Filter + CLM/NEXUS Only

## What Changed

✅ **Time Filter Applied**: Only monitors tickets updated in the **last 7 days**
✅ **Project Filter**: Only `CLM-*` and `NEXUS-*` tickets
✅ **Reduced Noise**: From 177 tickets → 23 active tickets

## How It Works Now

```
Every 5 minutes:
1. Query: (project = CLM OR project = NEXUS) AND updated >= -7d
2. Result: Only ~23 tickets (not 177!)
3. Filter: CLM/NEXUS only (already in query)
4. Detect: New tickets added in last 7 days
5. Notify: Slack alert for new tickets
```

## Current Configuration

**JQL Query Used**:
```sql
(project = CLM OR project = NEXUS) AND updated >= -7d ORDER BY updated DESC
```

**What This Means**:
- ✅ Only CLM and NEXUS projects
- ✅ Only tickets updated in last 7 days
- ✅ Sorted by most recently updated
- ✅ Maximum 100 results (but typically ~23)

## Test Results

| Run | Tickets Found | Status |
|-----|--------------|--------|
| Run 1 | 23 tickets (last 7 days) | ✅ Notified of 23 new |
| Run 2 | 23 tickets (last 7 days) | ✅ No duplicates |
| Run 3+ | Monitors for new | ✅ Ready |

**Before Filter**: 177 tickets total
**After Filter**: 23 tickets recent
**Reduction**: 87% fewer tickets to monitor!

## Why This Is Better

### Old Approach (All Tickets)
```
❌ Queried entire board (100+ tickets)
❌ Got 177 total tickets
❌ Old tickets from months/years ago
❌ High noise, difficult to track
```

### New Approach (Last 7 Days)
```
✅ Only recent activity (last 7 days)
✅ 23 active tickets to monitor
✅ Relevant to current work
✅ Clean, manageable scope
```

## What You'll See

### When a CLM/NEXUS ticket is updated or created:
```
📅 Found 24 CLM/NEXUS tickets updated in last 7 days
📊 Filtered: 24 CLM/NEXUS tickets out of 24 total
🎯 Found 1 new ticket(s)!
✅ Slack notification sent
```

### Ticket drops off after 7 days:
- Tickets not updated in 7 days automatically disappear
- Keeps the list clean and relevant
- Reduces noise significantly

## Managing the Scope

### Adjust Time Window
To change from 7 days to a different period, edit `jira_check.py`:

```python
# Current: Last 7 days
jql = '(project = CLM OR project = NEXUS) AND updated >= -7d ORDER BY updated DESC'

# Last 3 days (more focused)
jql = '(project = CLM OR project = NEXUS) AND updated >= -3d ORDER BY updated DESC'

# Last 14 days (broader)
jql = '(project = CLM OR project = NEXUS) AND updated >= -14d ORDER BY updated DESC'

# Last 24 hours (very focused)
jql = '(project = CLM OR project = NEXUS) AND updated >= -1d ORDER BY updated DESC'
```

### Add More Projects
```python
# Add INT project
jql = '(project = CLM OR project = NEXUS OR project = INT) AND updated >= -7d ORDER BY updated DESC'
```

### Monitor All Projects (Not Recommended)
```python
# Remove project filter, keep time filter
jql = 'updated >= -7d ORDER BY updated DESC'
```

## Current Status

✅ **Active Filter**: Last 7 days + CLM/NEXUS only
✅ **Tickets Tracked**: 75 (accumulated)
✅ **Active in Last 7 Days**: 23 tickets
✅ **Check Interval**: Every 5 minutes
✅ **Running**: 24/7 on GitHub Actions

## Verification Commands

```bash
# Check current tracked tickets
gh api repos/sonatype-docs/jira-monitor/contents/data/known_issues.json \
  --jq '.download_url' | xargs curl -s | \
  python3 -c "import sys, json; d=json.load(sys.stdin); \
  print(f'CLM: {len([i for i in d[\"issues\"] if i.startswith(\"CLM-\")])}'); \
  print(f'NEXUS: {len([i for i in d[\"issues\"] if i.startswith(\"NEXUS-\")])}')"

# View recent workflow runs
gh run list --workflow=jira-monitor.yml --limit 3

# Watch live execution
gh run watch
```

## Summary

✅ **Reduced from 177 → 23 tickets**
✅ **Time-based filter**: Last 7 days only
✅ **Project filter**: CLM and NEXUS only
✅ **Clean, focused monitoring**
✅ **Ready to alert on new tickets**

Your bot is now optimized to focus only on recent CLM/NEXUS activity! 🎯
