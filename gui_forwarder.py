import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import queue
import logging
import os
from dotenv import load_dotenv

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
            
    def run_forwarder(self):
        """Run the forwarder logic in a separate thread"""
        try:
            # This is where you would integrate the actual forwarder logic
            # For now, we'll just simulate the process
            import time
            counter = 0
            while self.is_running:
                time.sleep(2)
                counter += 1
                self.logger.info(f"Checking for messages... (Check #{counter})")
                
                # Simulate message processing
                if counter % 5 == 0:
                    self.logger.info("No new messages from Bale")
                    
        except Exception as e:
            self.logger.error(f"Forwarder error: {str(e)}")
            
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