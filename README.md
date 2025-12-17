# Bale to Telegram Forwarder

This application automatically forwards all content from Bale messenger to a Telegram channel.

## Important Note for Users in Iran

Since Telegram is filtered in Iran, you must run this bot on a foreign VPS or use a VPN/proxy to bypass restrictions. The bot needs to access both Bale (which works in Iran) and Telegram (which requires a foreign IP).

Options for deployment:
- Foreign VPS (Virtual Private Server) - Recommended
- Cloud platforms like AWS, Google Cloud, or Azure
- Using a VPN or proxy on a local machine (less reliable for production)

## Branches

This repository has two main branches:

1. **main** - Contains the command-line version of the application
2. **gui-version** - Contains the GUI version with CustomTkinter interface (this branch)

## Prerequisites

1. Python 3.9 or higher
2. A Bale bot token
3. A Telegram bot token
4. A Telegram channel with your bot added as administrator

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a bot in Bale:
   - Open Bale messenger
   - Search for @BotFather
   - Send `/newbot` command and follow the instructions
   - Copy the bot token

2. Create a bot in Telegram:
   - Open Telegram
   - Search for @BotFather
   - Send `/newbot` command and follow the instructions
   - Copy the bot token

3. Create a Telegram channel:
   - Open Telegram
   - Create a new channel
   - Add your bot as an administrator with posting permissions

4. Set environment variables:
   Instead of using a config file, this application now uses environment variables for security.
   
   You can copy the [.env.example](file:///c%3A/Users/Hp/Desktop/projects/bale/.env.example) file to `.env` and update it with your values:
   ```
   cp .env.example .env
   ```
   
   Then edit the `.env` file with your actual tokens and channel ID.
   
   Alternatively, you can set environment variables directly:
   
   On Linux/Mac:
   ```
   export BALE_BOT_TOKEN="your_bale_bot_token"
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   export TELEGRAM_CHANNEL_ID="@your_channel_username"
   ```
   
   On Windows (Command Prompt):
   ```
   set BALE_BOT_TOKEN=your_bale_bot_token
   set TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   set TELEGRAM_CHANNEL_ID=@your_channel_username
   ```
   
   On Windows (PowerShell):
   ```
   $env:BALE_BOT_TOKEN="your_bale_bot_token"
   $env:TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   $env:TELEGRAM_CHANNEL_ID="@your_channel_username"
   ```

## Usage

### GUI Version
Run the GUI application:
```
python start_gui.py
```

The GUI version provides a user-friendly interface for configuring and controlling the forwarder.

## Supported Message Types

This application now supports forwarding all message types from Bale to Telegram:

- Text messages
- Photos (sends the largest available size)
- Documents
- Voice messages
- Videos
- Audio files

All media messages will be downloaded from Bale and re-uploaded to Telegram with their original captions preserved.

## Troubleshooting

If you encounter any issues:

1. Check that all environment variables are set correctly
2. Ensure your bots have proper permissions
3. Check the logs for error messages
4. Make sure you're using Python 3.9 or higher