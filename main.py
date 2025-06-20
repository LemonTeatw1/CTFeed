#!/usr/bin/env python3

import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = commands.Bot(command_prefix='!ctf ', intents=discord.Intents.default())
bot.known_events = set()

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

def create_event_embed(event, event_type="new"):

    start_time_utc = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
    finish_time_utc = datetime.fromisoformat(event['finish'].replace('Z', '+00:00'))
    
    taipei_tz = pytz.timezone('Asia/Taipei')
    start_time_taipei = start_time_utc.astimezone(taipei_tz)
    finish_time_taipei = finish_time_utc.astimezone(taipei_tz)
    
    if event_type == "new":
        title = "🆕 新 CTF 競賽發布！"
        color = discord.Color.green()
    else:
        title = "📅 即將開始的 CTF"
        color = discord.Color.blue()
    
    embed = discord.Embed(
        title=title,
        description=f"**{event['title']}**",
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
    check_new_events.start()

@bot.command(name='upcoming')
async def upcoming_events(ctx, limit: int = 5):

    events = await fetch_ctf_events()
    
    if not events:
        await ctx.send("❌ 無法獲取競賽資料")
        return
    
    if limit > 10:
        limit = 10
    
    embed = discord.Embed(
        title="📅 即將開始的 CTF 競賽",
        description=f"接下來 {min(len(events), limit)} 場競賽：",
        color=discord.Color.blue()
    )
    
    for i, event in enumerate(events[:limit]):
        start_time_utc = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
        taipei_tz = pytz.timezone('Asia/Taipei')
        start_time_taipei = start_time_utc.astimezone(taipei_tz)
        
        time_until = start_time_utc - datetime.now(pytz.UTC)
        days_until = time_until.days
        hours_until = time_until.seconds // 3600
        
        time_str = f"{days_until}天 {hours_until}小時後" if days_until > 0 else f"{hours_until}小時後"
        
        ctftime_url = f"https://ctftime.org/event/{event['id']}"
        
        embed.add_field(
            name=f"🏁 {event['title']}",
            value=f"📅 {start_time_taipei.strftime('%m月%d日 %H:%M')} (台北) | {start_time_utc.strftime('%H:%M UTC')}\n"
                  f"⏱️ 倒數：{time_str}\n"
                  f"⚖️ 權重：{event.get('weight', 0)}\n"
                  f"📊 {ctftime_url}",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='current')
async def current_events(ctx):
    url = "https://ctftime.org/api/v1/events/"
    now = datetime.now()
    params = {
        'limit': 20,
        'start': int((now - timedelta(days=7)).timestamp()),
        'finish': int((now + timedelta(days=1)).timestamp())
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    all_events = await response.json()
                else:
                    await ctx.send("❌ 無法獲取競賽資料")
                    return
    except Exception as e:
        await ctx.send(f"❌ API 錯誤: {e}")
        return
    
    current_events = []
    now_utc = datetime.now(pytz.UTC)
    for event in all_events:
        start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
        finish_time = datetime.fromisoformat(event['finish'].replace('Z', '+00:00'))
        if start_time <= now_utc <= finish_time:
            current_events.append(event)
    
    if not current_events:
        embed = discord.Embed(
            title="🏃 進行中的 CTF 競賽",
            description="目前沒有正在進行的競賽",
            color=discord.Color.yellow()
        )
    else:
        embed = discord.Embed(
            title="🏃 進行中的 CTF 競賽",
            description=f"目前有 {len(current_events)} 場競賽正在進行：",
            color=discord.Color.green()
        )
        
        for event in current_events:
            finish_time_utc = datetime.fromisoformat(event['finish'].replace('Z', '+00:00'))
            taipei_tz = pytz.timezone('Asia/Taipei')
            finish_time_taipei = finish_time_utc.astimezone(taipei_tz)
            
            time_left = finish_time_utc - datetime.now(pytz.UTC)
            days_left = time_left.days
            hours_left = time_left.seconds // 3600
            
            time_str = f"{days_left}天 {hours_left}小時" if days_left > 0 else f"{hours_left}小時"
            
            ctftime_url = f"https://ctftime.org/event/{event['id']}"
            
            embed.add_field(
                name=f"⚡ {event['title']}",
                value=f"🏁 結束：{finish_time_taipei.strftime('%m月%d日 %H:%M')} (台北) | {finish_time_utc.strftime('%H:%M UTC')}\n"
                      f"⏰ 剩餘：{time_str}\n"
                      f"⚖️ 權重：{event.get('weight', 0)}\n"
                      f"📊 {ctftime_url}",
                inline=True
            )
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    embed = discord.Embed(
        title="🏓 Pong!",
        description="Bot 運作正常",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

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
        await ctx.send("❌ 沒有找到 #ctftime 頻道")
        return
    
    for event in events:
        event_id = event['id']
        if event_id not in bot.known_events:
            bot.known_events.add(event_id)

            embed = create_event_embed(event, "new")
            try:
                await channel.send(embed=embed)
                logger.info(f"發送新事件通知: {event['title']}")
            except Exception as e:
                logger.error(f"發送通知失敗: {e}")

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