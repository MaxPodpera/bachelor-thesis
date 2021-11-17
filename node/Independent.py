import threading


class Independent:

    active = None
    thread = None

    def __init__(self):
        print("andres")
        self.active = True
        self.thread = threading.Thread(target=self.run())

    def start(self):
        self.active = True
        self.thread.start()

    def stop(self):
        self.active = False

    def run(self):
        """
        To be run in thread
        :return:
        """
        pass
