import hashlib
import hmac
import secrets

try:
    import bcrypt
except ImportError:
    bcrypt = None


def hash_password(password: str) -> str:
    # Add a random salt and hash with PBKDF2-SHA256
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if bcrypt is not None and hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    try:
        salt, stored_hash = hashed_password.split('$', 1)
    except ValueError:
        return False

    hash_obj = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
    return hmac.compare_digest(hash_obj.hex(), stored_hash)