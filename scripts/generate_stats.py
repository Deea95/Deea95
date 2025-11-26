import os
import requests
import matplotlib.pyplot as plt
from collections import Counter

USERNAME = "Deea95"
OUTPUT_DIR = "../.github/stats"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1️⃣ Get repos data
repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
repos = requests.get(repos_url).json()

# Top languages
languages = []
for repo in repos:
    lang = repo["language"]
    if lang:
        languages.append(lang)

lang_count = Counter(languages)

plt.figure(figsize=(8,5))
plt.bar(lang_count.keys(), lang_count.values(), color="purple")
plt.title("Top Languages")
plt.savefig(f"{OUTPUT_DIR}/top_languages.png")
plt.close()

# Top repos by stars
repos_sorted = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:5]
names = [r["name"] for r in repos_sorted]
stars = [r["stargazers_count"] for r in repos_sorted]

plt.figure(figsize=(8,5))
plt.barh(names[::-1], stars[::-1], color="blue")
plt.title("Top Repos by Stars")
plt.savefig(f"{OUTPUT_DIR}/top_repos.png")
plt.close()

# Commits per month (dummy, GitHub API rate limit avoids detailed)
# You can add a script to fetch commits per month using GraphQL API
import datetime
months = [f"{m:02d}-2025" for m in range(1,13)]
commits = [5,7,10,4,8,12,9,11,6,7,10,8]

plt.figure(figsize=(10,4))
plt.plot(months, commits, marker='o', color="green")
plt.title("Commits per Month (sample)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/commits_per_month.png")
plt.close()
