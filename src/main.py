import sys
import os
import threading
sys.path.append(os.getcwd())
from src.Messenger import Messenger
from src.Message import *
import time
"""
Entry point into the application.
Runs indefinitely 
"""
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    m = Messenger()
    t = threading.Thread(target=m.run)
    t.start()

    if m.node_id == "42376f7500df44e985e8f7255bcfa0f7":
        for i in range(0, 100):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "2b679c67277302db4ca0ae3fcbad51d3"
            msg.data = "A" * 20
            m.send(msg)
            time.sleep(1)
