import adafruit_hashlib as hashlib
import aesio
import binascii
import storage

# Define the unlock pattern
unlock_pattern = ["up", "down", "up", "down", "up"]

# Convert the unlock pattern to bytes
pattern_bytes = bytearray()
for direction in unlock_pattern:
    if direction == "up":
        pattern_bytes.append(0)
    elif direction == "down":
        pattern_bytes.append(1)
    elif direction == "left":
        pattern_bytes.append(2)
    elif direction == "right":
        pattern_bytes.append(3)

# Use SHA-256 to hash the pattern bytes
hashed_pattern = hashlib.sha256(pattern_bytes).digest()

# Truncate the hashed pattern to 16 bytes (AES-128)
key = hashed_pattern[:16]

# Initialize AES encryption/decryption with the key and ECB mode
cipher = aesio.AES(key, aesio.MODE_ECB)

# Function to pad data to a multiple of 16 bytes
def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + bytes([padding_length] * padding_length)

def encrypt_password(password):
    # Ensure password is exactly 16 bytes long
    password_bytes = pad(password.encode())[:16]
    encrypted_password = bytearray(16)
    # Encrypt the password
    cipher.encrypt_into(password_bytes, encrypted_password)
    return binascii.hexlify(encrypted_password).decode()

def encrypt_passwords_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    
    encrypted_passwords = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) == 3:
            website, username, password = parts
            encrypted_password = encrypt_password(password)
            encrypted_passwords.append(f"{website},{username},{encrypted_password}")
        else:
            encrypted_passwords.append(line.strip())
    
    with open("encrypted_passwords.csv", "w") as encrypted_file:
        encrypted_file.write("\n".join(encrypted_passwords))
    
    # Set the file system to read-only mode for the computer
    storage.remount("/", readonly=True)

# Usage example
passwords_file = "passwords.csv"
encrypt_passwords_file(passwords_file)
print("Encrypted passwords saved to 'encrypted_passwords.csv'")
