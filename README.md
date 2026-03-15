# 🌌 GitHub Dev Universe

Transform your GitHub profile into an **animated solar system** that visualizes your development activity, repositories, and programming languages.

**GitHub Dev Universe** generates a dynamic **SVG galaxy** where repositories orbit around your primary programming language like planets around a star.

The animation automatically updates using **GitHub Actions**, making your GitHub profile visually engaging and unique.

---

## 🚀 Features

### 🌞 Primary Language as the Sun

Your **most-used programming language** becomes the central star of the universe.

### 🪐 Repositories as Planets

Repositories orbit around the star.

Planet characteristics are derived from repository metrics:

| Attribute      | Meaning              |
| -------------- | -------------------- |
| Planet size    | Number of stars      |
| Orbit distance | Repository age       |
| Orbit speed    | Commit frequency     |
| Planet color   | Programming language |

---

### 🌙 Moons for Repository Stars

Repositories with high star counts generate **moons orbiting the planet**.

Example:

```
Repository Stars
0-5       → No moon
5-20      → 1 moon
20-100    → 2 moons
100+      → 3 moons
```

---

### ☄️ Asteroids (Issues & Pull Requests)

Open issues and pull requests appear as **asteroids traveling across the galaxy**.

```
Issue → small asteroid
Pull Request → glowing comet
```

---

### 🌌 Procedural Galaxy Background

The SVG background contains:

• randomly generated stars  
• nebula effects  
• subtle parallax animation

This makes the universe feel **alive rather than static**.

---

### ⚡ Activity-Based Orbit Speed

The more active a repository is, the faster it orbits.

```
commit_count → orbit_duration
```

Highly active repositories appear more dynamic.

---

### 🎨 Language-Based Planet Colors

Planet colors correspond to programming languages.

Example mapping:

```
Python → #3572A5
JavaScript → #F1E05A
TypeScript → #2B7489
Go → #00ADD8
Rust → #DEA584
Java → #B07219
```

Fallback color is used for unknown languages.

---

### 🛰 Repository Labels

Planets include optional **hover labels** showing:

• repository name  
• stars  
• primary language

Example tooltip:

```
repo-name
⭐ 143
Python
```

---

### 🔁 Automatic Updates

The universe updates automatically using **GitHub Actions**.

Default schedule:

```
Every 12 hours
```

Manual updates are also supported.

---

### 📦 Easy Installation

Users only need to add **one GitHub Action** to generate their universe.

---

## 🖼 Example Output

The generated SVG will display:

- **Central sun** representing your primary language
- **Orbiting planets** representing your top repositories
- **Moons** around popular repositories
- **Asteroids** representing open issues and pull requests
- **Background stars** creating a galaxy atmosphere

---

## ⚙️ Installation

### 1️⃣ Fork or Clone this Repository

```bash
git clone https://github.com/TheAmitChandra/dev-universe.git
cd dev-universe
```

Or click **Fork** at the top right of the repository.

---

### 2️⃣ Enable GitHub Actions

Navigate to:

```
Settings → Actions → General → Workflow permissions
```

Enable:
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

Then go to:

```
Actions tab → Enable workflows
```

---

### 3️⃣ Run the Workflow

Go to **Actions** tab → **Generate Dev Universe** → **Run workflow**

This will:
1. Analyze your GitHub repositories
2. Generate the animated universe SVG
3. Commit it to `output/universe.svg`

---

### 4️⃣ Add to Your Profile README

Create or edit your profile README (in a repo named `<username>/<username>`), and add:

```markdown
![Dev Universe](https://raw.githubusercontent.com/<username>/dev-universe/main/output/universe.svg)
```

Replace `<username>` with your GitHub username.

---

## 🛠 Configuration

Customize your universe by setting **repository variables**:

Navigate to: `Settings → Secrets and variables → Actions → Variables`

| Variable               | Description                    | Default |
| ---------------------- | ------------------------------ | ------- |
| MAX_PLANETS            | Maximum repositories displayed | 8       |
| SHOW_MOONS             | Enable moon generation         | true    |
| SHOW_ASTEROIDS         | Show issues & PRs              | true    |
| ORBIT_SPEED_MULTIPLIER | Speed adjustment               | 1.0     |
| BACKGROUND_STARS       | Number of stars in galaxy      | 200     |

Example configuration:

Create variables with these names and values:
- `MAX_PLANETS` = `10`
- `SHOW_MOONS` = `true`
- `BACKGROUND_STARS` = `300`

---

## 🧠 Data Sources

GitHub Dev Universe retrieves data using the GitHub API.

Endpoints used:

```
/users/{username}/repos
/repos/{owner}/{repo}/commits
/repos/{owner}/{repo}/issues
```

API requests are cached during workflow execution to reduce rate limits.

---

## 🧩 Project Architecture

```
github-dev-universe
│
├── src/
│   ├── __init__.py
│   ├── github_api.py          # GitHub API client
│   ├── repo_analyzer.py       # Repository metrics analyzer
│   ├── universe_generator.py  # Universe data generator
│   ├── svg_renderer.py        # SVG rendering engine
│   └── animation_engine.py    # Animation generator
│
├── output/
│   └── universe.svg           # Generated universe (auto-created)
│
├── scripts/
│   └── generate_universe.py   # Main generation script
│
├── .github/
│   └── workflows/
│       └── generate-universe.yml  # GitHub Actions workflow
│
├── requirements.txt           # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🎯 Local Development

### Prerequisites

- Python 3.7+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/TheAmitChandra/dev-universe.git
cd dev-universe

# Install dependencies (optional, uses stdlib)
pip install -r requirements.txt

# Set environment variables
export GITHUB_USERNAME="your-username"
export GITHUB_TOKEN="your-github-token"  # Optional but recommended

# Generate universe
python scripts/generate_universe.py
```

### Environment Variables

| Variable               | Required | Description                    |
| ---------------------- | -------- | ------------------------------ |
| GITHUB_USERNAME        | ✅       | Your GitHub username           |
| GITHUB_TOKEN           | ⚠️       | GitHub PAT (recommended)       |
| MAX_PLANETS            | ❌       | Max repositories (default: 8)  |
| SHOW_MOONS             | ❌       | Show moons (default: true)     |
| SHOW_ASTEROIDS         | ❌       | Show asteroids (default: true) |
| ORBIT_SPEED_MULTIPLIER | ❌       | Speed multiplier (default: 1.0)|
| BACKGROUND_STARS       | ❌       | Star count (default: 200)      |

---

## 🎨 SVG Animation Engine

Animations use native SVG features:

```xml
<animateMotion>      <!-- Orbital movement -->
<animateTransform>   <!-- Rotation -->
<animate>            <!-- Pulsing/twinkling -->
```

This ensures:

• lightweight rendering  
• no JavaScript required  
• compatibility with GitHub README

---

## 📈 Roadmap

Future enhancements planned:

### ⭐ v2

• 3D galaxy rendering  
• constellation view of repositories  
• contributor satellites

### ⭐ v3

• AI-generated developer insights  
• commit-based particle effects  
• repository clusters

### ⭐ v4

• interactive GitHub profile dashboard  
• WebGL animated universe

---

## 🤝 Contributing

Contributions are welcome!

Steps:

```bash
1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request
```

Please ensure code follows the existing structure and includes appropriate documentation.

---

## 🐛 Troubleshooting

### Issue: Workflow fails with "Resource not accessible by integration"

**Solution**: Enable write permissions in `Settings → Actions → General → Workflow permissions`

---

### Issue: No universe.svg generated

**Solution**: 
1. Check Actions logs for errors
2. Verify GITHUB_TOKEN has correct permissions
3. Ensure your account has public repositories

---

### Issue: Rate limit exceeded

**Solution**: 
1. Set GITHUB_TOKEN environment variable
2. Reduce MAX_PLANETS value
3. Wait for rate limit to reset (1 hour)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Support

If you find this project useful:

⭐ Star the repository  
🍴 Fork it  
🧑‍💻 Share it with the developer community

---

## 🌠 Inspiration

Inspired by the famous GitHub contribution visualizers such as:

• contribution snake animation  
• GitHub profile statistics cards

GitHub Dev Universe aims to bring **a new level of creativity to developer profiles**.

---

## 👨‍🚀 Author

Created by **Amit**  
AI / ML Engineer

---

**Turn your GitHub profile into a living universe.**

🌌 ✨ 🚀