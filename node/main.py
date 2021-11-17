import time

from Messenger import Messenger

if __name__ == '__main__':
    # TODO register file interface
    # init lora device
    # on file or network action take file or network action respectively
    m = Messenger()
    time.sleep(2)
    m.start()
    print("seas")
    while True:
        m.send({"data": "hello there", "recipient": {"pid": "asdsd", "at": "45:32:21:ae:bc"}})
        time.sleep(1)