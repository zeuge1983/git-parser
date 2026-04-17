from collections import Counter
from datetime import datetime, timezone

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


# ---------------------------------------------------------------------------
# time_ago
# ---------------------------------------------------------------------------

# The function calls datetime.now(timezone.utc) internally, so we freeze
# "now" to a fixed point in time. Otherwise tests would break the moment
# a second boundary is crossed.
FROZEN_NOW = datetime(2025, 4, 15, 12, 0, 0, tzinfo=timezone.utc)


class FakeDatetime(datetime):
    """datetime subclass that returns FROZEN_NOW from .now()."""

    @classmethod
    def now(cls, tz=None):
        return FROZEN_NOW


@pytest.fixture
def freeze_time(monkeypatch):
    # Replace the `datetime` name inside git_heartbeat's namespace.
    # strptime / replace / etc. are inherited from datetime so they still work.
    monkeypatch.setattr(git_heartbeat, "datetime", FakeDatetime)


@pytest.mark.parametrize(
    "timestamp, expected",
    [
        # 2 days before FROZEN_NOW → days branch
        ("2025-04-13T12:00:00Z", "2 days ago (2025-04-13)"),
        # Same day, 2.5 hours before → hours branch (delta.seconds = 9000)
        ("2025-04-15T09:30:00Z", "2 hours ago (2025-04-15)"),
        # Same day, 15 minutes before → minutes branch (delta.seconds = 900)
        ("2025-04-15T11:45:00Z", "15 minutes ago (2025-04-15)"),
        # 30 seconds before → just now branch (delta.seconds = 30)
        ("2025-04-15T11:59:30Z", "just now (2025-04-15)"),
    ],
    ids=["days", "hours", "minutes", "just_now"],
)
def test_time_ago(freeze_time, timestamp, expected):
    assert git_heartbeat.time_ago(timestamp) == expected
