import os
import socket
import sys
import click
import json

from click_shell import shell
from time import sleep
from threading import Thread

from draconus.CONFIG import SOCKETS_DIR, FORMAT_CODE_COMMUNICATION, DRACO_SOCKET_RAW_LEN, SYS_MSG_HEADERS
from draconus import Queen

class CommandCenter:
    def __init__(self):
        self._socket_dirs = SOCKETS_DIR
        self._format = FORMAT_CODE_COMMUNICATION
        self._raw_len = DRACO_SOCKET_RAW_LEN       
        self._draco_socket_path = os.path.join(self._socket_dirs, "DRACO_SOCKET")
        self._draco_socket = None
        self.SERVERS = {}
        self.sys_msg = SYS_MSG_HEADERS
        self.Queen = Queen()
        self._tmp = None

    def find_draco(self):
        if not os.path.exists(self._draco_socket_path):
            print("[SYSTEM] ERROR: Cant find Draconus")
            return None       
        _draco_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            _draco_socket.connect(self._draco_socket_path)
            print("[SYSTEM] Connected to DRACONUS")
            return _draco_socket
        except Exception as e:
            print("[SYSTEM] ERROR: ", e)
            print("[SYSTEM] Probably Draconus was not started. Run first Draconus")
            print("[!!] EXIT PROGRAM")
            return None
    
    def find_servers(self):
        count = 0
        for serv in os.listdir(self._socket_dirs):
            if serv == "DRACO_SOCKET" or serv in self.SERVERS:
                continue
            server = self._conn_serv(serv)
            if server:
                listen_msg = Thread(target=self.waiting_for_msg, args=(serv, ),daemon=True)
                listen_msg.start()
                count += 1
        return count
    
    def _conn_serv(self, socket_name):
        socket_path = os.path.join(self._socket_dirs, socket_name)
        try:
            serv_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            serv_socket.connect(socket_path)
            self.SERVERS[socket_name] = serv_socket
            # print("Find working socket: ", socket_name)
            return serv_socket
        except Exception as e:
            return None
    
    def recive_msg(self, conn):
        msg = b""
        while True:
            recv = conn.recv(self._raw_len)
            if recv:
                if len(recv) < self._raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        return msg.decode(self._format)
    
    def send_msg(self, msg, conn=None):
        if not conn:
            conn = self._draco_socket
        if isinstance(msg, str):
            msg = msg.encode(self._format)
        try:
            conn.send(msg)
        except Exception as e:
            print("ERROR Send: ", e)
    
    def send_json(self, msg):
        try:
            data = json.dumps(msg).encode(self._format)
        except Exception as e:
            print("[SYSTEM] Error Json: ", e)
            return False
        self.send_msg("JSON")
        sleep(0.2)
        self.send_msg(data)

    def recive_json(self, name):
        conn = self.SERVERS[name]
        data = self.recive_msg(conn)
        if not data:
            print("No data")
            return None
        try:
            dict_data = json.loads(data)
            return dict_data
        except Exception as e:
            print("ERROR Recv JSON: ", e)
            return None
    
    def exec_sys_cmd(self, serv_name, command):
        cmd = command.strip(self.sys_msg)
        if cmd == "JSON":
            sleep(0.5)
            self._tmp = self.recive_json(serv_name)
        else:
            print("Unknown sys cmd")





    def waiting_for_msg(self, name):
        conn = self.SERVERS[name]
        while True:
            resp = self.recive_msg(conn)
            if not resp:
                break
            if resp == "":
                continue
            else:
                if resp.startswith(self.sys_msg):
                    print(f"\nSYS MSG: {resp}\n")
                    self.exec_sys_cmd(name, resp)
                else:
                    print(f"\nMSG: {resp}\n")


    def START(self):
        self._draco_socket = self.find_draco()
        if not self._draco_socket:
            return False
        self.SERVERS["DRACONUS"] = self._draco_socket
        resp = Thread(target=self.waiting_for_msg, args=("DRACONUS", ), daemon=True)
        resp.start()
        print("[SYSTEM] Looking for working server")
        serv_num = self.find_servers()
        if serv_num > 0:
            print(f"[SYSTEM] I found {serv_num} servers ")
        return True





def build_draco_shell(CeCe):

    os.system("clear")
    print("[SYSTEM] Command Center Starting ...... ")
    if not CeCe.START():
        sys.exit()

    def exit_main_shell(*args, **kwargs):
        print("EXIT PROGRAM")
    
    @shell(prompt=f"[DRACONUS] >>", intro="------ Welcome To Draconus ! Put help for commands list ------- ", on_finished=exit_main_shell)
    def draco_shell():
        pass
    
    @draco_shell.command()
    def help():
        print("************ Draconus Base Commands ************\n")
        print("****** clr           - Clear screen")
        print("****** exit          - Exit Comand Center. Draconus still working")
        print("****** make          - Creates new server. see: 'make --help' for instruction")
        print("****** start <name>  - Start server listening. Ex: 'start MyServer' ")
        print("****** stop <name>   - Stop server listening. Ex: 'stop MyServer' ")
    
    @draco_shell.command()
    def clr():
        os.system("clear")
    
    @draco_shell.command()
    @click.option("--config", "-c", required=False, is_flag=True, help="Show servers config")
    def show(config):
        if config:
            CeCe.send_msg("conf")

    @draco_shell.command()
    def test():
        print("Send Test Command to Draconus")
        CeCe.send_msg("TEST")
        sleep(0.5)
        test_dict = {"NAME": "test_name", "PORT" : 1234567}
        print("Send Test JSON")
        CeCe.send_json(test_dict)
        
    
    @draco_shell.command(context_settings={'help_option_names': ['-h', '--help']})
    @click.argument("serv_type")
    @click.argument("name")
    @click.argument("port")
    @click.option("--start", "-s", is_flag=True, required=False, help="Start Listening server immediately")
    @click.option("--no_print", "-np", is_flag=True, required=False, help="Prints only important message but still logs all messages")
    def make(serv_type, name, port, start, no_print):
        config = {
            "SERV_TYPE" : serv_type,
            "NAME" : name,
            "PORT" : port
        }
        if start:
            config["START_NOW"] = True
        if no_print:
            config["MESS_NO_PRINTS"] = True

        CeCe.send_json(config)
        sleep(0.1)
        CeCe.send_msg("MAKE")
        sleep(0.5)
        CeCe.find_servers()
    
    @draco_shell.command()
    @click.argument("name")
    def start(name):
        if name:
            CeCe.send_msg(f"start {name}")
    
    @draco_shell.command()
    @click.argument("name")
    def stop(name):
        if name:
            CeCe.send_msg(f"stop {name}")
    
    @draco_shell.command()
    @click.argument("name")
    def hive(name):
        serv = CeCe.SERVERS.get(name)
        if not serv:
            print(f"[QUEEN] ERROR: Server '{name} doesnt exist !!")
            return False
        CeCe.send_msg(f"$conf {name}")
        print("[QUEEN] Preparing New Worm ... wait moment")
        sleep(2)
        config = CeCe._tmp
        if not config:
            print(f"[QUEEN] ERROR: Cant recive config server")
            return False
        CeCe.Queen.accept_config(**config)

    
    @draco_shell.command()
    @click.argument("name")
    def conn(name):
        if name:
            CeCe.send_msg(f"canal {name}")
            server_shell = build_server_shell(CeCe, name)
            server_shell()
    
    return draco_shell



def build_server_shell(CeCe, name):

    def exit_server_shell(*args, **kwargs):
        CeCe.send_msg("EXIT")
        print("[DRACONUS] Exit Server Shell")
    
    @shell(prompt=f"[{name}] >>", intro="------ Server Shell. Commands will be send directly to server ! Put help for commands list ------- ", on_finished=exit_server_shell)
    def server_shell():
        pass

    @server_shell.command()
    @click.argument("command")
    def ss(command):
        if command:
            CeCe.send_msg(command)
    

    
    return server_shell







if __name__ == "__main__":
    master_shell = build_draco_shell(CommandCenter())
    sleep(1)
    master_shell()

