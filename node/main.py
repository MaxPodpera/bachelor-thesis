import time

from Messenger import Messenger

class Test:

    def __init__(self):
        # TODO register file interface
        # init lora device
        # on file or network action take file or network action respectively
        m = Messenger()
        time.sleep(2)
        m.start()
        m.send({"data": "hello there", "recipient": {"pid": "asdsd", "at": "45:32:21:ae:bc"}})

if __name__ == '__main__':
    t = Test()