"""
Animation Engine
Generates SVG animation elements for the universe.
"""

import math
from typing import Dict, List, Any, Tuple
import random


class AnimationEngine:
    """Generates SVG animation definitions and elements."""
    
    @staticmethod
    def create_orbit_animation(
        planet_id: str,
        orbit_distance: float,
        duration: float,
        angle_offset: float = 0
    ) -> str:
        """
        Create circular orbit animation path for a planet.
        
        Args:
            planet_id: Unique identifier for the planet
            orbit_distance: Radius of orbit in pixels
            duration: Duration of one complete orbit in seconds
            angle_offset: Starting angle offset in degrees
            
        Returns:
            SVG animateMotion element as string
        """
        # Calculate the circular path
        # SVG path for a circle: M cx cy m -r 0 a r r 0 1 0 (r*2) 0 a r r 0 1 0 -(r*2) 0
        r = orbit_distance
        path = f"M 0,0 m -{r},0 a {r},{r} 0 1,1 {r*2},0 a {r},{r} 0 1,1 -{r*2},0"
        
        # Calculate starting rotation based on angle offset
        rotate_transform = f'rotate({angle_offset} 500 500)' if angle_offset != 0 else ''
        
        animation = f'''
    <animateMotion
      dur="{duration}s"
      repeatCount="indefinite"
      path="{path}"
      rotate="auto"
      {f'transform="{rotate_transform}"' if rotate_transform else ''}
    />'''
        
        return animation
    
    @staticmethod
    def create_rotation_animation(duration: float, direction: str = "normal") -> str:
        """
        Create rotation animation for spinning objects.
        
        Args:
            duration: Duration of one complete rotation in seconds
            direction: Animation direction ("normal" or "reverse")
            
        Returns:
            SVG animateTransform element as string
        """
        return f'''
    <animateTransform
      attributeName="transform"
      attributeType="XML"
      type="rotate"
      from="0 0 0"
      to="360 0 0"
      dur="{duration}s"
      repeatCount="indefinite"
      direction="{direction}"
    />'''
    
    @staticmethod
    def create_pulse_animation(
        attribute: str,
        from_value: Any,
        to_value: Any,
        duration: float
    ) -> str:
        """
        Create pulsing animation for glowing effects.
        
        Args:
            attribute: SVG attribute to animate (e.g., "opacity", "r")
            from_value: Starting value
            to_value: Ending value
            duration: Duration of one pulse in seconds
            
        Returns:
            SVG animate element as string
        """
        return f'''
    <animate
      attributeName="{attribute}"
      values="{from_value};{to_value};{from_value}"
      dur="{duration}s"
      repeatCount="indefinite"
    />'''
    
    @staticmethod
    def create_twinkle_animation(delay: float = 0) -> str:
        """
        Create twinkling animation for stars.
        
        Args:
            delay: Animation delay in seconds
            
        Returns:
            SVG animate element as string
        """
        duration = random.uniform(1.5, 3.5)
        return f'''
    <animate
      attributeName="opacity"
      values="0.3;1;0.3"
      dur="{duration}s"
      begin="{delay}s"
      repeatCount="indefinite"
    />'''
    
    @staticmethod
    def create_moon_orbit(
        moon_index: int,
        planet_size: float,
        orbit_radius: float,
        duration: float
    ) -> Tuple[float, float, str]:
        """
        Create moon orbit animation around a planet.
        
        Args:
            moon_index: Index of the moon (0, 1, 2...)
            planet_size: Size of the parent planet
            orbit_radius: Radius of moon's orbit around planet
            duration: Duration of one orbit
            
        Returns:
            Tuple of (moon_x, moon_y, animation_element)
        """
        # Calculate moon starting position
        angle_offset = (360 / 3) * moon_index  # Spread moons evenly
        angle_rad = math.radians(angle_offset)
        
        moon_x = orbit_radius * math.cos(angle_rad)
        moon_y = orbit_radius * math.sin(angle_rad)
        
        # Create orbit path around (0, 0) which will be relative to planet
        path = f"M 0,0 m -{orbit_radius},0 a {orbit_radius},{orbit_radius} 0 1,1 {orbit_radius*2},0 a {orbit_radius},{orbit_radius} 0 1,1 -{orbit_radius*2},0"
        
        animation = f'''
      <animateMotion
        dur="{duration}s"
        repeatCount="indefinite"
        path="{path}"
        begin="{angle_offset/360 * duration}s"
      />'''
        
        return moon_x, moon_y, animation
    
    @staticmethod
    def create_asteroid_trajectory(trajectory_id: int, total_trajectories: int) -> str:
        """
        Create asteroid trajectory animation across the galaxy.
        
        Args:
            trajectory_id: Unique trajectory identifier
            total_trajectories: Total number of asteroid trajectories
            
        Returns:
            SVG animateMotion element as string
        """
        # Generate varied trajectories
        # Some diagonal, some curved
        
        # Randomize based on trajectory_id for consistency
        random.seed(trajectory_id)
        
        # Start from random edge
        edge = trajectory_id % 4  # 0=top, 1=right, 2=bottom, 3=left
        
        if edge == 0:  # Top
            start_x = random.uniform(100, 900)
            start_y = 0
            end_x = random.uniform(100, 900)
            end_y = 1000
        elif edge == 1:  # Right
            start_x = 1000
            start_y = random.uniform(100, 900)
            end_x = 0
            end_y = random.uniform(100, 900)
        elif edge == 2:  # Bottom
            start_x = random.uniform(100, 900)
            start_y = 1000
            end_x = random.uniform(100, 900)
            end_y = 0
        else:  # Left
            start_x = 0
            start_y = random.uniform(100, 900)
            end_x = 1000
            end_y = random.uniform(100, 900)
        
        # Add some curve for variety
        mid_x = (start_x + end_x) / 2 + random.uniform(-200, 200)
        mid_y = (start_y + end_y) / 2 + random.uniform(-200, 200)
        
        # Create curved path
        path = f"M {start_x},{start_y} Q {mid_x},{mid_y} {end_x},{end_y}"
        
        duration = random.uniform(20, 40)
        delay = (trajectory_id / max(total_trajectories, 1)) * 10
        
        animation = f'''
    <animateMotion
      dur="{duration}s"
      repeatCount="indefinite"
      path="{path}"
      begin="{delay}s"
    />'''
        
        # Reset random seed
        random.seed()
        
        return animation
    
    @staticmethod
    def create_nebula_animation() -> str:
        """
        Create subtle animation for nebula background effects.
        
        Returns:
            SVG animate element as string
        """
        return '''
    <animate
      attributeName="opacity"
      values="0.1;0.2;0.1"
      dur="20s"
      repeatCount="indefinite"
    />'''
    
    @staticmethod
    def create_glow_filter(filter_id: str, color: str, intensity: float = 1.0) -> str:
        """
        Create SVG filter for glow effect.
        
        Args:
            filter_id: Unique filter ID
            color: Glow color in hex format
            intensity: Glow intensity multiplier
            
        Returns:
            SVG filter definition as string
        """
        blur_amount = 4 * intensity
        
        return f'''
  <filter id="{filter_id}" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{blur_amount}" result="blur"/>
    <feFlood flood-color="{color}" flood-opacity="0.8"/>
    <feComposite in2="blur" operator="in" result="glow"/>
    <feMerge>
      <feMergeNode in="glow"/>
      <feMergeNode in="glow"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>'''
    
    @staticmethod
    def create_gradient(gradient_id: str, color1: str, color2: str) -> str:
        """
        Create radial gradient for celestial bodies.
        
        Args:
            gradient_id: Unique gradient ID
            color1: Center color in hex format
            color2: Edge color in hex format
            
        Returns:
            SVG radialGradient definition as string
        """
        return f'''
  <radialGradient id="{gradient_id}">
    <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
    <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
  </radialGradient>'''
    
    @staticmethod
    def create_comet_tail_gradient(gradient_id: str) -> str:
        """
        Create gradient for comet/PR tails.
        
        Args:
            gradient_id: Unique gradient ID
            
        Returns:
            SVG linearGradient definition as string
        """
        return f'''
  <linearGradient id="{gradient_id}">
    <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.8" />
    <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
  </linearGradient>'''
