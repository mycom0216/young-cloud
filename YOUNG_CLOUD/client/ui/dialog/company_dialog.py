# -*- coding: utf-8 -*-
import requests
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QMessageBox
)

# 비즈노(Bizno.net) REST API 키를 아래 따옴표 안에 입력해주세요.
COMPANY_API_KEY = "2xN4CgaqByeUI0bWIf5QIvtN"


class CompanySearchDialog(QDialog):
    """비즈노 REST API를 이용해 상호명을 검색하고 선택하는 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회사 검색")
        self.resize(360, 420)
        self.setStyleSheet("background-color: #EFF8F1;")
        self.selected_company_name = ""

        layout = QVBoxLayout(self)

        # 상단 검색 바 영역
        search_layout = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("회사명을 입력하세요 (예: 삼성전자)")
        self.input_search.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 6px;"
        )
        self.input_search.returnPressed.connect(self.search_companies)

        self.btn_search = QPushButton("검색")
        self.btn_search.setStyleSheet(
            "QPushButton {"
            "    background-color: #63F2F2;"
            "    color: #333333;"
            "    border-radius: 4px;"
            "    padding: 6px 12px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #66E4F2;"
            "}"
        )
        self.btn_search.clicked.connect(self.search_companies)

        search_layout.addWidget(self.input_search)
        search_layout.addWidget(self.btn_search)
        layout.addLayout(search_layout)

        # 결과 목록 리스트위젯
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 4px;"
        )
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

        # 선택 완료 버튼
        self.btn_select = QPushButton("선택완료")
        self.btn_select.setStyleSheet(
            "QPushButton {"
            "    background-color: #63F2F2;"
            "    color: #333333;"
            "    border-radius: 4px;"
            "    padding: 8px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #66E4F2;"
            "}"
        )
        self.btn_select.clicked.connect(self.on_select_clicked)
        layout.addWidget(self.btn_select)

    def search_companies(self):
        corp_name = self.input_search.text().strip()
        if not corp_name:
            QMessageBox.warning(self, "안내", "회사명을 입력해주세요.")
            return

        self.list_widget.clear()

        # 비즈노 API 호출
        url = "https://bizno.net/api/fapi"
        params = {
            "key": COMPANY_API_KEY,
            "gb": "3",        # 3: 상호명 검색
            "q": corp_name,
            "type": "json"
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            result_code = data.get("resultCode")
            if result_code not in (0, "0", None):
                msg = data.get("resultMsg", "회사 정보를 조회할 수 없습니다.")
                QMessageBox.warning(self, "조회 실패", f"[{result_code}] {msg}")
                return

            items = data.get("items") or data.get("item") or []

            if isinstance(items, dict):
                items = [items]

            if not items:
                self.list_widget.addItem("검색 결과가 없습니다.")
                return

            found_count = 0
            for item in items:
                comp_name = item.get("company") or item.get("title") or item.get("company_name") or ""
                comp_name = str(comp_name).strip()
                if comp_name:
                    self.list_widget.addItem(comp_name)
                    found_count += 1

            if found_count == 0:
                self.list_widget.addItem("검색 결과가 없습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"API 호출 중 문제가 발생했습니다:\n{e}")

    def on_item_double_clicked(self, item):
        if item.text() != "검색 결과가 없습니다.":
            self.selected_company_name = item.text()
            self.accept()

    def on_select_clicked(self):
        current_item = self.list_widget.currentItem()
        if (
            current_item
            and current_item.text()
            and current_item.text() != "검색 결과가 없습니다."
        ):
            self.selected_company_name = current_item.text()
            self.accept()
        else:
            QMessageBox.warning(self, "안내", "목록에서 회사를 선택해주세요.")