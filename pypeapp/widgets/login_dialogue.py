# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\CODE\github\pypeclub\pype-setup\temp\pype_project_settins_ui\login_dialogue.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

import sys
from Qt import QtCore, QtGui, QtWidgets

from pypeapp import style

SIZE_W = 250
SIZE_H = 200


class Login_Dialog_ui(object):
    def __init__(self):
        super(Login_Dialog_ui, self).__init__()
        self.Dialog = QtWidgets.QDialog()
        self.Dialog.setStyleSheet(style.load_stylesheet())
        self.Dialog.setObjectName("Dialog")
        self.Dialog.resize(SIZE_W, SIZE_H)
        self.Dialog.setMinimumSize(QtCore.QSize(SIZE_W, SIZE_H))
        self.verticalLayoutWidget = QtWidgets.QWidget(self.Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, SIZE_W + 1, SIZE_H + 1))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(10, 5, 10, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.user_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user_label.sizePolicy().hasHeightForWidth())
        self.user_label.setSizePolicy(sizePolicy)
        self.user_label.setMinimumSize(QtCore.QSize(150, 28))
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Condensed")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(50)
        font.setKerning(True)
        self.user_label.setFont(font)
        self.user_label.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.user_label.setTextFormat(QtCore.Qt.RichText)
        self.user_label.setObjectName("user_label")
        self.verticalLayout.addWidget(self.user_label)
        self.user_input = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.user_input.setEnabled(True)
        self.user_input.setFrame(True)
        self.user_input.setObjectName("user_input")
        self.verticalLayout.addWidget(self.user_input)
        self.passw_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.passw_label.sizePolicy().hasHeightForWidth())
        self.passw_label.setSizePolicy(sizePolicy)
        self.passw_label.setMinimumSize(QtCore.QSize(150, 28))
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Condensed")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(50)
        font.setKerning(True)
        self.passw_label.setFont(font)
        self.passw_label.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.passw_label.setTextFormat(QtCore.Qt.RichText)
        self.passw_label.setObjectName("passw_label")
        self.verticalLayout.addWidget(self.passw_label)
        self.passw_input = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.passw_input.setEnabled(True)
        self.passw_input.setInputMethodHints(
            QtCore.Qt.ImhHiddenText | QtCore.Qt.ImhNoAutoUppercase | QtCore.Qt.ImhNoPredictiveText | QtCore.Qt.ImhSensitiveData)
        self.passw_input.setInputMask("")
        self.passw_input.setText("")
        self.passw_input.setFrame(True)
        self.passw_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passw_input.setReadOnly(False)
        self.passw_input.setObjectName("passw_input")
        self.verticalLayout.addWidget(self.passw_input)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(self.Dialog)
        self.buttonBox.accepted.connect(self.execute)
        self.buttonBox.rejected.connect(self.Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(self.Dialog)
        self.Dialog.setTabOrder(self.user_input, self.passw_input)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.user_label.setText(_translate("Dialog", "user-name or email"))
        self.user_input.setPlaceholderText(_translate("Dialog", "john.newman"))
        self.passw_label.setText(_translate("Dialog", "password"))
        self.passw_input.setPlaceholderText(_translate("Dialog", "*******"))

    def show(self):
        self.Dialog.show()


class Login_Dialog(Login_Dialog_ui):
    def __init__(self):
        super(Login_Dialog, self).__init__()
        self.user_input.textChanged.connect(self.user_changed)
        self.passw_input.textChanged.connect(self.passwd_changed)

    def user_changed(self):
        print(self.user_input.text())

    def passwd_changed(self):
        print(self.passw_input.text())

    def execute(self):
        user = self.user_input.text()
        passwd = self.passw_input.text()
        print(user)
        print(passwd)
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Login_Dialog()
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

# main()
