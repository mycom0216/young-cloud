# client/ui/message_window.py
import sys
import os
from PySide6.QtCore import Qt, QStringListModel, QSettings, QTimer
from PySide6.QtGui import QFont, QIcon, QCursor, QColor, QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QDialog, QCompleter
)

# 상위 폴더 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
try:
    from network_client import NetworkClient
except ImportError:
    try:
        from client.network_client import NetworkClient
    except ImportError:
        NetworkClient = None
        
from dialog.message_dialog_ui import Ui_Form as Ui_MessageDialog

class MessageDialog(QDialog, Ui_MessageDialog):
    """
    [메시지 다이얼로그 창 클래스]
    - mode == 'view' : 받은 메시지 상세 확인 및 답장 모드
    - mode == 'sent_view' : 보낸 메시지 상세 확인 모드 (입력창 비활성화, 확인 버튼)
    - mode == 'send' : 신규 메시지 작성 모드 (관리자 여부에 따라 전체 전송/개별 전송 분기)
    """
    def __init__(self, mode='view', sender_email="", content="", current_user_email="", net_client=None, receiver_email="", is_admin=False, user_info=None):
        super().__init__()
        self.setupUi(self)
        
        self.mode = mode                  
        self.sender_email = sender_email  
        self.receiver_email = receiver_email
        self.current_user_email = current_user_email  
        self.net_client = net_client      
        
        if user_info:
            self.is_admin = bool(user_info.get("is_admin", user_info.get("IS_ADMIN", 0)))
        else:
            self.is_admin = bool(is_admin)
        
        self.settings = QSettings("YoungCloud", "MessageApp")
        
        # 💡 [핵심 수정] 기존 UI 파일의 QLineEdit을 여러 줄 입력이 가능한 QTextEdit으로 교체하여 줄바꿈 지원
        self.replace_line_edit_with_text_edit()
        
        self.init_dialog_ui(content)

    def replace_line_edit_with_text_edit(self):
        """기존 UI의 QLineEdit 위젯을 여러 줄 작성이 가능한 QTextEdit으로 교체합니다."""
        old_lineEdit = self.lineEdit
        parent_widget = old_lineEdit.parent()
        
        # 기존 QLineEdit의 기하학적 위치와 스타일 계승
        geometry = old_lineEdit.geometry()
        old_lineEdit.deleteLater()
        
        self.lineEdit = QTextEdit(parent_widget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(geometry)
        self.lineEdit.setFont(QFont("나눔스퀘어", 9))
        self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid #D0D8D2; border-radius: 4px;")

    def init_dialog_ui(self, content):
        if self.mode == 'view':
            self.setWindowTitle("받은 메시지 상세")
            self.label_title.setText("보낸메시지")                  
            
            if self.is_admin:
                self.label_2.setText(f"보낸 사람 : {self.sender_email} (관리자 전체 전송 모드)")
            else:
                self.label_2.setText(f"보낸 사람 : {self.sender_email}")  
            
            self.lineEdit.setPlainText(content)
            self.lineEdit.setReadOnly(True)                       
            
            self.pushButton_send.setText("답장")
            self.pushButton_send.clicked.connect(self.switch_to_reply_mode)
            
        elif self.mode == 'sent_view':
            self.setWindowTitle("보낸 메시지 상세")
            self.label_title.setText("보낸메시지")
            self.label_2.setText(f"받는 사람 : {self.receiver_email}")
            
            self.lineEdit.setPlainText(content)
            self.lineEdit.setReadOnly(True)                      
            
            self.pushButton_send.setText("확인")                 
            self.pushButton_send.clicked.connect(self.close)     

        elif self.mode == 'send':
            self.setWindowTitle("메시지 보내기")
            self.label_title.setText("보낸메시지")
            
            if self.is_admin:
                self.label_2.setText("받는 사람 : 전체 이용자")
            else:
                self.label_2.setText("받는 사람 : ")
                self.setup_receiver_input()
            
            # 서버에서 기본 메시지와 마무리 메시지를 불러와 자동 조합 (마무리 메시지는 줄바꿈 후 맨 아래 배치)
            auto_content = ""
            if self.net_client and self.current_user_email:
                try:
                    res = self.net_client.get_user_messages_config(self.current_user_email)
                    if res.get("status") == "success":
                        def_msg = res.get("default_message", "")
                        outro_msg = res.get("outro_message", "")
                        
                        parts = []
                        if def_msg: 
                            parts.append(def_msg)
                        parts.append("\n\n") # 본인 입력 공간 확보용 줄바꿈
                        if outro_msg: 
                            parts.append(outro_msg) # 마무리 메시지가 끝에 오도록 배치
                        auto_content = "".join(parts)
                except Exception as e:
                    print(f"[메시지 설정 로드 에러]: {e}")

            self.lineEdit.setPlainText(auto_content)
            self.lineEdit.setReadOnly(False)
            
            # 💡 [핵심 구현] DB 본문 제한(VARCHAR 1024)에 맞춘 실시간 글자 수 초과 감지 및 차단 연결
            self.lineEdit.textChanged.connect(self.check_message_length)
            
            self.pushButton_send.setText("보내기")
            self.pushButton_send.clicked.connect(self.confirm_and_send)

        self.pushButton_5.setText("닫기")
        self.pushButton_5.clicked.connect(self.close)

    def setup_receiver_input(self):
        self.receiver_input = QLineEdit(self)
        self.receiver_input.setGeometry(75, 58, 305, 25)
        self.receiver_input.setPlaceholderText("받는 사람 아이디(이메일) 입력")
        self.receiver_input.setStyleSheet(
            "background-color: rgb(255, 255, 255); "
            "border: 1px solid #D0D8D2; "
            "border-radius: 3px; "
            "font-size: 9pt;"
        )
        recent_contacts = self.load_recent_contacts()
        completer = QCompleter(recent_contacts, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.receiver_input.setCompleter(completer)

    def load_recent_contacts(self):
        key = f"recent_contacts_{self.current_user_email}"
        contacts = self.settings.value(key, [])
        if not isinstance(contacts, list):
            contacts = []
        return contacts

    def save_recent_contact(self, receiver_email):
        key = f"recent_contacts_{self.current_user_email}"
        contacts = self.load_recent_contacts()
        if receiver_email in contacts:
            contacts.remove(receiver_email)
        contacts.insert(0, receiver_email)
        contacts = contacts[:10]
        self.settings.setValue(key, contacts)

    def switch_to_reply_mode(self):
        self.label_title.setText("보낸메시지")
        
        if self.is_admin:
            self.label_2.setText("받는 사람 : 전체 이용자")
            receiver_target = "ALL"
        else:
            self.label_2.setText(f"받는 사람 : {self.sender_email}")
            receiver_target = self.sender_email

        self.lineEdit.clear()
        self.lineEdit.setReadOnly(False)
        self.pushButton_send.setText("보내기")
        self.pushButton_send.clicked.disconnect()
        self.pushButton_send.clicked.connect(lambda: self.send_message_process(receiver=receiver_target))

    def confirm_and_send(self):
        if self.is_admin:
            receiver = "ALL"
        else:
            receiver = self.receiver_input.text().strip()
            if not receiver:
                QMessageBox.warning(self, "경고", "받는 사람 아이디를 입력해주세요.")
                return
                
        self.send_message_process(receiver=receiver)

    def send_message_process(self, receiver):
        content = self.lineEdit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "경고", "메시지 내용을 입력해주세요.")
            return

        target_text = "전체 이용자" if self.is_admin else receiver
        reply = QMessageBox.question(
            self, "메시지 전송 확인", f"정말 [{target_text}]에게 메시지를 보낼까요?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.net_client:
                res = self.net_client.send_message(self.current_user_email, receiver, content)
                if res.get("status") == "success":
                    if not self.is_admin:
                        self.save_recent_contact(receiver)
                    QMessageBox.information(self, "성공", "메시지가 성공적으로 전송되었습니다.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "실패", res.get("message", "전송 실패"))
            else:
                if not self.is_admin:
                    self.save_recent_contact(receiver)
                QMessageBox.information(self, "성공", f"[{target_text}]에게 메시지 전송 완료!")
                self.accept()

    def check_message_length(self):
        """메시지 본문 글자 수가 1024자를 초과하는지 감시하고 초과 시 입력을 제한합니다."""
        text = self.lineEdit.toPlainText()
        if len(text) > 1024:
            # 1024자를 초과한 경우 경고 팝업 출력
            if not getattr(self, '_length_warning_shown', False):
                QMessageBox.warning(self, "입력 제한", "메시지 본문은 최대 1024자까지만 입력할 수 있습니다.")
                self._length_warning_shown = True
            
            # 1024자 이후의 입력은 강제로 잘라냄 (더 이상 입력 불가 처리)
            cursor = self.lineEdit.textCursor()
            pos = cursor.position()
            self.lineEdit.setPlainText(text[:1024])
            cursor.setPosition(min(pos, 1024))
            self.lineEdit.setTextCursor(cursor)
        else:
            self._length_warning_shown = False         


class MessageWidget(QWidget):
    """받은 메시지함 화면 위젯 클래스"""
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "user@example.com")
        self.net_client = NetworkClient() if NetworkClient else None
        print(f"[DEBUG] 전달받은 user_info: {self.user_info}")
        print(f"[DEBUG] 관리자 여부(is_admin): {self.user_info.get('is_admin')}")
        self.current_page = 0
        self.items_per_page = 20
        self.all_messages = []
        
        self.init_ui()
        self.load_messages()
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.load_messages)
        self.timer.start()
        
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)    
        
    def init_ui(self):
        self.setStyleSheet("background-color: #FFFFFF; font-family: '나눔스퀘어', 'Malgun Gothic', sans-serif;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        search_label = QLabel("아이디 검색")
        search_label.setStyleSheet("background-color: #EFF8F1; font-size: 12px; font-weight: bold; color: #333;")
        top_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색할 내용을 입력하세요...")
        self.search_input.setFixedHeight(30)
        self.search_input.setStyleSheet("border: 1px solid #D0D8D2; border-radius: 4px; padding-left: 5px; font-size: 10px;")
        top_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("검색")
        self.search_btn.setFixedSize(50, 30)
        self.search_btn.setStyleSheet("background-color: #63F2F2; color: #333; font-weight: bold; border-radius: 4px;")
        self.search_btn.clicked.connect(self.filter_messages)
        top_layout.addWidget(self.search_btn)

        top_layout.addStretch()

        self.delete_btn = QPushButton(" 삭제")
        self.delete_btn.setFixedSize(70, 30)
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        del_icon_path = os.path.join(base_path, "source", "image", "del.png")
        if os.path.exists(del_icon_path):
            self.delete_btn.setIcon(QIcon(del_icon_path))
        
        self.delete_btn.setStyleSheet("""
            QPushButton { background-color: #FFF; border: 1px solid #D0D8D2; border-radius: 4px; font-weight: bold; font-size: 10px; color: #333; }
            QPushButton:hover { background-color: #F5F5F5; }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_messages)
        top_layout.addWidget(self.delete_btn)
        main_layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "보낸사람", "내용", "받은 날짜"])
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: 1px solid #D0D8D2; gridline-color: #EFEFEF; font-size: 9pt; }
            QHeaderView::section { background-color: #EFF8F1; padding: 6px; border: none; font-weight: bold; font-size: 9pt; color: #333; }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 150)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 140)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_clicked)
        main_layout.addWidget(self.table)
        
        page_layout = QHBoxLayout()
        page_layout.addStretch()
        self.prev_btn = QPushButton("◀ 이전")
        self.prev_btn.setFixedSize(70, 28)
        self.prev_btn.clicked.connect(self.prev_page)
        page_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("1 / 1 페이지")
        page_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("다음 ▶")
        self.next_btn.setFixedSize(70, 28)
        self.next_btn.clicked.connect(self.next_page)
        page_layout.addWidget(self.next_btn)
        page_layout.addStretch()
        main_layout.addLayout(page_layout)

    def load_messages(self):
        messages = []
        if self.net_client:
            res = self.net_client.get_received_messages(self.user_email)
            if res.get("status") == "success":
                messages = res.get("messages", [])
        self.all_messages = messages
        self.update_table_view()
            
    def update_table_view(self):
        total_items = len(self.all_messages)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0: total_pages = 1
        if self.current_page >= total_pages: self.current_page = max(0, total_pages - 1)

        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_messages = self.all_messages[start_idx:end_idx]

        self.table.setRowCount(len(page_messages))
        self.page_label.setText(f"{self.current_page + 1} / {total_pages} 페이지")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        for row, msg in enumerate(page_messages):
            msg_id = msg.get("MESSAGE_ID")
            sender = msg.get("SENDER_EMAIL", "")
            content = msg.get("CONTENT", "")
            is_read = msg.get("IS_READ", False)
            date_str = msg.get("CREATED_AT", "")

            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, msg_id)
            self.table.setItem(row, 0, chk_item)

            font = QFont("나눔스퀘어", 9)
            font.setWeight(QFont.Black if not is_read else QFont.Normal)

            self.table.setItem(row, 1, QTableWidgetItem(str(sender)))
            self.table.setItem(row, 2, QTableWidgetItem(str(content)))
            self.table.setItem(row, 3, QTableWidgetItem(str(date_str)))
            # 1~3번 열의 폰트 및 읽음 여부에 따른 글자 색상 적용
            for c in range(1, 4):
                item = self.table.item(row, c)
                item.setFont(font)
                
                # 💡 [추가] 안 읽은 메시지(False)는 검은색, 읽은 메시지(True)는 회색으로 설정
                if is_read:
                    item.setForeground(QColor(128, 128, 128))  # 회색 (RGB: 128, 128, 128)
                else:
                    item.setForeground(QColor(0, 0, 0))        # 검은색
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table_view()

    def next_page(self):
        total_pages = (len(self.all_messages) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table_view()            
            
    def on_row_clicked(self, row, column):
        if column == 0: return
        actual_index = (self.current_page * self.items_per_page) + row
        if actual_index >= len(self.all_messages): return

        msg_data = self.all_messages[actual_index]
        msg_id = msg_data.get("MESSAGE_ID")
        sender = msg_data.get("SENDER_EMAIL")
        content = msg_data.get("CONTENT")
        is_read = msg_data.get("IS_READ", False)

        if not is_read and self.net_client:
            try:
                self.net_client.mark_message_read(msg_id)
            except Exception:
                pass

        # 💡 [수정] MessageDialog 호출 시 user_info 전달하여 관리자 권한 반영
        dialog = MessageDialog(mode='view', sender_email=sender, content=content, current_user_email=self.user_email, net_client=self.net_client, user_info=self.user_info)
        dialog.exec()
        self.load_messages()

    def filter_messages(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            if keyword in self.table.item(row, 1).text().lower() or keyword in self.table.item(row, 2).text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def delete_selected_messages(self):
        selected_ids = [self.table.item(r, 0).data(Qt.UserRole) for r in range(self.table.rowCount()) if self.table.item(r, 0).checkState() == Qt.Checked]
        if not selected_ids:
            QMessageBox.warning(self, "알림", "삭제할 메시지를 선택해주세요.")
            return
        if QMessageBox.question(self, "삭제 확인", "선택한 메시지를 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if self.net_client:
                self.net_client.delete_messages(selected_ids)
            self.load_messages()


class SentMessageWidget(QWidget):
    """보낸 메시지함 화면 위젯 클래스"""
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "user@example.com")
        self.net_client = NetworkClient() if NetworkClient else None
        
        self.current_page = 0
        self.items_per_page = 20
        self.all_messages = []
        
        self.init_ui()
        self.load_messages()
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.load_messages)
        self.timer.start()
        
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)    
        
    def init_ui(self):
        self.setStyleSheet("background-color: #FFFFFF; font-family: '나눔스퀘어', 'Malgun Gothic', sans-serif;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        search_label = QLabel("아이디 검색")
        search_label.setStyleSheet("background-color: #EFF8F1; font-size: 12px; font-weight: bold; color: #333;")
        top_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색할 내용을 입력하세요...")
        self.search_input.setFixedHeight(30)
        self.search_input.setStyleSheet("border: 1px solid #D0D8D2; border-radius: 4px; padding-left: 5px; font-size: 10px;")
        top_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("검색")
        self.search_btn.setFixedSize(50, 30)
        self.search_btn.setStyleSheet("background-color: #63F2F2; color: #333; font-weight: bold; border-radius: 4px;")
        self.search_btn.clicked.connect(self.filter_messages)
        top_layout.addWidget(self.search_btn)

        top_layout.addStretch()

        self.delete_btn = QPushButton(" 삭제")
        self.delete_btn.setFixedSize(70, 30)
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        del_icon_path = os.path.join(base_path, "source", "image", "del.png")
        if os.path.exists(del_icon_path):
            self.delete_btn.setIcon(QIcon(del_icon_path))
        
        self.delete_btn.setStyleSheet("""
            QPushButton { background-color: #FFF; border: 1px solid #D0D8D2; border-radius: 4px; font-weight: bold; font-size: 10px; color: #333; }
            QPushButton:hover { background-color: #F5F5F5; }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_messages)
        top_layout.addWidget(self.delete_btn)
        main_layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "받는사람", "내용", "보낸 날짜"])
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: 1px solid #D0D8D2; gridline-color: #EFEFEF; font-size: 9pt; }
            QHeaderView::section { background-color: #EFF8F1; padding: 6px; border: none; font-weight: bold; font-size: 9pt; color: #333; }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 150)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 140)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_clicked)
        main_layout.addWidget(self.table)
        
        page_layout = QHBoxLayout()
        page_layout.addStretch()
        self.prev_btn = QPushButton("◀ 이전")
        self.prev_btn.setFixedSize(70, 28)
        self.prev_btn.clicked.connect(self.prev_page)
        page_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("1 / 1 페이지")
        page_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("다음 ▶")
        self.next_btn.setFixedSize(70, 28)
        self.next_btn.clicked.connect(self.next_page)
        page_layout.addWidget(self.next_btn)
        page_layout.addStretch()
        main_layout.addLayout(page_layout)

    def load_messages(self):
        messages = []
        if self.net_client:
            res = self.net_client.get_sent_messages(self.user_email)
            if res.get("status") == "success":
                messages = res.get("messages", [])
        self.all_messages = messages
        self.update_table_view()
            
    def update_table_view(self):
        total_items = len(self.all_messages)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0: total_pages = 1
        if self.current_page >= total_pages: self.current_page = max(0, total_pages - 1)

        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_messages = self.all_messages[start_idx:end_idx]

        self.table.setRowCount(len(page_messages))
        self.page_label.setText(f"{self.current_page + 1} / {total_pages} 페이지")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        font = QFont("나눔스퀘어", 9)
        font.setWeight(QFont.Normal)

        for row, msg in enumerate(page_messages):
            msg_id = msg.get("MESSAGE_ID")
            receiver = msg.get("RECEIVER_EMAIL", "")
            content = msg.get("CONTENT", "")
            date_str = msg.get("CREATED_AT", "")

            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, msg_id)
            self.table.setItem(row, 0, chk_item)

            self.table.setItem(row, 1, QTableWidgetItem(str(receiver)))
            self.table.setItem(row, 2, QTableWidgetItem(str(content)))
            self.table.setItem(row, 3, QTableWidgetItem(str(date_str)))
            for c in range(1, 4):
                self.table.item(row, c).setFont(font)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table_view()

    def next_page(self):
        total_pages = (len(self.all_messages) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table_view()            
            
    def on_row_clicked(self, row, column):
        if column == 0: return
        actual_index = (self.current_page * self.items_per_page) + row
        if actual_index >= len(self.all_messages): return

        msg_data = self.all_messages[actual_index]
        receiver = msg_data.get("RECEIVER_EMAIL")
        content = msg_data.get("CONTENT")

        # 💡 [수정] MessageDialog 호출 시 user_info 전달하여 관리자 권한 반영
        dialog = MessageDialog(mode='sent_view', receiver_email=receiver, content=content, current_user_email=self.user_email, net_client=self.net_client, user_info=self.user_info)
        dialog.exec()
        self.load_messages()

    def filter_messages(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            if keyword in self.table.item(row, 1).text().lower() or keyword in self.table.item(row, 2).text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def delete_selected_messages(self):
        selected_ids = [self.table.item(r, 0).data(Qt.UserRole) for r in range(self.table.rowCount()) if self.table.item(r, 0).checkState() == Qt.Checked]
        if not selected_ids:
            QMessageBox.warning(self, "알림", "삭제할 메시지를 선택해주세요.")
            return
        if QMessageBox.question(self, "삭제 확인", "선택한 메시지를 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if self.net_client:
                self.net_client.delete_messages(selected_ids)
            self.load_messages()