# CTFeed

A Discord bot that automatically tracks CTF (Capture The Flag) events from [CTFtime.org](https://ctftime.org) and sends notifications when new competitions are announced.

## Prerequisites

- Python 3.13 and uv package manager
- A Discord bot application with proper permissions

## Setup

1. Create a Discord bot application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Copy your bot token
3. Grant your bot the following permissions:
   - Send Messages
   - Manage Messages
4. Invite the bot to your Discord server
5. Install project dependencies:
   ```shell
   uv sync
   ```
6. Set up your environment configuration using the interactive script:
   ```shell
   ./setup_env.sh
   ```
   The script will guide you through entering:
   - Discord Bot Token
   - Check interval (default: 30 minutes)
   - Discord channel name for announcements
   
   Alternatively, you can manually copy and edit the configuration:
   ```shell
   cp -v .env.example .env
   # Then edit .env file with your values
   ```

### Launch Bot

7. Run the bot:
   ```shell
   uv run python ctfeed.py
   ```
   Or with traditional Python:
   ```shell
   python3 ctfeed.py
   ```

The bot needs to run continuously in the background to monitor CTF events and send Discord notifications. You can use tools like `screen`, `tmux`, or `nohup` to keep it running in the background.