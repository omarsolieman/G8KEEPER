from config import PASSWORDS_FILE
from encryption import generate_key, initialize_cipher, encrypt_password, decrypt_password

class PasswordStorage:
    def __init__(self, unlock_pattern):
        self.passwords_file = PASSWORDS_FILE
        self.key = generate_key(unlock_pattern)
        self.cipher = initialize_cipher(self.key)

    def load_passwords(self):
        try:
            with open(self.passwords_file, "r") as file:
                lines = file.readlines()
                passwords = []
                for line in lines:
                    parts = line.strip().split(",")
                    if len(parts) == 3:
                        website, username, encrypted_password = parts
                        decrypted_password = decrypt_password(self.cipher, encrypted_password)
                        passwords.append([website, username, decrypted_password])
                return passwords
        except FileNotFoundError:
            return []

    def save_passwords(self, passwords):
        encrypted_passwords = []
        for website, username, password in passwords:
            encrypted_password = encrypt_password(self.cipher, password)
            encrypted_passwords.append(f"{website},{username},{encrypted_password}")

        with open(self.passwords_file, "w") as file:
            file.write("\n".join(encrypted_passwords))