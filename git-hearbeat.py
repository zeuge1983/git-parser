import requests
import os
import sys
import argparse

from datetime import datetime, timezone
from collections import Counter

from dotenv import load_dotenv
load_dotenv()

token = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"token {token}"} if token else {}

def fetch_repositories(url):
    repos = []
    params = {"per_page": 100, "page": 1}
    try:
        while True:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 404:
                print("User not found (check username)")
                return []
            
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

def get_most_starred(repos):
    return max(repos, key=lambda r: r["stargazers_count"], default=None)

def print_stats(repos, full_repos):
    language_counts = get_language_counts(repos)
    most_recent = get_most_recently_updated(repos)
    most_starred = get_most_starred(full_repos)

    print("\n--- GitHub Repository Stats ---")
    print("Total Repositories (filtered):", len(repos))
    print("Total Repositories (all):", len(full_repos))

    print("\n--- Most starred repo (overall) ---")
    if most_starred:
        print(
            most_starred["name"],
            "->",
            most_starred["stargazers_count"],
            "stars"
        )

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
    parser = argparse.ArgumentParser(description="GitHub Repository Stats Tool")

    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--language", help="Filter repositories by language")
    parser.add_argument("--no-forks", action="store_true", help="Exclude forked repositories")
    parser.add_argument("--top", type=int, help="Show top N repositories")
    parser.add_argument("--sort", choices=["stars"], help="Sort repositories")

    args = parser.parse_args()

    print("Authenticated:", "Yes" if token else "No")
    print(f"\nFetching data for user: {args.username}...")

    url = f"https://api.github.com/users/{args.username}/repos"

    repos = fetch_repositories(url)
    full_repos = repos.copy()

    # --- Show active filters (UX) ---
    print("\n--- Filters ---")
    if args.language:
        print(f"language = {args.language}")

    if args.no_forks:
        print("excluding forks")

    if args.top:
        print(f"top: {args.top} repositories")

    if args.sort:
        print(f"sorted by: {args.sort}")

    # --- Apply filters ---
    if args.no_forks:
        repos = [repo for repo in repos if not repo["fork"]]

    if args.language:
        repos = [
            repo for repo in repos
            if (repo["language"] or "").lower() == args.language.lower()
        ]

    # --- Sort ---
    if args.sort == "stars":
        repos = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)

    if args.top:
        repos = repos[:args.top]

    print_stats(repos, full_repos)
