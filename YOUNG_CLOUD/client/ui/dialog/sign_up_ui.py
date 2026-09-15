# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sign_up_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 550)
        Form.setStyleSheet(u"background-color: rgb(239, 248, 241);")
        self.label_title = QLabel(Form)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QRect(10, 20, 91, 31))
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
        self.gridLayoutWidget = QWidget(Form)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(14, 80, 371, 261))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_3 = QPushButton(self.gridLayoutWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        font1 = QFont()
        font1.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font1.setBold(True)
        self.pushButton_3.setFont(font1)
        self.pushButton_3.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")

        self.gridLayout.addWidget(self.pushButton_3, 2, 2, 1, 1)

        self.lineEdit_4 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_4.sizePolicy().hasHeightForWidth())
        self.lineEdit_4.setSizePolicy(sizePolicy)
        self.lineEdit_4.setMaximumSize(QSize(16777215, 29))
        font2 = QFont()
        font2.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        self.lineEdit_4.setFont(font2)
        self.lineEdit_4.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lineEdit_4.setInputMethodHints(Qt.InputMethodHint.ImhNone)

        self.gridLayout.addWidget(self.lineEdit_4, 3, 1, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        font3 = QFont()
        font3.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font3.setPointSize(10)
        self.label_3.setFont(font3)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font3)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font3)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.pushButton_2 = QPushButton(self.gridLayoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setFont(font1)
        self.pushButton_2.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")

        self.gridLayout.addWidget(self.pushButton_2, 1, 2, 1, 1)

        self.pushButton = QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setFont(font1)
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")

        self.gridLayout.addWidget(self.pushButton, 0, 2, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font3)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.lineEdit = QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QSize(0, 29))
        self.lineEdit.setFont(font2)
        self.lineEdit.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lineEdit.setInputMethodHints(Qt.InputMethodHint.ImhNone)

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.lineEdit_5 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        sizePolicy.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy)
        self.lineEdit_5.setMaximumSize(QSize(16777215, 29))
        self.lineEdit_5.setFont(font2)
        self.lineEdit_5.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lineEdit_5.setInputMethodHints(Qt.InputMethodHint.ImhNone)

        self.gridLayout.addWidget(self.lineEdit_5, 4, 1, 1, 1)

        self.lineEdit_2 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMaximumSize(QSize(16777215, 29))
        self.lineEdit_2.setFont(font2)
        self.lineEdit_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lineEdit_2.setInputMethodHints(Qt.InputMethodHint.ImhNone)

        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font3)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        sizePolicy.setHeightForWidth(self.lineEdit_3.sizePolicy().hasHeightForWidth())
        self.lineEdit_3.setSizePolicy(sizePolicy)
        self.lineEdit_3.setMaximumSize(QSize(16777215, 29))
        self.lineEdit_3.setFont(font2)
        self.lineEdit_3.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lineEdit_3.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText|Qt.InputMethodHint.ImhNoAutoUppercase|Qt.InputMethodHint.ImhNoPredictiveText|Qt.InputMethodHint.ImhSensitiveData)
        self.lineEdit_3.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 1)

        self.pushButton_7 = QPushButton(self.gridLayoutWidget)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setFont(font1)
        self.pushButton_7.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")
        icon = QIcon()
        icon.addFile(u"../source/image/search.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_7.setIcon(icon)

        self.gridLayout.addWidget(self.pushButton_7, 4, 2, 1, 1)

        self.horizontalLayoutWidget = QWidget(Form)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(110, 470, 181, 51))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_4 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setMinimumSize(QSize(65, 0))
        font4 = QFont()
        font4.setFamilies([u"\ub098\ub214\uc2a4\ud018\uc5b4"])
        font4.setPointSize(10)
        font4.setBold(True)
        self.pushButton_4.setFont(font4)
        self.pushButton_4.setStyleSheet(u"QPushButton {\n"
"                background-color: #63F2F2;\n"
"                color: #333333;\n"
"                border-radius: 5px;\n"
"                padding: 8px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #66E4F2;\n"
"            }")

        self.horizontalLayout.addWidget(self.pushButton_4)

        self.horizontalSpacer = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_5 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setMinimumSize(QSize(65, 0))
        self.pushButton_5.setFont(font4)
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

        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(13, 351, 55, 29))
        self.label_6.setFont(font3)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.gridLayoutWidget_2 = QWidget(Form)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(79, 344, 281, 80))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.radioButton = QRadioButton(self.gridLayoutWidget_2)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton, 0, 0, 1, 1)

        self.radioButton_2 = QRadioButton(self.gridLayoutWidget_2)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton_2, 0, 1, 1, 1)

        self.radioButton_3 = QRadioButton(self.gridLayoutWidget_2)
        self.radioButton_3.setObjectName(u"radioButton_3")
        self.radioButton_3.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton_3, 1, 0, 1, 1)

        self.radioButton_4 = QRadioButton(self.gridLayoutWidget_2)
        self.radioButton_4.setObjectName(u"radioButton_4")
        self.radioButton_4.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton_4, 1, 1, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_title.setText(QCoreApplication.translate("Form", u"\ud68c\uc6d0\uac00\uc785", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"\ube44\ubc00\ubc88\ud638 \ud655\uc778", None))
        self.lineEdit_4.setPlaceholderText("")
        self.label_3.setText(QCoreApplication.translate("Form", u"\ube44\ubc00\ubc88\ud638 :", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\uc774\uba54\uc77c :", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\uc774\ub984 :", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\uc778\uc99d\ud655\uc778", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\uc778\uc99d\ucf54\ub4dc\ubc1c\uc1a1", None))
        self.label.setText(QCoreApplication.translate("Form", u"\uc778\uc99d\ucf54\ub4dc :", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"ex)a1234@gmail.com", None))
        self.lineEdit_5.setPlaceholderText("")
        self.lineEdit_2.setPlaceholderText("")
        self.label_5.setText(QCoreApplication.translate("Form", u"\ud68c\uc0ac\uba85 :", None))
        self.lineEdit_3.setPlaceholderText(QCoreApplication.translate("Form", u"\uc601\ubb38,\uc22b\uc790,\ud2b9\uc218\ubb38\uc790 \ud3ec\ud568 \uc870\ud569 8-20\uc790", None))
        self.pushButton_7.setText(QCoreApplication.translate("Form", u"\ud68c\uc0ac\uac80\uc0c9", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"\uac00\uc785\ud558\uae30", None))
        self.pushButton_5.setText(QCoreApplication.translate("Form", u"\ub2eb\uae30", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\ub4f1\uae09 :", None))
        self.radioButton.setText(QCoreApplication.translate("Form", u"\uc77c\ubc18(\ucd5c\ub300100MB)", None))
        self.radioButton_2.setText(QCoreApplication.translate("Form", u"\ube44\uc9c0\ub2c8\uc2a4(\ucd5c\ub300200MB)", None))
        self.radioButton_3.setText(QCoreApplication.translate("Form", u"VIP(\ucd5c\ub300500MB)", None))
        self.radioButton_4.setText(QCoreApplication.translate("Form", u"VVIP(\ucd5c\ub3001GB)", None))
    # retranslateUi

