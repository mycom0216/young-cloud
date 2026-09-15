# server/security.py

import re
import secrets
import string
import hashlib  # hashlib 추가 (bcrypt 대신 사용)

from config import PASSWORD_MIN_LEN, PASSWORD_MAX_LEN, EMAIL_CODE_LENGTH


def hash_password(plain_password: str) -> str:
    """평문 비밀번호를 SHA-256 단방향 해시 문자열(64자리 Hex)로 변환"""
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """입력받은 평문을 SHA-256 변환하여 DB의 stored_hash 값과 비교"""
    if not stored_hash:
        return False
    
    # constant-time 비교 함수(compare_digest)를 사용하여 타이밍 공격(Timing Attack) 방지
    hashed_input = hash_password(plain_password)
    return hashlib.compare_digest(hashed_input.lower(), stored_hash.lower())


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