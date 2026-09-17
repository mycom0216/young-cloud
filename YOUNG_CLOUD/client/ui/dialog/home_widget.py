import os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon, QPixmap
from .home_widget_ui import Ui_contentWidget
from .calender_widget_ui import Ui_contentWidget as calender


class HomeWidget(QWidget, Ui_contentWidget):
    """
    [홈 메인 화면 위젯 클래스]
    - 로그인한 사용자의 이름과 환영 문구를 출력합니다.
    - 사용자의 클라우드 사용량 퍼센트 및 등급 정보를 받아와 홈 화면에 반영합니다.
    """
    def __init__(self, user_info=None):
        super().__init__()
        self.setupUi(self)
        
        self.user_info = user_info or {}
        self.update_user_info(self.user_info)
        
        # 광고 이미지 및 캘린더 스타일 설정
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        img_path_1 = os.path.join(base_path, "..", "source", "image", "ad_1.png")
        img_path_2 = os.path.join(base_path, "..", "source", "image", "ad_2.png")
        img_path_3 = os.path.join(base_path, "..", "source", "image", "ad_3.png")
        img_path_4 = os.path.join(base_path, "..", "source", "image", "ad_4.png")
        
        if os.path.exists(img_path_1): self.label_3.setPixmap(QPixmap(img_path_1))
        if os.path.exists(img_path_2): self.label_4.setPixmap(QPixmap(img_path_2))
        if os.path.exists(img_path_3): self.label_5.setPixmap(QPixmap(img_path_3))
        if os.path.exists(img_path_4): self.label_6.setPixmap(QPixmap(img_path_4))
        
        self.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #9CBF1F;
                selection-color: #FFFFFF;
            }
        """)    

    def update_user_info(self, user_info):
        """외부(메인 윈도우 등)에서 최신 사용자 정보가 갱신될 때 호출하는 메서드"""
        self.user_info = user_info or {}
        self.user_name = self.user_info.get("name", "사용자")
        
        # 1. 환영 문구 업데이트
        self.label.setText(f"{self.user_name}님, 환영합니다.")
        
        # 2. 프로그래스바 및 등급/용량 텍스트 업데이트
        storage_percent = self.user_info.get("storage_percent", 0)
        if hasattr(self, 'progressBar'):
            self.progressBar.setValue(storage_percent)
            
        grade_name = self.user_info.get("grade_name", "일반")
        max_storage_bytes = self.user_info.get("max_storage", 500 * 1024 * 1024)
        total_used_bytes = self.user_info.get("total_used", 0)
        
        used_mb = total_used_bytes / (1024 * 1024)
        max_mb = max_storage_bytes / (1024 * 1024)
        
        if max_mb >= 1024:
            used_str = f"{used_mb / 1024:.1f}GB"
            max_str = f"{max_mb / 1024:.0f}GB"
        else:
            used_str = f"{int(used_mb)}MB"
            max_str = f"{int(max_mb)}MB"
            
        # UI 파일에 정의된 등급 및 용량 표시 라벨 반영
        if hasattr(self, 'label_bar_name'):
            self.label_bar_name.setText(f"등급 : {grade_name}  |  사용량 : {used_str} / {max_str}")


class CalenderWidget(QWidget, calender):
    def __init__(self):
        super().__init__()
        self.setupUi(self)        
        self.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #9CBF1F;
                selection-color: #FFFFFF;
            }
        """)