import logging
import time
import sys
import os

sys.path.append(os.getcwd())
from node.Messenger import Messenger
from node.Message import Message

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # TODO register file interface
    # init lora device
    # on file or network action take file or network action respectively
    m = Messenger()
    m.start()

    # Hard coded message TODO interaction with FS to load messages.
    message = Message()
    message.data = "Hello there"
    message.recipient = "42376f7500df44e985e8f7255bcfa0f7"
    message.pid = 11111
    message.sender_pid = 22222

    i = 20
    while i > 0:
        logging.info("loop")
        m.send(message)
        time.sleep(3)
        i = i - 1
    m.stop()
