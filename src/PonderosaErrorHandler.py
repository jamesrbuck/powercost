import signal
import sys
import os
from time import time, ctime
import time

class PonderosaErrorHandler:
    def __init__(self,thePID,theAR):
        signal.signal(signal.SIGINT, self.catch)
        self.PID = thePID
        self.AR = theAR
    def catch(self, signalNumber, frame):
        mytime = time.localtime()
        print( f"\n==> PonderosaErrorHandler.py: Catching signal at {time.strftime('%H:%M:%S', mytime)}, Received Signal={str(signalNumber)}")
        if (os.path.exists(self.AR)):  # Remove "We are running" indicator file.
            print( f"==> PonderosaErrorHandler.py: Removing file {self.AR}")
            os.remove(self.AR)
        else:
            print( f"==> PonderosaErrorHandler.py: File does not exist: {self.AR}")

      # FINAL KILL: 21 = SIGBREAK) to kill sleep()
        print( "==> PonderosaErrorHandler.py: Executing os.kill(" + str(self.PID) + ",21) or SIGBREAK")
        sys.stdout.flush()
        sys.stderr.flush()
        os.kill(self.PID,21)  # Kill SIGBREAK this process in sleep()
