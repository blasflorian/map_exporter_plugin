# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help_dialog.ui'
#
# Created: Wed Apr 12 14:26:07 2017
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QUrl
from ..plugin_path import get_plugin_path

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_HelpDialog(object):
    def setupUi(self, HelpDialog):
        HelpDialog.setObjectName(_fromUtf8("HelpDialog"))
        HelpDialog.resize(628, 519)
        self.buttonBox = QtGui.QDialogButtonBox(HelpDialog)
        self.buttonBox.setGeometry(QtCore.QRect(270, 480, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.webView = QtWebKit.QWebView(HelpDialog)
        self.webView.setGeometry(QtCore.QRect(0, 0, 631, 471))
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.webView.load(QUrl("file:///" + get_plugin_path() + "/help/help.html"))

        self.retranslateUi(HelpDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), HelpDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HelpDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(HelpDialog)

    def retranslateUi(self, HelpDialog):
        HelpDialog.setWindowTitle(QtGui.QApplication.translate("HelpDialog", "Help", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
