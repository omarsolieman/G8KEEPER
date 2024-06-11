import adafruit_hashlib as hashlib
import aesio
import binascii
import os

# HMAC-SHA256 function
def hmac_sha256(key, message):
    block_size = 64
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()
    if len(key) < block_size:
        key += b'\x00' * (block_size - len(key))
    inner_key = bytes(x ^ 0x36 for x in key)
    outer_key = bytes(x ^ 0x5C for x in key)
    inner_message = inner_key + message
    outer_message = outer_key + hashlib.sha256(inner_message).digest()
    return hashlib.sha256(outer_message).digest()

# PBKDF2-HMAC-SHA256 function
def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
    if not isinstance(hash_name, str):
        raise TypeError("hash_name must be a string")
    if not isinstance(password, (bytes, bytearray)):
        password = bytes(password, 'utf-8')
    if not isinstance(salt, (bytes, bytearray)):
        salt = bytes(salt, 'utf-8')
    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("iterations must be a positive integer")
    if dklen is None:
        dklen = 32
    if dklen < 1:
        raise ValueError("dklen must be a positive integer")

    hash_size = 32
    blocks_needed = (dklen + hash_size - 1) // hash_size
    dk = bytearray(dklen)

    for block_index in range(1, blocks_needed + 1):
        block = hmac_sha256(password, salt + bytes([block_index]))
        u = block
        out = u
        for _ in range(1, iterations):
            u = hmac_sha256(password, u)
            out = bytes(x ^ y for x, y in zip(out, u))
        start = (block_index - 1) * hash_size
        end = start + hash_size
        dk[start:end] = out[:dklen - start]

    return bytes(dk)

# Derive key from unlock pattern
def derive_key(unlock_pattern, salt, iterations):
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
        elif direction == "click":
            pattern_bytes.append(4)
    key = pbkdf2_hmac('sha256', pattern_bytes, salt, iterations)
    return key[:16]  # AES-128 key size

# Initialize AES cipher
def initialize_cipher(key, iv):
    return aesio.AES(key, aesio.MODE_CBC, iv)

# Pad data to a multiple of 16 bytes
def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + bytes([padding_length] * padding_length)

# Unpad data
def unpad(data):
    padding_length = data[-1]
    if padding_length < 1 or padding_length > 16:
        raise ValueError(f"Invalid padding length: {padding_length}")
    if data[-padding_length:] != bytes([padding_length] * padding_length):
        raise ValueError("Invalid padding bytes")
    return data[:-padding_length]

# Encrypt password
# Encrypt password
def encrypt_password(key, password, iv):
    cipher = initialize_cipher(key, iv)  # Initialize the cipher with the provided key and IV
    password_bytes = pad(password.encode())
    encrypted_password = bytearray()
    for i in range(0, len(password_bytes), 16):
        block = password_bytes[i:i+16]
        encrypted_block = bytearray(16)
        cipher.encrypt_into(block, encrypted_block)
        encrypted_password.extend(encrypted_block)
    return binascii.hexlify(encrypted_password).decode()

# Decrypt password
def decrypt_password(key, encrypted_password, iv):
    cipher = initialize_cipher(key, iv)
    encrypted_password_bytes = binascii.unhexlify(encrypted_password)
    print(f"Encrypted password bytes: {encrypted_password_bytes}")  # Debugging output
    decrypted_password = bytearray()
    for i in range(0, len(encrypted_password_bytes), 16):
        block = encrypted_password_bytes[i:i+16]
        decrypted_block = bytearray(16)
        cipher.decrypt_into(block, decrypted_block)
        decrypted_password.extend(decrypted_block)
    print(f"Decrypted password bytes before unpadding: {decrypted_password}")  # Debugging output
    try:
        decrypted_password = unpad(decrypted_password).decode()
    except Exception as e:
        print(f"Error during unpadding: {e}")
        print(f"Decrypted password bytes: {decrypted_password}")
        raise
    return decrypted_password

# Example usage
unlock_pattern = ["up", "down", "up", "down", "up"]
salt = b'random_salt'
iterations = 10
key = derive_key(unlock_pattern, salt, iterations)
iv = bytearray(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')
password = '!@#$OmarSolieman54'
encrypted_password = encrypt_password(key, password, iv)
print(f"Encrypted password: {encrypted_password}")
decrypted_password = decrypt_password(key, encrypted_password, iv)
print(f"Decrypted password: {decrypted_password}")
