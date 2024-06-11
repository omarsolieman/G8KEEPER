# password_manager.py

from oled_display import OLEDDisplay
from user_input import PasswordManagerInput
from password_storage import PasswordStorage
from password_generator import PasswordGenerator
from config import PATTERN_LENGTH, MAX_PASSWORD_LENGTH, LOCK_SCREEN, MAIN_MENU, VIEW_PASSWORDS, ADD_PASSWORD, GENERATE_PASSWORD, RTC_SETUP, character_sets, unlock_pattern
from autotype import AutoType
import time
import busio
import board
from rtc_manager import RTCManager

class PasswordManager:
    def __init__(self):
        self.i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
        self.display = OLEDDisplay(self.i2c)
        self.rtc_manager = RTCManager(self.i2c)
        self.user_input = PasswordManagerInput(self)
        self.password_storage = PasswordStorage(unlock_pattern)
        self.password_generator = PasswordGenerator()
        self.current_screen = LOCK_SCREEN
        self.selected_menu_item = 0
        self.current_password_page = 0
        self.password_complexity = "High"
        self.password_length = 14
        self.current_password_index = 0
        self.reset_button_press_count = 0
        self.user_input_pattern = [""] * PATTERN_LENGTH
        self.pattern = unlock_pattern
        self.user_input_index = 0
        self.password_input = ""
        self.autotype = AutoType()
        self.website_input = ""
        self.username_input = ""
        self.current_set = 0
        self.character_position = 0
        self.passwords_data = self.password_storage.load_passwords()
        self.character_sets = character_sets
        self.main_menu_items = ["View Passwords", "Add Password", "Generate Password", "Lock Device", "RTC Setup"]
        self.rtc_menu_items = ["Set Time", "Check Time", "Check Status", "Back"]
        
        self.button_actions = {
            LOCK_SCREEN: {
                "UP": lambda: self.record_user_input("up"),
                "DOWN": lambda: self.record_user_input("down"),
                "LEFT": lambda: self.record_user_input("left"),
                "RIGHT": lambda: self.record_user_input("right"),
                "CLICK": lambda: self.record_user_input("click"),
                "SET": self.handle_lock_screen_set_button_pressed
            },
            MAIN_MENU: {
                "UP": lambda: self.handle_menu_navigation("UP"),
                "DOWN": lambda: self.handle_menu_navigation("DOWN"),
                "SET": self.handle_main_menu_set_button_pressed,
                "RESET": self.handle_main_menu_reset_button_pressed
            },
            VIEW_PASSWORDS: {
                "UP": lambda: self.handle_view_passwords_navigation("UP"),
                "DOWN": lambda: self.handle_view_passwords_navigation("DOWN"),
                "LEFT": lambda: self.handle_view_passwords_navigation("LEFT"),
                "RIGHT": lambda: self.handle_view_passwords_navigation("RIGHT"),
                "SET": self.handle_back_button_pressed,
                "RESET": self.type_password_entry
            },
            ADD_PASSWORD: {
                "UP": self.cycle_next_character,
                "DOWN": self.cycle_previous_character,
                "LEFT": self.switch_to_previous_set,
                "RIGHT": self.switch_to_next_set,
                "SET": self.handle_back_button_pressed
            },
            GENERATE_PASSWORD: {
                "UP": lambda: self.handle_generate_password_length("UP"),
                "DOWN": lambda: self.handle_generate_password_length("DOWN"),
                "SET": self.handle_back_button_pressed
            },
            RTC_SETUP: {
                "UP": lambda: self.handle_menu_navigation("UP"),
                "DOWN": lambda: self.handle_menu_navigation("DOWN"),
                "SET": self.handle_rtc_set_button_pressed
            }
        }
    
    def run(self):
        while True:
            self.user_input.update()
            self.handle_current_screen()
            
    def handle_current_screen(self):
        screen_handlers = {
            LOCK_SCREEN: self.handle_lock_screen,
            RTC_SETUP: self.handle_rtc_setup,
            MAIN_MENU: self.handle_main_menu,
            VIEW_PASSWORDS: self.handle_view_passwords,  # changed to a wrapper method
            ADD_PASSWORD: self.handle_add_password,
            GENERATE_PASSWORD: self.handle_generate_password
        }
        handler = screen_handlers.get(self.current_screen)
        if handler:
            handler()
            
    def handle_rtc_setup(self):
        self.display_menu(self.rtc_menu_items)
        
    def display_menu(self, menu_items):
        self.display.clear()
        max_display_items = 4
        start_index, end_index = self.get_menu_display_range(menu_items, max_display_items)
        for i in range(start_index, end_index):
            if i == self.selected_menu_item:
                self.display.display_text("> " + menu_items[i], 5, 10 + (i - start_index) * 15)
            else:
                self.display.display_text("  " + menu_items[i], 5, 10 + (i - start_index) * 15)
        self.display.update_display()

    def get_menu_display_range(self, menu_items, max_display_items):
        if self.selected_menu_item < max_display_items:
            start_index = 0
            end_index = max_display_items
        elif self.selected_menu_item >= len(menu_items) - max_display_items:
            start_index = len(menu_items) - max_display_items
            end_index = len(menu_items)
        else:
            start_index = self.selected_menu_item - (max_display_items // 2)
            end_index = start_index + max_display_items
        return start_index, end_index

    def handle_lock_screen(self):
        self.display.clear()
        self.display.display_text("Device Locked", 10, 5)
        self.display.display_text("Enter pattern:", 10, 20)
        for i in range(self.user_input_index):
            self.display.display_text("*", 10 + i * 10, 40)
        self.display.update_display()
        time.sleep(0.1)
        
    def handle_rtc_setup(self):
        self.display.clear()
        menu_items = ["Set Time", "Check Time", "Check Status", "Back"]
        for i, item in enumerate(menu_items):
            if i == self.selected_menu_item:
                self.display.display_text("> " + item, 5, 10 + i * 15)
            else:
                self.display.display_text("  " + item, 5, 10 + i * 15)
        self.display.update_display()

        if self.user_input.on_button_pressed("SET"):
            if self.selected_menu_item == 0:
                self.rtc_manager.handle_set_time()
            elif self.selected_menu_item == 1:
                current_time = self.rtc_manager.handle_check_time()
                self.display_time(current_time)
            elif self.selected_menu_item == 2:
                temp_c, temp_f = self.rtc_manager.handle_check_status()
                self.display_temperature(temp_c, temp_f)
            elif self.selected_menu_item == 3:
                self.current_screen = MAIN_MENU

    def display_time(self, current_time):
        self.display.clear()
        if current_time:
            self.display.display_text("Current Time:", 5, 5)
            self.display.display_text(str(current_time), 5, 20)
        else:
            self.display.display_text("RTC is not initialized.", 5, 5)
        self.display.display_text("Back", 5, 50)
        self.display.update_display()

    def display_temperature(self, temp_c, temp_f):
        self.display.clear()
        if temp_c is not None and temp_f is not None:
            self.display.display_text(f"Temperature: {temp_c:.2f} C ({temp_f:.2f} F)", 5, 5)
        else:
            self.display.display_text("RTC is not initialized or not connected properly.", 5, 5)
        self.display.display_text("Back", 5, 50)
        self.display.update_display()
        
    def generate_password(self):
        password = self.password_generator.generate_password(self.password_length, self.password_complexity)
        self.display.clear()
        self.display.display_text("Generated password:", 5, 5)
        self.display.display_text(password, 5, 20)
        self.display.display_text("Back", 5, 80)
        self.display.update_display()

    def lock_device(self):
        self.current_screen = LOCK_SCREEN
        self.reset_user_input()


    def handle_main_menu(self):
        self.display_menu(self.main_menu_items)
    
    def handle_view_passwords(self):
        print("Received passwords data:", self.passwords_data)  # Debugging statement
        self.display.clear()
        if self.passwords_data:
            password_entry = self.passwords_data[self.current_password_index]
            print("Current password entry:", password_entry)  # Debugging statement
            if self.current_password_page == 0:
                self.display.display_text(f"Password {self.current_password_index + 1}/{len(self.passwords_data)}", 5, 5)
                self.display.display_text("Website:", 5, 20)
                self.display.display_text(password_entry[0], 5, 35)
                self.display.display_text("Next", 5, 50)
            elif self.current_password_page == 1:
                self.display.display_text(f"Password {self.current_password_index + 1}/{len(self.passwords_data)}", 5, 5)
                self.display.display_text("Username:", 5, 20)
                self.display.display_text(password_entry[1], 5, 35)
                self.display.display_text("Next", 5, 50)
            elif self.current_password_page == 2:
                self.display.display_text(f"Password {self.current_password_index + 1}/{len(self.passwords_data)}", 5, 5)
                self.display.display_text("Password:", 5, 20)
                self.display.display_text(password_entry[2], 5, 35)
                self.display.display_text("Back", 5, 50)
        else:
            self.display.display_text("No passwords found", 5, 20)
            self.display.display_text("Back", 5, 50)
        self.display.update_display()

    def handle_add_password(self):
        self.display.clear()
        self.display.display_text("Enter website:", 5, 5)
        self.display.display_text(self.website_input, 5, 20)
        self.display.display_text("Enter username:", 5, 35)
        self.display.display_text(self.username_input, 5, 50)
        self.display.display_text("Enter password:", 5, 65)
        self.display.display_text(self.password_input, 5, 80)
        self.display.display_text("Current character:", 5, 95)
        self.display.display_text(self.get_current_character(), 5, 110)
        self.display.display_text("Save", 5, 125)
        self.display.display_text("Back", 5, 140)
        self.display.update_display()

    def handle_generate_password(self):
        self.display.clear()
        self.display.display_text("Password Length:", 5, 5)
        self.display.display_text(str(self.password_length), 5, 20)
        self.display.display_text("Password Complexity:", 5, 35)
        self.display.display_text(self.password_complexity, 5, 50)
        self.display.display_text("Generate", 5, 65)
        self.display.display_text("Back", 5, 80)
        self.display.update_display()

    def handle_button_press(self, button_name):
        print(f"Button pressed: {button_name} on screen {self.current_screen}")  # Debugging statement
        action = self.button_actions.get(self.current_screen, {}).get(button_name)
        if action:
            action()
        else:
            print(f"No action defined for button {button_name} on screen {self.current_screen}")  # Debugging statement


    def record_user_input_true(self):
        self.record_user_input(True)

    def record_user_input_false(self):
        self.record_user_input(False)

    def handle_lock_screen_set_button_pressed(self):
        print("Handling lock screen SET button press")  # Debugging statement
        if self.check_pattern():
            self.reset_button_press_count = 0
            self.current_screen = MAIN_MENU
        else:
            self.reset_user_input()

    def handle_menu_navigation(self, button_name):
        if button_name == "UP":
            self.selected_menu_item = (self.selected_menu_item - 1) % len(self.main_menu_items)
        elif button_name == "DOWN":
            self.selected_menu_item = (self.selected_menu_item + 1) % len(self.main_menu_items)
        self.handle_current_screen()
        print(f"Menu navigation: {button_name}, selected item: {self.selected_menu_item}")  # Debugging statement

    def handle_main_menu_set_button_pressed(self):
        if self.selected_menu_item == 0:
            self.current_screen = VIEW_PASSWORDS
            self.current_password_index = 0
        elif self.selected_menu_item == 1:
            self.current_screen = ADD_PASSWORD
            self.password_input = ""
            self.current_set = 0
            self.character_position = 0
        elif self.selected_menu_item == 2:
            self.current_screen = GENERATE_PASSWORD
        elif self.selected_menu_item == 3:
            self.lock_device()
        elif self.selected_menu_item == 4:
            self.current_screen = RTC_SETUP

    def handle_main_menu_reset_button_pressed(self):
        self.reset_button_press_count += 1
        if self.reset_button_press_count >= 3:
            self.reset_button_press_count = 0
            self.lock_device()

    def handle_generate_password_length(self, button_name):
        if self.current_screen == GENERATE_PASSWORD:
            self.password_length = (self.password_length % MAX_PASSWORD_LENGTH) + 1

    def handle_view_passwords_navigation(self, button_name):
        if self.current_screen == VIEW_PASSWORDS:
            if button_name == "RIGHT":
                self.current_password_index = (self.current_password_index + 1) % len(self.passwords_data)
            elif button_name == "LEFT":
                self.current_password_index = (self.current_password_index - 1) % len(self.passwords_data)
            elif button_name == "UP":
                self.current_password_page = (self.current_password_page + 1) % 3
            elif button_name == "DOWN":
                self.current_password_page = (self.current_password_page - 1) % 3

    def handle_back_button_pressed(self):
        self.current_screen = MAIN_MENU


    def handle_rtc_set_button_pressed(self):
        if self.selected_menu_item == 0:
            self.rtc_manager.handle_set_time()
        elif self.selected_menu_item == 1:
            current_time = self.rtc_manager.handle_check_time()
            self.display_time(current_time)
        elif self.selected_menu_item == 2:
            temp_c, temp_f = self.rtc_manager.handle_check_status()
            self.display_temperature(temp_c, temp_f)
        elif self.selected_menu_item == 3:
            self.current_screen = MAIN_MENU

    def record_user_input(self, direction):
        print(f"Recording user input: {direction}")  # Debugging statement
        self.user_input_pattern[self.user_input_index] = direction
        self.user_input_index += 1
        if self.user_input_index == PATTERN_LENGTH:
            self.user_input_index = 0
        print(f"Updated user input pattern: {self.user_input_pattern}")  # Debugging statement

    def reset_user_input(self):
        self.user_input_index = 0
        self.user_input_pattern = [False] * PATTERN_LENGTH

    def check_pattern(self):
        print(f"Checking pattern:")  # Debugging statement
        print(f"User input pattern: {self.user_input_pattern}")  # Debugging statement
        print(f"Expected pattern: {self.pattern}")  # Debugging statement
        return self.user_input_pattern == self.pattern

    def type_password_entry(self):
        password_entry = self.passwords_data[self.current_password_index]
        if self.current_password_page == 1:  # Username
            self.autotype.type_text(password_entry[1])
        elif self.current_password_page == 2:  # Password
            self.autotype.type_text(password_entry[2])

    def get_current_character(self):
        current_char_index = self.character_position % len(self.character_sets[self.current_set])
        return self.character_sets[self.current_set][current_char_index]

    def cycle_next_character(self):
        self.character_position = (self.character_position + 1) % len(self.character_sets[self.current_set])

    def cycle_previous_character(self):
        self.character_position = (self.character_position - 1) % len(self.character_sets[self.current_set])

    def switch_to_next_set(self):
        self.current_set = (self.current_set + 1) % len(self.character_sets)
        self.character_position = min(self.character_position, len(self.character_sets[self.current_set]) - 1)

    def switch_to_previous_set(self):
        self.current_set = (self.current_set - 1) % len(self.character_sets)
        self.character_position = min(self.character_position, len(self.character_sets[self.current_set]) - 1)