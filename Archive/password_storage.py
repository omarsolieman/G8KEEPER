# password_storage.py

from config import PASSWORDS_FILE


class PasswordStorage:
    def __init__(self, unlock_pattern):
        self.passwords_file = PASSWORDS_FILE

    def load_passwords(self):
        try:
            with open(self.passwords_file, "r") as file:
                lines = file.readlines()
                passwords = []
                for line in lines:
                    parts = line.strip().split(",")
                    if len(parts) == 4:
                        website, username, password, enc = parts
                        passwords.append([website, username, password])
                print("Passwords loaded successfully.")
                return passwords
        except OSError as e:
            print(f"Error loading passwords: {e}")
            return []

    def save_passwords(self, passwords):
        encrypted_passwords = []
        for website, username, password in passwords:
            encrypted_password = encrypt_password(self.cipher, password)
            encrypted_passwords.append(f"{website},{username},{encrypted_password}")

        try:
            with open(self.passwords_file, "w") as file:
                file.write("\n".join(encrypted_passwords))
            print("Passwords saved successfully.")
        except OSError as e:
            print(f"Error saving passwords: {e}")
