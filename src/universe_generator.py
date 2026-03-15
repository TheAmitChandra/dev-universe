"""
Universe Generator
Orchestrates the creation of the dev universe from GitHub data.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import random

from .github_api import GitHubAPI
from .repo_analyzer import RepositoryAnalyzer, PlanetData, AsteroidData


@dataclass
class UniverseData:
    """Complete universe data structure."""
    username: str
    primary_language: str
    sun: Dict[str, Any]
    planets: List[PlanetData]
    asteroids: List[AsteroidData]
    background_stars: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class UniverseGenerator:
    """Generates complete universe data from GitHub profile."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize universe generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.github_token = self.config.get('GITHUB_TOKEN')
        self.username = self.config.get('GITHUB_USERNAME')
        self.background_star_count = int(self.config.get('BACKGROUND_STARS', 200))
        
        # Initialize components
        self.api = GitHubAPI(token=self.github_token, username=self.username)
        self.analyzer = RepositoryAnalyzer(config=self.config)
    
    def generate(self) -> UniverseData:
        """
        Generate complete universe data.
        
        Returns:
            UniverseData object with all universe elements
        """
        print("\n" + "="*60)
        print("🌌 GENERATING DEV UNIVERSE")
        print("="*60 + "\n")
        
        # Step 1: Get primary language (the sun)
        print("☀️ STEP 1: Determining primary language...")
        primary_language = self.api.get_primary_language()
        sun = self.analyzer.get_sun_properties(primary_language)
        
        # Step 2: Fetch repository data
        print("\n🪐 STEP 2: Fetching repository data...")
        max_planets = self.analyzer.max_planets
        repos = self.api.get_full_repo_data(max_repos=max_planets)
        
        # Step 3: Analyze repositories into planets
        print("\n🔬 STEP 3: Analyzing repositories...")
        planets = self.analyzer.analyze_repositories(repos)
        
        # Step 4: Extract asteroids (issues and PRs)
        print("\n☄️ STEP 4: Extracting asteroids...")
        asteroids = self.analyzer.extract_asteroids(repos)
        
        # Step 5: Generate background stars
        print("\n✨ STEP 5: Generating background stars...")
        background_stars = self._generate_background_stars()
        
        # Step 6: Compile metadata
        print("\n📊 STEP 6: Compiling metadata...")
        metadata = self._compile_metadata(repos, planets, asteroids)
        
        universe = UniverseData(
            username=self.username,
            primary_language=primary_language,
            sun=sun,
            planets=planets,
            asteroids=asteroids,
            background_stars=background_stars,
            metadata=metadata
        )
        
        print("\n" + "="*60)
        print("✅ UNIVERSE GENERATION COMPLETE")
        print("="*60 + "\n")
        
        self._print_summary(universe)
        
        return universe
    
    def _generate_background_stars(self) -> List[Dict[str, Any]]:
        """
        Generate random background stars for the galaxy.
        
        Returns:
            List of star data dictionaries
        """
        stars = []
        
        # SVG viewBox dimensions (1200×600)
        width = 1200
        height = 600
        center_x = width / 2
        center_y = height / 2
        
        for i in range(self.background_star_count):
            # Random position
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            
            # Avoid placing stars too close to center (where sun is)
            distance_from_center = ((x - center_x)**2 + (y - center_y)**2)**0.5
            if distance_from_center < 100:
                # Push star away from center
                angle = random.uniform(0, 360)
                distance = random.uniform(100, 200)
                x = center_x + distance * math.cos(math.radians(angle))
                y = center_y + distance * math.sin(math.radians(angle))
            
            # Random size (smaller stars more common)
            size = random.choices(
                [0.5, 1, 1.5, 2, 2.5],
                weights=[50, 30, 10, 7, 3]
            )[0]
            
            # Random opacity for depth effect
            opacity = random.uniform(0.3, 1.0)
            
            # Random twinkle delay for animation
            twinkle_delay = random.uniform(0, 5)
            
            stars.append({
                'x': x,
                'y': y,
                'size': size,
                'opacity': opacity,
                'twinkle_delay': twinkle_delay
            })
        
        print(f"✅ Generated {len(stars)} background stars")
        return stars
    
    def _compile_metadata(
        self,
        repos: List[Dict],
        planets: List[PlanetData],
        asteroids: List[AsteroidData]
    ) -> Dict[str, Any]:
        """
        Compile metadata about the universe.
        
        Args:
            repos: Raw repository data
            planets: Analyzed planet data
            asteroids: Asteroid data
            
        Returns:
            Metadata dictionary
        """
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_commits = sum(repo.get('commit_count', 0) for repo in repos)
        total_issues = sum(1 for a in asteroids if a.type == 'issue')
        total_prs = sum(1 for a in asteroids if a.type == 'pr')
        
        # Language distribution
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        metadata = {
            'total_repositories': len(repos),
            'total_stars': total_stars,
            'total_commits': total_commits,
            'total_issues': total_issues,
            'total_prs': total_prs,
            'planet_count': len(planets),
            'asteroid_count': len(asteroids),
            'language_distribution': languages,
            'generated_at': self._get_timestamp()
        }
        
        return metadata
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _print_summary(self, universe: UniverseData):
        """Print a summary of the generated universe."""
        print("\n📋 UNIVERSE SUMMARY")
        print("-" * 60)
        print(f"👤 User: {universe.username}")
        print(f"☀️ Primary Language: {universe.primary_language}")
        print(f"🪐 Planets: {len(universe.planets)}")
        print(f"☄️ Asteroids: {len(universe.asteroids)}")
        print(f"   - Issues: {universe.metadata['total_issues']}")
        print(f"   - Pull Requests: {universe.metadata['total_prs']}")
        print(f"✨ Background Stars: {len(universe.background_stars)}")
        print(f"⭐ Total Repository Stars: {universe.metadata['total_stars']}")
        print(f"💾 Total Recent Commits: {universe.metadata['total_commits']}")
        
        print("\n🪐 PLANET DETAILS:")
        for i, planet in enumerate(universe.planets, 1):
            moons_text = f"🌙×{planet.moons}" if planet.moons > 0 else ""
            print(f"  {i}. {planet.name}")
            print(f"     ⭐ {planet.stars} stars | 💻 {planet.language} | "
                  f"💫 {planet.commit_count} commits {moons_text}")
        
        print("\n" + "-" * 60)
    
    def to_dict(self, universe: UniverseData) -> Dict[str, Any]:
        """
        Convert UniverseData to dictionary for serialization.
        
        Args:
            universe: UniverseData object
            
        Returns:
            Dictionary representation
        """
        return {
            'username': universe.username,
            'primary_language': universe.primary_language,
            'sun': universe.sun,
            'planets': [asdict(p) for p in universe.planets],
            'asteroids': [asdict(a) for a in universe.asteroids],
            'background_stars': universe.background_stars,
            'metadata': universe.metadata
        }


# Import math for background star generation
import math
