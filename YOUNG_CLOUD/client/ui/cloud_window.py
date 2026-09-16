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


class CloudClient:
    """클라우드 파일 업로드/다운로드 등과 관련된 서버 통신을 담당하는 클래스"""
    
    # 이전 코드와 동일하게 타입 힌트를 빼고 기본값을 None으로 줍니다.
    def __init__(self, net_client=None):
        self.net_client = net_client

    def upload_file(self, file_name, file_size):
        """파일 업로드 시작을 서버에 알리는 요청 함수"""
        if self.net_client:
            return self.net_client.send_request("cloud_upload", {"file_name": file_name, "file_size": file_size})
        # 시뮬레이션용 가짜 응답
        print(f"[시뮬레이션] 파일 업로드 요청: {file_name} ({file_size} bytes)")
        return {"status": "success", "message": "업로드 준비 완료"}

    def download_file(self, file_id):
        """파일 다운로드를 요청하는 함수"""
        if self.net_client:
            return self.net_client.send_request("cloud_download", {"file_id": file_id})
        # 시뮬레이션용 가짜 응답
        print(f"[시뮬레이션] 파일 다운로드 요청: ID {file_id}")
        return {"status": "success", "message": "다운로드 시작"}