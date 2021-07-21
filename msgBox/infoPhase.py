import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class InfoPhase(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("")
        self.setText("VALID VALUE Phase \n\n"
                        "◊  1 \n\n"
                        "◊  2 \n\n"
                        "◊  3 \n\n"
                        "◊  4 \n\n"
                        "◊  5 \n\n"
                        "◊  6 \n\n"
                        "◊  7 \n\n"
                        "◊  8 \n\n"
                        "◊  0")

        self.setIcon(QMessageBox.Information)
x = InfoPhase()
def info_phs():
    global x
    return x.show()
