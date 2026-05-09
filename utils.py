from datetime import datetime, timedelta, timezone
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

def next_review_interval(rating: int, review_count: int) -> datetime:
    if rating == 5:
        factor = 2.5
    elif rating == 4:
        factor = 2.0
    elif rating == 3:
        factor = 1.5
    elif rating == 2:
        factor = 1.0
    elif rating == 1:
        factor = 0.5
    interval_days = 1*(factor**review_count)
    next_review = datetime.now(timezone.utc) + timedelta(days=interval_days)
    return next_review
