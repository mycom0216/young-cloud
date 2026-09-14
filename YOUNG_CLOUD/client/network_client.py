import socket
import json

class NetworkClient:
    """서버와 TCP 연결을 맺고 메시지를 송수신하는 공용 통신 클래스"""
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.sock = None  # 소켓 객체 초기화

    def connect(self):
        """서버에 TCP 연결을 시도하는 함수"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[네트워크 에러] 서버 연결 실패: {e}")
            return False

    def send_request(self, action, data=None):
        """서버로 작업 요청(Action)과 데이터를 전송하고 응답을 받아오는 함수"""
        # 소켓 연결이 안 되어 있다면 연결 먼저 시도
        if not self.sock:
            if not self.connect():
                return {"status": "fail", "message": "서버와 연결할 수 없습니다."}

        # 서버가 알아볼 수 있도록 딕셔너리 형태로 데이터 포맷 구성
        payload = {
            "action": action,
            "data": data or {}
        }

        try:
            # 파이썬 딕셔너리를 JSON 문자열로 변환 후 바이트로 인코딩해서 서버로 전송
            self.sock.sendall(json.dumps(payload).encode('utf-8'))
            
            # 서버로부터 응답 데이터 수신 (최대 4096바이트)
            response_data = self.sock.recv(4096)
            
            # 받은 바이트 데이터를 다시 파이썬 딕셔너리로 변환하여 반환
            return json.loads(response_data.decode('utf-8'))
        except Exception as e:
            print(f"[네트워크 에러] 데이터 송수신 중 오류 발생: {e}")
            return {"status": "error", "message": str(e)}

    def close(self):
        """서버와의 연결을 안전하게 끊는 함수"""
        if self.sock:
            self.sock.close()
            self.sock = None