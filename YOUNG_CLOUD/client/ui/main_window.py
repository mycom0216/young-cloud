import os
import sys
from ui.cloud_window import CloudWindow
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
from settings_window import ServiceSettingWidget, UserInfoSettingWidget
from message_window import MessageWidget, MessageDialog, SentMessageWidget


# 💡 아직 개발되지 않은 메뉴들을 위한 임시 안내 화면 클래스
class PlaceholderView(QWidget):
    def __init__(self, menu_name):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(f"'{menu_name}' 화면은 팀원이 개발 중입니다. 🚧")
        label.setStyleSheet("font-size: 15px; color: #555; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)




class MainWindow(QMainWindow):
    def __init__(self, user_info = None):
        super().__init__()
        self.setWindowTitle("Young Cloud Desktop App")
        self.resize(1100, 750)
        self.user_info = user_info or {}
        self.user_name = self.user_info.get("name", "사용자")
        # 💡 [추가] 메인 윈도우에서 사용할 공용 네트워크 클라이언트 초기화
        from network_client import NetworkClient
        self.net_client = NetworkClient()
        
        # 관리자 여부 확인 (서버 응답 키값에 따라 소문자/대문자 모두 대응)
        self.is_admin = bool(
            self.user_info.get("is_admin", False) or 
            self.user_info.get("IS_ADMIN", False)
        )

        # 현재 스크립트가 위치한 디렉토리 경로
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

        # 💡 3. 서브메뉴와 메인컨텐츠 사이의 세로 구분선 생성 및 추가
        self.vertical_line = QFrame()
        self.vertical_line.setFrameShape(QFrame.VLine)
        self.vertical_line.setFrameShadow(QFrame.Sunken)
        self.vertical_line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.vertical_line.setStyleSheet("background-color: #C5D2C7; border: none;")
        self.vertical_line.setFixedWidth(2)  # 선 두께 (2픽셀)
        main_layout.addWidget(self.vertical_line)

        # 4. 메인 컨텐츠 영역 생성 및 추가 (stretch=1을 주어 남은 공간을 꽉 채우게 함)
        self.init_content_area(main_layout)
        main_layout.addWidget(self.content_area, stretch=1)
    def init_sidebar(self, parent_layout):
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #9CBF1F;
            }
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
        
        # 사용자 프로필 영역
        profile_label = QLabel(f"       {self.user_name}님")
        profile_label.setStyleSheet("color: black; font-weight: bold; font-size: 13px; background: transparent;")
        layout.addWidget(profile_label)

        # 로고 이미지 라벨 추가
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

        # 💡 [권한별 사이드바 메뉴 분기]
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

        # 하단 로그아웃 버튼
        logout_btn = QPushButton("로그아웃")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #63F2F2;
                color: #333333;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66E4F2;
            }
        """)
        logout_btn.setMinimumHeight(35)
        # 로그아웃 버튼 클릭 시그널 연결
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        parent_layout.addWidget(self.sidebar)

    def logout(self):
        """로그아웃 처리: 현재 메인 창을 닫고 로그인 창을 다시 엶"""
        print("[GUI] 로그아웃을 수행합니다.")
        # 순환 참조 방지를 위해 함수 내부에서 로그인 윈도우 임포트
        # (프로젝트 폴더 구조에 맞게 경로를 조정해주세요. 예: from ui.login_window import LoginWindow)
        from login_window import LoginWindow 
        self.login_window = LoginWindow()
        self.login_window.show()
        
        # 현재 메인 윈도우 닫기
        self.close()


    def init_submenu(self, parent_layout):
        self.submenu_container = QWidget()
        self.submenu_container.setStyleSheet("background-color: #EFF8F1;")
        self.submenu_container.setFixedWidth(180)

        layout = QVBoxLayout(self.submenu_container)
        layout.setContentsMargins(15, 20, 15, 20)

        # 서브메뉴 상단 파일 용량 게이지 영역
        storage_layout = QVBoxLayout()
        storage_layout.setSpacing(5)

        storage_label = QLabel("500MB | VIP")
        storage_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #333; background: transparent;")
        storage_layout.addWidget(storage_label)

        progress_bar = QProgressBar()
        progress_bar.setValue(45)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(6)
        progress_bar.setStyleSheet("""
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
        storage_layout.addWidget(progress_bar)

        layout.addLayout(storage_layout)
        layout.addSpacing(12)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #D0D8D2; background-color: #D0D8D2;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        layout.addSpacing(15)

        self.submenu_stack = QStackedWidget()
        self.submenu_stack.setStyleSheet("background: transparent;")

        # 💡 [권한별 서브메뉴 타이틀 및 하위 항목 분기]
        if self.is_admin:
            menu_titles = ["HOME", "메시지", "차단설정"]
        else:
            menu_titles = ["HOME", "캘린더", "클라우드", "메시지", "설정"]

        for i in range(len(menu_titles)):
            page = QWidget()
            p_layout = QVBoxLayout(page)
            p_layout.setContentsMargins(0, 0, 0, 0)

            title_label = QLabel(f"> {menu_titles[i]}")
            title_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333;")
            p_layout.addWidget(title_label)

            p_layout.addSpacing(15)

            sub_list = QListWidget()
            sub_list.setStyleSheet("""
                QListWidget {
                    background-color: transparent;
                    border: none;
                    font-size: 13px;
                    color: #444444;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 4px;
                }
                QListWidget::item:selected {
                    background-color: #D6E8DB;
                    color: #000000;
                    font-weight: bold;
                }
            """)

            if self.is_admin:
                if i == 0: # HOME
                    items = ["홈 메인"]
                elif i == 1: # 메시지
                    items = ["보낸메시지","메시지 보내기"]
                else: # 차단설정
                    items = ["서비스제한"]
            else:
                if i == 0: # HOME
                    items = ["홈 메인"]
                elif i == 1: # 캘린더
                    items = ["달력보기"]
                elif i == 2: # 클라우드
                    items = ["내 파일", "휴지통"]
                elif i == 3: # 메시지
                    items = ["받은메시지", "보낸메시지", "메시지 보내기"]
                else: # 설정
                    items = ["서비스 확인 및 변경", "개인정보변경", "기본메시지 설정", "마무리메시지 설정", "블랙리스트 설정", "클라우드 설정"]

            for item in items:
                sub_list.addItem(item)

            sub_list.itemClicked.connect(self.on_submenu_clicked)

            p_layout.addWidget(sub_list)
            p_layout.addStretch()
            self.submenu_stack.addWidget(page)

        layout.addWidget(self.submenu_stack)
        parent_layout.addWidget(self.submenu_container)

    def init_content_area(self, parent_layout):
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #EFF8F1;")

        layout = QVBoxLayout(self.content_area)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 상단 경로 표시 레이블
        self.path_label = QLabel("> 홈 메인")
        self.path_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #222;")
        layout.addWidget(self.path_label)

        # 메인 컨텐츠 화면 전환을 위한 QStackedWidget 설정
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: transparent;")

        # 기본 빈 페이지 추가 (필요에 따라 동적으로 채워넣거나 확장 가능)
        # self.default_page = QWidget()
        # self.content_stack.addWidget(self.default_page)

        # layout.addWidget(self.content_stack)
        # parent_layout.addWidget(self.content_area, stretch=1)
        
        
        
        ####여기에 팀원들이 만든 위젯들을 인스턴스화하여 스택에 추가###############
        # =========================================================================
        # 💡 [팀원 연동 매핑 딕셔너리] 
        # 서브메뉴 항목 이름과 팀원이 만든 위젯 클래스를 1:1로 매핑하는 공간입니다.
        # 개발 완료된 화면 위젯으로 교체해 주세요.
        # =========================================================================
        # self.content_pages = {
        #     "홈 메인": HomeWidget(self.user_info),
        #     "달력보기": SampleView("달력보기"),
        #     "내 파일": SampleView("내 파일"),
        #     "공유 문서": SampleView("공유 문서"),
        #     "휴지통": SampleView("휴지통"),
        #     "메시지함": SampleView("메시지함"),
        #     "메시지 보내기": SampleView("메시지 보내기"),
        #     "받은메시지": SampleView("받은메시지"),
        #     "보낸메시지": SampleView("보낸메시지"),
        #     "서비스 확인 및 변경": SampleView("서비스 확인 및 변경"),
        #     "개인정보변경": SampleView("개인정보변경"),
        #     "기본메시지 설정": SampleView("기본메시지 설정"),
        #     "마무리메시지 설정": SampleView("마무리메시지 설정"),
        #     "블랙리스트 설정": SampleView("블랙리스트 설정"),
        #     "클라우드 설정": SampleView("클라우드 설정"),
        # }


#### 여기서부터 메인위젯 테스트용
# 💡 모든 서브메뉴 항목 리스트 정의 (일반 사용자 + 관리자 메뉴 통합)
        all_menu_names = [
            "홈 메인", "달력보기", "내 파일", "공유 문서", "휴지통", 
            "메시지함", "메시지 보내기", "받은메시지", "보낸메시지", 
            "서비스 확인 및 변경", "개인정보변경", "기본메시지 설정", 
            "마무리메시지 설정", "블랙리스트 설정", "클라우드 설정", "서비스제한"
        ]

        # 💡 스택 페이지 딕셔너리 동적 생성 ("홈 메인"만 진짜 홈위젯, 나머지는 임시 화면)
        self.content_pages = {}
        for name in all_menu_names:
            if name == "홈 메인":
                self.content_pages[name] = HomeWidget(self.user_info)
            elif name == "내 파일":
                self.content_pages[name] = CloudWindow()
            elif name == "달력보기":
                self.content_pages[name] = CalenderWidget()
            elif name == "서비스 확인 및 변경":  # 👈 이 조건문을 추가합니다
                # 사용자 이메일 정보를 함께 전달 (user_info에 email 정보가 있다면 활용)
                user_email = self.user_info.get("email", "user@example.com")
                self.content_pages[name] = ServiceSettingWidget(user_email=user_email)
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
            else:
                self.content_pages[name] = PlaceholderView(name)


    ### 여기까지 테스트용 코드



        # 스택에 페이지들을 등록하고 인덱스 맵 구성
        self.page_index_map = {}
        for idx, (name, widget) in enumerate(self.content_pages.items()):
            self.content_stack.addWidget(widget)
            self.page_index_map[name] = idx

        layout.addWidget(self.content_stack)
        parent_layout.addWidget(self.content_area, stretch=1)
        
        

    def change_submenu(self, index):
        """사이드바 메뉴 클릭 시 서브메뉴 스택을 변경하고, 해당 서브메뉴의 첫 번째 항목 선택"""
        self.submenu_stack.setCurrentIndex(index)
        
        current_page = self.submenu_stack.currentWidget()
        sub_list = current_page.findChild(QListWidget)
        if sub_list and sub_list.count() > 0:
            sub_list.setCurrentRow(0)
            first_item_text = sub_list.item(0).text()
            self.update_content_view(first_item_text)

    def on_submenu_clicked(self, item):
        """서브메뉴의 개별 항목을 클릭했을 때 호출"""
        menu_text = item.text()
        
        # 💡 "메시지 보내기"를 클릭한 경우: 메인 영역 스택을 바꾸지 않고 팝업 다이얼로그 띄우기
        if menu_text == "메시지 보내기":
            current_user_email = self.user_info.get("email")
            net_client = getattr(self, 'net_client', None)
            
            # 'send' 모드로 메시지 보내기 다이얼로그 호출
            dialog = MessageDialog(mode='send', current_user_email=current_user_email, net_client=net_client)
            dialog.exec()
        else:
            # 그 외 일반 메뉴일 경우 기존처럼 우측 메인 영역 스택 페이지 전환
            self.update_content_view(menu_text)
            

    # 서브메뉴바에서 메뉴를 클릭
    def handle_menu_click(self, menu_name):
        """사이드바/서브메뉴바에서 메뉴를 클릭했을 때의 동작 제어"""
        if menu_name == "메시지 보내기":
            # 💡 [요구사항 2 루트] 메인 area는 마지막으로 열린 스택위젯창을 유지한 채 팝업 띄우기
            current_user_email = self.user_info.get("email", "user@example.com")
            net_client = getattr(self, 'net_client', None)
            
            # 'send' 모드로 메시지 보내기 다이얼로그 호출
            dialog = MessageDialog(mode='send', current_user_email=current_user_email, net_client=net_client)
            dialog.exec()
        else:
            # 다른 일반 페이지 메뉴일 경우 스택 위젯 페이지 전환
            if menu_name in self.content_pages:
                self.stackedWidget.setCurrentWidget(self.content_pages[menu_name])    



    def update_content_view(self, menu_text):
        """우측 메인 컨텐츠 상단 경로명 업데이트"""
        self.path_label.setText(f"> {menu_text}")
        # 💡 선택된 메뉴 이름에 해당하는 페이지로 스택 인덱스 변경
        if menu_text in self.page_index_map:
            self.content_stack.setCurrentIndex(self.page_index_map[menu_text])
        
        
    # def open_file_upload_dialog(self):
    #     dialog = FileUploadPopup(self)
    #     dialog.exec()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    