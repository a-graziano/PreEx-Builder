#!/usr/bin/env Python
# This script transforms dxf and csvs to a joined layer of Extents and Levels
# CSV must be formatted using the method csv_import in dailyCsv.py


import os
import sys
from urllib import parse
import datetime
#Not sure all these are needed
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.PyQt.QtCore import *
from PyQt5.QtWidgets import *
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface

'''QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.16\apps\qgis-ltr", True)
qgs = QgsApplication([], False)
QgsApplication.initQgis()
sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')'''
from qgis import processing

from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())




# method load_dxf: this method will be imported from fileLoad.py on later versions
def load_dxf(fp, layername='entities', geometry='LineString', crs='epsg:27700'):
    '''this method loads a dxf file
    layername: entities, geometry: LineString, crs: 27700,
    pass explicit to change'''

    fn = os.path.split(fp)[1][:-4]
    uri = "{}|layername={}|geometrytype={}".format(fp, layername, geometry)
    dxflayer = QgsVectorLayer(uri, fn, "ogr")
    osgb = QgsCoordinateReferenceSystem(crs)
    dxflayer.setCrs(osgb)
    #QgsProject.instance().addMapLayer(dxflayer)
    print('dxf variable set')
    return dxflayer, fn


# method load_csv will be imported from fileLoad.py on later versions
def load_csv(fp, x='X', y='Y', z='Z', crs='epsg:27700', delimiter=','):
    ''' this loads a csv file:
    fp: filepath to the csv or text (IMPORTANT format using dailyCsv.py first),
    x = X, y = Y, z =Z, crs: 27700, delimiter : ,'''
    fn = os.path.split(fp)[1][:-4]+'_csv'

    params = {'crs':crs,
        'delimiter': ',',
        'xField': x,
        'yField': y,
        'zField':z}

    pars = parse.unquote(parse.urlencode(params))

    #some path problems between Windows and Mac, add extra '/' for windows; so 'file:///'
    pth = r'{}{}{}{}'.format('file:///', fp, '?', pars)

    csv_layer = QgsVectorLayer(pth, fn, "delimitedtext")
    QgsProject.instance().addMapLayer(csv_layer)
    print('csv_file imported')
    return csv_layer



def add_attrs(layer, text):
    ''' this methods adds fields to the join layer
   N.B more can be added here to make similar to ARK '''

    field_list = [QgsField("Area", QVariant.Double, 'double',10,2),QgsField("class", QVariant.String),
    QgsField("mitig_area", QVariant.String),
    QgsField("id", QVariant.String), QgsField('created', QVariant.String)]

    dp = layer.dataProvider()

    dp.addAttributes(field_list)

    layer.updateFields()
    print('Fields Updated')



    with edit(layer):
        '''''mitig_area needs work'''
        for f in layer.getFeatures():

            f['class'] = 'context'
            f['mitig_area'] = text
            if f['POINT_ID'] is not None:
               f['id'] = f['POINT_ID'][3:9]
            f['created'] = datetime.datetime.now().strftime('%y-%m-%dT%H:%M:%S')

            layer.updateFeature(f)


# main code for the script: always needs work
#use dxf and csv from daily uploads.
def import_daily(dxffp, csvfp, col='Layer', code='ext'):
    '''creates a joined polygon layer between dxf and csv files for
    daily uploads
    dxffp = path to dxf file, csvfp = path to csv/txt file,
    col = column for expression
    code= survey code for expression'''

    layer, fn =load_dxf(dxffp)


    exp = " \"{}\" = '{}' ".format(col, code)
    layer.selectByExpression(exp)
    print('Levels selected')
    #create a memory object from selected features

    vlyr = QgsVectorLayer('Polygon?crs=epsg:27700', 'daily_interventions' , "memory")
    pr = vlyr.dataProvider()
    pr.addAttributes([QgsField("Layer", QVariant.String),
    QgsField("Area", QVariant.Double)])


    vlyr.updateFields()

    for f in layer.selectedFeatures():
        #check if extent has three or more vertices
        if len(list(f.geometry().vertices())) >= 3:

            lst = [(QgsPointXY(v.x(),v.y())) for v in f.geometry().vertices()]

            polyg = QgsGeometry.fromPolygonXY([lst])
            #check if polygon is valid
            if not polyg.isGeosValid():
                polyg = polyg.makeValid()

            f = QgsFeature()
            f.setGeometry(polyg)
            f.setAttributes(['ext', f.geometry().area()])
            pr.addFeature(f)
    vlyr.updateExtents()
    print('Polygons Created')
    vlyr.setName('{}{}'.format(fn, '_polys'))
    print('Polys name changed to {}'.format(vlyr.name()))
    QgsProject.instance().addMapLayer(vlyr)



    #import csv file
    clayer = load_csv(csvfp)

    # select features in csv file
    cexp = " \"CODE\" = 'lvl' "
    clayer.selectByExpression(cexp)
    print('CSV lvl selected')

    #run the processing script 'native::joinattributesbylocation' . PREDICATE set to 1,5 = 'contains', 'within',
    joined = processing.run("native:joinattributesbylocation", {'INPUT':vlyr,'JOIN':QgsProcessingFeatureSourceDefinition(clayer.name(),
        selectedFeaturesOnly=True,
        featureLimit=-1,
        geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'PREDICATE':[1,5],'JOIN_FIELDS':['POINT_ID','file'],'METHOD':0,'DISCARD_NONMATCHING':False,'PREFIX':'',
        'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    print('Join Completed')
    joined.setName(fn +'_join')
    print('Name = {}'.format(joined.name()))

    QgsProject.instance().addMapLayer(joined)
    print('Map Layer Added')
    #variable input for Mitigation Area
    qid = QInputDialog()
    title = 'Enter Mitig Area'
    label = 'Mitig Area'
    mode = QLineEdit.Normal
    default = "<mitigation area here>"
    text, ok = QInputDialog.getText(qid, title, label, mode, default)

    add_attrs(joined, text)

    if joined.isValid():
        #this removes the POINT_ID column

        fieldnames = [i.name() for i in joined.fields()]
        dp = joined.dataProvider()
        dp.deleteAttributes([fieldnames.index('POINT_ID')])
        joined.updateFields()
        QMessageBox.about(None, 'Intervention Script Update', 'Interventions Created Without Error')
    else: QMessageBox.warning(None, 'Intervention Script Update', 'Failure: Check Data')

widget = QWidget()
layout = QVBoxLayout()
label1 = QLabel('Create Intervention')# Create label and button
button1 = QPushButton('Add DXF')
def opendxf():
    global dxffp
    dxffp,_ = QFileDialog.getOpenFileName(caption='DXF file', filter = "CAD Files(*.dxf *.dwg)")

button1.clicked.connect(opendxf)

button2 = QPushButton('Add CSV')
def openCsv():
    global csvfp
    csvfp,_ = QFileDialog.getOpenFileName(caption='csv file', filter = "TXT Files(*.csv *.txt)")
button2.clicked.connect(openCsv)
button3 = QPushButton('Run')
def runScript():
    global csvfp
    global dxffp
    if len(dxffp)>0:
        import_daily(dxffp, csvfp)

button3.clicked.connect(runScript)


        # Create layout and add widgets

layout.addWidget(label1)
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(button3)
widget.setLayout(layout)
