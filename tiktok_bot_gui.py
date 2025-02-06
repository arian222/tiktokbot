"""
TikTok Automation Bot - GUI Version
Created by: ALECS
GitHub: [Your GitHub URL]
"""

import re
import logging
import threading
import random
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Custom color scheme
COLORS = {
    "primary": "#FF0050",      # TikTok pink
    "secondary": "#00F2EA",    # TikTok cyan
    "background": "#1A1B1E",   # Dark background
    "surface": "#2B2B2B",      # Slightly lighter background
    "text": "#FFFFFF",         # White text
    "accent": "#FE2C55"        # TikTok red
}

# Set the appearance mode and custom theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

@dataclass
class Service:
    title: str
    selector: str
    status: Optional[str] = None

class TikTokBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables first
        self.driver = None
        self.is_running = False
        self.current_thread = None
        self.services = self._init_services()
        
        # Then setup logging and window
        self._setup_logging()
        self._setup_window()
        
        # Configure window style
        self.configure(fg_color=COLORS["background"])

    def _setup_logging(self):
        """Configure logging with timestamp and proper format"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tiktok_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _setup_window(self):
        """Setup the main window and UI components"""
        # Configure window
        self.title("ALECS TikTok Bot")
        self.geometry("900x700")
        
        # Create main container with gradient effect
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=15
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ALECS Brand Header
        brand_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["primary"],
            corner_radius=10,
            height=100
        )
        brand_frame.pack(fill="x", padx=20, pady=(20, 10))
        brand_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            brand_frame,
            text="ALECS",
            font=("Roboto", 40, "bold"),
            text_color=COLORS["text"]
        )
        title.pack(pady=(10, 0))
        
        subtitle = ctk.CTkLabel(
            brand_frame,
            text="TikTok Automation Bot",
            font=("Roboto", 16),
            text_color=COLORS["text"]
        )
        subtitle.pack()
        
        # URL Input with custom styling
        self.url_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        self.url_frame.pack(fill="x", padx=20, pady=10)
        
        url_label = ctk.CTkLabel(
            self.url_frame,
            text="TikTok Video URL:",
            font=("Roboto", 14, "bold"),
            text_color=COLORS["secondary"]
        )
        url_label.pack(side="left", padx=5)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            width=400,
            height=35,
            corner_radius=8,
            border_color=COLORS["secondary"],
            fg_color=COLORS["background"]
        )
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Services Frame with custom styling
        services_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["background"],
            corner_radius=10
        )
        services_frame.pack(fill="x", padx=20, pady=10)
        
        services_label = ctk.CTkLabel(
            services_frame,
            text="Select Service:",
            font=("Roboto", 16, "bold"),
            text_color=COLORS["secondary"]
        )
        services_label.pack(pady=5)
        
        # Services Radio Buttons Container - Horizontal Layout
        radio_container = ctk.CTkFrame(
            services_frame,
            fg_color="transparent"
        )
        radio_container.pack(fill="x", padx=10, pady=5)
        
        # Create 2 rows of services, 4 services per row
        self.selected_service = ctk.StringVar(value="views")
        self.service_radios = {}
        
        # First row
        row1_frame = ctk.CTkFrame(radio_container, fg_color="transparent")
        row1_frame.pack(fill="x", pady=2)
        
        # Second row
        row2_frame = ctk.CTkFrame(radio_container, fg_color="transparent")
        row2_frame.pack(fill="x", pady=2)
        
        # Distribute services across rows
        services_list = list(self.services.items())
        for idx, (service_key, service) in enumerate(services_list[:4]):  # First 4 services
            radio = ctk.CTkRadioButton(
                row1_frame,
                text=service.title,
                variable=self.selected_service,
                value=service_key,
                font=("Roboto", 13),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                border_color=COLORS["secondary"]
            )
            radio.pack(side="left", padx=20, expand=True)
            self.service_radios[service_key] = radio
            
        for idx, (service_key, service) in enumerate(services_list[4:]):  # Remaining services
            radio = ctk.CTkRadioButton(
                row2_frame,
                text=service.title,
                variable=self.selected_service,
                value=service_key,
                font=("Roboto", 13),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                border_color=COLORS["secondary"]
            )
            radio.pack(side="left", padx=20, expand=True)
            self.service_radios[service_key] = radio
        
        # Status Text with custom styling - Reduced height
        self.status_text = ctk.CTkTextbox(
            self.main_container,
            height=150,  # Reduced height
            width=600,
            corner_radius=10,
            fg_color=COLORS["background"],
            text_color=COLORS["text"],
            font=("Roboto", 12),
            border_color=COLORS["secondary"],
            border_width=1
        )
        self.status_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Control Buttons with custom styling
        buttons_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["surface"],
            corner_radius=10
        )
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        # Start Button - Green theme
        self.start_button = ctk.CTkButton(
            buttons_frame,
            text="START BOT",
            command=self.start_bot,
            font=("Roboto", 18, "bold"),
            fg_color="#00FF00",  # Bright green
            hover_color="#00CC00",  # Darker green
            corner_radius=8,
            height=50,
            width=200,
            border_width=2,
            border_color="#FFFFFF",
            text_color="#000000"  # Black text
        )
        self.start_button.pack(side="left", padx=20, pady=15, expand=True)
        
        # Stop Button - Red theme
        self.stop_button = ctk.CTkButton(
            buttons_frame,
            text="STOP BOT",
            command=self.stop_bot,
            font=("Roboto", 18, "bold"),
            fg_color="#FF0000",  # Bright red
            hover_color="#CC0000",  # Darker red
            corner_radius=8,
            height=50,
            width=200,
            border_width=2,
            border_color="#FFFFFF",
            text_color="#FFFFFF",  # White text
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=20, pady=15, expand=True)
        
        # Footer with credits
        footer = ctk.CTkLabel(
            self.main_container,
            text="Created by ALECS © 2024",
            font=("Roboto", 12),
            text_color=COLORS["text"]
        )
        footer.pack(pady=10)

    def _init_services(self) -> Dict[str, Service]:
        """Initialize available TikTok services"""
        return {
            "followers": Service("Followers", "t-followers-button"),
            "hearts": Service("Hearts", "t-hearts-button"),
            "comments_hearts": Service("Comments Hearts", "t-chearts-button"),
            "views": Service("Views", "t-views-button"),
            "shares": Service("Shares", "t-shares-button"),
            "favorites": Service("Favorites", "t-favorites-button"),
            "live_stream": Service("Live Stream [VS+LIKES]", "t-livesteam-button"),
        }

    def _init_driver(self) -> webdriver.Firefox:
        """Initialize and configure Firefox webdriver with optimal settings"""
        try:
            self.log_message("Initializing Firefox driver...")
            
            options = webdriver.FirefoxOptions()
            options.add_argument("--width=800")
            options.add_argument("--height=700")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
            service = webdriver.firefox.service.Service(
                executable_path=GeckoDriverManager().install()
            )
            
            driver = webdriver.Firefox(
                options=options,
                service=service
            )
            
            self.log_message("Firefox driver initialized successfully")
            return driver
            
        except Exception as e:
            self.log_message(f"Failed to initialize driver: {e}", "error")
            raise

    def log_message(self, message: str, level: str = "info"):
        """Add message to status text box"""
        self.status_text.configure(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_text.insert("end", f"[{timestamp}] {message}\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")
        
        # Also log to file
        if level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

    def start_bot(self):
        """Start the bot in a separate thread"""
        if not self.url_entry.get():
            self.log_message("Please enter a TikTok video URL", "error")
            return
            
        if self.is_running:
            self.log_message("Bot is already running", "error")
            return
            
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        self.current_thread = threading.Thread(target=self._run_bot)
        self.current_thread.start()

    def stop_bot(self):
        """Stop the bot"""
        self.is_running = False
        self.log_message("Stopping bot...")
        self.cleanup()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _run_bot(self):
        """Main bot operation"""
        try:
            self.driver = self._init_driver()
            self.driver.get("https://zefoy.com")
            
            # Așteaptă să apară captcha și informează utilizatorul
            self.log_message("Please complete the captcha in the browser window")
            
            # Așteaptă input field-ul pentru captcha
            try:
                captcha_input = self._wait_for_element(By.TAG_NAME, "input", timeout=30)
                self.log_message("Captcha input field found. Please complete the captcha.")
                
                # Așteaptă până când captcha este rezolvat verificând dacă pagina s-a schimbat
                while True:
                    try:
                        # Verifică dacă există vreun serviciu disponibil
                        self.driver.find_element(By.CLASS_NAME, "t-views-button")
                        self.log_message("Captcha completed successfully")
                        break
                    except:
                        time.sleep(1)
                        continue
                
                # Double refresh for stability
                for _ in range(2):
                    time.sleep(2)
                    self.driver.refresh()
                
                self._check_services_status()
                self._execute_service(
                    self.selected_service.get(),
                    self.url_entry.get()
                )
                
            except TimeoutException:
                self.log_message("Could not find captcha input. Please try again.", "error")
                self.cleanup()
                return
            
        except Exception as e:
            self.log_message(f"Bot operation failed: {e}", "error")
        finally:
            self.cleanup()
            self.is_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    def _wait_for_element(self, by: By, value: str, timeout: int = 15) -> WebElement:
        """Wait for element with improved error handling"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.log_message(f"Element {value} not found after {timeout} seconds", "error")
            raise

    def _check_services_status(self):
        """Check and update the status of all services"""
        for service_key, service in self.services.items():
            try:
                element = self.driver.find_element(By.CLASS_NAME, service.selector)
                service.status = "[WORKING]" if element.is_enabled() else "[OFFLINE]"
                self.service_radios[service_key].configure(
                    state="normal" if service.status == "[WORKING]" else "disabled"
                )
            except NoSuchElementException:
                service.status = "[OFFLINE]"
                self.service_radios[service_key].configure(state="disabled")
            self.log_message(f"Service {service.title} status: {service.status}")

    def _execute_service(self, service: str, video_url: str):
        """Execute the selected service with error handling and retry logic"""
        service_info = self.services[service]
        try:
            # Click service button and wait for container
            self._wait_for_element(By.CLASS_NAME, service_info.selector).click()
            container = self._wait_for_element(
                By.CSS_SELECTOR, 
                "div.col-sm-5.col-xs-12.p-1.container:not(.nonec)"
            )

            # Initialize counters
            success_count = 0
            attempt_count = 0
            max_attempts = 100  # Increased maximum attempts
            
            self.log_message(f"Starting {service_info.title} service for {video_url}")
            
            while self.is_running and attempt_count < max_attempts:
                try:
                    # Adjust timing based on service type
                    if service == "hearts":
                        time.sleep(2)
                    elif service == "followers":
                        time.sleep(3)  # Extra delay for followers
                    
                    result = self._process_service_cycle(container, video_url, service_info.title, service)
                    if result:
                        success_count += 1
                        if service == "followers":
                            self.log_message(f"Successfully sent followers request. Total successful requests: {success_count}")
                        else:
                            self.log_message(f"Success count: {success_count}")
                    attempt_count += 1
                    
                    # Add service-specific delay between requests
                    if self.is_running:
                        if service == "hearts":
                            delay = 3 + random.random() * 2  # 3-5 seconds for hearts
                        elif service == "followers":
                            delay = 5 + random.random() * 3  # 5-8 seconds for followers
                        else:
                            delay = 0.5 + random.random()  # 0.5-1.5 seconds for other services
                        time.sleep(delay)
                        
                except Exception as e:
                    self.log_message(f"Cycle error: {e}", "error")
                    time.sleep(2)
                    
                # Service-specific refresh intervals
                if service == "hearts":
                    refresh_interval = 5
                elif service == "followers":
                    refresh_interval = 3  # More frequent refresh for followers
                else:
                    refresh_interval = 10
                    
                if success_count > 0 and success_count % refresh_interval == 0:
                    self.driver.refresh()
                    time.sleep(3)
                    self._wait_for_element(By.CLASS_NAME, service_info.selector).click()
                    container = self._wait_for_element(
                        By.CSS_SELECTOR, 
                        "div.col-sm-5.col-xs-12.p-1.container:not(.nonec)"
                    )

        except Exception as e:
            self.log_message(f"Service execution failed: {e}", "error")

    def _process_service_cycle(self, container: WebElement, video_url: str, service_title: str, service: str = None) -> bool:
        """Process a single service cycle including submission and waiting"""
        try:
            # Clear and enter URL
            input_element = container.find_element(By.TAG_NAME, "input")
            input_element.clear()
            input_element.send_keys(video_url)

            # Service-specific delays before submit
            if service == "hearts":
                time.sleep(2)
            elif service == "followers":
                time.sleep(3)  # Longer delay for followers

            # Click submit button
            submit_button = container.find_element(By.CSS_SELECTOR, "button.btn.btn-primary")
            submit_button.click()
            
            # Service-specific wait times after submit
            if service == "hearts":
                time.sleep(3)
            elif service == "followers":
                time.sleep(4)  # Longer wait for followers
            else:
                time.sleep(1)

            try:
                # Try to click the confirmation button if it exists
                confirm_button = container.find_element(By.CSS_SELECTOR, "button.btn.btn-dark")
                
                # Service-specific delays before confirmation
                if service == "hearts":
                    time.sleep(1)
                elif service == "followers":
                    time.sleep(2)  # Extra wait before confirming followers
                    
                confirm_button.click()
                
                if service == "followers":
                    self.log_message("Followers request confirmed successfully")
                else:
                    self.log_message(f"{service_title} request sent successfully")
                return True
                
            except NoSuchElementException:
                # Check for waiting time message
                if waiting_time := self._get_waiting_time(container, service):
                    minutes, seconds = divmod(waiting_time, 60)
                    
                    # Service-specific wait time optimization
                    if service == "hearts":
                        optimized_wait = max(waiting_time, 60)
                    elif service == "followers":
                        optimized_wait = max(waiting_time, 120)  # Minimum 120 seconds for followers
                    else:
                        optimized_wait = min(waiting_time, 30)
                    
                    self.log_message(f"Waiting for {optimized_wait} seconds before next attempt")
                    
                    # Wait in small increments to allow for stopping
                    for _ in range(optimized_wait):
                        if not self.is_running:
                            break
                        time.sleep(1)
                        
                    if service == "followers":
                        # Extra verification after wait for followers
                        time.sleep(2)
                return False

        except Exception as e:
            self.log_message(f"Process cycle error: {e}", "error")
            return False

    def _get_waiting_time(self, container: WebElement, service: str = None) -> Optional[int]:
        """Extract and calculate waiting time from container"""
        try:
            time_element = container.find_element(By.CSS_SELECTOR, "span.br")
            if "Please wait" in time_element.text:
                minutes, seconds = map(int, re.findall(r"\d+", time_element.text))
                total_seconds = minutes * 60 + seconds
                
                # Service-specific wait time adjustments
                if service == "hearts":
                    return max(total_seconds, 60)
                elif service == "followers":
                    return max(total_seconds, 120)  # Minimum 120 seconds for followers
                else:
                    return min(total_seconds, 30)
            return None
        except NoSuchElementException:
            return None

    def cleanup(self):
        """Clean up resources and close browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.log_message("Browser closed successfully")
        except Exception as e:
            self.log_message(f"Cleanup failed: {e}", "error")

if __name__ == "__main__":
    app = TikTokBotGUI()
    app.mainloop() 