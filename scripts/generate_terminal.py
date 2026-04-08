#!/usr/bin/env python3
"""
GitHub Terminal Card — Main Generator Script

Usage (local):
    $env:GITHUB_USERNAME = "your-username"
    $env:GITHUB_TOKEN    = "ghp_..."          # optional but avoids rate limits
    python scripts/generate_terminal.py

The generated SVG is written to  output/terminal.svg
Embed it in your profile README with:
    ![Terminal Card](output/terminal.svg)
"""

import os
import sys
from pathlib import Path

# Allow imports from src/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.github_api import GitHubAPI
from src.profile_builder import ProfileBuilder
from src.terminal_renderer import TerminalRenderer


def main() -> None:
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════╗\n"
        "║        GitHub Terminal Card Generator                   ║\n"
        "║  Animated terminal SVG — drop it into your README       ║\n"
        "╚══════════════════════════════════════════════════════════╝\n"
    )

    token    = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    username = os.getenv("GITHUB_USERNAME") or os.getenv("GITHUB_ACTOR")

    if not username:
        print("❌  GITHUB_USERNAME is not set.")
        print("    Windows PowerShell : $env:GITHUB_USERNAME = 'your-username'")
        print("    Linux / macOS      : export GITHUB_USERNAME=your-username")
        sys.exit(1)

    print(f"👤  User      : {username}")
    if token:
        print("🔑  Auth      : token found   (5 000 req/hr)")
    else:
        print("⚠️   Auth      : no token      (60 req/hr — set GITHUB_TOKEN to avoid limits)")

    # ── Fetch data ──────────────────────────────────────────────────────
    api     = GitHubAPI(token=token, username=username)
    builder = ProfileBuilder(api=api, max_repos=5, max_languages=5)
    profile = builder.build()

    # ── Render SVG ──────────────────────────────────────────────────────
    print("🎨  Rendering terminal card…")
    renderer = TerminalRenderer()
    svg      = renderer.render(profile)

    # ── Write output ────────────────────────────────────────────────────
    out_dir  = project_root / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "terminal.svg"
    out_path.write_text(svg, encoding="utf-8")

    size_kb = len(svg) / 1024
    print(f"\n✅  Done!  →  {out_path}  ({size_kb:.1f} KB)\n")
    print("📋  Embed in your README:")
    print("    ![Terminal Card](output/terminal.svg)\n")


if __name__ == "__main__":
    main()
