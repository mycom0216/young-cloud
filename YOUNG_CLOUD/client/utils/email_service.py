# server/email_service.py
# pip install yagmail
# 사전 준비: 구글 계정 2단계인증 활성화 -> "앱 비밀번호" 발급 -> config.py에 입력

import threading
import time

import yagmail

from config import EMAIL_SENDER_ADDRESS, EMAIL_APP_PASSWORD, EMAIL_CODE_EXPIRE_SECONDS
from security import generate_verification_code

_pending_codes: dict[str, tuple[str, float]] = {}  # {이메일: (코드, 발급시각)}
_lock = threading.Lock()

_smtp_client = yagmail.SMTP(user=EMAIL_SENDER_ADDRESS, password=EMAIL_APP_PASSWORD)


def send_verification_email(to_email: str) -> None:
    code = generate_verification_code()
    with _lock:
        _pending_codes[to_email] = (code, time.time())

    subject = "[메신저 서비스] 이메일 인증코드"
    body = (
        f"인증코드: {code}\n"
        f"이 코드는 {EMAIL_CODE_EXPIRE_SECONDS // 60}분간 유효합니다.\n"
        f"본인이 요청하지 않았다면 이 메일을 무시하세요."
    )
    _smtp_client.send(to=to_email, subject=subject, contents=body)


def verify_code(email: str, input_code: str) -> bool:
    with _lock:
        record = _pending_codes.get(email)
        if record is None:
            return False
        saved_code, issued_at = record
        if time.time() - issued_at > EMAIL_CODE_EXPIRE_SECONDS:
            del _pending_codes[email]
            return False
        if saved_code != input_code:
            return False
        del _pending_codes[email]
        return True
