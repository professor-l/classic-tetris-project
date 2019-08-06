import os
import pkgutil
from importlib import import_module

def import_dir(dirname, package):
    for _, package_name, is_pkg in pkgutil.walk_packages([dirname]):
        if is_pkg:
            import_dir(os.path.join(dirname, package_name), f"{package}.{package_name}")
        else:
            import_module("." + package_name, package)

import_dir(os.path.dirname(__file__), "classic_tetris_project.commands")
