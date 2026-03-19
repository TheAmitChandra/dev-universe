"""
Animation Engine v4 — Bright, Luminous 3-D Solar System
========================================================
Critical fix over v3: On a dark/black background, gradients that fade
to black make objects INVISIBLE. v4 ensures:
  - Sun gradient: white → bright glow → saturated color (NEVER black)
  - Planet gradient: white highlight → saturated color → 30% darker
    tint of the same hue (NEVER black/near-black)
  - No "terminator" overlay — it just darkened everything to mush
  - Sphere illusion comes from offset radial gradient alone
"""

import math
import random


class AnimationEngine:
    """SVG <defs>, filters, gradients, and animation primitives."""

    # ────────────────────────────────────────────────────────────────
    # Elliptical orbit path
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def ellipse_orbit_path(rx: float, ry: float) -> str:
        return (
            f"M {rx},0 "
            f"A {rx},{ry} 0 0,1 {-rx},0 "
            f"A {rx},{ry} 0 0,1 {rx},0 Z"
        )

    @staticmethod
    def orbit_motion(rx: float, ry: float, dur: float, begin: float = 0) -> str:
        path = AnimationEngine.ellipse_orbit_path(rx, ry)
        return (
            f'    <animateMotion path="{path}" '
            f'dur="{dur}s" begin="{begin:.1f}s" '
            f'repeatCount="indefinite" calcMode="linear"/>'
        )

    @staticmethod
    def depth_scale_anim(dur: float, begin: float = 0,
                         front: float = 1.18, back: float = 0.7) -> str:
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
                           front_op: float = 1.0, back_op: float = 0.5) -> str:
        mid = round((front_op + back_op) / 2, 2)
        return (
            f'    <animate attributeName="opacity" '
            f'values="{mid};{front_op};{mid};{back_op};{mid}" '
            f'keyTimes="0;0.25;0.5;0.75;1" '
            f'dur="{dur}s" begin="{begin:.1f}s" '
            f'repeatCount="indefinite"/>'
        )

    # ────────────────────────────────────────────────────────────────
    # Sun gradients — BRIGHT, never fading to black
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def sun_gradient(color: str, glow: str) -> str:
        # The sun body should be luminous: white center → glow → color
        # The DARKEST stop is still the full saturated color, never black
        bright = _lighten(color, 0.7)
        return f'''
  <radialGradient id="sunGrad" cx="45%" cy="45%" r="55%">
    <stop offset="0%"  stop-color="#ffffff"/>
    <stop offset="25%" stop-color="{bright}"/>
    <stop offset="65%" stop-color="{glow}"/>
    <stop offset="100%" stop-color="{color}"/>
  </radialGradient>
  <radialGradient id="sunCorona" cx="50%" cy="50%" r="50%">
    <stop offset="0%"  stop-color="{glow}" stop-opacity="0.6"/>
    <stop offset="40%" stop-color="{color}" stop-opacity="0.2"/>
    <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
  </radialGradient>'''

    # ────────────────────────────────────────────────────────────────
    # Planet gradient — VISIBLE 3-D sphere on dark background
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def planet_gradient(pid: str, color: str, light: str, dark: str) -> str:
        """Offset radial gradient: bright highlight → base color → mild shadow.

        Critical: `dark` is only ~30% darker than `color`, NOT black.
        On a dark background, black edges = invisible planet.
        """
        return f'''
  <radialGradient id="{pid}Grad" cx="35%" cy="32%" r="65%">
    <stop offset="0%"  stop-color="#ffffff" stop-opacity="0.9"/>
    <stop offset="18%" stop-color="{light}"/>
    <stop offset="55%" stop-color="{color}"/>
    <stop offset="100%" stop-color="{dark}"/>
  </radialGradient>'''

    @staticmethod
    def atmosphere_gradient(pid: str, color: str) -> str:
        glow = _lighten(color, 0.55)
        return f'''
  <radialGradient id="{pid}Atmo" cx="50%" cy="50%" r="50%">
    <stop offset="60%"  stop-color="{color}" stop-opacity="0"/>
    <stop offset="82%"  stop-color="{glow}" stop-opacity="0.35"/>
    <stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
  </radialGradient>'''

    # ────────────────────────────────────────────────────────────────
    # Filters — simpler, less blur (heavy blur = washed out)
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def glow_filter(fid: str, std: float = 6) -> str:
        return f'''
  <filter id="{fid}" x="-150%" y="-150%" width="400%" height="400%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{std}" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>'''

    @staticmethod
    def bg_gradient() -> str:
        return '''
  <radialGradient id="bgSpace" cx="50%" cy="50%" r="80%">
    <stop offset="0%"  stop-color="#0d1b2a"/>
    <stop offset="100%" stop-color="#020409"/>
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
  <radialGradient id="moonGrad" cx="38%" cy="35%" r="60%">
    <stop offset="0%"  stop-color="#f0f3f6"/>
    <stop offset="100%" stop-color="#8b949e"/>
  </radialGradient>'''

    @staticmethod
    def ring_gradient(pid: str, color: str) -> str:
        light = _lighten(color, 0.55)
        return f'''
  <linearGradient id="{pid}Ring" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%"  stop-color="{light}" stop-opacity="0.55"/>
    <stop offset="50%" stop-color="{color}" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="{light}" stop-opacity="0.55"/>
  </linearGradient>'''

    # ────────────────────────────────────────────────────────────────
    # Simple animations
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
            f'values="0.2;1;0.2" dur="{dur}s" '
            f'begin="{round(delay, 1)}s" repeatCount="indefinite"/>'
        )

    @staticmethod
    def comet_motion(tid: int, total: int, w: int, h: int) -> str:
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
        mx = (sx + ex) / 2 + random.uniform(-150, 150)
        my = (sy + ey) / 2 + random.uniform(-50, 50)
        dur = round(random.uniform(20, 42), 1)
        delay = round((tid / max(total, 1)) * 14, 1)
        random.seed()
        return (
            f'    <animateMotion path="M{sx:.0f},{sy:.0f} '
            f'Q{mx:.0f},{my:.0f} {ex:.0f},{ey:.0f}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
        )


# ── Color helpers ─────────────────────────────────────────────────

def _lighten(hex_color: str, amount: float = 0.4) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken(hex_color: str, amount: float = 0.3) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return f"#{r:02x}{g:02x}{b:02x}"
