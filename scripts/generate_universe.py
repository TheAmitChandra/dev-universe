#!/usr/bin/env python3
"""
GitHub Dev Universe Generator
Main script to generate animated SVG universe from GitHub profile.
"""

import os
import sys
from pathlib import Path

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.universe_generator import UniverseGenerator
from src.svg_renderer import SVGRenderer


def load_config_from_env() -> dict:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    config = {
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN'),
        'GITHUB_USERNAME': os.getenv('GITHUB_USERNAME') or os.getenv('GITHUB_ACTOR'),
        'MAX_PLANETS': int(os.getenv('MAX_PLANETS', '8')),
        'SHOW_MOONS': os.getenv('SHOW_MOONS', 'true').lower() == 'true',
        'SHOW_ASTEROIDS': os.getenv('SHOW_ASTEROIDS', 'true').lower() == 'true',
        'ORBIT_SPEED_MULTIPLIER': float(os.getenv('ORBIT_SPEED_MULTIPLIER', '1.0')),
        'BACKGROUND_STARS': int(os.getenv('BACKGROUND_STARS', '200')),
    }
    
    return config


def main():
    """Main execution function."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🌌 GitHub Dev Universe Generator 🌌              ║
║                                                              ║
║         Transform your GitHub into an animated galaxy        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Load configuration
    print("⚙️ Loading configuration...")
    config = load_config_from_env()
    
    # Validate required config
    if not config['GITHUB_USERNAME']:
        print("❌ Error: GITHUB_USERNAME environment variable is required!")
        print("   Set it with: export GITHUB_USERNAME=your-username")
        sys.exit(1)
    
    print(f"✅ Configuration loaded")
    print(f"   Username: {config['GITHUB_USERNAME']}")
    print(f"   Max Planets: {config['MAX_PLANETS']}")
    print(f"   Show Moons: {config['SHOW_MOONS']}")
    print(f"   Show Asteroids: {config['SHOW_ASTEROIDS']}")
    print(f"   Background Stars: {config['BACKGROUND_STARS']}")
    
    if not config['GITHUB_TOKEN']:
        print("⚠️  Warning: No GITHUB_TOKEN found. API rate limits will be lower.")
        print("   For better results, set GITHUB_TOKEN environment variable.")
    
    try:
        # Initialize generator
        print("\n🚀 Initializing universe generator...")
        generator = UniverseGenerator(config)
        
        # Generate universe data
        universe = generator.generate()
        
        # Initialize renderer
        print("\n🎨 Initializing SVG renderer...")
        renderer = SVGRenderer(width=1920, height=600)  # Cover dimensions
        
        # Render SVG
        svg_content = renderer.render(universe)
        
        # Ensure output directory exists
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # Write SVG file
        output_file = output_dir / 'universe.svg'
        print(f"\n💾 Writing SVG to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        file_size = output_file.stat().st_size / 1024  # KB
        
        print(f"✅ Universe generated successfully!")
        print(f"   File: {output_file}")
        print(f"   Size: {file_size:.2f} KB")
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    ✨ Generation Complete! ✨                 ║
║                                                              ║
║  Your universe is ready at: output/universe.svg              ║
║                                                              ║
║  Add it to your GitHub profile README:                       ║
║  ![Dev Universe](./output/universe.svg)                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error generating universe: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
