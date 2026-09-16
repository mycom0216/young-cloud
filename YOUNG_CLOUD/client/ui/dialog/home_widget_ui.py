# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
        contentWidget.resize(750, 710)
        contentWidget.setStyleSheet(u"QWidget#contentWidget {\n"
"    background-color: #EFF8F1; /* \uc6d0\ud558\ub294 \ubc30\uacbd\uc0c9 */\n"
"}\n"
"\n"
"/* 2. \uce98\ub9b0\ub354 \uc704\uc82f(QCalendarWidget)\uc740 \uc2a4\ud0c0\uc77c \uc0c1\uc18d\uc744 \ubc1b\uc9c0 \uc54a\ub3c4\ub85d \ubcc4\ub3c4\ub85c \uae30\ubcf8 \ubc30\uacbd\uc0c9 \uc9c0\uc815 */\n"
"QCalendarWidget {\n"
"    background-color: #FFFFFF; \n"
"	border-radius: 3px;\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_navigationbar {\n"
"    background-color: #128BA6; /* \uc6d0\ud558\ub294 \ud30c\ub780\uc0c9 \ucf54\ub4dc\ub85c \ubcc0\uacbd \uac00\ub2a5 */\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled {\n"
"    selection-background-color: #9CBF1F; /* \uc120\ud0dd\ub41c \ub0a0\uc9dc\uc758 \ubc30\uacbd\uc0c9 (\ud30c\ub780\uc0c9) */\n"
"    selection-color: #FFFFFF;            /* \uc120\ud0dd\ub41c \ub0a0\uc9dc\uc758 \uae00\uc790\uc0c9 (\ud770\uc0c9) */\n"
"}\n"
"\n"
"")
        self.label = QLabel(contentWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 50, 391, 21))
        font = QFont()
        font.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font.setPointSize(11)
        self.label.setFont(font)
        self.progressBar = QProgressBar(contentWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(10, 120, 391, 16))
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
        self.label_bar_name.setGeometry(QRect(10, 90, 381, 21))
        font1 = QFont()
        font1.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font1.setPointSize(10)
        self.label_bar_name.setFont(font1)
        self.label_2 = QLabel(contentWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(440, 180, 141, 21))
        self.label_2.setFont(font)
        self.label_3 = QLabel(contentWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 210, 210, 100))
        self.label_3.setPixmap(QPixmap(u"../source/image/ad_1.png"))
        self.label_3.setScaledContents(True)
        self.label_4 = QLabel(contentWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 320, 210, 271))
        self.label_4.setPixmap(QPixmap(u"../source/image/ad_2.png"))
        self.label_4.setScaledContents(True)
        self.calendarWidget = QCalendarWidget(contentWidget)
        self.calendarWidget.setObjectName(u"calendarWidget")
        self.calendarWidget.setGeometry(QRect(440, 210, 271, 381))
        font2 = QFont()
        font2.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font2.setBold(True)
        self.calendarWidget.setFont(font2)
        self.calendarWidget.setStyleSheet(u"")
        self.label_5 = QLabel(contentWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(232, 210, 185, 101))
        self.label_5.setPixmap(QPixmap(u"../source/image/ad_3.png"))
        self.label_5.setScaledContents(True)
        self.label_6 = QLabel(contentWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(232, 320, 185, 271))
        self.label_6.setPixmap(QPixmap(u"../source/image/ad_4.png"))
        self.label_6.setScaledContents(True)

        self.retranslateUi(contentWidget)

        QMetaObject.connectSlotsByName(contentWidget)
    # setupUi

    def retranslateUi(self, contentWidget):
        contentWidget.setWindowTitle(QCoreApplication.translate("contentWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("contentWidget", u"000\ub2d8, \ud658\uc601\ud569\ub2c8\ub2e4.", None))
        self.label_bar_name.setText(QCoreApplication.translate("contentWidget", u"\ub4f1\uae09 \ubc0f \uc6a9\ub7c9", None))
        self.label_2.setText(QCoreApplication.translate("contentWidget", u"\uce98\ub9b0\ub354", None))
        self.label_3.setText("")
        self.label_4.setText("")
        self.label_5.setText("")
        self.label_6.setText("")
    # retranslateUi

