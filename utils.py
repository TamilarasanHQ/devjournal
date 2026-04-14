import hashlib
import secrets

def hash_password(password: str) -> str:
    # Add a random salt
    salt = secrets.token_hex(16)
    # Hash with sha256 (no length limit)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt, stored_hash = hashed_password.split('$')
    hash_obj = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
    return hash_obj.hex() == stored_hash