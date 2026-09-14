# -*- coding: utf-8 -*-
import sys
import os

# 상위 폴더(프로젝트 루트) 경로를 파이썬 경로에 추가하여 client.py를 임포트할 수 있도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

# 통신 파일에서 필요한 함수만 '가져다' 쓰기
from network_client import send_login_request
# from sign_client import send_login_request

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """UI 컴포넌트 초기화 및 디자인 배치"""
        self.setWindowTitle("YOUNG CLOUD - 로그인")
        self.setFixedSize(900, 650)
        
        # 1. 배경 색상 설정 (#EFF8F1)
        self.setStyleSheet("background-color: #EFF8F1;")
        
        # 전체를 담을 메인 레이아웃 (수직 배치)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 40, 50, 40)
        
        # 2. 상단 로고 이미지 배치
        self.logo_label = QLabel(self)
        image_path = os.path.join(parent_dir, "source", "image", "YOUNG CLOUD.png")
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("[ YOUNG CLOUD 로고 이미지 ]")
            self.logo_label.setStyleSheet("color: #555555; font-weight: bold;")
            
        self.logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.logo_label)
   
        # 3. 환영 문구
        welcome_label = QLabel("“0”부터 무한대까지 클라우드를 즐겨보세요!", self)
        welcome_font = QFont("Arial", 16, QFont.Bold)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #222222; margin-top: 14px; margin-bottom: 30px;")
        main_layout.addWidget(welcome_label)
        
        # 4. 입력폼 그리드 레이아웃 (라벨, 입력창, 버튼을 격자로 정렬)
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)   # 라벨과 입력창 사이 간격
        form_layout.setVerticalSpacing(12)     # 아이디 행과 비밀번호 행 사이 간격
        
        # [수정 1] 그리드 자체를 중앙으로 모으기 위해 부모 레이아웃에서 정렬 설정
        # ---------------------------------------------------------
        # 아이디 라벨 및 입력창
        id_label = QLabel("아이디 :", self)
        id_label.setFont(QFont("Arial", 10, QFont.Bold))
        id_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter) # 우측 정렬로 변경하여 콜론(:) 맞춤
        
        self.id_input = QLineEdit(self)
        self.id_input.setFixedSize(300, 42)
        self.id_input.setPlaceholderText("ex) young123@gmail.com")
        # [수정 2] margin-left 제거 (그리드가 이미 위치를 잡아주므로 중복 마진은 제거해야 함)
        self.id_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 8px;")
        
        # 비밀번호 라벨 및 입력창
        pw_label = QLabel("비밀번호 :", self)
        pw_label.setFont(QFont("Arial", 10, QFont.Bold))
        pw_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter) # 우측 정렬
        
        self.pw_input = QLineEdit(self)
        self.pw_input.setFixedSize(300, 42)
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setPlaceholderText("비밀번호를 입력하세요")
        # [수정 3] margin-left 제거
        self.pw_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 8px;")
        
        # 로그인 버튼 (입력창과 동일한 300px 너비)
        self.login_btn = QPushButton("로그인", self)
        self.login_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.login_btn.setFixedSize(300, 42)
        
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #72EFEF;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5ce3e3;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login_click)
        
        # [수정 4] 그리드에 위젯 배치 (라벨을 열 0번에, 입력창/버튼을 열 1번에 배치)
        form_layout.addWidget(id_label, 0, 0)
        form_layout.addWidget(self.id_input, 0, 1)
        
        form_layout.addWidget(pw_label, 1, 0)
        form_layout.addWidget(self.pw_input, 1, 1)
        
        # 로그인 버튼을 2행 1열에 배치
        form_layout.addWidget(self.login_btn, 2, 1)
        
        # [수정 5] 그리드 레이아웃 전체를 메인 레이아웃의 '가운데'에 오도록 설정
        # QGridLayout은 기본적으로 왼쪽 정렬되므로 수평 중앙 정렬을 위해 서브 레이아웃으로 감싸거나 정렬 지정
        container_widget = QWidget()
        container_widget.setLayout(form_layout)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(container_widget)
        center_layout.addStretch()
        
        main_layout.addLayout(center_layout)
        
    # 5. 하단 '회원가입', '비밀번호 변경' 텍스트 버튼 레이아웃
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        # [핵심] '회원가입' 버튼보다 왼쪽에 빈 공간을 주어 전체를 오른쪽으로 밀어냄!
        # 숫자를 키울수록 '회원가입'과 '비밀번호 변경'이 모두 오른쪽으로 이동합니다.
        footer_layout.addSpacing(15)  # <-- 이 숫자를 조절해 보세요 (예: 15, 25 등)
        
        self.signup_btn = QPushButton("회원가입", self)
        self.signup_btn.setStyleSheet("background: transparent; color: #000000; border: none; font-size: 14px; font-weight: bold;")
        self.signup_btn.setCursor(Qt.PointingHandCursor)
        self.signup_btn.clicked.connect(self.open_signup_page)
        
        self.pw_reset_btn = QPushButton("비밀번호 변경", self)
        self.pw_reset_btn.setStyleSheet("background: transparent; color: #000000; border: none; font-size: 14px; font-weight: bold;")
        self.pw_reset_btn.setCursor(Qt.PointingHandCursor)
        self.pw_reset_btn.clicked.connect(self.open_pw_reset_page)
        
        # 위젯 배치
        footer_layout.addWidget(self.signup_btn)
        
        # '회원가입'과 '비밀번호 변경' 사이의 간격 (이 숫자로 두 버튼 사이 벌어짐 조절)
        footer_layout.addSpacing(50)  
        
        footer_layout.addWidget(self.pw_reset_btn)
        
        # 300px 폭을 가진 컨테이너 박스 생성
        footer_container = QWidget()
        footer_container.setLayout(footer_layout)
        footer_container.setFixedSize(300, 30) 
        
        # 300px 박스 전체를 화면 정중앙에 배치
        footer_center_layout = QHBoxLayout()
        footer_center_layout.addStretch()
        footer_center_layout.addWidget(footer_container)
        footer_center_layout.addStretch()
        
        # 하단 푸터에 상단 여백 추가 후 메인에 레이아웃 결합
        main_layout.addSpacing(15)
        main_layout.addLayout(footer_center_layout)
        
        self.setLayout(main_layout)
    def handle_login_click(self):
        """로그인 버튼 클릭 시 유효성 검사 및 서버 통신을 수행하는 함수"""
        email = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "경고", "아이디와 비밀번호를 모두 입력해주세요.")
            return
            
        response = send_login_request(email, password)
        
        if response.get("status") == "success":
            user_name = response.get("name", "사용자")
            QMessageBox.information(self, "성공", f"로그인 성공! 환영합니다, {user_name}님.")
            self.open_main_window()
        else:
            error_msg = response.get("message", "로그인에 실패했습니다.")
            QMessageBox.critical(self, "로그인 실패", error_msg)

    def open_main_window(self):
        """로그인 성공 시 메인 화면으로 전환하는 뼈대 함수"""
        print("[GUI] 메인 화면으로 전환을 수행합니다.")
        self.close()

    def open_signup_page(self):
        QMessageBox.information(self, "안내", "회원가입 화면으로 이동합니다. (구현 예정)")

    def open_pw_reset_page(self):
        QMessageBox.information(self, "안내", "비밀번호 변경 화면으로 이동합니다. (구현 예정)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())