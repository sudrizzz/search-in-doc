import sys
from PyQt5.QtWidgets import QApplication

from View import App

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = App([['', '', '']])
    app.exec_()
