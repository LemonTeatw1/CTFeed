#!/bin/bash

set -e

echo "==================================="
echo "    CTFeed Environment Setup"
echo "==================================="
echo ""

if [ -f ".env" ]; then
    echo ".env already exists! Nothing to do."
    echo "If you want to run again please rm the .env file"
    exit 0
fi

if [ ! -f ".env.example" ]; then
    echo ".env.example file not found!"
    echo "Please make sure you're running this script from the project root directory."
    exit 1
fi

echo "Please provide the following information:"
echo "   (Press Enter after pasting each value)"
echo ""

echo "Discord Bot Token:"
echo "   Get this from https://discord.com/developers/applications"
while true; do
    read -p "   Paste your Discord Bot Token: " DISCORD_BOT_TOKEN
    if [ -n "$DISCORD_BOT_TOKEN" ]; then
        break
    else
        echo "   Error: Discord Bot Token cannot be empty. Please try again."
    fi
done

echo ""
echo "Check Interval (in minutes):"
echo "   How often should the bot check for new CTF events?"
echo "   Default is 30 minutes"
read -p "   Enter check interval in minutes (press Enter for default 30): " CHECK_INTERVAL_MINUTES
if [ -z "$CHECK_INTERVAL_MINUTES" ]; then
    CHECK_INTERVAL_MINUTES=30
fi

echo ""
echo "Announcement Channel ID:"
echo "   The Discord channel where CTF announcements will be posted"
echo "   The channel name that on your server"
while true; do
    read -p "   Paste your Discord Channel Name: " ANNOUNCEMENT_CHANNEL_ID
    if [ -n "$ANNOUNCEMENT_CHANNEL_ID" ]; then
        break
    else
        echo "   Error: Discord Channel Name cannot be empty. Please try again."
    fi
done

echo ""
echo "Please review your configuration:"
echo "   Discord Bot Token: ${DISCORD_BOT_TOKEN:0:30}********** (hidden)"
echo "   Check Interval: $CHECK_INTERVAL_MINUTES minutes"
echo "   Announcement Channel Name: $ANNOUNCEMENT_CHANNEL_ID"
echo ""

while true; do
    read -p "Is this configuration correct? (y/n): " -n 1 -r
    echo ""
    case $REPLY in
        [Yy]* ) 
            break
            ;;
        [Nn]* ) 
            echo "Configuration cancelled. Please run the script again."
            exit 0
            ;;
        * ) 
            echo "Please answer y (yes) or n (no)."
            ;;
    esac
done

echo ""
echo "Writing configuration to .env file..."
echo ""

cat > .env << EOF
# Discord Bot Configuration
DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN

# CTF Tracking Configuration
CHECK_INTERVAL_MINUTES=$CHECK_INTERVAL_MINUTES
ANNOUNCEMENT_CHANNEL_ID=$ANNOUNCEMENT_CHANNEL_ID

# CTFtime API Configuration
CTFTIME_API_BASE_URL=https://ctftime.org/api/v1

# Cache event file located
KNOWN_EVENTS_FILE=data/known_events.json
EOF

echo "Are ready to go .env file is created. Please run the bot with python like this:"
echo ""
echo "python ctfeed.py"
echo "or"
echo "python3 ctfeed.py"