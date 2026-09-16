import sys
import os

# 상위 폴더(프로젝트 루트) 경로를 파이썬 경로에 추가하여 client.py를 임포트할 수 있도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from client.network_client import NetworkClient
except ImportError:
    NetworkClient = None  # 단독 테스트를 위한 예외 처리


class MessageClient:
    """메시지 송수신 및 읽음 처리를 담당하는 서버 통신 클래스"""
    
    # 타입 힌트를 제거하고 기본값을 None으로 설정하여 단독 실행 및 Pylance 에러 방지
    def __init__(self, net_client=None):
        self.net_client = net_client

    def send_message(self, receiver, content):
        """상대방에게 메시지를 전송하는 요청 함수"""
        if self.net_client:
            return self.net_client.send_request("message_send", {"receiver": receiver, "content": content})
        
        # 시뮬레이션용 가짜 응답
        print(f"[시뮬레이션] 메시지 전송 요청: 대상({receiver}), 내용({content})")
        return {"status": "success", "message": "메시지 전송 성공"}

    def get_received_messages(self, user_email):
        """내가 받은 메시지 목록을 조회하는 요청 함수"""
        if self.net_client:
            return self.net_client.send_request("message_received", {"email": user_email})
        
        # 시뮬레이션용 가짜 응답 (UI에서 목록이 잘 뜨는지 확인하기 위한 더미 데이터)
        print(f"[시뮬레이션] 메시지 목록 조회 요청: {user_email}")
        return {
            "status": "success", 
            "messages": [
                {"id": 1, "sender": "admin@cloud.com", "content": "클라우드 서비스 가입을 환영합니다!", "date": "2026-09-15"},
                {"id": 2, "sender": "test@example.com", "content": "안녕하세요, 잘 부탁드립니다.", "date": "2026-09-15"}
            ]
        }