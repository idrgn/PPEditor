import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

from data import bytes_to_string, resource_path, string_to_bytes, validate_byte_string
from interface import main_window
from interface.check_box_field import QCheckBoxField
from interface.color_picker_field import QColorPickerField
from interface.combo_box_field import QComboBoxField
from interface.line_edit_field import QLineEditField
from interface.raw_data_edit import RawDataEditWindow
from param.param import Param
from settings.settings import Settings


class Application(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.output_path = None
        self.setupUi(self)
        self.set_connections()
        self.set_action_state(False)
        self.action_save.setEnabled(False)
        self.setWindowIcon(QtGui.QIcon(str(resource_path("res/icon.png"))))

        # Load settings from the settings file
        self.settings = None
        self.load_settings()

        # Create a param file
        self.param = Param(None, self.settings)
        self.path = None

        # If opened via cmd with parameters
        if len(sys.argv) > 1:
            if sys.argv[1]:
                file = sys.argv[1]
                file = file.replace("\\", "/")
                self.load_param_file(file)

    def load_msg_enums(self):
        """
        Load msg data for Settings
        """
        # Get current directory
        current_path = os.getcwd()
        enum_path = f"{current_path}{os.sep}msg{os.sep}"

        # Check if there's an enum folder in current directory
        if os.path.exists(enum_path) and os.path.isdir(enum_path):
            directory = Path(enum_path)
        else:
            directory = resource_path("res/msg/")

        # Load msg files from directory
        for path in directory.glob("*.msg"):
            if not path.is_file():
                continue
            with open(path, "rb") as file:
                data = file.read()
                self.settings.add_enum_from_msg(path.stem, data)

    def load_settings(self):
        """
        Create Settings object and load data
        """
        self.settings = Settings()

        # Add the enums from msg files
        self.load_msg_enums()

        # If settings exist, load from current location
        # If not, load from resources folder
        current_path = os.getcwd()
        settings_path = f"{current_path}{os.sep}settings.txt"
        if os.path.exists(settings_path):
            data = open(settings_path).readlines()
        else:
            data = open(resource_path("res/settings.txt")).readlines()

        self.settings.load_enums_from_data(data)
        self.settings.load_fields_from_data(data)

    def update_settings(self):
        """
        Updates settings for current param file
        """
        self.load_settings()
        self.param.reload_settings(self.settings)
        self.update_selected_entry()
        self.show_message("Updated settings")

    def update_msg_enums(self):
        """
        Updates msg enums for current param file
        """
        self.load_msg_enums()
        self.param.reload_settings(self.settings)
        self.update_selected_entry()
        self.show_message("Updated messages")

    def set_connections(self):
        """
        Set UI element connections
        """

        # Actions
        self.action_load.triggered.connect(self.select_param)
        self.action_save.triggered.connect(self.save_param_file)
        self.action_save_as.triggered.connect(self.save_param_file_as)
        self.action_refresh.triggered.connect(self.refresh_file)
        self.action_reload_messages.triggered.connect(self.update_msg_enums)
        self.action_reload_settings.triggered.connect(self.update_settings)

        # Combo box changes
        self.cb_sections.currentTextChanged.connect(self.load_section_entries)
        self.cb_entries.currentTextChanged.connect(self.update_selected_entry)

        # Buttons
        self.pb_add_new_section.clicked.connect(self.add_section)
        self.pb_copy_entry.clicked.connect(self.copy_entry)
        self.pb_paste_entry.clicked.connect(self.paste_entry)
        self.pb_remove_current_entry.clicked.connect(self.remove_entry)
        self.pb_add_new_entry.clicked.connect(self.add_entry)
        self.pb_edit_raw_data.clicked.connect(self.edit_raw_data)

    def set_action_state(self, enabled: bool = False):
        # Actions
        self.action_refresh.setEnabled(enabled)
        # self.action_save.setEnabled(enabled)
        self.action_save_as.setEnabled(enabled)

        # Combo boxes
        self.cb_sections.setEnabled(enabled)
        self.cb_entries.setEnabled(enabled)

        # Line edits
        self.le_section_size.setEnabled(enabled)
        self.le_section_entry_amount.setEnabled(enabled)

        # Buttons
        self.pb_add_new_section.setEnabled(enabled)
        self.pb_copy_entry.setEnabled(enabled)
        self.pb_paste_entry.setEnabled(enabled)
        self.pb_remove_current_entry.setEnabled(enabled)
        self.pb_add_new_entry.setEnabled(enabled)

        # Raw data
        self.te_raw_data.setEnabled(enabled)
        self.pb_edit_raw_data.setEnabled(enabled)

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
        with open(file, "rb") as f:
            data = f.read()
            self.path = file
            self.param.load_from_data(data)
            self.output_path = os.path.dirname(os.path.abspath(self.path))
            self.file_name = os.path.basename(os.path.abspath(self.path))
            self.lb_file_name.setText(f"Filename: {self.file_name}")
            self.refresh()
            self.set_action_state(True)
            self.show_message(f"Loaded file {self.path}")
            self.uptate_window_title()

    def uptate_window_title(self):
        """
        Updates window title, sets current filename
        """
        if self.path:
            self.setWindowTitle(f"Patapon Param Editor [{self.path}]")
        else:
            self.setWindowTitle(f"Patapon Param Editor")

    def refresh_file(self):
        if self.path is None:
            return
        self.load_param_file(self.path)

    def save_param_file(self, ignore_backup: bool = False):
        """
        Saves Param file
        """

        # Save backup if enabled in settings
        if not ignore_backup:
            if self.check_backup.isChecked:
                try:
                    shutil.copy(self.path, f"{self.path}.bak")
                except PermissionError or FileNotFoundError as e:
                    print(f"Error when saving backup: {e}")

        # Save file
        if self.path and self.param:
            data_to_save = self.param.to_bytes()
            with open(self.path, "wb") as f:
                f.write(data_to_save)
            self.show_message(f"Saved file {self.path}")

    def save_param_file_as(self):
        """
        Opens dialog to save param file in a different location, with a different name
        """
        if not self.param:
            return

        # Options
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Uncomment only if native dialog gives issues

        # Open dialog
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            self.path,
            "All Files (*)",
            options=options,
        )

        # Save file under new name, but don't ingore backup unless path remains the same
        if file_name:
            create_backup = self.path != file_name
            self.path = file_name
            self.save_param_file(create_backup)
            self.uptate_window_title()

    def refresh(self):
        """
        Refreshes UI
        """
        if self.param is None:
            return

        self.load_sections()
        self.load_section_entries()

    def show_message(self, message: str, duration: int = 4000):
        """
        Shows message in status bar
        Args:
            message (str): _description_
            duration (int, optional): _description_. Defaults to 4000.
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"[{current_time}]: {message}", duration)

    def load_sections(self, save_index: bool = False):
        """
        Loads sections
        """
        index = self.cb_sections.currentIndex()
        self.cb_sections.clear()
        for section in self.param.section_list:
            self.cb_sections.addItem(f"{section.id+1} ({section.entry_amount} entries)")

        if save_index:
            self.cb_sections.setCurrentIndex(index)

    def load_section_entries(self):
        """
        Loads entries
        """
        self.cb_entries.clear()
        for entry in self.param.get_section_entries(self.cb_sections.currentIndex()):
            entry_name = entry.get_name()
            if not entry_name:
                self.cb_entries.addItem(f"{entry.id}")
            else:
                self.cb_entries.addItem(f"{entry.id}: {entry_name}")

    def update_selected_entry(self):
        """
        Loads field list of current entry
        """
        scroll_position = self.sc.verticalScrollBar().value()
        self.sc.setVisible(False)
        self.clear_form_items()

        current_section = self.cb_sections.currentIndex()
        current_entry = self.cb_entries.currentIndex()

        entry = self.param.get_section_entry(current_section, current_entry)

        for field in entry.fields:
            label = QtWidgets.QLabel(field.settings.name)
            label.setToolTip(field.settings.description)

            if field.settings.type == "bool":
                widget = QCheckBoxField(self.sc_content)
            elif (
                field.settings.enum
                and -1 <= field.value < len(field.settings.enum.get_values()) - 1
            ):
                widget = QComboBoxField(self.frame_controls)
            elif field.settings.type == "rgba":
                widget = QColorPickerField(self.sc_content)
            else:
                widget = QLineEditField(self.sc_content)
            widget.set_field(field)
            widget.field_changed.connect(self.field_changed)
            self.fl_fields.addRow(label, widget)

        text = bytes_to_string(entry.to_bytes())
        self.te_raw_data.setPlainText(text)

        self.sc.verticalScrollBar().setValue(scroll_position)
        self.sc.setVisible(True)

    def field_changed(self):
        """
        Executed whenever a field is modified
        """
        if self.param.is_changed():
            self.action_save.setEnabled(True)
        else:
            self.action_save.setEnabled(False)

    def clear_form_items(self):
        """
        Clears all items in form
        """
        for i in reversed(range(self.fl_fields.count())):
            # Maybe use 'range(self.fl_fields.count() - 1, -1, -1)'?
            self.fl_fields.itemAt(i).widget().setParent(None)

    def get_current_entry(self):
        """
        Returns current selected entry
        """
        current_section_index = self.cb_sections.currentIndex()
        current_entry_index = self.cb_entries.currentIndex()

        current_entry = self.param.get_section_entry(
            current_section_index, current_entry_index
        )

        return current_entry

    def get_current_section(self):
        """
        Returns current selected section
        """
        current_section_index = self.cb_sections.currentIndex()
        current_section = self.param.get_section(current_section_index)
        return current_section

    def copy_entry(self):
        """
        Copies current entry in hex format
        """
        if self.param is None:
            return

        current_entry = self.get_current_entry()
        if current_entry is None:
            return

        text = bytes_to_string(current_entry.to_bytes())
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)
        self.show_message("Copied entry data to clipboard")

    def paste_entry(self):
        """
        Pastes current entry in hex format
        """
        if self.param is None:
            return

        current_entry = self.get_current_entry()
        if current_entry is None:
            return

        cb = QtWidgets.QApplication.clipboard()
        text = cb.text()

        if not validate_byte_string(text):
            return

        ba = string_to_bytes(text)

        current_entry.update_raw_data(ba)
        self.update_selected_entry()
        self.show_message("Pasted entry data from clipboard")

    def remove_entry(self):
        """
        Removes current entry
        """
        if self.param is None:
            return

        current_entry = self.get_current_entry()
        if current_entry is None:
            return

        current_section = self.get_current_section()
        current_section.remove_entry(current_entry)

        self.cb_entries.removeItem(self.cb_entries.currentIndex())
        self.show_message("Removed selected entry")

    def add_entry(self):
        """
        Adds new empty entry
        """
        current_section = self.get_current_section()
        current_section.add_entry()
        self.load_section_entries()
        self.show_message("Added new entry")

    def add_section(self):
        """
        Adds an empty section
        """
        try:
            section_size = eval(self.le_section_size.text())
            section_entries_amount = eval(self.le_section_entry_amount.text())
        except (ValueError, SyntaxError) as _:
            return

        if section_size <= 0:
            return

        if section_entries_amount <= 0:
            return

        self.param.add_section(section_size, section_entries_amount)

        self.le_section_size.setText("")
        self.le_section_entry_amount.setText("")

        self.load_sections(True)
        self.show_message("Added new section")

    def edit_raw_data(self):
        """
        Opens an editor to edit raw data
        """
        entry = self.get_current_entry()
        text = bytes_to_string(entry.to_bytes())
        text_editor = RawDataEditWindow(self, text)
        if text_editor.exec_() == QtWidgets.QDialog.Accepted:
            new_text = text_editor.text_edit.toPlainText()
            new_raw = string_to_bytes(new_text)
            entry.update_raw_data(new_raw)
            self.update_selected_entry()
            self.show_message("Updated raw data")
