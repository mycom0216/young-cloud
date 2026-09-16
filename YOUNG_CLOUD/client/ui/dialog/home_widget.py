import os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon, QPixmap
from .home_widget_ui import Ui_contentWidget
from .calender_widget_ui import Ui_contentWidget as calender


class HomeWidget(QWidget, Ui_contentWidget):
    """
    [홈 메인 화면 위젯 클래스]
    - 로그인한 사용자의 이름과 환영 문구를 출력합니다.
    - 사용자의 클라우드 사용량 퍼센트를 받아와 홈 화면의 프로그래스바에 반영합니다.
    - 각종 광고 이미지와 캘린더 위젯을 초기화하고 배치합니다.
    """
    def __init__(self, user_info=None):
        super().__init__()
        self.setupUi(self)
        
        # 전달받은 사용자 정보 딕셔너리 초기화 (없으면 빈 딕셔너리 사용)
        self.user_info = user_info or {}
        self.user_name = self.user_info.get("name", "사용자")
        
        # 1. 환영 문구 업데이트 (예: "포도송님, 환영합니다.")
        self.label.setText(f"{self.user_name}님, 환영합니다.")
        
        # 2. 메인 윈도우에서 계산되어 넘어온 클라우드 사용량 퍼센트 가져오기 (기본값 0)
        storage_percent = self.user_info.get("storage_percent", 0)
        
        # 💡 홈 UI 파일에 정의된 프로그래스바(progressBar)에 현재 사용량 퍼센트 반영
        if hasattr(self, 'progressBar'):
            self.progressBar.setValue(storage_percent)
            
        # 💡 (선택 사항) 퍼센트 수치를 텍스트로 보여주는 라벨이 있다면 함께 갱신
        if hasattr(self, 'label_percent'):
            self.label_percent.setText(f"{storage_percent}%")
        
        # 3. 광고 이미지 경로 설정 (dialog 폴더 기준 상대 경로 맞춤)
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        img_path_1 = os.path.join(base_path, "..", "source", "image", "ad_1.png")
        img_path_2 = os.path.join(base_path, "..", "source", "image", "ad_2.png")
        img_path_3 = os.path.join(base_path, "..", "source", "image", "ad_3.png")
        img_path_4 = os.path.join(base_path, "..", "source", "image", "ad_4.png")
        
        # QPixmap()으로 이미지를 불러와서 각 라벨에 장착
        if os.path.exists(img_path_1): 
            self.label_3.setPixmap(QPixmap(img_path_1))
        if os.path.exists(img_path_2): 
            self.label_4.setPixmap(QPixmap(img_path_2))
        if os.path.exists(img_path_3): 
            self.label_5.setPixmap(QPixmap(img_path_3))
        if os.path.exists(img_path_4): 
            self.label_6.setPixmap(QPixmap(img_path_4))
        
        # 4. 캘린더 날짜 영역 배경을 밝고 깔끔하게 잡아주는 스타일시트 적용
        self.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #9CBF1F;
                selection-color: #FFFFFF;
            }
        """)    
        
class CalenderWidget(QWidget, calender):
    """
    [캘린더 단독 화면 위젯 클래스]
    - 서브메뉴에서 캘린더보기를 눌렀을 때 띄워주는 달력 전용 위젯입니다.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)        
        
        # 캘린더 날짜 영역 배경 스타일시트 적용
        self.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #9CBF1F;
                selection-color: #FFFFFF;
            }
        """)