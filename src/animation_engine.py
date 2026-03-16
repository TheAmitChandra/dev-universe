"""
Animation Engine v3 — Cinematic 3-D Solar System
=================================================
Core insight: `animateTransform rotate` around a center only produces
CIRCLES, not ellipses.  To get real elliptical orbits we use
`<animateMotion path="...">` with a true SVG ellipse arc path, AND
pair it with an `<animate>` on `scale` keyed to the same period so
planets grow as they move to the "front" and shrink in the "back".

Additionally we generate rich filter stacks for:
  - 3-D sphere illusion (radial gradient + specular + terminator shadow)
  - Atmospheric glow (double blur merge)
  - Realistic sun with chromatic corona layers
"""

import math
import random


class AnimationEngine:
    """Generates SVG <defs>, filters, gradients, and animation elements."""

    # ────────────────────────────────────────────────────────────────
    # Elliptical orbit path  (THE critical piece that v2 got wrong)
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def ellipse_orbit_path(rx: float, ry: float) -> str:
        """Return an SVG path d-string for a centered ellipse at origin.

        The planet group is translated to (cx, cy) already, so the
        orbit path is centred at (0,0).

        We draw two arcs:  right-half then left-half.
        """
        return (
            f"M {rx},0 "
            f"A {rx},{ry} 0 0,1 {-rx},0 "
            f"A {rx},{ry} 0 0,1 {rx},0 Z"
        )

    @staticmethod
    def orbit_motion(rx: float, ry: float, dur: float, begin: float = 0) -> str:
        """<animateMotion> that follows the ellipse path.

        `begin` offsets the animation start so planets don't all begin
        at 3-o'clock.
        """
        path = AnimationEngine.ellipse_orbit_path(rx, ry)
        return (
            f'    <animateMotion path="{path}" '
            f'dur="{dur}s" begin="{begin:.1f}s" '
            f'repeatCount="indefinite" calcMode="linear" rotate="auto"/>'
        )

    @staticmethod
    def depth_scale_anim(dur: float, begin: float = 0,
                         front: float = 1.15, back: float = 0.7) -> str:
        """Animate scale so planets look bigger in front, smaller behind.

        Key-times synced to orbit_motion (which starts at 3-o'clock,
        goes clockwise):
          0%   → 3 o'clock  (middle depth)
          25%  → 6 o'clock  (front — biggest)
          50%  → 9 o'clock  (middle depth)
          75%  → 12 o'clock (back — smallest)
          100% → 3 o'clock  (back to start)
        """
        mid = round((front + back) / 2, 3)
        return (
            f'    <animateTransform attributeName="transform" type="scale" '
            f'values="{mid};{front};{mid};{back};{mid}" '
            f'keyTimes="0;0.25;0.5;0.75;1" '
            f'dur="{dur}s" begin="{begin:.1f}s" '
            f'repeatCount="indefinite" additive="sum"/>'
        )

    @staticmethod
    def depth_opacity_anim(dur: float, begin: float = 0,
                           front_op: float = 1.0, back_op: float = 0.55) -> str:
        """Fade planets slightly when behind the sun for depth cue."""
        mid = round((front_op + back_op) / 2, 2)
        return (
            f'    <animate attributeName="opacity" '
            f'values="{mid};{front_op};{mid};{back_op};{mid}" '
            f'keyTimes="0;0.25;0.5;0.75;1" '
            f'dur="{dur}s" begin="{begin:.1f}s" '
            f'repeatCount="indefinite"/>'
        )

    # ────────────────────────────────────────────────────────────────
    # Gradients
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def sun_gradient(color: str, glow: str) -> str:
        return f'''
  <!-- sun core gradient -->
  <radialGradient id="sunGrad" cx="38%" cy="38%" r="60%" fx="35%" fy="35%">
    <stop offset="0%"  stop-color="#fff"/>
    <stop offset="18%" stop-color="{glow}"/>
    <stop offset="55%" stop-color="{color}"/>
    <stop offset="100%" stop-color="{_darken(color, 0.5)}"/>
  </radialGradient>
  <!-- corona glow -->
  <radialGradient id="sunCorona" cx="50%" cy="50%" r="50%">
    <stop offset="0%"  stop-color="{glow}" stop-opacity="0.55"/>
    <stop offset="45%" stop-color="{color}" stop-opacity="0.12"/>
    <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
  </radialGradient>'''

    @staticmethod
    def planet_gradient(pid: str, color: str, light: str, dark: str) -> str:
        """3-D sphere gradient: bright highlight top-left, dark limb bottom-right."""
        return f'''
  <radialGradient id="{pid}Grad" cx="32%" cy="28%" r="68%" fx="30%" fy="26%">
    <stop offset="0%"  stop-color="#ffffff" stop-opacity="0.95"/>
    <stop offset="12%" stop-color="{light}"/>
    <stop offset="50%" stop-color="{color}"/>
    <stop offset="85%" stop-color="{dark}"/>
    <stop offset="100%" stop-color="{_darken(dark, 0.55)}" stop-opacity="0.95"/>
  </radialGradient>'''

    @staticmethod
    def atmosphere_gradient(pid: str, color: str) -> str:
        """Transparent halo around planet for atmosphere look."""
        return f'''
  <radialGradient id="{pid}Atmo" cx="50%" cy="50%" r="50%">
    <stop offset="70%"  stop-color="{color}" stop-opacity="0"/>
    <stop offset="88%"  stop-color="{_lighten(color, 0.4)}" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="{_lighten(color, 0.6)}" stop-opacity="0"/>
  </radialGradient>'''

    # ────────────────────────────────────────────────────────────────
    # Filters
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def glow_filter(fid: str, std: float = 6, layers: int = 3) -> str:
        """Multi-layer blur for a rich glow."""
        merges = "".join(
            f'<feMergeNode in="b{j}"/>' for j in range(layers)
        )
        blurs = "\n    ".join(
            f'<feGaussianBlur in="SourceGraphic" stdDeviation="{std * (j + 1)}" result="b{j}"/>'
            for j in range(layers)
        )
        return f'''
  <filter id="{fid}" x="-200%" y="-200%" width="500%" height="500%">
    {blurs}
    <feMerge>{merges}<feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''

    @staticmethod
    def sphere_shadow_filter() -> str:
        """Soft drop shadow beneath each planet (cast 'downward')."""
        return '''
  <filter id="sphereShadow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="blur"/>
    <feOffset dx="0" dy="4" result="off"/>
    <feComponentTransfer result="shadow">
      <feFuncA type="linear" slope="0.5"/>
    </feComponentTransfer>
    <feMerge>
      <feMergeNode in="shadow"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>'''

    @staticmethod
    def terminator_filter() -> str:
        """Simulates the day/night terminator across a sphere.

        A soft black→transparent linear gradient masked over the planet
        body creates a visible dark-side crescent.
        """
        return '''
  <linearGradient id="terminator" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%"  stop-color="#000" stop-opacity="0"/>
    <stop offset="55%" stop-color="#000" stop-opacity="0"/>
    <stop offset="80%" stop-color="#000" stop-opacity="0.38"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0.6"/>
  </linearGradient>'''

    @staticmethod
    def bg_gradient() -> str:
        return '''
  <radialGradient id="bgSpace" cx="50%" cy="50%" r="75%">
    <stop offset="0%"  stop-color="#0f1729"/>
    <stop offset="100%" stop-color="#030508"/>
  </radialGradient>'''

    @staticmethod
    def comet_gradient() -> str:
        return '''
  <linearGradient id="cometTail" x1="0%" y1="50%" x2="100%" y2="50%">
    <stop offset="0%"  stop-color="#79c0ff" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="#79c0ff" stop-opacity="0"/>
  </linearGradient>'''

    @staticmethod
    def moon_gradient() -> str:
        return '''
  <radialGradient id="moonGrad" cx="35%" cy="30%" r="65%">
    <stop offset="0%"  stop-color="#e6edf3"/>
    <stop offset="100%" stop-color="#484f58"/>
  </radialGradient>'''

    @staticmethod
    def ring_gradient(pid: str, color: str) -> str:
        """Saturn-like ring gradient for high-star repos."""
        light = _lighten(color, 0.5)
        return f'''
  <linearGradient id="{pid}Ring" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%"  stop-color="{light}" stop-opacity="0.5"/>
    <stop offset="50%" stop-color="{color}" stop-opacity="0.2"/>
    <stop offset="100%" stop-color="{light}" stop-opacity="0.5"/>
  </linearGradient>'''

    # ────────────────────────────────────────────────────────────────
    # Simple element animations
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def pulse(attr: str, v1, v2, dur: float) -> str:
        return (
            f'    <animate attributeName="{attr}" '
            f'values="{v1};{v2};{v1}" dur="{dur}s" repeatCount="indefinite"/>'
        )

    @staticmethod
    def twinkle(delay: float) -> str:
        dur = round(random.uniform(2.5, 6), 1)
        return (
            f'    <animate attributeName="opacity" '
            f'values="0.15;1;0.15" dur="{dur}s" '
            f'begin="{round(delay, 1)}s" repeatCount="indefinite"/>'
        )

    @staticmethod
    def comet_motion(tid: int, total: int, w: int, h: int) -> str:
        """Quadratic Bezier path across the viewport for asteroids/comets."""
        random.seed(tid + 7777)
        edge = tid % 4
        if edge == 0:
            sx, sy = random.uniform(0.05 * w, 0.95 * w), -30
            ex, ey = random.uniform(0.05 * w, 0.95 * w), h + 30
        elif edge == 1:
            sx, sy = w + 30, random.uniform(0.05 * h, 0.95 * h)
            ex, ey = -30, random.uniform(0.05 * h, 0.95 * h)
        elif edge == 2:
            sx, sy = random.uniform(0.05 * w, 0.95 * w), h + 30
            ex, ey = random.uniform(0.05 * w, 0.95 * w), -30
        else:
            sx, sy = -30, random.uniform(0.05 * h, 0.95 * h)
            ex, ey = w + 30, random.uniform(0.05 * h, 0.95 * h)
        mx = (sx + ex) / 2 + random.uniform(-180, 180)
        my = (sy + ey) / 2 + random.uniform(-60, 60)
        dur = round(random.uniform(20, 45), 1)
        delay = round((tid / max(total, 1)) * 14, 1)
        random.seed()
        return (
            f'    <animateMotion path="M{sx:.0f},{sy:.0f} '
            f'Q{mx:.0f},{my:.0f} {ex:.0f},{ey:.0f}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
        )


# ── Colour helpers (module-level) ─────────────────────────────────

def _lighten(hex_color: str, amount: float = 0.4) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken(hex_color: str, amount: float = 0.4) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return f"#{r:02x}{g:02x}{b:02x}"
