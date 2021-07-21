import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class InfoDupl(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("How to Select/Duplicate")
        self.setText("Step 1 - Select layer or features \n\n"
                        "Step 2 - click Duplicate or Selected \n\n"
                        "Step 3 - change the name of the output")

        self.setIcon(QMessageBox.Information)
x = InfoDupl()
def info_sel():
    global x
    return x.show()
