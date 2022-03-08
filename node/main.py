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

    # testing

    time.sleep(2)

    # Hard coded message TODO interaction with FS to load messages.
    message = Message()
    message.data = "Hello there this is an amazing message that is very long so it needs more than one package" \
                   "to be sent over completely. It will be printed once everything was received. This requires some" \
                   "more characters though. But to completely and thorough test this i will now attempt to create a" \
                   "message that is long enough to be sent as three messages. This way the later two should be" \
                   " received. This line is the last one i need for this."

    message.recipient = "42376f7500df44e985e8f7255bcfa0f7"
    message.pid = 11111
    message.sender_pid = 22222
    message.message_id = 4
    
    print(message.split())

    """   
    i = 1
    while i > 0:
        m.send(message)
        time.sleep(2)
        i = i - 1
        message.message_id += i
    #time.sleep(10)
    #m.stop()
    """
