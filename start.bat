@echo off
echo Bale to Telegram Forwarder
echo ========================
echo Before running this script, please set the following environment variables:
echo BALE_BOT_TOKEN - Your Bale bot token
echo TELEGRAM_BOT_TOKEN - Your Telegram bot token
echo TELEGRAM_CHANNEL_ID - Your Telegram channel ID (e.g., @channelname)
echo.
echo You can set them manually or edit this file to include them.
echo.
echo Example:
echo set BALE_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
echo set TELEGRAM_BOT_TOKEN=123456789:ABCDEFabcdef1234567890ABCDEFabcdef
echo set TELEGRAM_CHANNEL_ID=@your_channel_name
echo.

pause

echo Installing required packages...
pip install -r requirements.txt

echo Starting Bale to Telegram forwarder...
python forwarder.py

pause