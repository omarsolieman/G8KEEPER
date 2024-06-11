class UIElement:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self, display):
        pass

class Label(UIElement):
    def __init__(self, text, x, y, font_size=1):
        super().__init__(x, y, len(text) * 6 * font_size, 8 * font_size)
        self.text = text
        self.font_size = font_size
    
    def render(self, display):
        display.display_text(self.text, self.x, self.y, 1)

class Button(UIElement):
    def __init__(self, text, x, y, width, height, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback

    def render(self, display):
        display.display_rectangle(self.x, self.y, self.width, self.height, 1)
        text_x = self.x + (self.width - len(self.text) * 6) // 2
        text_y = self.y + (self.height - 8) // 2
        display.display_text(self.text, text_x, text_y, 1)

class ButtonGrid(UIElement):
    def __init__(self, x, y, button_width, button_height, buttons):
        super().__init__(x, y, button_width * len(buttons[0]), button_height * len(buttons))
        self.button_width = button_width
        self.button_height = button_height
        self.buttons = buttons

    def render(self, display):
        for row in range(len(self.buttons)):
            for col in range(len(self.buttons[row])):
                button = self.buttons[row][col]
                button.x = self.x + col * self.button_width
                button.y = self.y + row * self.button_height
                button.width = self.button_width
                button.height = self.button_height
                button.render(display)



