import sys
import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QCursor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox
)

# 상위 폴더(프로젝트 루트) 경로를 파이썬 경로에 추가하여 client.py를 임포트할 수 있도록 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from client.network_client import NetworkClient
except ImportError:
    NetworkClient = None  # <--- 2. None 대신 Any로 변경


class SettingsClient:
    """개인정보 수정, 비밀번호 변경, 등급 변경 등을 처리하는 서버 통신 클래스"""
    def __init__(self, net_client=  None):
        self.net_client = net_client

    def update_password(self, email, new_password):
        """비밀번호 변경을 요청하는 함수"""
        if self.net_client:
            return self.net_client.send_request("password_update", {"email": email, "password": new_password})
        print(f"[시뮬레이션] 비밀번호 변경 요청: {email}")
        return {"status": "success", "message": "비밀번호 변경 성공"}

    def update_tier(self, email, new_tier_id):
        """사용자의 서비스 등급(일반/VIP 등) 변경을 요청하는 함수"""
        if self.net_client:
            return self.net_client.send_request("settings_tier_update", {"email": email, "service_id": new_tier_id})
        print(f"[시뮬레이션] 등급 변경 요청: {email} -> {new_tier_id}")
        return {"status": "success", "message": "등급 변경 성공"}


class TierCardWidget(QFrame):
    """이미지 속 4개의 요금제 카드를 나타내는 개별 위젯"""
    def __init__(self, tier_id, tier_name, capacity_text, category="FREE", is_current=False, parent=None):
        super().__init__(parent)
        self.tier_id = tier_id
        self.tier_name = tier_name
        self.capacity_text = capacity_text
        self.is_selected = False

        self.setFixedWidth(135)
        self.setFixedHeight(210)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)

        # 1. 상단 FREE 표시
        cat_label = QLabel(category)
        cat_label.setAlignment(Qt.AlignCenter)
        cat_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #222222; background: transparent;")
        layout.addWidget(cat_label)

        # 2. 중간 둥근 배지 (일반, 비즈니스, VIP, VVIP)
        self.badge_btn = QPushButton(tier_name)
        self.badge_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A99E;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 12px;
                padding: 6px 10px;
            }
        """)
        # 클릭 이벤트를 카드 전체로 넘기기 설정
        self.badge_btn.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.badge_btn)

        layout.addStretch()

        # 3. 용량 안내
        cap_title = QLabel("용량")
        cap_title.setAlignment(Qt.AlignCenter)
        cap_title.setStyleSheet("font-size: 12px; color: #444444; background: transparent;")
        layout.addWidget(cap_title)

        cap_val = QLabel(f"최대 {capacity_text}")
        cap_val.setAlignment(Qt.AlignCenter)
        cap_val.setStyleSheet("font-size: 13px; font-weight: bold; color: #222222; background: transparent;")
        layout.addWidget(cap_val)

        layout.addStretch()

        self.update_style()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        """선택 여부에 따라 카드 테두리 및 배경색 변경"""
        if self.is_selected:
            self.setStyleSheet("""
                TierCardWidget {
                    background-color: #E2F4F1;
                    border: 2px solid #28A99E;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                TierCardWidget {
                    background-color: #EFF8F1;
                    border: 1px solid #63F2F2;
                    border-radius: 12px;
                }
                TierCardWidget:hover {
                    background-color: #E8F7F4;
                    border: 1.5px solid #28A99E;
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 부모 위젯(ServiceSettingWidget)의 select_tier 호출
            parent_service = self.window()
            if hasattr(parent_service, "select_tier"):
                parent_service.select_tier(self.tier_id)
        super().mousePressEvent(event)


class ServiceSettingWidget(QWidget):
    """
    '사용자 - 서비스 환경' (서비스 확인 및 변경) 화면 UI 및 기능 클래스.
    """
    def __init__(self, settings_client: SettingsClient = None, user_email: str = "user@example.com"):
        super().__init__()
        self.settings_client = settings_client or SettingsClient()
        self.user_email = user_email
        self.current_tier = "VIP"  # 기본 이용 중인 등급 (이미지 기준)
        self.selected_tier = "VIP"

        self.setStyleSheet("background-color: #EFF8F1; font-family: 'Malgun Gothic', sans-serif;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # 1. 상단 타이틀 & 현재 이용 등급 표시
        self.init_header(main_layout)

        # 2. 요금제 카드 4종 (일반, 비즈니스, VIP, VVIP)
        self.init_tier_cards(main_layout)

        # 3. 하단 변경하기 버튼
        self.init_bottom_button(main_layout)

    def init_header(self, parent_layout):
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)

        # 현재 이용중인 등급 레이블
        self.tier_status_label = QLabel(f"현재 이용중인 등급 : {self.current_tier}")
        self.tier_status_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #222222;")
        header_layout.addWidget(self.tier_status_label)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #D0D8D2; background-color: #D0D8D2;")
        line.setFixedHeight(1)
        header_layout.addWidget(line)

        parent_layout.addLayout(header_layout)

    def init_tier_cards(self, parent_layout):
        parent_layout.addStretch()

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignCenter)

        tiers_info = [
            ("일반", "일반", "100MB"),
            ("비즈니스", "비즈니스", "200MB"),
            ("VIP", "VIP", "500MB"),
            ("VVIP", "VVIP", "1GB")
        ]

        self.cards = {}
        for tier_id, tier_name, capacity in tiers_info:
            card = TierCardWidget(
                tier_id=tier_id,
                tier_name=tier_name,
                capacity_text=capacity,
                category="FREE",
                is_current=(tier_id == self.current_tier)
            )
            cards_layout.addWidget(card)
            self.cards[tier_id] = card

        parent_layout.addLayout(cards_layout)
        parent_layout.addStretch()

        # 기본으로 현재 이용중인 등급 선택 표시
        self.select_tier(self.current_tier)

    def init_bottom_button(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.change_btn = QPushButton("변경하기")
        self.change_btn.setFixedSize(200, 40)
        self.change_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.change_btn.setStyleSheet("""
            QPushButton {
                background-color: #63F2F2;
                color: #222222;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #52D4D4;
            }
            QPushButton:pressed {
                background-color: #42C4C4;
            }
        """)
        self.change_btn.clicked.connect(self.handle_tier_change)
        btn_layout.addWidget(self.change_btn)

        parent_layout.addLayout(btn_layout)

    def select_tier(self, tier_id):
        """카드를 클릭하면 실행되는 등급 선택 함수"""
        self.selected_tier = tier_id
        for tid, card in self.cards.items():
            card.set_selected(tid == tier_id)

    def handle_tier_change(self):
        """'변경하기' 버튼 클릭 시 서버로 등급 변경 요청"""
        if self.selected_tier == self.current_tier:
            QMessageBox.information(self, "알림", f"현재 이미 '{self.current_tier}' 등급을 이용 중입니다.")
            return

        reply = QMessageBox.question(
            self,
            "등급 변경 확인",
            f"서비스 등급을 '{self.current_tier}'에서 '{self.selected_tier}'(으)로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # SettingsClient의 update_tier 함수 호출
            res = self.settings_client.update_tier(self.user_email, self.selected_tier)
            self.current_tier = self.selected_tier
            self.tier_status_label.setText(f"현재 이용중인 등급 : {self.current_tier}")
            QMessageBox.information(self, "완료", f"서비스 등급이 '{self.current_tier}'(으)로 변경되었습니다.")


# 단독 테스트 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServiceSettingWidget()
    window.setWindowTitle("사용자 - 서비스 환경 (설정)")
    window.resize(800, 550)
    window.show()
    sys.exit(app.exec())