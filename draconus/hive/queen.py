import os

from jinja2 import Template

from ..CONFIG import APP_DIRECTORY


class Queen:
    def __init__(self):
        self.out_dir = os.path.join(APP_DIRECTORY, "HATCHERY")
        self.templates_dir = os.path.join(APP_DIRECTORY, "draconus", "hive", "templates")
        self.make_dirs()
        self._template = {}

    

    def make_dirs(self):
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
    

    def accept_config(self, **config):
        print(config)
        