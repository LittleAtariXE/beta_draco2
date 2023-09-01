import socket
import base64
from time import sleep
from threading import Thread
from multiprocessing import Process


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
            
            out_msg = base64.b64decode(msg.decode(self.format_code))
            return out_msg
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

    def run(self):
        while True:
            if not self._build_socket():
                continue
            while True:
                if self.connect():
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

   