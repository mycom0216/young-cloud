# client/ui/message_window.py
import sys
import os
from PySide6.QtCore import Qt, QStringListModel, QSettings, QTimer
from PySide6.QtGui import QFont, QIcon, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QDialog, QCompleter
)

# 상위 폴더 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from client.network_client import NetworkClient
except ImportError:
    NetworkClient = None

from dialog.message_dialog_ui import Ui_Form as Ui_MessageDialog

class MessageDialog(QDialog, Ui_MessageDialog):
    """
    [메시지 다이얼로그 창 클래스]
    - mode == 'view' : 받은 메시지 상세 내용을 확인하고 '답장'을 보낼 수 있는 모드 (reply.png 스타일)
    - mode == 'send' : 서브메뉴바에서 신규 메시지를 작성하여 보내는 모드 (send.png 스타일, 최근 아이디 자동완성 제공)
    """
    def __init__(self, mode='view', sender_email="", content="", current_user_email="", net_client=None):
        super().__init__()
        self.setupUi(self)
        
        # 기본 속성 바인딩
        self.mode = mode                  # 다이얼로그 모드 ('view' 또는 'send')
        self.sender_email = sender_email  # 받은 메시지인 경우 상대방 이메일
        self.current_user_email = current_user_email  # 현재 로그인한 유저 이메일
        self.net_client = net_client      # 서버 통신용 네트워크 클라이언트 객체
        
        # QSettings 초기화 (서버 DB 대신 클라이언트단 로컬 저장소에 최근 연락처 저장용)
        # 조직명("YoungCloud"), 애플리케이션명("MessageApp")을 기준으로 레지스트리/로컬 파일에 저장됨
        self.settings = QSettings("YoungCloud", "MessageApp")
        
        # UI 초기 설정 실행
        self.init_dialog_ui(content)

    def init_dialog_ui(self, content):
        """다이얼로그의 모드('view' vs 'send')에 따라 UI 텍스트, 입력창 상태, 버튼 동작을 분기 처리하는 함수"""
        
        if self.mode == 'view':
            # ==========================================
            # [루트 1] 받은 메시지 상세 확인 및 답장 모드
            # ==========================================
            self.setWindowTitle("받은 메시지 상세")
            self.label_title.setText("보낸메시지")                  # 타이틀 요구사항 반영
            self.label_2.setText(f"보낸 사람 : {self.sender_email}")  # 보낸 사람 표시
            
            self.lineEdit.setText(content)
            self.lineEdit.setReadOnly(True)                       # 상세 보기 시 본문 수정 불가(읽기 전용)
            
            self.pushButton_send.setText("답장")
            # '답장' 버튼 클릭 시 답장 입력 모드로 전환하는 함수 연결
            self.pushButton_send.clicked.connect(self.switch_to_reply_mode)
            
        elif self.mode == 'send':
            # ==========================================
            # [루트 2] 서브메뉴바를 통한 신규 메시지 보내기 모드
            # ==========================================
            self.setWindowTitle("메시지 보내기")
            self.label_title.setText("보낸메시지")
            self.label_2.setText("받는 사람 : ")
            
            # 받는 사람을 직접 입력할 수 있는 입력창 생성 및 최근 아이디 자동완성 컴포넌트 장착
            self.setup_receiver_input()
            
            self.lineEdit.clear()
            self.lineEdit.setReadOnly(False)                      # 메시지 작성 가능하도록 활성화
            self.lineEdit.setPlaceholderText("메시지를 입력하세요.")
            
            self.pushButton_send.setText("보내기")
            # '보내기' 버튼 클릭 시 전송 확인 팝업 및 전송 프로세스 연결
            self.pushButton_send.clicked.connect(self.confirm_and_send)

        # 공통 닫기 버튼 설정
        self.pushButton_5.setText("닫기")
        self.pushButton_5.clicked.connect(self.close)

    def setup_receiver_input(self):
        """받는 사람 입력용 QLineEdit 위젯을 동적으로 생성하고, QSettings에 저장된 최근 아이디 10개 자동완성(Completer)을 적용하는 함수"""
        # 받는 사람 입력 필드 생성 (label_2 우측 공간에 배치)
        self.receiver_input = QLineEdit(self)
        self.receiver_input.setGeometry(75, 58, 305, 25)
        self.receiver_input.setPlaceholderText("받는 사람 아이디(이메일) 입력")
        self.receiver_input.setStyleSheet(
            "background-color: rgb(255, 255, 255); "
            "border: 1px solid #D0D8D2; "
            "border-radius: 3px; "
            "font-size: 9pt;"
        )
        
        # 클라이언트 로컬(QSettings)에서 최근 주고받은 아이디 목록 불러오기
        recent_contacts = self.load_recent_contacts()
        
        # QCompleter를 생성하여 아이디 입력 시 자동완성 드롭다운 팝업 연동
        completer = QCompleter(recent_contacts, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)  # 대소문자 구분 없음
        self.receiver_input.setCompleter(completer)

    def load_recent_contacts(self):
        """클라이언트 로컬 저장소(QSettings)에서 현재 유저의 최근 대화 상대 아이디 리스트를 불러오는 함수"""
        # 사용자별로 독립된 키값 생성 (예: recent_contacts_user@example.com)
        key = f"recent_contacts_{self.current_user_email}"
        contacts = self.settings.value(key, [])
        
        # 데이터 타입이 리스트가 아닐 경우 안전하게 빈 리스트 반환
        if not isinstance(contacts, list):
            contacts = []
        return contacts

    def save_recent_contact(self, receiver_email):
        """메시지 전송 성공 시, 해당 수신자 아이디를 로컬 최근 목록에 추가하고 최대 10개까지만 유지하는 함수"""
        key = f"recent_contacts_{self.current_user_email}"
        contacts = self.load_recent_contacts()
        
        # 이미 목록에 존재하는 아이디라면 기존 위치에서 제거 후 맨 앞에 재추가 (최신순 정렬 유지)
        if receiver_email in contacts:
            contacts.remove(receiver_email)
        contacts.insert(0, receiver_email)
        
        # 최대 10개까지만 유지되도록 슬라이싱
        contacts = contacts[:10]
        
        # QSettings에 최신 목록 저장
        self.settings.setValue(key, contacts)

    def switch_to_reply_mode(self):
        """받은 메시지 상세 창('view')에서 '답장' 버튼을 눌렀을 때, 화면을 답장 작성 모드로 전환하는 함수"""
        self.label_title.setText("보낸메시지")
        self.label_2.setText(f"받는 사람 : {self.sender_email}")
        
        # 본문 입력창 초기화 및 수정 가능 상태로 변경
        self.lineEdit.clear()
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setPlaceholderText("답장 내용을 입력하세요.")
        
        # 버튼의 기능을 '보내기'로 변경하고 기존 시그널 연결 해제 후 새 프로세스 연결
        self.pushButton_send.setText("보내기")
        self.pushButton_send.clicked.disconnect()
        self.pushButton_send.clicked.connect(lambda: self.send_message_process(receiver=self.sender_email))

    def confirm_and_send(self):
        """서브메뉴바를 통한 전송 시, 입력된 받는 사람의 유효성을 검증하고 전송 프로세스로 진입하는 함수"""
        receiver = self.receiver_input.text().strip()
        
        # 받는 사람이 비어있는지 검증
        if not receiver:
            QMessageBox.warning(self, "경고", "받는 사람 아이디를 입력해주세요.")
            return
            
        self.send_message_process(receiver=receiver)

    def send_message_process(self, receiver):
        """'정말 메시지를 보낼까요?' 확인 큐메시지(QMessageBox)를 띄운 후, 최종 서버 전송 및 로컬 저장소를 업데이트하는 함수"""
        content = self.lineEdit.text().strip()
        
        # 메시지 내용이 비어있는지 검증
        if not content:
            QMessageBox.warning(self, "경고", "메시지 내용을 입력해주세요.")
            return

        # 사용자에게 전송 여부를 묻는 확인 창(QMessageBox) 출력
        reply = QMessageBox.question(
            self, 
            "메시지 전송 확인", 
            "정말 메시지를 보낼까요?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        # 사용자가 'Yes'를 누른 경우에만 전송 진행
        if reply == QMessageBox.Yes:
            if self.net_client:
                # 서버 네트워크 클라이언트를 통해 메시지 전송 요청
                res = self.net_client.send_message(self.current_user_email, receiver, content)
                if res.get("status") == "success":
                    # 전송 성공 시 클라이언트 로컬(QSettings)에 최근 연락처 저장
                    self.save_recent_contact(receiver)
                    
                    QMessageBox.information(self, "성공", "메시지가 성공적으로 전송되었습니다.")
                    self.accept()  # 다이얼로그 정상 종료
                else:
                    QMessageBox.warning(self, "실패", res.get("message", "전송 실패"))
            else:
                # 네트워크 클라이언트가 없는 오프라인/테스트 환경 시뮬레이션 처리
                self.save_recent_contact(receiver)
                QMessageBox.information(self, "성공", f"[{receiver}]에게 메시지 전송 완료!")
                self.accept()


class MessageWidget(QWidget):
    """메시지함(받은 메시지 목록) 화면 위젯 클래스"""
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}
        self.user_email = self.user_info.get("email", "user@example.com")
        self.net_client = NetworkClient() if NetworkClient else None
        
        self.init_ui()
        self.load_messages()
        # 💡 5초(5000ms)마다 load_messages를 자동 실행하는 타이머 설정
        self.timer = QTimer(self)
        self.timer.setInterval(5000)  # 5초 설정
        self.timer.timeout.connect(self.load_messages)
        self.timer.start()
        
    def closeEvent(self, event):
        """메시지 창/위젯이 닫힐 때 타이머를 정지하여 리소스 정리"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)    
        
    def init_ui(self):
        """화면 레이아웃 초기화"""
        self.setStyleSheet("background-color: #FFFFFF; font-family: '나눔스퀘어', 'Malgun Gothic', sans-serif;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 상단 컨트롤 영역 (검색 및 삭제 버튼)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        search_label = QLabel("아이디 검색")
        search_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #333;")
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
            QPushButton {
                background-color: #FFF;
                border: 1px solid #D0D8D2;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                color: #333;
            }
            QPushButton:hover { background-color: #F5F5F5; }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_messages)
        top_layout.addWidget(self.delete_btn)

        main_layout.addLayout(top_layout)

        # 메시지 테이블 위젯
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "보낸사람", "내용", "받은 날짜"])
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D0D8D2;
                gridline-color: #EFEFEF;
                font-size: 9pt;
            }
            QHeaderView::section {
                background-color: #EFF8F1;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 9pt;
                color: #333;
            }
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
        
        # 행 클릭 시 1번 루트(받은 메시지 상세 보기) 실행
        self.table.cellClicked.connect(self.on_row_clicked)

        main_layout.addWidget(self.table)

    def load_messages(self):
        """메시지 목록 로드"""
        messages = []
        if self.net_client:
            res = self.net_client.get_received_messages(self.user_email)
            if res.get("status") == "success":
                messages = res.get("messages", [])
        else:
            messages = [
                {"MESSAGE_ID": 1, "SENDER_EMAIL": "admin@cloud.com", "CONTENT": "환영합니다!", "IS_READ": False, "CREATED_AT": "2026-09-16 10:00:00"}
            ]

        self.table.setRowCount(len(messages))
        self.message_data_cache = messages

        for row, msg in enumerate(messages):
            msg_id = msg.get("MESSAGE_ID")
            sender = msg.get("SENDER_EMAIL", "")
            content = msg.get("CONTENT", "")
            is_read = msg.get("IS_READ", False)
            date_str = msg.get("CREATED_AT", "")

            # 0열: 체크박스
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, msg_id)
            self.table.setItem(row, 0, chk_item)

            # 공통 폰트 설정 (읽지 않았으면 볼드체)
            font = QFont("나눔스퀘어", 9)
            if not is_read:
                font.setBold(True)

            # 1열: 보낸사람
            item_sender = QTableWidgetItem(str(sender))
            item_sender.setFont(font)
            self.table.setItem(row, 1, item_sender)

            # 2열: 내용 (CONTENT)
            item_content = QTableWidgetItem(str(content))
            item_content.setFont(font)
            self.table.setItem(row, 2, item_content)

            # 3열: 받은 날짜
            item_date = QTableWidgetItem(str(date_str))
            item_date.setFont(font)
            self.table.setItem(row, 3, item_date)

            self.table.setItem(row, 1, QTableWidgetItem(sender)).setFont(font) if self.table.setItem(row, 1, QTableWidgetItem(sender)) else None
            # 위 코드 간결화 적용
            item_sender = QTableWidgetItem(sender); item_sender.setFont(font); self.table.setItem(row, 1, item_sender)
            item_content = QTableWidgetItem(content); item_content.setFont(font); self.table.setItem(row, 2, item_content)
            item_date = QTableWidgetItem(date_str); item_date.setFont(font); self.table.setItem(row, 3, item_date)

    def on_row_clicked(self, row, column):
        """[루트 1] 테이블 행 클릭 시 받은 메시지 상세 창 오픈"""
        if column == 0:
            return

        msg_data = self.message_data_cache[row]
        sender = msg_data.get("SENDER_EMAIL")
        content = msg_data.get("CONTENT")

        # mode='view'로 다이얼로그 생성
        dialog = MessageDialog(mode='view', sender_email=sender, content=content, current_user_email=self.user_email, net_client=self.net_client)
        if dialog.exec() == QDialog.Accepted:
            self.load_messages()

    def filter_messages(self):
        """검색 기능"""
        keyword = self.search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            if keyword in self.table.item(row, 1).text().lower() or keyword in self.table.item(row, 2).text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def delete_selected_messages(self):
        """선택 메시지 삭제"""
        selected_ids = [self.table.item(r, 0).data(Qt.UserRole) for r in range(self.table.rowCount()) if self.table.item(r, 0).checkState() == Qt.Checked]
        if not selected_ids:
            QMessageBox.warning(self, "알림", "삭제할 메시지를 선택해주세요.")
            return

        if QMessageBox.question(self, "삭제 확인", "선택한 메시지를 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if self.net_client:
                self.net_client.delete_messages(selected_ids)
            self.load_messages()