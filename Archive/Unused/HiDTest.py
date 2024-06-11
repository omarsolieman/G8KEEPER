import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS


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

# The keyboard object
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)


def SendStringHID(string):
    keyboard_layout.write(string)
    print(f"Typed: {string}")

# while True:
#     for button, pin in BUTTON_PINS.items():
#         if not pin.value:  # Button is pressed
#             print(f"Button {button} pressed.")
# 
#             # input string
#             string = "Hello this is a test"
# 
#             # Type the random string
#             keyboard_layout.write(string)
# 
#             # Wait for the button to be released
#             while not pin.value:
#                 pass
# 
#             print(f"Typed: {string}")
# 
#     time.sleep(0.01)
    
