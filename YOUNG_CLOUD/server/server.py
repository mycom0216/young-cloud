# server/main.py
# --------------------------------------------------------
# 실행: server/ 디렉터리에서 `python main.py`
# (project_root/common 패키지를 import해야 하므로, client_handler.py 안에서
#  이미 project_root를 sys.path에 추가하고 있습니다)
# --------------------------------------------------------

import os
import socket

from config import HOST, PORT, LISTEN_BACKLOG, STORAGE_ROOT
from client_handler import ClientHandler


def main():
    os.makedirs(STORAGE_ROOT, exist_ok=True)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, PORT))
    listener.listen(LISTEN_BACKLOG)

    print(f"서버 시작: {HOST}:{PORT} 에서 대기 중...")

    try:
        while True:
            conn, addr = listener.accept()
            handler = ClientHandler(conn, addr)
            handler.start()
    except KeyboardInterrupt:
        print("\n서버 종료 신호(Ctrl+C) 수신, 서버를 종료합니다.")
    finally:
        listener.close()


if __name__ == "__main__":
    main()