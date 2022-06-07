import sys
import os
import threading
sys.path.append(os.getcwd())
from src.Utilities import file_name
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
        file_name = "statistics_10sec_3pck_100msg.csv"
        for i in range(0, 1):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "42376f7500df44e985e8f7255bcfa0f7"
            msg.data = str(datetime.now()) + str(i) + ("A" * 90) + str(i) + ("B" * 80)
            m.send(msg)
            time.sleep(10)

        file_name = "statistics_5sec_3pck_100msg.csv"
        time.sleep(60 * 40)

        for i in range(0, 100):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "42376f7500df44e985e8f7255bcfa0f7"
            msg.data = str(datetime.now()) + str(i) + ("A" * 90) + str(i) + ("B" * 80)
            m.send(msg)
            time.sleep(5)

        file_name = "statistics_1sec_3pck_100msg.csv"
        time.sleep(60 * 40)

        for i in range(0, 100):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "42376f7500df44e985e8f7255bcfa0f7"
            msg.data = str(datetime.now()) + str(i) + ("A" * 90) + str(i) + ("B" * 80)
            m.send(msg)
            time.sleep(1)