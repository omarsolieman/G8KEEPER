from screen import Screen
from adafruit_ssd1306 import SSD1306_I2C
from input_handler import InputHandler
import busio
import board
import digitalio

class PasswordManager:
    def __init__(self, BUTTON_PINS, PATTERN_LENGTH, PASSWORDS_FILE):
        self.BUTTON_PINS = BUTTON_PINS
        self.PATTERN_LENGTH = PATTERN_LENGTH
        self.PASSWORDS_FILE = PASSWORDS_FILE
        self.current_screen = LOCK_SCREEN
        self.selected_menu_item = 0
        self.current_password_index = 0
        self.reset_button_press_count = 0
        self.passwords_data = []
        self.character_sets = [
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "0123456789",
            "!@#$%^&*()-=_+"
        ]
        self.character_position = 0
        self.current_set = 0
        self.character_position = 0
        self.user_input_index = 0
        self.user_input = [False] * PATTERN_LENGTH
        self.pattern = [True, False, True, False, True]  # Example pattern "UDUDU" (True, False, True, False, True)
        self.password_input = ""
        self.screen = Screen(SSD1306_I2C(128, 64, busio.I2C(sda=board.GP20, scl=board.GP21)))
        self.input_handler = InputHandler(BUTTON_PINS, PATTERN_LENGTH)

    def load_passwords(self):
        """
        Load passwords from the passwords file.
        """
        try:
            with open(self.PASSWORDS_FILE, "r") as file:
                return [line.strip().split(',') for line in file]
        except Exception as e:
            print("Error loading passwords:", e)
            return []

    def save_passwords(self):
        """
        Save passwords to the passwords file.
        """
        with open(self.PASSWORDS_FILE, "w") as file:
            for entry in self.passwords_data:
                file.write(','.join(entry) + '\n')

    def handle_lock_screen(self):
        """
        Handle input for the lock screen.
        """
        print("Current screen: LOCK_SCREEN")
        self.screen.draw_lock_screen(self.user_input_index)

        if not self.BUTTON_PINS["UP"].value:
            self.input_handler.record_user_input(True)
        elif not self.BUTTON_PINS["DOWN"].value:
            self.input_handler.record_user_input(False)

        if self.input_handler.user_input_index == self.PATTERN_LENGTH:
            if self.input_handler.check_pattern():
                self.reset_button_press_count = 0  # Reset the counter when the correct pattern is entered
                self.current_screen = MAIN_MENU
            else:
                self.input_handler.reset_user_input()

    def handle_main_menu(self):
        """
        Handle input for the main menu.
        """
        print("Current screen: MAIN_MENU")
        self.screen.draw_main_menu(self.selected_menu_item)

        if not self.BUTTON_PINS["UP"].value:
            self.selected_menu_item = (self.selected_menu_item + 3) % 4
        elif not self.BUTTON_PINS["DOWN"].value:
            self.selected_menu_item = (self.selected_menu_item + 1) % 4

        if not self.BUTTON_PINS["CLICK"].value:
            self.handle_selected_menu_item()

        # Check for SET button press
        if self.BUTTON_PINS["SET"].value == 0:
            self.current_screen = LOCK_SCREEN

        if self.BUTTON_PINS["RESET"].value == 0:
            self.reset_button_press_count += 1
            if self.reset_button_press_count >= 3:
                self.reset_button_press_count = 0
                self.current_screen = LOCK_SCREEN

    def handle_view_passwords(self):
        """
        Handle input for viewing passwords.
        """
        print("Current screen: VIEW_PASSWORDS")
        self.screen.draw_view_passwords(self.passwords_data, self.current_password_index)

        if not self.BUTTON_PINS["UP"].value:
            self.current_password_index = (self.current_password_index + len(self.passwords_data) - 1) % len(self.passwords_data)
        elif not self.BUTTON_PINS["DOWN"].value:
            self.current_password_index = (self.current_password_index + 1) % len(self.passwords_data)

        if self.BUTTON_PINS["SET"].value == 0:
            self.current_screen = MAIN_MENU

        if self.BUTTON_PINS["RESET"].value == 0:
            self.input_handler.initialize_usb_hid()
            self.input_handler.SendStringHID(self.passwords_data[self.current_password_index][2])

    def handle_add_password(self):
        """
        Handle input for adding a new password.
        """
        print("Current screen: ADD_PASSWORD")
        self.screen.draw_add_password(self.password_input, self.current_set, self.character_position)

        if not self.BUTTON_PINS["UP"].value:
            self.cycle_next_character()
        elif not self.BUTTON_PINS["DOWN"].value:
            self.cycle_previous_character()
        elif not self.BUTTON_PINS["LEFT"].value:
            self.switch_to_previous_set()
        elif not self.BUTTON_PINS["RIGHT"].value:
            self.switch_to_next_set()
        elif not self.BUTTON_PINS["CLICK"].value:
            if self.input_handler.debounce_button(self.BUTTON_PINS["CLICK"]):
                if self.confirm_character():
                    if len(self.password_input) == MAX_PASSWORD_LENGTH:
                        new_password_entry = [self.password_input] + [self.get_current_character()] * 2
                        self.passwords_data.append(new_password_entry)
                        self.save_passwords()
                        self.password_input = ""
                        self.current_screen = MAIN_MENU
                    else:
                        self.password_input += self.character_sets[self.current_set][self.character_position]

        if self.BUTTON_PINS["SET"].value == 0:
            self.current_screen = MAIN_MENU

    def handle_generate_password(self):
        """
        Handle input for generating a password.
        """
        print("Current screen: GENERATE_PASSWORD")
        self.screen.draw_generate_password()

        if self.BUTTON_PINS["RESET"].value == 0:
            password = self.input_handler.generate_random_password(12, 'Medium')
            self.screen.display_generated_password(password)
            self.current_screen = GENERATE_PASSWORD
        if self.BUTTON_PINS["SET"].value == 0:
            self.current_screen = MAIN_MENU
        if self.BUTTON_PINS["UP"].value == 0:
            password = self.input_handler.generate_random_password(14, 'High')
            self.screen.display_generated_password(password)
            self.current_screen = GENERATE_PASSWORD
        if self.BUTTON_PINS["DOWN"].value == 0:
            password = self.input_handler.generate_random_password(12, 'Medium')
            self.screen.display_generated_password(password)
            self.current_screen = GENERATE_PASSWORD

    def run(self):
        """
        Main loop to run the password manager.
        """
        while True:
            if self.current_screen == LOCK_SCREEN:
                self.handle_lock_screen()
            elif self.current_screen == MAIN_MENU:
                self.handle_main_menu()
            elif self.current_screen == VIEW_PASSWORDS:
                self.handle_view_passwords()
            elif self.current_screen == ADD_PASSWORD:
                self.handle_add_password()
            elif self.current_screen == GENERATE_PASSWORD:
                self.handle_generate_password()