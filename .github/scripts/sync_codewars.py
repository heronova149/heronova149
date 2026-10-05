import os
import re
import requests

USERNAME = "YOUR_CODEWARS_USERNAME"  # Replace with your Codewars username

# Map Codewars language slugs to standard file extensions
EXTENSIONS = {
    "python": "py",
    "sql": "sql",
    "javascript": "js",
    "typescript": "ts",
    "csharp": "cs",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "rust": "rs",
    "go": "go",
    "ruby": "rb",
    "php": "php",
    "swift": "swift",
    "kotlin": "kt",
    "scala": "scala",
    "shell": "sh",
    "bash": "sh",
    "r": "r",
    "julia": "jl",
    "dart": "dart",
    "elixir": "ex",
    "clojure": "clj",
    "haskell": "hs",
    "lua": "lua"
}

def slugify(text):
    return re.sub(r'[\W_]+', '_', text.lower()).strip('_')

def get_completed_challenges():
    challenges = []
    page = 0
    while True:
        url = f"https://www.codewars.com/api/v1/users/{USERNAME}/code-challenges/completed?page={page}"
        res = requests.get(url)
        if res.status_code != 200:
            break
        data = res.json().get("data", [])
        if not data:
            break
        challenges.extend(data)
        page += 1
        if page >= res.json().get("totalPages", 1):
            break
    return challenges

def get_challenge_details(challenge_id):
    url = f"https://www.codewars.com/api/v1/code-challenges/{challenge_id}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else {}

def sync():
    challenges = get_completed_challenges()
    summary = {}

    for item in challenges:
        c_id = item["id"]
        c_name = item["name"]
        languages = item.get("completedLanguages", [])
        
        details = get_challenge_details(c_id)
        rank_name = (details.get("rank") or {}).get("name", "beta").replace(" ", "_")
        
        # Save every language solution completed for this challenge
        for lang in languages:
            ext = EXTENSIONS.get(lang.lower(), "txt")
            dir_path = os.path.join(lang, rank_name, slugify(c_name))
            os.makedirs(dir_path, exist_ok=True)
            
            file_path = os.path.join(dir_path, f"solution.{ext}")
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"/*\n" if ext in ["js", "ts", "cs", "java", "c", "cpp", "rs", "go", "php", "swift", "kt", "scala"] else "# "
                    )
                    f.write(f"Codewars Kata: {c_name}\n")
                    f.write(f"Rank: {rank_name.replace('_', ' ').title()}\n")
                    f.write(f"Language: {lang}\n")
                    f.write(f"URL: https://www.codewars.com/kata/{c_id}\n")
                    f.write(
                        f"*/\n\n// Verified completed via Codewars Public API\n" if ext in ["js", "ts", "cs", "java", "c", "cpp", "rs", "go", "php", "swift", "kt", "scala"]
                        else f"# Verified completed via Codewars Public API\n"
                    )
            
            summary[lang] = summary.get(lang, 0) + 1

    update_readme(summary, len(challenges))

def update_readme(summary, total_count):
    if not os.path.exists("README.md"):
        return
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Sort languages descending by number of completed katas
    sorted_summary = sorted(summary.items(), key=lambda x: x[1], reverse=True)

    table = "| Language | Completed Katas |\n| :--- | :---: |\n"
    for lang, count in sorted_summary:
        display_name = {
            "csharp": "C#",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "cpp": "C++",
            "sql": "SQL"
        }.get(lang.lower(), lang.capitalize())
        table += f"| **{display_name}** | {count} |\n"
    table += f"| **Total Unique Katas** | **{total_count}** |\n"

    new_content = re.sub(
        r"<!-- STATS_START -->.*<!-- STATS_END -->",
        f"<!-- STATS_START -->\n{table}<!-- STATS_END -->",
        content,
        flags=re.DOTALL
    )
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    sync()
