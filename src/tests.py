import os

from data import resource_path
from param.param import Param
from settings.settings import Settings

settings = Settings(open(resource_path("res/settings.txt")).readlines())
param = Param(None, settings)
directory = "res/base_params/"

with open(resource_path("res/base_params/classparam"), "rb") as file:
    data = file.read()
    param.load_from_data(data)
    print("Checking that classparam has 5 sections")
    assert param.sections == 5

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    with open(resource_path(f), "rb") as file:
        data = file.read()
        print(f"Loading param file: {filename}")
        param.load_from_data(data)

print("Tests passed")
