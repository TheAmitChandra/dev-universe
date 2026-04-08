"""
Terminal Renderer
Generates an animated terminal-style SVG card for a GitHub profile README.

Design:
  - Dark theme matching GitHub's own UI (#0d1117 bg)
  - macOS-style traffic-light title bar
  - Monospace font, color-coded output
  - Each line fades in with a staggered delay (pure CSS, no JS)
  - Blinking block cursor at the end
  - Works in GitHub README as a native <img src="...svg"> embed
"""

from typing import Dict, List, Tuple
from datetime import datetime

from .profile_builder import ProfileData, RepoSummary


class TerminalRenderer:
    # ── Card dimensions ─────────────────────────────────────────────────
    W = 800
    TITLE_H = 38
    PAD_X = 26
    LINE_H = 22
    FONT_SIZE = 13
    PAD_TOP = 18        # gap between title bar bottom and first line
    PAD_BOTTOM = 26

    # ── Font stack (system monospace only — GitHub strips external refs) ─
    FONT = (
        "'Cascadia Code','Cascadia Mono','Consolas',"
        "'Menlo','Monaco','Liberation Mono','Courier New',monospace"
    )

    # ── Color palette: GitHub Dark ───────────────────────────────────────
    BG        = "#0d1117"
    TITLE_BG  = "#161b22"
    BORDER    = "#30363d"

    C_PROMPT  = "#7ee787"   # green  — prompt character
    C_USER    = "#58a6ff"   # blue   — user@host
    C_CMD     = "#e6edf3"   # white  — command text
    C_OUT     = "#8b949e"   # gray   — general output
    C_ACCENT  = "#f0883e"   # orange — numbers / highlights
    C_CYAN    = "#79c0ff"   # cyan   — repo names
    C_GREEN   = "#56d364"   # green  — skill bars filled
    C_YELLOW  = "#e3b341"   # yellow — star symbol
    C_DIM     = "#444c56"   # dim    — empty bar / separators
    C_CURSOR  = "#7ee787"   # green  — blinking cursor block
    C_TITLE   = "#8b949e"   # gray   — title bar text

    # Traffic lights
    TL_RED    = "#ff5f57"
    TL_YELLOW = "#febc2e"
    TL_GREEN  = "#28c840"

    # ── Programming language accent colors ───────────────────────────────
    LANG_COLORS: Dict[str, str] = {
        "Python":         "#3572a5",
        "JavaScript":     "#f1e05a",
        "TypeScript":     "#3178c6",
        "Java":           "#b07219",
        "Go":             "#00add8",
        "Rust":           "#dea584",
        "C++":            "#f34b7d",
        "C":              "#555555",
        "C#":             "#178600",
        "PHP":            "#4f5d95",
        "Ruby":           "#701516",
        "Swift":          "#f05138",
        "Kotlin":         "#a97bff",
        "Dart":           "#00b4ab",
        "Scala":          "#c22d40",
        "R":              "#198ce7",
        "Shell":          "#89e051",
        "PowerShell":     "#012456",
        "HTML":           "#e34c26",
        "CSS":            "#563d7c",
        "Vue":            "#41b883",
        "Svelte":         "#ff3e00",
        "Elixir":         "#6e4a7e",
        "Haskell":        "#5e5086",
        "Lua":            "#000080",
        "MATLAB":         "#e16737",
        "Perl":           "#0298c3",
        "Jupyter Notebook": "#da5b0b",
    }

    def _lang_color(self, lang: str) -> str:
        return self.LANG_COLORS.get(lang, self.C_OUT)

    # ── Utilities ────────────────────────────────────────────────────────

    @staticmethod
    def _esc(text: str) -> str:
        """Escape XML special characters."""
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    @staticmethod
    def _relative_time(iso_str: str) -> str:
        if not iso_str:
            return "unknown"
        try:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.utcnow()
            days = (now - dt).days
            if days < 1:
                return "today"
            if days < 7:
                return f"{days}d ago"
            if days < 30:
                return f"{days // 7}w ago"
            if days < 365:
                return f"{days // 30}mo ago"
            return f"{days // 365}y ago"
        except Exception:
            return "unknown"

    @staticmethod
    def _fmt(n: int) -> str:
        return f"{n:,}"

    @staticmethod
    def _bar(pct: float, width: int = 10) -> str:
        """Unicode block bar: ████████░░ for 82%"""
        filled = max(0, min(width, round(pct / 100 * width)))
        return "\u2588" * filled + "\u2591" * (width - filled)

    # ── Line descriptors ─────────────────────────────────────────────────
    # Each line is a dict:
    #   parts    : list of (text, color) tuples
    #   delay    : float  seconds before this line appears
    #   no_anim  : bool   blank spacer lines — always visible
    #   cursor   : bool   append a blinking cursor block

    def _build_lines(self, p: ProfileData) -> List[dict]:
        lines: List[dict] = []
        t = 0.3  # rolling delay cursor

        def add(parts: List[Tuple[str, str]], dt: float = 0.38):
            nonlocal t
            lines.append({"parts": parts, "delay": t})
            t += dt

        def blank():
            lines.append({"parts": [("", self.C_OUT)], "no_anim": True})

        def prompt(cmd: str) -> List[Tuple[str, str]]:
            return [
                (f"{p.username}@github", self.C_USER),
                (":~$ ",                  self.C_PROMPT),
                (self._esc(cmd),           self.C_CMD),
            ]

        def out(*segments: Tuple[str, str]) -> List[Tuple[str, str]]:
            return [("  ", self.C_OUT)] + list(segments)

        # ── whoami ─────────────────────────────────────────────────────
        add(prompt("whoami"), dt=0.55)

        name = self._esc(p.display_name or p.username)
        loc  = f"  \u00b7  {self._esc(p.location)}" if p.location else ""
        add(out((f"{name}{loc}", self.C_CMD)), dt=0.32)

        add(out(
            (self._fmt(p.followers), self.C_ACCENT),
            (" followers  \u00b7  ",  self.C_OUT),
            (str(p.public_repos),     self.C_ACCENT),
            (" public repos  \u00b7  since ", self.C_OUT),
            (p.account_since,         self.C_ACCENT),
        ), dt=0.55)

        blank()

        # ── git stats ──────────────────────────────────────────────────
        add(prompt("git log --all --oneline | wc -l"), dt=0.55)

        commits_str = self._fmt(p.recent_commits) if p.recent_commits else "N/A"
        stars_str   = self._fmt(p.total_stars)
        add(out(
            (commits_str,      self.C_ACCENT),
            (" recent commits  \u00b7  \u2605 ", self.C_OUT),
            (stars_str,        self.C_YELLOW),
            (" total stars  \u00b7  ", self.C_OUT),
            (str(p.public_repos), self.C_ACCENT),
            (" public repos",   self.C_OUT),
        ), dt=0.55)

        blank()

        # ── top repos ──────────────────────────────────────────────────
        add(prompt("ls repos/ --sort=stars"), dt=0.55)

        for repo in p.top_repos:
            star_s = str(repo.stars).rjust(5)
            name_s = self._esc(repo.name[:22]).ljust(24)
            lang_s = self._esc(repo.language[:12]).ljust(13)
            when   = self._relative_time(repo.updated_at)
            add([
                ("\u2605 ", self.C_YELLOW),
                (star_s + "  ", self.C_ACCENT),
                (name_s,       self.C_CYAN),
                (lang_s,       self._lang_color(repo.language)),
                (when,         self.C_DIM),
            ], dt=0.22)

        blank()

        # ── language breakdown ─────────────────────────────────────────
        add(prompt("cat ~/.config/languages"), dt=0.55)

        for lang, pct in p.language_stats.items():
            bar      = self._bar(pct)
            lang_s   = self._esc(lang[:14]).ljust(16)
            lc       = self._lang_color(lang)
            # Split bar into filled and empty parts for individual coloring
            filled   = max(0, min(10, round(pct / 100 * 10)))
            bar_full = "\u2588" * filled
            bar_empty= "\u2591" * (10 - filled)
            add([
                ("  ",       self.C_OUT),
                (lang_s,     lc),
                (bar_full,   self.C_GREEN),
                (bar_empty,  self.C_DIM),
                (f"  {pct}%", self.C_ACCENT),
            ], dt=0.22)

        blank()

        # ── blinking cursor ────────────────────────────────────────────
        lines.append({
            "parts":  [
                (f"{p.username}@github", self.C_USER),
                (":~$ ",                  self.C_PROMPT),
            ],
            "delay":  t,
            "cursor": True,
        })

        return lines

    # ── SVG assembly ─────────────────────────────────────────────────────

    def render(self, profile: ProfileData) -> str:
        lines = self._build_lines(profile)
        content_h = len(lines) * self.LINE_H
        h = self.TITLE_H + self.PAD_TOP + content_h + self.PAD_BOTTOM

        parts = [
            self._header(h),
            self._style(),
            self._chrome(h),
            self._title_bar(profile.username),
            self._content(lines),
            "</svg>",
        ]
        return "\n".join(parts)

    def _header(self, h: int) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg"\n'
            f'     viewBox="0 0 {self.W} {h}"\n'
            f'     width="{self.W}" height="{h}"\n'
            '     role="img" aria-label="GitHub Terminal Profile Card">'
        )

    def _style(self) -> str:
        return (
            "<style>\n"
            f"  text, tspan {{ font-family: {self.FONT}; font-size: {self.FONT_SIZE}px; }}\n"
            "  @keyframes fadein {\n"
            "    from { opacity: 0; transform: translateY(5px); }\n"
            "    to   { opacity: 1; transform: translateY(0);   }\n"
            "  }\n"
            "  @keyframes blink {\n"
            "    0%, 49% { opacity: 1; }\n"
            "    50%, 100% { opacity: 0; }\n"
            "  }\n"
            "</style>"
        )

    def _chrome(self, h: int) -> str:
        r = 10
        # Card background
        bg   = f'<rect width="{self.W}" height="{h}" rx="{r}" ry="{r}" fill="{self.BG}"/>'
        # Title bar background (top rounded only)
        tb   = (
            f'<rect width="{self.W}" height="{self.TITLE_H + r}" rx="{r}" ry="{r}" fill="{self.TITLE_BG}"/>'
            f'<rect y="{self.TITLE_H}" width="{self.W}" height="{r}" fill="{self.TITLE_BG}"/>'
        )
        # Separator
        sep  = f'<line x1="0" y1="{self.TITLE_H}" x2="{self.W}" y2="{self.TITLE_H}" stroke="{self.BORDER}" stroke-width="1"/>'
        # Border ring
        bord = f'<rect width="{self.W}" height="{h}" rx="{r}" ry="{r}" fill="none" stroke="{self.BORDER}" stroke-width="1"/>'
        return "\n".join([bg, tb, sep, bord])

    def _title_bar(self, username: str) -> str:
        cy = self.TITLE_H // 2
        tl = (
            f'<circle cx="20" cy="{cy}" r="6" fill="{self.TL_RED}"/>'
            f'<circle cx="40" cy="{cy}" r="6" fill="{self.TL_YELLOW}"/>'
            f'<circle cx="60" cy="{cy}" r="6" fill="{self.TL_GREEN}"/>'
        )
        title = (
            f'<text x="{self.W // 2}" y="{cy + 5}" '
            f'text-anchor="middle" fill="{self.C_TITLE}" '
            f'font-size="{self.FONT_SIZE}px">'
            f'{self._esc(username)}@github:~'
            f'</text>'
        )
        return f"<!-- title bar -->\n{tl}\n{title}"

    def _content(self, lines: List[dict]) -> str:
        parts = ["<!-- terminal content -->"]
        first_y = self.TITLE_H + self.PAD_TOP + self.LINE_H

        for i, line in enumerate(lines):
            y     = first_y + i * self.LINE_H
            delay = line.get("delay", 0.0)
            no_a  = line.get("no_anim", False)
            cursor= line.get("cursor", False)

            if no_a:
                style = ""
            else:
                style = (
                    f"opacity:0;"
                    f"animation:fadein 0.18s ease forwards {delay:.2f}s"
                )

            # Build tspan markup — no whitespace between tags to preserve spacing
            tspan_parts = []
            for text, color in line.get("parts", []):
                if text:
                    tspan_parts.append(f'<tspan fill="{color}">{text}</tspan>')

            if cursor:
                cd = delay + 0.1
                tspan_parts.append(
                    f'<tspan fill="{self.C_CURSOR}" '
                    f'style="animation:blink 1s steps(2,end) infinite {cd:.2f}s">'
                    f'\u2588'
                    f'</tspan>'
                )
                style = f"opacity:0;animation:fadein 0.05s ease forwards {delay:.2f}s,blink 1s steps(2,end) infinite {cd:.2f}s"

            inner = "".join(tspan_parts)
            style_attr = f' style="{style}"' if style else ""
            parts.append(
                f'<text x="{self.PAD_X}" y="{y}"'
                f' xml:space="preserve"{style_attr}>{inner}</text>'
            )

        return "\n".join(parts)
