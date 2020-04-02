try:
    from .private.admin import *
except ModuleNotFoundError:
    # private not loaded, ignore
    pass
