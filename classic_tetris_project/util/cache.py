import os
import os.path
from django.conf import settings


class FileCache:
    def __init__(self, name):
        self.name = name
        self.root = os.path.join(settings.BASE_DIR, "cache", name)
        os.makedirs(self.root, exist_ok=True)

    def has(self, filename):
        return os.path.isfile(os.path.join(self.root, filename))

    def put(self, filename, content):
        with open(os.path.join(self.root, filename), "wb") as f:
            f.write(content)
