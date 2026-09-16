import sys
import os

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QHeaderView,
)



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
    
    
class CloudWindow(QWidget):
    def __init__(self, net_client=None, parent=None):
        super().__init__(parent)
        self.cloud_client = CloudClient(net_client)
        self.setStyleSheet("""
            QWidget {
                background-color: #EFF8F1;
                font-size: 10pt;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #D5DED8;
            }

            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #EEEEEE;
            }

            QPushButton {
                background-color: #63F2F2;
                border: none;
                border-radius: 5px;
                padding: 7px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #45DCDC;
            }
        """)

        self.init_ui()
        self.load_sample_files()

    def init_ui(self):
        """클라우드 화면 구성"""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # 제목
        title_label = QLabel("> 내 파일")
        title_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold;"
        )
        main_layout.addWidget(title_label)

        # 상단 버튼 영역
        button_layout = QHBoxLayout()

        self.upload_button = QPushButton("파일 올리기")
        self.download_button = QPushButton("파일 받기")
        self.delete_button = QPushButton("삭제")

        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # 구분선
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #C8D5CC;")
        main_layout.addWidget(line)

        # 파일 목록 테이블
        self.file_table = QTableWidget(0, 5)
        self.file_table.setHorizontalHeaderLabels(
            ["선택", "파일명", "종류", "수정일", "용량"]
        )

        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )

        self.file_table.setColumnWidth(0, 50)
        self.file_table.setColumnWidth(2, 70)

        main_layout.addWidget(self.file_table)

        # 버튼 이벤트 연결
        self.upload_button.clicked.connect(self.upload_file)
        self.download_button.clicked.connect(self.download_file)
        self.delete_button.clicked.connect(self.delete_file)

    def load_sample_files(self):
        """UI 확인을 위한 임시 파일 목록"""

        sample_files = [
            ["서비스 운영관리", "폴더", "2026-09-30", ""],
            ["신규프로젝트", "폴더", "2026-09-30", ""],
            ["웹하드 운영서비스", "폴더", "2026-09-23", ""],
            ["웹하드프로젝트", "폴더", "2026-09-30", ""],
            ["웹하드 리뉴얼 이벤트 디자인.jpg", "파일", "2026-09-30", "762.5 KB"],
            ["웹하드 신규오픈 이벤트.jpg", "파일", "2026-09-30", "581.3 KB"],
        ]

        self.file_table.setRowCount(0)

        for file_data in sample_files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            # 체크박스
            check_box = QCheckBox()
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)
            check_layout.setContentsMargins(0, 0, 0, 0)
            check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            check_layout.addWidget(check_box)

            self.file_table.setCellWidget(row, 0, check_widget)

            # 나머지 정보
            for column, value in enumerate(file_data, start=1):
                item = QTableWidgetItem(value)
                self.file_table.setItem(row, column, item)

    def upload_file(self):
        """파일 올리기"""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "업로드할 파일 선택",
        )

        if not file_path:
            return

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        response = self.cloud_client.upload_file(
            file_name,
            file_size,
        )

        QMessageBox.information(
            self,
            "파일 업로드",
            response.get("message", "업로드 요청 완료"),
        )

    def download_file(self):
        """파일 받기"""

        current_row = self.file_table.currentRow()

        if current_row < 0:
            QMessageBox.warning(
                self,
                "선택 필요",
                "다운로드할 파일을 선택해주세요.",
            )
            return

        response = self.cloud_client.download_file(
            current_row
        )

        QMessageBox.information(
            self,
            "파일 다운로드",
            response.get("message", "다운로드 요청 완료"),
        )

    def delete_file(self):
        """파일 삭제"""

        current_row = self.file_table.currentRow()

        if current_row < 0:
            QMessageBox.warning(
                self,
                "선택 필요",
                "삭제할 파일을 선택해주세요.",
            )
            return

        self.file_table.removeRow(current_row)

        QMessageBox.information(
            self,
            "삭제 완료",
            "선택한 파일을 삭제했습니다.",
        )