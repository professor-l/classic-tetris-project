import os
import pkgutil
from importlib import import_module

for _, package_name, _ in pkgutil.iter_modules([os.path.dirname(__file__)]):
    import_module("." + package_name, "classic_tetris_project.commands")