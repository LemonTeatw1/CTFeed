import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ANNOUNCEMENT_CHANNEL_ID = os.getenv("ANNOUNCEMENT_CHANNEL_ID")

CTFTIME_API_URL = "https://ctftime.org/api/v1/events/"
TEAM_API_URL = "https://ctftime.org/api/v1/teams/"

CHECK_INTERVAL = 30

SEARCH_DAYS = 90
