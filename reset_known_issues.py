#!/usr/bin/env python3
"""
Reset the known issues database.
This marks all current tickets as known, preventing notifications for existing tickets.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "known_issues.json"

def reset_known_issues():
    """Clear known issues to start fresh."""
    data = {
        "issues": [],
        "last_updated": datetime.now().isoformat(),
        "note": "Reset - next run will populate all current issues as known without notification"
    }

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Known issues reset at {data['last_updated']}")
    print(f"📁 File: {DATA_FILE}")
    print("\nNext run will:")
    print("  - Fetch all current issues from the board")
    print("  - Mark them as known (no notifications)")
    print("  - Only notify for FUTURE new tickets")

if __name__ == "__main__":
    reset_known_issues()
