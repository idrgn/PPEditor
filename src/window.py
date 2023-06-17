import os
import shutil
import sys

from PyQt5 import QtWidgets

from data import resource_path
from interface import main_window
from param.param import Param
from settings.settings import Settings


class Application(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_connections()

        self.settings = Settings(open(resource_path("res/settings.txt")).readlines())
        self.param = Param(None, self.settings)
        self.path = None

        # If opened via cmd with parameters
        if len(sys.argv) > 1:
            if sys.argv[1]:
                file = sys.argv[1]
                file = file.replace("\\", "/")
                self.load_param_file(file)

    def set_connections(self):
        """
        Set UI element connections
        """
        self.action_load.triggered.connect(self.select_param)
        self.action_save.triggered.connect(self.save_param_file)

    def select_param(self):
        """
        Opens select param
        """
        input_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open")
        if input_file:
            if input_file[0] != "":
                self.load_param_file(input_file[0])

    def load_param_file(self, file):
        """
        Read Param file
        """
        with open(file, "r+b") as f:
            data = f.read()
            self.path = file
            self.param.load_from_data(data)
            self.output_path = os.path.dirname(os.path.abspath(self.path))
            self.file_name = os.path.basename(os.path.abspath(self.path))
            self.refresh()

    def save_param_file(self):
        """
        Saves BND file
        """
        # Save backup if enabled in settings
        if not self.check_backup.isChecked:
            shutil.copy(self.path, f"{self.path}.bak")

        # Save file
        if self.path and self.param:
            with open(self.path, "wb") as f:
                f.write(self.param.to_bytes())

    def refresh(self):
        for section in self.param.section_list:
            self.cb_sections.addItem(
                f"Section {section.id+1} ({section.entry_amount} entries)"
            )

        for entry in self.param.get_section_entries():
            self.cb_entries.addItem(f"{entry.id+1} ({entry.get_name()})")
