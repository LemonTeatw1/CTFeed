#!/usr/bin/env python3

import asyncio
import aiohttp
import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import logging
import os
import json
from dotenv import load_dotenv
import pytz

logging.basicConfig(level=logging.INFO)
logging.getLogger('discord.client').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

bot = discord.Client(intents=discord.Intents.default())

def load_known_events():
    try:
        known_events_file = os.getenv('KNOWN_EVENTS_FILE', 'data/known_events.json')
        if os.path.exists(known_events_file):
            with open(known_events_file, 'r') as f:
                events = json.load(f)
                logger.info(f"載入了 {len(events)} 個已知事件")
                return set(events)
    except Exception as e:
        logger.error(f"載入已知事件失敗: {e}")
    return set()

def save_known_events(events):
    try:
        known_events_file = os.getenv('KNOWN_EVENTS_FILE', 'data/known_events.json')
        os.makedirs(os.path.dirname(known_events_file), exist_ok=True)
        with open(known_events_file, 'w') as f:
            json.dump(list(events), f)
        logger.info(f"保存了 {len(events)} 個已知事件")
    except Exception as e:
        logger.error(f"保存已知事件失敗: {e}")

bot.known_events = load_known_events()

async def fetch_team_info(team_id):
    """獲取團隊資訊，包括國家"""
    url = f"https://ctftime.org/api/v1/teams/{team_id}/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    team_data = await response.json()
                    return team_data.get('country'), team_data.get('name')
    except Exception as e:
        logger.error(f"獲取團隊資訊錯誤: {e}")
    return None, None

def get_country_info(country_code):
    if not country_code:
        return "🌍", "未知"
    
    country_flags = {
        'CN': '🇨🇳', 'JP': '🇯🇵', 'KR': '🇰🇷', 'TW': '🇹🇼', 'HK': '🇭🇰', 'MO': '🇲🇴',
        'IN': '🇮🇳', 'SG': '🇸🇬', 'MY': '🇲🇾', 'TH': '🇹🇭', 'VN': '🇻🇳', 'ID': '🇮🇩',
        'PH': '🇵🇭', 'BD': '🇧🇩', 'PK': '🇵🇰', 'LK': '🇱🇰', 'NP': '🇳🇵', 'MM': '🇲🇲',
        'KH': '🇰🇭', 'LA': '🇱🇦', 'BN': '🇧🇳', 'MN': '🇲🇳', 'UZ': '🇺🇿', 'KZ': '🇰🇿',
        
        'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷', 'IT': '🇮🇹', 'ES': '🇪🇸', 'NL': '🇳🇱',
        'CH': '🇨🇭', 'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮', 'BE': '🇧🇪',
        'AT': '🇦🇹', 'PL': '🇵🇱', 'CZ': '🇨🇿', 'SK': '🇸🇰', 'HU': '🇭🇺', 'RO': '🇷🇴',
        'BG': '🇧🇬', 'HR': '🇭🇷', 'RS': '🇷🇸', 'SI': '🇸🇮', 'BA': '🇧🇦', 'ME': '🇲🇪',
        'MK': '🇲🇰', 'AL': '🇦🇱', 'GR': '🇬🇷', 'CY': '🇨🇾', 'MT': '🇲🇹', 'PT': '🇵🇹',
        'IE': '🇮🇪', 'IS': '🇮🇸', 'LU': '🇱🇺', 'LI': '🇱🇮', 'AD': '🇦🇩', 'SM': '🇸🇲',
        'VA': '🇻🇦', 'MC': '🇲🇨', 'RU': '🇷🇺', 'UA': '🇺🇦', 'BY': '🇧🇾', 'LT': '🇱🇹',
        'LV': '🇱🇻', 'EE': '🇪🇪', 'MD': '🇲🇩', 'GE': '🇬🇪', 'AM': '🇦🇲', 'AZ': '🇦🇿',

        'US': '🇺🇸', 'CA': '🇨🇦', 'MX': '🇲🇽', 'GT': '🇬🇹', 'BZ': '🇧🇿', 'SV': '🇸🇻',
        'HN': '🇭🇳', 'NI': '🇳🇮', 'CR': '🇨🇷', 'PA': '🇵🇦', 'CU': '🇨🇺', 'JM': '🇯🇲',
        'HT': '🇭🇹', 'DO': '🇩🇴', 'PR': '🇵🇷', 'TT': '🇹🇹', 'BB': '🇧🇧', 'GD': '🇬🇩',
        
        'BR': '🇧🇷', 'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'PE': '🇵🇪', 'VE': '🇻🇪',
        'EC': '🇪🇨', 'BO': '🇧🇴', 'PY': '🇵🇾', 'UY': '🇺🇾', 'SR': '🇸🇷', 'GY': '🇬🇾',
        
        'ZA': '🇿🇦', 'EG': '🇪🇬', 'NG': '🇳🇬', 'KE': '🇰🇪', 'MA': '🇲🇦', 'ET': '🇪🇹',
        'GH': '🇬🇭', 'TN': '🇹🇳', 'DZ': '🇩🇿', 'LY': '🇱🇾', 'SD': '🇸🇩', 'UG': '🇺🇬',
        'TZ': '🇹🇿', 'ZW': '🇿🇼', 'ZM': '🇿🇲', 'MW': '🇲🇼', 'MZ': '🇲🇿', 'BW': '🇧🇼',
        'NA': '🇳🇦', 'SZ': '🇸🇿', 'LS': '🇱🇸', 'MG': '🇲🇬', 'MU': '🇲🇺', 'SC': '🇸🇨',
        
        'IL': '🇮🇱', 'TR': '🇹🇷', 'IR': '🇮🇷', 'SA': '🇸🇦', 'AE': '🇦🇪', 'IQ': '🇮🇶',
        'SY': '🇸🇾', 'LB': '🇱🇧', 'JO': '🇯🇴', 'PS': '🇵🇸', 'YE': '🇾🇪', 'OM': '🇴🇲',
        'QA': '🇶🇦', 'BH': '🇧🇭', 'KW': '🇰🇼', 'AF': '🇦🇫',
        
        'AU': '🇦🇺', 'NZ': '🇳🇿', 'FJ': '🇫🇯', 'PG': '🇵🇬', 'TO': '🇹🇴', 'WS': '🇼🇸',
        'VU': '🇻🇺', 'SB': '🇸🇧', 'PW': '🇵🇼', 'FM': '🇫🇲', 'MH': '🇲🇭', 'KI': '🇰🇮',
        'TV': '🇹🇻', 'NR': '🇳🇷'
    }
    
    code = country_code.upper()
    flag_emoji = country_flags.get(code, f"🏳️")
    
    return flag_emoji, code

async def fetch_ctf_events():
    url = "https://ctftime.org/api/v1/events/"
    params = {
        'limit': 20,
        'start': int(datetime.now().timestamp()),
        'finish': int((datetime.now() + timedelta(days=90)).timestamp())
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        logger.error(f"API 錯誤: {e}")
    return []

async def create_event_embed(event):
    start_time_utc = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
    finish_time_utc = datetime.fromisoformat(event['finish'].replace('Z', '+00:00'))
    
    taipei_tz = pytz.timezone('Asia/Taipei')
    start_time_taipei = start_time_utc.astimezone(taipei_tz)
    finish_time_taipei = finish_time_utc.astimezone(taipei_tz)
    
    title = "🆕 新 CTF 競賽發布！"
    color = discord.Color.green()
    
    organizer_info = []
    first_country_flag = ""
    if event.get('organizers'):
        logger.info(f"處理 {len(event['organizers'])} 個主辦方")
        for i, org in enumerate(event['organizers'][:3]):
            try:
                country_code, team_name = await fetch_team_info(org['id'])
                logger.info(f"主辦方 {org['name']} (ID: {org['id']}) 國家: {country_code}")
                country_flag, country_name = get_country_info(country_code)
                if i == 0:
                    first_country_flag = country_flag
                organizer_info.append(f"{country_flag} {org['name']}")
            except Exception as e:
                logger.error(f"獲取主辦方 {org['name']} 資訊失敗: {e}")
                organizer_info.append(f"🌍 {org['name']}")
    
    title_with_flag = event['title']
    if first_country_flag:
        title_with_flag = f"{first_country_flag} {event['title']}"
    
    embed = discord.Embed(
        title=title,
        description=f"**{title_with_flag}**",
        color=color
    )
    
    embed.add_field(
        name="🕐 比賽時間",
        value=f"**開始：** {start_time_taipei.strftime('%m月%d日 %H:%M')} (台北) | {start_time_utc.strftime('%H:%M UTC')}\n"
              f"**結束：** {finish_time_taipei.strftime('%m月%d日 %H:%M')} (台北) | {finish_time_utc.strftime('%H:%M UTC')}\n"
              f"**持續：** {event['duration']['days']}天 {event['duration']['hours']}小時",
        inline=False
    )
    
    details = []
    details.append(f"**權重：** {event.get('weight', 0)}")
    details.append(f"**格式：** {event.get('format', '未知')}")
    if event.get('restrictions'):
        details.append(f"**限制：** {event['restrictions']}")
    
    if organizer_info:
        if len(organizer_info) == 1:
            details.append(f"**主辦：** {organizer_info[0]}")
        else:
            details.append(f"**主辦：** {', '.join(organizer_info)}")
    
    embed.add_field(
        name="📋 比賽詳情",
        value="\n".join(details),
        inline=True
    )
    
    links = []
    if event.get('url'):
        links.append(f"🌐 **官方網站：** {event['url']}")
    
    ctftime_url = f"https://ctftime.org/event/{event['id']}"
    links.append(f"📊 **CTFtime：** {ctftime_url}")
    
    if links:
        embed.add_field(
            name="🔗 相關連結",
            value="\n".join(links),
            inline=False
        )
    
    embed.set_footer(text=f"Event ID: {event['id']} | CTFtime.org")
    
    return embed

@bot.event
async def on_ready():
    logger.info(f'Bot 已登入: {bot.user}')
    logger.info(f"目前追蹤 {len(bot.known_events)} 個已知事件")
    check_new_events.start()

@tasks.loop(minutes=30)
async def check_new_events():
    events = await fetch_ctf_events()
    
    channel = None
    for guild in bot.guilds:
        for text_channel in guild.text_channels:
            if text_channel.name.lower() == 'ctftime':
                channel = text_channel
                break
        if channel:
            break
    
    if not channel:
        logger.warning("沒有找到 #ctftime 頻道")
        return
    
    new_events_found = False
    for event in events:
        event_id = event['id']
        if event_id not in bot.known_events:
            bot.known_events.add(event_id)
            new_events_found = True

            embed = await create_event_embed(event)
            try:
                await channel.send(embed=embed)
                logger.info(f"發送新事件通知: {event['title']}")
            except Exception as e:
                logger.error(f"發送通知失敗: {e}")
    
    if new_events_found:
        save_known_events(bot.known_events)

@check_new_events.before_loop
async def before_check():
    await bot.wait_until_ready()

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')

    if not token:
        print("Please set Discord bot token in .env file")
        exit(1)
    
    print("Launching CTF Bot...")
    bot.run(token)