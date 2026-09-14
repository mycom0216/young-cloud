import os
import sys
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



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Young Cloud Desktop App")
        self.resize(1100, 750)

        # 현재 스크립트가 위치한 디렉토리 경로
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 3. 메인 컨텐츠 영역 생성
        self.init_content_area(main_layout)

        # 2. 좌측 서브메뉴 영역 생성
        self.init_submenu(main_layout)

        # 1. 좌측 사이드바 영역 생성
        self.init_sidebar(main_layout)
        
        # 레이아웃 순서 조정 (사이드바 -> 서브메뉴 -> 메인컨텐츠 순)
        main_layout.removeWidget(self.sidebar)
        main_layout.removeWidget(self.submenu_container)
        main_layout.removeWidget(self.content_area)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.submenu_container)
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
        profile_label = QLabel("000님,")
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

        # 사이드바 메뉴 정의 (텍스트, 아이콘 파일명, 콜백)
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
        layout.addWidget(logout_btn)

        parent_layout.addWidget(self.sidebar)

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

        menu_titles = ["HOME", "캘린더", "클라우드", "메시지", "설정"]

        for i in range(5):
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

            if i == 0: # HOME
                items = ["홈 메인"]
            elif i == 1: # 캘린더
                items = ["달력보기"]
            elif i == 2: # 클라우드
                items = ["내 파일", "공유 문서", "휴지통"]
            elif i == 3: # 메시지
                items = ["메시지함", "메시지 보내기", "받은메시지", "보낸메시지"]
            else: # 설정
                items = ["서비스 확인 및 변경", "개인정보변경", "기본메시지 설정", "마무리메시지 설정", "블랙리스트 설정", "클라우드 설정"]

            for item in items:
                sub_list.addItem(item)

            # 서브메뉴 항목 클릭 시 우측 메인 컨텐츠 전환 함수 연결
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
        self.default_page = QWidget()
        self.content_stack.addWidget(self.default_page)

        layout.addWidget(self.content_stack)
        parent_layout.addWidget(self.content_area, stretch=1)
        
        
        
        # ####여기에 팀원들이 만든 위젯들을 인스턴스화하여 스택에 추가###############
        # # =========================================================================
        # # 💡 [팀원 연동 매핑 딕셔너리] 
        # # 서브메뉴 항목 이름과 팀원이 만든 위젯 클래스를 1:1로 매핑하는 공간입니다.
        # # 개발 완료된 화면 위젯으로 교체해 주세요.
        # # =========================================================================
        # self.content_pages = {
        #     "홈 메인": SampleView("홈 메인"),
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

        # # 스택에 페이지들을 등록하고 인덱스 맵 구성
        # self.page_index_map = {}
        # for idx, (name, widget) in enumerate(self.content_pages.items()):
        #     self.content_stack.addWidget(widget)
        #     self.page_index_map[name] = idx

        # layout.addWidget(self.content_stack)
        # parent_layout.addWidget(self.content_area, stretch=1)
        
        

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
        self.update_content_view(menu_text)

    def update_content_view(self, menu_text):
        """우측 메인 컨텐츠 상단 경로명 업데이트"""
        self.path_label.setText(f"> {menu_text}")
        
    # def open_file_upload_dialog(self):
    #     dialog = FileUploadPopup(self)
    #     dialog.exec()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    