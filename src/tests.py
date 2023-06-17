from data import resource_path
from settings.settings import Settings
from param.param import Param


settings = Settings(open(resource_path("res/settings.txt")).readlines())
param = Param(None, settings)


with open(resource_path("res/base_params/classparam"), "rb") as file:
    data = file.read()
    param.load_from_data(data)

    assert param.sections == 5


print("Tests passed")
