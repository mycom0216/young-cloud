# -*- coding: utf-8 -*-
"""메시지함 화면: 받은 메시지 목록, 검색, 삭제, 읽음 처리, 답장."""
import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QTextEdit, QDialogButtonBox, QFormLayout, QAbstractItemView)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.dirname(CURRENT_DIR)
if CLIENT_DIR not in sys.path:
    sys.path.append(CLIENT_DIR)


class MessageComposeDialog(QDialog):
    """Designer UI가 없어도 실행 가능한 기본 메시지 작성 팝업."""
    def __init__(self, parent=None, receiver="", title="", content=""):
        super().__init__(parent)
        self.setWindowTitle("메시지 보내기")
        self.resize(430, 300)
        form = QFormLayout(self)
        self.receiver_edit = QLineEdit(receiver)
        self.title_edit = QLineEdit(title)
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(content)
        form.addRow("받는 사람 아이디", self.receiver_edit)
        form.addRow("제목", self.title_edit)
        form.addRow("내용", self.content_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        return (self.receiver_edit.text().strip(), self.title_edit.text().strip(),
                self.content_edit.toPlainText().strip())


class MessageWidget(QWidget):
    """MainWindow의 content_stack에 넣어 사용하는 메시지 위젯."""
    def __init__(self, user_info=None, net_client=None, parent=None, message_action="message_received"):
        super().__init__(parent)
        self.user_info = user_info or {}
        self.net_client = net_client
        self.messages = []
        self.message_action = message_action
        self.messages_title = "보낸 메시지" if message_action == "message_sent" else "받은 메시지"
        self.user_email = (self.user_info.get("email") or self.user_info.get("user_id")
                           or self.user_info.get("EMAIL") or "")
        self.setStyleSheet("QWidget { background-color: white; font-size: 9pt; }")
        self._build_ui()
        self.load_messages()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("아이디 검색"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("보낸 사람 아이디를 입력하세요")
        self.search_edit.returnPressed.connect(self.search_messages)
        search_layout.addWidget(self.search_edit, 1)
        search_button = QPushButton("검색")
        search_button.clicked.connect(self.search_messages)
        search_layout.addWidget(search_button)
        delete_button = QPushButton("삭제")
        # del.png가 있으면 아이콘을 적용하고, 없으면 글자 버튼으로 표시합니다.
        delete_icon = os.path.join(CURRENT_DIR, "source", "image", "del.png")
        if os.path.exists(delete_icon):
            delete_button.setIcon(QIcon(delete_icon))
        delete_button.clicked.connect(self.delete_checked_messages)
        search_layout.addWidget(delete_button)
        root.addLayout(search_layout)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["선택", "보낸 사람", "제목 - 내용", "받은 날짜"])
        self.table.setFont(QFont("맑은 고딕", 9))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 45)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellClicked.connect(self._cell_clicked)
        root.addWidget(self.table, 1)

    def _request(self, action, data):
        if not self.net_client:
            return {"status": "fail", "message": "네트워크 클라이언트가 연결되지 않았습니다."}
        return self.net_client.send_request(action, data)

    def load_messages(self):
        response = self._request(self.message_action, {"email": self.user_email})
        if response.get("status") == "success":
            self.messages = response.get("messages", [])
            self._fill_table(self.messages)
        elif response.get("message"):
            self.table.setRowCount(0)
            QMessageBox.warning(self, "메시지 조회 실패", response["message"])

    def _fill_table(self, messages):
        self.table.setRowCount(0)
        for message in messages:
            row = self.table.rowCount()
            self.table.insertRow(row)
            check = QTableWidgetItem()
            check.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            check.setCheckState(Qt.CheckState.Unchecked)
            self.table.setItem(row, 0, check)
            sender = message.get("sender_name") or message.get("sender") or ""
            title = message.get("title") or "(제목 없음)"
            content = (message.get("content") or "").replace("\n", " ")
            preview = content if len(content) <= 55 else content[:55] + "..."
            date = message.get("received_at") or message.get("date") or ""
            sender_item = QTableWidgetItem(str(sender))
            subject_item = QTableWidgetItem(f"{title} - {preview}")
            date_item = QTableWidgetItem(str(date)[:19])
            for item in (sender_item, subject_item, date_item):
                item.setData(Qt.ItemDataRole.UserRole, message)
            # 제목은 읽음 여부와 관계없이 항상 굵게 표시합니다.
            title_font = QFont()
            title_font.setBold(True)
            subject_item.setFont(title_font)

            # 읽지 않은 메시지는 보낸 사람과 날짜도 함께 굵게 표시합니다.
            unread = message.get("is_read", message.get("read", 0)) in (0, False, "0", "N", "n")
            if unread:
                unread_font = QFont()
                unread_font.setBold(True)
                sender_item.setFont(unread_font)
                date_item.setFont(unread_font)
            self.table.setItem(row, 1, sender_item)
            self.table.setItem(row, 2, subject_item)
            self.table.setItem(row, 3, date_item)

    def _cell_clicked(self, row, column):
        # 첫 번째 열은 체크박스이므로 클릭해도 상세창을 열지 않습니다.
        if column != 0:
            self.open_message(row, column)

    def search_messages(self):
        keyword = self.search_edit.text().strip().lower()
        if not keyword:
            self._fill_table(self.messages)
            return
        self._fill_table([m for m in self.messages
                          if keyword in str(m.get("sender", "")).lower()
                          or keyword in str(m.get("sender_name", "")).lower()])

    def _message_id_from_row(self, row):
        item = self.table.item(row, 1) or self.table.item(row, 2)
        message = item.data(Qt.ItemDataRole.UserRole) if item else {}
        return message.get("id") or message.get("message_id")

    def delete_checked_messages(self):
        ids = [self._message_id_from_row(row) for row in range(self.table.rowCount())
               if self.table.item(row, 0).checkState() == Qt.CheckState.Checked]
        ids = [message_id for message_id in ids if message_id is not None]
        if not ids:
            QMessageBox.information(self, "안내", "삭제할 메시지를 선택해주세요.")
            return
        response = self._request("message_delete", {"email": self.user_email, "message_ids": ids})
        if response.get("status") == "success":
            self.load_messages()
        else:
            QMessageBox.warning(self, "삭제 실패", response.get("message", "삭제하지 못했습니다."))

    def open_message(self, row, _column):
        item = self.table.item(row, 1) or self.table.item(row, 2)
        message = item.data(Qt.ItemDataRole.UserRole) if item else {}
        if not message:
            return
        message_id = message.get("id") or message.get("message_id")
        if message_id is not None:
            self._request("message_mark_read", {"email": self.user_email, "message_id": message_id})
        dialog = MessageComposeDialog(self, receiver=message.get("sender", ""),
                                      title="Re: " + str(message.get("title", "")))
        dialog.setWindowTitle("받은 메시지")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            receiver, title, content = dialog.values()
            if not receiver or not content:
                QMessageBox.warning(self, "입력 확인", "받는 사람과 내용을 입력해주세요.")
                return
            response = self._request("message_send", {
                "sender": self.user_email, "receiver": receiver,
                "title": title, "content": content})
            if response.get("status") == "success":
                QMessageBox.information(self, "전송 완료", "메시지를 보냈습니다.")
            else:
                QMessageBox.warning(self, "전송 실패", response.get("message", "메시지를 보내지 못했습니다."))
        self.load_messages()
