import sys
import os
import socket
import json
import hashlib
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget, QDialog
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader


# 서버 연결 정보 설정
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9000


def send_login_request(email, raw_password):
    """
    서버로 로그인 요청을 전송하고 응답 결과를 반환하는 함수
    - 비밀번호는 보안을 위해 클라이언트에서 단방향 해시(SHA-256) 처리하여 전송
    """
    try:
        # 비밀번호 단방향 해시 암호화 (데이터 정의서 PASSWORD HASH 규격 대응)
        password_hash = hashlib.sha256(raw_password.encode('utf-8')).hexdigest()
        
        # 전송할 요청 데이터 규격 정의
        request_data = {
            "action": "POST_LOGIN",
            "email": email,
            "password": password_hash
        }
        
        # TCP 소켓 생성 및 서버 연결
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        
        # 데이터 전송
        client_socket.sendall(json.dumps(request_data).encode('utf-8'))
        
        # 서버로부터 응답 대기 및 수신
        response_data = client_socket.recv(4096)
        client_socket.close()
        
        if response_data:
            return json.loads(response_data.decode('utf-8'))
        else:
            return {"status": "fail", "message": "서버로부터 응답이 없습니다."}
            
    except ConnectionRefusedError:
        return {"status": "fail", "message": "서버와 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."}
    except Exception as e:
        return {"status": "fail", "message": f"통신 오류 발생: {str(e)}"}
    
    
