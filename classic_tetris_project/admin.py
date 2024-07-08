try:
    from .web.admin import *
except ModuleNotFoundError:
    # private not loaded, ignore
    pass
