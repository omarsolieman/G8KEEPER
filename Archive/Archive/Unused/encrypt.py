import aesio
import adafruit_hashlib as hashlib

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

# Function to encrypt a password
def encrypt_password(password):
    # Ensure password is exactly 16 bytes long
    password_bytes = pad(password.encode())[:16]
    encrypted_password = bytearray(16)
    # Encrypt the password
    cipher.encrypt_into(password_bytes, encrypted_password)
    return encrypted_password

# Function to decrypt a password
def decrypt_password(encrypted_password):
    # Create a buffer for the decrypted password
    decrypted_password = bytearray(16)
    # Decrypt the password
    cipher.decrypt_into(encrypted_password, decrypted_password)
    # Decode the decrypted password
    return decrypted_password.decode()

# Example usage
password = "epasswordblabla"
encrypted_password = encrypt_password(password)
print("Encrypted Password:", encrypted_password)
decrypted_password = decrypt_password(encrypted_password)
print("Decrypted Password:", decrypted_password)
