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
        if not self.sock:
            if not self.connect():
                return {"status": "fail", "message": "서버와 연결할 수 없습니다."}

        payload = {
            "action": action,
            "data": data or {}
        }

        try:
            self.sock.sendall(json.dumps(payload).encode('utf-8'))
            response_data = self.sock.recv(4096)
            return json.loads(response_data.decode('utf-8'))
        except Exception as e:
            print(f"[네트워크 에러] 데이터 송수신 중 오류 발생: {e}")
            return {"status": "error", "message": str(e)}

    def send_email_verification(self, email):
        """서버로 이메일 인증코드 발송 요청"""
        return self.send_request("send_email", {"email": email})

    def send_signup(self, user_info):
        """서버로 회원가입 정보 등록 요청"""
        return self.send_request("signup", user_info)

    def close(self):
        """서버와의 연결을 안전하게 끊는 함수"""
        if self.sock:
            self.sock.close()
            self.sock = None
            
            
# ==========================================
    # 💡 메시지 관련 통신 함수들
    # ==========================================
    def get_sent_messages(self, email):
        """서버로 내가 보낸 메시지 목록 조회를 요청합니다."""
        return self.send_request("message_sent", {"email": email})
    
    
    def get_received_messages(self, email):
        """서버로 내가 받은 메시지 목록 조회를 요청합니다."""
        return self.send_request("message_received", {"email": email})

    def send_message(self, sender_email, receiver_email, content):
        """서버로 다른 사용자에게 메시지 전송을 요청합니다."""
        return self.send_request("message_send", {
            "sender": sender_email,
            "receiver": receiver_email,
            "content": content
        })
        
    def mark_message_read(self, message_id):
        """특정 메시지를 읽음 상태로 변경 요청"""
        data = {"message_id": message_id}
        return self.send_request("mark_message_read", data)
    
    def delete_messages(self, message_ids):
        """서버로 선택한 메시지들의 삭제를 요청합니다."""
        return self.send_request("message_delete", {"message_ids": message_ids})

    def close(self):
        """서버와의 연결을 안전하게 끊는 함수"""
        if self.sock:
            self.sock.close()
            self.sock = None
                        
    def get_user_service(self, email):
        """서버로 사용자의 현재 서비스 등급 정보를 요청합니다."""
        return self.send_request("get_user_service", {"email": email})

    def update_user_service(self, email, grade_name):
        """서버로 사용자의 서비스 등급 변경을 요청합니다."""
        return self.send_request("settings_tier_update", {
            "email": email, 
            "grade_name": grade_name
        })
        
    def update_user_name(self, email, name):
        """서버로 사용자 이름 변경을 요청합니다."""
        return self.send_request("update_user_name", {
            "email": email,
            "name": name
        })

    def update_user_password(self, email, password):
        """서버로 사용자 비밀번호 변경을 요청합니다."""
        return self.send_request("update_user_password", {
            "email": email,
            "password": password
        })            
            
    # ==========================================
    # 💡 [관리자] 사용자 차단 및 제한 관련 통신 함수
    # ==========================================
    def admin_get_users(self):
        """서버로 관리자 권한의 전체 이용자 목록 조회를 요청합니다."""
        return self.send_request("admin_get_users", {})

    def admin_update_ban_status(self, email, is_banned):
        """서버로 특정 사용자의 차단 상태(정지 True / 정상 False) 변경을 요청합니다."""
        return self.send_request("admin_update_ban", {
            "email": email,
            "is_banned": is_banned
        })

    def get_user_storage_info(self, email):
        """서버로 사용자의 클라우드 사용량 및 등급 정보 조회를 요청합니다."""
        return self.send_request("get_user_storage_info", {"email": email})





# ==========================================
# 💡 [호환성 유지 함수] login_window.py 대응
# ==========================================
def send_login_request(email, password):
    """login_window.py에서 임포트하는 함수 에러 방지용 래퍼 함수"""
    client = NetworkClient(host='127.0.0.1', port=8888)
    response = client.send_request("login", {
        "user_id": email,
        "password": password
    })
    client.close()
    return response


