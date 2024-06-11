import digitalio

class InputHandler:
    def __init__(self, BUTTON_PINS, PATTERN_LENGTH, current_screen):
        self.BUTTON_PINS = BUTTON_PINS
        self.PATTERN_LENGTH = PATTERN_LENGTH
        self.current_screen = current_screen
        self.user_input_index = 0
        self.user_input = [False] * self.PATTERN_LENGTH
        self.pattern = [True, False, True, False, True]  # Example pattern "UDUDU" (True, False, True, False, True)
        self.character_sets = [
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "0123456789",
            "!@#$%^&*()-=_+"
        ]
        self.current_set = 0
        self.character_position = 0

    def record_user_input(self, value):
        self.user_input[self.user_input_index] = value
        self.user_input_index += 1

    def reset_user_input(self):
        self.user_input_index = 0
        for i in range(self.PATTERN_LENGTH):
            self.user_input[i] = False

    def check_pattern(self):
        for i in range(self.PATTERN_LENGTH):
            if self.user_input[i] != self.pattern[i]:
                print(f"Pattern mismatch at index {i}: expected {self.pattern[i]}, got {self.user_input[i]}")
                return False
        print("Pattern matched!")
        return True
            
    def go_to_main_menu():
        self.current_screen = MAIN_MENU

    def cycle_next_character(self):
        self.character_position = (self.character_position + 1) % len(self.character_sets[self.current_set])

    def cycle_previous_character(self):
        self.character_position = (self.character_position - 1) % len(self.character_sets[self.current_set])

    def switch_to_next_set(self):
        self.current_set = (self.current_set + 1) % len(self.character_sets)
        self.character_position = min(self.character_position, len(self.character_sets[self.current_set]) - 1)

    def switch_to_previous_set(self):
        self.current_set = (self.current_set - 1) % len(self.character_sets)
        self.character_position = min(self.character_position, len(self.character_sets[self.current_set]) - 1)

    def reset_character_position(self):
        self.character_position = 0
        
    def handle_lock_screen_input(self):
        if not self.BUTTON_PINS["UP"].value:
            self.record_user_input(True)
        elif not self.BUTTON_PINS["DOWN"].value:
            self.record_user_input(False)

        if self.user_input_index == self.PATTERN_LENGTH:
            if self.check_pattern():
                self.reset_button_press_count = 0  # Reset the counter when the correct pattern is entered
                self.go_to_main_menu()
            else:
                self.reset_user_input()
                    
    def confirm_character(self):
        """
        Confirm the current character entry.
        """
        debounce_time = 5  # Adjust as needed (time in milliseconds)
        current_state = self.BUTTON_PINS["CLICK"].value()
        time.sleep_ms(debounce_time)
        return current_state == self.BUTTON_PINS["CLICK"].value()

    def debounce_button(self, pin):
        """
        Debounce the button input to prevent double presses.
        """
        debounce_time = 5  # Adjust as needed (time in milliseconds)
        current_state = pin.value()
        time.sleep_ms(debounce_time)
        return current_state == pin.value()