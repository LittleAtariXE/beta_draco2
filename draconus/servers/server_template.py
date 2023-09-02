import socket
import selectors
import multiprocessing
import base64

from multiprocessing import Process, Pipe
from threading import Thread
from time import sleep

from ..tools import Messenger
from ..CONFIG import DEFAULT_IP, RAW_LEN, FORMAT_CODE, LISTENING_STEP, MESSENGER_NO_PRINTS, SYS_MSG_HEADERS


class MrHandler:
    def __init__(self, conn, addr, client_id):
        self._id = client_id
        self._conn_tuple = (conn, addr)
        self.conn = conn
        self.addr = addr
        self.Addr = f"{self.addr[0]} : {self.addr[1]}"
        self._sys_op = "Unknown"
        self._sys_env = "Unknown"
    
    def close(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except:
            pass




class BasicTemplate(Process):
    def __init__(self, main_pipe, **kwargs):
        Process.__init__(self, daemon=True)
        self.name = kwargs.get("NAME")
        self.owner = "DRACONUS"
        self._main_pipe = main_pipe
        self._ip = kwargs.get("IP", DEFAULT_IP)
        self._port = int(kwargs.get("PORT"))
        self._raw_len = kwargs.get("RAW_LEN", RAW_LEN)
        self._format_code = kwargs.get("FORMAT_CODE", FORMAT_CODE)
        self._listening_step = kwargs.get("LISTENING_STEP", LISTENING_STEP)
        self._mess_no_prints = kwargs.get("MESS_NO_PRINTS", MESSENGER_NO_PRINTS)
        self.ADDR = (self._ip, self._port)
        self.sys_msg = SYS_MSG_HEADERS
        self._is_listening = False
        self._listen_FLAG = False
        self.CTRL = None
        self.Msg = None
        self.CONNECTIONS = {}
        self._conn_ID = 0
        self._handler = MrHandler
        
        

    def _build_server(self, first_time=True):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as error:
            print(f"{self.owner} Error when create socket: ", error)
            return False
        try:
            self.server.bind(self.ADDR)
        except OSError as error:
            print(f"{self.owner} Error when bind socket: ", error)
            return False

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.server, selectors.EVENT_READ)
        if first_time:
            self.Msg = Messenger(self.name, self._mess_no_prints)
            self.CTRL = ServerControler(self._main_pipe, self)
            self.CTRL.start()
        self.Msg(f"[{self.name}] Server < {self.name} > create succesfull. Addr: {self._ip} : {self._port}", level=True)
        return True
    
    def _rebuild_socket(self):
        if self._listen_FLAG:
            self.Msg(f"[{self.name}] ERROR: Cant rebuild socket. Is still active", level=True)
            return False
        else:
            if self._build_server(first_time=False):
                self.Msg(f"[{self.name}] Socket rebuild successfull", level=True)
                self._is_listening = False
                return True
    
    def _build_listening(self):
        try:
            self.server.listen()
            self.Msg(f"\n[{self.name}] SERVER LISTENING ... waiting for connections ....\n", level=True)
            self._is_listening = True
            return True
        except OSError as error:
            self.Msg(f"\n[{self.name}] Error. Server cant listen: {error}")
            return False
        
    def _listening(self):
        while self._listen_FLAG:
            events = self.selector.select(timeout=self._listening_step)
            for key, mask in events:
                if key.fileobj is self.server:
                    self._accept_conn()
        self.Msg(f"\n[{self.name}] Stop Listening ....", level=True)
        self.selector.unregister(self.server)
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        self._rebuild_socket()


        

    def listening(self):
        if not self._build_listening():
            return False
        self._listen_FLAG = True
        listen = Thread(target=self._listening, daemon=True)
        listen.start()
    
    def _accept_conn(self):
        conn, addr = self.server.accept()
        self.Msg(f"[{self.name}] New Connection from: {addr[0]} : {addr[1]}")
        new_client = self._add_conn(conn, addr)
        self.ACCEPT_CONN(new_client)
  
    def _add_conn(self, conn, addr):
        self._conn_ID += 1
        self.CONNECTIONS[str(self._conn_ID)] = self._handler(conn, addr, str(self._conn_ID))
        return self.CONNECTIONS[str(self._conn_ID)]

    def _show_connections(self):
        self.Msg(f"CONNECTIONS: {self.CONNECTIONS}")
        self.Msg(f"\n[{self.name}] ------------- Connected Clients --------------------------\n", level=True, end=False)
        self.Msg(f"\n[{self.name}]--- ID ----- IP -------- PORT--------OP SYSTEM--------\n", level=True, end=False)
        for c in self.CONNECTIONS:
            self.Msg(f"** {c}  -  {self.CONNECTIONS[c].Addr}  - {self.CONNECTIONS[c]._sys_op}", level=True, end=False)
        self.Msg("")
    
    def _client_info(self, client_id):
        client = self.CONNECTIONS.get(str(client_id))
        if not client:
            self.Msg(f"[{self.name}] ERROR: Client is not connected", level=True)
            return False
        self.Msg(f"[{self.name}] ---- Client: {client.Addr} ------\n{client._sys_env}")
        
        
    
    def _close_conn(self):
        for c in self.CONNECTIONS:
            self.CONNECTIONS[c].close()
        self.CONNECTIONS = {}
        self._listen_FLAG = False
    
    def _close_target_conn(self, handler):
        handler.close()
        del self.CONNECTIONS[handler._id]
        return handler.Addr
    
    def _recive_msg(self, handler):
        msg = b""
        while True:
            recv = handler.conn.recv(self._raw_len)
            if recv:
                if len(recv) < self._raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        try:
            real_m = base64.b64decode(msg).decode(self._format_code)
            return real_m
        except base64.binascii.Error:
            self.Msg("[!!] WARNING [!!] Client send unencrypted data or someone try spoofing your client", end=False)
            return "[!!] MESSAGE NOT ENCRYPTED [!!] : " + msg.decode(self._format_code)
        

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
            if msg.startswith(self.sys_msg):
                self._exec_sys_command(handler, msg)
            else:
                self.Msg(f"\nMsg from: {handler.Addr}\n{msg}\n")
        self.Msg.only_log(f"Close Connection: {self._close_target_conn(handler)}\n")
    
    def _send_msg(self, msg, handler):
        send_msg = base64.b64encode(msg.encode(self._format_code))
        handler.conn.send(send_msg)
    
    def _unpack_sys_cmd(self, command):
        msg = command.split(self.sys_msg)
        cmd = []
        for m in msg:
            if m == "":
                continue
            cmd.append(m)
        return cmd
        
    def _exec_sys_command(self, handler, command):
        self.Msg(f"SYS COMMAND FROM CLIENT '{handler.Addr}': {command}")
        cmd = self._unpack_sys_cmd(command)
        if cmd[0] == "sys_info":
            handler._sys_op = cmd[1]
        if cmd[0] == "sys_env":
            handler._sys_env = cmd[1]
    
    def _show_config(self):
        config = {
        "NAME" : self.name,
        "IP" : self._ip,
        "PORT": self._port,
        "RAW_LEN" : self._raw_len,
        "FORMAT_CODE" : self._format_code,
        "IS_LISTENING" : self._is_listening,
        "MESS_NO_PRINTS" : self._mess_no_prints
        }
        return config
    
    def _send_config(self):
        self.Msg(f"{self.sys_msg}JSON")
        sleep(0.2)
        self.Msg._send_json(self.show_config())



        
    
    def show_config(self):
        return self._show_config()
    
    def ACCEPT_CONN(self, handler):
        acc_conn = Thread(target=self._listen_for_msg, args=(handler, ), daemon=True)
        acc_conn.start()

    
    def CLOSE_CONN(self):
        self._close_conn()
    
    def run(self):
        if self._build_server():
            while True:
                sleep(20)
        self.Msg("ENDDDDDDDDD")



class ServerControler(Thread):
    def __init__(self, main_pipe, server):
        Thread.__init__(self, daemon=True)
        self.main_pipe = main_pipe
        self.SERVER = server
    
    def _check_signal(self):
        check = self.main_pipe.poll
        if not check:
            return None
        else:
            out = self.main_pipe.recv()
            return out
    
    


    def _base_command(self, cmd):
        if cmd == "start":
            self.SERVER.listening()
        elif cmd == "show":
            self.SERVER._show_connections()
        elif cmd == "stop":
            self.SERVER.CLOSE_CONN()
        elif cmd == "conf":
            self.SERVER.Msg(self.SERVER.show_config(), level=True)
        elif cmd == "$conf":
            self.SERVER._send_config()
        elif cmd.startswith("info"):
            client_id = cmd.lstrip("info").strip(" ")
            self.SERVER._client_info(client_id)
        else:
            print("Unknown")
    
    def run(self):
        while True:
            check = self._check_signal()
            if not check:
                continue
            else:
                self._base_command(check)