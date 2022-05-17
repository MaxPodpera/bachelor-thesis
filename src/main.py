import sys
import os
import threading
sys.path.append(os.getcwd())
from src.Messenger import Messenger
from src.Message import *

"""
Entry point into the application.
Runs indefinitely 
"""
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    m = Messenger()
    t = threading.Thread(target=m.run)
    t.start()
