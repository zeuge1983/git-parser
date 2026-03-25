# Git Heartbeat 🫀

A command-line tool that fetches and displays statistics about a GitHub user's repositories — including language breakdown, most recently updated repo, and more.

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **GitHub Personal Access Token** — [Create one here](https://github.com/settings/tokens)
  - Required scope: `public_repo` (for accessing public repository data)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/git-parser.git
   cd git-parser
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```bash
   GITHUB_TOKEN=your_github_personal_access_token
   ```

## Usage

```bash
python git-hearbeat.py <github_username>
```

**Example:**

```bash
python git-hearbeat.py octocat
```

### Output

The script will display:

- ✅ Authentication status
- 📦 Total number of repositories
- 📋 Full repository list with languages
- 🕐 Most recently updated repository
- 📊 Language breakdown across all repos
- 🏆 Most used programming language

## Dependencies

| Package        | Description                              |
|----------------|------------------------------------------|
| `requests`     | HTTP library for GitHub API calls        |
| `python-dotenv`| Loads environment variables from `.env`  |

## License

This project is open source and available under the [MIT License](LICENSE).
