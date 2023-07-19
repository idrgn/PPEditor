
from src.data import (
    read_byte_array,
    replace_byte_array,
)

from src.param.param_field import ParamField


class ParamEntry:
    """
    Entry
    """

    def __init__(self, id: int, settings: list, data: bytes):
        self.id = id
        self.settings = settings
        self.raw_data = data
        self.initial_raw_data = data

        self.fields = []
        self._parse_data()

    def _parse_data(self):
        self.fields.clear()
        if self.settings is None:
            return

        for setting in self.settings:
            field_data = read_byte_array(self.raw_data, setting.address, setting.size)
            self.fields.append(
                ParamField(self.settings.index(setting), setting, field_data)
            )

    def to_bytes(self) -> bytes:
        raw_data = self.raw_data

        # Apply patches
        for field in self.fields:
            raw_data = replace_byte_array(
                raw_data, field.settings.address, field.to_bytes()
            )

        return raw_data

    def get_name(self) -> str:
        words = []

        for field in self.fields:
            if field.settings.shown:
                if field.settings.enum:
                    words.append(field.settings.enum.get_value(field.value))
                else:
                    words.append(str(field.value))

        if not words:
            return "No identifier"
        else:
            return " - ".join(filter(lambda word: word != "", words))

    def update_raw_data(self, data: bytes):
        self.raw_data = data
        self._parse_data()

    def is_changed(self) -> bool:
        if self.raw_data != self.initial_raw_data:
            return True

        return any((field.is_changed() for field in self.fields))
