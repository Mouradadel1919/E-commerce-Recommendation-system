from helpers import Settings, get_setting

class BaseDataModel:
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.settings = get_setting()
        