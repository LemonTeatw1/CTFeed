import aiohttp
import logging
from datetime import datetime, timedelta
from src.config import CTFTIME_API_URL, TEAM_API_URL, SEARCH_DAYS

logger = logging.getLogger(__name__)

async def fetch_ctf_events():
    params = {
        'limit': 20,
        'start': int(datetime.now().timestamp()),
        'finish': int((datetime.now() + timedelta(days=SEARCH_DAYS)).timestamp())
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CTFTIME_API_URL, params=params) as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        logger.error(f"API 錯誤: {e}")
    return []

async def fetch_team_info(team_id):
    url = f"{TEAM_API_URL}{team_id}/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    team_data = await response.json()
                    return team_data.get('country'), team_data.get('name')
    except Exception as e:
        logger.error(f"獲取團隊資訊錯誤: {e}")
    return None, None 