from time import sleep
from .server_template import BasicTemplate

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
    
    
