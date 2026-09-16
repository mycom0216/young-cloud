import socket
import json


class NetworkClient:
    """서버와 TCP 연결을 맺고 요청/응답을 주고받는 공용 통신 클래스."""
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.sock = None
        self.session_token = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[네트워크 에러] 서버 연결 실패: {e}")
            self.sock = None
            return False

    def send_request(self, action, data=None):
        if not self.sock and not self.connect():
            return {"status": "fail", "message": "서버와 연결할 수 없습니다."}
        request_data = dict(data or {})
        # 로그인 후 받은 토큰을 모든 요청에 자동으로 넣습니다.
        if self.session_token and action != "login":
            request_data["_session_token"] = self.session_token
        payload = {"action": action, "data": request_data}
        try:
            self.sock.sendall(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            response_data = self.sock.recv(65536)
            if not response_data:
                return {"status": "error", "message": "서버 응답이 없습니다."}
            response = json.loads(response_data.decode("utf-8"))
            if response.get("session_token"):
                self.session_token = response["session_token"]
            return response
        except Exception as e:
            print(f"[네트워크 에러] 데이터 송수신 중 오류 발생: {e}")
            return {"status": "error", "message": str(e)}

    def get_received_messages(self, email):
        return self.send_request("message_received", {"email": email})

    def send_message(self, sender, receiver, title, content):
        return self.send_request("message_send", {
            "sender": sender, "receiver": receiver,
            "title": title, "content": content})

    def mark_message_read(self, email, message_id):
        return self.send_request("message_mark_read", {"email": email, "message_id": message_id})

    def delete_messages(self, email, message_ids):
        return self.send_request("message_delete", {"email": email, "message_ids": message_ids})

    def get_sent_messages(self, email):
        return self.send_request("message_sent", {"email": email})

    def update_profile(self, email, name, company, password=""):
        return self.send_request("user_update", {
            "email": email, "name": name,
            "company": company, "password": password
        })

    def update_message_setting(self, email, setting_type, content):
        return self.send_request("message_setting_update", {
            "email": email, "setting_type": setting_type, "content": content
        })

    def list_blacklist(self, email):
        return self.send_request("blacklist_list", {"email": email})

    def add_blacklist(self, email, target_email):
        return self.send_request("blacklist_add", {
            "email": email, "target_email": target_email
        })

    def list_cloud_files(self, email):
        return self.send_request("cloud_list", {"email": email})

    def list_shared_files(self, email):
        return self.send_request("cloud_shared", {"email": email})

    def list_trash_files(self, email):
        return self.send_request("cloud_trash", {"email": email})

    def upload_cloud_file(self, email, file_name, content_base64):
        return self.send_request("cloud_upload", {
            "email": email, "file_name": file_name,
            "content_base64": content_base64
        })

    def download_cloud_file(self, email, file_id):
        return self.send_request("cloud_download", {
            "email": email, "file_id": file_id
        })

    def delete_cloud_file(self, email, file_id):
        return self.send_request("cloud_delete", {
            "email": email, "file_id": file_id
        })

    def restore_cloud_file(self, email, file_id):
        return self.send_request("cloud_restore", {
            "email": email, "file_id": file_id
        })

    def send_email_verification(self, email):
        return self.send_request("send_email", {"email": email})

    def send_signup(self, user_info):
        return self.send_request("signup", user_info)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None


def send_login_request(email, password):
    client = NetworkClient(host='127.0.0.1', port=8888)
    response = client.send_request("login", {"user_id": email, "password": password})
    client.close()
    return response
