import logging
import time
import sys
import os

sys.path.append(os.getcwd())
from node.Messenger import Messenger
from node.Message import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # TODO register file interface
    # init lora device
    # on file or network action take file or network action respectively
    m = Messenger()
    m.start()
    #time.sleep(2)
    #if m.node_id == "42376f7500df44e985e8f7255bcfa0f7":
    #    time.sleep(10)
    # Hard coded message TODO interaction with FS to load messages.
    message = Message()
    message.data = "Hello there this is an amazing message that is very long so it needs more than one package" \
                   "to be sent over completely. It will be printed once everything was received"#. This requires some" \
                  # "more characters though."
    message.recipient = "42376f7500df44e985e8f7255bcfa0f7"
    message.pid = 11111
    message.sender_pid = 22222
    message.message_id = 5
    i = 1

    while i > 0:
        logging.info("Adding to queue")
        m.send(message)
        i = i - 1
        message.message_id = i
    time.sleep(30)
    m.stop()
