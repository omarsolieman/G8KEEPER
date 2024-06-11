# oled_display.py

import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from config import OLED_WIDTH, OLED_HEIGHT, OLED_ADDRESS, OLED_SDA_PIN, OLED_SCL_PIN

class OLEDDisplay:
    def __init__(self, i2c):
        self.i2c = i2c
        self.oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, self.i2c, addr=OLED_ADDRESS)
        self.buffer = bytearray(OLED_WIDTH * OLED_HEIGHT // 8)
        self.oled.fill(0)
        self.oled.show()

    def clear(self):
        self.oled.fill(0)

    def display_text(self, text, x, y, color=1):
        self.oled.text(text, x, y, color)

    def display_rectangle(self, x, y, width, height, color=1):
        self.oled.rect(x, y, width, height, color)

    def display_filled_rectangle(self, x, y, width, height, color=1):
        self.oled.fill_rect(x, y, width, height, color)

    def update_display(self):
        self.oled.show()