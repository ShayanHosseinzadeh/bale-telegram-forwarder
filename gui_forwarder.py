import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import queue
import logging
import os
import requests
import io
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables from .env file if it exists
load_dotenv()

class BaleTelegramForwarderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bale to Telegram Forwarder")
        self.root.geometry("600x500")
        
        # Setup logging
        self.log_queue = queue.Queue()
        self.setup_logging()
        
        # Create GUI elements
        self.create_widgets()
        
        # Forwarder state
        self.is_running = False
        self.forwarder_thread = None
        self.last_update_id = 0
        
    def setup_logging(self):
        """Setup logging to display in the GUI"""
        # Create a custom handler that puts log messages in the queue
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
                
            def emit(self, record):
                self.log_queue.put(self.format(record))
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add our custom handler
        queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        queue_handler.setFormatter(formatter)
        self.logger.addHandler(queue_handler)
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Bale to Telegram Forwarder", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Environment Variables Section
        env_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        env_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        env_frame.columnconfigure(1, weight=1)
        
        # Bale Bot Token
        ttk.Label(env_frame, text="Bale Bot Token:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.bale_token_var = tk.StringVar(value=os.environ.get('BALE_BOT_TOKEN', ''))
        bale_entry = ttk.Entry(env_frame, textvariable=self.bale_token_var, width=50)
        bale_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Telegram Bot Token
        ttk.Label(env_frame, text="Telegram Bot Token:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.telegram_token_var = tk.StringVar(value=os.environ.get('TELEGRAM_BOT_TOKEN', ''))
        telegram_entry = ttk.Entry(env_frame, textvariable=self.telegram_token_var, width=50)
        telegram_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Telegram Channel ID
        ttk.Label(env_frame, text="Telegram Channel ID:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.channel_id_var = tk.StringVar(value=os.environ.get('TELEGRAM_CHANNEL_ID', ''))
        channel_entry = ttk.Entry(env_frame, textvariable=self.channel_id_var, width=50)
        channel_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Forwarder", command=self.start_forwarder)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Forwarder", command=self.stop_forwarder, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="Save Config", command=self.save_config)
        self.save_button.pack(side=tk.LEFT)
        
        # Status Label
        self.status_var = tk.StringVar(value="Status: Stopped")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky=tk.W)
        
        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Exit Button
        exit_button = ttk.Button(main_frame, text="Exit", command=self.root.quit)
        exit_button.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # Start checking for log messages
        self.check_log_queue()
        
    def start_forwarder(self):
        """Start the forwarder in a separate thread"""
        # Validate inputs
        if not self.bale_token_var.get().strip():
            messagebox.showerror("Error", "Please enter Bale Bot Token")
            return
            
        if not self.telegram_token_var.get().strip():
            messagebox.showerror("Error", "Please enter Telegram Bot Token")
            return
            
        if not self.channel_id_var.get().strip():
            messagebox.showerror("Error", "Please enter Telegram Channel ID")
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Status: Running")
        self.logger.info("Starting Bale to Telegram Forwarder...")
        
        # Start forwarder in a separate thread
        self.forwarder_thread = threading.Thread(target=self.run_forwarder, daemon=True)
        self.forwarder_thread.start()
        
    def stop_forwarder(self):
        """Stop the forwarder"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Status: Stopped")
        self.logger.info("Forwarder stopped by user")
        
    def save_config(self):
        """Save configuration to .env file"""
        try:
            with open('.env', 'w') as f:
                f.write(f"BALE_BOT_TOKEN={self.bale_token_var.get()}\n")
                f.write(f"TELEGRAM_BOT_TOKEN={self.telegram_token_var.get()}\n")
                f.write(f"TELEGRAM_CHANNEL_ID={self.channel_id_var.get()}\n")
            self.logger.info("Configuration saved to .env file")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
    def get_bale_updates(self, bale_token):
        """Get updates from Bale"""
        try:
            bale_api_url = f"https://tapi.bale.ai/bot{bale_token}"
            response = requests.get(f"{bale_api_url}/getUpdates", params={"offset": self.last_update_id + 1})
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get Bale updates: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting Bale updates: {str(e)}")
            return None

    def download_bale_file(self, file_id, bale_token):
        """Download a file from Bale"""
        try:
            bale_api_url = f"https://tapi.bale.ai/bot{bale_token}"
            # First, get file information
            file_response = requests.get(f"{bale_api_url}/getFile", params={"file_id": file_id})
            if file_response.status_code != 200:
                self.logger.error(f"Failed to get file info from Bale: {file_response.status_code} - {file_response.text}")
                return None
                
            file_data = file_response.json()
            if not file_data.get("ok"):
                self.logger.error(f"Failed to get file info from Bale: {file_data}")
                return None
                
            file_path = file_data["result"]["file_path"]
            
            # Download the file content
            file_url = f"https://tapi.bale.ai/file/bot{bale_token}/{file_path}"
            file_response = requests.get(file_url)
            if file_response.status_code != 200:
                self.logger.error(f"Failed to download file from Bale: {file_response.status_code} - {file_response.text}")
                return None
                
            return file_response.content
        except Exception as e:
            self.logger.error(f"Error downloading file from Bale: {str(e)}")
            return None

    async def forward_to_telegram(self, message, telegram_token, channel_id):
        """Forward a message from Bale to Telegram channel"""
        try:
            self.logger.info(f"Attempting to forward message to Telegram channel: {channel_id}")
            
            # Create Telegram bot instance
            telegram_bot = Bot(token=telegram_token)
            
            # Handle different message types
            if "text" in message:
                # Forward text messages
                self.logger.info(f"Sending text message: {message['text']}")
                result = await telegram_bot.send_message(
                    chat_id=channel_id,
                    text=message['text']
                )
                self.logger.info(f"Message sent successfully. Result: {result}")
            elif "photo" in message:
                # Forward photo messages
                self.logger.info("Photo message received")
                # Get the largest photo
                photo_sizes = message["photo"]
                largest_photo = max(photo_sizes, key=lambda x: x["file_size"] if "file_size" in x else x["width"] * x["height"])
                file_id = largest_photo["file_id"]
                
                # Download the photo from Bale
                photo_content = self.download_bale_file(file_id, self.bale_token_var.get())
                if photo_content:
                    # Send the photo to Telegram
                    result = await telegram_bot.send_photo(
                        chat_id=channel_id,
                        photo=io.BytesIO(photo_content),
                        caption=message.get('caption', '')
                    )
                    self.logger.info(f"Photo sent successfully. Result: {result}")
                else:
                    # Fallback to text message if download failed
                    result = await telegram_bot.send_message(
                        chat_id=channel_id,
                        text="Photo message received (failed to forward media)"
                    )
                    self.logger.info(f"Fallback message sent. Result: {result}")
            elif "document" in message:
                # Forward document messages
                self.logger.info("Document message received")
                file_id = message["document"]["file_id"]
                
                # Download the document from Bale
                doc_content = self.download_bale_file(file_id, self.bale_token_var.get())
                if doc_content:
                    # Send the document to Telegram
                    filename = message["document"].get("file_name", "document")
                    result = await telegram_bot.send_document(
                        chat_id=channel_id,
                        document=io.BytesIO(doc_content),
                        filename=filename,
                        caption=message.get('caption', '')
                    )
                    self.logger.info(f"Document sent successfully. Result: {result}")
                else:
                    # Fallback to text message if download failed
                    result = await telegram_bot.send_message(
                        chat_id=channel_id,
                        text="Document message received (failed to forward media)"
                    )
                    self.logger.info(f"Fallback message sent. Result: {result}")
            elif "voice" in message:
                # Forward voice messages
                self.logger.info("Voice message received")
                file_id = message["voice"]["file_id"]
                
                # Download the voice message from Bale
                voice_content = self.download_bale_file(file_id, self.bale_token_var.get())
                if voice_content:
                    # Send the voice message to Telegram
                    result = await telegram_bot.send_voice(
                        chat_id=channel_id,
                        voice=io.BytesIO(voice_content),
                        caption=message.get('caption', '')
                    )
                    self.logger.info(f"Voice message sent successfully. Result: {result}")
                else:
                    # Fallback to text message if download failed
                    result = await telegram_bot.send_message(
                        chat_id=channel_id,
                        text="Voice message received (failed to forward media)"
                    )
                    self.logger.info(f"Fallback message sent. Result: {result}")
            elif "video" in message:
                # Forward video messages
                self.logger.info("Video message received")
                file_id = message["video"]["file_id"]
                
                # Download the video from Bale
                video_content = self.download_bale_file(file_id, self.bale_token_var.get())
                if video_content:
                    # Send the video to Telegram
                    result = await telegram_bot.send_video(
                        chat_id=channel_id,
                        video=io.BytesIO(video_content),
                        caption=message.get('caption', '')
                    )
                    self.logger.info(f"Video sent successfully. Result: {result}")
                else:
                    # Fallback to text message if download failed
                    result = await telegram_bot.send_message(
                        chat_id=channel_id,
                        text="Video message received (failed to forward media)"
                    )
                    self.logger.info(f"Fallback message sent. Result: {result}")
            elif "audio" in message:
                # Forward audio messages
                self.logger.info("Audio message received")
                file_id = message["audio"]["file_id"]
                
                # Download the audio from Bale
                audio_content = self.download_bale_file(file_id, self.bale_token_var.get())
                if audio_content:
                    # Send the audio to Telegram
                    result = await telegram_bot.send_audio(
                        chat_id=channel_id,
                        audio=io.BytesIO(audio_content),
                        caption=message.get('caption', '')
                    )
                    self.logger.info(f"Audio sent successfully. Result: {result}")
                else:
                    # Fallback to text message if download failed
                    result = await telegram_bot.send_message(
                        chat_id=channel_id,
                        text="Audio message received (failed to forward media)"
                    )
                    self.logger.info(f"Fallback message sent. Result: {result}")
            else:
                # Forward unsupported message types as text
                self.logger.info("Unsupported message type received")
                result = await telegram_bot.send_message(
                    chat_id=channel_id,
                    text="Received an unsupported message type"
                )
                self.logger.info(f"Message sent successfully. Result: {result}")
            
            self.logger.info(f"Message forwarded successfully from Bale to Telegram")
        except Exception as e:
            self.logger.error(f"Error forwarding message to Telegram: {str(e)}")

    def process_bale_updates(self, bale_token, telegram_token, channel_id):
        """Process updates from Bale"""
        updates = self.get_bale_updates(bale_token)
        
        if updates and "result" in updates:
            self.logger.info(f"Received {len(updates['result'])} updates from Bale")
            for update in updates["result"]:
                if "update_id" in update:
                    self.last_update_id = max(self.last_update_id, update["update_id"])
                    
                if "message" in update:
                    message = update["message"]
                    self.logger.info(f"Processing message from Bale: {message.get('text', 'Media message')}")
                    # Run the async function
                    asyncio.run(self.forward_to_telegram(message, telegram_token, channel_id))
        elif updates:
            self.logger.info("No new updates from Bale")
        else:
            self.logger.info("Failed to get updates from Bale")

    def run_forwarder(self):
        """Run the forwarder logic in a separate thread"""
        try:
            # Get tokens and channel ID
            bale_token = self.bale_token_var.get()
            telegram_token = self.telegram_token_var.get()
            channel_id = self.channel_id_var.get()
            
            # Validate tokens
            if not bale_token or not telegram_token or not channel_id:
                self.logger.error("Missing required configuration")
                self.stop_forwarder()
                return
                
            self.logger.info("Forwarder started successfully")
            
            # Main loop
            while self.is_running:
                try:
                    self.process_bale_updates(bale_token, telegram_token, channel_id)
                    # Wait before polling again
                    import time
                    time.sleep(2)
                except Exception as e:
                    self.logger.error(f"Error in forwarder loop: {str(e)}")
                    import time
                    time.sleep(5)  # Wait longer on error
                    
        except Exception as e:
            self.logger.error(f"Forwarder error: {str(e)}")
        finally:
            self.logger.info("Forwarder thread stopped")
            
    def check_log_queue(self):
        """Check for new log messages and display them"""
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, log_message + '\n')
                self.log_text.config(state=tk.DISABLED)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.check_log_queue)

def main():
    root = tk.Tk()
    app = BaleTelegramForwarderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()