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

    if m.node_id == "2b679c67277302db4ca0ae3fcbad51d3":
        for i in range(0, 100):
            msg = Message()
            msg.sender_pid = 00000
            msg.pid = 11111
            msg.recipient = "17109be4e4b711ec8fea0242ac120002"
            msg.sender = "2b679c67277302db4ca0ae3fcbad51d3"
            msg.data = str(datetime.now()) + str(i) + ("F" * 90)
            m.send(msg)
            time.sleep(10)

        # time.sleep(3600 * 3)

        # for i in range(0, 100):
        #     msg = Message()
        #     msg.sender_pid = 00000
        #     msg.pid = 11111
        #     msg.recipient = "17109be4e4b711ec8fea0242ac120002"
        #     msg.sender = "2b679c67277302db4ca0ae3fcbad51d3"
        #     msg.data = str(datetime.now()) + str(i) + ("D" * 90) + str(i) + ("D" * 80)
        #     m.send(msg)
        #     time.sleep(1)
        #
        # time.sleep(3600 * 4)
        #
        # for i in range(0, 100):
        #     msg = Message()
        #     msg.sender_pid = 00000
        #     msg.pid = 11111
        #     msg.recipient = "17109be4e4b711ec8fea0242ac120002"
        #     msg.sender = "2b679c67277302db4ca0ae3fcbad51d3"
        #     msg.data = str(datetime.now()) + str(i) + ("E" * 90) + str(i) + ("E" * 80)
        #     m.send(msg)
        #     time.sleep(5)
        #
        # time.sleep(3600 * 4)
        #
        # for i in range(0, 100):
        #     msg = Message()
        #     msg.sender_pid = 00000
        #     msg.pid = 11111
        #     msg.recipient = "17109be4e4b711ec8fea0242ac120002"
        #     msg.sender = "2b679c67277302db4ca0ae3fcbad51d3"
        #     msg.data = str(datetime.now()) + str(i) + ("F" * 90) + str(i) + ("F" * 80)
        #     m.send(msg)
        #     time.sleep(1)
