import os
import sys
import threading
import time

import yagmail

# 프로젝트 루트(YOUNG_CLOUD) 경로를 sys.path에 추가하여 server 폴더 접근 가능하게 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from server.config import (
    EMAIL_SENDER_ADDRESS,
    EMAIL_APP_PASSWORD,
    EMAIL_CODE_EXPIRE_SECONDS,
)
from server.security import generate_verification_code

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