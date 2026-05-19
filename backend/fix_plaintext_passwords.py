"""
fix_plaintext_passwords.py
--------------------------
Detects users whose `password_hash` column is not a valid bcrypt hash
(e.g. seeded test data with fake/PHP-style hashes) and re-hashes them
with a temporary password so they can log in.

Usage
-----
    cd backend
    python fix_plaintext_passwords.py

All affected accounts will have their password set to: TestPass1234!
Affected users should then change it via Settings -> Change Password.
"""

import bcrypt
from database import SessionLocal
import models
import auth_utils


def is_valid_bcrypt(value: str) -> bool:
    """Return True only if *value* is a valid bcrypt hash Python's bcrypt can use."""
    if not value:
        return False
    # Python bcrypt only handles $2b$ (and tolerates $2a$); $2y$ is PHP-only.
    # Also reject obviously fake/short hashes.
    stripped = value.strip()
    if not (stripped.startswith("$2b$") or stripped.startswith("$2a$")):
        return False
    if len(stripped) < 59:
        return False
    try:
        bcrypt.checkpw(b"probe", stripped.encode("utf-8"))
        return True
    except ValueError:
        return False
    except Exception:
        # Wrong answer but salt was valid -> hash itself is fine.
        return True


TEMP_PASSWORD = "TestPass1234!"


def main():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        bad_users = [u for u in users if not is_valid_bcrypt(u.password_hash)]

        if not bad_users:
            print("[OK] All password hashes are valid. No action needed.")
            return

        print(f"[WARNING] Found {len(bad_users)} user(s) with invalid hashes.")
        print(f"[INFO]    Re-hashing all of them with temporary password: {TEMP_PASSWORD!r}\n")

        new_hash = auth_utils.hash_password(TEMP_PASSWORD)   # compute once, reuse
        for u in bad_users:
            u.password_hash = new_hash

        db.commit()

        print(f"[DONE] Successfully re-hashed {len(bad_users)} account(s).")
        print(f"       They can now log in with the password: {TEMP_PASSWORD!r}")
        print("       Advise them to change it via Settings -> Change Password.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
