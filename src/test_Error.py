from PonderosaErrorHandler import PonderosaErrorHandler
from time import time, ctime
import time
import os
import signal

PID = os.getpid()
alreadyRunning = 'XXX'

EH = PonderosaErrorHandler(PID,alreadyRunning)

#os.kill(PID,signal.CTRL_C_EVENT)
wait = input("Time to press Ctrl-C ... ")