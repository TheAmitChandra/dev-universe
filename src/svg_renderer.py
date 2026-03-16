"""
SVG Renderer v3 — Cinematic 3-D Solar System
=============================================
Key breakthroughs over v2:
  1. Planets ACTUALLY follow elliptical paths via <animateMotion> with
     real ellipse arc d-strings — not rotate transforms that trace circles.
  2. Depth illusion: each planet also runs a synced <animateTransform scale>
     so it grows as it swings to the front and shrinks when behind the sun.
  3. Opacity pulses in sync — planets dim when in the back half.
  4. Much bolder sun (r=60) with chromatic multi-layer corona.
  5. Saturn-like rings on high-star repos.
  6. Rich starfield with multi-colour temperature, multi-size stars.
  7. Animated nebula clouds in the background.
  8. Proper 3-D sphere shading: radial gradient with highlight/terminator
     overlay, atmospheric glow ring, and drop-shadow beneath.
  9. Dynamic z-ordering approximation: planets with start-offset in the
     back half are drawn before the sun; those starting in the front half
     after. (True dynamic z-order requires JS which GitHub blocks.)
  10. Cover-image size: 1200 × 600 viewBox that scales to any container.

No JavaScript — pure SVG + SMIL animations, fully GitHub README compatible.
"""

from typing import Dict, List, Any
import math
import random

from .universe_generator import UniverseData
from .repo_analyzer import PlanetData, AsteroidData
from .animation_engine import AnimationEngine, _lighten, _darken

# ── Viewport ──────────────────────────────────────────────────────

W, H = 1200, 600
CX, CY = W / 2, H / 2


class SVGRenderer:
    """Renders UniverseData → animated SVG string."""

    def __init__(self, width: int = W, height: int = H):
        self.w = width
        self.h = height
        self.cx = width / 2
        self.cy = height / 2
        self.anim = AnimationEngine()

    # ══════════════════════════════════════════════════════════════════
    # Public entry point
    # ══════════════════════════════════════════════════════════════════

    def render(self, universe: UniverseData) -> str:
        print("🎨 Rendering premium SVG universe v3…")
        parts: list[str] = [
            self._header(),
            self._defs(universe),
            self._background(),
            self._starfield(universe.background_stars),
            self._nebulae(),
            self._orbit_tracks(universe.planets),
            self._back_planets(universe.planets),
            self._sun(universe.sun),
            self._front_planets(universe.planets),
            self._asteroids(universe.asteroids),
            self._overlay(universe),
            "</svg>",
        ]
        svg = "\n".join(parts)
        print(f"✅ SVG rendering complete  ({len(svg):,} bytes)")
        return svg

    # ══════════════════════════════════════════════════════════════════
    # SVG scaffold
    # ══════════════════════════════════════════════════════════════════

    def _header(self) -> str:
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg"\n'
            f'     xmlns:xlink="http://www.w3.org/1999/xlink"\n'
            f'     viewBox="0 0 {self.w} {self.h}"\n'
            f'     width="100%" height="100%"\n'
            f'     style="background:#030508">\n'
            f'<style>\n'
            f'  text {{ font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }}\n'
            f'</style>'
        )

    # ══════════════════════════════════════════════════════════════════
    # <defs> — gradients, filters, clip-paths
    # ══════════════════════════════════════════════════════════════════

    def _defs(self, u: UniverseData) -> str:
        sun = u.sun
        d: list[str] = ["<defs>"]

        # Global
        d.append(self.anim.bg_gradient())
        d.append(self.anim.sphere_shadow_filter())
        d.append(self.anim.terminator_filter())
        d.append(self.anim.glow_filter("sunGlow", 10, 3))
        d.append(self.anim.glow_filter("planetGlow", 3, 2))
        d.append(self.anim.comet_gradient())
        d.append(self.anim.moon_gradient())

        # Sun
        d.append(self.anim.sun_gradient(sun["color"], sun["glow_color"]))

        # Per-planet
        for i, p in enumerate(u.planets):
            pid = f"p{i}"
            light = _lighten(p.color, 0.5)
            dark = _darken(p.color, 0.45)
            d.append(self.anim.planet_gradient(pid, p.color, light, dark))
            d.append(self.anim.atmosphere_gradient(pid, p.color))
            d.append(self.anim.glow_filter(f"{pid}Glow", 4, 2))
            # Rings on popular repos (≥10 stars)
            if p.stars >= 10:
                d.append(self.anim.ring_gradient(pid, p.color))

        d.append("</defs>")
        return "\n".join(d)

    # ══════════════════════════════════════════════════════════════════
    # Background layers
    # ══════════════════════════════════════════════════════════════════

    def _background(self) -> str:
        return f'<rect width="{self.w}" height="{self.h}" fill="url(#bgSpace)"/>'

    def _starfield(self, stars: List[Dict]) -> str:
        lines = ["<!-- ✦ starfield -->", '<g id="starfield">']
        palette = ["#ffffff", "#cad3f5", "#f5a97f", "#a6da95",
                   "#8aadf4", "#ee99a0", "#f4dbd6"]
        for s in stars:
            x, y, r, op = s["x"], s["y"], s["size"], s["opacity"]
            col = random.choice(palette) if r > 1.2 else "#c9d1d9"
            lines.append(
                f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                f'fill="{col}" opacity="{op:.2f}">'
            )
            lines.append(self.anim.twinkle(s["twinkle_delay"]))
            lines.append("  </circle>")
        lines.append("</g>")
        return "\n".join(lines)

    def _nebulae(self) -> str:
        configs = [
            (self.w * 0.15, self.h * 0.30, 250, 140, "#1f6feb", 0.07),
            (self.w * 0.80, self.h * 0.60, 280, 160, "#8957e5", 0.06),
            (self.w * 0.52, self.h * 0.85, 220, 120, "#da3633", 0.05),
            (self.w * 0.90, self.h * 0.18, 180, 100, "#3fb950", 0.04),
            (self.w * 0.35, self.h * 0.12, 200, 110, "#58a6ff", 0.04),
        ]
        parts = ["<!-- nebulae -->"]
        for cx, cy, rx, ry, col, op in configs:
            parts.append(
                f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx}" ry="{ry}" '
                f'fill="{col}" opacity="{op}" filter="url(#sunGlow)">'
            )
            parts.append(
                f'  <animate attributeName="opacity" '
                f'values="{op};{op * 2.0:.3f};{op}" dur="22s" repeatCount="indefinite"/>'
            )
            parts.append("</ellipse>")
        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════
    # Orbit tracks (faint dashed ellipses)
    # ══════════════════════════════════════════════════════════════════

    def _orbit_tracks(self, planets: List[PlanetData]) -> str:
        lines = ["<!-- orbit tracks -->"]
        for p in planets:
            rx, ry = self._radii(p.orbit_distance)
            lines.append(
                f'<ellipse cx="{self.cx}" cy="{self.cy}" '
                f'rx="{rx:.1f}" ry="{ry:.1f}" '
                f'fill="none" stroke="#30363d" stroke-width="0.6" '
                f'opacity="0.3" stroke-dasharray="5 8"/>'
            )
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════
    # Sun
    # ══════════════════════════════════════════════════════════════════

    def _sun(self, sun: Dict[str, Any]) -> str:
        r = sun["size"]
        name = sun["name"]
        return (
            f'\n<!-- ☀ Sun: {name} -->\n'
            f'<g transform="translate({self.cx},{self.cy})">\n'
            # outer corona
            f'  <circle r="{r * 3.5:.0f}" fill="url(#sunCorona)" opacity="0.5">\n'
            f'{self.anim.pulse("r", r * 3.5, r * 4.0, 8)}\n'
            f'  </circle>\n'
            # middle corona
            f'  <circle r="{r * 2.2:.0f}" fill="url(#sunCorona)" opacity="0.4" filter="url(#sunGlow)">\n'
            f'{self.anim.pulse("r", r * 2.2, r * 2.5, 6)}\n'
            f'  </circle>\n'
            # inner corona
            f'  <circle r="{r * 1.5:.0f}" fill="url(#sunCorona)" opacity="0.55">\n'
            f'{self.anim.pulse("r", r * 1.5, r * 1.65, 4)}\n'
            f'  </circle>\n'
            # body
            f'  <circle r="{r}" fill="url(#sunGrad)" filter="url(#sunGlow)">\n'
            f'{self.anim.pulse("opacity", 0.93, 1.0, 3.5)}\n'
            f'  </circle>\n'
            # specular highlight
            f'  <ellipse cx="{-r * 0.22:.1f}" cy="{-r * 0.25:.1f}" '
            f'rx="{r * 0.38:.1f}" ry="{r * 0.25:.1f}" '
            f'fill="#fff" opacity="0.55"/>\n'
            # label
            f'  <text y="{r + 24}" text-anchor="middle" '
            f'fill="#e6edf3" font-size="16" font-weight="700" '
            f'opacity="0.9">{name}</text>\n'
            f'</g>'
        )

    # ══════════════════════════════════════════════════════════════════
    # Depth-split planet rendering
    # ══════════════════════════════════════════════════════════════════

    def _back_planets(self, planets: List[PlanetData]) -> str:
        """Planets whose start angle puts them behind the sun."""
        lines = ["<!-- ── back-half planets (behind sun) ── -->"]
        for i, p in enumerate(planets):
            if self._starts_behind(p.angle_offset):
                lines.append(self._planet(p, i))
        return "\n".join(lines)

    def _front_planets(self, planets: List[PlanetData]) -> str:
        """Planets whose start angle puts them in front of the sun."""
        lines = ["<!-- ── front-half planets (in front of sun) ── -->"]
        for i, p in enumerate(planets):
            if not self._starts_behind(p.angle_offset):
                lines.append(self._planet(p, i))
        return "\n".join(lines)

    @staticmethod
    def _starts_behind(angle: float) -> bool:
        return 180 <= (angle % 360) < 360

    # ──────────────────────────────────────────────────────────────
    # Single planet assembly
    # ──────────────────────────────────────────────────────────────

    def _planet(self, p: PlanetData, idx: int) -> str:
        pid = f"p{idx}"
        rx, ry = self._radii(p.orbit_distance)
        r = p.size
        dur = p.orbit_duration

        # Compute begin offset so planet starts at its angle_offset
        # orbit_motion starts at 3-o'clock (0°). Fraction of dur to
        # advance = angle / 360.
        begin = round((p.angle_offset / 360.0) * dur, 1)

        ring_svg = ""
        if p.stars >= 10:
            ring_svg = self._ring(pid, r)

        moon_svg = self._moons(p, r, dur, begin)

        return (
            f'\n<!-- 🪐 {p.name} -->\n'
            # Outer <g> is centred at universe origin.
            # animateMotion will move it along the ellipse around (0,0).
            f'<g transform="translate({self.cx},{self.cy})">\n'
            f'{self.anim.orbit_motion(rx, ry, dur, begin)}\n'
            # Inner <g> receives depth-scale + depth-opacity
            f'  <g>\n'
            f'{self.anim.depth_scale_anim(dur, begin)}\n'
            f'{self.anim.depth_opacity_anim(dur, begin)}\n'
            # atmosphere halo
            f'    <circle r="{r + 6}" fill="url(#{pid}Atmo)" filter="url(#{pid}Glow)"/>\n'
            # planet body
            f'    <circle r="{r}" fill="url(#{pid}Grad)" filter="url(#sphereShadow)">\n'
            f'      <title>{p.name}  ⭐ {p.stars}  {p.language}</title>\n'
            f'    </circle>\n'
            # terminator overlay (day/night)
            f'    <circle r="{r}" fill="url(#terminator)" opacity="0.55"/>\n'
            # specular highlight
            f'    <ellipse cx="{-r * 0.3:.1f}" cy="{-r * 0.3:.1f}" '
            f'rx="{r * 0.35:.1f}" ry="{r * 0.22:.1f}" '
            f'fill="#fff" opacity="0.5"/>\n'
            f'{ring_svg}'
            f'{moon_svg}'
            # label
            f'    <text y="{r + 18}" text-anchor="middle" '
            f'fill="#e6edf3" font-size="11" font-weight="600" '
            f'opacity="0.85">{p.name}</text>\n'
            f'    <text y="{r + 30}" text-anchor="middle" '
            f'fill="#8b949e" font-size="9" opacity="0.7">'
            f'⭐ {p.stars}</text>\n'
            f'  </g>\n'
            f'</g>'
        )

    # ── Saturn-like ring ──────────────────────────────────────────

    @staticmethod
    def _ring(pid: str, planet_r: float) -> str:
        rx = planet_r * 1.7
        ry = planet_r * 0.35
        return (
            f'    <ellipse cx="0" cy="0" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="none" stroke="url(#{pid}Ring)" '
            f'stroke-width="3" opacity="0.6"/>\n'
        )

    # ── Moons ─────────────────────────────────────────────────────

    def _moons(self, p: PlanetData, planet_r: float,
               parent_dur: float, parent_begin: float) -> str:
        if p.moons == 0:
            return ""
        lines = ["    <!-- moons -->"]
        moon_orbit = planet_r + 12
        moon_r = max(2.5, planet_r * 0.18)
        for m in range(p.moons):
            dur_m = round(3.5 + m * 0.9, 1)
            begin_m = round(m * 1.2, 1)
            mrx = moon_orbit + m * 5
            mry = moon_orbit * 0.45 + m * 2
            path = self.anim.ellipse_orbit_path(mrx, mry)
            lines.append(
                f'    <circle r="{moon_r:.1f}" fill="url(#moonGrad)" opacity="0.85">\n'
                f'      <animateMotion path="{path}" '
                f'dur="{dur_m}s" begin="{begin_m}s" repeatCount="indefinite"/>\n'
                f'    </circle>'
            )
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════
    # Asteroids / comets
    # ══════════════════════════════════════════════════════════════════

    def _asteroids(self, asteroids: List[AsteroidData]) -> str:
        if not asteroids:
            return "<!-- no asteroids -->"
        lines = ["<!-- asteroids & comets -->", '<g id="asteroids">']
        for a in asteroids:
            motion = self.anim.comet_motion(a.trajectory_id, len(asteroids),
                                            self.w, self.h)
            if a.type == "issue":
                lines.append(
                    f'  <circle r="3.5" fill="#f85149" opacity="0.8">\n'
                    f'    <title>Issue #{a.number}: {a.title}</title>\n'
                    f'{motion}\n'
                    f'  </circle>'
                )
            else:
                lines.append(
                    f'  <g>\n'
                    f'    <ellipse rx="26" ry="3.5" fill="url(#cometTail)" opacity="0.7">\n'
                    f'{motion}\n'
                    f'    </ellipse>\n'
                    f'    <circle r="5" fill="#58a6ff" opacity="0.95" filter="url(#planetGlow)">\n'
                    f'      <title>PR #{a.number}: {a.title}</title>\n'
                    f'{motion}\n'
                    f'    </circle>\n'
                    f'  </g>'
                )
        lines.append("</g>")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════
    # Info overlay
    # ══════════════════════════════════════════════════════════════════

    def _overlay(self, u: UniverseData) -> str:
        m = u.metadata
        y0 = self.h - 56
        return (
            f'\n<!-- info panel -->\n'
            f'<g>\n'
            f'  <rect x="14" y="{y0 - 12}" width="460" height="60" rx="12" '
            f'fill="#0d1117" opacity="0.72" stroke="#21262d" stroke-width="1"/>\n'
            f'  <text x="26" y="{y0 + 6}" fill="#58a6ff" font-size="14" '
            f'font-weight="700">@{u.username}\'s Dev Universe</text>\n'
            f'  <text x="26" y="{y0 + 22}" fill="#e6edf3" font-size="11">'
            f'🪐 {m["planet_count"]} repos · ⭐ {m["total_stars"]} stars · '
            f'💫 {m["total_commits"]} commits</text>\n'
            f'  <text x="26" y="{y0 + 38}" fill="#8b949e" font-size="10">'
            f'☄️ {m["total_issues"]} issues · 🚀 {m["total_prs"]} PRs · '
            f'auto-updates every 12 h</text>\n'
            f'</g>'
        )

    # ══════════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════════

    def _radii(self, orbit_distance: float):
        """Convert logical orbit_distance to (rx, ry) for the tilted ellipse.

        rx is the full semi-major axis; ry is compressed to ~35 % for
        the perspective-tilt illusion.
        """
        rx = orbit_distance
        ry = orbit_distance * 0.35
        return rx, ry
