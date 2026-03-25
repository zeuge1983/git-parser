import requests
import os
import sys

from datetime import datetime, timezone
from collections import Counter

from dotenv import load_dotenv
load_dotenv()

token = os.getenv("GITHUB_TOKEN")

headers = { "Authorization": f"Bearer {token}"} 
if token:
    print("Authenticated: Yes")
else:
    print("Authenticated: No")

def fetch_repositories(url):
    repos = []
    params = {"per_page": 100, "page": 1}
    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            repos.extend(data)
            if len(data) < 100:
                break
            params["page"] += 1
        return repos
    except requests.exceptions.RequestException as e:
        print("Error fetching repositories:", e)
        return repos
    
def time_ago(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delta = now - dt

    date_str = dt.strftime("%Y-%m-%d")

    days = delta.days
    seconds = delta.seconds

    if days > 0:
        return f"{days} days ago ({date_str})"
    elif seconds > 3600:
        hours = seconds // 3600
        return f"{hours} hours ago ({date_str})"
    elif seconds > 60:
        minutes = seconds // 60
        return f"{minutes} minutes ago ({date_str})"
    else:
        return f"just now ({date_str})"

def get_language_counts(repos):
    return Counter(repo["language"] or "Unknown" for repo in repos)


def get_most_recently_updated(repos):
    return max(repos, key=lambda r: r["updated_at"], default=None)


def print_stats(repos):
    language_counts = get_language_counts(repos)
    most_recent = get_most_recently_updated(repos)

    print("\n--- GitHub Repository Stats ---")
    print("Total Repositories:", len(repos))

    print("\n--- Repository list ---")
    for repo in repos:
        print("Repo:", repo["name"], "|", "Language:", repo["language"] or "Unknown")

    print("\n--- Most recently updated repo ---")
    if most_recent:
        print(most_recent["name"], "->", time_ago(most_recent["updated_at"]))

    print("\n--- Language Count ---")
    for language, count in language_counts.most_common():
        print(f"{language}: {count} repos")

    print("\n--- Most Used Language ---")
    if language_counts:
        top_language, top_count = language_counts.most_common(1)[0]
        print(f"Top language: {top_language} ({top_count} repos)")


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else None

    print(f"\nFetching data for user: {username}...")

    if not username:
        print("Usage: python git-hearbeat.py <github_username>")
        sys.exit(1)

    url = f"https://api.github.com/users/{username}/repos"

    repos = fetch_repositories(url)
    print_stats(repos)
