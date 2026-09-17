import socket
import json
import os
import struct  # 💡 데이터 길이를 4바이트 헤더로 패킹/언패킹하기 위해 추가

class NetworkClient:
    """서버와 TCP 연결을 맺고 메시지 및 클라우드 데이터를 송수신하는 공용 통신 클래스"""
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """서버에 TCP 연결을 시도하는 함수"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[네트워크 에러] 서버 연결 실패: {e}")
            return False
        
    def _recv_all(self, sock, n):
        """지정한 n 바이트를 모두 수신할 때까지 반복 수신하는 Helper 함수"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def send_request(self, action, data=None):
        """서버로 작업 요청(Action)과 데이터를 전송하고 응답을 받아오는 함수"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            
            payload = {
                "action": action,
                "data": data or {}
            }
            
            # 1. 요청 데이터 인코딩 및 4바이트 길이 헤더 전송
            json_bytes = json.dumps(payload).encode('utf-8')
            header = struct.pack('>I', len(json_bytes))
            sock.sendall(header + json_bytes)

            # 2. 서버 응답의 4바이트 길이 헤더 수신
            raw_length = self._recv_all(sock, 4)
            if not raw_length:
                sock.close()
                return {"status": "error", "message": "서버 응답 없음"}

            data_length = struct.unpack('>I', raw_length)[0]

            # 3. 데이터 길이만큼 전체 바디 완벽 수신
            body_bytes = self._recv_all(sock, data_length)
            sock.close()

            if not body_bytes:
                return {"status": "error", "message": "데이터 수신 손실"}

            # 4. 완벽히 수신된 데이터만 JSON 파싱
            return json.loads(body_bytes.decode('utf-8'))
        except Exception as e:
            print(f"[네트워크 에러] 데이터 송수신 중 오류 발생: {e}")
            self.close()
            return {"status": "error", "message": str(e)}

    def close(self):
        """서버와의 연결을 안전하게 끊는 함수"""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    # ==========================================
    # 💡 인증 및 계정 관련 통신 함수
    # ==========================================
    def send_email_verification(self, email):
        """서버로 이메일 인증코드 발송 요청"""
        return self.send_request("send_email", {"email": email})

    def send_signup(self, user_info):
        """서버로 회원가입 정보 등록 요청"""
        return self.send_request("signup", user_info)

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
        return self.send_request("mark_message_read", {"message_id": message_id})
    
    def delete_messages(self, message_ids):
        """서버로 선택한 메시지들의 삭제를 요청합니다."""
        return self.send_request("message_delete", {"message_ids": message_ids})

    # ==========================================
    # 💡 [클라우드/파일] 관련 통신 함수
    # ==========================================
    def get_file_list(self, user_id, folder_path="/"):
        """클라우드 내 파일/폴더 목록 조회 요청"""
        return self.send_request("cloud_list_files", {
            "user_id": user_id,
            "folder_path": folder_path
        })

    def get_trash_list(self, user_id):
        """휴지통 목록 조회 요청"""
        return self.send_request("cloud_trash_list", {"user_id": user_id})

    def delete_file(self, file_id, user_id):
        """파일 휴지통으로 이동(임시 삭제) 요청"""
        return self.send_request("cloud_delete_file", {
            "file_id": file_id,
            "user_id": user_id
        })

    def restore_file(self, file_id, user_id):
        """휴지통 파일 복구 요청"""
        return self.send_request("cloud_restore_file", {
            "file_id": file_id,
            "user_id": user_id
        })

    def permanent_delete_file(self, file_id, user_id):
        """파일 영구 삭제 요청"""
        return self.send_request("cloud_permanent_delete", {
            "file_id": file_id,
            "user_id": user_id
        })

    def get_storage_info(self, user_id):
        """사용자의 사용 중인 저장 용량 정보 요청"""
        return self.send_request("cloud_storage_info", {"user_id": user_id})

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

        return self.send_request("cloud_storage_info", {"email": email})


    # ==========================================
    # 💡 [설정] 기본/마무리 메시지 관련 통신 함수
    # ==========================================
    def get_user_messages_config(self, email):
        """서버로 사용자의 기본 메시지 및 마무리 메시지 조회를 요청합니다."""
        return self.send_request("get_user_messages_config", {"email": email})

    def update_user_messages_config(self, email, default_message, outro_message):
        """서버로 사용자의 기본 메시지 및 마무리 메시지 수정을 요청합니다."""
        return self.send_request("update_user_messages_config", {
            "email": email,
            "default_message": default_message,
            "outro_message": outro_message
        })


    # ==========================================
    # 💡 [설정] 블랙리스트 관리 관련 통신 함수
    # ==========================================
    def search_users_for_blacklist(self, owner_email, keyword):
        """서버로 블랙리스트 검색을 위한 사용자 조회 및 차단 여부 확인을 요청합니다."""
        return self.send_request("search_users_for_blacklist", {
            "owner_email": owner_email,
            "keyword": keyword
        })

    def update_blacklist_status(self, owner_email, target_email, is_block):
        """서버로 특정 사용자의 블랙리스트 차단 등록 또는 해제를 요청합니다."""
        return self.send_request("update_blacklist_status", {
            "owner_email": owner_email,
            "target_email": target_email,
            "is_block": is_block
        })    

    def get_blocked_users_list(self, owner_email):
            """서버로 내가 차단한 유저 목록 조회를 요청합니다."""
            return self.send_request("get_blocked_users_list", {"owner_email": owner_email})
        
    # network_client.py에 추가할 통신 함수들

    def get_user_download_path(self, email):
        """서버로 사용자의 파일 받기 저장 경로 조회를 요청합니다."""
        return self.send_request("get_user_download_path", {"email": email})

    def update_user_download_path(self, email, download_path):
        """서버로 사용자의 파일 받기 저장 경로 변경을 요청합니다."""
        return self.send_request("update_user_download_path", {
            "email": email,
            "download_path": download_path
        })    
        

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