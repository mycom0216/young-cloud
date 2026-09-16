# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calender.ui'
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
from PySide6.QtWidgets import (QApplication, QCalendarWidget, QSizePolicy, QWidget)

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
        self.calendarWidget = QCalendarWidget(contentWidget)
        self.calendarWidget.setObjectName(u"calendarWidget")
        self.calendarWidget.setGeometry(QRect(40, 90, 661, 541))
        font = QFont()
        font.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font.setBold(True)
        self.calendarWidget.setFont(font)
        self.calendarWidget.setStyleSheet(u"")

        self.retranslateUi(contentWidget)

        QMetaObject.connectSlotsByName(contentWidget)
    # setupUi

    def retranslateUi(self, contentWidget):
        contentWidget.setWindowTitle(QCoreApplication.translate("contentWidget", u"Form", None))
    # retranslateUi

