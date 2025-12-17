#!/bin/bash

echo "Bale to Telegram Forwarder"
echo "========================"
echo "Before running this script, please set the following environment variables:"
echo "BALE_BOT_TOKEN - Your Bale bot token"
echo "TELEGRAM_BOT_TOKEN - Your Telegram bot token"
echo "TELEGRAM_CHANNEL_ID - Your Telegram channel ID (e.g., @channelname)"
echo ""
echo "You can set them manually or edit this file to include them."
echo ""
echo "Example:"
echo "export BALE_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
echo "export TELEGRAM_BOT_TOKEN=123456789:ABCDEFabcdef1234567890ABCDEFabcdef"
echo "export TELEGRAM_CHANNEL_ID=@your_channel_name"
echo ""

read -p "Press Enter to continue..."

echo "Installing required packages..."
pip install -r requirements.txt

echo "Starting Bale to Telegram forwarder..."
python forwarder.py