import aesio
import csv
from binascii import unhexlify, hexlify
import os

class PasswordStorage:
    def __init__(self, key, csv_path):
        self.passwords_file = csv_path
        self.aes = aesio.AES(key, aesio.MODE_ECB)

    def load_passwords(self):
        try:
            with open(self.passwords_file, "r") as file:
                csv_reader = csv.reader(file)
                passwords = list(csv_reader)
                return passwords
        except FileNotFoundError:
            return []

    def save_passwords(self, passwords):
        with open(self.passwords_file, "w", newline="") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(passwords)

    def encrypt_password_entry(self, entry):
        website, username, password = entry
        password_bytes = password.encode()
        encrypted_password = bytearray()

        for i in range(0, len(password_bytes), 16):
            block = password_bytes[i:i+16]
            padded_block = bytearray(block)
            padded_block.extend(b'\x00' * (16 - len(block)))
            encrypted_block = bytearray(16)
            self.aes.encrypt_into(padded_block, encrypted_block)
            encrypted_password.extend(encrypted_block)

        encrypted_password_hex = hexlify(encrypted_password).decode()
        encrypted_entry = [website, username, encrypted_password_hex]
        return encrypted_entry

    def decrypt_password_entry(self, encrypted_entry):
        website, username, encrypted_password = encrypted_entry
        encrypted_password_bytes = unhexlify(encrypted_password)
        decrypted_password = bytearray(16)
        self.aes.decrypt_into(encrypted_password_bytes, decrypted_password)
        password = decrypted_password.decode().rstrip('\0')
        decrypted_entry = [website, username, password]
        return decrypted_entry

def main():
    key = b'your_encryption_key_here'  # Replace with your own key

    while True:
        csv_path = input("Enter the path of the CSV file (or 'exit' to quit): ")
        if csv_path.lower() == 'exit':
            break

        if not os.path.isfile(csv_path):
            print("Invalid file path. Please try again.")
            continue

        password_storage = PasswordStorage(key, csv_path)

        while True:
            print("\nPassword Manager")
            print("1. View passwords")
            print("2. Add new password entry")
            print("3. Update password entry")
            print("4. Delete password entry")
            print("5. Change CSV file")
            print("6. Exit")
            choice = input("Enter your choice (1-6): ")

            if choice == "1":
                passwords = password_storage.load_passwords()
                if passwords:
                    print("\nWebsite | Username | Password")
                    for entry in passwords:
                        if len(entry) == 3:
                            website, username, password = entry
                            if password.startswith("b'") and password.endswith("'"):
                                decrypted_entry = password_storage.decrypt_password_entry(entry)
                                website, username, password = decrypted_entry
                            print(f"{website} | {username} | {password}")
                else:
                    print("No passwords found.")
            elif choice == "2":
                website = input("Enter website: ")
                username = input("Enter username: ")
                password = input("Enter password: ")
                encrypt_choice = input("Encrypt password? (y/n): ")

                if encrypt_choice.lower() == "y":
                    encrypted_entry = password_storage.encrypt_password_entry([website, username, password])
                    passwords = password_storage.load_passwords()
                    passwords.append(encrypted_entry)
                    password_storage.save_passwords(passwords)
                else:
                    passwords = password_storage.load_passwords()
                    passwords.append([website, username, password])
                    password_storage.save_passwords(passwords)

                print("Password entry added successfully!")
            elif choice == "3":
                website = input("Enter website to update: ")
                username = input("Enter username to update: ")
                passwords = password_storage.load_passwords()
                updated = False

                for i, entry in enumerate(passwords):
                    if len(entry) == 3:
                        if entry[0] == website and entry[1] == username:
                            new_password = input("Enter new password: ")
                            encrypt_choice = input("Encrypt password? (y/n): ")

                            if encrypt_choice.lower() == "y":
                                encrypted_entry = password_storage.encrypt_password_entry([website, username, new_password])
                                passwords[i] = encrypted_entry
                            else:
                                passwords[i] = [website, username, new_password]

                            password_storage.save_passwords(passwords)
                            print("Password entry updated successfully!")
                            updated = True
                            break

                if not updated:
                    print("Password entry not found.")
            elif choice == "4":
                website = input("Enter website to delete: ")
                username = input("Enter username to delete: ")
                passwords = password_storage.load_passwords()
                updated = False

                for i, entry in enumerate(passwords):
                    if len(entry) == 3:
                        if entry[0] == website and entry[1] == username:
                            del passwords[i]
                            password_storage.save_passwords(passwords)
                            print("Password entry deleted successfully!")
                            updated = True
                            break

                if not updated:
                    print("Password entry not found.")
            elif choice == "5":
                break
            elif choice == "6":
                exit()
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()