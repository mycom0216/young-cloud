from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit
)

class BasePopup(QDialog):
    """
    모든 팝업창에서 공통으로 사용하는 3분할 레이아웃 베이스 클래스
    - 상단: 타이틀 영역
    - 중간: 컨텐츠(텍스트 입력/조회) 영역
    - 하단: 액션 및 닫기 버튼 영역
    """
    def __init__(self, title_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title_text)
        self.resize(450, 550)
        self.setStyleSheet("background-color: #EFF8F1;")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. 상단 영역 (타이틀)
        self.top_container = QWidget()
        self.top_layout = QVBoxLayout(self.top_container)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(10)
        
        self.title_label = QLabel(title_text)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #111;")
        self.top_layout.addWidget(self.title_label)
        main_layout.addWidget(self.top_container)

        # 2. 중간 영역 (컨텐츠 - 서브클래스에서 구체화)
        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(10)
        main_layout.addWidget(self.center_container, stretch=1)

        # 3. 하단 영역 (기본 닫기 버튼 포함)
        self.bottom_container = QWidget()
        self.bottom_layout = QHBoxLayout(self.bottom_container)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(10)
        
        self.bottom_layout.addStretch()
        self.close_btn = QPushButton("닫기")
        self.close_btn.setFixedSize(80, 35)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #63F2F2;
                color: #333333;
                border-radius: 5px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #4ce5e5; }
        """)
        self.close_btn.clicked.connect(self.close)
        self.bottom_layout.addWidget(self.close_btn)
        main_layout.addWidget(self.bottom_container)


class ReceiveMessagePopup(BasePopup):
    """목업 이미지를 기반으로 구현한 [받은메시지] 상세 팝업창"""
    def __init__(self, parent=None):
        super().__init__("받은메시지", parent)
        self.init_content()

    def init_content(self):
        # 상단 영역: 보낸 사람 레이아웃 추가
        sender_label = QLabel("보낸 사람 : ")
        sender_label.setStyleSheet("font-weight: bold; color: #333;")
        self.top_layout.addWidget(sender_label)

        # 중간 영역: 메시지 본문 출력을 위한 QTextEdit (텍스트 입력/조회 영역)
        self.msg_content_edit = QTextEdit()
        self.msg_content_edit.setPlaceholderText("메시지 내용을 입력하거나 확인하세요.")
        self.msg_content_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.center_layout.addWidget(self.msg_content_edit)

        # 하단 영역: '답장' 버튼 추가 (닫기 버튼 왼쪽에 삽입)
        self.reply_btn = QPushButton("답장")
        self.reply_btn.setFixedSize(80, 35)
        self.reply_btn.setStyleSheet("""
            QPushButton {
                background-color: #63F2F2;
                color: #333333;
                border-radius: 5px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #4ce5e5; }
        """)
        # 하단 레이아웃의 스트레치와 닫기 버튼 사이에 '답장' 버튼 배치
        self.bottom_layout.insertWidget(1, self.reply_btn)