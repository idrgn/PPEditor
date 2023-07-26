from settings.settings_enum import SettingsEnum


class SettingsField:
    def __init__(
        self,
        field_id: int,
        section: int,
        address: int,
        size: int,
        name: str,
        description: str,
        field_type: str,
        shown: bool = False,
        enum: SettingsEnum = None,
    ) -> None:
        self.id = field_id
        self.section = section
        self.address = address
        self.size = size
        self.name = name
        self.description = description
        self.type = field_type
        self.shown = shown
        self.enum = enum
