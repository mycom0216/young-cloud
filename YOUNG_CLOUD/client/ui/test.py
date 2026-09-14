import sys
import os

# 부모 폴더(client 폴더)를 경로에 추가하여 network_client 모듈을 정상적으로 불러오도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))  # client/ui
client_dir = os.path.dirname(current_dir)                 # client
sys.path.append(client_dir)

# 이제 상위 폴더에 있는 network_client를 정상적으로 불러올 수 있습니다!
from network_client import NetworkClient

def run_test():
    print("[테스트 클라이언트 시작] 서버와 통신을 시도합니다...")
    
    # 공용 네트워크 클라이언트 객체 생성 (로컬 환경 테스트 시 127.0.0.1 또는 localhost 사용)
    # 만약 원격 가상환경 서버라면 서버의 IP 주소로 변경해주세요.
    client = NetworkClient(host='127.0.0.1', port=8888)
    
    # 1. 서버 연결 시도
    if not client.connect():
        print("[테스트 실패] 서버에 연결하지 못했습니다. 서버가 켜져 있는지 확인해주세요.")
        return

    print("[서버 연결 성공!] 로그인 요청 테스트를 전송합니다.")

    # 2. 서버로 보낼 테스트 데이터 구성 (로그인 액션)
    # 주의: 실제 DB에 존재하는 테스트용 계정 정보(이메일, 비밀번호)가 있어야 성공합니다.
    test_data = {
        "user_id": "test@youngcloud.com",
        "password": "secure_password123"
    }

    # 3. 서버에 'login' 액션 요청 전송 및 응답 받기
    response = client.send_request(action="login", data=test_data)
    
    print("-" * 40)
    print(f"[서버로부터 받은 응답 결과]")
    print(response)
    print("-" * 40)

    # 4. 연결 종료
    client.close()
    print("[테스트 완료] 클라이언트 연결을 종료합니다.")

if __name__ == "__main__":
    run_test()