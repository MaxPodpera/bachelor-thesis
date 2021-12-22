import threading

"""
Class to wrap independently running parts of the software in.
"""


class Independent:

    active = None
    _thread = None

    def __init__(self):
        self._thread = threading.Thread(target=self.run, args=())

    def start(self) -> None:
        self.active = True
        self._thread.start()

    def stop(self) -> None:
        self.active = False
        self._thread.join()

    def run(self):
        """
        To be run in thread. Has to be implemented by child class. Run method should stop when active variable is set to false.
        :return:
        """
        pass
