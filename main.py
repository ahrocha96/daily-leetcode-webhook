import os
import json
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

DIFFICULTY_COLORS = {
    "Easy": 0x00B8A3,
    "Medium": 0xFFC01E,
    "Hard": 0xFF375F,
}

# Mon/Tue = Easy, Wed/Thu = Medium, Fri = Hard
WEEKDAY_DIFFICULTY = {
    0: "Easy",
    1: "Easy",
    2: "Medium",
    3: "Medium",
    4: "Hard",
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Anchor week — first Monday the bot will run.
# Changing this shifts which problem shows on which week.
REFERENCE_DATE = date(2026, 3, 20)


def load_problems():
    with open("neetcode150.json") as f:
        return json.load(f)


def get_todays_problem(problems):
    today = date.today()
    weekday = today.weekday()  # 0 = Monday … 6 = Sunday

    if weekday not in WEEKDAY_DIFFICULTY:
        return None  # weekend

    target_difficulty = WEEKDAY_DIFFICULTY[weekday]
    pool = [p for p in problems if p["difficulty"] == target_difficulty]

    days_since_ref = (today - REFERENCE_DATE).days
    week_num = max(0, days_since_ref // 7)

    # Each week provides 2 problems per difficulty tier (Mon+Tue, Wed+Thu).
    # Friday gets 1 problem per week from the Hard pool.
    if weekday in (0, 2):   # Monday / Wednesday → even slot
        idx = (week_num * 2) % len(pool)
    elif weekday in (1, 3): # Tuesday / Thursday → odd slot
        idx = (week_num * 2 + 1) % len(pool)
    else:                   # Friday
        idx = week_num % len(pool)

    return pool[idx]


def post_to_discord(problem):
    difficulty = problem["difficulty"]
    color = DIFFICULTY_COLORS.get(difficulty, 0x95A5A6)
    category = problem.get("category", "Neetcode 150")

    today = date.today()
    day_name = DAY_NAMES[today.weekday()]

    embed = {
        "title": problem["title"],
        "url": problem["url"],
        "color": color,
        "fields": [
            {"name": "Difficulty", "value": difficulty, "inline": True},
            {"name": "Category",   "value": category,   "inline": True},
        ],
        "footer": {"text": f"Neetcode 150  ·  {day_name}, {today}"},
    }

    payload = {
        "content": f"Good morning! Here's your {day_name} LeetCode problem:",
        "embeds": [embed],
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    print(f"Posted: {problem['title']} ({difficulty})")


if __name__ == "__main__":
    problems = load_problems()
    problem = get_todays_problem(problems)
    if problem:
        post_to_discord(problem)
    else:
        print("No problem today (weekend).")
