import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class InfoBox(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("Manage Dxf Tips")
        self.setText("Step 1 - Add Dxf to the Layer panel \n\n"
                        "Step 2 - Select the DXF layer \n\n"
                        "Step 3 - Convert DXf \n\n"
                        "Step 4 - add Interpr")

        self.setIcon(QMessageBox.Information)
x = InfoBox()
def info():
    global x
    return x.show()
