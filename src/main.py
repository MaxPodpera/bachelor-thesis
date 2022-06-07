import sys
import os
import threading
sys.path.append(os.getcwd())
from src.Messenger import Messenger
from src.Message import *
from datetime import datetime
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
            msg.sender = "42376f7500df44e985e8f7255bcfa0f7"
            msg.data = str(datetime.now()) + str(i) + ("A" * 90) + str(i) + ("A" * 80)
            m.send(msg)
            time.sleep(1)

        time.sleep(3600 * 4)

        for i in range(0, 100):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "42376f7500df44e985e8f7255bcfa0f7"
            msg.data = str(datetime.now()) + str(i) + ("B" * 90) + str(i) + ("B" * 80)
            m.send(msg)
            time.sleep(5)

        time.sleep(3600 * 4)

        for i in range(0, 100):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "42376f7500df44e985e8f7255bcfa0f7"
            msg.data = str(datetime.now()) + str(i) + ("C" * 90) + str(i) + ("C" * 80)
            m.send(msg)
            time.sleep(1)