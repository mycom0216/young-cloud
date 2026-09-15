# -*- coding: utf-8 -*-
import os
import random
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # client 폴더
root_dir = os.path.dirname(parent_dir)  # 프로젝트 루트 폴더
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "utils"))

from dialog.sign_up_ui import Ui_Form
from dialog.company_dialog import CompanySearchDialog  # 분리된 회사 검색 다이얼로그 임포트
from network_client import NetworkClient, send_login_request
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SignUpDialog(QDialog, Ui_Form):
    """회원가입 창 클래스 (sign_up_ui.py 연동)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("YOUNG CLOUD - 회원가입")

        # 상태 변수 초기화
        self.server_auth_code = None  # 서버로부터 받은 인증 코드 저장
        self.is_email_verified = False  # 이메일 인증 완료 여부
        self.is_pw_checked = False  # 비밀번호 유효성 검사 통과 여부

        # 버튼 이벤트 연결
        self.pushButton.clicked.connect(self.request_auth_code)       # 인증코드발송 버튼
        self.pushButton_2.clicked.connect(self.verify_auth_code)      # 인증확인 버튼
        self.pushButton_3.clicked.connect(self.check_password_valid)  # 비밀번호 확인 버튼
        self.pushButton_4.clicked.connect(self.handle_signup)         # 가입하기 버튼
        self.pushButton_5.clicked.connect(self.close)                 # 닫기 버튼
        self.pushButton_7.clicked.connect(self.handle_company_api)    # 회사명 검색 버튼

    def handle_company_api(self):
        """회사 검색 다이얼로그를 띄우고 선택된 회사명을 lineEdit_5에 대입"""
        search_dlg = CompanySearchDialog(self)
        if search_dlg.exec() == QDialog.Accepted:
            if search_dlg.selected_company_name:
                self.lineEdit_5.setText(search_dlg.selected_company_name)

    def request_auth_code(self):
        """1. 이메일 입력 후 [인증코드발송] 버튼 클릭 시"""
        email = self.lineEdit.text().strip()
        if not email or "@" not in email:
            QMessageBox.warning(self, "경고", "올바른 이메일 주소를 입력해주세요.")
            return

        client = NetworkClient()
        response = client.send_email_verification(email)
        client.close()

        if response.get("status") == "success":
            self.server_auth_code = str(response.get("auth_code"))
            QMessageBox.information(self, "성공", "인증 코드가 이메일로 발송되었습니다.")
        else:
            QMessageBox.critical(
                self, "실패", response.get("message", "인증 코드 발송에 실패했습니다.")
            )

    def verify_auth_code(self):
        """2. [인증확인] 버튼 클릭 시"""
        user_code = self.lineEdit_2.text().strip()
        if not self.server_auth_code:
            QMessageBox.warning(self, "경고", "먼저 인증코드를 발송해주세요.")
            return

        if user_code == self.server_auth_code:
            self.is_email_verified = True
            QMessageBox.information(self, "성공", "이메일 인증이 완료되었습니다.")
            self.lineEdit.setReadOnly(True)
            self.lineEdit_2.setReadOnly(True)
        else:
            QMessageBox.warning(self, "실패", "인증 코드가 일치하지 않습니다.")

    def check_password_valid(self):
        """3. [비밀번호 확인] 버튼 클릭 시 (영문, 숫자, 특수문자 포함 8~20자 검증)"""
        import re

        password = self.lineEdit_3.text().strip()
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+~`-{}\[\]:;\"'<>,.?/\\|]).{8,20}$"

        if re.match(pattern, password):
            self.is_pw_checked = True
            QMessageBox.information(self, "사용 가능", "사용 가능한 안전한 비밀번호입니다.")
        else:
            self.is_pw_checked = False
            QMessageBox.warning(
                self,
                "조건 불충족",
                "비밀번호는 영문, 숫자, 특수문자를 포함하여 8~20자로 설정해야 합니다.",
            )

    def handle_signup(self):
        """4. [가입하기] 버튼 클릭 시 최종 회원가입 요청"""
        email = self.lineEdit.text().strip()
        password = self.lineEdit_3.text().strip()
        name = self.lineEdit_4.text().strip()
        company = self.lineEdit_5.text().strip()

        if not self.is_email_verified:
            QMessageBox.warning(self, "경고", "이메일 인증을 완료해주세요.")
            return
        if not self.is_pw_checked:
            QMessageBox.warning(self, "경고", "비밀번호 유효성 검사를 진행해주세요.")
            return
        if not name or not company:
            QMessageBox.warning(self, "경고", "이름과 회사명을 모두 입력해주세요.")
            return

        grade = "일반"
        if self.radioButton_2.isChecked():
            grade = "비즈니스"
        elif self.radioButton_3.isChecked():
            grade = "VIP"
        elif self.radioButton_4.isChecked():
            grade = "VVIP"
        elif not self.radioButton.isChecked():
            grade = "일반"

        signup_data = {
            "email": email,
            "password": password,
            "name": name,
            "company": company,
            "grade": grade,
        }

        client = NetworkClient()
        response = client.send_signup(signup_data)
        client.close()

        if response.get("status") == "success":
            QMessageBox.information(
                self, "환영합니다", "회원가입이 완료되었습니다! 로그인해주세요."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "가입 실패",
                response.get("message", "회원가입 중 오류가 발생했습니다."),
            )


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YOUNG CLOUD - 로그인")
        self.setFixedSize(900, 650)
        self.setStyleSheet("background-color: #EFF8F1;")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 40, 50, 40)

        # 상단 로고
        self.logo_label = QLabel(self)
        image_path = os.path.join(
            root_dir, "client", "ui", "source", "image", "YOUNG CLOUD.png"
        )
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("[ YOUNG CLOUD 로고 이미지 ]")
            self.logo_label.setStyleSheet("color: #555555; font-weight: bold;")
        self.logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.logo_label)

        # 환영 문구
        welcome_label = QLabel("“0”부터 무한대까지 클라우드를 즐겨보세요!", self)
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(
            "color: #222222; margin-top: 14px; margin-bottom: 30px;"
        )
        main_layout.addWidget(welcome_label)

        # 입력폼 그리드
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(12)

        id_label = QLabel("아이디 :", self)
        id_label.setFont(QFont("Arial", 10, QFont.Bold))
        id_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.id_input = QLineEdit(self)
        self.id_input.setFixedSize(300, 42)
        self.id_input.setPlaceholderText("ex) young123@gmail.com")
        self.id_input.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 8px;"
        )

        pw_label = QLabel("비밀번호 :", self)
        pw_label.setFont(QFont("Arial", 10, QFont.Bold))
        pw_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.pw_input = QLineEdit(self)
        self.pw_input.setFixedSize(300, 42)
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.pw_input.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 8px;"
        )

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

        form_layout.addWidget(id_label, 0, 0)
        form_layout.addWidget(self.id_input, 0, 1)
        form_layout.addWidget(pw_label, 1, 0)
        form_layout.addWidget(self.pw_input, 1, 1)
        form_layout.addWidget(self.login_btn, 2, 1)

        container_widget = QWidget()
        container_widget.setLayout(form_layout)

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(container_widget)
        center_layout.addStretch()
        main_layout.addLayout(center_layout)

        # 하단 버튼 (회원가입, 비밀번호 변경)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addSpacing(15)

        self.signup_btn = QPushButton("회원가입", self)
        self.signup_btn.setStyleSheet(
            "background: transparent; color: #000000; border: none; font-size: 14px; font-weight: bold;"
        )
        self.signup_btn.setCursor(Qt.PointingHandCursor)
        self.signup_btn.clicked.connect(self.open_signup_page)

        self.pw_reset_btn = QPushButton("비밀번호 변경", self)
        self.pw_reset_btn.setStyleSheet(
            "background: transparent; color: #000000; border: none; font-size: 14px; font-weight: bold;"
        )
        self.pw_reset_btn.setCursor(Qt.PointingHandCursor)
        self.pw_reset_btn.clicked.connect(self.open_pw_reset_page)

        footer_layout.addWidget(self.signup_btn)
        footer_layout.addSpacing(50)
        footer_layout.addWidget(self.pw_reset_btn)

        footer_container = QWidget()
        footer_container.setLayout(footer_layout)
        footer_container.setFixedSize(300, 30)

        footer_center_layout = QHBoxLayout()
        footer_center_layout.addStretch()
        footer_center_layout.addWidget(footer_container)
        footer_center_layout.addStretch()

        main_layout.addSpacing(15)
        main_layout.addLayout(footer_center_layout)
        self.setLayout(main_layout)

    def handle_login_click(self):
        email = self.id_input.text().strip()
        password = self.pw_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "경고", "아이디와 비밀번호를 모두 입력해주세요.")
            return

        response = send_login_request(email, password)

        if response.get("status") == "success":
            QMessageBox.information(self, "성공", "로그인 성공!")
            self.open_main_window()
        else:
            error_msg = response.get("message", "로그인에 실패했습니다.")
            QMessageBox.critical(self, "로그인 실패", error_msg)

    def open_main_window(self):
        print("[GUI] 메인 화면으로 전환을 수행합니다.")
        self.close()

    def open_signup_page(self):
        """회원가입 다이얼로그 오픈"""
        self.signup_dialog = SignUpDialog(self)
        self.signup_dialog.exec()

    def open_pw_reset_page(self):
        QMessageBox.information(
            self, "안내", "비밀번호 변경 화면으로 이동합니다. (구현 예정)"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())