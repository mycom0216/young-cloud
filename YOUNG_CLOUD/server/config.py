# server/config.py
# --------------------------------------------------------
# 서버 전역 설정. 실서비스에서는 비밀번호/앱 비밀번호를 환경변수로 분리하세요.
# --------------------------------------------------------

HOST = "0.0.0.0"
PORT = 8080
LISTEN_BACKLOG = 100

MAX_MESSAGE_BYTES = 1024          # 메시지 최대 1024Byte (요구사항)
FILE_CHUNK_SIZE = 64 * 1024       # 파일 송수신 청크 크기 (64KB)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "app_user",
    "password": "CHANGE_ME",
    "database": "messenger_db",
    "charset": "utf8mb4",
    "autocommit": False,
}

# 등급별 저장 용량 (요구사항: 일반 100MB / 비즈니스 200MB / VIP 500MB / VVIP 1GB)
GRADE_QUOTA_BYTES = {
    "NORMAL":   100 * 1024 * 1024,
    "BUSINESS": 200 * 1024 * 1024,
    "VIP":      500 * 1024 * 1024,
    "VVIP":     1024 * 1024 * 1024,
}

STORAGE_ROOT = "./storage"  # 서버 실행 위치(server/) 기준 상대경로

EMAIL_SENDER_ADDRESS = "your_service@gmail.com"
EMAIL_APP_PASSWORD = "CHANGE_ME"      # 구글 "앱 비밀번호" (일반 로그인 비밀번호 아님)
EMAIL_CODE_LENGTH = 6
EMAIL_CODE_EXPIRE_SECONDS = 60 * 5

PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 20
