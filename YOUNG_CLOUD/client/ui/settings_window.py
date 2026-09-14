import sys
import os

# 상위 폴더(프로젝트 루트) 경로를 파이썬 경로에 추가하여 client.py를 임포트할 수 있도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from client.network_client import NetworkClient

class SettingsClient:
    """개인정보 수정, 비밀번호 변경, 등급 변경 등을 처리하는 서버 통신 클래스"""
    def __init__(self, net_client: NetworkClient):
        self.net_client = net_client

    def update_password(self, email, new_password):
        """비밀번호 변경을 요청하는 함수"""
        return self.net_client.send_request("password_update", {"email": email, "password": new_password})

    def update_tier(self, email, new_tier_id):
        """사용자의 서비스 등급(일반/VIP 등) 변경을 요청하는 함수"""
        return self.net_client.send_request("settings_tier_update", {"email": email, "service_id": new_tier_id})