# autotype.py

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

class AutoType:
    def __init__(self):
        self.keyboard = None
        self.keyboard_layout = None
        self.usb_hid_available = False
        self.initialize_usb_hid()

    def initialize_usb_hid(self):
        try:
            self.keyboard = Keyboard(usb_hid.devices)
            self.keyboard_layout = KeyboardLayoutUS(self.keyboard)
            self.usb_hid_available = True
            print("USB HID initialized successfully.")
        except OSError as e:
            print("USB HID initialization failed:", str(e))
            self.usb_hid_available = False

    def type_text(self, text):
        if self.usb_hid_available:
            self.keyboard_layout.write(text)
            print(f"Typed: {text}")
        else:
            print("USB HID not available. Text not typed.")