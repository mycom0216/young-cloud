# -*- coding: utf-8 -*-
"""Figma 목업에 있는 보조 화면 위젯 모음.

화면별 클래스를 분리해 MainWindow에서 메뉴와 연결하기 쉽게 했습니다.
서버에 아직 해당 테이블/액션이 없는 기능은 사용자에게 안내하고,
NetworkClient가 연결되면 같은 요청 흐름으로 확장할 수 있습니다.
"""

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QCalendarWidget, QListWidget, QListWidgetItem, QMessageBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QComboBox
)


class BaseFeatureWidget(QWidget):
    """모든 보조 화면이 공통으로 사용하는 네트워크 요청 도우미."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(parent)
        self.user_info = user_info or {}
        self.net_client = net_client
        self.email = (self.user_info.get("email")
                      or self.user_info.get("user_id")
                      or self.user_info.get("EMAIL") or "")
        self.setStyleSheet("""
            QWidget { background-color: #EFF8F1; color: #222; font-size: 10pt; }
            QLineEdit, QTextEdit, QComboBox, QListWidget, QTableWidget {
                background-color: white; border: 1px solid #C8D8CC;
                border-radius: 4px; padding: 5px;
            }
            QPushButton {
                background-color: #63F2F2; border: none; border-radius: 5px;
                padding: 7px 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #48DADA; }
        """)

    def request(self, action, data=None):
        if not self.net_client:
            return {"status": "fail", "message": "네트워크 클라이언트가 연결되지 않았습니다."}
        return self.net_client.send_request(action, data or {})

    def title(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        return label


class ComposeMessageWidget(BaseFeatureWidget):
    """목업의 '메시지 보내기' 화면."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(user_info, net_client, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(self.title("> 메시지 보내기"))
        form = QFormLayout()
        self.receiver_edit = QLineEdit()
        self.receiver_edit.setPlaceholderText("받는 사람 이메일")
        self.title_edit = QLineEdit()
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("메시지 내용을 입력하세요.")
        form.addRow("받는 사람", self.receiver_edit)
        form.addRow("제목", self.title_edit)
        form.addRow("내용", self.content_edit)
        layout.addLayout(form)
        button_row = QHBoxLayout()
        button_row.addStretch()
        send_button = QPushButton("보내기")
        send_button.clicked.connect(self.send)
        button_row.addWidget(send_button)
        layout.addLayout(button_row)
        layout.addStretch()

    def send(self):
        receiver = self.receiver_edit.text().strip()
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        if not receiver or not content:
            QMessageBox.warning(self, "입력 확인", "받는 사람과 내용을 입력해주세요.")
            return
        response = self.request("message_send", {
            "sender": self.email, "receiver": receiver,
            "title": title, "content": content
        })
        if response.get("status") == "success":
            QMessageBox.information(self, "전송 완료", "메시지를 보냈습니다.")
            self.receiver_edit.clear()
            self.title_edit.clear()
            self.content_edit.clear()
        else:
            QMessageBox.warning(self, "전송 실패", response.get("message", "전송하지 못했습니다."))


class CalendarWidget(BaseFeatureWidget):
    """목업의 달력 화면. 날짜 선택과 일정 추가/삭제를 제공합니다."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(user_info, net_client, parent)
        self.events = {}
        layout = QVBoxLayout(self)
        layout.addWidget(self.title("> 달력"))
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.show_day_events)
        layout.addWidget(self.calendar)

        row = QHBoxLayout()
        self.event_edit = QLineEdit()
        self.event_edit.setPlaceholderText("선택한 날짜의 일정을 입력하세요")
        add_button = QPushButton("일정 추가")
        add_button.clicked.connect(self.add_event)
        row.addWidget(self.event_edit, 1)
        row.addWidget(add_button)
        layout.addLayout(row)
        self.event_list = QListWidget()
        layout.addWidget(self.event_list)
        self.show_day_events(self.calendar.selectedDate())

    def add_event(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        text = self.event_edit.text().strip()
        if not text:
            QMessageBox.warning(self, "입력 확인", "일정 내용을 입력해주세요.")
            return
        self.events.setdefault(date, []).append(text)
        self.event_edit.clear()
        self.show_day_events(self.calendar.selectedDate())

    def show_day_events(self, date):
        key = date.toString("yyyy-MM-dd")
        self.event_list.clear()
        for event in self.events.get(key, []):
            self.event_list.addItem(QListWidgetItem(event))


class ProfileSettingsWidget(BaseFeatureWidget):
    """목업의 개인정보 변경 화면."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(user_info, net_client, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(self.title("> 개인정보 변경"))
        form = QFormLayout()
        self.name_edit = QLineEdit(str(self.user_info.get("name", "")))
        self.company_edit = QLineEdit(str(self.user_info.get("company", "")))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("이름", self.name_edit)
        form.addRow("회사명", self.company_edit)
        form.addRow("새 비밀번호", self.password_edit)
        layout.addLayout(form)
        save_button = QPushButton("변경하기")
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def save(self):
        data = {
            "email": self.email,
            "name": self.name_edit.text().strip(),
            "company": self.company_edit.text().strip(),
            "password": self.password_edit.text()
        }
        response = self.request("user_update", data)
        if response.get("status") == "success":
            QMessageBox.information(self, "완료", "개인정보가 변경되었습니다.")
        else:
            QMessageBox.warning(self, "변경 실패", response.get("message", "변경하지 못했습니다."))


class MessageSettingsWidget(BaseFeatureWidget):
    """기본/마무리 메시지를 저장하는 설정 화면."""

    def __init__(self, user_info=None, net_client=None, mode="default", parent=None):
        super().__init__(user_info, net_client, parent)
        self.mode = mode
        layout = QVBoxLayout(self)
        label = "기본 메시지 설정" if mode == "default" else "마무리 메시지 설정"
        layout.addWidget(self.title(f"> {label}"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("자동으로 사용할 메시지를 입력하세요.")
        layout.addWidget(self.content_edit)
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def save(self):
        response = self.request("message_setting_update", {
            "email": self.email, "setting_type": self.mode,
            "content": self.content_edit.toPlainText().strip()
        })
        if response.get("status") == "success":
            QMessageBox.information(self, "저장 완료", "메시지 설정을 저장했습니다.")
        else:
            QMessageBox.warning(self, "저장 실패", response.get("message", "저장하지 못했습니다."))


class BlacklistWidget(BaseFeatureWidget):
    """목업의 블랙리스트 설정 화면."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(user_info, net_client, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(self.title("> 블랙리스트 설정"))
        row = QHBoxLayout()
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("차단할 아이디/이메일")
        add_button = QPushButton("차단")
        add_button.clicked.connect(self.add_user)
        row.addWidget(self.email_edit, 1)
        row.addWidget(add_button)
        layout.addLayout(row)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.load_users()

    def load_users(self):
        response = self.request("blacklist_list", {"email": self.email})
        if response.get("status") == "success":
            self.list_widget.clear()
            for item in response.get("users", []):
                self.list_widget.addItem(str(item.get("email", item)))

    def add_user(self):
        target = self.email_edit.text().strip()
        if not target:
            return
        response = self.request("blacklist_add", {"email": self.email, "target_email": target})
        if response.get("status") == "success":
            self.email_edit.clear()
            self.load_users()
        else:
            QMessageBox.warning(self, "차단 실패", response.get("message", "차단하지 못했습니다."))


class CloudSettingsWidget(BaseFeatureWidget):
    """목업의 클라우드 설정 화면."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(user_info, net_client, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(self.title("> 클라우드 설정"))
        form = QFormLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("기본 저장 폴더")
        self.auto_share = QComboBox()
        self.auto_share.addItems(["자동 공유 안 함", "업로드 시 공유"])
        form.addRow("저장 폴더", self.folder_edit)
        form.addRow("공유 설정", self.auto_share)
        layout.addLayout(form)
        save = QPushButton("저장")
        save.clicked.connect(self.save)
        layout.addWidget(save, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def save(self):
        response = self.request("cloud_setting_update", {
            "email": self.email,
            "folder": self.folder_edit.text().strip(),
            "auto_share": self.auto_share.currentText()
        })
        if response.get("status") == "success":
            QMessageBox.information(self, "저장 완료", "클라우드 설정을 저장했습니다.")
        else:
            QMessageBox.warning(self, "저장 실패", response.get("message", "저장하지 못했습니다."))


class AdminBanWidget(BaseFeatureWidget):
    """관리자 차단 설정 화면."""

    def __init__(self, user_info=None, net_client=None, parent=None):
        super().__init__(user_info, net_client, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(self.title("> 차단 설정"))
        row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("차단할 사용자 아이디")
        button = QPushButton("차단")
        button.clicked.connect(self.block_user)
        row.addWidget(self.search_edit, 1)
        row.addWidget(button)
        layout.addLayout(row)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["아이디", "상태"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def block_user(self):
        target = self.search_edit.text().strip()
        if not target:
            return
        response = self.request("admin_block_user", {"email": target})
        if response.get("status") == "success":
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(target))
            self.table.setItem(row, 1, QTableWidgetItem("차단됨"))
            self.search_edit.clear()
        else:
            QMessageBox.warning(self, "차단 실패", response.get("message", "차단하지 못했습니다."))
