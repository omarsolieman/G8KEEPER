import board
import busio
import digitalio
from adafruit_ssd1306 import SSD1306_I2C
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import random


# Constants
PATTERN_LENGTH = 5
character_sets = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "!@#$%^&*()-=_+"
]
MAX_PASSWORD_LENGTH = 5
PASSWORDS_FILE = "passwords.csv"
LOCK_SCREEN, MAIN_MENU, VIEW_PASSWORDS, ADD_PASSWORD, GENERATE_PASSWORD = range(5)

# Button pins
BUTTON_PINS = {
    "UP": digitalio.DigitalInOut(board.GP2),
    "DOWN": digitalio.DigitalInOut(board.GP3),
    "LEFT": digitalio.DigitalInOut(board.GP4),
    "RIGHT": digitalio.DigitalInOut(board.GP5),
    "CLICK": digitalio.DigitalInOut(board.GP6),
    "SET": digitalio.DigitalInOut(board.GP7),
    "RESET": digitalio.DigitalInOut(board.GP8),
}

for pin in BUTTON_PINS.values():
    pin.switch_to_input(pull=digitalio.Pull.UP)

# OLED setup
i2c = busio.I2C(sda=board.GP20, scl=board.GP21)
oled = SSD1306_I2C(128, 64, i2c)

# The keyboard object
keyboard = None
keyboard_layout = None

# Define a function to initialize USB HID when the reset button is pressed
def initialize_usb_hid():
    global keyboard, keyboard_layout
    
    # Attempt to import HID related modules, but suppress ImportError
    try:
        from adafruit_hid.keyboard import Keyboard
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
        usb_hid_available = True
    except ImportError:
        usb_hid_available = False

    if usb_hid_available:
        keyboard = Keyboard(usb_hid.devices)
        keyboard_layout = KeyboardLayoutUS(keyboard)
    else:
        print("USB HID not available.")

# Global variables
current_screen = LOCK_SCREEN
selected_menu_item = 0
current_password_index = 0
reset_button_press_count = 0
user_input = [False] * PATTERN_LENGTH
pattern = [True, False, True, False, True]  # Example pattern "UDUDU" (True, False, True, False, True) last high to select
user_input_index = 0
password_input = ""
current_set = 0
character_position = 0

# Define SendStringHID function
def SendStringHID(string):
    if keyboard_layout:
        keyboard_layout.write(string)
        print(f"Typed: {string}")
    else:
        print("USB HID not available. String not sent.")


def draw_lock_screen():
    """
    Draw the lock screen on the OLED display.
    """
    oled.fill(0)
    oled.text("Device Locked", 10, 5, 1)  # Adding '1' as the color argument for white text
    oled.text("Enter pattern:", 10, 20, 1)
    for i in range(user_input_index):
        oled.text("*", 10 + i * 10, 40, 1)  # Adding '1' as the color argument for white text
    oled.show()

def handle_lock_screen_input():
    """
    Handle input for the lock screen.
    """
    global reset_button_press_count

    if not BUTTON_PINS["UP"].value:
        record_user_input(True)
    elif not BUTTON_PINS["DOWN"].value:
        record_user_input(False)

    if user_input_index == PATTERN_LENGTH:
        if check_pattern():
            reset_button_press_count = 0  # Reset the counter when the correct pattern is entered
            go_to_main_menu()
        else:
            reset_user_input()

def load_passwords():
    """
    Load passwords from the passwords file.
    """
    try:
        with open(PASSWORDS_FILE, "r") as file:
            return [line.strip().split(',') for line in file]
    except Exception as e:
        print("Error loading passwords:", e)
        return []

def save_passwords(passwords_data):
    """
    Save passwords to the passwords file.
    """
    with open(PASSWORDS_FILE, "w") as file:
        for entry in passwords_data:
            file.write(','.join(entry) + '\n')

def display_password_entry(website, username, password):
    oled.fill(0)
    oled.text(website, 5, 10)
    oled.text(username, 5, 30)
    oled.text(password, 5, 50)
    oled.show()

def draw_main_menu():
    oled.fill(0)
    for i in range(selected_menu_item, min(selected_menu_item + 4, 5)):
        menu_item_text = f" {get_menu_text(i)}"
        oled.text(menu_item_text, -3, 10 + (i - selected_menu_item) * 20, 1)  # Adding '1' as the color argument for white text

    scrollbar_y = 10 + (selected_menu_item * 10)  # Adjust as needed
    oled.rect(120, 10, 4, 40, 1)  # Scrollbar frame
    oled.fill_rect(120, scrollbar_y, 2, 10, 1)  # Scrollbar indicator
    oled.show()

def draw_view_passwords():
    oled.fill(0)
    for i in range(current_password_index, min(current_password_index + 1, len(passwords_data))):
        # Center the website text
        x_website = (128 - len(passwords_data[i][0]) * 6) // 2
        oled.text(passwords_data[i][0], x_website, 10, 1)  # Adding '1' as the color argument for white text

        # Center the username text
        x_username = (128 - len(passwords_data[i][1]) * 6) // 2
        oled.text(passwords_data[i][1], x_username, 30, 1)  # Adding '1' as the color argument for white textcurrent_set

        # Center the password text
        x_password = (128 - len(passwords_data[i][2]) * 6) // 2
        oled.text(passwords_data[i][2], x_password, 50, 1)  # Adding '1' as the color argument for white text

    oled.show()

def draw_add_password():
    oled.fill(0)
    oled.text("Enter password:", 5, 10, 1) 
    oled.text(get_current_character() + " " + password_input, 5, 30, 1)
    oled.text("Set: {}".format(character_sets[current_set]), 5, 50, 1)
    oled.show()

def get_current_character():
    current_char_index = (character_position) % len(character_sets[current_set])
    return character_sets[current_set][current_char_index]

def draw_generate_password():
    oled.fill(0)
    oled.text("Length: 12", 10, 10, 1)
    oled.text("Complexity: Medium", 10, 30, 1)
    oled.text("Press SET to generate", 10, 50, 1)
    oled.show()
    
def display_generated_password(password):
    oled.fill(0)
    oled.text("Generated Password:", 5, 10, 1) 
    oled.text(password, 5, 30, 1)
    oled.show()
    time.sleep(10)  # Adjust the delay time as needed
    
# Function to generate a random password
def generate_random_password(length, complexity):
    password = ''
    character_set = ''
    
    if complexity == 'Low':
        character_set = character_sets[0]  # Only uppercase and lowercase letters
    elif complexity == 'Medium':
        character_set = character_sets[0] + character_sets[1]  # Letters and numbers
    elif complexity == 'High':
        character_set = character_sets[0] + character_sets[1] + character_sets[2]  # Letters, numbers, and symbols
    
    for _ in range(length):
        password += random.choice(character_set)
    
    return password

def handle_generate_password_input():
    global current_screen
    
    if BUTTON_PINS["RESET"].value == 0:
        password = generate_random_password(12, 'Medium')  # Example: generate a 12-character password with medium complexity
        display_generated_password(password)
        current_screen = GENERATE_PASSWORD
    if BUTTON_PINS["SET"].value == 0:
        current_screen = MAIN_MENU
        
    if BUTTON_PINS["UP"].value == 0:
        password = generate_random_password(14, 'High')
        display_generated_password(password)
        current_screen = GENERATE_PASSWORD
        
    if BUTTON_PINS["DOWN"].value == 0:
        password = generate_random_password(12, 'Medium')
        display_generated_password(password)
        current_screen = GENERATE_PASSWORD

def get_menu_text(menu_item):
    switcher = {
        0: "View Passwords",
        1: "Add Password",
        2: "Generate Pass",
        3: "Del Password",
        4: "Lock Device",
    }
    return switcher.get(menu_item, "")

def handle_selected_menu_item():
    global current_screen, current_password_index

    if selected_menu_item == 0:
        current_screen = VIEW_PASSWORDS  # Move to view passwords screen
        current_password_index = 0
    elif selected_menu_item == 1:
        current_screen = ADD_PASSWORD  # Move to add password screen
    elif selected_menu_item == 2:
        current_screen = GENERATE_PASSWORD  # Move to generate password screen
    elif selected_menu_item == 3:
        # Delete Password
        pass

    if BUTTON_PINS["SET"].value == 0:
        go_to_main_menu()

def handle_view_passwords_input():
    global current_password_index

    if not BUTTON_PINS["UP"].value:
        current_password_index = (current_password_index + len(passwords_data) - 1) % len(passwords_data)
    elif not BUTTON_PINS["DOWN"].value:
        current_password_index = (current_password_index + 1) % len(passwords_data)

    if BUTTON_PINS["SET"].value == 0:
        go_to_main_menu()
        
    if BUTTON_PINS["RESET"].value == 0:
        initialize_usb_hid()
        SendStringHID(passwords_data[current_password_index][2])

def record_user_input(value):
    global user_input_index
    user_input[user_input_index] = value
    user_input_index += 1

def reset_user_input():
    global user_input_index
    user_input_index = 0
    for i in range(PATTERN_LENGTH):
        user_input[i] = False

def check_pattern():
    for i in range(PATTERN_LENGTH):
        if user_input[i] != pattern[i]:
            return False
    return True

def handle_main_menu_input():
    global selected_menu_item, reset_button_press_count

    if not BUTTON_PINS["UP"].value:
        selected_menu_item = (selected_menu_item + 3) % 4
    elif not BUTTON_PINS["DOWN"].value:
        selected_menu_item = (selected_menu_item + 1) % 4

    if not BUTTON_PINS["CLICK"].value:
        handle_selected_menu_item()

    # Check for SET button press
    if BUTTON_PINS["SET"].value == 0:
        go_to_main_menu()

    if BUTTON_PINS["RESET"].value == 0:
        reset_button_press_count += 1
        if reset_button_press_count >= 3:
            reset_button_press_count = 0
            lock_device()

def handle_add_password_input():
    global current_screen, passwords_data, password_input

    if not BUTTON_PINS["UP"].value:
        cycle_next_character()
    elif not BUTTON_PINS["DOWN"].value:
        cycle_previous_character()
    elif not BUTTON_PINS["LEFT"].value:
        switch_to_previous_set()
    elif not BUTTON_PINS["RIGHT"].value:
        switch_to_next_set()
    elif not BUTTON_PINS["CLICK"].value:
        if debounce(BUTTON_PINS["CLICK"]):
            if confirm_character():
                if len(password_input) == MAX_PASSWORD_LENGTH:
                    new_password_entry = [password_input] + [get_current_character() for _ in range(2)]
                    passwords_data.append(new_password_entry)
                    save_passwords(passwords_data)
                    password_input = ""
                    current_screen = MAIN_MENU
                else:
                    password_input += character_sets[current_set][character_position]

    if BUTTON_PINS["SET"].value == 0:
        go_to_main_menu()

def debounce(pin):
    """
    Debounce the button input to prevent double presses.
    """
    debounce_time = 5  # Adjust as needed (time in milliseconds)
    current_state = pin.value()
    time.sleep_ms(debounce_time)
    return button_pressed == pin.value()

def cycle_next_character():
    global character_position
    character_position = (character_position + 1) % len(character_sets[current_set])

def cycle_previous_character():
    global character_position
    character_position = (character_position - 1) % len(character_sets[current_set])

def switch_to_next_set():
    global current_set, character_position
    current_set = (current_set + 1) % len(character_sets)
    character_position = min(character_position, len(character_sets[current_set]) - 1)

def switch_to_previous_set():
    global current_set, character_position
    current_set = (current_set - 1) % len(character_sets)
    character_position = min(character_position, len(character_sets[current_set]) - 1)

def reset_character_position():
    global character_position
    character_position = 0

def confirm_character():
    """
    Confirm the current character entry.
    """
    return debounce(BUTTON_PINS["CLICK"])

def go_to_main_menu():
    global current_screen
    current_screen = MAIN_MENU

def lock_device():
    global current_screen, user_input_index, reset_button_press_count
    current_screen = LOCK_SCREEN
    reset_user_input()
    reset_button_press_count = 0

# Initialize passwords_data on startup
passwords_data = load_passwords()

# Main loop
while True:
    if current_screen == LOCK_SCREEN:
        draw_lock_screen()
        handle_lock_screen_input()
    elif current_screen == MAIN_MENU:
        draw_main_menu()
        handle_main_menu_input()
    elif current_screen == VIEW_PASSWORDS:
        draw_view_passwords()
        handle_view_passwords_input()
    elif current_screen == ADD_PASSWORD:
        draw_add_password()
        handle_add_password_input()
    elif current_screen == GENERATE_PASSWORD:
        draw_generate_password()
        handle_generate_password_input()

    time.sleep(0.1)  # Adjust as needed
