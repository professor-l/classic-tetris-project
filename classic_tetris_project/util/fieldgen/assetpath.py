import os


class AssetPath(object):
    ASSET_FOLDER = "img"

    @staticmethod
    def get_file_root():
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_asset_root():
        return os.path.join(AssetPath.get_file_root(), AssetPath.ASSET_FOLDER)
