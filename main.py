import os
import requests
from dotenv import load_dotenv

load_dotenv()

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      questionFrontendId
      title
      difficulty
      topicTags {
        name
      }
    }
  }
}
"""

DIFFICULTY_COLORS = {
    "Easy": 0x00B8A3,
    "Medium": 0xFFC01E,
    "Hard": 0xFF375F,
}


def fetch_daily_question():
    response = requests.post(
        LEETCODE_GRAPHQL,
        json={"query": QUERY},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()["data"]["activeDailyCodingChallengeQuestion"]

    question = data["question"]
    return {
        "id": question["questionFrontendId"],
        "title": question["title"],
        "difficulty": question["difficulty"],
        "tags": [tag["name"] for tag in question["topicTags"]],
        "url": f"https://leetcode.com{data['link']}",
        "date": data["date"],
    }


def post_to_discord(question):
    difficulty = question["difficulty"]
    color = DIFFICULTY_COLORS.get(difficulty, 0x95A5A6)
    tags = ", ".join(question["tags"]) if question["tags"] else "None"

    embed = {
        "title": f"#{question['id']} — {question['title']}",
        "url": question["url"],
        "color": color,
        "fields": [
            {"name": "Difficulty", "value": difficulty, "inline": True},
            {"name": "Topics", "value": tags, "inline": True},
        ],
        "footer": {"text": f"LeetCode Daily Challenge · {question['date']}"},
    }

    payload = {
        "content": "Good afternon! Here's today's LeetCode daily challenge:",
        "embeds": [embed],
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    print(f"Posted: #{question['id']} {question['title']} ({difficulty})")


if __name__ == "__main__":
    question = fetch_daily_question()
    post_to_discord(question)
