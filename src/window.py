from PyQt5 import QtWidgets
from data import resource_path

from interface import main_window
from settings.settings import Settings
from param.param import Param


class Application(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        settings = Settings(open(resource_path("res/settings.txt")).readlines())
        param = Param(None, settings)
