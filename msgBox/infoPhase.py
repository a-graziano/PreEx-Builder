import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class InfoPhase(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("")
        self.setText("VALID VALUE Phase \n\n"
                        "◊ Phase 1 \n\n"
                        "◊ Phase 2 \n\n"
                        "◊ Phase 3 \n\n"
                        "◊ Phase 4 \n\n"
                        "◊ Phase 5 \n\n"
                        "◊ Phase 6 \n\n"
                        "◊ Phase 7 \n\n"
                        "◊ Phase 8 \n\n"
                        "◊ Unknown")

        self.setIcon(QMessageBox.Information)
x = InfoPhase()
def info_phs():
    global x
    return x.show()
