# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(400, 250)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginDialog.sizePolicy().hasHeightForWidth())
        LoginDialog.setSizePolicy(sizePolicy)
        LoginDialog.setMinimumSize(QtCore.QSize(400, 250))
        LoginDialog.setMaximumSize(QtCore.QSize(400, 250))
        self.verticalLayout = QtWidgets.QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.bannerLabel = QtWidgets.QLabel(LoginDialog)
        self.bannerLabel.setMinimumSize(QtCore.QSize(350, 70))
        self.bannerLabel.setMaximumSize(QtCore.QSize(350, 70))
        self.bannerLabel.setText("")
        self.bannerLabel.setTextFormat(QtCore.Qt.RichText)
        self.bannerLabel.setPixmap(QtGui.QPixmap("Resources/ZSpotifyBannerTP.png"))
        self.bannerLabel.setScaledContents(True)
        self.bannerLabel.setObjectName("bannerLabel")
        self.verticalLayout_2.addWidget(self.bannerLabel)
        self.loginInfoLabel = QtWidgets.QLabel(LoginDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loginInfoLabel.sizePolicy().hasHeightForWidth())
        self.loginInfoLabel.setSizePolicy(sizePolicy)
        self.loginInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.loginInfoLabel.setObjectName("loginInfoLabel")
        self.verticalLayout_2.addWidget(self.loginInfoLabel)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.usernameInput = QtWidgets.QLineEdit(LoginDialog)
        self.usernameInput.setMinimumSize(QtCore.QSize(200, 0))
        self.usernameInput.setMaximumSize(QtCore.QSize(200, 16777215))
        self.usernameInput.setObjectName("usernameInput")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.usernameInput)
        self.label_2 = QtWidgets.QLabel(LoginDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.passwordInput = QtWidgets.QLineEdit(LoginDialog)
        self.passwordInput.setMinimumSize(QtCore.QSize(200, 0))
        self.passwordInput.setMaximumSize(QtCore.QSize(200, 16777215))
        self.passwordInput.setInputMethodHints(QtCore.Qt.ImhNone)
        self.passwordInput.setInputMask("")
        self.passwordInput.setObjectName("passwordInput")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.passwordInput)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelBtn = QtWidgets.QPushButton(LoginDialog)
        self.cancelBtn.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelBtn.sizePolicy().hasHeightForWidth())
        self.cancelBtn.setSizePolicy(sizePolicy)
        self.cancelBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelBtn.setObjectName("cancelBtn")
        self.horizontalLayout.addWidget(self.cancelBtn)
        self.loginBtn = QtWidgets.QPushButton(LoginDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loginBtn.sizePolicy().hasHeightForWidth())
        self.loginBtn.setSizePolicy(sizePolicy)
        self.loginBtn.setObjectName("loginBtn")
        self.horizontalLayout.addWidget(self.loginBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(LoginDialog)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Login"))
        self.loginInfoLabel.setText(_translate("LoginDialog", "Enter Spotify credentials."))
        self.label.setText(_translate("LoginDialog", "Username:"))
        self.label_2.setText(_translate("LoginDialog", "Password:"))
        self.cancelBtn.setText(_translate("LoginDialog", "Cancel"))
        self.loginBtn.setText(_translate("LoginDialog", "Login"))
