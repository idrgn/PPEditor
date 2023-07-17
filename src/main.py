import sys

from PyQt5 import QtWidgets

from src.window import Application

print("Param Editor. Created by Maikel.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Application()
    main_window.show()
    app.exec_()
