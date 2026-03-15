"""
SVG Renderer v2 — Premium 3-D Galaxy Visualization
===================================================
Key design decisions vs. v1
- **Elliptical orbits** (rx ≫ ry) create perspective-tilt illusion
- **Depth layering**: back-half orbits → sun → front-half orbits
- **Rotate transforms** instead of animateMotion for buttery-smooth motion
- **3-D planet shading**: highlight spot + radial gradient + drop-shadow
- **Rich background**: dense starfield, nebula blobs, faint grid rings
- No JavaScript — pure SVG + CSS animations, compatible with GitHub README
"""

from typing import Dict, List, Any
import math
import random

from .universe_generator import UniverseData
from .repo_analyzer import PlanetData, AsteroidData
from .animation_engine import AnimationEngine

# ---------------------------------------------------------------------------

W, H = 1200, 600          # viewBox — scales to any container
CX, CY = W / 2, H / 2    # universe center


class SVGRenderer:
    """Renders UniverseData → animated SVG string."""

    def __init__(self, width: int = W, height: int = H):
        self.w = width
        self.h = height
        self.cx = width / 2
        self.cy = height / 2
        self.anim = AnimationEngine()

    # ── public entry point ────────────────────────────────────────────

    def render(self, universe: UniverseData) -> str:
        print("🎨 Rendering premium SVG universe…")
        parts: list[str] = [
            self._header(),
            self._defs(universe),
            self._background(),
            self._starfield(universe.background_stars),
            self._nebulae(),
            self._orbit_rings(universe.planets),
            self._back_planets(universe.planets),
            self._sun(universe.sun),
            self._front_planets(universe.planets),
            self._asteroids(universe.asteroids),
            self._overlay(universe),
            "</svg>",
        ]
        print("✅ SVG rendering complete!")
        return "\n".join(parts)

    # ── header ────────────────────────────────────────────────────────

    def _header(self) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {self.w} {self.h}" width="100%" height="100%"
     style="background:#060a14">
<style>
  text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}
</style>'''

    # ── defs (gradients + filters) ────────────────────────────────────

    def _defs(self, u: UniverseData) -> str:
        sun = u.sun
        d = ["<defs>"]
        d.append(self.anim.bg_gradient())
        d.append(self.anim.shadow_filter())
        d.append(self.anim.glow_filter("sunGlow", 12))
        d.append(self.anim.glow_filter("planetGlow", 3))
        d.append(self.anim.sun_gradient(sun["color"], sun["glow_color"]))
        d.append(self.anim.comet_gradient())
        d.append(self.anim.moon_gradient())

        for i, p in enumerate(u.planets):
            pid = f"p{i}"
            light = _lighten(p.color, 0.55)
            dark = _darken(p.color, 0.45)
            d.append(self.anim.planet_gradient(pid, p.color, light, dark))
            d.append(self.anim.glow_filter(f"{pid}Glow", 2.5))

        d.append("</defs>")
        return "\n".join(d)

    # ── background ────────────────────────────────────────────────────

    def _background(self) -> str:
        return f'''
<!-- deep-space background -->
<rect width="{self.w}" height="{self.h}" fill="url(#bgCenter)"/>'''

    # ── starfield ─────────────────────────────────────────────────────

    def _starfield(self, stars: List[Dict]) -> str:
        lines = ["<!-- starfield -->", '<g id="starfield">']
        for s in stars:
            x, y, r, op = s["x"], s["y"], s["size"], s["opacity"]
            col = "#fff" if op > 0.65 else ("#c9d1d9" if op > 0.4 else "#6e7681")
            lines.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op:.2f}">')
            lines.append(self.anim.twinkle(s["twinkle_delay"]))
            lines.append("  </circle>")
        lines.append("</g>")
        return "\n".join(lines)

    # ── nebulae ───────────────────────────────────────────────────────

    def _nebulae(self) -> str:
        configs = [
            (self.w * 0.18, self.h * 0.35, 220, 130, "#1f6feb", 0.09),
            (self.w * 0.78, self.h * 0.55, 260, 150, "#8957e5", 0.07),
            (self.w * 0.50, self.h * 0.80, 200, 110, "#da3633", 0.06),
            (self.w * 0.88, self.h * 0.20, 170,  95, "#3fb950", 0.05),
        ]
        parts = ["<!-- nebulae -->"]
        for cx, cy, rx, ry, col, op in configs:
            parts.append(
                f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx}" ry="{ry}" '
                f'fill="{col}" opacity="{op}" filter="url(#sunGlow)">'
            )
            parts.append(f'  <animate attributeName="opacity" values="{op};{op*1.8:.3f};{op}" dur="18s" repeatCount="indefinite"/>')
            parts.append("</ellipse>")
        return "\n".join(parts)

    # ── orbit rings ───────────────────────────────────────────────────

    def _orbit_rings(self, planets: List[PlanetData]) -> str:
        """Faint elliptical orbit guides drawn *below* all planets."""
        lines = ["<!-- orbit rings -->"]
        for i, p in enumerate(planets):
            rx, ry = self._orbit_radii(p.orbit_distance)
            lines.append(
                f'<ellipse cx="{self.cx}" cy="{self.cy}" rx="{rx:.1f}" ry="{ry:.1f}" '
                f'fill="none" stroke="#30363d" stroke-width="0.8" opacity="0.35" '
                f'stroke-dasharray="4 6"/>'
            )
        return "\n".join(lines)

    # ── sun ───────────────────────────────────────────────────────────

    def _sun(self, sun: Dict[str, Any]) -> str:
        r = sun["size"]
        name = sun["name"]
        return f'''
<!-- ☀ Sun: {name} -->
<g transform="translate({self.cx},{self.cy})">
  <!-- corona (outermost) -->
  <circle r="{r*3}" fill="url(#sunCorona)" opacity="0.6">
{self.anim.pulse("r", r*3, r*3.4, 7)}
  </circle>
  <!-- mid glow -->
  <circle r="{r*1.7}" fill="url(#sunCorona)" opacity="0.45" filter="url(#sunGlow)">
{self.anim.pulse("r", r*1.7, r*1.9, 5)}
  </circle>
  <!-- body -->
  <circle r="{r}" fill="url(#sunGrad)" filter="url(#sunGlow)">
{self.anim.pulse("opacity", 0.92, 1.0, 4)}
  </circle>
  <!-- specular highlight on sphere -->
  <ellipse cx="{-r*0.22:.1f}" cy="{-r*0.22:.1f}" rx="{r*0.32:.1f}" ry="{r*0.22:.1f}"
           fill="#fff" opacity="0.55"/>
  <!-- label -->
  <text y="{r+22}" text-anchor="middle" fill="#c9d1d9" font-size="15" font-weight="700" opacity="0.9">{name}</text>
</g>'''

    # ── depth-sorted planets ──────────────────────────────────────────

    def _back_planets(self, planets: List[PlanetData]) -> str:
        """Planets whose initial position is on the *back* half of their orbit
        (behind the sun). We draw them BEFORE the sun so they appear behind."""
        lines = ["<!-- back-half planets (behind sun) -->"]
        for i, p in enumerate(planets):
            if self._is_back_half(p.angle_offset):
                lines.append(self._planet_group(p, i))
        return "\n".join(lines)

    def _front_planets(self, planets: List[PlanetData]) -> str:
        """Planets in front of the sun — drawn AFTER sun."""
        lines = ["<!-- front-half planets (in front of sun) -->"]
        for i, p in enumerate(planets):
            if not self._is_back_half(p.angle_offset):
                lines.append(self._planet_group(p, i))
        return "\n".join(lines)

    @staticmethod
    def _is_back_half(angle: float) -> bool:
        """Angles 180-360 are 'behind' the sun in our perspective."""
        return 180 <= (angle % 360) < 360

    # ── single planet ─────────────────────────────────────────────────

    def _planet_group(self, p: PlanetData, idx: int) -> str:
        pid = f"p{idx}"
        rx, ry = self._orbit_radii(p.orbit_distance)

        # The planet sits at (cx + rx, cy) then gets rotated around (cx, cy)
        planet_cx = self.cx + rx
        planet_cy = self.cy

        # Depth-based scale: when planet is "far" (top of ellipse) it should
        # appear slightly smaller.  We approximate with a fixed size for now
        # but could add animateTransform scale keyed to the rotation angle.
        r = p.size

        moon_svg = self._moons(p, r)

        return f'''
<!-- 🪐 {p.name} -->
<g>
{self.anim.orbit_rotate(self.cx, self.cy, p.orbit_duration, p.angle_offset)}
  <!-- planet at orbital position -->
  <g transform="translate({planet_cx:.1f},{planet_cy:.1f})">
    <!-- shadow beneath planet -->
    <ellipse cx="0" cy="{r*0.85:.1f}" rx="{r*0.7:.1f}" ry="{r*0.18:.1f}" fill="#000" opacity="0.25"/>
    <!-- atmosphere rim -->
    <circle r="{r+3}" fill="none" stroke="{_lighten(p.color, 0.4)}" stroke-width="1.5" opacity="0.3" filter="url(#{pid}Glow)"/>
    <!-- body -->
    <circle r="{r}" fill="url(#{pid}Grad)" filter="url(#dropShadow)">
      <title>{p.name}  ⭐ {p.stars}  {p.language}</title>
    </circle>
    <!-- specular highlight -->
    <ellipse cx="{-r*0.28:.1f}" cy="{-r*0.28:.1f}" rx="{r*0.32:.1f}" ry="{r*0.2:.1f}" fill="#fff" opacity="0.45"/>
{moon_svg}
    <!-- label -->
    <text y="{r+16}" text-anchor="middle" fill="#c9d1d9" font-size="11" font-weight="600" opacity="0.85">{p.name}</text>
    <text y="{r+28}" text-anchor="middle" fill="#8b949e" font-size="9" opacity="0.7">⭐ {p.stars}</text>
  </g>
</g>'''

    # ── moons ─────────────────────────────────────────────────────────

    def _moons(self, p: PlanetData, planet_r: float) -> str:
        if p.moons == 0:
            return ""
        lines = ["    <!-- moons -->"]
        moon_orbit_r = planet_r + 14
        moon_r = max(2.5, planet_r * 0.16)
        for m in range(p.moons):
            angle0 = (360 / p.moons) * m
            dur = round(3 + m * 0.7, 1)
            # Moon sits at (moon_orbit_r, 0) and rotates around planet center (0,0)
            lines.append(f'    <g>')
            lines.append(f'{self.anim.orbit_rotate(0, 0, dur, angle0)}')
            lines.append(f'      <circle cx="{moon_orbit_r}" cy="0" r="{moon_r:.1f}" fill="url(#moonGrad)" opacity="0.85"/>')
            lines.append(f'    </g>')
        return "\n".join(lines)

    # ── asteroids / comets ────────────────────────────────────────────

    def _asteroids(self, asteroids: List[AsteroidData]) -> str:
        if not asteroids:
            return "<!-- no asteroids -->"
        lines = ["<!-- asteroids & comets -->", '<g id="asteroids">']
        for a in asteroids:
            if a.type == "issue":
                lines.append(self._issue(a, len(asteroids)))
            else:
                lines.append(self._comet(a, len(asteroids)))
        lines.append("</g>")
        return "\n".join(lines)

    def _issue(self, a: AsteroidData, total: int) -> str:
        motion = self.anim.comet_motion(a.trajectory_id, total, self.w, self.h)
        return f'''  <circle r="3" fill="#f85149" opacity="0.8">
    <title>Issue #{a.number}: {a.title}</title>
{motion}
  </circle>'''

    def _comet(self, a: AsteroidData, total: int) -> str:
        motion = self.anim.comet_motion(a.trajectory_id, total, self.w, self.h)
        return f'''  <g>
    <ellipse rx="22" ry="3" fill="url(#cometTail)" opacity="0.7">
{motion}
    </ellipse>
    <circle r="4.5" fill="#58a6ff" opacity="0.95" filter="url(#planetGlow)">
      <title>PR #{a.number}: {a.title}</title>
{motion}
    </circle>
  </g>'''

    # ── info overlay ──────────────────────────────────────────────────

    def _overlay(self, u: UniverseData) -> str:
        m = u.metadata
        y0 = self.h - 58
        return f'''
<!-- info panel -->
<g>
  <rect x="16" y="{y0-10}" width="440" height="56" rx="10" fill="#0d1117" opacity="0.75" stroke="#21262d" stroke-width="1"/>
  <text x="28" y="{y0+8}" fill="#58a6ff" font-size="13" font-weight="700">@{u.username}</text>
  <text x="28" y="{y0+24}" fill="#c9d1d9" font-size="11">🪐 {m["planet_count"]} repos · ⭐ {m["total_stars"]} stars · 💫 {m["total_commits"]} commits</text>
  <text x="28" y="{y0+38}" fill="#8b949e" font-size="10">☄️ {m["total_issues"]} issues · 🚀 {m["total_prs"]} PRs · auto-updates every 12 h</text>
</g>'''

    # ── helpers ───────────────────────────────────────────────────────

    def _orbit_radii(self, distance: float) -> tuple[float, float]:
        """Convert linear distance → (rx, ry) for elliptical orbit.
        ry is scaled down to ~0.35 of rx to simulate a 70° viewing tilt."""
        rx = distance
        ry = distance * 0.35
        return rx, ry


# ── colour helpers (module-level) ─────────────────────────────────────

def _lighten(hex_c: str, f: float = 0.3) -> str:
    h = hex_c.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r + (255 - r) * f)
    g = int(g + (255 - g) * f)
    b = int(b + (255 - b) * f)
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken(hex_c: str, f: float = 0.3) -> str:
    h = hex_c.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{int(r*(1-f)):02x}{int(g*(1-f)):02x}{int(b*(1-f)):02x}"
