"""
SVG Renderer
Renders the complete universe as an animated SVG.
"""

from typing import Dict, List, Any
import math

from .universe_generator import UniverseData
from .repo_analyzer import PlanetData, AsteroidData
from .animation_engine import AnimationEngine


class SVGRenderer:
    """Renders universe data as animated SVG."""
    
    def __init__(self, width: int = 1000, height: int = 1000):
        """
        Initialize SVG renderer.
        
        Args:
            width: SVG canvas width
            height: SVG canvas height
        """
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.animation_engine = AnimationEngine()
    
    def render(self, universe: UniverseData) -> str:
        """
        Render complete universe as SVG string.
        
        Args:
            universe: UniverseData object
            
        Returns:
            Complete SVG markup as string
        """
        print("🎨 Rendering SVG universe...")
        
        svg_parts = []
        
        # SVG header
        svg_parts.append(self._render_header())
        
        # Definitions (gradients, filters, etc.)
        svg_parts.append(self._render_definitions(universe))
        
        # Background
        svg_parts.append(self._render_background(universe))
        
        # Nebula effects
        svg_parts.append(self._render_nebula())
        
        # Background stars
        svg_parts.append(self._render_stars(universe.background_stars))
        
        # Central sun
        svg_parts.append(self._render_sun(universe.sun))
        
        # Planets with orbits
        svg_parts.append(self._render_planets(universe.planets))
        
        # Asteroids (issues and PRs)
        svg_parts.append(self._render_asteroids(universe.asteroids))
        
        # Info overlay
        svg_parts.append(self._render_info_overlay(universe))
        
        # SVG footer
        svg_parts.append(self._render_footer())
        
        svg_content = '\n'.join(svg_parts)
        
        print("✅ SVG rendering complete!")
        return svg_content
    
    def _render_header(self) -> str:
        """Render SVG header."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" 
     viewBox="0 0 {self.width} {self.height}" 
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     style="background: #0d1117;">
'''
    
    def _render_footer(self) -> str:
        """Render SVG footer."""
        return '</svg>'
    
    def _render_definitions(self, universe: UniverseData) -> str:
        """Render SVG definitions (gradients, filters, etc.)."""
        defs = ['  <defs>']
        
        # Sun glow filter
        sun_color = universe.sun['color']
        defs.append(self.animation_engine.create_glow_filter('sunGlow', sun_color, 2.0))
        
        # Planet gradients and filters
        for i, planet in enumerate(universe.planets):
            planet_id = f"planet{i}"
            
            # Gradient for 3D effect
            lighter_color = self._lighten_color(planet.color, 0.3)
            darker_color = self._darken_color(planet.color, 0.2)
            defs.append(self.animation_engine.create_gradient(
                f'{planet_id}Gradient', 
                lighter_color, 
                darker_color
            ))
            
            # Subtle glow filter
            defs.append(self.animation_engine.create_glow_filter(
                f'{planet_id}Glow', 
                planet.color, 
                0.5
            ))
        
        # Comet tail gradient for PRs
        defs.append(self.animation_engine.create_comet_tail_gradient('cometTail'))
        
        defs.append('  </defs>')
        return '\n'.join(defs)
    
    def _render_background(self, universe: UniverseData) -> str:
        """Render background rectangle."""
        return f'''
  <!-- Background -->
  <rect width="{self.width}" height="{self.height}" fill="#0d1117"/>
'''
    
    def _render_nebula(self) -> str:
        """Render nebula background effects."""
        nebula_parts = ['  <!-- Nebula effects -->']
        
        # Create a few large nebula clouds
        nebula_configs = [
            (200, 300, 200, '#1f6feb', 0.08),
            (700, 600, 250, '#8957e5', 0.06),
            (400, 700, 180, '#da3633', 0.05),
        ]
        
        for i, (cx, cy, r, color, opacity) in enumerate(nebula_configs):
            nebula_parts.append(f'''
  <circle cx="{cx}" cy="{cy}" r="{r}" 
          fill="{color}" opacity="{opacity}"
          filter="url(#sunGlow)">
{self.animation_engine.create_nebula_animation()}
  </circle>''')
        
        return '\n'.join(nebula_parts)
    
    def _render_stars(self, stars: List[Dict[str, Any]]) -> str:
        """Render background stars."""
        star_parts = ['  <!-- Background stars -->']
        star_parts.append('  <g id="stars">')
        
        for star in stars:
            star_parts.append(f'''
    <circle cx="{star['x']}" cy="{star['y']}" r="{star['size']}" 
            fill="#ffffff" opacity="{star['opacity']}">
{self.animation_engine.create_twinkle_animation(star['twinkle_delay'])}
    </circle>''')
        
        star_parts.append('  </g>')
        return '\n'.join(star_parts)
    
    def _render_sun(self, sun: Dict[str, Any]) -> str:
        """Render the central sun (primary language)."""
        size = sun['size']
        color = sun['color']
        glow_color = sun['glow_color']
        name = sun['name']
        
        sun_svg = f'''
  <!-- Central Sun ({name}) -->
  <g id="sun" transform="translate({self.center_x}, {self.center_y})">
    <!-- Outer glow -->
    <circle r="{size * 1.5}" fill="{glow_color}" opacity="0.3"
            filter="url(#sunGlow)">
{self.animation_engine.create_pulse_animation('r', size * 1.5, size * 1.7, 4)}
    </circle>
    
    <!-- Sun body -->
    <circle r="{size}" fill="{color}" filter="url(#sunGlow)">
{self.animation_engine.create_pulse_animation('opacity', 0.9, 1.0, 3)}
    </circle>
    
    <!-- Sun label -->
    <text y="{size + 20}" text-anchor="middle" 
          fill="#ffffff" font-size="14" font-weight="bold"
          font-family="Arial, sans-serif">
      {name}
    </text>
  </g>
'''
        return sun_svg
    
    def _render_planets(self, planets: List[PlanetData]) -> str:
        """Render all planets with their orbits and moons."""
        planet_parts = ['  <!-- Planets and orbits -->']
        
        for i, planet in enumerate(planets):
            planet_parts.append(self._render_single_planet(planet, i))
        
        return '\n'.join(planet_parts)
    
    def _render_single_planet(self, planet: PlanetData, index: int) -> str:
        """Render a single planet with orbit and moons."""
        planet_id = f"planet{index}"
        
        # Calculate initial position based on angle offset
        angle_rad = math.radians(planet.angle_offset)
        initial_x = self.center_x + planet.orbit_distance * math.cos(angle_rad)
        initial_y = self.center_y + planet.orbit_distance * math.sin(angle_rad)
        
        planet_svg = f'''
  <!-- Planet: {planet.name} -->
  <g id="{planet_id}">
    <!-- Orbit path -->
    <circle cx="{self.center_x}" cy="{self.center_y}" 
            r="{planet.orbit_distance}"
            fill="none" stroke="#30363d" stroke-width="1" 
            opacity="0.3" stroke-dasharray="5,5"/>
    
    <!-- Planet group with animation -->
    <g transform="translate({self.center_x}, {self.center_y})">
      <g>
{self.animation_engine.create_orbit_animation(planet_id, planet.orbit_distance, planet.orbit_duration, planet.angle_offset)}
        
        <!-- Planet body -->
        <circle r="{planet.size}" 
                fill="url(#{planet_id}Gradient)"
                filter="url(#{planet_id}Glow)"
                stroke="{planet.color}" stroke-width="1">
          <title>{planet.name}&#10;⭐ {planet.stars}&#10;{planet.language}</title>
        </circle>
        
        <!-- Moons -->
{self._render_moons(planet, planet.size)}
        
        <!-- Planet label -->
        <g opacity="0.8">
          <text y="{planet.size + 15}" text-anchor="middle"
                fill="#ffffff" font-size="10" font-weight="normal"
                font-family="Arial, sans-serif">
            {planet.name}
          </text>
        </g>
      </g>
    </g>
  </g>
'''
        return planet_svg
    
    def _render_moons(self, planet: PlanetData, planet_size: float) -> str:
        """Render moons orbiting a planet."""
        if planet.moons == 0:
            return ''
        
        moon_parts = ['        <!-- Moons -->']
        moon_parts.append('        <g id="moons">')
        
        moon_orbit_radius = planet_size + 15
        moon_size = planet_size * 0.2
        moon_duration = 5  # Fast orbit
        
        for moon_idx in range(planet.moons):
            moon_x, moon_y, animation = self.animation_engine.create_moon_orbit(
                moon_idx, planet_size, moon_orbit_radius, moon_duration
            )
            
            moon_parts.append(f'''
          <circle r="{moon_size}" fill="#8b949e" opacity="0.7">
{animation}
          </circle>''')
        
        moon_parts.append('        </g>')
        return '\n'.join(moon_parts)
    
    def _render_asteroids(self, asteroids: List[AsteroidData]) -> str:
        """Render asteroids (issues and PRs)."""
        if not asteroids:
            return '  <!-- No asteroids -->'
        
        asteroid_parts = ['  <!-- Asteroids (Issues & PRs) -->']
        asteroid_parts.append('  <g id="asteroids">')
        
        for asteroid in asteroids:
            if asteroid.type == 'issue':
                asteroid_parts.append(self._render_issue(asteroid))
            else:  # pr
                asteroid_parts.append(self._render_pr(asteroid))
        
        asteroid_parts.append('  </g>')
        return '\n'.join(asteroid_parts)
    
    def _render_issue(self, issue: AsteroidData) -> str:
        """Render an issue as a small asteroid."""
        size = 3
        animation = self.animation_engine.create_asteroid_trajectory(
            issue.trajectory_id, 20
        )
        
        return f'''
    <circle r="{size}" fill="#f85149" opacity="0.8">
      <title>Issue #{issue.number}: {issue.title}</title>
{animation}
    </circle>'''
    
    def _render_pr(self, pr: AsteroidData) -> str:
        """Render a PR as a glowing comet."""
        size = 4
        animation = self.animation_engine.create_asteroid_trajectory(
            pr.trajectory_id, 20
        )
        
        return f'''
    <g>
      <!-- Comet tail -->
      <ellipse rx="15" ry="3" fill="url(#cometTail)" opacity="0.6">
{animation}
      </ellipse>
      <!-- Comet head -->
      <circle r="{size}" fill="#58a6ff" opacity="0.9">
        <title>PR #{pr.number}: {pr.title}</title>
{animation}
      </circle>
    </g>'''
    
    def _render_info_overlay(self, universe: UniverseData) -> str:
        """Render info overlay with statistics."""
        metadata = universe.metadata
        
        info_y = self.height - 80
        
        return f'''
  <!-- Info overlay -->
  <g id="info" opacity="0.7">
    <text x="20" y="{info_y}" 
          fill="#8b949e" font-size="12" font-family="monospace">
      @{universe.username}'s Dev Universe
    </text>
    <text x="20" y="{info_y + 18}" 
          fill="#8b949e" font-size="10" font-family="monospace">
      🪐 {metadata['planet_count']} repos  •  ⭐ {metadata['total_stars']} stars  •  💫 {metadata['total_commits']} commits
    </text>
    <text x="20" y="{info_y + 33}" 
          fill="#8b949e" font-size="10" font-family="monospace">
      ☄️ {metadata['total_issues']} issues  •  🚀 {metadata['total_prs']} PRs
    </text>
  </g>
'''
    
    def _lighten_color(self, hex_color: str, factor: float = 0.3) -> str:
        """Lighten a hex color."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, hex_color: str, factor: float = 0.3) -> str:
        """Darken a hex color."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
