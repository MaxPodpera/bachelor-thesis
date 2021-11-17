import time
from Messenger import Messenger
from Message import Message

if __name__ == '__main__':
    # TODO register file interface
    # init lora device
    # on file or network action take file or network action respectively
    m = Messenger()
    m.start()
    i = 20
    message = Message()
    message.data = "Hello there"
    message.recipient = "bbcdef123456789d"
    message.pid = 11111
    while i > 0:
        m.send(message)
        time.sleep(1)
        i = i - 1

    m.stop()
