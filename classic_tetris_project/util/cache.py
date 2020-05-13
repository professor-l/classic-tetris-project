import io
import os
import os.path
from django.conf import settings


class FileCache:
    def __init__(self, name):
        self.name = name
        self.root = os.path.join(settings.BASE_DIR, "cache", name)
        os.makedirs(self.root, exist_ok=True)

    def full_path(self, filename):
        return os.path.join(self.root, filename)

    def cache_path(self, filename):
        return os.path.join("/cache", self.name, filename)

    def has(self, filename):
        return os.path.isfile(self.full_path(filename))

    def put(self, filename, content):
        with open(self.full_path(filename), "wb") as f:
            f.write(content)
    
    def get(self, filename):
        return open(self.full_path(filename), "rb")
