# -*- coding: utf-8 -*-
import sys
import os

# 경로 설정 (client 폴더와 ui 폴더를 파이썬 경로에 추가)
current_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.join(current_dir, "ui")
sys.path.append(current_dir)
sys.path.append(ui_dir)

from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow

def main():
    # 1. QApplication 생성 (PySide6 앱 실행 필수 객체)
    app = QApplication(sys.argv)
    
    # 2. 로그인 창(LoginWindow) 인스턴스 생성 및 표시
    login_window = LoginWindow()
    login_window.show()
    
    # 3. 이벤트 루프 실행 및 프로그램 종료 처리
    sys.exit(app.exec())

if __name__ == "__main__":
    main()