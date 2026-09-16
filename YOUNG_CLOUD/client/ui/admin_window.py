import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QDialog
)

# 기존에 존재하는 메시지 다이얼로그 UI 틀을 재사용하기 위해 임포트합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dialog.message_dialog_ui import Ui_Form as Ui_MessageDialog

class AdminUserDialog(QDialog, Ui_MessageDialog):
    """
    [관리자용 사용자 제한 및 정지 다이얼로그 클래스]
    - message_dialog_ui.py 양식을 활용하여 대상 유저를 정지하거나 해제합니다.
    """
    def __init__(self, user_email, is_banned, net_client):
        super().__init__()
        self.setupUi(self)
        
        self.user_email = user_email
        self.is_banned = is_banned  # True: 이미 차단된 상태, False: 정상 상태
        self.net_client = net_client
        
        self.init_custom_ui()

    def init_custom_ui(self):
        # 다이얼로그 창 제목 및 상단 타이틀 설정
        self.setWindowTitle("서비스 제한 및 정지")
        self.label_title.setText("서비스 제한 및 정지")
        
        # 대상 이용자 이메일 표시
        self.label_2.setText(f"대상 이용자 : {self.user_email}")
        
        # 입력창(lineEdit)에 현재 상태 안내 문구 표시 및 읽기 전용 설정
        self.lineEdit.setText(f"현재 상태: {'차단됨 (정지)' if self.is_banned else '정상 이용 중'}")
        self.lineEdit.setReadOnly(True)
        
        # 💡 이미 정지된 아이디라면 '차단해제하기', 아니면 '차단하기'로 버튼 문구 변경
        if self.is_banned:
            self.pushButton_send.setText("차단해제하기")
        else:
            self.pushButton_send.setText("차단하기")
            
        self.pushButton_send.clicked.connect(self.on_ban_action_clicked)
        
        self.pushButton_5.setText("닫기")
        self.pushButton_5.clicked.connect(self.close)

    def on_ban_action_clicked(self):
        """차단하기 또는 차단해제하기 버튼을 눌렀을 때 호출되는 함수"""
        if self.is_banned:
            # 이미 차단된 상태인 경우 해제 확인 큐메시지
            msg = f"\"{self.user_email}\"를 정말로 차단해제를 할까요?"
            new_ban_status = False
        else:
            # 정상 상태인 경우 정지 확인 큐메시지
            msg = f"\"{self.user_email}\"를 정말로 정지할까요?"
            new_ban_status = True
            
        # 확인/취소 팝업창 띄우기
        reply = QMessageBox.question(
            self, "상태 변경 확인", msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.net_client:
                # 서버로 변경 요청 전송
                res = self.net_client.admin_update_ban_status(self.user_email, new_ban_status)
                if res.get("status") == "success":
                    QMessageBox.information(self, "성공", res.get("message", "처리가 완료되었습니다."))
                    self.accept()  # 다이얼로그 닫기 및 성공 신호 전달
                else:
                    QMessageBox.warning(self, "실패", res.get("message", "요청 처리에 실패했습니다."))
            else:
                QMessageBox.information(self, "성공", "처리 완료 (테스트 모드)")
                self.accept()


class AdminServiceWidget(QWidget):
    """
    [관리자 모드: 서비스 제한 화면 메인 위젯]
    - 상단 아이디 검색창과 전체 유저 테이블을 관리합니다.
    """
    def __init__(self, net_client=None):
        super().__init__()
        self.net_client = net_client
        self.user_list = []  # 유저 데이터를 담아둘 리스트
        
        self.init_ui()
        self.load_users()

    def init_ui(self):
        self.setStyleSheet("background-color: #FFFFFF; font-family: '나눔스퀘어', 'Malgun Gothic', sans-serif;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. 상단 검색 영역 (아이디검색 레이블, 입력창, 검색 버튼)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        search_label = QLabel("아이디 검색")
        search_label.setStyleSheet("background-color: #EFF8F1; font-size: 12px; font-weight: bold; color: #333; padding: 4px;")
        top_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색할 아이디를 입력하세요...")
        self.search_input.setFixedHeight(30)
        self.search_input.setStyleSheet("border: 1px solid #D0D8D2; border-radius: 4px; padding-left: 5px; font-size: 11px;")
        self.search_input.returnPressed.connect(self.filter_users)  # 엔터 키 연동
        top_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("검색")
        self.search_btn.setFixedSize(50, 30)
        self.search_btn.setStyleSheet("background-color: #63F2F2; color: #333; font-weight: bold; border-radius: 4px;")
        self.search_btn.clicked.connect(self.filter_users)
        top_layout.addWidget(self.search_btn)

        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # 2. 테이블 위젯 설정 (체크박스 없음, 헤더: 이용자 아이디, 이름, 등급, 상태)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["이용자 아이디", "이름", "등급", "상태"])
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: 1px solid #D0D8D2; gridline-color: #EFEFEF; font-size: 9pt; }
            QHeaderView::section { background-color: #EFF8F1; padding: 6px; border: none; font-weight: bold; font-size: 9pt; color: #333; }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 130)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 110)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.setColumnWidth(3, 100)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 💡 테이블의 행(아이디가 있는 줄)을 클릭했을 때 이벤트 연결
        self.table.cellClicked.connect(self.on_row_clicked)
        
        main_layout.addWidget(self.table)

    def load_users(self):
        """서버로부터 전체 이용자 목록을 가져오는 함수"""
        users = []
        if self.net_client:
            res = self.net_client.admin_get_users()
            if res.get("status") == "success":
                users = res.get("users", [])
        self.user_list = users
        self.update_table_view(self.user_list)

    def update_table_view(self, users_to_display):
        """가져온 유저 데이터를 테이블 위젯에 그립니다."""
        self.table.setRowCount(len(users_to_display))
        
        for row, user in enumerate(users_to_display):
            email = user.get("EMAIL", "")
            name = user.get("NAME", "")
            grade = user.get("GRADE_NAME", "일반")
            is_banned = bool(user.get("IS_BANNED", False))
            
            status_str = "차단" if is_banned else "정상"
            
            item_email = QTableWidgetItem(str(email))
            item_name = QTableWidgetItem(str(name))
            item_grade = QTableWidgetItem(str(grade))
            item_status = QTableWidgetItem(str(status_str))
            
            # 상태에 따라 글자 색상 다르게 표시 (차단은 빨간색, 정상은 초록색)
            if is_banned:
                item_status.setForeground(Qt.red)
            else:
                item_status.setForeground(Qt.darkGreen)
                
            self.table.setItem(row, 0, item_email)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_grade)
            self.table.setItem(row, 3, item_status)

    def filter_users(self):
        """검색창 입력 키워드에 따라 유저 목록을 실시간 필터링합니다."""
        keyword = self.search_input.text().strip().lower()
        if not keyword:
            self.update_table_view(self.user_list)
            return
            
        filtered = [
            u for u in self.user_list 
            if keyword in u.get("EMAIL", "").lower() or keyword in u.get("NAME", "").lower()
        ]
        self.update_table_view(filtered)

    def on_row_clicked(self, row, column):
        """테이블의 행을 누르면 다이얼로그 창을 띄웁니다."""
        email_item = self.table.item(row, 0)
        status_item = self.table.item(row, 3)
        
        if not email_item:
            return
            
        target_email = email_item.text()
        is_banned = (status_item.text() == "차단")
        
        # 다이얼로그 실행
        dialog = AdminUserDialog(target_email, is_banned, self.net_client)
        result = dialog.exec()
        
        # 다이얼로그에서 변경을 완료하고 나왔다면 목록을 새로고침합니다.
        if result == QDialog.Accepted:
            self.load_users()