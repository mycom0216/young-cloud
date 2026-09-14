# server/security.py
# pip install bcrypt

import re
import secrets
import string

import bcrypt

from config import PASSWORD_MIN_LEN, PASSWORD_MAX_LEN, EMAIL_CODE_LENGTH


def hash_password(plain_password: str) -> str:
    hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# 영문 + 숫자 + 특수문자 각 1개 이상, 8~20자
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'\",.<>/?])"
    rf".{{{PASSWORD_MIN_LEN},{PASSWORD_MAX_LEN}}}$"
)


def is_valid_password(plain_password: str) -> bool:
    return bool(_PASSWORD_PATTERN.match(plain_password))


def generate_verification_code() -> str:
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(EMAIL_CODE_LENGTH))
