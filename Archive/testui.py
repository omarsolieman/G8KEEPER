# main.py
import time
import digitalio
import displayio
import busio
import terminalio
import board
from oled_display import OLEDDisplay
from config import BUTTON_PINS, UNLOCK_PATTERN
import adafruit_imageload
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

class PasswordManager:
    def __init__(self, display):
        self.display = display
        self.buttons = self.setup_buttons()
        self.is_locked = True

    def setup_buttons(self):
        buttons = {}
        for name, pin in BUTTON_PINS.items():
            button = digitalio.DigitalInOut(pin)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
            buttons[name] = button
        return buttons

    def check_button_press(self):
        for name, button in self.buttons.items():
            if not button.value:
                return name
        return None

    def lock_screen(self):
        pattern = []
        while self.is_locked:
            self.display.clear()
            self.display.display_text("Enter unlock pattern:", 0, 0)
            self.display.display_text("".join(pattern), 0, 10)
            self.display.update_display()

            button = self.check_button_press()
            if button:
                pattern.append(button)
                print(f"Button pressed: {button}")  # Logging statement
                print(f"Current pattern: {pattern}")  # Logging statement

                if pattern == UNLOCK_PATTERN:
                    self.is_locked = False
                    print("Unlock pattern matched. Device unlocked.")  # Logging statement
                elif len(pattern) >= len(UNLOCK_PATTERN):
                    pattern = []
                    print("Invalid pattern. Resetting.")  # Logging statement

                time.sleep(0.2)
                
    def main_menu(self):
        menu_options = [
            {"name": "View Password", "icon": "view_32.bmp"},
            {"name": "Edit Password", "icon": "edit_32.bmp"},
            {"name": "Generate Password", "icon": "generate_32.bmp"},
            {"name": "Encrypt Password", "icon": "encrypt_32.bmp"},
            {"name": "Lock Device", "icon": "lock_32.bmp"},
        ]
        selected_option = 0

        group = displayio.Group()

        arrow_left = Rect(0, 16, 10, 32, fill=0xFFFFFF)
        arrow_right = Rect(118, 16, 10, 32, fill=0xFFFFFF)
        group.append(arrow_left)
        group.append(arrow_right)

        icon_sprite = displayio.TileGrid(None, pixel_shader=displayio.ColorConverter(), width=1, height=1, tile_width=32, tile_height=32)
        icon_sprite.x = 48
        icon_sprite.y = 8
        group.append(icon_sprite)

        text_label = label.Label(font=terminalio.FONT, text="", color=0xFFFFFF, x=64, y=48, anchor_point=(0.5, 0.0))
        group.append(text_label)

        self.display.show(group)

        # Load the initial bitmap image
        initial_icon_file = menu_options[selected_option]["icon"]
        print(f"Loading initial icon file: {initial_icon_file}")  # Log the initial icon file name

        try:
            initial_icon_bitmap, initial_icon_palette = adafruit_imageload.load(
                initial_icon_file,
                bitmap=displayio.Bitmap,
                palette=displayio.Palette
            )
            icon_sprite.bitmap = initial_icon_bitmap
            icon_sprite.pixel_shader = initial_icon_palette
            text_label.text = menu_options[selected_option]["name"]
        except Exception as e:
            print(f"Error loading initial bitmap: {str(e)}")  # Log the error message

        while not self.is_locked:
            button = self.check_button_press()
            if button == "LEFT":
                selected_option = (selected_option - 1) % len(menu_options)
            elif button == "RIGHT":
                selected_option = (selected_option + 1) % len(menu_options)
            elif button == "CLICK":
                if selected_option == 4:
                    self.is_locked = True
                else:
                    self.display.clear()
                    self.display.display_text("Selected: " + menu_options[selected_option]["name"], 0, 0)
                    self.display.update_display()
                    time.sleep(1)

            # Load the bitmap image for the current selected option
            icon_file = menu_options[selected_option]["icon"]
            print(f"Loading icon file: {icon_file}")  # Log the icon file name

            try:
                icon_bitmap, icon_palette = adafruit_imageload.load(
                    icon_file,
                    bitmap=displayio.Bitmap,
                    palette=displayio.Palette
                )
                icon_sprite.bitmap = icon_bitmap
                icon_sprite.pixel_shader = icon_palette
                text_label.text = menu_options[selected_option]["name"]
            except Exception as e:
                print(f"Error loading bitmap: {str(e)}")  # Log the error message

            time.sleep(0.2)

    def run(self):
        while True:
            if self.is_locked:
                self.lock_screen()
            else:
                self.main_menu()

if __name__ == "__main__":
    i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
    display = OLEDDisplay(i2c)
    password_manager = PasswordManager(display)
    password_manager.run()