import requests
from datetime import datetime

USER = "ivengexnce"

data = requests.get(f"https://api.github.com/users/{USER}/events/public").json()

latest = data[0]["created_at"]

content = f"""
## 🧠 Dev Activity

- Last GitHub activity: {latest}
- Updated automatically via GitHub Actions
"""

with open("activity.md", "w") as f:
    f.write(content)