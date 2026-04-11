"""
Terminal Renderer v2
Generates a polished, animated terminal-style SVG card for GitHub profile READMEs.

Design goals:
  - Professional dark theme (GitHub Dark #0d1117)
  - macOS traffic-light title bar with subtle inner glow
  - 6 sections: identity · links · stats grid · activity · repos · languages
  - Staggered fade-in + slide-up per line (pure CSS — no JS, works in GitHub)
  - Blinking block cursor at the end
  - Footer with profile URL and generation date
  - Language dots colored with per-language accent colors
  - Single <img> embed — no iFrames, no CDN fonts
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime

from .profile_builder import ProfileData, RepoSummary


# ── helpers ──────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _relative_time(iso_str: str) -> str:
    if not iso_str:
        return "unknown"
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        days = (datetime.utcnow() - dt).days
        if days < 1:   return "today"
        if days < 7:   return f"{days}d ago"
        if days < 30:  return f"{days // 7}w ago"
        if days < 365: return f"{days // 30}mo ago"
        return f"{days // 365}y ago"
    except Exception:
        return "unknown"


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _bar(pct: float, width: int = 16) -> Tuple[str, str]:
    """Return (filled_chars, empty_chars) for a block progress bar."""
    filled = max(0, min(width, round(pct / 100 * width)))
    return "\u2588" * filled, "\u2591" * (width - filled)


# ── language dot colors ───────────────────────────────────────────────────────

LANG_COLORS: Dict[str, str] = {
    "Python":           "#3572a5",
    "JavaScript":       "#f1e05a",
    "TypeScript":       "#3178c6",
    "Java":             "#b07219",
    "Go":               "#00add8",
    "Rust":             "#dea584",
    "C++":              "#f34b7d",
    "C":                "#555555",
    "C#":               "#178600",
    "PHP":              "#4f5d95",
    "Ruby":             "#701516",
    "Swift":            "#f05138",
    "Kotlin":           "#a97bff",
    "Dart":             "#00b4ab",
    "Scala":            "#c22d40",
    "R":                "#198ce7",
    "Shell":            "#89e051",
    "PowerShell":       "#012456",
    "HTML":             "#e34c26",
    "CSS":              "#563d7c",
    "Vue":              "#41b883",
    "Svelte":           "#ff3e00",
    "Elixir":           "#6e4a7e",
    "Haskell":          "#5e5086",
    "Lua":              "#000080",
    "MATLAB":           "#e16737",
    "Perl":             "#0298c3",
    "Jupyter Notebook": "#da5b0b",
    "Dockerfile":       "#384d54",
    "YAML":             "#cb171e",
    "MDX":              "#fcb32c",
}

_FALLBACK_LC = "#8b949e"


def _lc(lang: str) -> str:
    return LANG_COLORS.get(lang, _FALLBACK_LC)


# ── palette ───────────────────────────────────────────────────────────────────

BG       = "#0d1117"
TITLE_BG = "#161b22"
BORDER   = "#30363d"

C_PROMPT = "#7ee787"
C_USER   = "#58a6ff"
C_CMD    = "#e6edf3"
C_OUT    = "#8b949e"
C_ACCENT = "#f0883e"
C_CYAN   = "#79c0ff"
C_GREEN  = "#56d364"
C_YELLOW = "#e3b341"
C_DIM    = "#3d444d"
C_CURSOR = "#7ee787"
C_TITLE  = "#8b949e"
C_PINK   = "#ff7b72"
C_PURPLE = "#d2a8ff"
C_FOOTER = "#6e7681"

TL_RED   = "#ff5f57"
TL_YEL   = "#febc2e"
TL_GRN   = "#28c840"

# ── layout ─────────────────────────────────────────────────────────────────

W        = 860
TITLE_H  = 40
PAD_X    = 28
LINE_H   = 23
FS       = 13
PAD_TOP  = 16
PAD_BOT  = 32
CORNER_R = 12

FONT = (
    "'Cascadia Code','Cascadia Mono','Consolas',"
    "'Menlo','Monaco','Liberation Mono','Courier New',monospace"
)


# ── line helpers ─────────────────────────────────────────────────────────────

def _L(parts: List[Tuple[str, str]], delay: float) -> dict:
    return {"parts": parts, "delay": delay}

def _S() -> dict:
    return {"parts": [], "static": True}


def _prompt(username: str, cmd: str) -> List[Tuple[str, str]]:
    return [
        (f"{username}@github", C_USER),
        (":~$ ", C_PROMPT),
        (_esc(cmd), C_CMD),
    ]


def _out(*segs: Tuple[str, str]) -> List[Tuple[str, str]]:
    return [("  ", C_OUT)] + list(segs)


# ── main renderer ─────────────────────────────────────────────────────────────

class TerminalRenderer:

    def render(self, p: ProfileData) -> str:
        lines = self._build_lines(p)
        h = TITLE_H + PAD_TOP + len(lines) * LINE_H + PAD_BOT
        return "\n".join([
            self._header(h),
            self._style(),
            self._chrome(h),
            self._title_bar(p.username),
            self._scanlines(h),
            self._content(lines),
            self._footer(p, h),
            "</svg>",
        ])

    def _header(self, h: int) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg"\n'
            f'     viewBox="0 0 {W} {h}" width="{W}" height="{h}"\n'
            '     role="img" aria-label="GitHub Terminal Profile Card">'
        )

    def _style(self) -> str:
        return (
            "<style>\n"
            f"  text, tspan {{ font-family: {FONT}; font-size: {FS}px; }}\n"
            "  @keyframes fadein {\n"
            "    from { opacity:0; transform:translateY(6px); }\n"
            "    to   { opacity:1; transform:translateY(0);   }\n"
            "  }\n"
            "  @keyframes blink {\n"
            "    0%,49% { opacity:1; } 50%,100% { opacity:0; }\n"
            "  }\n"
            "</style>"
        )

    def _chrome(self, h: int) -> str:
        r = CORNER_R
        bg   = f'<rect width="{W}" height="{h}" rx="{r}" ry="{r}" fill="{BG}"/>'
        tb   = (
            f'<rect width="{W}" height="{TITLE_H + r}" rx="{r}" ry="{r}" fill="{TITLE_BG}"/>'
            f'<rect y="{TITLE_H}" width="{W}" height="{r}" fill="{TITLE_BG}"/>'
        )
        glow = (
            f'<rect x="1" y="1" width="{W-2}" height="{TITLE_H-1}" '
            f'rx="{r-1}" ry="{r-1}" fill="none" '
            f'stroke="#58a6ff" stroke-width="0.4" opacity="0.25"/>'
        )
        sep  = (
            f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" '
            f'stroke="{BORDER}" stroke-width="1"/>'
        )
        bord = (
            f'<rect width="{W}" height="{h}" rx="{r}" ry="{r}" '
            f'fill="none" stroke="{BORDER}" stroke-width="1"/>'
        )
        return "\n".join([bg, tb, glow, sep, bord])

    def _title_bar(self, username: str) -> str:
        cy = TITLE_H // 2
        lights = (
            f'<circle cx="22" cy="{cy}" r="6.5" fill="{TL_RED}"/>'
            f'<circle cx="44" cy="{cy}" r="6.5" fill="{TL_YEL}"/>'
            f'<circle cx="66" cy="{cy}" r="6.5" fill="{TL_GRN}"/>'
        )
        shines = (
            f'<circle cx="20" cy="{cy-2}" r="2" fill="#ffffff" opacity="0.35"/>'
            f'<circle cx="42" cy="{cy-2}" r="2" fill="#ffffff" opacity="0.35"/>'
            f'<circle cx="64" cy="{cy-2}" r="2" fill="#ffffff" opacity="0.35"/>'
        )
        label = (
            f'<text x="{W//2}" y="{cy+5}" text-anchor="middle" '
            f'fill="{C_TITLE}" font-size="{FS}px">'
            f'{_esc(username)}@github \u2014 terminal'
            f'</text>'
        )
        dot = f'<circle cx="{W-22}" cy="{cy}" r="4" fill="{TL_GRN}" opacity="0.8"/>'
        dot_label = (
            f'<text x="{W-32}" y="{cy+5}" text-anchor="end" '
            f'fill="{C_DIM}" font-size="11px">live</text>'
        )
        return "\n".join(["<!-- title bar -->", lights, shines, label, dot, dot_label])

    def _scanlines(self, h: int) -> str:
        lines = ['<!-- scanlines -->']
        lines.append('<g opacity="1">')
        y = TITLE_H + 2
        while y < h - PAD_BOT:
            lines.append(
                f'<line x1="{PAD_X//2}" y1="{y}" x2="{W - PAD_X//2}" y2="{y}" '
                f'stroke="#ffffff" stroke-width="0.6" opacity="0.018"/>'
            )
            y += 4
        lines.append("</g>")
        return "\n".join(lines)

    def _footer(self, p: ProfileData, h: int) -> str:
        today = datetime.utcnow().strftime("%b %d, %Y")
        fy    = h - PAD_BOT // 2 + 5
        left  = f"github.com/{_esc(p.username)}"
        right = f"Updated: {today} (UTC)"
        return (
            f'<!-- footer -->\n'
            f'<line x1="{PAD_X}" y1="{h - PAD_BOT + 2}" '
            f'x2="{W - PAD_X}" y2="{h - PAD_BOT + 2}" '
            f'stroke="{C_DIM}" stroke-width="0.8" stroke-dasharray="4,4"/>\n'
            f'<text x="{PAD_X}" y="{fy}" fill="{C_FOOTER}" font-size="11px">{left}</text>\n'
            f'<text x="{W - PAD_X}" y="{fy}" text-anchor="end" '
            f'fill="{C_FOOTER}" font-size="11px">{right}</text>'
        )

    # ── line content ─────────────────────────────────────────────────────

    def _build_lines(self, p: ProfileData) -> List[dict]:
        lines: List[dict] = []
        t = 0.25

        def add(parts: List[Tuple[str, str]], dt: float = 0.32):
            nonlocal t
            lines.append(_L(parts, t))
            t += dt

        def blank():
            lines.append(_S())

        def section(title: str):
            nonlocal t
            dash = "\u2500" * max(2, 54 - len(title))
            lines.append(_L(
                [(f"# \u2500\u2500 {title} ", C_PURPLE), (dash, C_DIM)],
                t
            ))
            t += 0.10

        # ── 1. identity ───────────────────────────────────────────────
        section("identity")
        add(_prompt(p.username, "whoami"), dt=0.45)

        name_s = _esc(p.display_name or p.username)
        loc_s  = f"  \u00b7  \U0001f4cd {_esc(p.location)}" if p.location else ""
        since  = f"  \u00b7  GitHub since {p.account_since}"
        add(_out((f"{name_s}{loc_s}{since}", C_CMD)), dt=0.24)

        if p.bio:
            bio_s = _esc(p.bio[:72] + ("\u2026" if len(p.bio) > 72 else ""))
            add(_out(('"', C_DIM), (bio_s, C_OUT), ('"', C_DIM)), dt=0.24)

        # Profile links
        link_parts: List[Tuple[str, str]] = []
        if p.website:
            display_url = (
                p.website.replace("https://", "").replace("http://", "").rstrip("/")
            )
            link_parts += [("\U0001f310 ", C_PINK), (_esc(display_url[:36]), C_CYAN)]
        if p.twitter:
            if link_parts:
                link_parts += [("   \u00b7   ", C_DIM)]
            link_parts += [("Twitter @", C_DIM), (_esc(p.twitter), C_CYAN)]
        if p.company:
            if link_parts:
                link_parts += [("   \u00b7   ", C_DIM)]
            link_parts += [("\u2039\u203a ", C_DIM), (_esc(p.company[:24]), C_OUT)]
        if link_parts:
            add([("  ", C_OUT)] + link_parts, dt=0.45)

        blank()

        # ── 2. stats ──────────────────────────────────────────────────
        section("stats")
        add(_prompt(p.username, "github --stats"), dt=0.45)

        # Column header
        add(_out(
            ("FOLLOWERS ".ljust(13), C_DIM),
            ("FOLLOWING ".ljust(13), C_DIM),
            ("REPOS ".ljust(11),     C_DIM),
            ("STARS ".ljust(11),     C_DIM),
            ("FORKS",                C_DIM),
        ), dt=0.10)

        # Separator
        add(_out(
            ("\u2500" * 11 + "  ", C_DIM),
            ("\u2500" * 11 + "  ", C_DIM),
            ("\u2500" * 9  + "  ", C_DIM),
            ("\u2500" * 9  + "  ", C_DIM),
            ("\u2500" * 7,         C_DIM),
        ), dt=0.14)

        # Values
        add(_out(
            (_fmt(p.followers).ljust(13),                         C_ACCENT),
            (_fmt(p.following).ljust(13),                         C_ACCENT),
            (_fmt(p.public_repos).ljust(11),                      C_ACCENT),
            ((f"\u2605 {_fmt(p.total_stars)}").ljust(11),         C_YELLOW),
            (f"\u2442 {_fmt(p.total_forks)}",                     C_PINK),
        ), dt=0.45)

        blank()

        # ── 3. activity ───────────────────────────────────────────────
        section("activity")
        add(_prompt(p.username, 'git log --all --since="30 days" --oneline'), dt=0.45)

        commits_s = _fmt(p.recent_commits) if p.recent_commits else "0"
        days_s    = str(p.active_days)
        busyness  = round(min(p.active_days / 30 * 100, 100))
        bf, be    = _bar(busyness, width=20)
        add([
            ("  ",              C_OUT),
            (bf,                C_GREEN),
            (be,                C_DIM),
            (f"  {commits_s}",  C_ACCENT),
            (" commits  \u00b7  ", C_OUT),
            (days_s,            C_ACCENT),
            (" active days  \u00b7  ", C_OUT),
            (_esc(p.activity_label), C_PURPLE),
        ], dt=0.24)

        if p.most_active_day and p.most_active_day != "N/A":
            add(_out(
                ("Most active day: ",      C_OUT),
                (_esc(p.most_active_day),  C_ACCENT),
                ("   Primary language: ",  C_OUT),
                (_esc(p.primary_language), _lc(p.primary_language)),
            ), dt=0.45)

        blank()

        # ── 4. repos ──────────────────────────────────────────────────
        section("repos")
        add(_prompt(p.username, "ls ~/repos/ --sort=stars -n 5"), dt=0.45)

        for repo in p.top_repos:
            star_s = _fmt(repo.stars).rjust(5)
            name_s = _esc(repo.name[:28]).ljust(30)
            lang_s = _esc((repo.language or "N/A")[:14]).ljust(16)
            when_s = _relative_time(repo.updated_at)
            lc_col = _lc(repo.language or "")
            add([
                ("  \u2605 ",       C_YELLOW),
                (star_s + "  ",     C_ACCENT),
                (name_s,            C_CYAN),
                (lang_s,            lc_col),
                (when_s,            C_DIM),
            ], dt=0.18)
            if repo.description:
                desc_s = _esc(
                    repo.description[:68] + ("\u2026" if len(repo.description) > 68 else "")
                )
                add([("         ", C_DIM), (desc_s, C_OUT)], dt=0.10)

        blank()

        # ── 5. languages ──────────────────────────────────────────────
        section("languages")
        add(_prompt(p.username, "cat ~/.config/languages"), dt=0.45)

        for lang, pct in p.language_stats.items():
            lc_col = _lc(lang)
            lang_s = _esc(lang[:18]).ljust(20)
            bf, be = _bar(pct, width=16)
            add([
                ("  \u25cf ", lc_col),
                (lang_s,      lc_col),
                (bf,          C_GREEN),
                (be,          C_DIM),
                (f"  {pct:>3}%", C_ACCENT),
            ], dt=0.16)

        blank()

        # ── cursor ────────────────────────────────────────────────────
        lines.append({
            "parts":  [(f"{p.username}@github", C_USER), (":~$ ", C_PROMPT)],
            "delay":  t,
            "cursor": True,
        })

        return lines

    # ── SVG text output ───────────────────────────────────────────────────

    def _content(self, lines: List[dict]) -> str:
        parts    = ["<!-- terminal content -->"]
        first_y  = TITLE_H + PAD_TOP + LINE_H

        for i, line in enumerate(lines):
            y      = first_y + i * LINE_H
            delay  = line.get("delay", 0.0)
            static = line.get("static", False)
            cursor = line.get("cursor", False)

            style = (
                ""
                if static
                else f"opacity:0;animation:fadein 0.20s ease forwards {delay:.2f}s"
            )

            tspans = []
            for text, color in line.get("parts", []):
                if text:
                    tspans.append(f'<tspan fill="{color}">{text}</tspan>')

            if cursor:
                cd = delay + 0.08
                tspans.append(
                    f'<tspan fill="{C_CURSOR}" '
                    f'style="animation:blink 1.1s steps(2,end) infinite {cd:.2f}s">'
                    f'\u2588</tspan>'
                )
                style = f"opacity:0;animation:fadein 0.05s ease forwards {delay:.2f}s"

            inner      = "".join(tspans)
            style_attr = f' style="{style}"' if style else ""
            parts.append(
                f'<text x="{PAD_X}" y="{y}" xml:space="preserve"{style_attr}>'
                f'{inner}</text>'
            )

        return "\n".join(parts)
