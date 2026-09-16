# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'message.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 300)
        Form.setStyleSheet(u"background-color: rgb(239, 248, 241);")
        self.label_title = QLabel(Form)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QRect(10, 20, 261, 31))
        font = QFont()
        font.setFamilies([u"\ub098\ub214\uace0\ub515"])
        font.setPointSize(16)
        font.setBold(True)
        self.label_title.setFont(font)
        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 50, 371, 16))
        self.line.setLineWidth(2)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.horizontalLayoutWidget = QWidget(Form)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(100, 251, 181, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_send = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_send.setObjectName(u"pushButton_send")
        self.pushButton_send.setMinimumSize(QSize(65, 0))
        font1 = QFont()
        font1.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font1.setPointSize(10)
        font1.setBold(True)
        self.pushButton_send.setFont(font1)
        self.pushButton_send.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")

        self.horizontalLayout.addWidget(self.pushButton_send)

        self.horizontalSpacer = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_5 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setMinimumSize(QSize(65, 0))
        self.pushButton_5.setFont(font1)
        self.pushButton_5.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")

        self.horizontalLayout.addWidget(self.pushButton_5)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 60, 371, 30))
        font2 = QFont()
        font2.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font2.setPointSize(10)
        self.label_2.setFont(font2)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(10, 90, 371, 151))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(0, 29))
        font3 = QFont()
        font3.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        self.lineEdit.setFont(font3)
        self.lineEdit.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lineEdit.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_title.setText(QCoreApplication.translate("Form", u"\ubc1b\uc740 \uba54\uc2dc\uc9c0", None))
        self.pushButton_send.setText(QCoreApplication.translate("Form", u"\ub2f5\uc7a5", None))
        self.pushButton_5.setText(QCoreApplication.translate("Form", u"\ub2eb\uae30", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\ubcf4\ub0b8 \uc0ac\ub78c :", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\uba54\uc2dc\uc9c0\ub97c \uc785\ub825\ud558\uc138\uc694.", None))
    # retranslateUi

