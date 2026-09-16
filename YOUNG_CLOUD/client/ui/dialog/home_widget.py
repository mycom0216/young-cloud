import os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon, QPixmap
from .home_widget_ui import Ui_contentWidget
from .calender_widget_ui import Ui_contentWidget as calender


class HomeWidget(QWidget, Ui_contentWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.setupUi(self)
        
        self.user_info = user_info or {}
        self.user_name = self.user_info.get("name", "사용자")
        
        # 환영 문구 업데이트 (예: "홍길동님, 환영합니다.")
        self.label.setText(f"{self.user_name}님, 환영합니다.")
        
        # 이미지 경로 설정 (dialog 폴더 기준 상대 경로 맞춤)
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        img_path_1 = os.path.join(base_path, "..", "source", "image", "ad_1.png")
        img_path_2 = os.path.join(base_path, "..", "source", "image", "ad_2.png")
        img_path_3 = os.path.join(base_path, "..", "source", "image", "ad_3.png")
        img_path_4 = os.path.join(base_path, "..", "source", "image", "ad_4.png")
        
        # 💡 QPixmap()으로 감싸서 전달하도록 수정
        if os.path.exists(img_path_1): 
            self.label_3.setPixmap(QPixmap(img_path_1))
        if os.path.exists(img_path_2): 
            self.label_4.setPixmap(QPixmap(img_path_2))
        if os.path.exists(img_path_3): 
            self.label_5.setPixmap(QPixmap(img_path_3))
        if os.path.exists(img_path_4): 
            self.label_6.setPixmap(QPixmap(img_path_4))
        
        # 💡 [추가] 캘린더 날짜 영역 배경을 밝게 잡아주는 스타일시트 적용
        self.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #9CBF1F;
                selection-color: #FFFFFF;
            }
        """)    
        
class CalenderWidget(QWidget, calender):
    def __init__(self):
        super().__init__()
        self.setupUi(self)        
          # 💡 [추가] 캘린더 날짜 영역 배경을 밝게 잡아주는 스타일시트 적용
        self.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #9CBF1F;
                selection-color: #FFFFFF;
                    }
                """)   