"""
Profile Builder
Collects and structures GitHub profile data for the terminal card.
Only 3-4 API calls total — fast, works with or without a token.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone

from .github_api import GitHubAPI


@dataclass
class RepoSummary:
    name: str
    stars: int
    language: str
    url: str
    updated_at: str
    description: str


@dataclass
class ProfileData:
    username: str
    display_name: str
    bio: str
    location: str
    website: str                # blog / website URL
    company: str                # company name
    twitter: str                # handle without @
    followers: int
    following: int
    public_repos: int
    account_since: str          # "2019"
    total_stars: int
    total_forks: int
    recent_commits: int         # commits from last ~100 events
    active_days: int            # unique days with pushes in last 100 events
    most_active_day: str        # e.g. "Friday"
    activity_label: str         # e.g. "Weekend Warrior"
    top_repos: List[RepoSummary]
    language_stats: Dict[str, float]   # lang -> percentage (0-100)

    @property
    def primary_language(self) -> str:
        if self.language_stats:
            return max(self.language_stats, key=lambda k: self.language_stats[k])
        return "Unknown"


class ProfileBuilder:
    """
    Builds a ProfileData from GitHub API responses.

    API calls made:
      1. GET /users/{username}              — profile info
      2. GET /users/{username}/repos        — all repos (1-2 pages)
      3. GET /users/{username}/events       — recent push activity
      4. GET /repos/{u}/{r}/languages       — per-repo byte counts (cached)
    """

    def __init__(
        self,
        api: GitHubAPI,
        max_repos: int = 5,
        max_languages: int = 5,
    ) -> None:
        self.api = api
        self.max_repos = max_repos
        self.max_languages = max_languages

    def build(self) -> ProfileData:
        print("👤  Fetching user profile…")
        raw_profile = self.api.get_user_profile()

        print("📚  Fetching repositories…")
        repos = self.api.get_user_repos(max_repos=100)

        print("⚡  Counting recent activity…")
        activity = self.api.get_activity_stats()
        recent_commits = activity["total_commits"]

        # ── own (non-fork) repos ──────────────────────────────────
        own = [r for r in repos if not r.get("fork")]

        # Top repos by stars then by most recently updated
        top_sorted = sorted(
            own,
            key=lambda r: (r.get("stargazers_count", 0), r.get("updated_at", "")),
            reverse=True,
        )
        top_repos = [
            RepoSummary(
                name=r["name"],
                stars=r.get("stargazers_count", 0),
                language=r.get("language") or "N/A",
                url=r.get("html_url", ""),
                updated_at=r.get("updated_at", ""),
                description=r.get("description") or "",
            )
            for r in top_sorted[: self.max_repos]
        ]

        # Language breakdown — use actual byte counts from the API
        print("🌐  Fetching language byte counts…")
        lang_bytes = self.api.get_user_languages()  # {lang: total_bytes}

        if lang_bytes:
            total_bytes = sum(lang_bytes.values()) or 1
            lang_pct = {
                lang: round(bytes_ / total_bytes * 100)
                for lang, bytes_ in sorted(lang_bytes.items(), key=lambda x: -x[1])
            }
            # Drop any that round to 0%
            lang_pct = {k: v for k, v in lang_pct.items() if v > 0}
        else:
            # Fallback: count repos per primary language
            lang_counts: Dict[str, int] = {}
            for r in own:
                lang = r.get("language")
                if lang:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
            total_lang = sum(lang_counts.values()) or 1
            lang_pct = {
                lang: round(count / total_lang * 100)
                for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1])
            }

        top_langs = dict(list(lang_pct.items())[: self.max_languages])

        # Aggregate totals across own repos
        total_stars = sum(r.get("stargazers_count", 0) for r in own)
        total_forks = sum(r.get("forks_count", 0) for r in own)

        # Account creation year
        created_at = raw_profile.get("created_at", "")
        since_year = created_at[:4] if created_at else "N/A"

        display_name = raw_profile.get("name") or raw_profile.get("login") or self.api.username

        # Clean up website URL for display
        website_raw = raw_profile.get("blog") or ""
        if website_raw and not website_raw.startswith("http"):
            website_raw = "https://" + website_raw

        print("✅  Profile data ready.\n")

        return ProfileData(
            username=self.api.username,
            display_name=display_name,
            bio=raw_profile.get("bio") or "",
            location=raw_profile.get("location") or "",
            website=website_raw,
            company=(raw_profile.get("company") or "").lstrip("@").strip(),
            twitter=raw_profile.get("twitter_username") or "",
            followers=raw_profile.get("followers", 0),
            following=raw_profile.get("following", 0),
            public_repos=raw_profile.get("public_repos", 0),
            account_since=since_year,
            total_stars=total_stars,
            total_forks=total_forks,
            recent_commits=recent_commits,
            active_days=activity["active_days"],
            most_active_day=activity["most_active_day"],
            activity_label=activity["activity_label"],
            top_repos=top_repos,
            language_stats=top_langs,
        )
