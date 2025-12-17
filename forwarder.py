import asyncio
import time
import logging
import requests
import os
import io
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get tokens and channel ID from environment variables
BALE_BOT_TOKEN = os.environ.get('BALE_BOT_TOKEN')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')

# Validate that all required environment variables are set
if not BALE_BOT_TOKEN:
    raise ValueError("BALE_BOT_TOKEN environment variable is not set")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
if not TELEGRAM_CHANNEL_ID:
    raise ValueError("TELEGRAM_CHANNEL_ID environment variable is not set")

# API endpoints
BALE_API_URL = f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Create Telegram bot instance
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Store the last update ID to avoid processing the same messages multiple times
last_update_id = 0

def get_bale_updates():
    """Get updates from Bale"""
    global last_update_id
    try:
        response = requests.get(f"{BALE_API_URL}/getUpdates", params={"offset": last_update_id + 1})
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get Bale updates: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting Bale updates: {str(e)}")
        return None

def download_bale_file(file_id):
    """Download a file from Bale"""
    try:
        # First, get file information
        file_response = requests.get(f"{BALE_API_URL}/getFile", params={"file_id": file_id})
        if file_response.status_code != 200:
            logger.error(f"Failed to get file info from Bale: {file_response.status_code} - {file_response.text}")
            return None
            
        file_data = file_response.json()
        if not file_data.get("ok"):
            logger.error(f"Failed to get file info from Bale: {file_data}")
            return None
            
        file_path = file_data["result"]["file_path"]
        
        # Download the file content
        file_url = f"https://tapi.bale.ai/file/bot{BALE_BOT_TOKEN}/{file_path}"
        file_response = requests.get(file_url)
        if file_response.status_code != 200:
            logger.error(f"Failed to download file from Bale: {file_response.status_code} - {file_response.text}")
            return None
            
        return file_response.content
    except Exception as e:
        logger.error(f"Error downloading file from Bale: {str(e)}")
        return None

async def forward_to_telegram(message):
    """Forward a message from Bale to Telegram channel"""
    try:
        logger.info(f"Attempting to forward message to Telegram channel: {TELEGRAM_CHANNEL_ID}")
        
        # Handle different message types
        if "text" in message:
            # Forward text messages
            logger.info(f"Sending text message: {message['text']}")
            result = await telegram_bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message['text']
            )
            logger.info(f"Message sent successfully. Result: {result}")
        elif "photo" in message:
            # Forward photo messages
            logger.info("Photo message received")
            # Get the largest photo
            photo_sizes = message["photo"]
            largest_photo = max(photo_sizes, key=lambda x: x["file_size"] if "file_size" in x else x["width"] * x["height"])
            file_id = largest_photo["file_id"]
            
            # Download the photo from Bale
            photo_content = download_bale_file(file_id)
            if photo_content:
                # Send the photo to Telegram
                result = await telegram_bot.send_photo(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    photo=io.BytesIO(photo_content),
                    caption=message.get('caption', '')
                )
                logger.info(f"Photo sent successfully. Result: {result}")
            else:
                # Fallback to text message if download failed
                result = await telegram_bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text="Photo message received (failed to forward media)"
                )
                logger.info(f"Fallback message sent. Result: {result}")
        elif "document" in message:
            # Forward document messages
            logger.info("Document message received")
            file_id = message["document"]["file_id"]
            
            # Download the document from Bale
            doc_content = download_bale_file(file_id)
            if doc_content:
                # Send the document to Telegram
                filename = message["document"].get("file_name", "document")
                result = await telegram_bot.send_document(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    document=io.BytesIO(doc_content),
                    filename=filename,
                    caption=message.get('caption', '')
                )
                logger.info(f"Document sent successfully. Result: {result}")
            else:
                # Fallback to text message if download failed
                result = await telegram_bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text="Document message received (failed to forward media)"
                )
                logger.info(f"Fallback message sent. Result: {result}")
        elif "voice" in message:
            # Forward voice messages
            logger.info("Voice message received")
            file_id = message["voice"]["file_id"]
            
            # Download the voice message from Bale
            voice_content = download_bale_file(file_id)
            if voice_content:
                # Send the voice message to Telegram
                result = await telegram_bot.send_voice(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    voice=io.BytesIO(voice_content),
                    caption=message.get('caption', '')
                )
                logger.info(f"Voice message sent successfully. Result: {result}")
            else:
                # Fallback to text message if download failed
                result = await telegram_bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text="Voice message received (failed to forward media)"
                )
                logger.info(f"Fallback message sent. Result: {result}")
        elif "video" in message:
            # Forward video messages
            logger.info("Video message received")
            file_id = message["video"]["file_id"]
            
            # Download the video from Bale
            video_content = download_bale_file(file_id)
            if video_content:
                # Send the video to Telegram
                result = await telegram_bot.send_video(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    video=io.BytesIO(video_content),
                    caption=message.get('caption', '')
                )
                logger.info(f"Video sent successfully. Result: {result}")
            else:
                # Fallback to text message if download failed
                result = await telegram_bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text="Video message received (failed to forward media)"
                )
                logger.info(f"Fallback message sent. Result: {result}")
        elif "audio" in message:
            # Forward audio messages
            logger.info("Audio message received")
            file_id = message["audio"]["file_id"]
            
            # Download the audio from Bale
            audio_content = download_bale_file(file_id)
            if audio_content:
                # Send the audio to Telegram
                result = await telegram_bot.send_audio(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    audio=io.BytesIO(audio_content),
                    caption=message.get('caption', '')
                )
                logger.info(f"Audio sent successfully. Result: {result}")
            else:
                # Fallback to text message if download failed
                result = await telegram_bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text="Audio message received (failed to forward media)"
                )
                logger.info(f"Fallback message sent. Result: {result}")
        else:
            # Forward unsupported message types as text
            logger.info("Unsupported message type received")
            result = await telegram_bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text="Received an unsupported message type"
            )
            logger.info(f"Message sent successfully. Result: {result}")
        
        logger.info(f"Message forwarded successfully from Bale to Telegram")
    except Exception as e:
        logger.error(f"Error forwarding message to Telegram: {str(e)}")
        # Log additional debugging information
        logger.error(f"Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:5]}...")  # First 5 chars only for security
        logger.error(f"Telegram Channel ID: {TELEGRAM_CHANNEL_ID}")

def process_bale_updates():
    """Process updates from Bale"""
    global last_update_id
    updates = get_bale_updates()
    
    if updates and "result" in updates:
        logger.info(f"Received {len(updates['result'])} updates from Bale")
        for update in updates["result"]:
            if "update_id" in update:
                last_update_id = max(last_update_id, update["update_id"])
                
            if "message" in update:
                message = update["message"]
                logger.info(f"Processing message from Bale: {message.get('text', 'Media message')}")
                # Run the async function in the event loop
                asyncio.create_task(forward_to_telegram(message))
    elif updates:
        logger.info("No new updates from Bale")
    else:
        logger.info("Failed to get updates from Bale")

async def main():
    """Main function to start the forwarder"""
    logger.info("Starting Bale to Telegram forwarder...")
    logger.info(f"Using Telegram Channel ID: {TELEGRAM_CHANNEL_ID}")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        while True:
            process_bale_updates()
            # Wait before polling again
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        logger.info("Forwarder stopped by user")
    except Exception as e:
        logger.error(f"Forwarder encountered an error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())