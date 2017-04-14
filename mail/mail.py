# ********************************* #
# author: Blas Florian              #
# e-mail: florian.blas[at]gmail.com #
# ********************************* #
from .mail_dialog import Ui_MailDialog
from PyQt4.QtGui import QDialog
import webbrowser
import shutil


class Mail(QDialog, Ui_MailDialog):

    def __init__(self, map_exporter):
        super(Mail, self).__init__()
        self.setupUi(self)
        self.map_exporter = map_exporter

        # connect signals
        self.pushButton_dir.clicked.connect(self.attach_dir)
        self.pushButton_file.clicked.connect(self.attach_file)

        self.mail_str = "mailto:"

    def open_mail_client(self):
        webbrowser.open(self.mail_str, new=1)
        self.close()

    def attach_dir(self):
        directory = self.map_exporter.dockwidget.lineEdit_dir.text()
        shutil.make_archive("qgis_mail.zip", "zip", directory)
        self.mail_str += "&attachment=\"{}\"".format(directory + "/qgis_mail.zip")
        pass

    def attach_file(self):
        filepath = self.map_exporter.export()
        self.mail_str += "&attachment=\"{}\"".format(filepath)

