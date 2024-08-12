import board
import busio
import digitalio
from adafruit_ssd1306 import SSD1306_I2C
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import random
import adafruit_ds3231
import os

# Constants
PATTERN_LENGTH = 5
character_sets = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "!@#$%^&*()-=_+"
]
MAX_PASSWORD_LENGTH = 5
PASSWORDS_FILE = "passwords.csv"
LOCK_SCREEN, MAIN_MENU, VIEW_PASSWORDS, ADD_PASSWORD, GENERATE_PASSWORD, RTC_MENU, RTC_SET_TIME, RTC_CHECK_TIME, RTC_CHECK_STATUS, ENCRYPTION_MENU, ENCRYPT_FILE, DECRYPT_FILE, TEST_ENCRYPTION = range(13)

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
# RTC setup
rtc = adafruit_ds3231.DS3231(i2c)


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
passwords_data = []

# Define SendStringHID function
def SendStringHID(string):
    if keyboard_layout:
        keyboard_layout.write(string)
        print(f"Typed: {string}")
    else:
        print("USB HID not available. String not sent.")


def draw_loading_screen():
    oled.fill(0)
    oled.text("Password Manager", 10, 10, 1)
    oled.text("Loading...", 30, 30, 1)
    oled.show()

    # Animate loading dots
    for i in range(3):
        time.sleep(0.5)
        oled.text("." * (i + 1), 90, 30, 1)
        oled.show()

def draw_lock_screen():
    """
    Draw the lock screen on the OLED display with centered time above "Device Locked".
    """
    global user_input_index
    
    print(f"Drawing lock screen. user_input_index: {user_input_index}")  # Debug print

    oled.fill(0)
    
    # Display current time
    current_time = rtc.datetime
    time_str = f"{current_time.tm_hour:02d}:{current_time.tm_min:02d}"
    time_width = len(time_str) * 8
    time_x = (128 - time_width) // 2
    oled.text(time_str, time_x, 5, 1)
    
    oled.text("Device Locked", 10, 20, 1)
    oled.text("Enter pattern:", 10, 35, 1)
    
    for i in range(user_input_index):
        oled.text("*", 10 + i * 10, 50, 1)
    
    oled.show()

def update_lock_screen_time():
    current_time = rtc.datetime
    time_str = f"{current_time.tm_hour:02d}:{current_time.tm_min:02d}"
    time_width = len(time_str) * 8
    time_x = (128 - time_width) // 2
    oled.fill_rect(0, 5, 128, 8, 0)  # Clear the entire time area
    oled.text(time_str, time_x, 5, 1)
    oled.show()
    

    
    
def handle_lock_screen_input():
    global user_input_index, current_screen

    if not BUTTON_PINS["UP"].value:
        print("UP button pressed")  # Debug print
        record_user_input(True)
    elif not BUTTON_PINS["DOWN"].value:
        print("DOWN button pressed")  # Debug print
        record_user_input(False)

    print(f"Current user_input_index: {user_input_index}")  # Debug print

    if user_input_index == PATTERN_LENGTH:
        print("Pattern length reached")  # Debug print
        if check_pattern():
            print("Correct pattern entered")  # Debug print
            decrypt_file()  # Decrypt the file when unlocking
            current_screen = MAIN_MENU
            reset_user_input()
        else:
            print("Incorrect pattern")  # Debug print
            reset_user_input()
    
    draw_lock_screen()

def load_passwords():
    try:
        with open(PASSWORDS_FILE, "r") as file:
            return [line.strip().split(',') for line in file]
    except Exception as e:
        print("Error loading passwords:", e)
        return []
    
def save_passwords(passwords_data):
    with open(PASSWORDS_FILE, "w") as file:
        for entry in passwords_data:
            file.write(','.join(entry) + '\n')
            
def display_password_entry(website, username, password):
    oled.fill(0)
    oled.text(website, 5, 10, 1)
    oled.text(username, 5, 30, 1)
    oled.text(password, 5, 50, 1)
    oled.show()

def draw_main_menu():
    oled.fill(0)
    for i in range(selected_menu_item, min(selected_menu_item + 4, 8)):
        menu_item_text = f" {get_menu_text(i)}"
        oled.text(menu_item_text, -3, 10 + (i - selected_menu_item) * 20, 1)  # Adding '1' as the color argument for white text

    scrollbar_y = 10 + (selected_menu_item * 10)  # Adjust as needed
    oled.rect(121, 10, 1, 64, 1)  # Scrollbar frame
    oled.fill_rect(120, scrollbar_y, 3, 8, 1)  # Scrollbar indicator
    oled.show()

def center_text(text, y, max_width=128):
    text_width = len(text) * 6  # Assuming each character is 6 pixels wide
    if text_width > max_width:
        text = truncate_text(text, max_width // 6)
        text_width = len(text) * 6
    x = (max_width - text_width) // 2
    oled.text(text, x, y, 1)

def draw_view_passwords():
    global passwords_data
    if not passwords_data:
        passwords_data = load_and_decrypt_passwords()

    oled.fill(0)
    if not passwords_data:
        center_text("No passwords", 30)
    else:
        entry = passwords_data[current_password_index]
        
        # Display password count and current index
        oled.text(f"{current_password_index + 1}/{len(passwords_data)}", 0, 0, 1)
        
        # Display current password details (centered)
        center_text(entry[0], 8)  # Website
        center_text(entry[1], 24)  # Username
        center_text(entry[2], 40)  # Password
        
        # Display navigation hints
        oled.text("^v:Nav <:Back >:Type", 0, 56, 1)

    oled.show()
    
def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def draw_password_detail():
    oled.fill(0)
    entry = passwords_data[current_password_index]
    oled.text("Password:", 0, 0, 1)
    
    # Split password into multiple lines if necessary
    password = entry[2]
    max_chars_per_line = 16
    for i in range(0, len(password), max_chars_per_line):
        line = password[i:i+max_chars_per_line]
        oled.text(line, 0, 16 + (i // max_chars_per_line) * 10, 1)
    
    oled.text("CLICK:Back RST:Type", 0, 56, 1)
    oled.show()
    
    # Wait for button press
    while True:
        if not BUTTON_PINS["CLICK"].value or BUTTON_PINS["SET"].value == 0:
            time.sleep(0.2)  # Debounce delay
            break
        elif BUTTON_PINS["RESET"].value == 0:
            initialize_usb_hid()
            SendStringHID(entry[2])
            time.sleep(0.2)  # Debounce delay

def draw_add_password():
    oled.fill(0)
    oled.text("Enter password:", 5, 10, 1) 
    oled.text(get_current_character() + " " + password_input, 5, 30, 1)
    oled.text("Set: {}".format(character_sets[current_set]), 5, 50, 1)
    oled.show()
    
def draw_add_name():
    oled.fill(0)
    oled.text("Enter username:", 5, 10, 1) 
    oled.text(get_current_character() + " " + name_input, 5, 30, 1)
    oled.text("Set: {}".format(character_sets[current_set]), 5, 50, 1)
    oled.show()

def draw_add_website():
    oled.fill(0)
    oled.text("Enter website:", 5, 10, 1) 
    oled.text(get_current_character() + " " + website_input, 5, 30, 1)
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
        4: "RTC Menu",
        5: "Lock Device",
        6: "Encryption",
        7: "Start Encryption",
    }
    return switcher.get(menu_item, "")

def handle_selected_menu_item():
    global current_screen, current_password_index

    if selected_menu_item == 0:
        current_screen = VIEW_PASSWORDS
        current_password_index = 0
        print("Switching to VIEW_PASSWORDS screen")  # Debug print
    elif selected_menu_item == 1:
        current_screen = ADD_PASSWORD
    elif selected_menu_item == 2:
        current_screen = GENERATE_PASSWORD
    elif selected_menu_item == 3:
        # Delete Password
        pass
    elif selected_menu_item == 4:
        current_screen = RTC_MENU
    elif selected_menu_item == 5:
        lock_device()
    elif selected_menu_item == 6:
        current_screen = ENCRYPTION_MENU
    elif selected_menu_item == 7:
        current_screen = TEST_ENCRYPTION

    # Remove this line as it's preventing the screen from changing
    if BUTTON_PINS["SET"].value == 0:
        go_to_main_menu()


def handle_view_passwords_input():
    global current_password_index, current_screen

    if not BUTTON_PINS["UP"].value:
        current_password_index = (current_password_index - 1) % len(passwords_data)
        time.sleep(0.1)  # Debounce delay
    elif not BUTTON_PINS["DOWN"].value:
        current_password_index = (current_password_index + 1) % len(passwords_data)
        time.sleep(0.1)  # Debounce delay
    elif BUTTON_PINS["LEFT"].value == 0:  # Changed from SET to LEFT
        current_screen = MAIN_MENU
        time.sleep(0.1)  # Debounce delay
    elif BUTTON_PINS["RIGHT"].value == 0:  # Changed from RESET to RIGHT
        initialize_usb_hid()
        SendStringHID(passwords_data[current_password_index][2])
        time.sleep(0.1)  # Debounce delay

    draw_view_passwords()  # Redraw the screen after each input


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
    global selected_menu_item, reset_button_press_count, current_screen

    if not BUTTON_PINS["UP"].value:
        selected_menu_item = (selected_menu_item - 1) % 8
        time.sleep(0.1)  # Debounce delay
    elif not BUTTON_PINS["DOWN"].value:
        selected_menu_item = (selected_menu_item + 1) % 8
        time.sleep(0.1)  # Debounce delay

    if not BUTTON_PINS["CLICK"].value:
        handle_selected_menu_item()
        time.sleep(0.1)  # Debounce delay
        return  # Exit the function after handling the selection

    if BUTTON_PINS["SET"].value == 0:
        go_to_main_menu()
        time.sleep(0.1)  # Debounce delay

    if BUTTON_PINS["RESET"].value == 0:
        reset_button_press_count += 1
        if reset_button_press_count >= 3:
            reset_button_press_count = 0
            lock_device()
        time.sleep(0.2)  # Debounce delay
        
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

def debounce_button(pin):
    """
    Debounce the button input to prevent double presses.
    """
    debounce_time = 5  # Adjust as needed (time in milliseconds)
    current_state = pin.value()
    time.sleep_ms(debounce_time)
    return current_state == pin.value()

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
    encrypt_file()
    current_screen = LOCK_SCREEN
    reset_user_input()
    reset_button_press_count = 0
    
######################RTC#########################
def draw_rtc_menu():
    oled.fill(0)
    oled.text("RTC Menu", 10, 10, 1)
    menu_options = ["Set Time", "Check Time", "Check Status"]
    
    for i, option in enumerate(menu_options):
        if current_screen == RTC_SET_TIME + i:
            oled.text("> " + option, 0, 30 + i * 10, 1)
        else:
            oled.text("  " + option, 0, 30 + i * 10, 1)
    
    oled.show()

def handle_rtc_menu_input():
    global current_screen

    if not BUTTON_PINS["UP"].value:
        current_screen = max(RTC_SET_TIME, current_screen - 1)
        time.sleep(0.2)  # Debounce delay
    elif not BUTTON_PINS["DOWN"].value:
        current_screen = min(RTC_CHECK_STATUS, current_screen + 1)
        time.sleep(0.2)  # Debounce delay
    elif not BUTTON_PINS["CLICK"].value:
        if current_screen == RTC_SET_TIME:
            handle_rtc_set_time_input()
        elif current_screen == RTC_CHECK_TIME:
            handle_rtc_check_time_input()
        elif current_screen == RTC_CHECK_STATUS:
            handle_rtc_check_status_input()
        time.sleep(0.2)  # Debounce delay

    if BUTTON_PINS["SET"].value == 0:
        current_screen = MAIN_MENU
        time.sleep(0.2)  # Debounce delay
        
def draw_rtc_set_time(datetime_values, cursor_position):
    oled.fill(0)
    oled.text("Set RTC Time", 10, 10, 1)
    
    # Display the date
    date_text = f"{datetime_values[0]:04d}-{datetime_values[1]:02d}-{datetime_values[2]:02d}"
    oled.text(date_text, 10, 30, 1)
    
    # Display the time
    time_text = f"{datetime_values[3]:02d}:{datetime_values[4]:02d}:{datetime_values[5]:02d}"
    oled.text(time_text, 10, 40, 1)
    
    # Display the cursor
    cursor_x = 10
    if cursor_position < 4:
        cursor_x += cursor_position * 7
    elif cursor_position < 6:
        cursor_x += 28 + (cursor_position - 4) * 6
    elif cursor_position < 8:
        cursor_x += 40 + (cursor_position - 6) * 6
    elif cursor_position < 10:
        cursor_x += 58 + (cursor_position - 8) * 6
    elif cursor_position < 12:
        cursor_x += 70 + (cursor_position - 10) * 6
    else:
        cursor_x += 82 + (cursor_position - 12) * 6
    
    if cursor_position < 8:
        cursor_y = 38
    else:
        cursor_y = 48
    
    oled.text("^", cursor_x, cursor_y - 8, 1)
    
    oled.show()

def handle_rtc_set_time_input():
    global current_screen

    # Initialize variables for user input
    datetime_values = list(rtc.datetime)[:6]
    datetime_limits = [9999, 12, 31, 23, 59, 59]
    cursor_position = 0

    while True:
        draw_rtc_set_time(datetime_values, cursor_position)

        if not BUTTON_PINS["UP"].value:
            # Increment the selected value
            current_value = datetime_values[cursor_position // 2]
            current_digit = cursor_position % 2
            max_value = datetime_limits[cursor_position // 2]
            
            current_value += 10 ** (1 - current_digit)
            if current_value > max_value:
                current_value = current_value % 10
            
            datetime_values[cursor_position // 2] = current_value
            time.sleep(0.2)  # Debounce delay
        elif not BUTTON_PINS["DOWN"].value:
            # Decrement the selected value
            current_value = datetime_values[cursor_position // 2]
            current_digit = cursor_position % 2
            
            current_value -= 10 ** (1 - current_digit)
            if current_value < 0:
                current_value = datetime_limits[cursor_position // 2] - (10 ** (1 - current_digit) - 1)
            
            datetime_values[cursor_position // 2] = current_value
            time.sleep(0.2)  # Debounce delay
        elif not BUTTON_PINS["LEFT"].value:
            # Move the cursor to the previous position
            cursor_position = (cursor_position - 1) % 14
            time.sleep(0.2)  # Debounce delay
        elif not BUTTON_PINS["RIGHT"].value:
            # Move the cursor to the next position
            cursor_position = (cursor_position + 1) % 14
            time.sleep(0.2)  # Debounce delay
        elif not BUTTON_PINS["CLICK"].value:
            # Set the RTC time using the user input
            rtc.datetime = time.struct_time(tuple(datetime_values) + (0, -1, -1))
            print("RTC time set successfully!")
            current_screen = RTC_MENU
            break
        elif BUTTON_PINS["SET"].value == 0:
            # Go back to the RTC menu
            current_screen = RTC_MENU
            break

        time.sleep(0.1)  # Adjust as needed

        
        
def draw_rtc_check_time():
    oled.fill(0)
    oled.text("Current RTC Time", 10, 10, 1)
    current_time = rtc.datetime
    oled.text(f"{current_time.tm_year}-{current_time.tm_mon:02d}-{current_time.tm_mday:02d}", 10, 30, 1)
    oled.text(f"{current_time.tm_hour:02d}:{current_time.tm_min:02d}:{current_time.tm_sec:02d}", 10, 40, 1)
    oled.show()

def handle_rtc_check_time_input():
    global current_screen

    # No action needed, just display the current time
    time.sleep(2)  # Pause for 2 seconds to display the time
    current_screen = RTC_MENU

def draw_rtc_check_status():
    oled.fill(0)
    oled.text("RTC Status", 10, 10, 1)
    temp_c = rtc.temperature
    temp_f = temp_c * 9/5 + 32
    oled.text(f"Temp: {temp_c:.2f}C / {temp_f:.2f}F", 10, 30, 1)
    oled.show()
    
def handle_rtc_check_status_input():
    global current_screen

    # No action needed, just display the status
    time.sleep(2)  # Pause for 2 seconds to display the status
    current_screen = RTC_MENU
    
    
################Encryption###############################
import os
from encryption import derive_key, encrypt_password, decrypt_password

SALT_FILE = "salt.bin"

def save_salt(salt):
    with open(SALT_FILE, "wb") as file:
        file.write(salt)
    os.chmod(SALT_FILE, 0o600)  # Adjust as needed for your target environment

def load_salt():
    try:
        with open(SALT_FILE, "rb") as file:
            salt = file.read()
        if len(salt) != 16:
            raise ValueError("Invalid salt length")
        return salt
    except (FileNotFoundError, ValueError):
        new_salt = os.urandom(16)
        save_salt(new_salt)
        return new_salt

salt = load_salt()
iterations = 10  # You can now use a much higher iteration count
unlock_pattern = ["up", "down", "up", "down", "up"]
key = None  # Initialize key as None


def get_key():
    global key
    if key is None:
        key = derive_key(unlock_pattern, salt, iterations)
    return key


# Add this constant near the top of your file
ENCRYPTED_PASSWORDS_FILE = "encrypted_passwords.csv"

def create_empty_encrypted_file():
    try:
        # Try to open the file in read mode to check if it exists
        with open(ENCRYPTED_PASSWORDS_FILE, "r"):
            pass
    except OSError:
        # If the file doesn't exist, create an empty file
        with open(ENCRYPTED_PASSWORDS_FILE, "w") as file:
            pass
        print("Created empty encrypted passwords file.")

# Modify the encrypt_file function
def encrypt_file():
    passwords_data = load_passwords()
    if not passwords_data:
        print("No passwords to encrypt.")
        return

    encrypted_passwords = []
    for entry in passwords_data:
        if len(entry) == 3:
            encrypted_password = encrypt_password(get_key(), entry[2])
            encrypted_passwords.append([entry[0], entry[1], encrypted_password])
        else:
            encrypted_passwords.append(entry)
    save_encrypted_passwords(encrypted_passwords)
    print("File encrypted successfully!")

# Modify the decrypt_file function
def decrypt_file():
    encrypted_passwords = load_encrypted_passwords()
    decrypted_passwords = []
    for entry in encrypted_passwords:
        if len(entry) == 3:
            decrypted_password = decrypt_password(get_key(), entry[2])
            if decrypted_password:
                decrypted_passwords.append([entry[0], entry[1], decrypted_password])
            else:
                print(f"Failed to decrypt password for {entry[0]}")
        else:
            decrypted_passwords.append(entry)
    save_passwords(decrypted_passwords)
    print("File decrypted successfully!")


def save_encrypted_passwords(passwords_data):
    with open(ENCRYPTED_PASSWORDS_FILE, "w") as file:
        for entry in passwords_data:
            file.write(','.join(entry) + '\n')

def load_encrypted_passwords():
    try:
        with open(ENCRYPTED_PASSWORDS_FILE, "r") as file:
            return [line.strip().split(',') for line in file]
    except Exception as e:
        print("Error loading encrypted passwords:", e)
        return []

# Modify the load_and_decrypt_passwords function

def load_and_decrypt_passwords():
    global passwords_data
    encrypted_passwords = load_encrypted_passwords()
    if not encrypted_passwords:
        return []

    decrypted_passwords = []
    for entry in encrypted_passwords:
        if len(entry) == 3:
            decrypted_password = decrypt_password(get_key(), entry[2])
            if decrypted_password:
                decrypted_passwords.append([entry[0], entry[1], decrypted_password])
            else:
                print(f"Failed to decrypt password for {entry[0]}")
        else:
            decrypted_passwords.append(entry)
    
    passwords_data = decrypted_passwords
    return decrypted_passwords

def draw_test_encryption(stage, data=None, error_message=None):
    oled.fill(0)
    oled.text("Test Encryption", 10, 0, 1)
    
    if stage == "start":
        oled.text("Press UP to start", 10, 20, 1)
        oled.text("Press SET to exit", 10, 30, 1)
    elif stage == "encrypting":
        oled.text("Encrypting...", 10, 20, 1)
    elif stage == "encrypted":
        oled.text("Encrypted:", 10, 20, 1)
        if data:
            for i, entry in enumerate(data[:2]):  # Show first 2 entries
                oled.text(f"{entry[0][:8]}...", 10, 30 + i * 10, 1)
        oled.text("Press DOWN to decrypt", 10, 50, 1)
    elif stage == "decrypting":
        oled.text("Decrypting...", 10, 20, 1)
    elif stage == "decrypted":
        oled.text("Decrypted:", 10, 20, 1)
        if data:
            for i, entry in enumerate(data[:2]):  # Show first 2 entries
                oled.text(f"{entry[0][:8]}: {entry[2][:8]}...", 10, 30 + i * 10, 1)
        oled.text("Press SET to finish", 10, 50, 1)
    elif stage == "error":
        oled.text("Error:", 10, 20, 1)
        if error_message:
            oled.text(error_message[:16], 10, 30, 1)
            if len(error_message) > 16:
                oled.text(error_message[16:32], 10, 40, 1)
        oled.text("Press SET to exit", 10, 50, 1)
    
    oled.show()

def handle_test_encryption():
    global current_screen
    stage = "start"
    
    while True:
        draw_test_encryption(stage)
        
        if stage == "start":
            if not BUTTON_PINS["UP"].value:
                stage = "encrypting"
                time.sleep(0.2)
            elif BUTTON_PINS["SET"].value == 0:
                current_screen = MAIN_MENU
                return
        
        elif stage == "encrypting":
            # Load sample data
            sample_data = [
                ["Website1", "Username1", "Password1"],
                ["Website2", "Username2", "!@#$54Password"],
                ["Website3", "Username3", "Password3"]
            ]
            save_passwords(sample_data)
            
            # Encrypt the file
            encrypt_file()
            encrypted_data = load_encrypted_passwords()
            stage = "encrypted"
            draw_test_encryption(stage, encrypted_data)
        
        elif stage == "encrypted":
            if not BUTTON_PINS["DOWN"].value:
                stage = "decrypting"
                time.sleep(0.2)
        
        elif stage == "decrypting":
            # Decrypt the file
            decrypt_file()
            decrypted_data = load_passwords()
            stage = "decrypted"
            draw_test_encryption(stage, decrypted_data)
        
        elif stage == "decrypted":
            if BUTTON_PINS["SET"].value == 0:
                current_screen = MAIN_MENU
                return
        
        time.sleep(0.1)


# Main loop
create_empty_encrypted_file()  # Create empty file on first boot

draw_loading_screen()


while True:
    if current_screen == LOCK_SCREEN:
        draw_lock_screen()
        last_minute = rtc.datetime.tm_min
        while current_screen == LOCK_SCREEN:
            handle_lock_screen_input()
            if rtc.datetime.tm_min != last_minute:
                update_lock_screen_time()
                last_minute = rtc.datetime.tm_min
            time.sleep(0.1)
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
    elif current_screen == RTC_MENU:
        draw_rtc_menu()
        handle_rtc_menu_input()
    elif current_screen == RTC_SET_TIME:
        datetime_values = list(rtc.datetime)[:6]
        cursor_position = 0
        draw_rtc_set_time(datetime_values, cursor_position)
        handle_rtc_set_time_input()
    elif current_screen == RTC_CHECK_TIME:
        draw_rtc_check_time()
        handle_rtc_check_time_input()
    elif current_screen == RTC_CHECK_STATUS:
        draw_rtc_check_status()
        handle_rtc_check_status_input()
    elif current_screen == ENCRYPTION_MENU:
        draw_encryption_menu()
        handle_encryption_menu_input()
    elif current_screen == TEST_ENCRYPTION:
        handle_test_encryption()

    time.sleep(0.01)  # Adjust as needed
