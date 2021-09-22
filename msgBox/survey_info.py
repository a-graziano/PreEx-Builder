import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class InfoSurvey(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setText("Step 1 - Select csv file(POINT_ID,X,Y,Z,CODE) \n\n"
                        "Step 2 - add the site code and your name and tick the boxes \n\n"
                        "Step 3 - click Run \n\n"
                        "Step 4 - click on Schema \n\n"
                        "Step 5 - remove edit mode in site_pl_buf, plan_pl_buf and plan_pg_buf \n\n"
                        "Step 6 - click on Merge and Poly Merge \n\n"
                        "Step 7 - reactivate the edit mode and press merge on ArkSpatial")

        self.setIcon(QMessageBox.Information)
x = InfoSurvey()
def info_csv():
    global x
    return x.show()
