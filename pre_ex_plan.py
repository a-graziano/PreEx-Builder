# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PreExPlan
                                 A QGIS plugin
 This plugin allows you to create a shp from scratch to digitize the pre ex features, classify them according to type and extrapolate their respective dimensions. It also allows you to calculate the m2 to be excavated for each single feature.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-10-27
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Alessio Graziano
        email                : alessio.graz@gmail.com
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

from urllib import parse
from datetime import datetime as dt
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QColor
from PyQt5 import QtWidgets
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt import QtGui
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QInputDialog, QLineEdit
from qgis.core import QgsProject,QgsVectorLayer, QgsField, Qgis, QgsStyle, QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsMessageLog, QgsVectorDataProvider, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsVectorFileWriter, QgsFeatureRequest, QgsProcessingProvider, QgsProcessingAlgorithm, QgsPoint, QgsFeature, QgsGeometry, QgsFillSymbol
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QAction
from PyQt5.Qt import *
from qgis.utils import iface
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .pre_ex_plan_dockwidget import PreExPlanDockWidget
from .msgBox.infoScript import InfoBox
from .msgBox.infoSelect import InfoDupl
from .msgBox.infoPeriod import InfoPer
from .msgBox.infoPhase import InfoPhase
from .msgBox.SlotStat import SlotStat
from .msgBox.SlotTime import SlotTime
import os
import pandas as pd
import qgis
import processing
import os.path
import sys



class PreExPlan():
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
            'PreExPlan_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pre Ex Builder')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PreExPlan')
        self.toolbar.setObjectName(u'PreExPlan')

        #print "** INITIALIZING PreExPlan"

        self.pluginIsActive = False
        self.dockwidget = None
        self.mgm = None


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
        return QCoreApplication.translate('PreExPlan', message)


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

        icon_path = ':/plugins/pre_ex_plan/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Create a Pre Ex Plan'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING PreExPlan"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD PreExPlan"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pre Ex Builder'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

#Generate a new Pre Ex memory layer
    def new_shp(self):
        vl = QgsVectorLayer("polygon", "(mitig_area)_PreExPlan", "memory")

        vl.startEditing()

        pr = vl.dataProvider()
        pr.addAttributes([QgsField("Interpr", QVariant.String),
                        QgsField("site", QVariant.String,'string',30),
                        QgsField("mitig_area", QVariant.String),
                        QgsField("label", QVariant.String),
                        QgsField("Area", QVariant.Double, 'double',10,2),
                        QgsField("Length", QVariant.Double, 'double',10,2),
                        QgsField("Diameter", QVariant.Double, 'double', 10,2),
                        QgsField("Period", QVariant.String),
                        QgsField("Phase",QVariant.String,'string', 30),
                        QgsField("X", QVariant.Double, 'double', 10, 3),
                        QgsField("Y",QVariant.Double, 'double', 10, 3),
                        QgsField("Percentage", QVariant.Int),
                        QgsField("m2ToDig", QVariant.Double,'double',10,2 ),
                        ])
        vl.updateFields()

        qml_path = os.path.join(os.path.dirname(__file__), 'style/preex.qml')

        vl.loadNamedStyle(qml_path)

        QgsProject.instance().addMapLayer(vl)


#Generate a new SLOT memory layer
    def slot_shp(self):
        vl = QgsVectorLayer("polygon", "(mitig_area)_Slot", "memory")

        pr = vl.dataProvider()
        pr.addAttributes([QgsField("site", QVariant.String, 'string',30),
                        QgsField("mitig_area", QVariant.String),
                        QgsField("status", QVariant.String),
                        QgsField("time",QVariant.String)])
        vl.updateFields()

        QgsProject.instance().addMapLayer(vl)

#Generate a new LOE memory layer
    def loe_shp(self):
        vl = QgsVectorLayer("polygon", "(mitig_area)_LOE", "memory")

        pr = vl.dataProvider()
        pr.addAttributes([QgsField("site", QVariant.String,'string',30),
                        QgsField("mitig_area", QVariant.String),
                        QgsField("Area", QVariant.Double, 'double', 10,0),
                        QgsField("Date", QVariant.Date)])

        vl.updateFields()


        symbol = QgsFillSymbol.createSimple({'style_border':'dash dot','width_border':'0.7' ,'color': '255,99,71,0'})

        vl.renderer().setSymbol(symbol)

        vl.triggerRepaint()


        QgsProject.instance().addMapLayer(vl)


#Add the column in the layer for built a personalised shp
    def addColum(self):
        widget_1 = iface.messageBar().createMessage("Geometry & Metrics Column added", "Success")
        vl = iface.activeLayer()
        pr = vl.dataProvider()
        pr.addAttributes([QgsField("Interpr", QVariant.String),
                        QgsField("Area", QVariant.Double, 'double',10,2),
                        QgsField("Length", QVariant.Double, 'double',10,2),
                        QgsField("Diameter", QVariant.Double, 'double', 10,2),
                        QgsField("X", QVariant.Double, 'double', 10, 3),
                        QgsField("Y",QVariant.Double, 'double', 10, 3),
                        QgsField("Percentage", QVariant.Int),
                        QgsField("m2ToDig", QVariant.Double,'double',10,2)])

        vl.updateFields()
        iface.messageBar().pushWidget(widget_1, Qgis.Info, duration = 3)



#Classified the layer follow the Interpr field
    def style_feat(self):
        layer = iface.activeLayer()

        qml_path = os.path.join(os.path.dirname(__file__), 'style/preex.qml')

        layer.loadNamedStyle(qml_path)

        QgsProject.instance().addMapLayer(layer)


#Classified the slot layer by period
    def style_feat_period(self):
        layer = iface.activeLayer()

        qml_path = os.path.join(os.path.dirname(__file__), 'style/period.qml')

        layer.loadNamedStyle(qml_path)

        QgsProject.instance().addMapLayer(layer)

#Classified the slot layer by status
    def style_slot(self):
        layer = iface.activeLayer()

        qml_path = os.path.join(os.path.dirname(__file__), 'style/slot_stat.qml')

        layer.loadNamedStyle(qml_path)

        QgsProject.instance().addMapLayer(layer)



#Classified the slot layer by time
    def slot_time(self):
        layer = iface.activeLayer()

        qml_path = os.path.join(os.path.dirname(__file__), 'style/slot_time.qml')

        layer.loadNamedStyle(qml_path)

        QgsProject.instance().addMapLayer(layer)


#Calculate the Area for each features
    def addArea(self):
        widget_7 = iface.messageBar().createMessage("Area Calculated", "Well Done")

        vl = iface.activeLayer()

        expression1 = QgsExpression('$area')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['Area'] = expression1.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()
        iface.messageBar().pushWidget(widget_7, Qgis.Success, duration = 3)

    #Calculate the Length and the Diameter
    def add_Measure(self,edit):
        widget_8 = iface.messageBar().createMessage("Measure Calculated", "Well Done")
        vl = iface.activeLayer()

        expression2 = QgsExpression('''case when "Interpr" = 'Linear' then $perimeter/2
                                    when "Interpr" = 'Grave' then $perimeter/2
                                    when "Interpr" = 'Structure' then $perimeter/2
                                    when "Interpr" = 'Furrow' then $perimeter/2
                                    end ''')
        expression3 = QgsExpression('''case when "Interpr" = 'Pit' then  2 * sqrt("Area"/pi())
                                    when "Interpr" = 'Posthole' then 2 * sqrt("Area"/pi())
                                    when "Interpr" = 'Cremation' then 2 * sqrt("Area"/pi())
                                    end ''')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()

        for f in vl.getFeatures():
            context.setFeature(f)
            f['Length'] = expression2.evaluate(context)
            f['Diameter'] = expression3.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()

        iface.messageBar().pushWidget(widget_8, Qgis.Success, duration = 3)

#Generate the x and y centroids field for each features
    def addCentroid(self):
        widget_9 = iface.messageBar().createMessage("Centroid added", "Well Done")
        vl = iface.activeLayer()

        expression1 = QgsExpression('xmin(centroid($geometry))')
        expression2 = QgsExpression('ymin(centroid($geometry))')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['X'] = expression1.evaluate(context)
            f['Y'] = expression2.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()

        iface.messageBar().pushWidget(widget_9, Qgis.Success, duration = 3)

#Calculate how many m2 we should dig follow the Percentage of each features
    def dig(self):
        widget_10 = iface.messageBar().createMessage("m2 to dig calculated", "Well Done")
        vl = iface.activeLayer()

        expression1 = QgsExpression('''case when "Interpr" = 'Linear' then '10'
                                        when "Interpr" = 'Grave' then '100'
                                        when "Interpr" = 'Pit' then '50'
                                        when "Interpr" = 'Posthole' then '50'
                                        when "Interpr" = 'Cremation' then '100'
                                        when "Interpr" = 'Structure' then '100'
                                        end ''')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['Percentage'] = expression1.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()

        expression2 = QgsExpression('(Area * Percentage)/100')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['m2ToDig'] = expression2.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()

        iface.messageBar().pushWidget(widget_10, Qgis.Success, duration = 3)

#Calculate how many sections and plan we produced for each features
    def est_secPlan(self):
        widget_11 = iface.messageBar().createMessage("Estimation complete", "Well Done")
        vl = iface.activeLayer()

        pr = vl.dataProvider()
        pr.addAttributes([QgsField("est.sec", QVariant.Int),
                    QgsField("est.plan", QVariant.Int)])

        vl.updateFields()

        expression1 = QgsExpression('''case when "Interpr" = 'Linear' then '3'
                                        when "Interpr" = 'Grave' then '1'
                                        when "Interpr" = 'Pit' then '1'
                                        when "Interpr" = 'Posthole' then '1'
                                        when "Interpr" = 'Cremation' then '1'
                                        when "Interpr" = 'Structure' then '1'
                                        end ''')

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['est.sec'] = expression1.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()

        expression2 = QgsExpression('''case when "Interpr" = 'Linear' then '3'
                                        when "Interpr" = 'Grave' then '1'
                                        when "Interpr" = 'Pit' then '1'
                                        when "Interpr" = 'Posthole' then '1'
                                        when "Interpr" = 'Cremation' then '1'
                                        when "Interpr" = 'Structure' then '3'
                                        end ''')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['est.plan'] = expression2.evaluate(context)
            vl.updateFeature(f)
        vl.commitChanges()

        iface.messageBar().pushWidget(widget_11, Qgis.Success, duration = 3)



#Generate an ID just follow the row number
    def unique_id(self):
        widget = iface.messageBar().createMessage("ID generated", "Well Done")

        vl=iface.activeLayer()

        ## join ID field
        myField1 = QgsField('ID', QVariant.Int, 'int', 1,0)
        vl.startEditing()
        vl.dataProvider().addAttributes([myField1])
        vl.updateFields()
        ID=vl.dataProvider().fieldNameIndex('ID')
        vl.commitChanges()


        expression3 = QgsExpression('$id')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['ID'] = expression3.evaluate(context)
            vl.updateFeature(f)


        vl.commitChanges()
        iface.messageBar().pushWidget(widget, Qgis.Success, duration = 3)

# add the Interpr column with the same code present in the Layer Column
    def interpr_column(self):
        widget_12 = iface.messageBar().createMessage("Interpretation added", "Well Done")
        vl = iface.activeLayer()

        pr = vl.dataProvider()
        pr.addAttributes([QgsField("Interpr", QVariant.String)])
        vl.updateFields()

        expression1 = QgsExpression("Layer")
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vl))

        vl.startEditing()
        for f in vl.getFeatures():
            context.setFeature(f)
            f['Interpr'] = expression1.evaluate(context)
            vl.updateFeature(f)

        vl.commitChanges()
        iface.messageBar().pushWidget(widget_12, Qgis.Success, duration = 3)



# convert the dxf in polygon shp and add the new layer on the canvas
    def convertDXF(self):
        widget_14 = iface.messageBar().createMessage("Success", "Well Done")

        layer = iface.activeLayer()

        feats = [feat for feat in layer.getFeatures()]

        temp = QgsVectorLayer("LineString?crs=epsg:27700",
                      "PreEx",
                      "memory")

        temp_data = temp.dataProvider()

        attr = layer.dataProvider().fields().toList()
        temp_data.addAttributes(attr)
        temp.updateFields()

        temp_data.addFeatures(feats)


        input_layer= iface.activeLayer()

        plan = processing.run("qgis:linestopolygons", {'INPUT':input_layer,'OUTPUT': 'memory:'})

        input_layer= iface.activeLayer()

        result = plan['OUTPUT']


        QgsProject.instance().addMapLayer(result)

        iface.messageBar().pushWidget(widget_14, Qgis.Success, duration = 3)


    def duplicate_l(self):
        layer = iface.activeLayer()

        memory_layer = layer.materialize(QgsFeatureRequest().setFilterFids(layer.allFeatureIds()))

        QgsProject.instance().addMapLayer(memory_layer)



    def selected_feat_copy(self):
        layer = iface.activeLayer()

        memory_layer = layer.materialize(QgsFeatureRequest().setFilterFids(layer.selectedFeatureIds()))

        QgsProject.instance().addMapLayer(memory_layer)


    def style_phasing(self):
        layer = iface.activeLayer()

        qml_path = os.path.join(os.path.dirname(__file__), 'style/phasing.qml')

        layer.loadNamedStyle(qml_path)

        QgsProject.instance().addMapLayer(layer)


# Functions to call all the message boxes
    def info2(self):
        self.mw = InfoBox()
        self.mw.show()

    def infoSel(self):
        self.mw = InfoDupl()
        self.mw.show()

    def info_prd(self):
        self.mw = InfoPer()
        self.mw.show()

    def info_phs(self):
        self.mw = InfoPhase()
        self.mw.show()

    def slot_stat(self):
        self.mw = SlotStat()
        self.mw.show()

    def slot_clock(self):
        self.mw = SlotTime()
        self.mw.show()



    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING PreExPlan"

            # dockwidget may not exist if:
            #  first run of plugin
            #  removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PreExPlanDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.dockwidget.pushButton.clicked.connect(self.new_shp)
            self.dockwidget.pushButton_2.clicked.connect(self.style_feat)
            self.dockwidget.pushButton_3.clicked.connect(self.addArea)
            self.dockwidget.pushButton_4.clicked.connect(self.add_Measure)
            self.dockwidget.pushButton_6.clicked.connect(self.addCentroid)
            self.dockwidget.pushButton_5.clicked.connect(self.dig)
            self.dockwidget.pushButton_7.clicked.connect(self.unique_id)
            self.dockwidget.pushButton_8.clicked.connect(self.addColum)
            self.dockwidget.pushButton_9.clicked.connect(self.info2)
            self.dockwidget.pushButton_10.clicked.connect(self.infoSel)
            self.dockwidget.pushButton_11.clicked.connect(self.info_prd)
            self.dockwidget.pushButton_12.clicked.connect(self.info_phs)
            self.dockwidget.pushButton_13.clicked.connect(self.slot_stat)
            self.dockwidget.pushButton_14.clicked.connect(self.slot_clock)
            self.dockwidget.pushButton_15.clicked.connect(self.interpr_column)
            self.dockwidget.pushButton_17.clicked.connect(self.convertDXF)
            self.dockwidget.pushButton_18.clicked.connect(self.slot_shp)
            self.dockwidget.pushButton_19.clicked.connect(self.style_slot)
            self.dockwidget.pushButton_20.clicked.connect(self.loe_shp)
            self.dockwidget.pushButton_21.clicked.connect(self.slot_time)
            self.dockwidget.pushButton_22.clicked.connect(self.duplicate_l)
            self.dockwidget.pushButton_23.clicked.connect(self.selected_feat_copy)
            self.dockwidget.pushButton_25.clicked.connect(self.est_secPlan)
            self.dockwidget.pushButton_26.clicked.connect(self.style_phasing)
            self.dockwidget.pushButton_27.clicked.connect(self.style_feat_period)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)


            self.dockwidget.show()
