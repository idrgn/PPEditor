from struct import pack

from data import (
    bytearray_to_string,
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
from settings.settings_field import SettingsField


class ParamField:
    """
    Field
    """

    def __init__(self, field_id: int, settings: SettingsField, data: bytes):
        self.id = field_id
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
        t = self.settings.type
        if t == "uint" or t == "rgba":
            self.value = read_uint(data)
        elif t == "int":
            self.value = read_int(data)
        elif t == "short":
            self.value = read_short(data)
        elif t == "ushort":
            self.value = read_ushort(data)
        elif t == "char":
            self.value = read_char(data)
        elif t == "uchar":
            self.value = read_uchar(data)
        elif t == "bool":
            self.value = read_bool(data)
        elif t == "float":
            self.value = read_float(data)
        elif t == "str" or t == "string":
            try:
                self.value = bytearray_to_string(data)
            except Exception as _:
                self.value = read_str(data)
        else:
            self.value = None

    def set_value(self, new_value):
        self.value = new_value

    def set_value_from_string(self, new_value):
        t = self.settings.type
        if t in ["uint", "int", "ushort", "short", "uchar", "char", "rgba"]:
            self.value = int(new_value)
        elif t == "bool":
            self.value = bool(new_value)
        elif t == "float":
            self.value = float(new_value)
        elif t == "str" or t == "string":
            self.value = new_value

    def to_bytes(self) -> bytes:
        t = self.settings.type
        try:
            if t == "uint" or t == "rgba":
                return self.value.to_bytes(4, byteorder="little", signed=False)
            elif t == "int":
                return self.value.to_bytes(4, byteorder="little", signed=True)
            elif t == "ushort":
                return self.value.to_bytes(2, byteorder="little", signed=False)
            elif t == "short":
                return self.value.to_bytes(2, byteorder="little", signed=True)
            elif t == "uchar":
                return self.value.to_bytes(1, byteorder="little", signed=False)
            elif t == "char":
                return self.value.to_bytes(1, byteorder="little", signed=True)
            elif t == "float":
                return pack("f", self.value)
            elif t == "bool":
                if self.value:
                    return b"\x01"
                else:
                    return b"\x00"
            elif t == "str" or t == "string":
                return string_to_bytearray(self.value, self.settings.size)
        except Exception as e:
            print(
                f"Error when processing entry {self.settings.name} with value {self.value}"
            )
            print(f"Error message: {e}")

    def is_changed(self) -> bool:
        return self.initial_raw_data != self.to_bytes()
