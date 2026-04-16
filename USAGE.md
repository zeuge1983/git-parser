# git_heartbeat.py — Usage Guide

A CLI tool for fetching GitHub repository statistics and commit history.

## Prerequisites

- Python 3
- A `.env` file with `GITHUB_TOKEN` (optional, but recommended to avoid rate limits)

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `username` | Yes | GitHub username to fetch data for |
| `--language` | No | Filter repositories by programming language |
| `--no-forks` | No | Exclude forked repositories from results |
| `--top N` | No | Limit output to the top N repositories |
| `--sort stars` | No | Sort repositories by star count (descending) |
| `--output FILE` | No | Path for the JSON output file (default: `output.json`) |
| `--repo NAME` | No | Fetch full commit history for a specific repository and save to JSON |

## Examples

### Basic usage — get stats for a user

```bash
python git_heartbeat.py octocat
```

Prints stats to the console and saves them (including commit activity for the top 10 most-starred repos) to `output.json`.

### Filter by language

```bash
python git_heartbeat.py octocat --language python
```

### Exclude forks and show top 5 repos sorted by stars

```bash
python git_heartbeat.py octocat --no-forks --top 5 --sort stars
```

### Save stats to a custom file

```bash
python git_heartbeat.py octocat --output my-stats.json
```

### Fetch full commit history for a specific repo

```bash
python git_heartbeat.py octocat --repo Hello-World
```

Saves the entire commit history (sha, message, author, date, url) to `output.json`.

### Fetch commit history and save to a custom file

```bash
python git_heartbeat.py octocat --repo Hello-World --output hello-commits.json
```

## Notes

- When `--repo` is used, the tool fetches only the commit history for that repository and exits without running the general stats flow.
- By default, commit activity (last year / last two years) is fetched for the **10 most-starred** repositories.
- Authentication via `GITHUB_TOKEN` increases the API rate limit from 60 to 5000 requests/hour.
