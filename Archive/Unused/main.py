import board
import busio
import digitalio
from adafruit_ssd1306 import SSD1306_I2C
import time
import random
from screen import Screen
from input_handler import InputHandler

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

BUTTON_PINS = {
    "UP": digitalio.DigitalInOut(board.GP2),
    "DOWN": digitalio.DigitalInOut(board.GP3),
    "LEFT": digitalio.DigitalInOut(board.GP4),
    "RIGHT": digitalio.DigitalInOut(board.GP5),
    "CLICK": digitalio.DigitalInOut(board.GP6),
    "SET": digitalio.DigitalInOut(board.GP7),
    "RESET": digitalio.DigitalInOut(board.GP8),
}


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

for pin in BUTTON_PINS.values():
    pin.switch_to_input(pull=digitalio.Pull.UP)

i2c = busio.I2C(sda=board.GP20, scl=board.GP21)
oled = SSD1306_I2C(128, 64, i2c)

screen = Screen(oled)
input_handler = InputHandler(BUTTON_PINS, PATTERN_LENGTH, current_screen)



# Main loop
while True:
    if current_screen == LOCK_SCREEN:
        screen.draw_lock_screen(input_handler.user_input_index)
        input_handler.handle_lock_screen_input()
    elif current_screen == MAIN_MENU:
        screen.draw_main_menu()
        input_handler.handle_main_menu_input()
    elif current_screen == VIEW_PASSWORDS:
        screen.draw_view_passwords()
        input_handler.handle_view_passwords_input()
    elif current_screen == ADD_PASSWORD:
        screen.draw_add_password()
        input_handler.handle_add_password_input()
    elif current_screen == GENERATE_PASSWORD:
        screen.draw_generate_password()
        input_handler.handle_generate_password_input()

    time.sleep(0.1)  # Adjust as needed
