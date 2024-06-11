import board
import digitalio
from config import BUTTON_PINS

class UserInput:
    def __init__(self):
        self.buttons = {}
        self.button_states = {}
        for button_name, pin_name in BUTTON_PINS.items():
            pin = digitalio.DigitalInOut(getattr(board, pin_name))
            pin.switch_to_input(pull=digitalio.Pull.UP)
            self.buttons[button_name] = pin
            self.button_states[button_name] = False

    def update(self):
        for button_name, pin in self.buttons.items():
            current_state = not pin.value
            if current_state != self.button_states[button_name]:
                self.button_states[button_name] = current_state
                if current_state:
                    self.on_button_pressed(button_name)

    def on_button_pressed(self, button_name):
        pass

class PasswordManagerInput(UserInput):
    def __init__(self, password_manager):
        super().__init__()
        self.password_manager = password_manager

    def on_button_pressed(self, button_name):
        self.password_manager.handle_button_press(button_name)