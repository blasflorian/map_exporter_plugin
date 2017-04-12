from MapExporter.help.help_dialog import Ui_HelpDialog
from PyQt4.QtGui import QDialog


class Help(QDialog, Ui_HelpDialog):

    def __init__(self):
        super(Help, self).__init__()
        self.setupUi(self)