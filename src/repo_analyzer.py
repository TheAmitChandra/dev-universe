"""
Repository Analyzer
Analyzes repository metrics and transforms them into universe properties.
"""

import math
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class PlanetData:
    """Represents a repository as a planet in the universe."""
    name: str
    full_name: str
    stars: int
    language: str
    size: float  # Visual size in pixels
    orbit_distance: float  # Distance from sun in pixels
    orbit_duration: float  # Animation duration in seconds
    angle_offset: float  # Starting angle in degrees
    color: str  # Planet color
    moons: int  # Number of moons
    url: str  # Repository URL
    description: str  # Repository description
    commit_count: int
    created_at: str
    updated_at: str
    age_days: int


@dataclass
class AsteroidData:
    """Represents an issue or PR as an asteroid."""
    title: str
    type: str  # 'issue' or 'pr'
    number: int
    url: str
    repo_name: str
    trajectory_id: int  # Unique animation path ID


class RepositoryAnalyzer:
    """Analyzes repositories and converts metrics to visual properties."""
    
    # Language colors (GitHub standard colors)
    LANGUAGE_COLORS = {
        'Python': '#3572A5',
        'JavaScript': '#F1E05A',
        'TypeScript': '#2B7489',
        'Java': '#B07219',
        'Go': '#00ADD8',
        'Rust': '#DEA584',
        'C++': '#F34B7D',
        'C': '#555555',
        'C#': '#178600',
        'PHP': '#4F5D95',
        'Ruby': '#701516',
        'Swift': '#F05138',
        'Kotlin': '#A97BFF',
        'Dart': '#00B4AB',
        'Scala': '#C22D40',
        'R': '#198CE7',
        'Shell': '#89E051',
        'PowerShell': '#012456',
        'Objective-C': '#438EFF',
        'HTML': '#E34C26',
        'CSS': '#563D7C',
        'Vue': '#41B883',
        'Jupyter Notebook': '#DA5B0B',
        'Markdown': '#083FA1',
        'YAML': '#CB171E',
        'JSON': '#292929',
    }
    
    DEFAULT_COLOR = '#8B949E'  # GitHub gray
    
    # Moon thresholds
    MOON_THRESHOLDS = [
        (0, 0),      # 0-5 stars: no moon
        (5, 1),      # 5-20 stars: 1 moon
        (20, 2),     # 20-100 stars: 2 moons
        (100, 3),    # 100+ stars: 3 moons
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Configuration dictionary with settings
        """
        self.config = config or {}
        self.max_planets = self.config.get('MAX_PLANETS', 8)
        self.show_moons = self.config.get('SHOW_MOONS', True)
        self.show_asteroids = self.config.get('SHOW_ASTEROIDS', True)
        self.orbit_speed_multiplier = float(self.config.get('ORBIT_SPEED_MULTIPLIER', 1.0))
        
        # Visual parameters for 880×440 viewport
        self.min_planet_size = 22
        self.max_planet_size = 48
        self.min_orbit_distance = 90
        self.max_orbit_distance = 370
        self.min_orbit_duration = 25  # seconds
        self.max_orbit_duration = 80  # seconds
    
    def analyze_repositories(self, repos: List[Dict]) -> List[PlanetData]:
        """
        Analyze repositories and convert to planet data.
        
        Args:
            repos: List of repository data from GitHub API
            
        Returns:
            List of PlanetData objects
        """
        print(f"🔬 Analyzing {len(repos)} repositories...")
        
        # Sort by activity score (stars + commits + forks) for better ranking
        def _score(r):
            return (r.get('stargazers_count', 0) * 10
                    + r.get('commit_count', 0)
                    + r.get('forks_count', 0) * 5
                    + r.get('size', 0) // 100)
        sorted_repos = sorted(repos, key=_score, reverse=True)
        top_repos = sorted_repos[:self.max_planets]
        
        planets = []
        
        for i, repo in enumerate(top_repos):
            planet = self._repo_to_planet(repo, i, len(top_repos))
            if planet:
                planets.append(planet)
        
        print(f"✅ Created {len(planets)} planets")
        return planets
    
    def _repo_to_planet(self, repo: Dict, index: int, total: int) -> PlanetData:
        """
        Convert a single repository to planet data.
        
        Args:
            repo: Repository data dictionary
            index: Repository index in sorted list
            total: Total number of repositories
            
        Returns:
            PlanetData object
        """
        # Extract basic info
        name = repo.get('name', 'unknown')
        full_name = repo.get('full_name', name)
        stars = repo.get('stargazers_count', 0)
        language = repo.get('language') or 'Unknown'
        url = repo.get('html_url', '')
        description = repo.get('description') or ''
        
        # Calculate age
        created_at = repo.get('created_at', '')
        updated_at = repo.get('updated_at', '')
        age_days = self._calculate_age_days(created_at)
        
        # Get commit count and repo size (KB)
        commit_count = repo.get('commit_count', 0)
        repo_size = repo.get('size', 0)  # KB
        
        # Calculate visual properties
        size = self._calculate_planet_size(stars, commit_count, repo_size)
        orbit_distance = self._calculate_orbit_distance(age_days, index, total)
        orbit_duration = self._calculate_orbit_duration(commit_count)
        angle_offset = (360 / total) * index  # Spread planets evenly
        color = self._get_language_color(language)
        moons = self._calculate_moon_count(stars) if self.show_moons else 0
        
        return PlanetData(
            name=name,
            full_name=full_name,
            stars=stars,
            language=language,
            size=size,
            orbit_distance=orbit_distance,
            orbit_duration=orbit_duration,
            angle_offset=angle_offset,
            color=color,
            moons=moons,
            url=url,
            description=description,
            commit_count=commit_count,
            created_at=created_at,
            updated_at=updated_at,
            age_days=age_days
        )
    
    def _calculate_age_days(self, created_at: str) -> int:
        """Calculate repository age in days."""
        if not created_at:
            return 0
        try:
            created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
            age = datetime.now() - created_date
            return age.days
        except Exception:
            return 0
    
    def _calculate_planet_size(self, stars: int, commits: int = 0, repo_size: int = 0) -> float:
        """Planet size from multiple signals so 0-star repos still vary.
        
        Combines stars, commits, and repo size into a composite score.
        Even repos with 0 stars get differentiated by their commit
        count and code size.
        """
        # Composite activity score (each metric contributes)
        score = (stars * 10) + commits + (repo_size // 50)
        
        if score <= 0:
            return self.min_planet_size
        
        log_score = math.log10(score + 1)
        max_log = math.log10(5000)  # normalizing ceiling
        
        normalized = min(log_score / max_log, 1.0)
        size_range = self.max_planet_size - self.min_planet_size
        
        return self.min_planet_size + (size_range * normalized)
    
    def _calculate_orbit_distance(self, age_days: int, index: int, total: int) -> float:
        """
        Calculate orbit distance based on repository age.
        Older repositories orbit farther from the sun.
        
        Args:
            age_days: Repository age in days
            index: Repository index
            total: Total repositories
            
        Returns:
            Orbit distance in pixels
        """
        # Base distance on index to ensure spacing
        base_distance = self.min_orbit_distance + (
            (self.max_orbit_distance - self.min_orbit_distance) / (total - 1 if total > 1 else 1)
        ) * index
        
        # Add variation based on age (±20%)
        if age_days > 0:
            max_age = 365 * 5  # 5 years
            age_factor = min(age_days / max_age, 1.0)
            variation = (age_factor - 0.5) * 0.4  # -0.2 to +0.2
            base_distance *= (1 + variation)
        
        return base_distance
    
    def _calculate_orbit_duration(self, commit_count: int) -> float:
        """
        Calculate orbit duration based on commit frequency.
        More commits = faster orbit = shorter duration.
        
        Args:
            commit_count: Number of recent commits
            
        Returns:
            Orbit duration in seconds
        """
        if commit_count <= 0:
            return self.max_orbit_duration
        
        # Inverse relationship: more commits = faster orbit
        log_commits = math.log10(commit_count + 1)
        max_log = math.log10(500)  # Assume 500 as very active
        
        normalized = min(log_commits / max_log, 1.0)
        duration_range = self.max_orbit_duration - self.min_orbit_duration
        
        # Invert: high activity = low duration
        duration = self.max_orbit_duration - (duration_range * normalized)
        
        # Apply speed multiplier
        duration = duration / self.orbit_speed_multiplier
        
        return max(duration, self.min_orbit_duration)
    
    def _get_language_color(self, language: str) -> str:
        """Get color for a programming language."""
        return self.LANGUAGE_COLORS.get(language, self.DEFAULT_COLOR)
    
    def _calculate_moon_count(self, stars: int) -> int:
        """
        Calculate number of moons based on star count.
        
        Args:
            stars: Number of repository stars
            
        Returns:
            Number of moons (0-3)
        """
        for threshold, moon_count in reversed(self.MOON_THRESHOLDS):
            if stars >= threshold:
                return moon_count
        return 0
    
    def extract_asteroids(self, repos: List[Dict]) -> List[AsteroidData]:
        """
        Extract issues and PRs as asteroids.
        
        Args:
            repos: List of repository data with issues and PRs
            
        Returns:
            List of AsteroidData objects
        """
        if not self.show_asteroids:
            return []
        
        print("☄️ Extracting asteroids (issues & PRs)...")
        
        asteroids = []
        trajectory_id = 0
        
        for repo in repos:
            repo_name = repo.get('name', 'unknown')
            
            # Process issues
            for issue in repo.get('open_issues_list', []):
                asteroids.append(AsteroidData(
                    title=issue.get('title', 'Untitled'),
                    type='issue',
                    number=issue.get('number', 0),
                    url=issue.get('html_url', ''),
                    repo_name=repo_name,
                    trajectory_id=trajectory_id
                ))
                trajectory_id += 1
            
            # Process pull requests
            for pr in repo.get('open_prs', []):
                asteroids.append(AsteroidData(
                    title=pr.get('title', 'Untitled'),
                    type='pr',
                    number=pr.get('number', 0),
                    url=pr.get('html_url', ''),
                    repo_name=repo_name,
                    trajectory_id=trajectory_id
                ))
                trajectory_id += 1
        
        # Limit asteroids to prevent overcrowding
        max_asteroids = 20
        if len(asteroids) > max_asteroids:
            asteroids = asteroids[:max_asteroids]
        
        print(f"✅ Created {len(asteroids)} asteroids")
        return asteroids
    
    def get_sun_properties(self, primary_language: str) -> Dict[str, Any]:
        """
        Get properties for the central sun (primary language).
        
        Args:
            primary_language: Most-used programming language
            
        Returns:
            Dictionary with sun properties
        """
        return {
            'name': primary_language,
            'color': self._get_language_color(primary_language),
            'size': 60,  # Sun radius — big and dominant in 880×440
            'glow_color': self._lighten_color(self._get_language_color(primary_language))
        }
    
    def _lighten_color(self, hex_color: str, factor: float = 0.3) -> str:
        """
        Lighten a hex color for glow effects.
        
        Args:
            hex_color: Color in hex format (#RRGGBB)
            factor: Lightening factor (0-1)
            
        Returns:
            Lightened hex color
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Lighten
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
