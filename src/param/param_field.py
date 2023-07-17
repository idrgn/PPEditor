
from struct import pack

from src.data import (
    read_bool,
    read_char,
    read_float,
    read_int,
    read_short,
    read_str,
    read_uchar,
    read_uint,
    read_ushort,
    string_to_bytearray,
)
from src.settings.settings import SettingsFieldEntry


class ParamField:
    """
    Field
    """

    def __init__(self, id: int, settings: SettingsFieldEntry, data: bytes):
        self.id = id
        self.settings = settings
        self.raw_data = data
        self.initial_raw_data = data

        self.value = None
        self._parse_value()

    def update_raw_data(self, data: bytes):
        self.raw_data = data
        self._parse_value()

    def _parse_value(self):
        data = self.raw_data
        type = self.settings.type
        if type == "uint" or type == "rgba":
            self.value = read_uint(data)
        elif type == "int":
            self.value = read_int(data)
        elif type == "short":
            self.value = read_short(data)
        elif type == "ushort":
            self.value = read_ushort(data)
        elif type == "char":
            self.value = read_char(data)
        elif type == "uchar":
            self.value = read_uchar(data)
        elif type == "bool":
            self.value = read_bool(data)
        elif type == "float":
            self.value = read_float(data)
        elif type == "str" or type == "string":
            self.value = read_str(data)
        else:
            self.value = None

    def set_value(self, new_value):
        self.value = new_value

    def set_value_from_string(self, new_value):
        type = self.settings.type

        if type in ["uint", "int", "ushort", "short", "uchar", "char", "rgba"]:
            self.value = int(new_value)
        elif type == "bool":
            self.value = bool(new_value)
        elif type == "float":
            self.value = float(new_value)
        elif type == "str" or type == "string":
            self.value = new_value

    def to_bytes(self):
        type = self.settings.type

        try:
            if type == "uint" or type == "rgba":
                return self.value.to_bytes(4, byteorder="little", signed=False)
            elif type == "int":
                return self.value.to_bytes(4, byteorder="little", signed=True)
            elif type == "ushort":
                return self.value.to_bytes(2, byteorder="little", signed=False)
            elif type == "short":
                return self.value.to_bytes(2, byteorder="little", signed=True)
            elif type == "uchar":
                return self.value.to_bytes(1, byteorder="little", signed=False)
            elif type == "char":
                return self.value.to_bytes(1, byteorder="little", signed=True)
            elif type == "float":
                return pack("f", self.value)
            elif type == "bool":
                if self.value:
                    return b"\x01"
                else:
                    return b"\x00"
            elif type == "str" or type == "string":
                return string_to_bytearray(self.value, self.settings.size)
        except Exception as e:
            print(
                f"Error when processing entry {self.settings.name} with value {self.value}"
            )
            print(f"Error message: {e}")

    def is_changed(self) -> bool:
        return self.initial_raw_data != self.to_bytes()
