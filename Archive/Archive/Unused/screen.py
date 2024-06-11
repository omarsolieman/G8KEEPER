from adafruit_ssd1306 import SSD1306_I2C

class Screen:
    def __init__(self, oled):
        self.oled = oled

    def draw_lock_screen(self, user_input_index):
        self.oled.fill(0)
        self.oled.text("Device Locked", 10, 5, 1)  
        self.oled.text("Enter pattern:", 10, 20, 1)
        for i in range(user_input_index):
            self.oled.text("*", 10 + i * 10, 40, 1)
        self.oled.show()

    def draw_main_menu(self, selected_menu_item):
        self.oled.fill(0)
        for i in range(selected_menu_item, min(selected_menu_item + 4, 5)):
            menu_item_text = f" {self.get_menu_text(i)}"
            self.oled.text(menu_item_text, -3, 10 + (i - selected_menu_item) * 20, 1)

        scrollbar_y = 10 + (selected_menu_item * 10)
        self.oled.rect(120, 10, 4, 40, 1)
        self.oled.fill_rect(120, scrollbar_y, 2, 10, 1)
        self.oled.show()

    def draw_view_passwords(self, passwords_data, current_password_index):
        self.oled.fill(0)
        for i in range(current_password_index, min(current_password_index + 1, len(passwords_data))):
            # Center the website text
            x_website = (128 - len(passwords_data[i][0]) * 6) // 2
            self.oled.text(passwords_data[i][0], x_website, 10, 1)

            # Center the username text
            x_username = (128 - len(passwords_data[i][1]) * 6) // 2
            self.oled.text(passwords_data[i][1], x_username, 30, 1)

            # Center the password text
            x_password = (128 - len(passwords_data[i][2]) * 6) // 2
            self.oled.text(passwords_data[i][2], x_password, 50, 1)

        self.oled.show()

    def draw_add_password(self, password_input, current_set, character_position):
        self.oled.fill(0)
        self.oled.text("Enter password:", 5, 10, 1) 
        self.oled.text(self.get_current_character(current_set, character_position) + " " + password_input, 5, 30, 1)
        self.oled.text("Set: {}".format(self.character_sets[current_set]), 5, 50, 1)
        self.oled.show()

    def draw_generate_password(self):
        self.oled.fill(0)
        self.oled.text("Length: 12", 10, 10, 1)
        self.oled.text("Complexity: Medium", 10, 30, 1)
        self.oled.text("Press SET to generate", 10, 50, 1)
        self.oled.show()

    def display_generated_password(self, password):
        self.oled.fill(0)
        self.oled.text("Generated Password:", 5, 10, 1) 
        self.oled.text(password, 5, 30, 1)
        self.oled.show()

    def get_menu_text(self, menu_item):
        switcher = {
            0: "View Passwords",
            1: "Add Password",
            2: "Generate Pass",
            3: "Del Password",
            4: "Lock Device",
        }
        return switcher.get(menu_item, "")

    def get_current_character(self, current_set, character_position):
        current_char_index = (character_position) % len(self.character_sets[current_set])
        return self.character_sets[current_set][current_char_index]
