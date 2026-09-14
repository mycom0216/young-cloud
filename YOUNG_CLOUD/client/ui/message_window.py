import sys
import os

# 상위 폴더(프로젝트 루트) 경로를 파이썬 경로에 추가하여 client.py를 임포트할 수 있도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from client.network_client import NetworkClient

class MessageClient:
    """메시지 송수신 및 읽음 처리를 담당하는 서버 통신 클래스"""
    def __init__(self, net_client: NetworkClient):
        self.net_client = net_client

    def send_message(self, receiver, content):
        """상대방에게 메시지를 전송하는 요청 함수"""
        return self.net_client.send_request("message_send", {"receiver": receiver, "content": content})

    def get_received_messages(self, user_email):
        """내가 받은 메시지 목록을 조회하는 요청 함수"""
        return self.net_client.send_request("message_received", {"email": user_email})