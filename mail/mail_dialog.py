# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mail_dialog.ui'
#
# Created: Fri Apr 14 19:35:02 2017
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MailDialog(object):
    def setupUi(self, MailDialog):
        MailDialog.setObjectName(_fromUtf8("MailDialog"))
        MailDialog.resize(266, 77)
        self.gridLayoutWidget = QtGui.QWidget(MailDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 261, 71))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButton_dir = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButton_dir.setObjectName(_fromUtf8("pushButton_dir"))
        self.gridLayout.addWidget(self.pushButton_dir, 1, 0, 1, 1)
        self.pushButton_file = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButton_file.setObjectName(_fromUtf8("pushButton_file"))
        self.gridLayout.addWidget(self.pushButton_file, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.retranslateUi(MailDialog)
        QtCore.QMetaObject.connectSlotsByName(MailDialog)

    def retranslateUi(self, MailDialog):
        MailDialog.setWindowTitle(QtGui.QApplication.translate("MailDialog", "Mail Option", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_dir.setText(QtGui.QApplication.translate("MailDialog", "Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_file.setText(QtGui.QApplication.translate("MailDialog", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MailDialog", "<html><head/><body><p>Attach only file or whole directory?</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

