import os
from pathlib import Path

DEFAULT_IP = "192.168.100.21"


FORMAT_CODE = "utf-8"

RAW_LEN = 1024

DRACO_SOCKET_RAW_LEN = 1024

LISTENING_STEP = 3

# Format code for internal communication between Draconus, Command Center and Servers
FORMAT_CODE_COMMUNICATION = "utf-8"


MESSENGER_NO_PRINTS = False

SYS_MSG_HEADERS = "@@##$$@@"


CLIENT_PAUSE_CONNECTION = 5



APP_DIRECTORY = str(Path(os.path.dirname(__file__)).parent)
SOCKETS_DIR = os.path.join(APP_DIRECTORY, "draconus", "_sockets")
OUTPUT_DIR = os.path.join(APP_DIRECTORY, "OUTPUT")
EXTRAS_DIR = os.path.join(APP_DIRECTORY, "extras")


print(APP_DIRECTORY)
print(SOCKETS_DIR)
print(OUTPUT_DIR)

