import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class SlotStat(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("Valid Value")
        self.setText(" VALID VALUE status \n\n"
                        "• complete \n\n"
                        "• ongoing  \n\n"
                        "• to be done")

        self.setIcon(QMessageBox.Information)
x = SlotStat()
def slot_stat():
    global x
    return x.show()
