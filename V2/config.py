# config.py
PATTERN_LENGTH = 5
character_sets = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "!@#$%^&*()-=_+"
]
MAX_PASSWORD_LENGTH = 32
PASSWORDS_FILE = "passwords.csv"

LOCK_SCREEN, MAIN_MENU, VIEW_PASSWORDS, ADD_PASSWORD, GENERATE_PASSWORD, RTC_SETUP = range(6)

unlock_pattern = ["up", "down", "up", "down", "up"]

BUTTON_PINS = {
    "UP": "GP2",
    "DOWN": "GP3",
    "LEFT": "GP4",
    "RIGHT": "GP5",
    "CLICK": "GP6",
    "SET": "GP7",
    "RESET": "GP8",
}

OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDRESS = 0x3C
OLED_SDA_PIN = "GP20"
OLED_SCL_PIN = "GP21"