import adafruit_hashlib as hashlib
import aesio
import binascii

# Function to generate key from unlock pattern
def generate_key(unlock_pattern):
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
    hashed_pattern = hashlib.sha256(pattern_bytes).digest()
    key = hashed_pattern[:16]  # Truncate the hashed pattern to 16 bytes (AES-128 key size)
    return key

# Initialize AES encryption/decryption with the key and ECB mode
def initialize_cipher(key):
    return aesio.AES(key, aesio.MODE_ECB)

# Function to pad data to a multiple of 16 bytes
def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + bytes([padding_length] * padding_length)

# Function to encrypt password
def encrypt_password(cipher, password):
    password_bytes = pad(password.encode())[:16]  # Ensure password is exactly 16 bytes long
    encrypted_password = bytearray(16)
    cipher.encrypt_into(password_bytes, encrypted_password)
    return binascii.hexlify(encrypted_password).decode()

# Function to decrypt password
def decrypt_password(cipher, encrypted_password):
    encrypted_password_bytes = binascii.unhexlify(encrypted_password)
    decrypted_password = bytearray(16)
    cipher.decrypt_into(encrypted_password_bytes, decrypted_password)
    # Remove padding
    padding_length = decrypted_password[-1]
    return decrypted_password[:-padding_length].decode()