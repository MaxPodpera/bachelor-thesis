import logging
import time
from Messenger import Messenger
from Message import Message

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # TODO register file interface
    # init lora device
    # on file or network action take file or network action respectively
    m = Messenger()
    m.start()

    message = Message()
    message.data = "Hello there"
    message.recipient = "bbcdef123456789d"
    message.pid = 11111

    i = 20
    while i > 0:
        logging.info("loop")
        m.send(message)
        time.sleep(1)
        i = i - 1
    m.stop()
