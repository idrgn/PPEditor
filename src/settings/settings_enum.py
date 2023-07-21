class SettingsEnum:
    def __init__(
        self, name: str, description: str, values: list, null_value: str = None
    ) -> None:
        self.name = name
        self.description = description
        self.values = values
        self.null_value = null_value

    def get_values(self):
        if self.null_value is not None:
            return [self.null_value] + self.values
        else:
            return self.values

    def get_value(self, index: int):
        if index == -1:
            return self.null_value
        else:
            if index >= len(self.values):
                return "Unknown"
            else:
                return self.values[index]
