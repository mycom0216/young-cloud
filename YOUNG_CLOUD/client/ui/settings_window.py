from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


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
            return self.net_client.send_request("password_update", {"email": email, "password": new_password})
        print(f"[시뮬레이션] 비밀번호 변경 요청: {email}")
        return {"status": "success", "message": "비밀번호 변경 성공"}

    def update_tier(self, email, grade_name):
        """사용자의 서비스 등급 변경을 요청하는 함수"""
        if self.net_client:
            return self.net_client.update_user_service(email, grade_name)
        print(f"[시뮬레이션] 등급 변경 요청: {email} -> {grade_name}")
        return {"status": "success", "message": "등급 변경 성공"}


class ServiceSettingWidget(QWidget):
    """
    '사용자 - 서비스 환경' (서비스 확인 및 변경) 화면 UI 및 기능 클래스.
    """
    def __init__(self, settings_client: SettingsClient = None, user_email: str = "user@example.com", net_client=None):
        super().__init__()
        if settings_client is None:
            self.settings_client = SettingsClient(net_client=net_client)
        else:
            self.settings_client = settings_client

        self.user_email = user_email
        self.current_tier = "VIP"
        self.selected_tier = "VIP"

        self.tier_cards = {}  # 카드 Frame 객체 저장용 딕셔너리

        # 이미지 배경색과 동일하게 설정 (#EFF7F4)
        self.setStyleSheet("background-color: #EFF7F4; font-family: 'Malgun Gothic', sans-serif;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(0)

        # 1. 상단 타이틀 & 구분선 & 현재 이용 등급 표시
        self.init_header(main_layout)

        # 2. 요금제 카드 4종 (이미지 디자인 배치 완벽 반영)
        self.init_tier_cards(main_layout)

        # 3. 하단 민트색 변경하기 버튼
        self.init_bottom_button(main_layout)

        # 4. 서버로부터 현재 사용자 서비스 등급 정보 로드
        self.load_user_service_info()

    def init_header(self, parent_layout):
        """상단 헤더 (제목, 구분선, 현재 사용 중인 등급 안내)"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)

        title_label = QLabel("> 서비스 확인 및 변경")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")

        # 상단 구분선
        line_top = QFrame()
        line_top.setFrameShape(QFrame.HLine)
        line_top.setStyleSheet("color: #94A3B8; background-color: #94A3B8; height: 1px; border: none;")

        self.current_tier_label = QLabel(f"현재 이용중인 등급 : {self.current_tier}")
        self.current_tier_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")

        # 하단 구분선
        line_bottom = QFrame()
        line_bottom.setFrameShape(QFrame.HLine)
        line_bottom.setStyleSheet("color: #94A3B8; background-color: #94A3B8; height: 1px; border: none;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(line_top)
        header_layout.addWidget(self.current_tier_label)
        header_layout.addWidget(line_bottom)

        parent_layout.addLayout(header_layout)
        parent_layout.addSpacing(60)  # 헤더와 카드 레이아웃 간격

    def init_tier_cards(self, parent_layout):
        """요금제 카드 4종 생성 및 이미지 스타일 배치"""
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

            # 1. 카드 상단 FREE 텍스트
            free_label = QLabel("FREE")
            free_label.setAlignment(Qt.AlignCenter)
            free_label.setStyleSheet("font-size: 16px; font-weight: 900; color: #000000;")

            # 2. 카드 본체 Frame
            card_frame = QFrame()
            card_frame.setFixedSize(160, 240)
            card_frame.setCursor(Qt.PointingHandCursor)
            card_frame.mousePressEvent = lambda event, t=name: self.select_tier(t)

            card_layout = QVBoxLayout(card_frame)
            card_layout.setContentsMargins(15, 20, 15, 20)
            card_layout.setSpacing(0)

            # 2-1. 청록색 라운드 등급 태그 버튼
            badge_label = QLabel(display_name)
            badge_label.setFixedHeight(36)
            badge_label.setAlignment(Qt.AlignCenter)
            badge_label.setStyleSheet("""
                background-color: #179BAE;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
            """)

            # 2-2. 중앙 용량 안내 (용량 / 최대 XXMB)
            info_layout = QVBoxLayout()
            info_layout.setAlignment(Qt.AlignCenter)
            info_layout.setSpacing(4)

            cap_title_label = QLabel("용량")
            cap_title_label.setAlignment(Qt.AlignCenter)
            cap_title_label.setStyleSheet("font-size: 15px; color: #1E293B;")

            cap_val_label = QLabel(f"최대 {storage}")
            cap_val_label.setAlignment(Qt.AlignCenter)
            cap_val_label.setStyleSheet("font-size: 15px; color: #1E293B;")

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
        """하단 민트색 '변경하기' 버튼"""
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.change_btn = QPushButton("변경하기")
        self.change_btn.setFixedSize(170, 42)
        self.change_btn.setCursor(Qt.PointingHandCursor)
        self.change_btn.setStyleSheet("""
            QPushButton {
                background-color: #55E6ED;
                color: #000000;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #40D4DC;
            }
            QPushButton:pressed {
                background-color: #2CBCC4;
            }
        """)
        self.change_btn.clicked.connect(self.on_change_click)

        btn_layout.addWidget(self.change_btn)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def select_tier(self, tier_name):
        """요금제 카드를 클릭했을 때 실행되는 함수"""
        self.selected_tier = tier_name
        print(f"선택된 서비스 등급: {self.selected_tier}")
        self.update_card_styles()

    def update_card_styles(self):
        """선택된 카드는 진한 두꺼운 테두리, 미선택 카드는 기본 테두리로 전환"""
        for name, card in self.tier_cards.items():
            if name == self.selected_tier:
                card.setStyleSheet("""
                    QFrame {
                        background-color: #EFF7F4;
                        border: 2px solid #0E7490;
                        border-radius: 12px;
                    }
                """)
            else:
                card.setStyleSheet("""
                    QFrame {
                        background-color: #EFF7F4;
                        border: 1.5px solid #179BAE;
                        border-radius: 12px;
                    }
                """)

            card.style().unpolish(card)
            card.style().polish(card)

    def load_user_service_info(self):
        """서버로부터 사용자의 현재 서비스 정보 조회 및 반영"""
        res = self.settings_client.get_service_info(self.user_email)
        if isinstance(res, dict) and res.get("status") == "success":
            grade = res.get("grade_name", "VIP")
            self.current_tier = grade
            self.selected_tier = grade
            self.current_tier_label.setText(f"현재 이용중인 등급 : {self.current_tier}")
            self.update_card_styles()

    def on_change_click(self):
        """변경하기 버튼 클릭 시 서버 요청 전송 처리"""
        if self.selected_tier == self.current_tier:
            QMessageBox.information(self, "안내", f"이미 {self.current_tier} 등급을 이용 중입니다.")
            return

        reply = QMessageBox.question(
            self, 
            "서비스 변경 확인", 
            f"서비스 등급을 '{self.current_tier}'에서 '{self.selected_tier}'(으)로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            res = self.settings_client.update_tier(self.user_email, self.selected_tier)
            if isinstance(res, dict) and res.get("status") == "success":
                QMessageBox.information(self, "성공", f"서비스 등급이 '{self.selected_tier}'(으)로 변경되었습니다.")
                self.current_tier = self.selected_tier
                self.current_tier_label.setText(f"현재 이용중인 등급 : {self.current_tier}")
                self.update_card_styles()
            else:
                msg = res.get("message", "변경 요청 중 오류가 발생했습니다.") if isinstance(res, dict) else "통신 오류가 발생했습니다."
                QMessageBox.warning(self, "실패", msg)