import os
import base64
from PySide6.QtCore import Qt, QSettings, Signal
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
    QInputDialog,
)


def format_file_size(size_bytes):
    """파일 크기(bytes)를 읽기 쉬운 단위(B, KB, MB, GB)로 변환하는 유틸리티 함수"""
    if size_bytes is None:
        return "0 B"
    try:
        size = float(size_bytes)
    except (ValueError, TypeError):
        return "0 B"

    if size < 1024:
        return f"{int(size)} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def get_file_type(file_name, is_folder=False):
    """파일명의 확장자 또는 폴더 여부를 기반으로 종류 텍스트를 반환하는 함수"""
    if is_folder:
        return "폴더"
    ext = os.path.splitext(file_name)[1].lower()
    if not ext:
        return "파일"
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
        return "이미지"
    elif ext in [".pdf", ".doc", ".docx", ".hwp", ".txt"]:
        return "문서"
    elif ext in [".zip", ".rar", ".7z", ".tar", ".gz"]:
        return "압축파일"
    elif ext in [".mp4", ".avi", ".mkv"]:
        return "동영상"
    elif ext in [".xls", ".xlsx", ".csv"]:
        return "스프레드시트"
    elif ext in [".ppt", ".pptx"]:
        return "프레젠테이션"
    return "파일"


class CloudClient:
    """클라우드 관련 서버 네트워크 요청을 총괄 처리하는 클라이언트 Helper 클래스"""

    def __init__(self, net_client=None, user_info=None):
        self.net_client = net_client
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "")

    def get_file_list(self, parent_folder_id=None):
        """서버 DB로부터 사용자의 실제 파일/폴더 목록 조회를 요청합니다."""
        if self.net_client and self.user_email:
            return self.net_client.send_request(
                "cloud_list_files",
                {
                    "email": self.user_email,
                    "parent_folder_id": parent_folder_id
                }
            )
        return {"status": "fail", "message": "네트워크 클라이언트 연결이 없거나 사용자 이메일이 설정되지 않았습니다."}

    def create_folder(self, folder_name, parent_folder_id=None):
        """서버에 새 폴더 생성을 요청합니다."""
        if self.net_client and self.user_email:
            return self.net_client.send_request(
                "cloud_create_folder",
                {
                    "email": self.user_email,
                    "folder_name": folder_name,
                    "parent_folder_id": parent_folder_id
                }
            )
        return {"status": "fail", "message": "서버 연결에 실패했습니다."}

    def upload_file(self, file_path, folder_id=None):
        """파일 바이너리를 Base64로 인코딩하여 서버로 전송합니다."""
        if not os.path.exists(file_path):
            return {"status": "fail", "message": "선택한 파일이 존재하지 않습니다."}

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                file_data_b64 = base64.b64encode(file_bytes).decode('utf-8')

            if self.net_client and self.user_email:
                return self.net_client.send_request(
                    "cloud_upload",
                    {
                        "email": self.user_email,
                        "file_name": file_name,
                        "file_size": file_size,
                        "file_data": file_data_b64,
                        "folder_id": folder_id
                    }
                )
        except Exception as e:
            return {"status": "fail", "message": f"파일 읽기 중 오류 발생: {str(e)}"}

        return {"status": "fail", "message": "서버와 연결할 수 없습니다."}

    def download_file(self, file_id, save_folder):
        """서버로부터 파일 바이너리를 인코딩 받아 선택된 로컬 폴더에 저장합니다."""
        if not self.net_client:
            return {"status": "fail", "message": "서버와 연결되어 있지 않습니다."}

        res = self.net_client.send_request("cloud_download", {"file_id": file_id})
        if res.get("status") == "success":
            file_info = res.get("file_data", {})
            file_name = file_info.get("file_name", "downloaded_file")
            b64_data = file_info.get("file_bytes_base64", "")

            try:
                # 💡 [추가] 경로에 폴더가 존재하지 않으면 자동으로 생성 (이미 존재해도 에러 안 남)
                os.makedirs(save_folder, exist_ok=True)
                file_bytes = base64.b64decode(b64_data)
                save_path = os.path.join(save_folder, file_name)
                with open(save_path, "wb") as f:
                    f.write(file_bytes)
                return {"status": "success", "message": f"{file_name} 다운로드 완료"}
            except Exception as e:
                return {"status": "fail", "message": f"파일 저장 실패: {str(e)}"}
        return res

    def move_to_trash(self, item_id, item_type="FILE"):
        """파일또는 폴더를 휴지통 상태로 변경합니다."""
        if self.net_client:
            return self.net_client.send_request("cloud_move_to_trash", {"item_id": item_id, "file_id": item_id, "item_type": item_type})
        return {"status": "fail", "message": "서버와 연결할 수 없습니다."}

    def restore_from_trash(self, item_id, item_type="FILE"):
        """휴지통의 파일 또는 폴더를 다시 정상 복원합니다."""
        if self.net_client:
            return self.net_client.send_request("cloud_restore", {"item_id": item_id, "file_id": item_id, "item_type": item_type})
        return {"status": "fail", "message": "서버와 연결할 수 없습니다."}

    def get_trash_files(self):
        """휴지통 내의 파일 목록을 조회합니다."""
        if self.net_client and self.user_email:
            return self.net_client.send_request("cloud_list_trash", {"email": self.user_email})
        return {"status": "fail", "message": "연결 오류"}

    def delete_from_trash(self, item_id, item_type="FILE"):
        """휴지통 내의 파일 또는 폴더를 완전 영구 삭제합니다."""
        if self.net_client:
            return self.net_client.send_request("cloud_delete_permanently", {"item_id": item_id, "file_id": item_id, "item_type": item_type})
        return {"status": "fail", "message": "서버와 연결할 수 없습니다."}


class FileTransferDialog(QDialog):
    """파일 올리기(업로드) / 파일 받기(다운로드) 팝업 다이얼로그"""

    def __init__(self, title, mode, cloud_client, files=None, folder_id=None, parent=None):
        super().__init__(parent)

        self.mode = mode
        self.cloud_client = cloud_client
        self.files = files or []
        self.folder_id = folder_id
        
        # 💡 클라이언트단 설정 조회를 위한 QSettings 초기화
        self.settings = QSettings("YoungCloud", "ClientApp")
        self.user_email = self.cloud_client.user_email

        self.setWindowTitle(title)
        self.resize(420, 450)

        self.setStyleSheet("""
            QDialog { background-color: #EFF8F1; }
            QLabel { font-size: 9pt; color: #222222; }
            QPushButton {
                background-color: #5CE4E3;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #42D2D1; }
            QLineEdit { background-color: white; border: 1px solid #CCCCCC; padding: 4px; }
            QTableWidget { background-color: white; border: 1px solid #D9D9D9; }
            QHeaderView::section { background-color: #D9D9D9; border: none; padding: 4px; font-size: 9pt; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(line)

        select_layout = QHBoxLayout()

        if self.mode == "upload":
            select_label = QLabel("올릴 파일 선택")
            self.path_edit = QLineEdit()
            self.path_edit.setReadOnly(True)
            self.path_edit.setPlaceholderText("선택한 파일이 표시됩니다")

            select_button = QPushButton("파일찾기")
            select_button.clicked.connect(self.select_files)
        else:
            select_label = QLabel("받을 폴더 선택")
            self.path_edit = QLineEdit()
            self.path_edit.setReadOnly(True)
            
            # 💡 [핵심] 설정에 저장된 다운로드 경로 불러와서 기본 적용
            default_download = os.path.join(os.path.expanduser("~"), "Downloads")
            saved_download_path = self.settings.value(f"download_path_{self.user_email}", default_download)
            self.path_edit.setText(saved_download_path)

            select_button = QPushButton("폴더선택")
            select_button.clicked.connect(self.select_download_folder)

        select_layout.addWidget(select_label)
        select_layout.addWidget(self.path_edit, 1)
        select_layout.addWidget(select_button)
        main_layout.addLayout(select_layout)

        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(["파일명", "상태", "크기"])
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        main_layout.addWidget(self.file_table)

        send_layout = QHBoxLayout()
        send_layout.addStretch()
        send_button = QPushButton("전송 시작")
        send_button.clicked.connect(self.start_transfer)
        send_layout.addWidget(send_button)
        send_layout.addStretch()
        main_layout.addLayout(send_layout)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.reject)
        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)

        if self.mode == "download":
            self.load_download_files()

    def select_files(self):
        """파일 찾기 시 기존 선택된 목록을 유지하며 새 파일들을 누적(Append)합니다."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "업로드할 파일 선택", "", "모든 파일 (*.*)"
        )
        if not file_paths:
            return

        # 중복 없는 새 파일만 self.files에 추가
        added_count = 0
        for path in file_paths:
            if path not in self.files:
                self.files.append(path)
                added_count += 1

        if added_count == 0:
            QMessageBox.information(self, "알림", "이미 목록에 추가된 파일입니다.")
            return

        # 경로 표시 줄 업데이트
        first_file_name = os.path.basename(self.files[0])
        if len(self.files) == 1:
            self.path_edit.setText(first_file_name)
        else:
            self.path_edit.setText(f"{first_file_name} 외 {len(self.files) - 1}개")

        # UI 테이블 새로고침
        self.load_upload_files()

    def select_download_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "다운로드 저장 폴더 선택")
        if folder_path:
            self.path_edit.setText(folder_path)

    def load_upload_files(self):
        self.file_table.setRowCount(0)
        for file_path in self.files:
            if not os.path.isfile(file_path):
                continue
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            self.file_table.setItem(row, 0, QTableWidgetItem(file_name))
            self.file_table.setItem(row, 1, QTableWidgetItem("대기"))
            self.file_table.setItem(row, 2, QTableWidgetItem(format_file_size(file_size)))

    def load_download_files(self):
        self.file_table.setRowCount(0)
        for file_data in self.files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            self.file_table.setItem(row, 0, QTableWidgetItem(file_data["name"]))
            self.file_table.setItem(row, 1, QTableWidgetItem("대기"))
            self.file_table.setItem(row, 2, QTableWidgetItem(file_data["size"]))

    def start_transfer(self):
        if self.mode == "upload":
            if not self.files:
                QMessageBox.warning(self, "선택 필요", "업로드할 파일을 선택하세요.")
                return

            all_success = True
            for row, file_path in enumerate(self.files):
                res = self.cloud_client.upload_file(file_path, folder_id=self.folder_id)
                if res.get("status") == "success":
                    self.file_table.setItem(row, 1, QTableWidgetItem("완료"))
                else:
                    self.file_table.setItem(row, 1, QTableWidgetItem("실패"))
                    all_success = False

            if all_success:
                QMessageBox.information(self, "성공", "선택한 모든 파일이 클라우드에 성공적으로 업로드되었습니다.")
                self.accept()
            else:
                QMessageBox.warning(self, "일부 실패", "일부 파일 업로드 중 오류가 발생했습니다.")
        else:
            save_folder = self.path_edit.text().strip()
            if not save_folder:
                QMessageBox.warning(self, "폴더 필요", "다운로드 받을 폴더를 선택하세요.")
                return

            all_success = True
            for row, file_data in enumerate(self.files):
                res = self.cloud_client.download_file(file_data["id"], save_folder)
                if res.get("status") == "success":
                    self.file_table.setItem(row, 1, QTableWidgetItem("완료"))
                else:
                    self.file_table.setItem(row, 1, QTableWidgetItem("실패"))
                    all_success = False

            if all_success:
                QMessageBox.information(self, "성공", f"파일 다운로드가 완료되었습니다.\n저장위치: {save_folder}")
                self.accept()
            else:
                QMessageBox.warning(self, "실패", "파일 다운로드 중 오류가 발생했습니다.")


class CloudWindow(QWidget):
    """사용자 파일함 클래스"""
    # 용량 변경 발생 알림 시그널 정의
    storage_updated = Signal()
    def __init__(self, net_client=None, user_info=None, parent=None):
        super().__init__(parent)

        self.net_client = net_client
        self.user_info = user_info or {}
        self.current_folder_id = None
        self.folder_history = []

        self.cloud_client = CloudClient(net_client=self.net_client, user_info=self.user_info)

        self.setStyleSheet("""
            QWidget { background-color: #EFF8F1; font-size: 10pt; }
            QTableWidget { background-color: white; border: 1px solid #D5DED8; }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #EEEEEE; }
            QPushButton {
                background-color: #63F2F2;
                border: none;
                border-radius: 5px;
                padding: 7px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45DCDC; }
            QPushButton#up_button {
                background-color: #A0E2E2;
            }
            QPushButton#up_button:hover {
                background-color: #82D1D1;
            }
        """)

        self.init_ui()
        self.load_file_list()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        self.title_label = QLabel("> 내 파일")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        button_layout = QHBoxLayout()
        self.up_button = QPushButton("⬆ 상위 폴더")
        self.up_button.setObjectName("up_button")
        self.create_folder_button = QPushButton("새 폴더")
        self.upload_button = QPushButton("파일 올리기")
        self.download_button = QPushButton("파일 받기")
        self.delete_button = QPushButton("삭제")

        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.create_folder_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(line)

        self.file_table = QTableWidget(0, 5)
        self.file_table.setHorizontalHeaderLabels(["선택", "파일명", "종류", "수정일", "용량"])
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.file_table.setColumnWidth(0, 50)
        self.file_table.setColumnWidth(2, 90)

        main_layout.addWidget(self.file_table)

        self.up_button.clicked.connect(self.go_to_parent_folder)
        self.create_folder_button.clicked.connect(self.open_create_folder_dialog)
        self.upload_button.clicked.connect(self.open_upload_dialog)
        self.download_button.clicked.connect(self.open_download_dialog)
        self.delete_button.clicked.connect(self.move_selected_to_trash)
        self.file_table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def load_file_list(self):
        response = self.cloud_client.get_file_list(parent_folder_id=self.current_folder_id)
        self.file_table.setRowCount(0)

        if response.get("status") == "success":
            user_name = response.get("user_name", self.user_info.get("name", "사용자"))
            comp_name = response.get("comp_name", self.user_info.get("comp", ""))

            base_title = f"> 내 파일 ({comp_name} / {user_name}님의 공간)" if comp_name else f"> 내 파일 ({user_name}님의 공간)"
            if self.folder_history:
                path_str = " / ".join([h[1] for h in self.folder_history])
                self.title_label.setText(f"{base_title} > {path_str}")
            else:
                self.title_label.setText(base_title)

            folders = response.get("folders", [])
            for f_data in folders:
                row = self.file_table.rowCount()
                self.file_table.insertRow(row)

                check_box = QCheckBox()
                check_widget = QWidget()
                check_layout = QHBoxLayout(check_widget)
                check_layout.setContentsMargins(0, 0, 0, 0)
                check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                check_layout.addWidget(check_box)
                self.file_table.setCellWidget(row, 0, check_widget)

                folder_id = f_data.get("FOLDER_ID")
                folder_name = f_data.get("FOLDER_NAME", "")
                created_at = f_data.get("CREATED_AT", "")

                name_item = QTableWidgetItem(f"📁 {folder_name}")
                name_item.setData(Qt.ItemDataRole.UserRole, folder_id)
                name_item.setData(Qt.ItemDataRole.UserRole + 1, "FOLDER")
                self.file_table.setItem(row, 1, name_item)

                self.file_table.setItem(row, 2, QTableWidgetItem(get_file_type(folder_name, is_folder=True)))
                self.file_table.setItem(row, 3, QTableWidgetItem(str(created_at)))
                self.file_table.setItem(row, 4, QTableWidgetItem("-"))

            files = response.get("files", [])
            for file_data in files:
                row = self.file_table.rowCount()
                self.file_table.insertRow(row)

                check_box = QCheckBox()
                check_widget = QWidget()
                check_layout = QHBoxLayout(check_widget)
                check_layout.setContentsMargins(0, 0, 0, 0)
                check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                check_layout.addWidget(check_box)
                self.file_table.setCellWidget(row, 0, check_widget)

                file_id = file_data.get("FILE_ID")
                file_name = file_data.get("FILE_NAME", "")
                file_size = file_data.get("FILE_SIZE", 0)
                uploaded_at = file_data.get("UPLOADED_AT", "")

                name_item = QTableWidgetItem(file_name)
                name_item.setData(Qt.ItemDataRole.UserRole, file_id)
                name_item.setData(Qt.ItemDataRole.UserRole + 1, "FILE")
                self.file_table.setItem(row, 1, name_item)

                self.file_table.setItem(row, 2, QTableWidgetItem(get_file_type(file_name)))
                self.file_table.setItem(row, 3, QTableWidgetItem(str(uploaded_at)))
                self.file_table.setItem(row, 4, QTableWidgetItem(format_file_size(file_size)))

    def open_create_folder_dialog(self):
        folder_name, ok = QInputDialog.getText(
            self, 
            "새 폴더 생성", 
            "생성할 폴더명을 입력하세요:"
        )
        if ok and folder_name.strip():
            res = self.cloud_client.create_folder(folder_name.strip(), parent_folder_id=self.current_folder_id)
            if res.get("status") == "success":
                QMessageBox.information(self, "성공", f"'{folder_name.strip()}' 폴더가 생성되었습니다.")
                self.load_file_list()
            else:
                QMessageBox.warning(self, "실패", res.get("message", "폴더 생성 중 오류가 발생했습니다."))

    def on_item_double_clicked(self, item):
        row = item.row()
        name_item = self.file_table.item(row, 1)
        if not name_item:
            return

        item_type = name_item.data(Qt.ItemDataRole.UserRole + 1)
        if item_type == "FOLDER":
            folder_id = name_item.data(Qt.ItemDataRole.UserRole)
            folder_name = name_item.text().replace("📁 ", "")

            self.folder_history.append((folder_id, folder_name))
            self.current_folder_id = folder_id
            self.load_file_list()

    def go_to_parent_folder(self):
        if not self.folder_history:
            QMessageBox.information(self, "안내", "현재 최상위(루트) 폴더입니다.")
            return

        self.folder_history.pop()
        if self.folder_history:
            self.current_folder_id = self.folder_history[-1][0]
        else:
            self.current_folder_id = None

        self.load_file_list()

    def open_upload_dialog(self):
        dialog = FileTransferDialog(
            title="파일 올리기",
            mode="upload",
            cloud_client=self.cloud_client,
            folder_id=self.current_folder_id,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.load_file_list()
            self.storage_updated.emit()  # 🔥 여기서 시그널을 발생시켜야 합니다.

    def open_download_dialog(self):
        selected_files = self.get_checked_items(target_type="FILE")
        if not selected_files:
            QMessageBox.warning(self, "선택 필요", "다운로드할 파일을 체크해주세요.")
            return

        dialog = FileTransferDialog(
            title="파일 받기",
            mode="download",
            cloud_client=self.cloud_client,
            files=selected_files,
            parent=self
        )
        dialog.exec()

    def get_checked_items(self, target_type=None):
        selected_items = []
        for row in range(self.file_table.rowCount()):
            check_widget = self.file_table.cellWidget(row, 0)
            if not check_widget:
                continue
            check_box = check_widget.findChild(QCheckBox)
            if not check_box or not check_box.isChecked():
                continue

            name_item = self.file_table.item(row, 1)
            item_type = name_item.data(Qt.ItemDataRole.UserRole + 1)

            if target_type is None or item_type == target_type:
                type_item = self.file_table.item(row, 2)
                date_item = self.file_table.item(row, 3)
                size_item = self.file_table.item(row, 4)

                selected_items.append({
                    "id": name_item.data(Qt.ItemDataRole.UserRole),
                    "name": name_item.text().replace("📁 ", ""),
                    "item_type": item_type,
                    "type": type_item.text(),
                    "date": date_item.text(),
                    "size": size_item.text(),
                })
        return selected_items

    def move_selected_to_trash(self):
        selected_items = self.get_checked_items()
        if not selected_items:
            QMessageBox.warning(self, "선택 필요", "휴지통으로 보낼 대상을 체크해주세요.")
            return

        answer = QMessageBox.question(
            self,
            "휴지통 이동",
            f"선택한 {len(selected_items)}개 항목을 휴지통으로 이동할까요?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        # 💡 [수정] item_type(FILE 또는 FOLDER) 정보를 서버에 함께 전달
        for item in selected_items:
            self.cloud_client.move_to_trash(item["id"], item_type=item["item_type"])

        QMessageBox.information(self, "완료", "선택한 항목이 휴지통으로 이동되었습니다.")
        self.load_file_list()
        self.storage_updated.emit()
    # def upload_file_success(self):
    #     """파일 업로드 성공 시 호출되는 콜백/메소드"""
    #     self.load_file_list()  # 기존 파일 목록 갱신
    #     self.storage_updated.emit()  # 🔥 사이드바 용량 갱신 시그널 발생

    # def permanent_delete_success(self):
    #     """파일 완전 삭제 성공 시 호출되는 콜백/메소드"""
    #     self.load_file_list()
    #     self.storage_updated.emit()  # 🔥 사이드바 용량 갱신 시그널 발생

class TrashWindow(QWidget):
    """휴지통 전용 화면 클래스"""
    storage_updated = Signal()
    
    def __init__(self, net_client=None, user_info=None, parent=None):
        super().__init__(parent)
        self.net_client = net_client
        self.user_info = user_info or {}
        self.cloud_client = CloudClient(net_client=self.net_client, user_info=self.user_info)

        self.setStyleSheet("""
            QWidget { background-color: #EFF8F1; font-size: 10pt; }
            QTableWidget { background-color: white; border: 1px solid #D5DED8; }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #EEEEEE; }
            QPushButton {
                background-color: #63F2F2;
                border: none;
                border-radius: 5px;
                padding: 7px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45DCDC; }
            QPushButton#permanent_delete_btn {
                background-color: #FF7B7B;
                color: white;
            }
            QPushButton#permanent_delete_btn:hover {
                background-color: #E85555;
            }
        """)

        self.init_ui()
        self.load_file_list()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("> 휴지통")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        button_layout = QHBoxLayout()
        self.restore_button = QPushButton("복원")
        self.permanent_delete_button = QPushButton("영구 삭제")
        self.permanent_delete_button.setObjectName("permanent_delete_btn")

        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.permanent_delete_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        self.trash_table = QTableWidget(0, 5)
        self.trash_table.setHorizontalHeaderLabels(["선택", "파일명", "종류", "삭제일", "용량"])
        self.trash_table.verticalHeader().setVisible(False)
        self.trash_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.trash_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.trash_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.trash_table.setColumnWidth(0, 50)
        self.trash_table.setColumnWidth(2, 90)

        layout.addWidget(self.trash_table)

        self.restore_button.clicked.connect(self.restore_selected)
        self.permanent_delete_button.clicked.connect(self.delete_permanently)

    def load_file_list(self):
        """휴지통 내의 폴더 및 파일 목록 조회 및 출력"""
        response = self.cloud_client.get_trash_files()
        self.trash_table.setRowCount(0)

        if response.get("status") == "success":
            # 휴지통 내 폴더 출력
            folders = response.get("folders", [])
            for f_data in folders:
                row = self.trash_table.rowCount()
                self.trash_table.insertRow(row)

                check_box = QCheckBox()
                check_widget = QWidget()
                check_layout = QHBoxLayout(check_widget)
                check_layout.setContentsMargins(0, 0, 0, 0)
                check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                check_layout.addWidget(check_box)
                self.trash_table.setCellWidget(row, 0, check_widget)

                folder_id = f_data.get("FOLDER_ID")
                folder_name = f_data.get("FOLDER_NAME", "")
                created_at = f_data.get("CREATED_AT", "")

                item = QTableWidgetItem(f"📁 {folder_name}")
                item.setData(Qt.ItemDataRole.UserRole, folder_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, "FOLDER")

                self.trash_table.setItem(row, 1, item)
                self.trash_table.setItem(row, 2, QTableWidgetItem("폴더"))
                self.trash_table.setItem(row, 3, QTableWidgetItem(str(created_at)))
                self.trash_table.setItem(row, 4, QTableWidgetItem("-"))

            # 휴지통 내 파일 출력
            files = response.get("files", response.get("file_list", []))
            for file_data in files:
                row = self.trash_table.rowCount()
                self.trash_table.insertRow(row)

                check_box = QCheckBox()
                check_widget = QWidget()
                check_layout = QHBoxLayout(check_widget)
                check_layout.setContentsMargins(0, 0, 0, 0)
                check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                check_layout.addWidget(check_box)
                self.trash_table.setCellWidget(row, 0, check_widget)

                file_id = file_data.get("FILE_ID")
                file_name = file_data.get("FILE_NAME", "")
                file_size = file_data.get("FILE_SIZE", 0)
                uploaded_at = file_data.get("UPLOADED_AT", file_data.get("CREATED_AT", ""))

                item = QTableWidgetItem(file_name)
                item.setData(Qt.ItemDataRole.UserRole, file_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, "FILE")

                self.trash_table.setItem(row, 1, item)
                self.trash_table.setItem(row, 2, QTableWidgetItem(get_file_type(file_name)))
                self.trash_table.setItem(row, 3, QTableWidgetItem(str(uploaded_at)))
                self.trash_table.setItem(row, 4, QTableWidgetItem(format_file_size(file_size)))

    def get_checked_items(self):
        """휴지통 테이블에서 체크박스가 선택된 정보 추출"""
        selected_items = []
        for row in range(self.trash_table.rowCount()):
            check_widget = self.trash_table.cellWidget(row, 0)
            if not check_widget:
                continue
            check_box = check_widget.findChild(QCheckBox)
            if not check_box or not check_box.isChecked():
                continue

            item = self.trash_table.item(row, 1)
            if item:
                # 💡 [수정] KeyError 예외 방지를 위해 item_type 정보 추출 구문 추가
                selected_items.append({
                    "id": item.data(Qt.ItemDataRole.UserRole),
                    "item_type": item.data(Qt.ItemDataRole.UserRole + 1),
                    "name": item.text()
                })
        return selected_items

    def restore_selected(self):
        """선택된 항목(파일/폴더) 복원"""
        selected_items = self.get_checked_items()
        if not selected_items:
            QMessageBox.warning(self, "선택 필요", "복원할 항목을 체크해주세요.")
            return

        all_success = True
        for item in selected_items:
            res = self.cloud_client.restore_from_trash(item["id"], item_type=item["item_type"])
            if res.get("status") != "success":
                all_success = False

        if all_success:
            QMessageBox.information(self, "복원 완료", f"선택한 {len(selected_items)}개 항목이 복원되었습니다.")
        else:
            QMessageBox.warning(self, "일부 실패", "일부 항목 복원 중 오류가 발생했습니다.")

        self.load_file_list()
        # 💡 복원 시 사이드바 용량 갱신 시그널 발생
        self.storage_updated.emit()

    def delete_permanently(self):
        """선택된 항목(파일/폴더) 영구 삭제"""
        selected_items = self.get_checked_items()
        if not selected_items:
            QMessageBox.warning(self, "선택 필요", "영구 삭제할 항목을 체크해주세요.")
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("영구 삭제 확인")
        msg_box.setText(f"선택한 {len(selected_items)}개 항목을 진짜 지우시겠습니까?\n영구 삭제된 항목은 복구할 수 없습니다.")
        msg_box.setIcon(QMessageBox.Icon.Warning)

        confirm_btn = msg_box.addButton("확인", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("취소", QMessageBox.ButtonRole.RejectRole)
        msg_box.setDefaultButton(cancel_btn)

        msg_box.exec()

        if msg_box.clickedButton() != confirm_btn:
            return

        all_success = True
        for item in selected_items:
            res = self.cloud_client.delete_from_trash(item["id"], item_type=item["item_type"])
            if res.get("status") != "success":
                all_success = False

        if all_success:
            QMessageBox.information(self, "완료", "선택한 항목이 영구 삭제되었습니다.")
        else:
            QMessageBox.warning(self, "일부 실패", "일부 항목 영구 삭제 중 오류가 발생했습니다.")

        self.load_file_list()
        # 💡 영구 삭제 완료 시 사이드바 용량 갱신 시그널 발생
        self.storage_updated.emit()