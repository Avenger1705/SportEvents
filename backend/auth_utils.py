import os
import random
from datetime import datetime, timedelta

from jose import JWTError, jwt
import bcrypt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SECRET_KEY                  = os.getenv("SECRET_KEY", "CHANGE-ME-use-secrets.token_hex(32)")
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


# ── Passwords ─────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Returns True if *plain* matches the stored bcrypt *hashed* value.
    Returns False (instead of crashing) when the stored value is not a
    valid bcrypt hash (e.g. plaintext password or corrupted row) so the
    caller can respond with 401 rather than 500.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, Exception):
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ── OTP ───────────────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """
    Génère un code OTP de 6 chiffres.
    Format : 3 chiffres (100-999) + miroir (ex: 472 → 472274).
    """
    trio = random.randint(100, 999)
    mirror = str(trio)[::-1]
    return str(trio) + mirror


def otp_expiry() -> datetime:
    """OTP is valid for 10 minutes."""
    return datetime.utcnow() + timedelta(minutes=10)
