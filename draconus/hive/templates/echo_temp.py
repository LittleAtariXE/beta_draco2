

class EchoClient(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "EchoClient"
    

    def RUN(self):
        self.send_msg("Hello World from Echo Client")
        sleep(1)
        response = self.recive_msg()
        print("RESPONSE From Server: ", response)
        return False

