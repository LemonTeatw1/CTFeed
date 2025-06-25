# CTFeed

A Discord bot that automatically tracks CTF (Capture The Flag) events from [CTFtime.org](https://ctftime.org) and sends notifications when new competitions are announced.

## Prerequisites

- Python 3.13+ and uv package manager
- A Discord bot application with proper permissions

## Setup

1. Create a Discord bot application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Copy your bot token
3. Grant your bot the following permissions:
   - Send Messages
   - Manage Messages
4. Invite the bot to your Discord server
5. Copy the environment configuration file:
   ```shell
   cp -v .env.example .env
   ```
6. Modify `.env` file as needed for your setup
7. Install project dependencies:
   ```shell
   uv sync
   ```
8. Run the bot:
   ```shell
   python3 main.py
   ```