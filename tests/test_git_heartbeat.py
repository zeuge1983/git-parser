from collections import Counter

import pytest

import git_heartbeat


@pytest.mark.parametrize(
    "repos, expected",
    [
        # No repos at all → empty Counter. # 1
        ([], Counter()),
        # Single repo, single language. # 2
        ([{"language": "Python"}], Counter({"Python": 1})),
        # Several repos, multiple languages, duplicates counted. # 3
        (
            [
                {"language": "Python"},
                {"language": "Python"},
                {"language": "Go"},
            ],
            Counter({"Python": 2, "Go": 1}),
        ),
        # GitHub API returns `null` for repos with no detected language. # 4
        # The `or "Unknown"` branch should kick in.
        ([{"language": None}], Counter({"Unknown": 1})),
        # Mix of known languages and None. # 5
        (
            [
                {"language": "Python"},
                {"language": None},
                {"language": None},
            ],
            Counter({"Python": 1, "Unknown": 2}),
        ),
    ],
    ids=[
        "empty",
        "single",
        "multiple_mixed",
        "none_language",
        "known_plus_none",
    ],
)
def test_get_language_counts(repos, expected):
    assert git_heartbeat.get_language_counts(repos) == expected
