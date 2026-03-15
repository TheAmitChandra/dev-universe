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
    
    def __init__(self, width: int = 1920, height: int = 600):
        """
        Initialize SVG renderer.
        
        Args:
            width: SVG canvas width (cover size)
            height: SVG canvas height (cover size)
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
     style="background: linear-gradient(135deg, #0a0e27 0%, #1a1b3d 50%, #0d1117 100%);">
'''
    
    def _render_footer(self) -> str:
        """Render SVG footer."""
        return '</svg>'
    
    def _render_definitions(self, universe: UniverseData) -> str:
        """Render SVG definitions (gradients, filters, etc.)."""
        defs = ['  <defs>']
        
        # Advanced shadow filter for 3D depth
        defs.append('''  <filter id="shadow3D" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="8"/>
    <feOffset dx="0" dy="4" result="offsetblur"/>
    <feComponentTransfer>
      <feFuncA type="linear" slope="0.5"/>
    </feComponentTransfer>
    <feMerge>
      <feMergeNode/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>''')
        
        # Sun glow filter with enhanced intensity
        sun_color = universe.sun['color']
        defs.append(self.animation_engine.create_glow_filter('sunGlow', sun_color, 3.5))
        
        # Radial gradient for background depth
        defs.append('''  <radialGradient id="bgGradient" cx="50%" cy="50%">
    <stop offset="0%" style="stop-color:#1a2332;stop-opacity:0.3" />
    <stop offset="100%" style="stop-color:#000000;stop-opacity:0.8" />
  </radialGradient>''')
        
        # Planet gradients and filters with 3D effect
        for i, planet in enumerate(universe.planets):
            planet_id = f"planet{i}"
            
            # Enhanced 3D gradient
            lighter_color = self._lighten_color(planet.color, 0.5)
            mid_color = planet.color
            darker_color = self._darken_color(planet.color, 0.4)
            
            defs.append(f'''  <radialGradient id="{planet_id}Gradient" cx="35%" cy="35%">
    <stop offset="0%" style="stop-color:{lighter_color};stop-opacity:1" />
    <stop offset="40%" style="stop-color:{mid_color};stop-opacity:1" />
    <stop offset="100%" style="stop-color:{darker_color};stop-opacity:1" />
  </radialGradient>''')
            
            # Strong glow filter for planets
            defs.append(self.animation_engine.create_glow_filter(
                f'{planet_id}Glow', 
                planet.color, 
                1.5
            ))
        
        # Enhanced comet tail gradient
        defs.append('''  <linearGradient id="cometTail">
    <stop offset="0%" style="stop-color:#58a6ff;stop-opacity:0.9" />
    <stop offset="50%" style="stop-color:#79c0ff;stop-opacity:0.5" />
    <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
  </linearGradient>''')
        
        defs.append('  </defs>')
        return '\n'.join(defs)
    
    def _render_background(self, universe: UniverseData) -> str:
        """Render enhanced background with depth."""
        return f'''
  <!-- Background with depth -->
  <rect width="{self.width}" height="{self.height}" fill="url(#bgGradient)"/>
  
  <!-- Ambient space fog -->
  <circle cx="{self.width * 0.2}" cy="{self.height * 0.3}" r="300" 
          fill="#1f2d4d" opacity="0.1" filter="url(#sunGlow)"/>
  <circle cx="{self.width * 0.8}" cy="{self.height * 0.7}" r="350" 
          fill="#2d1f4d" opacity="0.08" filter="url(#sunGlow)"/>
'''
    
    def _render_nebula(self) -> str:
        """Render enhanced nebula effects with depth."""
        nebula_parts = ['  <!-- Nebula effects with depth -->']
        
        # Create dynamic nebula clouds across the cover
        nebula_configs = [
            (self.width * 0.15, self.height * 0.4, 280, '#1f6feb', 0.12),
            (self.width * 0.75, self.height * 0.3, 320, '#8957e5', 0.10),
            (self.width * 0.45, self.height * 0.65, 250, '#da3633', 0.08),
            (self.width * 0.85, self.height * 0.7, 200, '#56d364', 0.07),
        ]
        
        for i, (cx, cy, r, color, opacity) in enumerate(nebula_configs):
            nebula_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 0.7}" 
          fill="{color}" opacity="{opacity}"
          filter="url(#sunGlow)" transform="rotate({i * 30} {cx} {cy})">
{self.animation_engine.create_nebula_animation()}
  </ellipse>''')
        
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
        """Render the central sun with enhanced 3D effects."""
        size = sun['size'] * 1.3  # Larger sun
        color = sun['color']
        glow_color = sun['glow_color']
        name = sun['name']
        
        sun_svg = f'''
  <!-- Central Sun ({name}) with 3D effects -->
  <g id="sun" transform="translate({self.center_x}, {self.center_y})">
    <!-- Outer corona layers -->
    <circle r="{size * 2.5}" fill="{glow_color}" opacity="0.15"
            filter="url(#sunGlow)">
{self.animation_engine.create_pulse_animation('r', size * 2.5, size * 2.8, 6)}
{self.animation_engine.create_pulse_animation('opacity', 0.1, 0.2, 5)}
    </circle>
    
    <circle r="{size * 1.8}" fill="{glow_color}" opacity="0.25"
            filter="url(#sunGlow)">
{self.animation_engine.create_pulse_animation('r', size * 1.8, size * 2.0, 4)}
    </circle>
    
    <!-- Sun body with 3D gradient -->
    <circle r="{size}" fill="{color}" filter="url(#sunGlow) url(#shadow3D)">
{self.animation_engine.create_pulse_animation('opacity', 0.95, 1.0, 3)}
    </circle>
    
    <!-- Inner highlight for 3D effect -->
    <circle cx="{-size * 0.2}" cy="{-size * 0.2}" r="{size * 0.4}" 
            fill="{glow_color}" opacity="0.6"/>
    
    <!-- Sun label with shadow -->
    <text y="{size + 30}" text-anchor="middle" 
          fill="#000000" font-size="20" font-weight="bold"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
          opacity="0.3">
      {name}
    </text>
    <text y="{size + 28}" text-anchor="middle" 
          fill="#ffffff" font-size="20" font-weight="bold"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif">
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
        
        <!-- Planet body with 3D effect -->
        <circle r="{planet.size}" 
                fill="url(#{planet_id}Gradient)"
                filter="url(#{planet_id}Glow) url(#shadow3D)"
                stroke="{self._lighten_color(planet.color, 0.3)}" stroke-width="2">
          <title>{planet.name}&#10;⭐ {planet.stars}&#10;{planet.language}</title>
        </circle>
        
        <!-- Shine/highlight for 3D depth -->
        <ellipse cx="{-planet.size * 0.3}" cy="{-planet.size * 0.3}" 
                 rx="{planet.size * 0.35}" ry="{planet.size * 0.25}" 
                 fill="white" opacity="0.4"/>
        
        <!-- Moons -->
{self._render_moons(planet, planet.size)}
        
        <!-- Planet label -->
        <g opacity="0.8">
          <!-- Planet label with shadow -->
          <text y="{planet.size + 18}" text-anchor="middle"
                fill="#000000" font-size="12" font-weight="600"
                font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                opacity="0.4">
            {planet.name}
          </text>
          <text y="{planet.size + 16}" text-anchor="middle"
                fill="#ffffff" font-size="12" font-weight="600"
                font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
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
        """Render an issue as an asteroid with 3D effect."""
        size = 5
        animation = self.animation_engine.create_asteroid_trajectory(
            issue.trajectory_id, 20
        )
        
        return f'''
    <g>
      <circle r="{size}" fill="#f85149" opacity="0.9" 
              filter="url(#shadow3D)">
        <title>Issue #{issue.number}: {issue.title}</title>
{animation}
      </circle>
      <circle r="{size * 0.4}" cx="{-size * 0.3}" cy="{-size * 0.3}" 
              fill="#ff7b72" opacity="0.7">
{animation}
      </circle>
    </g>'''
    
    def _render_pr(self, pr: AsteroidData) -> str:
        """Render a PR as a glowing comet with enhanced effects."""
        size = 6
        animation = self.animation_engine.create_asteroid_trajectory(
            pr.trajectory_id, 20
        )
        
        return f'''
    <g>
      <!-- Comet tail with glow -->
      <ellipse rx="30" ry="5" fill="url(#cometTail)" opacity="0.8"
               filter="url(#sunGlow)">
{animation}
      </ellipse>
      <!-- Comet head with 3D effect -->
      <circle r="{size}" fill="#58a6ff" opacity="0.95"
              filter="url(#shadow3D)">
        <title>PR #{pr.number}: {pr.title}</title>
{animation}
      </circle>
      <!-- Inner glow -->
      <circle r="{size * 0.5}" fill="#79c0ff" opacity="0.9">
{animation}
      </circle>
    </g>'''
    
    def _render_info_overlay(self, universe: UniverseData) -> str:
        """Render enhanced info overlay with statistics."""
        metadata = universe.metadata
        
        info_y = self.height - 65
        
        return f'''
  <!-- Info overlay with glassmorphism -->
  <g id="info">
    <!-- Background panel -->
    <rect x="20" y="{info_y - 35}" width="550" height="80" 
          rx="12" fill="#161b22" opacity="0.8" 
          stroke="#30363d" stroke-width="1"/>
    
    <!-- Title -->
    <text x="35" y="{info_y - 10}" 
          fill="#58a6ff" font-size="16" font-weight="bold"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
      @{universe.username}'s Development Universe
    </text>
    
    <!-- Stats line 1 -->
    <text x="35" y="{info_y + 12}" 
          fill="#c9d1d9" font-size="13" font-weight="500"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
      🪐 {metadata['planet_count']} repositories  •  ⭐ {metadata['total_stars']} stars  •  💫 {metadata['total_commits']} recent commits
    </text>
    
    <!-- Stats line 2 -->
    <text x="35" y="{info_y + 30}" 
          fill="#8b949e" font-size="12"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
      ☄️ {metadata['total_issues']} open issues  •  🚀 {metadata['total_prs']} pull requests  •  Updates every 12 hours
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
