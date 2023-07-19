import os

from data import resource_path
from param.param import Param
from settings.settings import Settings

# Create settings
settings = Settings()

# Add the enums from msg files
directory = resource_path("res/msg/")
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    with open(resource_path(f), "rb") as file:
        data = file.read()
        settings.add_enum_from_msg(os.path.splitext(filename)[0], data)

# Load other data
data = open(resource_path("res/settings.txt")).readlines()
settings.load_enums_from_data(data)
settings.load_fields_from_data(data)

# Create param
param = Param(None, settings)
directory = "res/base_params/"

with open(resource_path("res/base_params/classparam"), "rb") as file:
    data = file.read()
    param.load_from_data(data)
    print("Checking that classparam has 5 sections")
    assert param.sections_amount == 5

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    with open(resource_path(f), "rb") as file:
        data = file.read()
        print(f"Loading param file: {filename}")
        param.load_from_data(data)
        print(f"Converting param file to bytes: {filename}")
        param.to_bytes()

print("Tests passed")
