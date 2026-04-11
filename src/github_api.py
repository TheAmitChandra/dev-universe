"""
GitHub API Handler
Fetches repository data, commits, issues, and pull requests from GitHub REST API.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import urllib.request
import urllib.error
from functools import lru_cache


class GitHubAPI:
    """GitHub API client with built-in caching and rate limit handling."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None, username: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub Personal Access Token (optional but recommended)
            username: GitHub username to analyze
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.username = username or os.getenv("GITHUB_ACTOR") or os.getenv("GITHUB_USERNAME")
        
        if not self.username:
            raise ValueError("GitHub username must be provided via parameter or GITHUB_USERNAME env var")
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Dev-Universe/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        self._cache = {}
        self._rate_limit_remaining = None
        self._rate_limit_reset = None
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Make a request to GitHub API with error handling and rate limit awareness.
        
        Args:
            endpoint: API endpoint (e.g., '/users/username/repos')
            params: Query parameters
            
        Returns:
            JSON response data
        """
        # Check cache
        cache_key = f"{endpoint}:{json.dumps(params or {})}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build URL
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
        
        # Check rate limit
        if self._rate_limit_remaining is not None and self._rate_limit_remaining < 5:
            if self._rate_limit_reset:
                wait_time = self._rate_limit_reset - time.time()
                if wait_time > 0:
                    print(f"⏳ Rate limit approaching, waiting {int(wait_time)}s...")
                    time.sleep(wait_time + 1)
        
        # Make request
        try:
            request = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                # Update rate limit info
                self._rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 999))
                reset_timestamp = response.headers.get('X-RateLimit-Reset')
                if reset_timestamp:
                    self._rate_limit_reset = int(reset_timestamp)
                
                # Parse response
                data = json.loads(response.read().decode('utf-8'))
                
                # Cache result
                self._cache[cache_key] = data
                return data
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No error body"
            print(f"❌ HTTP Error {e.code} for {endpoint}: {error_body}")
            
            if e.code == 403:
                print("⚠️ Rate limit exceeded or authentication issue")
            elif e.code == 404:
                print(f"⚠️ Resource not found: {endpoint}")
            
            raise
        except urllib.error.URLError as e:
            print(f"❌ URL Error: {e.reason}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            raise
    
    def get_user_repos(self, max_repos: int = 100) -> List[Dict]:
        """
        Fetch user's repositories.
        
        Args:
            max_repos: Maximum number of repositories to fetch
            
        Returns:
            List of repository data dictionaries
        """
        print(f"📚 Fetching repositories for {self.username}...")
        
        repos = []
        page = 1
        per_page = min(max_repos, 100)
        
        while len(repos) < max_repos:
            endpoint = f"/users/{self.username}/repos"
            params = {
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            }
            
            page_repos = self._make_request(endpoint, params)
            
            if not page_repos:
                break
            
            repos.extend(page_repos)
            
            if len(page_repos) < per_page:
                break
            
            page += 1
        
        print(f"✅ Found {len(repos)} repositories")
        return repos[:max_repos]
    
    def get_repo_commits(self, owner: str, repo_name: str, since_days: int = 365) -> List[Dict]:
        """
        Fetch recent commits for a repository.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            since_days: Number of days to look back
            
        Returns:
            List of commit data dictionaries
        """
        since_date = (datetime.now() - timedelta(days=since_days)).isoformat()
        
        try:
            endpoint = f"/repos/{owner}/{repo_name}/commits"
            params = {
                "since": since_date,
                "per_page": 100
            }
            
            commits = self._make_request(endpoint, params)
            return commits if commits else []
        except Exception as e:
            print(f"⚠️ Could not fetch commits for {repo_name}: {str(e)}")
            return []
    
    def get_repo_issues(self, owner: str, repo_name: str) -> List[Dict]:
        """
        Fetch open issues for a repository.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            List of issue data dictionaries
        """
        try:
            endpoint = f"/repos/{owner}/{repo_name}/issues"
            params = {
                "state": "open",
                "per_page": 100
            }
            
            issues = self._make_request(endpoint, params)
            
            # Filter out pull requests (they appear in issues endpoint too)
            if issues:
                issues = [issue for issue in issues if 'pull_request' not in issue]
            
            return issues if issues else []
        except Exception as e:
            print(f"⚠️ Could not fetch issues for {repo_name}: {str(e)}")
            return []
    
    def get_repo_pull_requests(self, owner: str, repo_name: str) -> List[Dict]:
        """
        Fetch open pull requests for a repository.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            List of pull request data dictionaries
        """
        try:
            endpoint = f"/repos/{owner}/{repo_name}/pulls"
            params = {
                "state": "open",
                "per_page": 100
            }
            
            prs = self._make_request(endpoint, params)
            return prs if prs else []
        except Exception as e:
            print(f"⚠️ Could not fetch PRs for {repo_name}: {str(e)}")
            return []
    
    def get_user_languages(self) -> Dict[str, int]:
        """
        Aggregate language usage across all repositories.
        
        Returns:
            Dictionary mapping language names to byte counts
        """
        print("🌐 Analyzing language usage...")
        
        repos = self.get_user_repos()
        language_stats = {}
        
        for repo in repos:
            owner = repo['owner']['login']
            repo_name = repo['name']
            
            try:
                endpoint = f"/repos/{owner}/{repo_name}/languages"
                languages = self._make_request(endpoint)
                
                if languages:
                    for lang, bytes_count in languages.items():
                        language_stats[lang] = language_stats.get(lang, 0) + bytes_count
            except Exception as e:
                print(f"⚠️ Could not fetch languages for {repo_name}")
                continue
        
        print(f"✅ Analyzed {len(language_stats)} languages")
        return language_stats
    
    def get_primary_language(self) -> str:
        """
        Get the user's most-used programming language.
        
        Returns:
            Primary language name
        """
        languages = self.get_user_languages()
        
        if not languages:
            return "Code"  # Fallback
        
        primary = max(languages.items(), key=lambda x: x[1])[0]
        print(f"⭐ Primary language: {primary}")
        return primary
    
    def get_full_repo_data(self, max_repos: int = 10) -> List[Dict]:
        """
        Get comprehensive data for top repositories including commits, issues, and PRs.
        
        Args:
            max_repos: Maximum number of repositories to analyze
            
        Returns:
            List of enhanced repository data dictionaries
        """
        print(f"\n🌌 Gathering complete universe data for {self.username}...\n")
        
        repos = self.get_user_repos(max_repos)
        enhanced_repos = []
        
        for i, repo in enumerate(repos[:max_repos], 1):
            print(f"[{i}/{max_repos}] Processing {repo['name']}...")
            
            owner = repo['owner']['login']
            repo_name = repo['name']
            
            # Enrich with commit data
            commits = self.get_repo_commits(owner, repo_name)
            repo['recent_commits'] = commits
            repo['commit_count'] = len(commits)
            
            # Enrich with issues
            issues = self.get_repo_issues(owner, repo_name)
            repo['open_issues_list'] = issues
            repo['issue_count'] = len(issues)
            
            # Enrich with pull requests
            prs = self.get_repo_pull_requests(owner, repo_name)
            repo['open_prs'] = prs
            repo['pr_count'] = len(prs)
            
            enhanced_repos.append(repo)
            
            # Small delay to be nice to the API
            time.sleep(0.1)
        
        print(f"\n✅ Universe data collection complete!\n")
        return enhanced_repos
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status."""
        endpoint = "/rate_limit"
        return self._make_request(endpoint)

    # ------------------------------------------------------------------ #
    #  Terminal Card helpers                                               #
    # ------------------------------------------------------------------ #

    def get_user_profile(self) -> Dict:
        """Fetch public user profile from /users/{username}."""
        return self._make_request(f"/users/{self.username}") or {}

    def get_private_repo_count(self) -> int:
        """
        Return the number of private repos owned by the authenticated user.
        Requires a token; returns -1 (unknown) when unauthenticated.
        """
        if not self.token:
            return -1   # unauthenticated — can't see private data
        try:
            data = self._make_request("/user")   # authenticated endpoint
            return data.get("total_private_repos", 0)
        except Exception:
            return -1

    def get_recent_push_count(self) -> int:
        """
        Estimate commit activity from the last ~100 public events.
        Returns the sum of distinct commits across PushEvents.
        """
        try:
            events = self._make_request(
                f"/users/{self.username}/events",
                {"per_page": 100}
            )
            if not events:
                return 0
            return sum(
                e.get("payload", {}).get("distinct_size", 1)
                for e in events
                if e.get("type") == "PushEvent"
            )
        except Exception:
            return 0

    def get_activity_stats(self) -> Dict:
        """
        Analyse the last ~100 public events to derive:
          - total_commits      : distinct commits across PushEvents
          - active_days        : unique calendar days that had a push
          - most_active_day    : weekday name with the most pushes
          - most_commits_day   : weekday name with the highest commit count
          - most_commits_count : number of commits on that peak day
          - day_breakdown      : OrderedDict[weekday -> commit count] Mon–Sun
          - activity_label     : human-friendly status string
        """
        try:
            events = self._make_request(
                f"/users/{self.username}/events",
                {"per_page": 100}
            )
            if not events:
                return self._empty_activity()

            push_events = [e for e in events if e.get("type") == "PushEvent"]
            total_commits = sum(
                e.get("payload", {}).get("distinct_size", 1)
                for e in push_events
            )

            active_days: set = set()
            day_counts: Dict[str, int] = {}

            for e in push_events:
                created = e.get("created_at", "")
                if not created:
                    continue
                try:
                    dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                    active_days.add(dt.date())
                    dow = dt.strftime("%A")
                    day_counts[dow] = day_counts.get(dow, 0) + 1
                except Exception:
                    pass

            n = len(active_days)
            if n >= 20:
                label = "Daily Coder"
            elif n >= 12:
                label = "Active Developer"
            elif n >= 6:
                label = "Regular Contributor"
            elif n >= 2:
                label = "Weekend Warrior"
            else:
                label = "Building in Stealth"

            most_active = (
                max(day_counts, key=lambda k: day_counts[k])
                if day_counts else "N/A"
            )

            # Ordered Mon → Sun breakdown
            weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            day_breakdown = {d: day_counts.get(d, 0) for d in weekday_order}

            peak_day   = most_active
            peak_count = day_counts.get(peak_day, 0) if peak_day != "N/A" else 0

            return {
                "total_commits":      total_commits,
                "active_days":        n,
                "most_active_day":    most_active,
                "most_commits_day":   peak_day,
                "most_commits_count": peak_count,
                "day_breakdown":      day_breakdown,
                "activity_label":     label,
            }
        except Exception:
            return self._empty_activity()

    @staticmethod
    def _empty_activity() -> Dict:
        weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        return {
            "total_commits":      0,
            "active_days":        0,
            "most_active_day":    "N/A",
            "most_commits_day":   "N/A",
            "most_commits_count": 0,
            "day_breakdown":      {d: 0 for d in weekday_order},
            "activity_label":     "Building in Stealth",
        }
