# settings_window.py
import re
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialog, QFileDialog,
    QPushButton, QFrame, QMessageBox, QLineEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QSettings


class SettingsClient:
    """개인정보 수정, 비밀번호 변경, 등급 변경 등을 처리하는 서버 통신 클래스"""
    def __init__(self, net_client=None):
        self.net_client = net_client

    def get_service_info(self, email):
        """사용자의 현재 서비스 등급 정보를 서버에서 조회하는 함수"""
        if self.net_client:
            return self.net_client.get_user_service(email)
        print(f"[시뮬레이션] 서비스 정보 조회: {email}")
        return {"status": "success", "grade_name": "VIP", "service_id": 3}

    def update_password(self, email, new_password):
        """비밀번호 변경을 요청하는 함수"""
        if self.net_client:
            return self.net_client.update_user_password(email, new_password)
        print(f"[시뮬레이션] 비밀번호 변경 요청: {email}")
        return {"status": "success", "message": "비밀번호 변경 성공"}

    def update_name(self, email, new_name):
        """이름 변경을 요청하는 함수"""
        if self.net_client:
            return self.net_client.update_user_name(email, new_name)
        print(f"[시뮬레이션] 이름 변경 요청: {email} -> {new_name}")
        return {"status": "success", "message": "이름 변경 성공"}

    def update_tier(self, email, grade_name):
        """사용자의 서비스 등급 변경을 요청하는 함수"""
        if self.net_client:
            return self.net_client.update_user_service(email, grade_name)
        print(f"[시뮬레이션] 등급 변경 요청: {email} -> {grade_name}")
        return {"status": "success", "message": "등급 변경 성공"}
    
class UserInfoSettingWidget(QWidget):
    """
    '사용자 - 개인정보 변경' 화면 UI 및 기능 클래스.
    """
    def __init__(self, settings_client: SettingsClient = None, user_info: dict = None, net_client=None):
        super().__init__()
        if settings_client is None:
            self.settings_client = SettingsClient(net_client=net_client)
        else:
            self.settings_client = settings_client

        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "podosong@gmail.com")
        self.user_name = self.user_info.get("name", "포도송이다")
        self.user_grade = self.user_info.get("grade_name", "VIP")

        self.is_name_checked = False
        self.is_pw_checked = False

        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(0)

        self.init_form_inputs(main_layout)
        self.init_bottom_button(main_layout)
        self.load_user_info()

    def init_form_inputs(self, parent_layout):
        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)
        form_layout.setAlignment(Qt.AlignLeft)

        label_style = "font-size: 15px; font-weight: bold; color: #1E293B;"
        input_style = """
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:disabled {
                background-color: #F1F5F9;
                color: #64748B;
            }
        """
        btn_style = """
            QPushButton {
                background-color: #55E6ED;
                color: #000000;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #40D4DC; }
        """
        # 0) 등급 (아이디 위로 이동)
        grade_box = QHBoxLayout()
        grade_box.setSpacing(15)
        lbl_grade_title = QLabel("등급 :")
        lbl_grade_title.setFixedWidth(80)
        lbl_grade_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_grade_title.setStyleSheet(label_style)

        # 등급 값 표시용 텍스트 (QLabel)
        self.grade_val_label = QLabel(self.user_grade)
        self.grade_val_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B;")

        grade_box.addWidget(lbl_grade_title)
        grade_box.addWidget(self.grade_val_label)
        grade_box.addStretch()



        # 1) 아이디
        id_box = QHBoxLayout()
        id_box.setSpacing(15)
        lbl_id = QLabel("아이디 :")
        lbl_id.setFixedWidth(80)
        lbl_id.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_id.setStyleSheet(label_style)

        self.input_id = QLineEdit(self.user_email)
        self.input_id.setFixedWidth(300)
        self.input_id.setEnabled(False)
        self.input_id.setStyleSheet(input_style)

        id_box.addWidget(lbl_id)
        id_box.addWidget(self.input_id)
        id_box.addStretch()

        # 2) 이름
        name_box = QHBoxLayout()
        name_box.setSpacing(15)
        lbl_name = QLabel("이름 :")
        lbl_name.setFixedWidth(80)
        lbl_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_name.setStyleSheet(label_style)

        self.input_name = QLineEdit(self.user_name)
        self.input_name.setFixedWidth(300)
        self.input_name.setStyleSheet(input_style)
        self.input_name.textChanged.connect(self.on_name_changed)

        btn_name_chk = QPushButton("확인")
        btn_name_chk.setFixedSize(60, 35)
        btn_name_chk.setCursor(Qt.PointingHandCursor)
        btn_name_chk.setStyleSheet(btn_style)
        btn_name_chk.clicked.connect(self.check_name)

        name_box.addWidget(lbl_name)
        name_box.addWidget(self.input_name)
        name_box.addWidget(btn_name_chk)
        name_box.addStretch()

        # 3) 비밀번호
        pw_box = QHBoxLayout()
        pw_box.setSpacing(15)
        lbl_pw = QLabel("비밀번호 :")
        lbl_pw.setFixedWidth(80)
        lbl_pw.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_pw.setStyleSheet(label_style)

        self.input_pw = QLineEdit()
        self.input_pw.setEchoMode(QLineEdit.Password)
        self.input_pw.setPlaceholderText("비밀번호 입력")
        self.input_pw.setFixedWidth(190)
        self.input_pw.setStyleSheet(input_style)
        self.input_pw.textChanged.connect(self.on_pw_changed)

        btn_pw_chk = QPushButton("확인")
        btn_pw_chk.setFixedSize(60, 35)
        btn_pw_chk.setCursor(Qt.PointingHandCursor)
        btn_pw_chk.setStyleSheet(btn_style)
        btn_pw_chk.clicked.connect(self.check_pw)

        lbl_pw_guide = QLabel("영문,숫자,특수문자 포함 조합 8-20자")
        lbl_pw_guide.setStyleSheet("font-size: 13px; color: #64748B;")

        pw_box.addWidget(lbl_pw)
        pw_box.addWidget(self.input_pw)
        pw_box.addWidget(btn_pw_chk)
        pw_box.addWidget(lbl_pw_guide)
        pw_box.addStretch()

        form_layout.addLayout(id_box)
        form_layout.addLayout(name_box)
        form_layout.addLayout(pw_box)

        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(50, 0, 0, 0)
        container_layout.addLayout(form_layout)

        parent_layout.addWidget(container_widget)
        parent_layout.addStretch()

    def init_bottom_button(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.change_btn = QPushButton("변경하기")
        self.change_btn.setFixedSize(170, 42)
        self.change_btn.setCursor(Qt.PointingHandCursor)
        self.change_btn.setStyleSheet("""
            QPushButton {
                background-color: #55E6ED; color: #000000; font-size: 16px; font-weight: bold; border: none; border-radius: 6px;
            }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        self.change_btn.clicked.connect(self.on_submit_change)
        btn_layout.addWidget(self.change_btn)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(30)

    def load_user_info(self):
        res = self.settings_client.get_service_info(self.user_email)
        if isinstance(res, dict) and res.get("status") == "success":
            self.user_grade = res.get("grade_name", "VIP")
            self.grade_val_label.setText(self.user_grade)
           

    def on_name_changed(self):
        self.is_name_checked = False

    def on_pw_changed(self):
        self.is_pw_checked = False

    def check_name(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "경고", "이름을 입력해주세요.")
            return
        self.is_name_checked = True
        QMessageBox.information(self, "확인 완료", "사용 가능한 이름입니다.")

    def check_pw(self):
        pw = self.input_pw.text().strip()
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'\",.<>/?]).{8,20}$"
        if not re.match(pattern, pw):
            QMessageBox.warning(self, "비밀번호 오류", "비밀번호는 영문, 숫자, 특수문자를 포함하여 8~20자로 작성해야 합니다.")
            self.is_pw_checked = False
            return
        self.is_pw_checked = True
        QMessageBox.information(self, "확인 완료", "사용 가능한 비밀번호 형식입니다.")

    def on_submit_change(self):
        new_name = self.input_name.text().strip()
        new_pw = self.input_pw.text().strip()
        changed = False

        if new_name != self.user_name:
            if not self.is_name_checked:
                QMessageBox.warning(self, "안내", "변경할 이름의 [확인] 버튼을 먼저 눌러주세요.")
                return
            res_name = self.settings_client.update_name(self.user_email, new_name)
            if isinstance(res_name, dict) and res_name.get("status") == "success":
                self.user_name = new_name
                changed = True
            else:
                QMessageBox.warning(self, "실패", "이름 변경 중 오류가 발생했습니다.")
                return

        if new_pw:
            if not self.is_pw_checked:
                QMessageBox.warning(self, "안내", "변경할 비밀번호의 [확인] 버튼을 먼저 눌러 유효성을 검사해주세요.")
                return
            res_pw = self.settings_client.update_password(self.user_email, new_pw)
            if isinstance(res_pw, dict) and res_pw.get("status") == "success":
                changed = True
                self.input_pw.clear()
            else:
                QMessageBox.warning(self, "실패", "비밀번호 변경 중 오류가 발생했습니다.")
                return

        if changed:
            QMessageBox.information(self, "성공", "개인정보가 성공적으로 변경되었습니다.")
        else:
            QMessageBox.information(self, "안내", "변경할 정보가 없거나 기존 정보와 동일합니다.")


class ServiceSettingWidget(QWidget):
    """'사용자 - 서비스 환경' 화면 클래스"""
    def __init__(self, settings_client: SettingsClient = None, user_email: str = "user@example.com", net_client=None):
        super().__init__()
        self.settings_client = settings_client or SettingsClient(net_client=net_client)
        self.user_email = user_email
        self.current_tier = "VIP"
        self.selected_tier = "VIP"
        self.tier_cards = {}

        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(0)

        self.init_header(main_layout)
        self.init_tier_cards(main_layout)
        self.init_bottom_button(main_layout)
        self.load_user_service_info()

    def init_header(self, parent_layout):
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)
        self.current_tier_label = QLabel(f"현재 이용중인 등급 : {self.current_tier}")
        self.current_tier_label.setStyleSheet("font-size: 14px; font-weight: bold; color: black;")
        header_layout.addWidget(self.current_tier_label)
        parent_layout.addLayout(header_layout)
        parent_layout.addSpacing(60)

    def init_tier_cards(self, parent_layout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(25)
        cards_layout.setAlignment(Qt.AlignCenter)

        tiers_info = [
            ("일반", "일반", "100MB"),
            ("비지니스", "비지니스", "200MB"),
            ("VIP", "VIP", "500MB"),
            ("VVIP", "VVIP", "1GB")
        ]

        for name, display_name, storage in tiers_info:
            card_container = QWidget()
            card_container.setFixedWidth(160)
            container_layout = QVBoxLayout(card_container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(8)

            free_label = QLabel("FREE")
            free_label.setAlignment(Qt.AlignCenter)
            free_label.setStyleSheet("font-size: 16px; font-weight: 900; color: #000000;")

            card_frame = QFrame()
            card_frame.setFixedSize(160, 240)
            card_frame.setCursor(Qt.PointingHandCursor)
            card_frame.mousePressEvent = lambda event, t=name: self.select_tier(t)

            card_layout = QVBoxLayout(card_frame)
            card_layout.setContentsMargins(15, 20, 15, 20)
            card_layout.setSpacing(0)

            badge_label = QLabel(display_name)
            badge_label.setFixedHeight(36)
            badge_label.setAlignment(Qt.AlignCenter)
            badge_label.setStyleSheet("""
                background-color: #179BAE; color: white; font-size: 15px; font-weight: bold; border-radius: 8px;
            """)

            info_layout = QVBoxLayout()
            info_layout.setAlignment(Qt.AlignCenter)
            info_layout.setSpacing(4)
            cap_title_label = QLabel("용량")
            cap_title_label.setAlignment(Qt.AlignCenter)
            cap_title_label.setStyleSheet("font-size: 13px; color: #1E293B; border: none;")
            cap_val_label = QLabel(f"최대 {storage}")
            cap_val_label.setAlignment(Qt.AlignCenter)
            cap_val_label.setStyleSheet("font-size: 13px; color: #1E293B; border: none;")

            info_layout.addWidget(cap_title_label)
            info_layout.addWidget(cap_val_label)

            card_layout.addWidget(badge_label)
            card_layout.addStretch()
            card_layout.addLayout(info_layout)
            card_layout.addStretch()

            container_layout.addWidget(free_label)
            container_layout.addWidget(card_frame)

            self.tier_cards[name] = card_frame
            cards_layout.addWidget(card_container)

        parent_layout.addLayout(cards_layout)
        parent_layout.addStretch()
        self.update_card_styles()

    def init_bottom_button(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        self.change_btn = QPushButton("변경하기")
        self.change_btn.setFixedSize(170, 42)
        self.change_btn.setCursor(Qt.PointingHandCursor)
        self.change_btn.setStyleSheet("""
            QPushButton { background-color: #55E6ED; color: #000000; font-size: 16px; font-weight: bold; border: none; border-radius: 6px; }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        self.change_btn.clicked.connect(self.on_change_click)
        btn_layout.addWidget(self.change_btn)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def select_tier(self, tier_name):
        self.selected_tier = tier_name
        
        # 기본 테두리 설정 (모든 카드 동일)
        default_border = "2px solid #00838F;" # 굵기를 2px로 통일
        
        # 선택된 카드 스타일 (색상만 변경)
        selected_border_color = "#005662" # 더 진한 색
        
        for name, card in self.tier_cards.items():
            if name == tier_name:
                # 선택된 카드: 두꺼운 테두리 유지 + 더 진한 색상 + 선택된 카드 내부 배경
                card.setStyleSheet(f"""
                    background-color: rgba(255, 255, 255, 204); 
                    border: 2px solid {selected_border_color}; 
                    border-radius: 12px;
                """)
            else:
                # 선택되지 않은 카드: 두꺼운 테두리 유지 + 기본 색상
                card.setStyleSheet(f"""
                    background-color: transparent; 
                    border: {default_border}; 
                    border-radius: 12px;
                """)

    def update_card_styles(self):
        for name, card in self.tier_cards.items():
            if name == self.selected_tier:
                card.setStyleSheet("QFrame { background-color: #EFF7F4; border: 2px solid #0E7490; border-radius: 12px; }")
            else:
                card.setStyleSheet("QFrame { background-color: #EFF7F4; border: 1.5px solid #179BAE; border-radius: 12px; }")
            card.style().unpolish(card)
            card.style().polish(card)

    def load_user_service_info(self):
        res = self.settings_client.get_service_info(self.user_email)
        if isinstance(res, dict) and res.get("status") == "success":
            grade = res.get("grade_name", "VIP")
            self.current_tier = grade
            self.selected_tier = grade
            self.current_tier_label.setText(f"현재 이용중인 등급 : {self.current_tier}")
            self.update_card_styles()

    def on_change_click(self):
        if self.selected_tier == self.current_tier:
            QMessageBox.information(self, "안내", f"이미 {self.current_tier} 등급을 이용 중입니다.")
            return

        reply = QMessageBox.question(
            self, "서비스 변경 확인", f"서비스 등급을 '{self.current_tier}'에서 '{self.selected_tier}'(으)로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            res = self.settings_client.update_tier(self.user_email, self.selected_tier)
            if isinstance(res, dict) and res.get("status") == "success":
                QMessageBox.information(self, "성공", f"서비스 등급이 '{self.selected_tier}'(으)로 변경되었습니다.\n적용을 위해 재로그인 해주세요.")
                self.current_tier = self.selected_tier
                self.current_tier_label.setText(f"현재 이용중인 등급 : {self.current_tier}")
                self.update_card_styles()
            else:
                QMessageBox.warning(self, "실패", "변경 요청 중 오류가 발생했습니다.")


class DefaultMessageSettingWidget(QWidget):
    """[기본 메시지 설정 화면]"""
    def __init__(self, settings_client: SettingsClient = None, user_info: dict = None, net_client=None):
        super().__init__()
        self.settings_client = settings_client or SettingsClient(net_client=net_client)
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "user@example.com")
        self.net_client = net_client

        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        desc_label = QLabel("메시지 보내기 시 자동으로 채워질 기본(상단) 메시지를 입력하세요.")
        desc_label.setStyleSheet("font-size: 14px; color: #475569;")
        layout.addWidget(desc_label)

        self.input_message = QLineEdit()
        self.input_message.setFixedHeight(100)
        self.input_message.setMaxLength(255)
        self.input_message.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.input_message.setStyleSheet("""
            QLineEdit { background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; padding: 10px; font-size: 14px; }
        """)
        layout.addWidget(self.input_message)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("저장하기")
        save_btn.setFixedSize(130, 40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #55E6ED; color: #000000; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        save_btn.clicked.connect(self.save_default_message)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        self.load_message_data()

    def load_message_data(self):
        if self.net_client:
            res = self.net_client.get_user_messages_config(self.user_email)
            if res.get("status") == "success":
                self.input_message.setText(res.get("default_message", ""))

    def save_default_message(self):
        new_msg = self.input_message.text().strip()
        if self.net_client:
            res_current = self.net_client.get_user_messages_config(self.user_email)
            outro_msg = res_current.get("outro_message", "") if res_current.get("status") == "success" else ""
            
            res = self.net_client.update_user_messages_config(self.user_email, new_msg, outro_msg)
            if res.get("status") == "success":
                QMessageBox.information(self, "성공", "기본 메시지가 성공적으로 저장되었습니다.")
            else:
                QMessageBox.warning(self, "실패", "저장 중 오류가 발생했습니다.")


class OutroMessageSettingWidget(QWidget):
    """[마무리 메시지 설정 화면]"""
    def __init__(self, settings_client: SettingsClient = None, user_info: dict = None, net_client=None):
        super().__init__()
        self.settings_client = settings_client or SettingsClient(net_client=net_client)
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "user@example.com")
        self.net_client = net_client

        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        desc_label = QLabel("메시지 보내기 시 자동으로 채워질 마무리(하단) 메시지를 입력하세요.")
        desc_label.setStyleSheet("font-size: 14px; color: #475569;")
        layout.addWidget(desc_label)

        self.input_message = QLineEdit()
        self.input_message.setFixedHeight(100)
        self.input_message.setMaxLength(255)
        self.input_message.setStyleSheet("""
            QLineEdit { background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; padding: 10px; font-size: 14px; }
        """)
        layout.addWidget(self.input_message)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("저장하기")
        save_btn.setFixedSize(130, 40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #55E6ED; color: #000000; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        save_btn.clicked.connect(self.save_outro_message)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        self.load_message_data()

    def load_message_data(self):
        if self.net_client:
            res = self.net_client.get_user_messages_config(self.user_email)
            if res.get("status") == "success":
                self.input_message.setText(res.get("outro_message", ""))

    def save_outro_message(self):
        new_outro = self.input_message.text().strip()
        if self.net_client:
            res_current = self.net_client.get_user_messages_config(self.user_email)
            default_msg = res_current.get("default_message", "") if res_current.get("status") == "success" else ""
            
            res = self.net_client.update_user_messages_config(self.user_email, default_msg, new_outro)
            if res.get("status") == "success":
                QMessageBox.information(self, "성공", "마무리 메시지가 성공적으로 저장되었습니다.")
            else:
                QMessageBox.warning(self, "실패", "저장 중 오류가 발생했습니다.")


class UserBlacklistDialog(QDialog):
    """[특정 유저 차단/해제 다이얼로그 클래스]"""
    def __init__(self, target_email, is_blocked, current_user_email, net_client):
        super().__init__()
        self.target_email = target_email
        self.is_blocked = is_blocked
        self.current_user_email = current_user_email
        self.net_client = net_client
        self.init_dialog_ui()

    def init_dialog_ui(self):
        self.setWindowTitle("블랙리스트 설정")
        self.resize(400, 250)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Malgun Gothic', sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title_label = QLabel("블랙리스트 설정")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        self.label_target = QLabel(f"대상 이용자 : {self.target_email}")
        self.label_target.setStyleSheet("font-size: 14px; color: #333333;")
        layout.addWidget(self.label_target)

        self.info_input = QLineEdit()
        self.info_input.setText(f"현재 상태: {'차단됨' if self.is_blocked else '정상 이용 중'}")
        self.info_input.setReadOnly(True)
        self.info_input.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; font-size: 13px; color: #64748B;")
        layout.addWidget(self.info_input)

        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.action_btn = QPushButton()
        self.action_btn.setFixedHeight(40)
        self.action_btn.setCursor(Qt.PointingHandCursor)
        
        if self.is_blocked:
            self.action_btn.setText("차단해제하기")
            self.action_btn.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; border-radius: 6px; border: none;")
        else:
            self.action_btn.setText("차단하기")
            self.action_btn.setStyleSheet("background-color: #55E6ED; color: #000000; font-weight: bold; border-radius: 6px; border: none;")
        
        self.action_btn.clicked.connect(self.on_blacklist_action_clicked)

        close_btn = QPushButton("닫기")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("background-color: #E2E8F0; color: #333333; font-weight: bold; border-radius: 6px; border: none;")
        close_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.action_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def on_blacklist_action_clicked(self):
        msg = f"\"{self.target_email}\"님을 정말로 차단 해제하시겠습니까?" if self.is_blocked else f"\"{self.target_email}\"님을 정말로 블랙리스트에 차단하시겠습니까?"
        new_status = not self.is_blocked

        reply = QMessageBox.question(self, "상태 변경 확인", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.net_client:
                res = self.net_client.update_blacklist_status(
                    owner_email=self.current_user_email,
                    target_email=self.target_email,
                    is_block=new_status
                )
                if res.get("status") == "success":
                    QMessageBox.information(self, "성공", res.get("message", "처리가 완료되었습니다."))
                    self.accept()
                else:
                    QMessageBox.warning(self, "실패", res.get("message", "요청 처리에 실패했습니다."))
            else:
                QMessageBox.information(self, "성공", "처리 완료 (테스트 모드)")
                self.accept()


class BlockedUsersListDialog(QDialog):
    """
    [💡 신규 구현] '블랙리스트 목록_목업.png' 디자인을 반영한 차단 목록 관리 다이얼로그
    """
    def __init__(self, current_user_email, net_client):
        super().__init__()
        self.current_user_email = current_user_email
        self.net_client = net_client
        self.init_ui()
        self.load_blocked_users()

    def init_ui(self):
        self.setWindowTitle("블랙리스트 목록")
        self.resize(500, 450)
        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # 상단 타이틀
        title_label = QLabel("블랙리스트 목록")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # 구분선
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #CBD5E1;")
        layout.addWidget(line)

        # 상단 우측 '차단 해제' 버튼
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.unblock_btn = QPushButton("차단 해제")
        self.unblock_btn.setFixedSize(90, 32)
        self.unblock_btn.setCursor(Qt.PointingHandCursor)
        self.unblock_btn.setStyleSheet("""
            QPushButton { background-color: #55E6ED; color: #000000; font-weight: bold; border-radius: 4px; border: none; font-size: 12px; }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        self.unblock_btn.clicked.connect(self.on_unblock_clicked)
        btn_layout.addWidget(self.unblock_btn)
        layout.addLayout(btn_layout)

        # 테이블 위젯 (아이디, 이름, 차단일)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["아이디", "이름", "차단일"])
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: 1px solid #D0D8D2; gridline-color: #EFEFEF; font-size: 9pt; }
            QHeaderView::section { background-color: #EFF8F1; padding: 6px; border: none; font-weight: bold; font-size: 9pt; color: #333; }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 120)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 140)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # 하단 닫기 버튼
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        close_btn = QPushButton("닫기")
        close_btn.setFixedSize(80, 35)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton { background-color: #55E6ED; color: #000000; font-weight: bold; border-radius: 4px; border: none; font-size: 12px; }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)
        layout.addLayout(bottom_layout)

    def load_blocked_users(self):
        """서버에서 내가 차단한 유저 목록 조회"""
        if self.net_client:
            res = self.net_client.get_blocked_users_list(self.current_user_email)
            if res.get("status") == "success":
                self.update_table(res.get("users", []))
            else:
                self.update_table([])
        else:
            # 테스트용 더미 데이터
            self.update_table([{"EMAIL": "test@example.com", "NAME": "홍길동", "CREATED_AT": "2026-09-17 12:00:00"}])

    def update_table(self, users):
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.get("EMAIL", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(user.get("NAME", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(user.get("CREATED_AT", ""))))

    def on_unblock_clicked(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "안내", "차단 해제할 사용자를 선택해주세요.")
            return

        target_email = self.table.item(selected_row, 0).text()
        reply = QMessageBox.question(self, "차단 해제 확인", f"\"{target_email}\"님을 차단 해제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.net_client:
                res = self.net_client.update_blacklist_status(
                    owner_email=self.current_user_email,
                    target_email=target_email,
                    is_block=False
                )
                if res.get("status") == "success":
                    QMessageBox.information(self, "성공", "차단이 해제되었습니다.")
                    self.load_blocked_users()
                else:
                    QMessageBox.warning(self, "실패", res.get("message", "요청 처리 실패"))


class BlacklistSettingWidget(QWidget):
    """
    [설정 - 블랙리스트 설정 화면 메인 위젯]
    - '차단 목록' 버튼 추가 및 공백 검색 시 초기화 기능 반영
    """
    def __init__(self, settings_client=None, user_info=None, net_client=None):
        super().__init__()
        self.settings_client = settings_client
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "user@example.com")
        self.net_client = net_client
        
        self.user_list = []

        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)

        # 1. 상단 검색 영역 및 '차단목록' 버튼 배치
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        search_label = QLabel("아이디 검색")
        search_label.setStyleSheet("background-color: #EFF8F1; font-size: 12px; font-weight: bold; color: #333; padding: 4px;")
        top_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색할 아이디를 입력하세요...")
        self.search_input.setFixedHeight(30)
        self.search_input.setStyleSheet("background-color: #FFFFFF; border: 1px solid #D0D8D2; border-radius: 4px; padding-left: 5px; font-size: 11px;")
        
        # 💡 [핵심 요구사항] 검색어 변경 시 감지하여 공백이 되면 자동으로 목록을 초기화
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.search_users)
        top_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("검색")
        self.search_btn.setFixedSize(50, 30)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setStyleSheet("background-color: #63F2F2; color: #333; font-weight: bold; border-radius: 4px; border: none;")
        self.search_btn.clicked.connect(self.search_users)
        top_layout.addWidget(self.search_btn)

        top_layout.addStretch()

        # 💡 [핵심 요구사항 1] '차단 목록' 버튼 추가 (목업 이미지 반영)
        self.blocked_list_btn = QPushButton("차단 목록")
        self.blocked_list_btn.setFixedSize(90, 30)
        self.blocked_list_btn.setCursor(Qt.PointingHandCursor)
        self.blocked_list_btn.setStyleSheet("background-color: #55E6ED; color: #000000; font-weight: bold; border-radius: 4px; border: none; font-size: 11px;")
        self.blocked_list_btn.clicked.connect(self.open_blocked_list_dialog)
        top_layout.addWidget(self.blocked_list_btn)

        main_layout.addLayout(top_layout)

        # 2. 테이블 위젯 설정
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["아이디", "이름", "차단 상태"])
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: 1px solid #D0D8D2; gridline-color: #EFEFEF; font-size: 9pt; }
            QHeaderView::section { background-color: #EFF8F1; padding: 6px; border: none; font-weight: bold; font-size: 9pt; color: #333; }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 150)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 120)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_clicked)

        main_layout.addWidget(self.table)
        self.update_table_view([])

    def on_search_text_changed(self):
        """검색창이 공백이 되면 테이블을 즉시 초기화합니다."""
        if not self.search_input.text().strip():
            self.user_list = []
            self.update_table_view([])

    def search_users(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.user_list = []
            self.update_table_view([])
            return

        if self.net_client:
            res = self.net_client.search_users_for_blacklist(self.user_email, keyword)
            if res.get("status") == "success":
                self.user_list = res.get("users", [])
                self.update_table_view(self.user_list)
            else:
                QMessageBox.warning(self, "조회 실패", res.get("message", "사용자 검색에 실패했습니다."))
        else:
            self.user_list = [{"EMAIL": keyword, "NAME": "테스트유저", "IS_BLOCKED": False}]
            self.update_table_view(self.user_list)

    def update_table_view(self, users_to_display):
        self.table.setRowCount(len(users_to_display))
        for row, user in enumerate(users_to_display):
            email = user.get("EMAIL", "")
            name = user.get("NAME", "")
            is_blocked = bool(user.get("IS_BLOCKED", False))

            status_str = "차단" if is_blocked else "정상"

            item_email = QTableWidgetItem(str(email))
            item_name = QTableWidgetItem(str(name))
            item_status = QTableWidgetItem(str(status_str))

            if is_blocked:
                item_status.setForeground(Qt.red)
            else:
                item_status.setForeground(Qt.darkGreen)

            self.table.setItem(row, 0, item_email)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_status)

    def on_row_clicked(self, row, column):
        email_item = self.table.item(row, 0)
        status_item = self.table.item(row, 2)
        if not email_item:
            return

        target_email = email_item.text()
        if target_email == self.user_email:
            QMessageBox.information(self, "안내", "본인은 블랙리스트에 등록할 수 없습니다.")
            return

        is_blocked = (status_item.text() == "차단")
        dialog = UserBlacklistDialog(target_email, is_blocked, self.user_email, self.net_client)
        if dialog.exec() == QDialog.Accepted:
            self.search_users()

    def open_blocked_list_dialog(self):
        """'차단 목록' 버튼 클릭 시 모달 다이얼로그 팝업 오픈"""
        dialog = BlockedUsersListDialog(self.user_email, self.net_client)
        dialog.exec()
        # 다이얼로그가 닫히면 현재 검색 결과 새로고침
        if self.search_input.text().strip():
            self.search_users()
            
# settings_window.py 파일 하단에 추가할 클라우드 설정 위젯 클래스

class CloudSettingWidget(QWidget):
    """
    💡 [클라우드 설정 화면]
    - 파일 받기 저장 경로를 QSettings(클라이언트단)에 저장 및 불러오기
    """
    def __init__(self, user_info: dict = None, net_client=None):
        super().__init__()
        self.user_info = user_info or {}
        self.net_client = net_client
        self.user_email = self.user_info.get("email", "user@example.com")
        
        # 💡 클라이언트단 로컬 저장을 위한 QSettings 초기화
        self.settings = QSettings("YoungCloud", "ClientApp")

        # 전체 위젯 배경색 및 기본 폰트 설정
        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")

        # 메인 레이아웃 생성
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # 1. 화면 제목 라벨
        title_label = QLabel("클라우드 환경 설정")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        main_layout.addWidget(title_label)

        # 구분선 생성
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #CBD5E1; max-height: 1px;")
        main_layout.addWidget(line)

        # 2. 파일 받기 저장 경로 설정 영역 레이아웃
        path_layout = QHBoxLayout()
        path_layout.setSpacing(15)

        lbl_path_title = QLabel("파일 받기 경로:")
        lbl_path_title.setFixedWidth(110)
        lbl_path_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155;")

        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        self.input_path.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #334155;
            }
        """)

        btn_change_path = QPushButton("변경하기")
        btn_change_path.setFixedSize(90, 38)
        btn_change_path.setCursor(Qt.PointingHandCursor)
        btn_change_path.setStyleSheet("""
            QPushButton {
                background-color: #55E6ED;
                color: #000000;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #40D4DC; }
        """)
        btn_change_path.clicked.connect(self.open_folder_dialog)

        path_layout.addWidget(lbl_path_title)
        path_layout.addWidget(self.input_path)
        path_layout.addWidget(btn_change_path)
        main_layout.addLayout(path_layout)

        # 3. 클라우드 용량 정보 표시 영역
        self.storage_info_label = QLabel("현재 클라우드 사용량 정보를 불러오는 중입니다...")
        self.storage_info_label.setStyleSheet("font-size: 14px; color: #475569; margin-top: 10px;")
        main_layout.addWidget(self.storage_info_label)

        main_layout.addStretch()

        self.load_settings_data()

    def load_settings_data(self):
        """로컬(QSettings)에서 저장 경로를 불러오고, 서버로부터 클라우드 용량을 조회합니다."""
        # 1. 클라이언트단 QSettings에서 다운로드 경로 불러오기 (기본값: 사용자 다운로드 폴더)
        default_download = os.path.join(os.path.expanduser("~"), "Downloads")
        saved_path = self.settings.value(f"download_path_{self.user_email}", default_download)
        self.input_path.setText(saved_path)

        # 2. 클라우드 용량 정보 조회 요청 (서버 연동)
        if not self.net_client or not self.user_email:
            self.storage_info_label.setText("클라우드 용량: 0 MB / 500 MB (일반 회원)")
            return

        res_storage = self.net_client.get_user_storage_info(self.user_email)
        if res_storage.get("status") == "success":
            grade_name = res_storage.get("grade_name", "일반")
            max_bytes = res_storage.get("max_storage", 500 * 1024 * 1024)
            used_bytes = res_storage.get("total_used", 0)

            used_mb = used_bytes / (1024 * 1024)
            max_mb = max_bytes / (1024 * 1024)

            self.storage_info_label.setText(
                f"📊 현재 클라우드 사용량: {used_mb:.1f} MB / {max_mb:.0f} MB (등급: {grade_name})\n"
                f"💡 파일을 삭제하거나 휴지통에서 영구 삭제하면 사용 가능한 용량이 자동으로 늘어납니다."
            )

    def open_folder_dialog(self):
        """폴더 선택 후 QSettings에 로컬 경로 저장"""
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "파일 받기 저장 경로 선택", 
            self.input_path.text()
        )

        if dir_path:
            normalized_path = os.path.normpath(dir_path)
            self.input_path.setText(normalized_path)
            
            # 💡 QSettings에 사용자별 다운로드 경로 저장
            self.settings.setValue(f"download_path_{self.user_email}", normalized_path)
            QMessageBox.information(self, "성공", "파일 받기 저장 경로가 성공적으로 변경되었습니다.")