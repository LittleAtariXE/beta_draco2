import os
import socket
import json
from datetime import datetime

from threading import Thread
from time import sleep

from ..CONFIG import FORMAT_CODE_COMMUNICATION, OUTPUT_DIR, SOCKETS_DIR, MESSENGER_NO_PRINTS



class Messenger():
    def __init__(self, name, no_prints, out_dir=OUTPUT_DIR, s_dir=SOCKETS_DIR, f_code=FORMAT_CODE_COMMUNICATION):
        self.name = name
        self.format = f_code
        self._socks_dir = s_dir
        self._sock_file = os.path.join(self._socks_dir, name)
        self._logs_dir = out_dir
        self._log_file = os.path.join(self._logs_dir, f"{self.name}.txt")
        self._no_prints = no_prints
        self.make_file()
        self._buff_msg = []
        self._tmp_msg = ""
        self.owner = None
        self.char_end = "\n\n" + "-" * 60 + "\n\n"
        self.start_server()

    
    def make_file(self):
        if not os.path.exists(self._socks_dir):
            os.mkdir(self._socks_dir)
        if os.path.exists(self._sock_file):
            try:
                os.unlink(self._sock_file)
            except Exception as e:
                print("ERROR: ", e)
                return False
        if not os.path.exists(self._logs_dir):
            os.mkdir(self._logs_dir)
        if not os.path.exists(self._log_file):
            with open(self._log_file, "w") as f:
                f.write("")
        
        return True
    
    def _build_socket(self):
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self._sock_file)
        self.server.listen(1)

    def _accept_conn(self):
        while True:
            conn, addr = self.server.accept()
            self.owner = (conn, addr)
            self.empty_buff()

        
    
    def start_server(self):
        self._build_socket()
        acc_conn = Thread(target=self._accept_conn, daemon=True)
        acc_conn.start()

    def _unpack_dict(self, dict_data):
        buff = f"------------------- {self.name} -------------------------------\n"
        for k, i in dict_data.items():
            buff += f"**  {str(k)}  :  {str(i)}\n"
        return buff
    
    def _send_msg(self, msg):
        if isinstance(msg, dict):
            msg = self._unpack_dict(msg)
        if not self.owner:
            self._buff_msg.append(msg)
            return False
        try:
            self.owner[0].sendall(msg.encode(self.format))
            return True
        except (BrokenPipeError, ConnectionAbortedError, OSError):
            self._buff_msg.append(msg)
            return False
    
    def _send_json(self, data):
        try:
            send_data = json.dumps(data).encode(self.format)
        except Exception as e:
            self._send_msg(f"ERROR JSON: {e}")
            return False
        
        try:
            self.owner[0].sendall(send_data)
            return True
        except (BrokenPipeError, ConnectionAbortedError, OSError):
            return False

        

        
    def _log2file(self, msg, end=True):
        if isinstance(msg, bytes):
            msg = str(msg.decode(self.format))
        try:
            msg = str(msg)
        except Exception as e:
            msg = f"[MESSENGER] ERROR: {e}\n"
        if self._tmp_msg == "":
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            intro = f"\n[{self.name}] ---------- {date} ------------------------\n"
        else:
            intro = ""
        self._tmp_msg += intro
        self._tmp_msg += ("\n" + msg)
        if end:       
            self._tmp_msg += self.char_end
            with open(self._log_file, "a+") as f:
                f.write(self._tmp_msg)
            self._tmp_msg = ""
    
    def empty_buff(self):
        if len(self._buff_msg) > 0:
            message = "\n".join(self._buff_msg)
            self.owner[0].sendall(message.encode(self.format))
            self._buff_msg = []


    def log_me(self, text, end=True, level=False):
        if not self._no_prints or level:
            self._send_msg(text)
        self._log2file(text, end)

    def only_log(self, text, end=True):
        self._log2file(text, end)
    

    def __call__(self, text, end=True, level=False, logs=True):
        if not self._no_prints or level:
            self._send_msg(text)
        if logs:
            self._log2file(text, end)

    def _change_format(self, data):
        if isinstance(data, bytes):
            return data.decode(self.format)
        if isinstance(data, str):
            return data.encode(self.format)

