import threading


class Independent:

    active = None
    thread = None

    def __init__(self):
        self.active = False
        self.thread = threading.Thread(target=self.run(), args=())

    def start(self):
        self.active = True
        self.thread.start()

    def stop(self):
        self.active = False
        self.thread.join()

    def run(self):
        """
        To be run in thread. Has to be implemented by child class
        :return:
        """
        pass
