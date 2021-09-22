#import the libraries

from qgis.core import QgsFeature, QgsPoint, QgsGeometry, QgsProject, QgsField, QgsVectorLayer,QgsWkbTypes, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, edit
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QLineEdit, QDialog, QPushButton, QVBoxLayout, QTextBrowser, QGroupBox, QGridLayout, QCheckBox
from PyQt5.QtCore import QVariant, QRect, Qt
from PyQt5.QtGui import QIcon
import pandas as pd
from datetime import datetime as dt
import os
from qgis.utils import iface, Qgis

import re

class ScriptWindow(QDialog):
    vlyr =  QgsVectorLayer('LineStringZM?crs=epsg:27700', 'daily_line' , "memory")
    plyr =  QgsVectorLayer("PolygonZ?crs=epsg:27700", "Schema", "memory")


    field_list = [QgsField( 'site', QVariant.String), QgsField( 'class', QVariant.String),
            QgsField( 'id', QVariant.String), QgsField('label', QVariant.String), QgsField( 'category', QVariant.String),
            QgsField( 'source_cd', QVariant.String), QgsField( 'source_cl', QVariant.String),
            QgsField('source_id',QVariant.String), QgsField( 'created', QVariant.String),
            QgsField( 'comment' ,QVariant.String), QgsField( 'creator' ,QVariant.String),
            QgsField('modified', QVariant.String), QgsField( 'modifier', QVariant.String),
            QgsField( 'uuid' ,QVariant.String), QgsField( 'file' ,QVariant.String)]

    pr = vlyr.dataProvider()
    ppr = plyr.dataProvider()
    pr.addAttributes(field_list)
    ppr.addAttributes(field_list)
    vlyr.updateFields()
    plyr.updateFields()
    if vlyr.wkbType() == QgsWkbTypes.LineStringZM:
        vlyr.loadNamedStyle('/Volumes/GoogleDrive/My Drive/QGIS_styles/plan_pl_buf_style.qml')
        vlyr.triggerRepaint()

    def __init__(self, *args, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('Convert Survey')
        self.setGeometry(150,150,400,400)
        self.setStyleSheet("background-color: lightsteelblue; font: Tahoma 12px; color: #232323")
        self.UiComponents()




    def UiComponents(self):
        self.createGridLayout()

        windowlayout = QVBoxLayout()

        # add a text browser for print log
        self.textbox = QTextBrowser()
        self.textbox.resize(280,200)
        self.textbox.setStyleSheet("background-color: white; border: 2px solid lightsteelblue; padding: 2px; font: Arial 12px; color: #232323")

        #set the layout
        windowlayout.addWidget(self.horizontalGroupBox)
        windowlayout.addWidget(self.textbox)

        self.setLayout(windowlayout)

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox()
        glayout = QGridLayout()

        pushbutton1 = QPushButton('CSV File Path')
        self.pushbutton2= QPushButton('Run')
        self.pushbutton2.setEnabled(False)
        self.pushbutton2.clicked.connect(self.process)
        self.pushbutton3 = QPushButton('Merge')
        self.pushbutton3.clicked.connect(self.merge)
        self.pushbutton4 = QPushButton('Schema')
        self.pushbutton4.setEnabled(False)
        self.pushbutton4.clicked.connect(self.poly_process)
        self.pushbutton5 = QPushButton('Poly Merge')
        self.pushbutton5.setEnabled(False)
        self.pushbutton5.clicked.connect(self.poly_merge)
        self.check1 = QCheckBox()
        self.check1.clicked.connect(self.buttonClick)
        self.check2 = QCheckBox()
        self.check2.clicked.connect(self.buttonClick2)
        self.siteLabel = QLabel(self)
        self.siteLabel.setText('Site Code:')
        self.site = QLineEdit()
        self.site.setStyleSheet("background-color: azure; border: 2px solid lightsteelblue; padding: 2px; color: #232323")

        self.creatorLabel = QLabel(self)
        self.creatorLabel.setText('Creator: ')
        self.creatorLabel.setStyleSheet("color: #232323; font: Arial 10px")
        self.creator = QLineEdit()
        self.creator.setStyleSheet("background-color: azure; border: 2px solid lightsteelblue; padding: 2px;color: #232323 ")







        glayout.setGeometry(QRect(1,1,300,300))
        #set style sheets for buttons ( min-width: 6em; )
        stylesheets = "background-color: lightslategrey; border-style: outset; border-width: 2px; border-radius: 10px; border-color: dimgray;font: Arial 10px; padding: 1px; color: white;"
        pushbutton1.setStyleSheet(stylesheets)
        self.pushbutton2.setStyleSheet(stylesheets)
        self.pushbutton3.setStyleSheet(stylesheets)
        self.pushbutton4.setStyleSheet(stylesheets)
        self.pushbutton5.setStyleSheet(stylesheets)
        pushbutton1.clicked.connect(self.LoadCsv)
        glayout.addWidget(pushbutton1, 0,0)
        glayout.addWidget(self.pushbutton2, 1,0)
        glayout.addWidget(self.siteLabel, 0,1,)
        glayout.addWidget(self.creatorLabel, 1,1)
        glayout.addWidget(self.site, 0,2,1,3)
        glayout.addWidget(self.creator, 1,2,1,3)
        glayout.addWidget(self.check1,0,6, alignment=Qt.AlignRight)
        glayout.addWidget(self.check2,1,6, alignment=Qt.AlignRight)
        glayout.addWidget(self.pushbutton3)
        glayout.addWidget(self.pushbutton4, 3,0)
        glayout.addWidget(self.pushbutton5, 3,1,1,2)



        self.horizontalGroupBox.setLayout(glayout)





    def LoadCsv(self):
        self.csv_path,_ = QFileDialog.getOpenFileName(None, 'Select Survey CSV', '', "Text Files (*.csv *.txt)")
        self.textbox.append('CSV selected: {}'.format(self.csv_path))
        self.pushbutton2.setEnabled(True)

    def buttonClick(self):
        if self.check1.isChecked():
            self.siteText = self.site.text()
            self.textbox.append('\nSite Code: {}'.format(self.siteText))

    def buttonClick2(self):
        if self.check2.isChecked():
            self.creatorText = self.creator.text()
            self.textbox.append('Creator: {}'.format(self.creatorText))


    def process(self):
        self.pushbutton4.setEnabled(True)
        QgsProject.instance().addMapLayer(ScriptWindow.vlyr)


        df = pd.read_csv(self.csv_path, usecols=[0,1,2,3,4], sep= ',')

        if not df.columns[0] == 'POINT_ID':
            cols = ['POINT_ID', 'X', 'Y', 'Z', 'CODE']
            df = pd.read_csv(self.csv_path,names=cols, usecols=[0,1,2,3,4], sep= ',')

        self.textbox.append(print(df.head()))

        #create geometry points column and populate
        df['geometry'] = df.apply(lambda x: QgsPoint(x.X,x.Y,x.Z), axis= 1)
        #split POINT_ID column at '.'
        df['POINT_ID'] = df.apply(lambda x: x.POINT_ID.split('.')[0], axis=1)
        #change sec to sln for ARK
        df['CODE'] = df['CODE'].apply(lambda x: x.replace('sec', 'sln'))

        self.textbox.append(print(df.head()))
        # Group the geometry
        groups = df.groupby(['POINT_ID','CODE'])['geometry']

        # dictionary to convert CODE to source_cl
        dicty = {
            'section': ['sln'],
            'context': ['loe', 'ext', 'bos', 'coffin'] }

        # get filename from path
        fn = os.path.split(self.csv_path)[1][:-4]

        # get datetime format
        now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")


        ScriptWindow.vlyr.startEditing()
        for key in groups.groups.keys():
                    if key[1] not in  ['lvl', 'bpt', 'tgt', 'pho', 'stn', '','spf', 'coffin', 'tch', 'tpt']:
                        identifier = re.sub('\D', '',key[0])
                        category = key[1]
                        for k, v in dicty.items():
                            if category in v:
                                source_cl = k

                        geos = groups.get_group(key)
                        if len(geos) >=2:
                            geom = QgsGeometry.fromPolyline([t for t in geos])
                        f = QgsFeature()
                        f.setGeometry(geom)
                        f.setAttributes([self.siteText, source_cl,identifier, '',category, 'survey', source_cl, '', now,
                        '', self.creatorText, '','','',fn,])
                        ScriptWindow.vlyr.addFeature(f)
                        ScriptWindow.vlyr.updateExtents()
        ScriptWindow.vlyr.commitChanges()

    def merge(self):
        iface.messageBar().pushMessage('REMEMBER: PreFixes have to be have been removed')
        # get the plan_pl_buf layer
        planbuf = QgsProject.instance().mapLayersByName('plan_pl_buf')[0]


        # select the category not equal to sln
        ScriptWindow.vlyr.selectByExpression(" \"category\" != 'sln' ")

        planbuf.startEditing()
            #remember to select features
        for f in ScriptWindow.vlyr.selectedFeatures():
                planbuf.addFeature(f)
                planbuf.updateExtents()
        planbuf.commitChanges()
        self.textbox.append('{} features added to Plan_pl_buf'.format(planbuf.featureCount()))

        sitebuf = QgsProject.instance().mapLayersByName('site_pl_buf')[0]

        ScriptWindow.vlyr.selectByExpression(" \"category\" = 'sln' ")
        sitebuf.startEditing()
            #remember to select features
        for f in ScriptWindow.vlyr.selectedFeatures():
                sitebuf.addFeature(f)
                sitebuf.updateExtents()
        sitebuf.commitChanges()
        self.textbox.append('{} features add to Site_pl_buf'.format(sitebuf.featureCount()))

    def poly_process(self):
        QgsProject.instance().addMapLayer(ScriptWindow.plyr)
        ScriptWindow.vlyr.selectByExpression(" \"category\" = 'ext' ")
        with edit(ScriptWindow.plyr):

            for feat in ScriptWindow.vlyr.selectedFeatures():
                # coerceToType creates a list, specify [0] to select individual geometry
                feat.setGeometry(feat.geometry().coerceToType(QgsWkbTypes.PolygonZ)[0])
                feat['category'] = 'sch'
                ScriptWindow.plyr.addFeature(feat)
                ScriptWindow.plyr.updateExtents()
        self.pushbutton5.setEnabled(True)

    def poly_merge(self):
        planpolybuf =  QgsProject.instance().mapLayersByName('plan_pg_buf')[0]

        with edit(planpolybuf):
            for feats in ScriptWindow.plyr.getFeatures():
                planpolybuf.addFeature(feats)
                planpolybuf.updateExtents()
            feats_count = planpolybuf.featureCount()
        self.textbox.append('{} features add to Plan_pg_buf'.format(feats_count))
        if feats_count == 0:
            iface.messageBar().pushMessage('ERROR', 'Check Columns match in source file', level = Qgis.Warning, duration = 5)



def main():
    app = QApplication([])
    window = ScriptWindow()
    window.show()
    app.exec_()


if __name__=='__main__':
    main()
