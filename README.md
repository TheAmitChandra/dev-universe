# GitHub Terminal Card

An **animated terminal SVG** that auto-generates from your GitHub profile and drops into any README as a single image tag.

```md
![Terminal Card](output/terminal.svg)
```

![preview](output/terminal.svg)

---

## What it shows

```
username@github:~$ whoami
  Your Name  ·  Location
  N followers  ·  N public repos  ·  since YYYY

username@github:~$ git log --all --oneline | wc -l
  N recent commits  ·  ★ N total stars  ·  N public repos

username@github:~$ ls repos/ --sort=stars
  ★   312  repo-one          Python      2d ago
  ★    47  another-repo      TypeScript  5d ago
  ★     5  cool-project      Go          1w ago

username@github:~$ cat ~/.config/languages
  Python          ████████░░  82%
  TypeScript      ███████░░░  71%
  Go              █████░░░░░  52%

username@github:~$ █
```

Each section fades in sequentially. The cursor blinks forever. Pure SVG + CSS — no JavaScript, no iframes. Works natively in any GitHub README.

---

## Quick start

### 1 — Use it as a GitHub Action (recommended)

Fork or copy this repo into your **profile repository** (`username/username`).

The workflow at [`.github/workflows/generate.yml`](.github/workflows/generate.yml) runs automatically:
- On every push to `main`
- Every 6 hours via cron
- On manual trigger from the Actions tab

It generates `output/terminal.svg` and commits it back to the repo. No secrets required — it uses the built-in `GITHUB_TOKEN`.

### 2 — Run locally

```bash
# Windows PowerShell
$env:GITHUB_USERNAME = "your-username"
$env:GITHUB_TOKEN    = "ghp_..."        # optional, avoids rate limits

python scripts/generate_terminal.py
```

```bash
# Linux / macOS
export GITHUB_USERNAME=your-username
export GITHUB_TOKEN=ghp_...

python scripts/generate_terminal.py
```

Output: `output/terminal.svg`

### 3 — Add to your profile README

```md
![Terminal Card](output/terminal.svg)
```

---

## Configuration

Edit `scripts/generate_terminal.py` or set environment variables:

| Variable           | Default | Description                          |
|--------------------|---------|--------------------------------------|
| `GITHUB_USERNAME`  | —       | **Required.** Your GitHub username   |
| `GITHUB_TOKEN`     | —       | Optional. Avoids the 60 req/hr limit |

To change how many repos or languages appear, edit the `ProfileBuilder` call in `generate_terminal.py`:

```python
builder = ProfileBuilder(api=api, max_repos=5, max_languages=5)
```

---

## How it works

| Step | File | What happens |
|------|------|--------------|
| 1 | `src/github_api.py` | 3 REST API calls: `/users/{u}`, `/users/{u}/repos`, `/users/{u}/events` |
| 2 | `src/profile_builder.py` | Aggregates stars, language breakdown, top repos |
| 3 | `src/terminal_renderer.py` | Emits a self-contained SVG with staggered CSS `fadein` animations |
| 4 | `scripts/generate_terminal.py` | Orchestrates 1→2→3 and writes `output/terminal.svg` |

No external Python dependencies — only the standard library.

---

## Requirements

- Python 3.8+
- A GitHub account (public repos only, no token required for basic usage)
