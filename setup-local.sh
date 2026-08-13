#!/bin/bash

# Jira Monitor Setup Script for Local Testing
# Run this locally to test your setup before pushing to GitHub

set -e

echo "========================================"
echo "Jira Monitor - Local Setup & Test"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Check credentials
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "❌ Missing credentials!"
    echo ""
    echo "Please set environment variables:"
    echo "  export JIRA_EMAIL='your-email@example.com'"
    echo "  export JIRA_API_TOKEN='your-api-token'"
    echo ""
    echo "Generate API token at: https://id.atlassian.com/manage-profile/security/api-tokens"
    exit 1
fi
echo "✅ JIRA_EMAIL: $JIRA_EMAIL"
echo "✅ JIRA_API_TOKEN: ${JIRA_API_TOKEN:0:8}..."

# Test API connection
echo ""
echo "Testing Jira API connection..."
python3 -c "
import os
import requests

email = os.getenv('JIRA_EMAIL')
token = os.getenv('JIRA_API_TOKEN')

session = requests.Session()
session.auth = (email, token)

# Test authentication
resp = session.get('https://sonatype.atlassian.net/rest/api/3/myself')

if resp.status_code == 200:
    user = resp.json()
    print(f'✅ Authenticated as: {user.get(\"displayName\")}')
else:
    print(f'❌ Authentication failed: {resp.status_code}')
    exit(1)

# Test filter access
resp = session.get('https://sonatype.atlassian.net/rest/api/3/filter/1866')
if resp.status_code == 200:
    print('✅ Can access filter #1866')
else:
    print(f'⚠️  Cannot access filter #1866: {resp.status_code}')

# Test board access
resp = session.get('https://sonatype.atlassian.net/rest/agile/1.0/board/298')
if resp.status_code == 200:
    board = resp.json()
    print(f'✅ Can access board #298: {board.get(\"name\", \"Unknown\")}')
else:
    print(f'⚠️  Cannot access board #298: {resp.status_code}')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ API test failed. Check your credentials and permissions."
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q requests python-dotenv 2>/dev/null || pip3 install -q requests python-dotenv

# Create data directory
mkdir -p data

# Run a test check
echo ""
echo "Running test check..."
python3 jira_check.py

echo ""
echo "========================================"
echo "✅ Setup complete!"
echo "========================================"
echo ""
echo "Next steps for GitHub Actions:"
echo "1. Create a GitHub repository"
echo "2. Add secrets in repo settings:"
echo "   - JIRA_EMAIL"
echo "   - JIRA_API_TOKEN"
echo "   - SLACK_WEBHOOK_URL (optional)"
echo "3. Push this code to GitHub"
echo "4. The workflow will run every 5 minutes automatically"
echo ""
