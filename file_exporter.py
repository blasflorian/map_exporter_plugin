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
        """ Constructor. Saves path to templates
            
            :param dockwidget: the main dockwidget
            :type dockwidget: QDockWidget
        """
        self.templates = {"Only map": "/resources/tmpl.qpt", "Map with legend": "/resources/tmpl_legend.qpt"}
        self.dockwidget = dockwidget

    def load_composition(self):
        """ Creates the composition object (which is needed for creating the file) from the template file.
            
            :returns: the composition object
            :rtype: QgsComposition
        """
        template_path = get_plugin_path() + self.templates[self.dockwidget.comboBox_template.currentText()]
        template_file = open(template_path, "r")
        content = template_file.read()
        template_file.close()

        # the method from QgsComposition for loading the template needs to be a QDomDocument
        document = QDomDocument()
        document.setContent(content)

        # composition = QgsComposition(iface.mapCanvas().mapSettings()) does not work
        #TODO: is deprecated but works ...fix in new version https://hub.qgis.org/issues/11077
        composition = QgsComposition(iface.mapCanvas().mapRenderer())
        if not composition.loadFromTemplate(document):
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
        """ Creates the png file
        
            :param path: the file path
            :type path: str
        """
        c = self.load_composition()
        img = c.printPageAsRaster(0)
        if img.save(path, "png"):
            iface.messageBar().pushMessage("PNG file {} successfully exported!".format(path), duration=5)
        else:
            iface.messageBar().pushMessage("Error while exporting png file {}".format(path), duration=5)

    def create_pdf(self, path):
        """ Creates the pdf file
        
            :param path: the file path
            :type path: str
        """
        c = self.load_composition()
        if c.exportAsPDF(path):
            iface.messageBar().pushMessage("PDF file {} successfully exported".format(path), duration=5)
        else:
            iface.messageBar().pushMessage("Error while exporting pdf file {}".format(path), duration=5)

    def get_templates(self):
        """ Creates a list of available templates
        
            :returns: a list of template descriptions
            :rtype: list-of-str
        """
        return [template for template in self.templates.keys()]

