# ********************************* #
# author: Blas Florian              #
# e-mail: florian.blas[at]gmail.com #
# ********************************* #
import os
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsComposition
from qgis.utils import iface

from plugin_path import get_plugin_path


class FileExporter:

    def __init__(self, dockwidget):
        self.templates = {"Only map": "/resources/tmpl.qpt", "Map with legend": "/resources/tmpl_legend.qpt"}
        self.dockwidget = dockwidget

    def load_composition(self):
        template_path = get_plugin_path() + self.templates[self.dockwidget.comboBox_template.currentText()]
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

        # set legend
        try:
            legend_item = composition.getComposerItemById("legend")
            legend_item.updateLegend()
        except AttributeError:  # in case first template was selected
            pass

        composition.refreshItems()
        return composition

    def create_png(self, path):
        c = self.load_composition()
        img = c.printPageAsRaster(0)
        if img.save(path, "png"):
            iface.messageBar().pushMessage("PNG file {} successfully exported!".format(path), duration=5)
        else:
            iface.messageBar().pushMessage("Error while exporting png file {}".format(path), duration=5)

    def create_pdf(self, path):
        c = self.load_composition()
        if c.exportAsPDF(path):
            iface.messageBar().pushMessage("PDF file {} successfully exported".format(path), duration=5)
        else:
            iface.messageBar().pushMessage("Error while exporting pdf file {}".format(path), duration=5)

    def get_templates(self):
        return [template for template in self.templates.keys()]

