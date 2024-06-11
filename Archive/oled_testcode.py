import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
import digitalio
import adafruit_framebuf as framebuf
from config import OLED_WIDTH, OLED_HEIGHT, OLED_ADDRESS, OLED_SDA_PIN, OLED_SCL_PIN, BUTTON_PINS

# Constants
NUM_ITEMS = 8
MAX_ITEM_LENGTH = 20

# OLED display setup
i2c = busio.I2C(getattr(board, OLED_SCL_PIN), getattr(board, OLED_SDA_PIN))
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDRESS)

# Button setup
buttons = {}
for button_name, pin_name in BUTTON_PINS.items():
    pin = digitalio.DigitalInOut(getattr(board, pin_name))
    pin.switch_to_input(pull=digitalio.Pull.UP)
    buttons[button_name] = pin

# Menu items
menu_items = [
    "3D Cube",
    "Battery",
    "Dashboard",
    "Fireworks",
    "GPS Speed",
    "Big Knob",
    "Park Sensor",
    "Turbo Gauge"
]

# Variables
button_up_clicked = False
button_select_clicked = False
button_down_clicked = False
item_selected = 0
current_screen = 0
demo_mode = False
demo_mode_state = 0
demo_mode_delay = 0

# Icon bitmaps
icon_bitmaps = [
    bytearray([
    0x00, 0x00, 0x01, 0x80, 0x07, 0x60, 0x19, 0x18, 0x61, 0x06, 0x51, 0x0a, 0x45, 0xa2, 0x41, 0x02, 
    0x45, 0x22, 0x41, 0x02, 0x45, 0xa2, 0x51, 0x0a, 0x61, 0x06, 0x19, 0x18, 0x07, 0x60, 0x01, 0x80
    ]),  # 3D Cube
    bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, 0xf8, 0x40, 0x04, 0x5b, 0x66, 0x5b, 0x66, 
  0x5b, 0x66, 0x40, 0x04, 0x3f, 0xf8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # Battery
    bytearray([0x07, 0xe0, 0x18, 0x18, 0x21, 0x24, 0x50, 0x02, 0x48, 0x0a, 0x84, 0x01, 0x83, 0x81, 0xa2, 0x45, 
  0x82, 0x41, 0x81, 0x81, 0xa0, 0x05, 0x40, 0x02, 0x4b, 0xd2, 0x23, 0xc4, 0x18, 0x18, 0x07, 0xe0]),  # Dashboard
    bytearray([0x00, 0x00, 0x00, 0x08, 0x00, 0x94, 0x10, 0x08, 0x10, 0x00, 0x6c, 0x00, 0x10, 0x10, 0x10, 0x10, 
  0x00, 0x00, 0x00, 0xc6, 0x00, 0x00, 0x00, 0x10, 0x04, 0x10, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x00]),  # Fireworks
    bytearray([0x00, 0x00, 0x03, 0xf0, 0x00, 0x08, 0x01, 0xe4, 0x00, 0x12, 0x00, 0xca, 0x06, 0x2a, 0x07, 0x2a, 
  0x07, 0x8a, 0x07, 0xc2, 0x07, 0xc0, 0x0a, 0x00, 0x1f, 0x00, 0x20, 0x80, 0x7f, 0xc0, 0x00, 0x00]),  # GPS Speed
    bytearray([0x00, 0x00, 0x1f, 0xf0, 0x13, 0x50, 0x1b, 0xb0, 0x11, 0x50, 0x1f, 0xf0, 0x03, 0x80, 0x01, 0x00, 
  0x00, 0x00, 0x09, 0x20, 0x49, 0x24, 0x20, 0x08, 0x00, 0x01, 0x80, 0x02, 0x00, 0x00, 0x00, 0x00]),  # Big Knob
    bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfc, 0x00, 0x22, 0x00, 0x25, 0x00, 0xf9, 0x00, 0x00, 0x81, 
  0x0c, 0x85, 0x12, 0x95, 0xd2, 0x95, 0x0c, 0x05, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # Park Sensor
    bytearray([0x00, 0x0e, 0x07, 0xf1, 0x18, 0x01, 0x20, 0x01, 0x40, 0x01, 0x43, 0xf1, 0x84, 0x4e, 0x8a, 0xa0, 
  0x89, 0x22, 0x8a, 0xa2, 0x84, 0x42, 0x43, 0x84, 0x40, 0x04, 0x20, 0x08, 0x18, 0x30, 0x07, 0xc0]),  # Turbo Gauge
]

def create_framebuffer(bitmap):
    return framebuf.FrameBuffer(bitmap, 16, 16, framebuf.GS4_HMSB)

# Define blit method within SSD1306_I2C class
def blit(self, source, source_x, source_y, width, height, dest_x, dest_y):
    """
    Blit (transfer) pixel data from a source buffer to this buffer.

    :param source: The source framebuffer from which to copy pixel data.
    :param source_x: The x-coordinate in the source buffer to start copying from.
    :param source_y: The y-coordinate in the source buffer to start copying from.
    :param width: The width of the region to copy, in pixels.
    :param height: The height of the region to copy, in pixels.
    :param dest_x: The x-coordinate in this buffer to copy data to.
    :param dest_y: The y-coordinate in this buffer to copy data to.
    """
    for y in range(height):
        for x in range(width):
            pixel = source.pixel(source_x + x, source_y + y)
            self.pixel(dest_x + x, dest_y + y, pixel)


# Add blit method to SSD1306_I2C class
SSD1306_I2C.blit = blit


def draw_menu_screen():
    # Selected item background
    oled.rect(0, 22, 128, 21, 1)

    # Draw previous item as icon + label
    icon_buffer = framebuf.FrameBuffer(icon_bitmaps[item_sel_previous], 16, 16, 0)
    oled.blit(icon_buffer, 0, 0, 16, 16, 4, 2)
    oled.text(menu_items[item_sel_previous], 25, 15, 1)

    # Draw selected item as icon + label in bold font
    icon_buffer = framebuf.FrameBuffer(icon_bitmaps[item_selected], 16, 16, 0)
    oled.blit(icon_buffer, 0, 0, 16, 16, 4, 24)
    oled.text(menu_items[item_selected], 25, 15+20+2, 1)

    # Draw next item as icon + label
    icon_buffer = framebuf.FrameBuffer(icon_bitmaps[item_sel_next], 16, 16, 0)
    oled.blit(icon_buffer, 0, 0, 16, 16, 4, 46)
    oled.text(menu_items[item_sel_next], 25, 15+20+20+2+2, 1)

    # Draw scrollbar
    oled.vline(128-8, 0, 64, 1)
    oled.fill_rect(125, 64//NUM_ITEMS * item_selected, 3, 64//NUM_ITEMS, 1)

def draw_dummy_screen():
    oled.text("Dummy Screen", 0, 0, 1)
    oled.text(menu_items[item_selected], 0, 20, 1)

while True:
    # Check demo mode
    if not buttons["RESET"].value:
        demo_mode = not demo_mode

    if demo_mode:
        # Demo mode logic
        demo_mode_delay += 1
        if demo_mode_delay > 15:
            demo_mode_delay = 0
            demo_mode_state += 1
            if demo_mode_state >= NUM_ITEMS * 2:
                demo_mode_state = 0

        if demo_mode_state % 2 == 0:
            current_screen = 0
            item_selected = demo_mode_state // 2
        else:
            current_screen = 1
            item_selected = demo_mode_state // 2
    else:
        # Normal mode logic
        if current_screen == 0:
            if not buttons["UP"].value and not button_up_clicked:
                item_selected = (item_selected - 1) % NUM_ITEMS
                button_up_clicked = True
            elif not buttons["DOWN"].value and not button_down_clicked:
                item_selected = (item_selected + 1) % NUM_ITEMS
                button_down_clicked = True

            if buttons["UP"].value and button_up_clicked:
                button_up_clicked = False
            if buttons["DOWN"].value and button_down_clicked:
                button_down_clicked = False

        if not buttons["SET"].value and not button_select_clicked:
            button_select_clicked = True
            current_screen = (current_screen + 1) % 2
        if buttons["SET"].value and button_select_clicked:
            button_select_clicked = False

    # Set correct values for the previous and next items
    item_sel_previous = (item_selected - 1) % NUM_ITEMS
    item_sel_next = (item_selected + 1) % NUM_ITEMS

    # Clear the display
    oled.fill(0)

    # Draw the appropriate screen based on current_screen
    if current_screen == 0:
        draw_menu_screen()
    else:
        draw_dummy_screen()

    # Update the display
    oled.show()
