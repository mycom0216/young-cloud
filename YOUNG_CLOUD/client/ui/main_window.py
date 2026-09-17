import os
import sys

# 모듈 경로 호환 임포트 (ui 하위 디렉토리 및 루트 디렉토리 동시 대응)
try:
    from ui.cloud_window import CloudWindow, TrashWindow
except ImportError:
    from cloud_window import CloudWindow, TrashWindow

from network_client import NetworkClient
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QListWidget,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QProgressBar,
    QFrame
)

from dialog.home_widget import HomeWidget
from dialog.home_widget import CalenderWidget
from settings_window import ServiceSettingWidget, UserInfoSettingWidget, DefaultMessageSettingWidget, OutroMessageSettingWidget
from message_window import MessageWidget, MessageDialog, SentMessageWidget
from admin_window import AdminServiceWidget


# 개발 중인 메뉴 안내용 플레이스홀더 클래스
class PlaceholderView(QWidget):
    def __init__(self, menu_name):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(f"'{menu_name}' 화면은 팀원이 개발 중입니다. 🚧")
        label.setStyleSheet("font-size: 15px; color: #555; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.setWindowTitle("Young Cloud Desktop App")
        self.resize(1100, 750)
        self.user_info = user_info or {}
        self.user_name = self.user_info.get("name", "사용자")
        
        # 메인 윈도우에서 사용할 공용 네트워크 클라이언트 초기화
        self.net_client = NetworkClient()
        
        # 관리자 여부 확인 (소문자/대문자 키값 수용)
        self.is_admin = bool(
            self.user_info.get("is_admin", False) or 
            self.user_info.get("IS_ADMIN", False)
        )

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 좌측 사이드바 영역 생성 및 추가
        self.init_sidebar(main_layout)
        main_layout.addWidget(self.sidebar)

        # 2. 좌측 서브메뉴 영역 생성 및 추가
        self.init_submenu(main_layout)
        main_layout.addWidget(self.submenu_container)

        # 3. 서브메뉴와 메인컨텐츠 사이 세로 구분선
        self.vertical_line = QFrame()
        self.vertical_line.setFrameShape(QFrame.VLine)
        self.vertical_line.setFrameShadow(QFrame.Sunken)
        self.vertical_line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.vertical_line.setStyleSheet("background-color: #C5D2C7; border: none;")
        self.vertical_line.setFixedWidth(2)
        main_layout.addWidget(self.vertical_line)

        # 4. 메인 컨텐츠 영역 생성 및 추가
        self.init_content_area(main_layout)
        main_layout.addWidget(self.content_area, stretch=1)

    def init_sidebar(self, parent_layout):
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("""
            QWidget { background-color: #9CBF1F; }
            QToolButton {
                background-color: transparent;
                border: none;
                color: #333333;
                font-weight: bold;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }
        """)
        self.sidebar.setFixedWidth(130)

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(20)

        profile_label = QLabel(f"       {self.user_name}님")
        profile_label.setStyleSheet("color: black; font-weight: bold; font-size: 13px; background: transparent;")
        layout.addWidget(profile_label)

        layout.addSpacing(20)
        logo_label = QLabel()
        logo_path = os.path.join(self.base_path, "source", "image", "YOUNG CLOUD.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(100, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("YOUNG CLOUD")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px;")

        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        layout.addSpacing(50)

        if self.is_admin:
            menus = [
                ("HOME", "home.png", lambda: self.change_submenu(0)),
                ("메시지", "message.png", lambda: self.change_submenu(1)),
                ("차단설정", "settings.png", lambda: self.change_submenu(2)),
            ]
        else:
            menus = [
                ("HOME", "home.png", lambda: self.change_submenu(0)),
                ("캘린더", "calendar.png", lambda: self.change_submenu(1)),
                ("클라우드", "cloud.png", lambda: self.change_submenu(2)),
                ("메시지", "message.png", lambda: self.change_submenu(3)),
                ("설정", "settings.png", lambda: self.change_submenu(4)),
            ]

        self.menu_buttons = []
        for name, icon_filename, callback in menus:
            btn = QToolButton()
            btn.setText(name)

            icon_path = os.path.join(self.base_path, "source", "image", icon_filename)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(32, 32))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(65)
            btn.clicked.connect(callback)

            layout.addWidget(btn)
            self.menu_buttons.append(btn)

        layout.addStretch()

        logout_btn = QPushButton("로그아웃")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #63F2F2;
                color: #333333;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #66E4F2; }
        """)
        logout_btn.setMinimumHeight(35)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        parent_layout.addWidget(self.sidebar)

    def logout(self):
        """로그아웃 처리: 로그인 창으로 이동"""
        try:
            from login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
        except Exception as e:
            print(f"[로그아웃] 이동 중 오류 발생: {e}")
        self.close()

    def init_submenu(self, parent_layout):
        self.submenu_container = QWidget()
        self.submenu_container.setStyleSheet("background-color: #EFF8F1;")
        self.submenu_container.setFixedWidth(180)

        layout = QVBoxLayout(self.submenu_container)
        layout.setContentsMargins(15, 20, 15, 20)

        storage_layout = QVBoxLayout()
        storage_layout.setSpacing(5)

        # 용량 및 등급 텍스트 라벨 (self. 붙여서 속성으로 지정)
        self.storage_label = QLabel("0MB | 일반")
        self.storage_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #333; background: transparent;")
        storage_layout.addWidget(self.storage_label)
        

        # 💡 [핵심 수정] self.을 반드시 붙여야 클래스 전체에서 인식할 수 있습니다!
        self.storage_progress_bar = QProgressBar()
        self.storage_progress_bar.setValue(0)
        self.storage_progress_bar.setTextVisible(False)
        self.storage_progress_bar.setFixedHeight(6)
        self.storage_progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #DCE5DE;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #63F2F2;
                border-radius: 3px;
            }
        """)
        storage_layout.addWidget(self.storage_progress_bar)

        layout.addLayout(storage_layout)
        
        # 서버로부터 사용자 용량 및 등급 정보를 불러와서 사이드바 UI 업데이트 실행
        self.load_and_update_storage_info()
        
        # 💡 [추가] 용량 게이지와 서브메뉴 사이의 간격 및 가로선(구분선) 배치
        layout.addSpacing(4)

        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #D0D8D2;")  # 연한 회록색 계열 선 색상
        layout.addWidget(line)

        layout.addSpacing(8)

        self.submenu_stack = QStackedWidget()
        self.submenu_stack.setStyleSheet("background: transparent;")

        if self.is_admin:
            menu_titles = ["HOME", "메시지", "차단설정"]
        else:
            menu_titles = ["HOME", "캘린더", "클라우드", "메시지", "설정"]

        for i, title in enumerate(menu_titles):
            page = QWidget()
            p_layout = QVBoxLayout(page)
            p_layout.setContentsMargins(0, 0, 0, 0)

            title_label = QLabel(f"> {title}")
            title_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333;")
            p_layout.addWidget(title_label)

            p_layout.addSpacing(10)
            
    
            sub_list = QListWidget()
            sub_list.setStyleSheet("""
                QListWidget {
                    background-color: transparent;
                    border: none;
                    font-size: 13px;
                    color: #444444;
                }
                QListWidget::item { padding: 8px; border-radius: 4px; }
                QListWidget::item:selected {
                    background-color: #D6E8DB;
                    color: #000000;
                    font-weight: bold;
                }
            """)

            if self.is_admin:
                items = ["홈 메인"] if i == 0 else ["보낸메시지", "메시지 보내기"] if i == 1 else ["서비스제한"]
            else:
                if i == 0:
                    items = ["홈 메인"]
                elif i == 1:
                    items = ["달력보기"]
                elif i == 2:
                    items = ["내 파일", "휴지통"]
                elif i == 3:
                    items = ["받은메시지", "보낸메시지", "메시지 보내기"]
                else:
                    items = ["서비스 확인 및 변경", "개인정보변경", "기본메시지 설정", "마무리메시지 설정", "블랙리스트 설정", "클라우드 설정"]

            for item in items:
                sub_list.addItem(item)

            sub_list.itemClicked.connect(self.on_submenu_clicked)

            p_layout.addWidget(sub_list)
            p_layout.addStretch()
            self.submenu_stack.addWidget(page)

        layout.addWidget(self.submenu_stack)
        parent_layout.addWidget(self.submenu_container)
        
        
    def load_and_update_storage_info(self):
            """서버에서 현재 사용자의 사용량과 등급별 최대 용량을 가져와 사이드바 및 홈 화면에 반영합니다."""
            user_email = self.user_info.get("email")
            if not user_email or not self.net_client:
                return

            res = self.net_client.get_user_storage_info(user_email)
            if res.get("status") == "success":
                grade_name = res.get("grade_name", "일반")
                max_storage_bytes = res.get("max_storage", 500 * 1024 * 1024) # 기본 500MB
                total_used_bytes = res.get("total_used", 0)

                # 바이트(Bytes)를 MB 단위로 보기 쉽게 변환
                used_mb = total_used_bytes / (1024 * 1024)
                max_mb = max_storage_bytes / (1024 * 1024)

                # 퍼센트 계산 (0 ~ 100)
                if max_mb > 0:
                    percent = int((total_used_bytes / max_storage_bytes) * 100)
                    percent = min(max(percent, 0), 100) # 0~100 사이 보정
                else:
                    percent = 0

                # 사이드바 라벨 및 프로그래스바 갱신
                if max_mb >= 1024:
                    used_str = f"{used_mb / 1024:.1f}GB"
                    max_str = f"{max_mb / 1024:.0f}GB"
                else:
                    used_str = f"{int(used_mb)}MB"
                    max_str = f"{int(max_mb)}MB"

                self.storage_label.setText(f"{used_str} / {max_str} | {grade_name}")
                self.storage_progress_bar.setValue(percent)
                
                # 홈 위젯 등 하위 화면에서도 쓸 수 있도록 user_info에 담아둠
                self.user_info["grade_name"] = grade_name
                self.user_info["max_storage"] = max_storage_bytes
                self.user_info["total_used"] = total_used_bytes
                self.user_info["storage_percent"] = percent

                # 💡 홈 메인 위젯이 생성되어 있다면 최신 사용자 정보로 동기화 갱신
                home_page = self.content_pages.get("홈 메인")
                if home_page and hasattr(home_page, "update_user_info"):
                    home_page.update_user_info(self.user_info)

    def init_content_area(self, parent_layout):
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #EFF8F1;")

        layout = QVBoxLayout(self.content_area)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.path_label = QLabel("> 홈 메인")
        self.path_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #222;")
        layout.addWidget(self.path_label)
        
        layout.setSpacing(19)
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #D0D8D2;")  # 연한 회록색 계열 선 색상
        layout.addWidget(line)
        

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: transparent;")

        all_menu_names = [
            "홈 메인", "달력보기", "내 파일", "공유 문서", "휴지통", 
            "메시지함", "메시지 보내기", "받은메시지", "보낸메시지", 
            "서비스 확인 및 변경", "개인정보변경", "기본메시지 설정", 
            "마무리메시지 설정", "블랙리스트 설정", "클라우드 설정", "서비스제한"
        ]

        self.content_pages = {}
        for name in all_menu_names:
            if name == "홈 메인":
                self.content_pages[name] = HomeWidget(self.user_info)
            # 💡 [클라우드] net_client 및 user_info 인자 전달
            elif name == "내 파일":
                self.content_pages[name] = CloudWindow(net_client=self.net_client, user_info=self.user_info)
            # 💡 [휴지통] TrashWindow 위젯 연결 및 인자 전달
            elif name == "휴지통":
                self.content_pages[name] = TrashWindow(net_client=self.net_client, user_info=self.user_info)
            elif name == "달력보기":
                self.content_pages[name] = CalenderWidget()
            elif name == "서비스 확인 및 변경":
                user_email = self.user_info.get("email", "user@example.com")
                self.content_pages[name] = ServiceSettingWidget(
                                    user_email=user_email, 
                                    net_client=self.net_client
                                )
            elif name == "개인정보변경":  # 💡 개인정보변경 위젯 연결
                self.content_pages[name] = UserInfoSettingWidget(
                    user_info=self.user_info,
                    net_client=self.net_client
                )    
            elif name in ["받은메시지", "메시지함"]:  # 👈 메시지 위젯 연결
                self.content_pages[name] = MessageWidget(self.user_info)
            elif name == "보낸메시지":
                self.content_pages[name] = SentMessageWidget(self.user_info)
            elif name == "서비스제한":
                self.content_pages[name] = AdminServiceWidget(net_client=self.net_client)  
            elif name == "기본메시지 설정":
                self.content_pages[name] = DefaultMessageSettingWidget(
                    user_info=self.user_info, net_client=self.net_client
                )
            elif name == "마무리메시지 설정":
                self.content_pages[name] = OutroMessageSettingWidget(
                    user_info=self.user_info, net_client=self.net_client
                )      
            elif name == "블랙리스트 설정":
                from settings_window import BlacklistSettingWidget
                self.content_pages[name] = BlacklistSettingWidget(
                    user_info=self.user_info, net_client=self.net_client
                )    
            else:
                self.content_pages[name] = PlaceholderView(name)

        self.page_index_map = {}
        for idx, (name, widget) in enumerate(self.content_pages.items()):
            self.content_stack.addWidget(widget)
            self.page_index_map[name] = idx

        layout.addWidget(self.content_stack)
        parent_layout.addWidget(self.content_area, stretch=1)

    def change_submenu(self, index):
        self.submenu_stack.setCurrentIndex(index)
        current_page = self.submenu_stack.currentWidget()
        sub_list = current_page.findChild(QListWidget)
        if sub_list and sub_list.count() > 0:
            sub_list.setCurrentRow(0)
            first_item_text = sub_list.item(0).text()
            self.update_content_view(first_item_text)

    def on_submenu_clicked(self, item):
        menu_text = item.text()
        if menu_text == "메시지 보내기":
            current_user_email = self.user_info.get("email")
            net_client = getattr(self, 'net_client', None)
            dialog = MessageDialog(mode='send', current_user_email=current_user_email, net_client=net_client, user_info=self.user_info)
            dialog.exec()
        else:
            self.update_content_view(menu_text)

    def update_content_view(self, menu_text):
        """메인 컨텐츠 화면 전환 및 자동 데이터 갱신"""
        self.path_label.setText(f"> {menu_text}")
        if menu_text in self.page_index_map:
            page_widget = self.content_pages[menu_text]
            # 💡 [자동 갱신] 내 파일 또는 휴지통 이동 시 DB 최신 데이터 자동 조회
            if hasattr(page_widget, "load_file_list"):
                page_widget.load_file_list()
            self.content_stack.setCurrentIndex(self.page_index_map[menu_text])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())