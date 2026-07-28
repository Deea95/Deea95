import os
import requests
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
from collections import Counter
import datetime

USERNAME = "Deea95"
OUTPUT_DIR = "../.github/stats"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Optional: pune-ți un GitHub token în variabila de mediu GH_TOKEN
# ca să eviți rate-limit-ul și să poți lua commit-uri reale via GraphQL.
GH_TOKEN = os.environ.get("GH_TOKEN")
HEADERS = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}

# ---------------------------------------------------------------
# 🎨 THEME "GitHub Dark Modern"
# ---------------------------------------------------------------
BG_COLOR = "#0d1117"          # fundal GitHub dark
PANEL_COLOR = "#161b22"       # fundal grafic
TEXT_COLOR = "#c9d1d9"
GRID_COLOR = "#21262d"
ACCENT_PURPLE = "#a371f7"
ACCENT_BLUE = "#58a6ff"
ACCENT_GREEN = "#3fb950"
PALETTE = ["#a371f7", "#58a6ff", "#3fb950", "#f778ba", "#f0883e", "#db6d28", "#79c0ff", "#56d364"]

plt.rcParams.update({
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": PANEL_COLOR,
    "axes.edgecolor": GRID_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titleweight": "bold",
    "axes.titlesize": 15,
    "axes.titlepad": 16,
    "savefig.facecolor": BG_COLOR,
})


def style_ax(ax, title):
    ax.set_title(title, color="white", loc="left")
    ax.grid(axis="y", alpha=0.3, linestyle="--", linewidth=0.7)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(length=0)


def rounded_bars(ax, x, heights, color, horizontal=False):
    """Bare cu colțuri rotunjite, stil modern (tip GitHub contribution cards)."""
    for i, (xi, h) in enumerate(zip(x, heights)):
        c = color[i] if isinstance(color, list) else color
        if horizontal:
            ax.add_patch(FancyBboxPatch(
                (0, xi - 0.35), h, 0.7,
                boxstyle="round,pad=0,rounding_size=0.15",
                linewidth=0, facecolor=c, mutation_aspect=1
            ))
        else:
            ax.add_patch(FancyBboxPatch(
                (xi - 0.35, 0), 0.7, h,
                boxstyle="round,pad=0,rounding_size=0.15",
                linewidth=0, facecolor=c, mutation_aspect=1
            ))


# ---------------------------------------------------------------
# 1️⃣ Date repo-uri
# ---------------------------------------------------------------
repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
repos = requests.get(repos_url, headers=HEADERS).json()

if not isinstance(repos, list):
    raise RuntimeError(f"Răspuns neașteptat de la GitHub API: {repos}")

# ---------------------------------------------------------------
# 📊 Top limbaje
# ---------------------------------------------------------------
languages = [repo["language"] for repo in repos if repo.get("language")]
lang_count = Counter(languages).most_common(8)
labels = [l for l, _ in lang_count]
values = [v for _, v in lang_count]

fig, ax = plt.subplots(figsize=(8, 5))
x_pos = range(len(labels))
rounded_bars(ax, x_pos, values, PALETTE)
ax.set_xlim(-0.6, len(labels) - 0.4)
ax.set_ylim(0, max(values) * 1.2)
ax.set_xticks(list(x_pos))
ax.set_xticklabels(labels, rotation=20, ha="right")
for xi, v in zip(x_pos, values):
    ax.text(xi, v + max(values) * 0.03, str(v), ha="center", color="white", fontsize=10, fontweight="bold")
style_ax(ax, "🧠 Top Languages")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/top_languages.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# ⭐ Top repos după stele
# ---------------------------------------------------------------
repos_sorted = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:5]
names = [r["name"] for r in repos_sorted][::-1]
stars = [r["stargazers_count"] for r in repos_sorted][::-1]

fig, ax = plt.subplots(figsize=(8, 5))
y_pos = range(len(names))
rounded_bars(ax, y_pos, stars, ACCENT_BLUE, horizontal=True)
ax.set_ylim(-0.6, len(names) - 0.4)
ax.set_xlim(0, max(stars, default=1) * 1.25 or 1)
ax.set_yticks(list(y_pos))
ax.set_yticklabels(names)
for yi, s in zip(y_pos, stars):
    ax.text(s + max(stars, default=1) * 0.03, yi, f"⭐ {s}", va="center", color="white", fontsize=10, fontweight="bold")
style_ax(ax, "⭐ Top Repos by Stars")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/top_repos.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 📈 Commits per month
# ---------------------------------------------------------------
def get_real_commit_counts(username, token):
    """Ia numărul de contribuții per lună din ultimul an via GraphQL, dacă avem token."""
    if not token:
        return None
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"login": username}},
        headers={"Authorization": f"bearer {token}"},
    )
    if resp.status_code != 200:
        return None
    data = resp.json()
    try:
        weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    except (KeyError, TypeError):
        return None

    monthly = Counter()
    for week in weeks:
        for day in week["contributionDays"]:
            month_key = day["date"][:7]  # YYYY-MM
            monthly[month_key] += day["contributionCount"]
    return dict(sorted(monthly.items()))


real_data = get_real_commit_counts(USERNAME, GH_TOKEN)

if real_data:
    months = list(real_data.keys())
    commits = list(real_data.values())
else:
    # fallback: date exemplu, doar dacă nu există token
    months = [f"2025-{m:02d}" for m in range(1, 13)]
    commits = [5, 7, 10, 4, 8, 12, 9, 11, 6, 7, 10, 8]

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(months, commits, marker="o", color=ACCENT_GREEN, linewidth=2.5,
        markersize=7, markerfacecolor="white", markeredgecolor=ACCENT_GREEN, markeredgewidth=2)
ax.fill_between(range(len(months)), commits, color=ACCENT_GREEN, alpha=0.12)
style_ax(ax, "📈 Commits per Month" + ("" if real_data else " (sample data)"))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/commits_per_month.png", dpi=150)
plt.close()

print("✅ Grafice generate în:", OUTPUT_DIR)
