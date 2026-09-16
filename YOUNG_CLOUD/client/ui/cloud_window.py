import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from client.network_client import NetworkClient
except ImportError:
    NetworkClient = None


# --- 1. 기존 통신 로직 클래스 ---
class CloudClient:
    """클라우드 파일 업로드/다운로드 등과 관련된 서버 통신을 담당하는 클래스"""

    def __init__(self, net_client=None):
        self.net_client = net_client

    def upload_file(self, file_name, file_size):
        if self.net_client:
            return self.net_client.send_request(
                "cloud_upload",
                {"file_name": file_name, "file_size": file_size},
            )
        print(f"[시뮬레이션] 파일 업로드 요청: {file_name} ({file_size} bytes)")
        return {"status": "success", "message": "업로드 준비 완료"}

    def download_file(self, file_id):
        if self.net_client:
            return self.net_client.send_request(
                "cloud_download", {"file_id": file_id}
            )
        print(f"[시뮬레이션] 파일 다운로드 요청: ID {file_id}")
        return {"status": "success", "message": "다운로드 시작"}


# --- 2. 클라우드 내 파일 UI 클래스 ---
class CloudWindow(QWidget):
    """클라우드 - 내 파일 대시보드 UI 클래스"""

    def __init__(self, net_client=None, parent=None):
        super().__init__(parent)
        self.cloud_client = CloudClient(net_client)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(12)
        self.setStyleSheet("background-color: #F4F9F5;")  # 연한 녹색/회색 배경

        # ----------------------------------------------------
        # 1. 상단 툴바 (QToolButton 적용으로 아이콘 아래 텍스트 배치)
        # ----------------------------------------------------
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(25)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 시스템 기본 아이콘 사용 (프로젝트 내 custom .png 아이콘 파일 경로로 교체 가능)
        style = self.style()
        self.btn_upload = self.create_tool_btn(
            "파일 올리기", style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        )
        self.btn_download = self.create_tool_btn(
            "파일 받기", style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        )
        self.btn_delete = self.create_tool_btn(
            "삭제", style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )

        # 버튼 이벤트 연결
        self.btn_upload.clicked.connect(self.handle_upload)
        self.btn_download.clicked.connect(self.handle_download)
        self.btn_delete.clicked.connect(self.handle_delete)

        toolbar_layout.addWidget(self.btn_upload)
        toolbar_layout.addWidget(self.btn_download)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # 상단과 하단을 나누는 구분선 (Image 2 스타일)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #D6D6D6;")
        main_layout.addWidget(line)

        # ----------------------------------------------------
        # 2. 파일 목록 테이블 (헤더 숨기기 적용)
        # ----------------------------------------------------
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        
        # 헤더 및 세로 헤더, 격자선 숨기기 (Image 2와 동일하게 변경)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(0, 35)
        self.table.setColumnWidth(1, 30)
        self.table.setColumnWidth(3, 40)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 80)

        # 깔끔한 테이블 스타일 지정
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F0F0F0;
                padding: 4px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #EBF5FB;
                color: #000000;
            }
        """)

        # 더미 파일 목록 로드
        sample_data = [
            {"is_file": False, "name": "서비스 운영관리", "date": "2009-09-30 15:13:38", "size": ""},
            {"is_file": False, "name": "신규프로젝트", "date": "2009-09-30 15:13:28", "size": ""},
            {"is_file": False, "name": "웹하드 운영서비스", "date": "2009-09-23 15:51:39", "size": ""},
            {"is_file": False, "name": "웹하드프로젝트", "date": "2009-09-30 15:11:59", "size": ""},
            {"is_file": True, "name": "웹하드 리뉴얼 이벤트 디자인_B안.jpg", "date": "2009-09-30 15:15:28", "size": "762.5 KB", "checked": True},
            {"is_file": True, "name": "웹하드 신규오픈 이벤트 A안.jpg", "date": "2009-09-30 15:15:28", "size": "581.3 KB"},
        ]
        self.load_file_list(sample_data)
        main_layout.addWidget(self.table)

    def create_tool_btn(self, text, icon):
        """상단 툴바용 QToolButton 생성 함수 (아이콘 아래 텍스트 배치)"""
        btn = QToolButton(self)
        btn.setText(text)
        btn.setIcon(icon)
        btn.setIconSize(QSize(28, 28))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
                font-size: 12px;
                font-weight: bold;
                color: #222222;
            }
            QToolButton:hover {
                color: #007ACC;
            }
        """)
        return btn

    def load_file_list(self, files):
        self.table.setRowCount(len(files))
        style = self.style()
        folder_icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        file_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        for row, item in enumerate(files):
            # 0번 열: 체크박스
            chk_box = QCheckBox()
            chk_box.setChecked(item.get("checked", False))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, chk_widget)

            # 1번 열: 별표
            star_item = QTableWidgetItem("★" if item.get("checked") else "☆")
            star_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            star_item.setForeground(QColor("#FFC107" if item.get("checked") else "#CCCCCC"))
            self.table.setItem(row, 1, star_item)

            # 2번 열: 아이콘 + 이름
            name_item = QTableWidgetItem(item["name"])
            name_item.setIcon(file_icon if item["is_file"] else folder_icon)
            self.table.setItem(row, 2, name_item)

            # 3번 열: 공유 아이콘
            share_item = QTableWidgetItem("💽")
            share_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, share_item)

            # 4번 열: 날짜
            date_item = QTableWidgetItem(item["date"])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_item.setForeground(QColor("#777777"))
            self.table.setItem(row, 4, date_item)

            # 5번 열: 용량
            size_item = QTableWidgetItem(item["size"])
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            size_item.setForeground(QColor("#777777"))
            self.table.setItem(row, 5, size_item)

    # 이벤트 동작 메서드
    def handle_upload(self):
        res = self.cloud_client.upload_file("sample_file.png", 2048)
        QMessageBox.information(
            self, "파일 업로드", res.get("message", "요청 완료")
        )

    def handle_download(self):
        res = self.cloud_client.download_file(file_id=1)
        QMessageBox.information(
            self, "파일 다운로드", res.get("message", "요청 완료")
        )

    def handle_delete(self):
        QMessageBox.information(self, "삭제", "선택한 항목을 삭제합니다.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CloudWindow()
    window.resize(750, 600)
    window.show()
    sys.exit(app.exec())