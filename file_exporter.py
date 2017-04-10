# ********************************* #
# author: Blas Florian              #
# e-mail: florian.blas[at]gmail.com #
# ********************************* #
import os
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsComposition
from qgis.utils import iface


class FileExporter:

    @staticmethod
    def load_composition():
        template_path = FileExporter.get_plugin_path() + "/resources/tmpl.qpt"
        template_file = open(template_path, "r")
        content = template_file.read()
        template_file.close()

        document = QDomDocument()
        document.setContent(content)
        # composition = QgsComposition(iface.mapCanvas().mapSettings())

        #TODO: is deprecated but works ...fix in new version https://hub.qgis.org/issues/11077
        composition = QgsComposition(iface.mapCanvas().mapRenderer())
        composition.loadFromTemplate(document)

        if not composition.loadFromTemplate(document):  # load template
            iface.messageBar().pushMessage("Error while loading template!")
            return

        # set map
        map_item = composition.getComposerItemById("map")
        map_item.setMapCanvas(iface.mapCanvas())
        map_item.zoomToExtent(iface.mapCanvas().extent())
        composition.refreshItems()
        return composition

    @staticmethod
    def create_png(path):
        c = FileExporter.load_composition()
        img = c.printPageAsRaster(0)
        if img.save(path, "png"):
            iface.messageBar().pushMessage("PNG file successfully exported!", duration=5)
        else:
            iface.messageBar().pushMessage("Error while exporting png file", duration=5)

    @staticmethod
    def create_pdf(path):
        c = FileExporter.load_composition()
        if c.exportAsPDF(path):
            iface.messageBar().pushMessage("PDF file successfully exported", duration=5)
        else:
            iface.messageBar().pushMessage("Error while exporting pdf file", duration=5)

    @staticmethod
    def get_plugin_path():
        return os.path.dirname(os.path.realpath(__file__))

