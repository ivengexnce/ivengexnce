import requests
import os
from datetime import datetime, timezone

USER = "ivengexnce"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

def fetch(url):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

events   = fetch(f"https://api.github.com/users/{USER}/events/public?per_page=5")
user     = fetch(f"https://api.github.com/users/{USER}")
repos    = fetch(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")

# Latest activity
latest_raw = events[0]["created_at"] if events else None
if latest_raw:
    dt = datetime.strptime(latest_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    latest = dt.strftime("%B %d, %Y at %H:%M UTC")
else:
    latest = "No recent public activity"

# Latest event type
event_map = {
    "PushEvent": "pushed code",
    "CreateEvent": "created a branch/repo",
    "PullRequestEvent": "opened a pull request",
    "IssuesEvent": "opened an issue",
    "WatchEvent": "starred a repo",
    "ForkEvent": "forked a repo",
    "DeleteEvent": "deleted a branch",
    "ReleaseEvent": "published a release",
}
latest_type = event_map.get(events[0]["type"], events[0]["type"]) if events else "activity"
latest_repo = events[0]["repo"]["name"] if events else ""

# Stats
total_stars = sum(r.get("stargazers_count", 0) for r in repos)
total_forks = sum(r.get("forks_count", 0) for r in repos)
public_repos = user.get("public_repos", 0)
followers    = user.get("followers", 0)

# Top repos by stars
top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:4]
repo_lines = "\n".join(
    f"| [{r['name']}]({r['html_url']}) | {r.get('description') or 'No description'} | "
    f"{'⭐ ' + str(r['stargazers_count']) if r['stargazers_count'] else '—'} | "
    f"{r.get('language') or '—'} |"
    for r in top_repos
)

# Recent activity feed
recent_lines = []
for e in events[:5]:
    etype = event_map.get(e["type"], e["type"])
    rname = e["repo"]["name"].split("/")[-1]
    rurl  = f"https://github.com/{e['repo']['name']}"
    raw   = e["created_at"]
    d     = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d")
    recent_lines.append(f"| {d} | {etype} | [{rname}]({rurl}) |")

recent_table = "\n".join(recent_lines) if recent_lines else "| — | No recent activity | — |"

updated_at = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

content = f"""## 🧠 Live Dev Activity

> Auto-updated every 24 hours via GitHub Actions · Last sync: **{updated_at}**

### 📡 Latest Action
**{latest_type.capitalize()}** in `{latest_repo}` on **{latest}**

### 📊 Quick Stats
| Metric | Count |
|--------|-------|
| Public Repos | {public_repos} |
| Total Stars Earned | {total_stars} |
| Total Forks | {total_forks} |
| Followers | {followers} |

### 🔥 Recent Activity Feed
| Date | Action | Repository |
|------|--------|------------|
{recent_table}

### 🏆 Top Repositories
| Repository | Description | Stars | Language |
|------------|-------------|-------|----------|
{repo_lines}
"""

with open("activity.md", "w") as f:
    f.write(content)

print(f"✅ activity.md updated — last action: {latest_type} in {latest_repo}")