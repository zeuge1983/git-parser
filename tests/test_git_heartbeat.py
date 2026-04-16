from collections import Counter

import git_heartbeat


def test_get_language_counts_counts_each_language():
    repos = [
        {"language": "Python"},
        {"language": "Python"},
        {"language": "Go"},
    ]
    result = git_heartbeat.get_language_counts(repos)
    assert result == Counter({"Python": 2, "Go": 1})
