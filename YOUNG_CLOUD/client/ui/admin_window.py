import sys
import os

# 상위 폴더(프로젝트 루트) 경로를 파이썬 경로에 추가하여 client.py를 임포트할 수 있도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from client.network_client import NetworkClient

class AdminClient:
    """관리자 기능(유저 관리, 차단 등)과 관련된 서버 통신을 담당하는 클래스"""
    def __init__(self, net_client: NetworkClient):
        self.net_client = net_client  # 공용 네트워크 객체 주입받기

    def fetch_all_users(self):
        """전체 유저 목록을 조회하는 요청 함수"""
        return self.net_client.send_request("admin_get_users")

    def block_user(self, target_email):
        """특정 사용자를 차단하는 요청 함수"""
        return self.net_client.send_request("admin_block_user", {"email": target_email})