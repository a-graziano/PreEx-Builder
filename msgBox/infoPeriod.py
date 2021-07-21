import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class InfoPer(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("")
        self.setText("VALID VALUE Period \n\n"
                        "◊ BRONZE AGE   \n\n"
                        "◊ IRON AGE     \n\n"
                        "◊ ROMAN        \n\n"
                        "◊ MEDIEVAL     \n\n"
                        "◊ POST MEDIEVAL\n\n"
                        "◊ MODERN       \n\n"
                        "◊ UNKNOWN      \n\n"
                        )

        self.setIcon(QMessageBox.Information)
x = InfoPer()
def info_prd():
    global x
    return x.show()
