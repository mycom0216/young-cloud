import socket
import threading
from handlers.client_handler import ClientHandler  # 방금 분리한 핸들러 파일 불러오기

# 서버가 실행될 주소(로컬호스트)와 포트 번호 설정
HOST = '0.0.0.0'
PORT = 8888

class Server:
    """전체 네트워크 연결을 대기하고 클라이언트 접속 시 스레드를 생성하는 메인 서버 클래스"""
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        
        # TCP 소켓 서버 객체 생성 (IPv4, TCP 통신 사용)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 서버 재시작 시 포트 중복 에러(Address already in use) 방지
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # [중요] 여러 스레드가 동시에 데이터베이스에 접근할 때 충돌이 나지 않도록 막아주는 잠금(Lock) 객체
        self.db_lock = threading.Lock()

    def start(self):
        """서버를 실행하고 클라이언트의 접속을 무한 대기(Listening)하는 함수"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # 동시에 대기할 수 있는 클라이언트 수 설정
        print(f"[서버 시작] {self.host}:{self.port}에서 클라이언트 접속을 기다리는 중...")

        try:
            while True:
                # 클라이언트가 접속하면 통신용 소켓(client_sock)과 주소(client_addr)를 반환받음
                client_sock, client_addr = self.server_socket.accept()
                print(f"[연결 성공] 클라이언트 접속 감지: {client_addr}")
                
                # 접속한 클라이언트마다 독립적인 일꾼(스레드)을 생성하여 업무 배정 (Spawn)
                thread = ClientHandler(client_sock, client_addr, self.db_lock)
                thread.daemon = True  # 메인 프로그램이 종료되면 스레드도 함께 안전하게 종료되도록 설정
                thread.start()
        except KeyboardInterrupt:
            print("[서버 중지] 사용자에 의해 서버가 강제 종료되었습니다.")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때 서버가 켜지도록 설정
    server = Server()
    server.start()