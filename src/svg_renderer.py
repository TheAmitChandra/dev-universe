"""
SVG Renderer v3.1 — Full-Width Cinematic Solar System for GitHub
================================================================
viewBox = 880 × 440   (matches GitHub's content column exactly)
width="880" height="440" ensures GitHub renders it full-width with
no shrinkage.  All elements are scaled to fill this space boldly.
"""

from typing import Dict, List, Any
import math
import random

from .universe_generator import UniverseData
from .repo_analyzer import PlanetData, AsteroidData
from .animation_engine import AnimationEngine, _lighten, _darken

# ── Viewport — sized to GitHub's content column ──────────────────

W, H = 880, 440
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
    # Public
    # ══════════════════════════════════════════════════════════════════

    def render(self, universe: UniverseData) -> str:
        print("🎨 Rendering SVG universe v3.1…")
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
        print(f"✅ SVG done ({len(svg):,} bytes)")
        return svg

    # ══════════════════════════════════════════════════════════════════
    # Header — explicit px width/height so GitHub renders full-size
    # ══════════════════════════════════════════════════════════════════

    def _header(self) -> str:
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg"\n'
            f'     xmlns:xlink="http://www.w3.org/1999/xlink"\n'
            f'     viewBox="0 0 {self.w} {self.h}"\n'
            f'     width="{self.w}" height="{self.h}"\n'
            f'     style="background:#030508">\n'
            f'<style>\n'
            f'  text {{ font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }}\n'
            f'</style>'
        )

    # ══════════════════════════════════════════════════════════════════
    # <defs>
    # ══════════════════════════════════════════════════════════════════

    def _defs(self, u: UniverseData) -> str:
        sun = u.sun
        d: list[str] = ["<defs>"]

        d.append(self.anim.bg_gradient())
        d.append(self.anim.sphere_shadow_filter())
        d.append(self.anim.terminator_filter())
        d.append(self.anim.glow_filter("sunGlow", 12, 3))
        d.append(self.anim.glow_filter("planetGlow", 4, 2))
        d.append(self.anim.comet_gradient())
        d.append(self.anim.moon_gradient())
        d.append(self.anim.sun_gradient(sun["color"], sun["glow_color"]))

        for i, p in enumerate(u.planets):
            pid = f"p{i}"
            light = _lighten(p.color, 0.5)
            dark = _darken(p.color, 0.45)
            d.append(self.anim.planet_gradient(pid, p.color, light, dark))
            d.append(self.anim.atmosphere_gradient(pid, p.color))
            d.append(self.anim.glow_filter(f"{pid}Glow", 5, 2))
            if p.stars >= 5:
                d.append(self.anim.ring_gradient(pid, p.color))

        d.append("</defs>")
        return "\n".join(d)

    # ══════════════════════════════════════════════════════════════════
    # Background
    # ══════════════════════════════════════════════════════════════════

    def _background(self) -> str:
        return f'<rect width="{self.w}" height="{self.h}" fill="url(#bgSpace)"/>'

    def _starfield(self, stars: List[Dict]) -> str:
        lines = ["<!-- starfield -->", '<g id="starfield">']
        palette = ["#ffffff", "#cad3f5", "#f5a97f", "#a6da95",
                   "#8aadf4", "#ee99a0", "#f4dbd6"]
        # Re-map star positions from original 1200×600 → 880×440
        sx = self.w / 1200.0
        sy = self.h / 600.0
        for s in stars:
            x = s["x"] * sx
            y = s["y"] * sy
            r = s["size"]
            op = s["opacity"]
            col = random.choice(palette) if r > 1.0 else "#c9d1d9"
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
            (self.w * 0.14, self.h * 0.28, 200, 120, "#1f6feb", 0.08),
            (self.w * 0.82, self.h * 0.58, 220, 130, "#8957e5", 0.07),
            (self.w * 0.50, self.h * 0.88, 180, 100, "#da3633", 0.06),
            (self.w * 0.92, self.h * 0.16, 150,  85, "#3fb950", 0.05),
            (self.w * 0.30, self.h * 0.10, 170,  95, "#58a6ff", 0.05),
        ]
        parts = ["<!-- nebulae -->"]
        for cx, cy, rx, ry, col, op in configs:
            parts.append(
                f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx}" ry="{ry}" '
                f'fill="{col}" opacity="{op}" filter="url(#sunGlow)">'
            )
            parts.append(
                f'  <animate attributeName="opacity" '
                f'values="{op};{op * 2.2:.3f};{op}" dur="20s" repeatCount="indefinite"/>'
            )
            parts.append("</ellipse>")
        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════
    # Orbit tracks
    # ══════════════════════════════════════════════════════════════════

    def _orbit_tracks(self, planets: List[PlanetData]) -> str:
        lines = ["<!-- orbit tracks -->"]
        for p in planets:
            rx, ry = self._radii(p.orbit_distance)
            lines.append(
                f'<ellipse cx="{self.cx}" cy="{self.cy}" '
                f'rx="{rx:.1f}" ry="{ry:.1f}" '
                f'fill="none" stroke="#30363d" stroke-width="0.7" '
                f'opacity="0.35" stroke-dasharray="4 7"/>'
            )
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════
    # Sun — BIG and bold
    # ══════════════════════════════════════════════════════════════════

    def _sun(self, sun: Dict[str, Any]) -> str:
        r = sun["size"]
        name = sun["name"]
        return (
            f'\n<!-- SUN: {name} -->\n'
            f'<g transform="translate({self.cx},{self.cy})">\n'
            # outermost corona
            f'  <circle r="{r * 3.8:.0f}" fill="url(#sunCorona)" opacity="0.4">\n'
            f'{self.anim.pulse("r", r * 3.8, r * 4.3, 9)}\n'
            f'  </circle>\n'
            # middle corona
            f'  <circle r="{r * 2.5:.0f}" fill="url(#sunCorona)" opacity="0.45" filter="url(#sunGlow)">\n'
            f'{self.anim.pulse("r", r * 2.5, r * 2.8, 6)}\n'
            f'  </circle>\n'
            # inner corona
            f'  <circle r="{r * 1.6:.0f}" fill="url(#sunCorona)" opacity="0.55">\n'
            f'{self.anim.pulse("r", r * 1.6, r * 1.75, 4)}\n'
            f'  </circle>\n'
            # body
            f'  <circle r="{r}" fill="url(#sunGrad)" filter="url(#sunGlow)">\n'
            f'{self.anim.pulse("opacity", 0.92, 1.0, 3)}\n'
            f'  </circle>\n'
            # specular highlight
            f'  <ellipse cx="{-r * 0.2:.1f}" cy="{-r * 0.22:.1f}" '
            f'rx="{r * 0.4:.1f}" ry="{r * 0.28:.1f}" '
            f'fill="#fff" opacity="0.5"/>\n'
            # label
            f'  <text y="{r + 22}" text-anchor="middle" '
            f'fill="#e6edf3" font-size="15" font-weight="700" '
            f'opacity="0.9">{name}</text>\n'
            f'</g>'
        )

    # ══════════════════════════════════════════════════════════════════
    # Depth-split planets
    # ══════════════════════════════════════════════════════════════════

    def _back_planets(self, planets: List[PlanetData]) -> str:
        lines = ["<!-- back-half planets -->"]
        for i, p in enumerate(planets):
            if self._starts_behind(p.angle_offset):
                lines.append(self._planet(p, i))
        return "\n".join(lines)

    def _front_planets(self, planets: List[PlanetData]) -> str:
        lines = ["<!-- front-half planets -->"]
        for i, p in enumerate(planets):
            if not self._starts_behind(p.angle_offset):
                lines.append(self._planet(p, i))
        return "\n".join(lines)

    @staticmethod
    def _starts_behind(angle: float) -> bool:
        return 180 <= (angle % 360) < 360

    # ──────────────────────────────────────────────────────────────
    # Single planet
    # ──────────────────────────────────────────────────────────────

    def _planet(self, p: PlanetData, idx: int) -> str:
        pid = f"p{idx}"
        rx, ry = self._radii(p.orbit_distance)
        r = p.size
        dur = p.orbit_duration
        begin = round((p.angle_offset / 360.0) * dur, 1)

        ring_svg = ""
        if p.stars >= 5:
            ring_svg = self._ring(pid, r)

        moon_svg = self._moons(p, r)

        return (
            f'\n<!-- {p.name} -->\n'
            f'<g transform="translate({self.cx},{self.cy})">\n'
            f'{self.anim.orbit_motion(rx, ry, dur, begin)}\n'
            f'  <g>\n'
            f'{self.anim.depth_scale_anim(dur, begin, 1.2, 0.65)}\n'
            f'{self.anim.depth_opacity_anim(dur, begin, 1.0, 0.5)}\n'
            # atmosphere halo
            f'    <circle r="{r + 8}" fill="url(#{pid}Atmo)" filter="url(#{pid}Glow)"/>\n'
            # planet body
            f'    <circle r="{r}" fill="url(#{pid}Grad)" filter="url(#sphereShadow)">\n'
            f'      <title>{p.name}  ⭐ {p.stars}  {p.language}</title>\n'
            f'    </circle>\n'
            # terminator
            f'    <circle r="{r}" fill="url(#terminator)" opacity="0.5"/>\n'
            # specular
            f'    <ellipse cx="{-r * 0.28:.1f}" cy="{-r * 0.28:.1f}" '
            f'rx="{r * 0.36:.1f}" ry="{r * 0.24:.1f}" '
            f'fill="#fff" opacity="0.5"/>\n'
            f'{ring_svg}'
            f'{moon_svg}'
            # name label
            f'    <text y="{r + 16}" text-anchor="middle" '
            f'fill="#e6edf3" font-size="12" font-weight="600" '
            f'opacity="0.9">{p.name}</text>\n'
            # star count
            f'    <text y="{r + 28}" text-anchor="middle" '
            f'fill="#8b949e" font-size="10" opacity="0.75">'
            f'⭐ {p.stars}</text>\n'
            f'  </g>\n'
            f'</g>'
        )

    # ── Ring ──────────────────────────────────────────────────────

    @staticmethod
    def _ring(pid: str, r: float) -> str:
        rx = r * 1.8
        ry = r * 0.38
        return (
            f'    <ellipse cx="0" cy="0" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="none" stroke="url(#{pid}Ring)" '
            f'stroke-width="3.5" opacity="0.6"/>\n'
        )

    # ── Moons ─────────────────────────────────────────────────────

    def _moons(self, p: PlanetData, planet_r: float) -> str:
        if p.moons == 0:
            return ""
        lines = ["    <!-- moons -->"]
        moon_orbit = planet_r + 14
        moon_r = max(3, planet_r * 0.2)
        for m in range(p.moons):
            dur_m = round(3.0 + m * 0.8, 1)
            begin_m = round(m * 1.1, 1)
            mrx = moon_orbit + m * 6
            mry = moon_orbit * 0.45 + m * 2.5
            path = self.anim.ellipse_orbit_path(mrx, mry)
            lines.append(
                f'    <circle r="{moon_r:.1f}" fill="url(#moonGrad)" opacity="0.9">\n'
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
                    f'  <circle r="4" fill="#f85149" opacity="0.85">\n'
                    f'    <title>Issue #{a.number}: {a.title}</title>\n'
                    f'{motion}\n'
                    f'  </circle>'
                )
            else:
                lines.append(
                    f'  <g>\n'
                    f'    <ellipse rx="30" ry="4" fill="url(#cometTail)" opacity="0.75">\n'
                    f'{motion}\n'
                    f'    </ellipse>\n'
                    f'    <circle r="5.5" fill="#58a6ff" opacity="0.95" filter="url(#planetGlow)">\n'
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
        y0 = self.h - 50
        return (
            f'\n<!-- info panel -->\n'
            f'<g>\n'
            f'  <rect x="12" y="{y0 - 14}" width="420" height="56" rx="10" '
            f'fill="#0d1117" opacity="0.75" stroke="#21262d" stroke-width="1"/>\n'
            f'  <text x="24" y="{y0 + 4}" fill="#58a6ff" font-size="14" '
            f'font-weight="700">@{u.username}\'s Dev Universe</text>\n'
            f'  <text x="24" y="{y0 + 20}" fill="#e6edf3" font-size="12">'
            f'🪐 {m["planet_count"]} repos · ⭐ {m["total_stars"]} stars · '
            f'💫 {m["total_commits"]} commits</text>\n'
            f'  <text x="24" y="{y0 + 36}" fill="#8b949e" font-size="10">'
            f'☄️ {m["total_issues"]} issues · 🚀 {m["total_prs"]} PRs · '
            f'auto-updates every 12 h</text>\n'
            f'</g>'
        )

    # ══════════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════════

    def _radii(self, orbit_distance: float):
        """Map orbit_distance → (rx, ry).

        orbit_distance comes from the analyzer (80–380 range now).
        ry is compressed to ~38% for perspective tilt.
        """
        rx = orbit_distance
        ry = orbit_distance * 0.38
        return rx, ry
