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

    message.recipient = "2b679c67277302db4ca0ae3fcbad51d3" #  "42376f7500df44e985e8f7255bcfa0f7"
    message.pid = 11111
    message.sender_pid = 22222
    message.message_id = 4
    
    message1 = Message()
    message1.data = "Hello again. You guessed it. This is another amazing message that will be transmitted." \
                    "The purpose of this message is to see if transmission fails because of split messages" \
                    "or just because its too fast or something. But whatever! I will find out soon enough"
    message1.recipient = message.recipient
    message1.pid = 11111
    message1.sender_pid = 22222
    message.message_id = 40
    
    #i = 10
    #while i > 0:
    m.send(message)
    m.send(message1)
    #    time.sleep(5)
    #    i = i - 1
    #    message.message_id += i
    #    message1.message_id += i
    time.sleep(60)
    m.stop()
