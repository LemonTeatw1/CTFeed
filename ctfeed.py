#!/usr/bin/env python3

import discord
from discord.ext import tasks
import logging
import os

from src.config import DISCORD_BOT_TOKEN, ANNOUNCEMENT_CHANNEL_ID, CHECK_INTERVAL
from src.data_manager import load_known_events, save_known_events
from src.ctf_api import fetch_ctf_events
from src.embed_creator import create_event_embed

logging.basicConfig(level=logging.INFO)
logging.getLogger('discord.client').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

bot = discord.Client(intents=discord.Intents.default())

known_events = load_known_events()

@bot.event
async def on_ready():
    logger.info(f'Bot 已登入: {bot.user}')
    logger.info(f"目前追蹤 {len(known_events)} 個已知事件")
    check_new_events.start()

@tasks.loop(minutes=CHECK_INTERVAL)
async def check_new_events():
    global known_events
    
    events = await fetch_ctf_events()
    
    channel_name = ANNOUNCEMENT_CHANNEL_ID
    if not channel_name:
        logger.error("❌ 請在 .env 檔案中設定 ANNOUNCEMENT_CHANNEL_ID 環境變數")
        logger.error("例如：ANNOUNCEMENT_CHANNEL_ID=ctftime")
        logger.error("請檢查 .env 檔案是否正確設定")
        await bot.close()
        return
    
    channel = None
    for guild in bot.guilds:
        for text_channel in guild.text_channels:
            if text_channel.name.lower() == channel_name.lower():
                channel = text_channel
                break
        if channel:
            break
    
    if not channel:
        logger.error(f"❌ 找不到名為 '{channel_name}' 的頻道")
        logger.error(f"請確認：")
        logger.error(f"1. 頻道名稱正確：{channel_name}")
        logger.error(f"2. Bot 有權限查看該頻道")
        logger.error(f"3. 該頻道存在於 Bot 所在的伺服器中")
        await bot.close()
        return
    
    new_events_found = False
    for event in events:
        event_id = event['id']
        if event_id not in known_events:
            known_events.add(event_id)
            new_events_found = True

            embed = await create_event_embed(event)
            try:
                await channel.send(embed=embed)
                logger.info(f"發送新事件通知: {event['title']}")
            except Exception as e:
                logger.error(f"發送通知失敗: {e}")
    
    if new_events_found:
        save_known_events(known_events)

@check_new_events.before_loop
async def before_check():
    await bot.wait_until_ready()

def main():
    if not DISCORD_BOT_TOKEN:
        print("❌ 請在 .env 檔案中設定 DISCORD_BOT_TOKEN")
        exit(1)
    
    print("🚀 啟動 CTF Bot...")
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()