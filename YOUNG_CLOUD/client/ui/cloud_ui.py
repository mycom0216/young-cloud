# -*- coding: utf-8 -*-
"""클라우드 파일 목록 UI."""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QStyle, QTableWidget, QTableWidgetItem, QToolButton,
    QVBoxLayout, QWidget
)


class CloudUI(QWidget):
    """파일 목록과 업로드/다운로드/삭제 툴바를 제공하는 기본 화면."""

    def __init__(self, mode="my_files", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setStyleSheet("background-color: #FFFFFF;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        title = {
            "my_files": "> 내 파일",
            "shared": "> 공유 문서",
            "trash": "> 휴지통",
        }.get(self.mode, "> 클라우드")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(25)
        style = self.style()
        self.btn_upload = self._create_tool_button(
            "파일 올리기", style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        )
        self.btn_download = self._create_tool_button(
            "파일 받기", style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        )
        self.btn_delete = self._create_tool_button(
            "삭제", style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )
        self.btn_restore = self._create_tool_button(
            "복원", style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        )
        toolbar.addWidget(self.btn_upload)
        toolbar.addWidget(self.btn_download)
        toolbar.addWidget(self.btn_delete)
        if self.mode == "trash":
            toolbar.addWidget(self.btn_restore)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["선택", "이름", "종류", "수정일", "크기"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(2, 70)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #DCE5DE; background: white; }
            QTableWidget::item { border-bottom: 1px solid #F0F0F0; padding: 5px; }
            QTableWidget::item:selected { background-color: #E2F4F1; color: #000; }
        """)
        layout.addWidget(self.table)

    def _create_tool_button(self, text, icon):
        button = QToolButton(self)
        button.setText(text)
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet("QToolButton { border: none; font-size: 12px; }")
        return button

    def set_files(self, files):
        self.table.setRowCount(0)
        for file_info in files:
            row = self.table.rowCount()
            self.table.insertRow(row)

            check = QCheckBox()
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)
            check_layout.setContentsMargins(0, 0, 0, 0)
            check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            check_layout.addWidget(check)
            self.table.setCellWidget(row, 0, check_widget)

            name = QTableWidgetItem(str(file_info.get("name", "")))
            name.setData(Qt.ItemDataRole.UserRole, file_info)
            self.table.setItem(row, 1, name)
            self.table.setItem(row, 2, QTableWidgetItem("파일"))
            self.table.setItem(row, 3, QTableWidgetItem(str(file_info.get("date", ""))[:19]))
            self.table.setItem(row, 4, QTableWidgetItem(self._format_size(file_info.get("size", 0))))

    @staticmethod
    def _format_size(value):
        try:
            size = float(value or 0)
        except (TypeError, ValueError):
            return str(value or "")
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}"
            size /= 1024
