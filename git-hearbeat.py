import requests
import os
import sys
import argparse
import json

from datetime import datetime, timedelta, timezone
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

def build_stats_data(repos, full_repos, username):
    language_counts = get_language_counts(repos)
    most_recent = get_most_recently_updated(repos)
    most_starred = get_most_starred(full_repos)
    
    top_by_stars = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:10]
    repos_for_commits = top_by_stars

    return {
        "total_repositories": {
            "filtered": len(repos),
            "all": len(full_repos)
        },
        "filters": {
            "language": args.language,
            "no_forks": args.no_forks,
            "top": args.top,
            "sort": args.sort
        },
        "most_starred": {
            "name": most_starred["name"] if most_starred else None,
            "stars": most_starred["stargazers_count"] if most_starred else 0
        },
        "most_recently_updated": {
            "name": most_recent["name"] if most_recent else None,
            "updated_at": most_recent["updated_at"] if most_recent else None,
            "human_readable": time_ago(most_recent["updated_at"]) if most_recent else None
        },
        "languages": dict(language_counts),
        "top_language": (
            language_counts.most_common(1)[0] if language_counts else None
        ),
        "repositories": [
            {
                "name": repo["name"],
                "language": repo["language"],
                "stars": repo["stargazers_count"],
                "updated_at": repo["updated_at"],
                "commit_activity": get_commit_activity_for_repo(username, repo["name"])
            }
            for repo in repos_for_commits
        ]
    }

def get_commit_count(owner, repo_name, since):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"

    params = {"since": since}
    count = 0
    page = 1

    while True:
        params["page"] = page
        params["per_page"] = 100

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 409:
            return 0

        response.raise_for_status()

        commits = response.json()

        if not commits:
            break

        count += len(commits)
        page += 1

    return count

def get_commit_activity_for_repo(owner, repo_name):
    now = datetime.now(timezone.utc)

    one_year_ago = (now - timedelta(days=365)).isoformat()
    two_years_ago = (now - timedelta(days=730)).isoformat()

    commits_1y = get_commit_count(owner, repo_name, one_year_ago)
    commits_2y = get_commit_count(owner, repo_name, two_years_ago)

    return {
        "last_year": commits_1y,
        "last_two_years": commits_2y
    }

def fetch_full_commit_history(owner, repo_name):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    commits = []
    page = 1

    while True:
        params = {"page": page, "per_page": 100}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        for c in data:
            commits.append({
                "sha": c["sha"],
                "message": c["commit"]["message"],
                "author": c["commit"]["author"]["name"],
                "date": c["commit"]["author"]["date"],
                "url": c["html_url"]
            })

        if len(data) < 100:
            break
        page += 1

    return commits

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
    parser.add_argument("--output", default="output.json", help="Save output to JSON file (default: output.json)")
    parser.add_argument("--repo", help="Fetch full commit history for a specific repository and save to JSON")

    args = parser.parse_args()

    print("Authenticated:", "Yes" if token else "No")
    print(f"\nFetching data for user: {args.username}...")

    url = f"https://api.github.com/users/{args.username}/repos"

    if args.repo:
        print(f"\nFetching full commit history for {args.username}/{args.repo}...")
        commits = fetch_full_commit_history(args.username, args.repo)
        output_file = args.output or "output.json"
        data = {
            "repository": f"{args.username}/{args.repo}",
            "total_commits": len(commits),
            "commits": commits
        }
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved {len(commits)} commits to {output_file}")
        sys.exit(0)

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

    data = build_stats_data(repos, full_repos, args.username)

    with open(args.output, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nSaved stats to {args.output}")
    print_stats(repos, full_repos)
