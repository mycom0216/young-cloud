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


class CloudClient:
    """클라우드 관련 서버 요청을 처리하는 클래스"""

    def __init__(self, net_client=None):
        self.net_client = net_client

    def upload_file(self, file_path):
        """선택한 파일의 업로드 요청을 서버에 보냅니다."""

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

        # 서버 미연결 상태에서 UI를 확인하기 위한 테스트 응답입니다.
        return {
            "status": "success",
            "message": f"{file_name} 업로드 요청 완료",
        }

    def download_file(self, file_id):
        """다운로드 요청을 서버에 보냅니다."""

        if self.net_client:
            return self.net_client.send_request(
                "cloud_download",
                {
                    "file_id": file_id,
                }
            )

        return {
            "status": "success",
            "message": "다운로드 요청 완료",
        }

    def move_to_trash(self, file_id):
        """파일을 휴지통으로 이동합니다."""

        if self.net_client:
            return self.net_client.send_request(
                "cloud_move_to_trash",
                {
                    "file_id": file_id,
                }
            )

        return {
            "status": "success",
            "message": "휴지통으로 이동했습니다.",
        }

    def delete_from_trash(self, file_id):
        """휴지통 파일을 영구 삭제합니다."""

        if self.net_client:
            return self.net_client.send_request(
                "cloud_delete_permanently",
                {
                    "file_id": file_id,
                }
            )

        return {
            "status": "success",
            "message": "영구 삭제했습니다.",
        }


class FileTransferDialog(QDialog):
    """파일 올리기 또는 파일 받기 팝업창"""

    def __init__(
        self,
        title,
        mode,
        cloud_client,
        files=None,
        parent=None,
    ):
        super().__init__(parent)

        self.mode = mode
        self.cloud_client = cloud_client
        self.files = files or []

        self.setWindowTitle(title)
        self.resize(390, 430)

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

        # 팝업 제목
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold;"
        )
        main_layout.addWidget(title_label)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(line)

        # 업로드는 파일 선택, 다운로드는 저장 폴더 선택
        select_layout = QHBoxLayout()

        if self.mode == "upload":
            select_label = QLabel("올릴 파일 선택")
        else:
            select_label = QLabel("받을 폴더 선택")

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)

        if self.mode == "upload":
            self.path_edit.setPlaceholderText(
                "선택한 파일이 표시됩니다"
            )

            select_button = QPushButton("파일선택")
            select_button.clicked.connect(
                self.select_files
            )
        else:
            self.path_edit.setPlaceholderText(
                "다운로드할 폴더가 표시됩니다"
            )

            select_button = QPushButton("폴더선택")
            select_button.clicked.connect(
                self.select_download_folder
            )

        select_layout.addWidget(select_label)
        select_layout.addWidget(self.path_edit, 1)
        select_layout.addWidget(select_button)

        main_layout.addLayout(select_layout)

        # 파일 목록 테이블
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

        # 전송 시작 버튼
        send_layout = QHBoxLayout()
        send_layout.addStretch()

        send_button = QPushButton("전송 시작")
        send_button.clicked.connect(
            self.start_transfer
        )

        send_layout.addWidget(send_button)
        send_layout.addStretch()

        main_layout.addLayout(send_layout)

        # 여백
        main_layout.addStretch()

        # 닫기 버튼
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.reject)

        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)

        # 다운로드 팝업은 메인 화면에서 체크한 파일을 표시합니다.
        if self.mode == "download":
            self.load_download_files()

    def select_files(self):
        """업로드할 파일을 여러 개 선택합니다."""

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "업로드할 파일 선택",
            "",
            "모든 파일 (*.*)"
        )

        if not file_paths:
            return

        self.files = file_paths

        first_file_name = os.path.basename(
            file_paths[0]
        )

        if len(file_paths) == 1:
            self.path_edit.setText(first_file_name)
        else:
            self.path_edit.setText(
                f"{first_file_name} 외 {len(file_paths) - 1}개"
            )

        self.load_upload_files()

    def select_download_folder(self):
        """다운로드 파일을 저장할 폴더를 선택합니다."""

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "다운로드할 폴더 선택"
        )

        if folder_path:
            self.path_edit.setText(folder_path)

    def load_upload_files(self):
        """선택한 업로드 파일을 테이블에 표시합니다."""

        self.file_table.setRowCount(0)

        for file_path in self.files:
            if not os.path.isfile(file_path):
                continue

            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

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
                    f"{file_size:,} bytes"
                )
            )

    def load_download_files(self):
        """메인 화면에서 체크한 다운로드 대상 파일을 표시합니다."""

        self.file_table.setRowCount(0)

        for file_data in self.files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            self.file_table.setItem(
                row,
                0,
                QTableWidgetItem(file_data["name"])
            )
            self.file_table.setItem(
                row,
                1,
                QTableWidgetItem("대기")
            )
            self.file_table.setItem(
                row,
                2,
                QTableWidgetItem(file_data["size"])
            )

    def start_transfer(self):
        """업로드 또는 다운로드 요청을 처리합니다."""

        if self.mode == "upload":
            if not self.files:
                QMessageBox.warning(
                    self,
                    "파일 선택 필요",
                    "업로드할 파일을 선택하세요."
                )
                return

            for row, file_path in enumerate(self.files):
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

                self.file_table.setItem(
                    row,
                    1,
                    QTableWidgetItem("완료")
                )

            QMessageBox.information(
                self,
                "파일 업로드",
                "선택한 파일의 업로드 요청이 완료되었습니다."
            )

        else:
            if not self.path_edit.text():
                QMessageBox.warning(
                    self,
                    "저장 위치 필요",
                    "다운로드할 폴더를 선택하세요."
                )
                return

            for row, file_data in enumerate(self.files):
                response = self.cloud_client.download_file(
                    file_data["id"]
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

                self.file_table.setItem(
                    row,
                    1,
                    QTableWidgetItem("완료")
                )

            QMessageBox.information(
                self,
                "파일 다운로드",
                "다운로드 요청이 완료되었습니다.\n"
                f"저장 위치: {self.path_edit.text()}"
            )


class CloudWindow(QWidget):
    """내 파일 화면"""

    def __init__(self, net_client=None, parent=None):
        super().__init__(parent)

        self.cloud_client = CloudClient(net_client)

        # 앱이 실행 중인 동안 휴지통 목록을 보관합니다.
        self.trash_files = []

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
        """내 파일 화면 UI 구성"""

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
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.file_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
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
            self.move_selected_to_trash
        )

    def open_upload_dialog(self):
        """파일 선택 방식의 업로드 팝업을 표시합니다."""
    # 팝업 생성 시 parent(self)를 넘겨줍니다.
        dialog = UploadDialog(self.net_client, self.user_email, self)
        dialog = FileTransferDialog(
            title="파일 올리기",
            mode="upload",
            cloud_client=self.cloud_client,
            parent=self
            
        # 팝업창에서 업로드가 성공하여 self.accept()가 호출되고 닫히면 메인 테이블 자동 갱신
    if dialog.exec() == QDialog.Accepted:
        self.load_file_list()  # 바탕화면 파일 목록 재조회
        )
        dialog.exec()

    def open_download_dialog(self):
        """체크된 파일을 다운로드 팝업에 표시합니다."""

        selected_files = self.get_checked_files()

        if not selected_files:
            QMessageBox.warning(
                self,
                "선택 필요",
                "다운로드할 파일을 체크해주세요."
            )
            return

        dialog = FileTransferDialog(
            title="파일 받기",
            mode="download",
            cloud_client=self.cloud_client,
            files=selected_files,
            parent=self
        )
        dialog.exec()

    def get_checked_files(self):
        """체크박스가 선택된 파일 정보를 반환합니다."""

        selected_files = []

        for row in range(self.file_table.rowCount()):
            check_widget = self.file_table.cellWidget(row, 0)

            if check_widget is None:
                continue

            check_box = check_widget.findChild(QCheckBox)

            if not check_box or not check_box.isChecked():
                continue

            name_item = self.file_table.item(row, 1)
            type_item = self.file_table.item(row, 2)
            date_item = self.file_table.item(row, 3)
            size_item = self.file_table.item(row, 4)

            selected_files.append({
                "id": name_item.data(
                    Qt.ItemDataRole.UserRole
                ),
                "name": name_item.text(),
                "type": type_item.text(),
                "date": date_item.text(),
                "size": size_item.text(),
            })

        return selected_files

    def load_sample_files(self):
        """UI 확인용 임시 파일 목록"""

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

        for index, file_data in enumerate(sample_files):
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
                item = QTableWidgetItem(value)

                # 서버의 실제 FILE_ID가 생기면 index 대신 그 값을 사용합니다.
                if column == 1:
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        index
                    )

                self.file_table.setItem(
                    row,
                    column,
                    item
                )

    def move_selected_to_trash(self):
        """선택 파일을 영구 삭제하지 않고 휴지통으로 이동합니다."""

        selected_files = self.get_checked_files()

        if not selected_files:
            QMessageBox.warning(
                self,
                "선택 필요",
                "휴지통으로 옮길 파일을 체크해주세요."
            )
            return

        answer = QMessageBox.question(
            self,
            "휴지통 이동",
            "선택한 파일을 휴지통으로 이동할까요?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        for file_data in selected_files:
            response = self.cloud_client.move_to_trash(
                file_data["id"]
            )

            if response.get("status") != "success":
                QMessageBox.warning(
                    self,
                    "이동 실패",
                    response.get(
                        "message",
                        "휴지통 이동에 실패했습니다."
                    )
                )
                return

        # 테이블에서 체크된 행을 아래부터 제거합니다.
        for row in reversed(range(self.file_table.rowCount())):
            check_widget = self.file_table.cellWidget(row, 0)
            check_box = check_widget.findChild(QCheckBox)

            if check_box and check_box.isChecked():
                self.file_table.removeRow(row)

        self.trash_files.extend(selected_files)

        QMessageBox.information(
            self,
            "휴지통 이동",
            "선택한 파일을 휴지통으로 이동했습니다."
        )


class TrashWindow(QWidget):
    """휴지통 화면"""

    def __init__(self, cloud_client, trash_files, parent=None):
        super().__init__(parent)

        self.cloud_client = cloud_client
        self.trash_files = trash_files

        self.init_ui()
        self.load_trash_files()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("> 휴지통")
        title.setStyleSheet(
            "font-size: 14pt; font-weight: bold;"
        )
        layout.addWidget(title)

        self.permanent_delete_button = QPushButton(
            "영구 삭제"
        )
        self.permanent_delete_button.clicked.connect(
            self.delete_permanently
        )
        layout.addWidget(self.permanent_delete_button)

        self.trash_table = QTableWidget(0, 5)
        self.trash_table.setHorizontalHeaderLabels(
            ["선택", "파일명", "종류", "삭제일", "용량"]
        )

        self.trash_table.verticalHeader().setVisible(False)

        header = self.trash_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        self.trash_table.setColumnWidth(0, 50)

        layout.addWidget(self.trash_table)

    def load_trash_files(self):
        """휴지통 목록을 화면에 표시합니다."""

        self.trash_table.setRowCount(0)

        for file_data in self.trash_files:
            row = self.trash_table.rowCount()
            self.trash_table.insertRow(row)

            check_box = QCheckBox()
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)

            check_layout.setContentsMargins(0, 0, 0, 0)
            check_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            check_layout.addWidget(check_box)

            self.trash_table.setCellWidget(
                row,
                0,
                check_widget
            )

            self.trash_table.setItem(
                row,
                1,
                QTableWidgetItem(file_data["name"])
            )
            self.trash_table.setItem(
                row,
                2,
                QTableWidgetItem(file_data["type"])
            )
            self.trash_table.setItem(
                row,
                3,
                QTableWidgetItem(file_data["date"])
            )
            self.trash_table.setItem(
                row,
                4,
                QTableWidgetItem(file_data["size"])
            )

    def delete_permanently(self):
        """체크한 휴지통 파일을 완전히 삭제합니다."""

        rows_to_delete = []

        for row in range(self.trash_table.rowCount()):
            check_widget = self.trash_table.cellWidget(row, 0)
            check_box = check_widget.findChild(QCheckBox)

            if check_box and check_box.isChecked():
                rows_to_delete.append(row)

        if not rows_to_delete:
            QMessageBox.warning(
                self,
                "선택 필요",
                "영구 삭제할 파일을 체크해주세요."
            )
            return

        answer = QMessageBox.warning(
            self,
            "영구 삭제",
            "영구 삭제한 파일은 복구할 수 없습니다.\n계속할까요?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        for row in reversed(rows_to_delete):
            file_id = self.trash_files[row]["id"]

            response = self.cloud_client.delete_from_trash(
                file_id
            )

            if response.get("status") != "success":
                QMessageBox.warning(
                    self,
                    "삭제 실패",
                    response.get(
                        "message",
                        "영구 삭제에 실패했습니다."
                    )
                )
                return

            del self.trash_files[row]
            self.trash_table.removeRow(row)

        QMessageBox.information(
            self,
            "삭제 완료",
            "선택한 파일을 영구 삭제했습니다."
        )