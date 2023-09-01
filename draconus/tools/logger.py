import os
from datetime import datetime
from time import sleep

from ..CONFIG import OUTPUT_DIR


class Logger:
    def __init__(self, name="DRACONUS", prints=False):
        self.name = name
        self._out_dir = OUTPUT_DIR
        self._log_file = os.path.join(self._out_dir, f"{self.name}.txt")
        self._tmp = ""
        self._prints = prints
        self.char_end = "\n" + "-" * 80 + "\n\n"
        self.make_file()
    
    def make_file(self):
        if not os.path.exists(self._out_dir):
            os.mkdir(self._out_dir)
        if not os.path.exists(self._log_file):
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self._log_file, "w") as f:
                f.write(f"File Creation Date: {date}\n\n")
    


    def log(self, text, end=True):
        if not isinstance(text, str):
            text = str(text)
        if self._prints:
            print(text)
        if self._tmp == "":
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            intro = f"\n[{self.name}]  ------ {date} ------------\n"
        else:
            intro = "\n"
        msg = intro + text
        if end:
            with open(self._log_file, "a+") as f:
                f.write(self._tmp + msg + self.char_end)
                self._tmp = ""
            
        else:
            self._tmp += msg
    
    def __call__(self, text, end=True):
        self.log(text, end)
    


