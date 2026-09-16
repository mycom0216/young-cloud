import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialog,
    QFrame,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QHeaderView,
)

# 실행 방식에 따라 두 가지 import를 차례로 시도합니다.
try:
    from ..network_client import NetworkClient
except ImportError:
    try:
        from network_client import NetworkClient
    except ImportError:
        NetworkClient = None


class CloudClient:
    """클라우드 관련 서버 요청을 담당하는 클래스"""

    def __init__(self, net_client=None):
        self.net_client = net_client

    def upload_file(self, file_path):
        """파일 업로드 요청"""

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        if self.net_client:
            return self.net_client.send_request(
                "cloud_upload",
                {
                    "file_name": file_name,
                    "file_size": file_size,
                }
            )

        # 서버 연결 전 테스트용 응답
        print(f"[테스트] 업로드 요청: {file_name}")
        return {
            "status": "success",
            "message": "업로드 요청 완료",
        }

    def download_file(self, file_id):
        """파일 다운로드 요청"""

        if self.net_client:
            return self.net_client.send_request(
                "cloud_download",
                {
                    "file_id": file_id,
                }
            )

        # 서버 연결 전 테스트용 응답
        print(f"[테스트] 다운로드 요청: {file_id}")
        return {
            "status": "success",
            "message": "다운로드 요청 완료",
        }


class FileTransferDialog(QDialog):
    """파일 올리기와 파일 받기에 사용하는 공통 팝업"""

    def __init__(
        self,
        title,
        folder_text,
        cloud_client=None,
        mode="upload",
        files=None,
        parent=None,
    ):
        super().__init__(parent)

        self.cloud_client = cloud_client
        self.mode = mode
        self.files = files or []

        self.setWindowTitle(title)
        self.resize(360, 430)

        self.setStyleSheet("""
            QDialog {
                background-color: #EFF8F1;
            }

            QLabel {
                font-size: 9pt;
                color: #222222;
            }

            QPushButton {
                background-color: #5CE4E3;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 9pt;
            }

            QPushButton:hover {
                background-color: #42D2D1;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 4px;
            }

            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #DDDDDD;
            }

            QHeaderView::section {
                background-color: #D9D9D9;
                border: none;
                padding: 4px;
                font-size: 9pt;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold;"
        )
        main_layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(line)

        # 폴더 선택 영역
        folder_layout = QHBoxLayout()

        folder_label = QLabel(folder_text)

        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setPlaceholderText(
            "선택한 폴더가 표시됩니다"
        )

        folder_button = QPushButton("폴더선택")
        folder_button.clicked.connect(self.select_folder)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit, 1)
        folder_layout.addWidget(folder_button)

        main_layout.addLayout(folder_layout)

        # 파일 목록
        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(
            ["파일명", "상태", "크기"]
        )

        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.file_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        main_layout.addWidget(self.file_table)

        # 전송 버튼
        send_layout = QHBoxLayout()
        send_layout.addStretch()

        send_button = QPushButton("전송 시작")
        send_button.clicked.connect(self.start_transfer)

        send_layout.addWidget(send_button)
        send_layout.addStretch()

        main_layout.addLayout(send_layout)

        main_layout.addStretch()

        # 닫기 버튼
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.reject)

        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)

        # 다운로드 팝업이면 이미 선택된 파일을 표시합니다.
        if self.mode == "download":
            self.load_download_files()

    def select_folder(self):
        """업로드 또는 다운로드 폴더 선택"""

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "폴더 선택"
        )

        if not folder_path:
            return

        self.folder_edit.setText(folder_path)

        # 업로드일 때만 폴더 안의 파일을 읽습니다.
        if self.mode == "upload":
            self.load_upload_files(folder_path)

    def load_upload_files(self, folder_path):
        """업로드할 폴더 안의 파일 표시"""

        self.file_table.setRowCount(0)
        self.files.clear()

        try:
            file_names = os.listdir(folder_path)
        except OSError as error:
            QMessageBox.warning(
                self,
                "오류",
                f"폴더를 읽을 수 없습니다.\n{error}"
            )
            return

        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)

            if not os.path.isfile(file_path):
                continue

            self.files.append(file_path)

            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            self.file_table.setItem(
                row,
                0,
                QTableWidgetItem(file_name)
            )
            self.file_table.setItem(
                row,
                1,
                QTableWidgetItem("대기")
            )
            self.file_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{os.path.getsize(file_path):,} bytes"
                )
            )

    def load_download_files(self):
        """다운로드할 원격 파일 목록 표시"""

        self.file_table.setRowCount(0)

        for file_data in self.files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            file_name = file_data.get("name", "")
            file_size = file_data.get("size", "-")

            self.file_table.setItem(
                row,
                0,
                QTableWidgetItem(file_name)
            )
            self.file_table.setItem(
                row,
                1,
                QTableWidgetItem("대기")
            )
            self.file_table.setItem(
                row,
                2,
                QTableWidgetItem(str(file_size))
            )

    def start_transfer(self):
        """전송 시작"""

        if not self.folder_edit.text():
            QMessageBox.warning(
                self,
                "알림",
                "먼저 폴더를 선택하세요."
            )
            return

        if self.file_table.rowCount() == 0:
            QMessageBox.warning(
                self,
                "알림",
                "전송할 파일이 없습니다."
            )
            return

        if self.mode == "upload":
            for file_path in self.files:
                response = self.cloud_client.upload_file(
                    file_path
                )

                if response.get("status") != "success":
                    QMessageBox.warning(
                        self,
                        "업로드 실패",
                        response.get(
                            "message",
                            "업로드에 실패했습니다."
                        )
                    )
                    return

            QMessageBox.information(
                self,
                "파일 업로드",
                "파일 업로드 요청이 완료되었습니다."
            )

        else:
            for file_data in self.files:
                response = self.cloud_client.download_file(
                    file_data.get("id")
                )

                if response.get("status") != "success":
                    QMessageBox.warning(
                        self,
                        "다운로드 실패",
                        response.get(
                            "message",
                            "다운로드에 실패했습니다."
                        )
                    )
                    return

            QMessageBox.information(
                self,
                "파일 다운로드",
                "파일 다운로드 요청이 완료되었습니다."
            )

        self.accept()


class CloudWindow(QWidget):
    """클라우드 메인 화면"""

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
        """클라우드 화면 UI 구성"""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        title_label = QLabel("> 내 파일")
        title_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold;"
        )
        main_layout.addWidget(title_label)

        button_layout = QHBoxLayout()

        self.upload_button = QPushButton("파일 올리기")
        self.download_button = QPushButton("파일 받기")
        self.delete_button = QPushButton("삭제")

        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(line)

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
            0,
            QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.file_table.setColumnWidth(0, 50)
        self.file_table.setColumnWidth(2, 70)

        main_layout.addWidget(self.file_table)

        self.upload_button.clicked.connect(
            self.open_upload_dialog
        )
        self.download_button.clicked.connect(
            self.open_download_dialog
        )
        self.delete_button.clicked.connect(
            self.delete_file
        )

    def open_upload_dialog(self):
        """파일 올리기 팝업 표시"""

        dialog = FileTransferDialog(
            "파일 올리기",
            "올릴 폴더 선택",
            self.cloud_client,
            "upload",
            parent=self
        )
        dialog.exec()

    def open_download_dialog(self):
        """파일 받기 팝업 표시"""

        selected_files = []

        for row in range(self.file_table.rowCount()):
            check_widget = self.file_table.cellWidget(row, 0)

            if check_widget is None:
                continue

            check_box = check_widget.findChild(QCheckBox)

            if check_box and check_box.isChecked():
                name_item = self.file_table.item(row, 1)
                size_item = self.file_table.item(row, 4)

                selected_files.append({
                    "id": row,
                    "name": name_item.text()
                    if name_item else "",
                    "size": size_item.text()
                    if size_item else "-",
                })

        if not selected_files:
            QMessageBox.warning(
                self,
                "선택 필요",
                "다운로드할 파일을 체크해주세요."
            )
            return

        dialog = FileTransferDialog(
            "파일 받기",
            "받을 폴더 선택",
            self.cloud_client,
            "download",
            selected_files,
            self
        )
        dialog.exec()

    def load_sample_files(self):
        """테스트용 파일 목록"""

        sample_files = [
            ["서비스 운영관리", "폴더", "2026-09-30", ""],
            ["신규프로젝트", "폴더", "2026-09-30", ""],
            ["웹하드 운영서비스", "폴더", "2026-09-23", ""],
            ["웹하드프로젝트", "폴더", "2026-09-30", ""],
            [
                "웹하드 리뉴얼 이벤트 디자인.jpg",
                "파일",
                "2026-09-30",
                "762.5 KB",
            ],
            [
                "웹하드 신규오픈 이벤트.jpg",
                "파일",
                "2026-09-30",
                "581.3 KB",
            ],
        ]

        self.file_table.setRowCount(0)

        for file_data in sample_files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            check_box = QCheckBox()
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)

            check_layout.setContentsMargins(0, 0, 0, 0)
            check_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            check_layout.addWidget(check_box)

            self.file_table.setCellWidget(
                row,
                0,
                check_widget
            )

            for column, value in enumerate(
                file_data,
                start=1
            ):
                self.file_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value)
                )

    def delete_file(self):
        """체크된 파일 삭제"""

        rows_to_delete = []

        for row in range(self.file_table.rowCount()):
            check_widget = self.file_table.cellWidget(row, 0)

            if check_widget is None:
                continue

            check_box = check_widget.findChild(QCheckBox)

            if check_box and check_box.isChecked():
                rows_to_delete.append(row)

        if not rows_to_delete:
            QMessageBox.warning(
                self,
                "선택 필요",
                "삭제할 파일을 체크해주세요."
            )
            return

        for row in reversed(rows_to_delete):
            self.file_table.removeRow(row)

        QMessageBox.information(
            self,
            "삭제 완료",
            "선택한 파일을 삭제했습니다."
        )