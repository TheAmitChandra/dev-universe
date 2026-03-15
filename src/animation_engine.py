"""
Animation Engine v2
Generates premium SVG animation elements with 3D orbital mechanics.
Uses elliptical orbits with rotate transforms for realistic motion.
"""

import math
import random
from typing import Tuple


class AnimationEngine:
    """Generates SVG animation and filter definitions for 3D universe."""

    # ── Filters & Gradients ──────────────────────────────────────────

    @staticmethod
    def sun_gradient(sun_color: str, glow_color: str) -> str:
        return f'''
  <radialGradient id="sunGrad" cx="40%" cy="40%">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="1"/>
    <stop offset="20%"  stop-color="{glow_color}" stop-opacity="1"/>
    <stop offset="60%"  stop-color="{sun_color}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{sun_color}" stop-opacity="0.8"/>
  </radialGradient>
  <radialGradient id="sunCorona" cx="50%" cy="50%">
    <stop offset="0%"   stop-color="{glow_color}" stop-opacity="0.6"/>
    <stop offset="50%"  stop-color="{glow_color}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{sun_color}" stop-opacity="0"/>
  </radialGradient>'''

    @staticmethod
    def planet_gradient(pid: str, color: str, light: str, dark: str) -> str:
        return f'''
  <radialGradient id="{pid}Grad" cx="35%" cy="30%">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="0.9"/>
    <stop offset="15%"  stop-color="{light}" stop-opacity="1"/>
    <stop offset="55%"  stop-color="{color}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{dark}" stop-opacity="1"/>
  </radialGradient>'''

    @staticmethod
    def glow_filter(fid: str, std: float = 4) -> str:
        return f'''
  <filter id="{fid}" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{std}" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''

    @staticmethod
    def shadow_filter() -> str:
        return '''
  <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
    <feOffset dx="0" dy="3" result="shifted"/>
    <feComponentTransfer result="shadow"><feFuncA type="linear" slope="0.45"/></feComponentTransfer>
    <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''

    @staticmethod
    def bg_gradient() -> str:
        return '''
  <radialGradient id="bgCenter" cx="50%" cy="50%">
    <stop offset="0%"   stop-color="#161b33" stop-opacity="1"/>
    <stop offset="100%" stop-color="#060a14" stop-opacity="1"/>
  </radialGradient>'''

    @staticmethod
    def comet_gradient() -> str:
        return '''
  <linearGradient id="cometTail" x1="0%" y1="50%" x2="100%" y2="50%">
    <stop offset="0%"   stop-color="#79c0ff" stop-opacity="1"/>
    <stop offset="100%" stop-color="#79c0ff" stop-opacity="0"/>
  </linearGradient>'''

    @staticmethod
    def moon_gradient() -> str:
        return '''
  <radialGradient id="moonGrad" cx="35%" cy="35%">
    <stop offset="0%"  stop-color="#e6edf3" stop-opacity="1"/>
    <stop offset="100%" stop-color="#6e7681" stop-opacity="1"/>
  </radialGradient>'''

    # ── Animations ───────────────────────────────────────────────────

    @staticmethod
    def orbit_rotate(cx: float, cy: float, dur: float, start_angle: float = 0) -> str:
        """Smooth rotate transform around (cx, cy)."""
        return f'''    <animateTransform attributeName="transform" type="rotate"
      from="{start_angle} {cx} {cy}" to="{start_angle + 360} {cx} {cy}"
      dur="{dur}s" repeatCount="indefinite"/>'''

    @staticmethod
    def pulse(attr: str, v1, v2, dur: float) -> str:
        return f'''    <animate attributeName="{attr}" values="{v1};{v2};{v1}" dur="{dur}s" repeatCount="indefinite"/>'''

    @staticmethod
    def twinkle(delay: float) -> str:
        dur = round(random.uniform(2, 5), 1)
        return f'''    <animate attributeName="opacity" values="0.2;1;0.2" dur="{dur}s" begin="{round(delay,1)}s" repeatCount="indefinite"/>'''

    @staticmethod
    def comet_motion(tid: int, total: int, w: int, h: int) -> str:
        """Create a straight-line comet trajectory across the viewport."""
        random.seed(tid + 9999)
        edge = tid % 4
        if edge == 0:
            sx, sy = random.uniform(0.1*w, 0.9*w), -20
            ex, ey = random.uniform(0.1*w, 0.9*w), h + 20
        elif edge == 1:
            sx, sy = w + 20, random.uniform(0.1*h, 0.9*h)
            ex, ey = -20, random.uniform(0.1*h, 0.9*h)
        elif edge == 2:
            sx, sy = random.uniform(0.1*w, 0.9*w), h + 20
            ex, ey = random.uniform(0.1*w, 0.9*w), -20
        else:
            sx, sy = -20, random.uniform(0.1*h, 0.9*h)
            ex, ey = w + 20, random.uniform(0.1*h, 0.9*h)
        mx = (sx+ex)/2 + random.uniform(-200, 200)
        my = (sy+ey)/2 + random.uniform(-60, 60)
        dur = round(random.uniform(18, 40), 1)
        delay = round((tid / max(total, 1)) * 12, 1)
        random.seed()
        return f'''    <animateMotion path="M{sx:.0f},{sy:.0f} Q{mx:.0f},{my:.0f} {ex:.0f},{ey:.0f}"
      dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'''
