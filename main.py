# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapExporter
                                 A QGIS plugin
 Exports the current map
                              -------------------
        begin                : 2017-04-10
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Florian Blas
        email                : florian.blas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import time
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSlot
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
import ConfigParser
# Initialize Qt resources from file resources.py
import resources
from qgis.utils import iface
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMessageBar

# Import the code for the DockWidget
from file_exporter import FileExporter
from help.help import Help
from main_dockwidget import MapExporterDockWidget
import os.path

from plugin_path import get_plugin_path


class MapExporter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MapExporter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Map Exporter')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'MapExporter')
        self.toolbar.setObjectName(u'MapExporter')

        self.pluginIsActive = False
        self.dockwidget = None
        self.cfg_file = get_plugin_path() + "/resources/usr.cfg"
        self.file_exporter = None

        self.dlg_help = Help()

        # save the ids according to path names
        self.labeling_ids = {}

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MapExporter', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MapExporter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Map Exporter'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.dockwidget.pushButton_dir.clicked.disconnect(self.open_dir)
        self.dockwidget.pushButton_export.clicked.disconnect(self.on_export)
        self.dockwidget.checkBox_all.clicked.disconnect(self.on_checkbox_clicked)
        self.iface.legendInterface().currentLayerChanged.disconnect(self.update_dropdown)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False
        self.save_cfg()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Map Exporter'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that loads and starts the plugin"""
        if len(QgsMapLayerRegistry.instance().mapLayers().values()) == 0:
            self.iface.messageBar().pushMessage("There must be at least one layer loaded!", level=QgsMessageBar.CRITICAL)
            return

        if not self.pluginIsActive:
            self.pluginIsActive = True
            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = MapExporterDockWidget()
                self.file_exporter = FileExporter(self.dockwidget)
                self.load_cfg()

            # connect signals
            self.dockwidget.pushButton_dir.clicked.connect(self.open_dir)
            self.dockwidget.pushButton_export.clicked.connect(self.on_export)
            self.dockwidget.pushButton_help.clicked.connect(lambda : self.dlg_help.exec_())
            self.dockwidget.checkBox_all.clicked.connect(self.on_checkbox_clicked)
            self.iface.legendInterface().currentLayerChanged.connect(self.update_dropdown)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # adjust combo boxes
            self.dockwidget.comboBox_fields.setVisible(False)
            self.dockwidget.comboBox_template.addItems(self.file_exporter.get_templates())

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    @pyqtSlot()
    def open_dir(self):
        """Lets the user choose a directory."""
        dir_path = QFileDialog.getExistingDirectory(self.dockwidget, "Choose Directory", self.dockwidget.lineEdit_dir.text())
        self.dockwidget.lineEdit_dir.setText(dir_path)

    @pyqtSlot()
    def update_dropdown(self):
        """ Updates dropdown list. If multiple layers are selected, only those fields occurring in every layer
            can be options for the user to choose from
        """
        self.dockwidget.comboBox_fields.clear()
        if len(self.iface.legendInterface().selectedLayers()) >= 2:
            fields = []
            for layer in self.iface.legendInterface().selectedLayers():
                fields.append(set([field.name() for field in layer.pendingFields()]))   # cast to set to use intersection method
            intersected_fields = set.intersection(*fields)
            self.dockwidget.comboBox_fields.addItems(list(intersected_fields))
        else:
            fields = [field.name() for field in self.iface.activeLayer().pendingFields()]
            self.dockwidget.comboBox_fields.addItems(fields)

    @pyqtSlot()
    def on_checkbox_clicked(self):
        if self.dockwidget.checkBox_all.isChecked():
            self.dockwidget.lineEdit_filename.setText(self.dockwidget.lineEdit_filename.text() + "_{layername}-{choose_field}")
            self.dockwidget.comboBox_fields.setVisible(True)
            self.update_dropdown()
        else:
            self.dockwidget.lineEdit_filename.setText("")
            self.dockwidget.comboBox_fields.setVisible(False)

    @pyqtSlot()
    def on_export(self):
        if self.dockwidget.checkBox_all.isChecked():
            for layer in self.iface.legendInterface().selectedLayers():
                self.export_all_features(layer)
        else:
            self.export()

    def export_all_features(self, layer):
        """ Exports every feature of a layer
        
            :param layer: the layer of which the features should be exported 
            :type layer: QgsVectorLayer
        """
        if layer.featureCount() == 0:
            self.iface.messageBar().pushMessage("Layer has no features", duration=5)
            return
        elif layer.featureCount() >= 100:
            answer = QMessageBox.question(self.dockwidget, "Warning", "Layer contains a lot of features. This could take a lot of time. Continue?", QMessageBox.Yes|QMessageBox.No)
            if answer == QMessageBox.No:
                return

        self.iface.legendInterface().setLayerVisible(layer, True)   # just in case user forgot
        self.iface.setActiveLayer(layer)    # set layer active so automatic labeling works
        for feat in layer.getFeatures():    # zoom to every feature to export it
            layer.setSelectedFeatures([feat.id()])
            self.iface.mapCanvas().zoomToSelected()
            self.iface.mapCanvas().refresh()
            layer.removeSelection()
            self.export(feat)

    def export(self, feat=None):
        """ Exports the current map view
        
            :param feat: the feature that is currently exported
            :type feat: QgsFeature
        """
        self.dockwidget.pushButton_export.setEnabled(False)     # a hint for the user if export is in progress
        png = self.dockwidget.checkBox_png.isChecked()
        pdf = self.dockwidget.checkBox_pdf.isChecked()
        filename = self.get_file_name(feat)
        if os.path.isdir(self.dockwidget.lineEdit_dir.text()) and len(filename) != 0:
            if png and pdf:
                filepath_png = self.create_path(self.dockwidget.lineEdit_dir.text(), filename, "png")
                filepath_pdf = self.create_path(self.dockwidget.lineEdit_dir.text(), filename, "pdf")
                if self.file_exists(filepath_png):
                    self.file_exporter.create_png(filepath_png)
                if self.file_exists(filepath_pdf):
                    self.file_exporter.create_pdf(filepath_pdf)
            elif png:
                filepath = self.create_path(self.dockwidget.lineEdit_dir.text(), filename, "png")
                if self.file_exists(filepath):
                    self.file_exporter.create_png(filepath)
            elif pdf:
                filepath = self.create_path(self.dockwidget.lineEdit_dir.text(), filename, "pdf")
                if self.file_exists(filepath):
                    self.file_exporter.create_pdf(filepath)
        else:
            self.iface.messageBar().pushMessage("Directory does not exist or no file name given!")
        self.dockwidget.pushButton_export.setEnabled(True)

    def create_path(self, dir, filename, type):
        """ Builds the path of the file. If the user wants to use a sequential id, replace the keyword with the
            right id for the path
            
            :param dir: the directory
            :type dir: str
            
            :param filename: the file name
            :type filename: str
            
            :param type: the document type (pdf or png)
            :type type: str
            
            :returns: the full path of the file
            :rtype: str
        """
        path = dir + "/" + filename + "." + type
        if "id_key" in filename:    # check if user wants to use id labeling feature
            return path.replace("id_key", str(self.get_labeling_id(path)))
        return path

    def get_labeling_id(self, path):
        """ Looks up the correct sequential number corresponding to the path or create a dictionary entry for
            the path. Basically this is just counting how often the name of the path occurred.
        
            :param path: the path of the file
            :type path: str
            
            :returns: the id of the path
            :rtype: int
        """
        if path in self.labeling_ids.keys():
            self.labeling_ids[path] += 1
        else:
            self.labeling_ids[path] = 1
        return self.labeling_ids[path]

    def file_exists(self, path):
        """ Checks if the file already exists and asks user how to proceed
        
            :param path: the file path
            :type path: str
            
            :returns: if saving should be proceeded
            :rtype: bool
        """
        if os.path.isfile(path):
            answer = QMessageBox.question(self.dockwidget, "Warning", "File {} exists. Override?".format(path), QMessageBox.Yes|QMessageBox.No)
            if answer == QMessageBox.No:
                return False
        return True

    def get_file_name(self, feat=None):
        """ Constructs the file name. User can enter keywords which need to be replaced with their current values.
            
            :param feat: the feature that is currently exported
            :type feat: QgsFeature
            
            :returns: the file name
            :rtype: str
        """
        keywords = {"layername": self.iface.activeLayer().name(), "id": "id_key", "date": time.strftime("%x").replace("/", "-")}    # specify available keywords
        if self.dockwidget.checkBox_all.isChecked():
            keywords["choose_field"] = str(feat.attribute(self.dockwidget.comboBox_fields.currentText()))
        text = self.dockwidget.lineEdit_filename.text()     # get user input
        keywords_in_text = [fname for _, fname, _, _ in text._formatter_parser()]   # find the entered keywords
        if len(keywords_in_text) > 0 and (None not in keywords_in_text):    # if there are no keywords list has one element which is None
            # get the corresponding methods in correct order of appearance
            methods = []
            for key in keywords_in_text:
                if key in keywords.keys():
                    methods.append(keywords[key])
                else:
                    self.iface.messageBar().pushMessage("Keyword {} doesn't exist!".format(key), level=QgsMessageBar.CRITICAL)
                    text = text.replace("{" + key + "}", "")    # delete none existing keywords
            if len(methods) == 0:   # check if there are still any valid keywords left after potentially deleting some invalid ones
                return text
            for keyword in keywords_in_text:
                text = text.replace(keyword, "")   # delete keywords so formatting works without them
            return text.format(*methods)    # format by unpacking methods since these are in the right order
        else:
            return text

    def load_cfg(self):
        """Loads settings from the user config file"""
        cfg = ConfigParser.RawConfigParser()
        cfg.read(self.cfg_file)
        self.dockwidget.checkBox_png.setChecked(cfg.getboolean("PNG", "clicked"))
        self.dockwidget.checkBox_pdf.setChecked(cfg.getboolean("PDF", "clicked"))
        self.dockwidget.lineEdit_dir.setText(cfg.get("Directory", "path"))

    def save_cfg(self):
        """Saves settings so user does not have to reenter every option"""
        cfg = ConfigParser.SafeConfigParser()
        cfg.read(self.cfg_file)
        cfg.set("PNG", "clicked", str(self.dockwidget.checkBox_png.isChecked()))
        cfg.set("PDF", "clicked", str(self.dockwidget.checkBox_pdf.isChecked()))
        cfg.set("Directory", "path", str(self.dockwidget.lineEdit_dir.text()))
        cfg_file = open(self.cfg_file, "w")
        cfg.write(cfg_file)

