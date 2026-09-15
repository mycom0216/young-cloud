# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCalendarWidget, QLabel, QProgressBar,
    QSizePolicy, QWidget)

class Ui_contentWidget(object):
    def setupUi(self, contentWidget):
        if not contentWidget.objectName():
            contentWidget.setObjectName(u"contentWidget")
        contentWidget.resize(819, 775)
        contentWidget.setStyleSheet(u"QWidget#contentWidget {\n"
"    background-color: #EFF8F1; /* 원하는 배경색 */\n"
"}\n"
"\n"
"/* 2. 캘린더 위젯(QCalendarWidget)은 스타일 상속을 받지 않도록 별도로 기본 배경색 지정 */\n"
"QCalendarWidget {\n"
"    background-color: #E1CB87;\n"
"	border-radius: 3px;\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_navigationbar {\n"
"    background-color: #128BA6; /* 원하는 파란색 코드로 변경 가능 */\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled {\n"
"    selection-background-color: #9CBF1F; /* 선택된 날짜의 배경색 (파란색) */\n"
"    selection-color: #FFFFFF;            /* 선택된 날짜의 글자색 (흰색) */\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton:hover {\n"
"    background-color: rgba(255, 255,"
                        " 255, 20%);\n"
"    border-radius: 4px;\n"
"}")
        self.label = QLabel(contentWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 50, 141, 21))
        font = QFont()
        font.setFamilies([u"나눔스퀘어"])
        font.setPointSize(13)
        self.label.setFont(font)
        self.progressBar = QProgressBar(contentWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(20, 120, 201, 16))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"                background-color: #DCE5DE;\n"
"                border: none;\n"
"                border-radius: 3px;\n"
"            }\n"
"            QProgressBar::chunk {\n"
"                background-color: #63F2F2;\n"
"                border-radius: 3px;\n"
"            }")
        self.progressBar.setValue(24)
        self.label_bar_name = QLabel(contentWidget)
        self.label_bar_name.setObjectName(u"label_bar_name")
        self.label_bar_name.setGeometry(QRect(20, 100, 141, 21))
        font1 = QFont()
        font1.setFamilies([u"나눔스퀘어"])
        font1.setPointSize(10)
        self.label_bar_name.setFont(font1)
        self.label_2 = QLabel(contentWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(490, 190, 141, 21))
        self.label_2.setFont(font)
        self.label_3 = QLabel(contentWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 190, 231, 111))
        self.label_3.setPixmap(QPixmap(u"../source/image/ad_1.png"))
        self.label_3.setScaledContents(True)
        self.label_4 = QLabel(contentWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 320, 221, 291))
        self.label_4.setPixmap(QPixmap(u"../source/image/ad_2.png"))
        self.label_4.setScaledContents(True)
        self.calendarWidget = QCalendarWidget(contentWidget)
        self.calendarWidget.setObjectName(u"calendarWidget")
        self.calendarWidget.setGeometry(QRect(490, 230, 281, 381))
        font2 = QFont()
        font2.setFamilies([u"나눔스퀘어"])
        font2.setBold(True)
        self.calendarWidget.setFont(font2)
        self.calendarWidget.setStyleSheet(u"")
        self.label_5 = QLabel(contentWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(260, 190, 201, 111))
        self.label_5.setPixmap(QPixmap(u"../source/image/ad_3.png"))
        self.label_5.setScaledContents(True)
        self.label_6 = QLabel(contentWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(260, 320, 201, 291))
        self.label_6.setPixmap(QPixmap(u"../source/image/ad_4.png"))
        self.label_6.setScaledContents(True)

        self.retranslateUi(contentWidget)

        QMetaObject.connectSlotsByName(contentWidget)
    # setupUi

    def retranslateUi(self, contentWidget):
        contentWidget.setWindowTitle(QCoreApplication.translate("contentWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("contentWidget", u"000님, 환영합니다.", None))
        self.label_bar_name.setText(QCoreApplication.translate("contentWidget", u"등급 및 용량", None))
        self.label_2.setText(QCoreApplication.translate("contentWidget", u"캘린더", None))
        self.label_3.setText("")
        self.label_4.setText("")
        self.label_5.setText("")
        self.label_6.setText("")
    # retranslateUi