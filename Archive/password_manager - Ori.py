# password_manager.py

from oled_display import OLEDDisplay
from user_input import PasswordManagerInput
from password_storage import PasswordStorage
from password_generator import PasswordGenerator
from config import PATTERN_LENGTH, MAX_PASSWORD_LENGTH, LOCK_SCREEN, MAIN_MENU, VIEW_PASSWORDS, ADD_PASSWORD, GENERATE_PASSWORD, character_sets
from autotype import AutoType
import time

class PasswordManager:
    def __init__(self):
        self.display = OLEDDisplay()
        self.user_input = PasswordManagerInput(self)
        self.password_storage = PasswordStorage()
        self.password_generator = PasswordGenerator()
        self.current_screen = LOCK_SCREEN
        self.selected_menu_item = 0
        self.current_password_page = 0
        self.current_set = []
        self.password_complexity = "High"
        self.password_length = 14
        self.current_password_index = 0
        self.reset_button_press_count = 0
        self.user_input_pattern = [False] * PATTERN_LENGTH
        self.pattern = [True, False, True, False, True]
        self.user_input_index = 0
        self.password_input = ""
        self.autotype = AutoType()
        self.website_input = ""
        self.username_input = ""
        self.password_input = ""
        self.current_set = 0
        self.character_position = 0
        self.passwords_data = self.password_storage.load_passwords()
        self.character_sets = character_sets  # Add this line

    def run(self):
        while True:
            self.user_input.update()
            if self.current_screen == LOCK_SCREEN:
                self.draw_lock_screen()
            elif self.current_screen == MAIN_MENU:
                self.draw_main_menu()
            elif self.current_screen == VIEW_PASSWORDS:
                self.draw_view_passwords()
            elif self.current_screen == ADD_PASSWORD:
                self.draw_add_password()
            elif self.current_screen == GENERATE_PASSWORD:
                self.draw_generate_password()

    def draw_lock_screen(self):
        self.display.clear()
        self.display.display_text("Device Locked", 10, 5)
        self.display.display_text("Enter pattern:", 10, 20)
        for i in range(self.user_input_index):
            self.display.display_text("*", 10 + i * 10, 40)
        self.display.update_display()

    def draw_main_menu(self):
        self.display.clear()
        menu_items = ["View Passwords", "Add Password", "Generate Password", "Lock Device"]
        for i, item in enumerate(menu_items):
            if i == self.selected_menu_item:
                self.display.display_text("> " + item, 5, 10 + i * 15)
            else:
                self.display.display_text("  " + item, 5, 10 + i * 15)
        self.display.update_display()

    def draw_view_passwords(self):
        self.display.clear()
        if self.passwords_data:
            password_entry = self.passwords_data[self.current_password_index]
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

    def draw_add_password(self):
        self.display.clear()
        self.display.display_text("Enter website:", 5, 5)
        self.display.display_text(self.website_input, 5, 20)
        self.display.display_text("Enter username:", 5, 35)
        self.display.display_text(self.username_input, 5, 50)
        self.display.display_text("Enter password:", 5, 65)
        self.display.display_text(self.password_input, 5, 80)
        self.display.display_text("Current character:", 5, 95)
        self.display.display_text(self.get_current_character(self.current_set, self.character_position), 5, 110)
        self.display.display_text("Save", 5, 125)
        self.display.display_text("Back", 5, 140)
        self.display.update_display()

    def draw_generate_password(self):
        self.display.clear()
        self.display.display_text("Password Length:", 5, 5)
        self.display.display_text(str(self.password_length), 5, 20)
        self.display.display_text("Password Complexity:", 5, 35)
        self.display.display_text(self.password_complexity, 5, 50)
        self.display.display_text("Generate", 5, 65)
        self.display.display_text("Back", 5, 80)
        self.display.update_display()

    # ... (rest of the code remains the 

    def handle_up_button_pressed(self):
        if self.current_screen == LOCK_SCREEN:
            self.record_user_input(True)
        elif self.current_screen == MAIN_MENU:
            self.selected_menu_item = (self.selected_menu_item - 1) % 4
        elif self.current_screen == VIEW_PASSWORDS:
            self.current_password_page = (self.current_password_page - 1) % 3
        elif self.current_screen == ADD_PASSWORD:
            if self.display.display_text("Save", 5, 125):
                self.save_password()
            elif self.display.display_text("Back", 5, 140):
                self.go_to_main_menu()
            else:
                self.cycle_next_character()
        elif self.current_screen == GENERATE_PASSWORD:
            if self.display.display_text("Generate", 5, 65):
                self.generate_password()
            elif self.display.display_text("Back", 5, 80):
                self.go_to_main_menu()
            else:
                self.password_length = min(self.password_length + 1, 32)

    def handle_down_button_pressed(self):
        if self.current_screen == LOCK_SCREEN:
            self.record_user_input(False)
        elif self.current_screen == MAIN_MENU:
            self.selected_menu_item = (self.selected_menu_item + 1) % 4
        elif self.current_screen == VIEW_PASSWORDS:
            self.current_password_page = (self.current_password_page + 1) % 3
        elif self.current_screen == ADD_PASSWORD:
            if self.display.display_text("Save", 5, 125):
                self.cycle_previous_character()
            elif self.display.display_text("Back", 5, 140):
                self.go_to_main_menu()
        elif self.current_screen == GENERATE_PASSWORD:
            if self.display.display_text("Generate", 5, 65):
                self.password_complexity = "Low" if self.password_complexity == "High" else "High"
            elif self.display.display_text("Back", 5, 80):
                self.password_length = max(self.password_length - 1, 8)

    def handle_left_button_pressed(self):
        if self.current_screen == VIEW_PASSWORDS:
            self.current_password_index = (self.current_password_index - 1) % len(self.passwords_data)
            self.current_password_page = 0
        elif self.current_screen == ADD_PASSWORD:
            self.switch_to_previous_set()

    def handle_right_button_pressed(self):
        if self.current_screen == VIEW_PASSWORDS:
            self.current_password_index = (self.current_password_index + 1) % len(self.passwords_data)
            self.current_password_page = 0
        elif self.current_screen == ADD_PASSWORD:
            self.switch_to_next_set()

    def handle_set_button_pressed(self):
        if self.current_screen == MAIN_MENU:
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
        elif self.current_screen == VIEW_PASSWORDS:
            self.go_to_main_menu()
        elif self.current_screen == ADD_PASSWORD:
            self.go_to_main_menu()
        elif self.current_screen == GENERATE_PASSWORD:
            self.go_to_main_menu()

    def handle_reset_button_pressed(self):
        if self.current_screen == VIEW_PASSWORDS:
            self.type_password_entry()
        elif self.current_screen == MAIN_MENU:
            self.reset_button_press_count += 1
            if self.reset_button_press_count >= 3:
                self.reset_button_press_count = 0
                self.lock_device()

    def record_user_input(self, value):
        self.user_input_pattern[self.user_input_index] = value
        self.user_input_index += 1
        if self.user_input_index == PATTERN_LENGTH:
            if self.check_pattern():
                self.reset_button_press_count = 0
                self.go_to_main_menu()
            else:
                self.reset_user_input()

    def reset_user_input(self):
        self.user_input_index = 0
        self.user_input_pattern = [False] * PATTERN_LENGTH

    def check_pattern(self):
        return self.user_input_pattern == self.pattern

    def go_to_main_menu(self):
        self.current_screen = MAIN_MENU

    def type_password_entry(self):
        password_entry = self.passwords_data[self.current_password_index]
        if self.current_password_page == 1:  # Username
            self.autotype.type_text(password_entry[1])
        elif self.current_password_page == 2:  # Password
            self.autotype.type_text(password_entry[2])

    def get_current_character(self, current_set, character_position):
        current_char_index = (character_position) % len(self.character_sets[current_set])
        return self.character_sets[current_set][current_char_index]

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

    def save_password(self):
        if not self.website_input:
            self.display.display_text("Website cannot be empty!", 5, 140)
            self.display.update_display()
            time.sleep(1)
            return
        if not self.username_input:
            self.display.display_text("Username cannot be empty!", 5, 140)
            self.display.update_display()
            time.sleep(1)
            return
        if not self.password_input:
            self.display.display_text("Password cannot be empty!", 5, 140)
            self.display.update_display()
            time.sleep(1)
            return

        self.passwords_data.append([self.website_input, self.username_input, self.password_input])
        self.password_storage.save_passwords(self.passwords_data)
        self.website_input = ""
        self.username_input = ""
        self.password_input = ""
        self.display.display_text("Password saved!", 5, 140)
        self.display.update_display()
        time.sleep(1)
        self.go_to_main_menu()

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