import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

class SlotTime(QMessageBox):
    def __init__(self):
        super(QMessageBox,self).__init__()

        self.setWindowTitle("Valid Value")
        self.setText(" VALID VALUE time  \n\n"
                        "• 1        \n\n"
                        "• 2        \n\n"
                        "• 3        \n\n"
                        "• 4        \n\n"
                        )

        self.setIcon(QMessageBox.Information)
x = SlotTime()
def slot_time():
    global x
    return x.show()
