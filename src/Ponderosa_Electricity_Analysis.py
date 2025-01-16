#!/usr/bin/python

import signal
import sys
import argparse

from decimal import Decimal, getcontext

from configparser import BasicInterpolation, ConfigParser

from time import time, ctime
import time
from xmlrpc.client import boolean
from emu_power import Emu

import mysql.connector


# Error Handler Class
# ===================
class MySignalHandler:
   def setup(self,thePID,theAR):
      signal.signal(signal.SIGINT, self.catch)
      self.PID = thePID
      self.AR = theAR
   def catch(self, signalNumber, frame):
      mytime = time.localtime()
      sigMsg = "\n==> signal_handler(): At " + time.strftime('%H:%M:%S', mytime) + ", Received Signal=" + str(signalNumber)
      print(sigMsg)


# =============================================================================
#                            M A I N   P R O G R A M
# =============================================================================
def main():
   #mytime = time.localtime()
   #print("==> Script started in __main__ at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))

   #startTS = time.strftime('%Y%m%d-%H%M%S', time.localtime())

   # Parse Command Line Arguments
   # ============================
   # Running like a daemon means having pythonw and not python execute the script.
   # pythonw means that there is no command line CMD.EXE ruuning me.  This is
   # appropriate for being started as a Windows Started Task. pythonw is used
   # for running GUI apps or character-mode apps with no interaction with the
   # console.
   # =======================================================================
   force = False
   parser = argparse.ArgumentParser()
   parser.add_argument('--ini', metavar='ini', type=str, required=True)
   args = parser.parse_args()
   INI = args.ini

   # Read configuration (Top Level Code: Global scope variables)
   # ==================
   config = ConfigParser()
   config.read(INI)

   # Continue setup now that the script was not already running.
   # ===========================================================
   dbUser              = config.get('database','dbUser')
   dbPassword          = config.get('database','dbPassword')
   dbHost              = config.get('database','dbHost')
   dbName              = config.get('database','dbName')
   dbRaiseOnWarnings   = config.getboolean('database','dbRaiseOnWarnings')
   dbConfig = {
      'user': dbUser,
      'password': dbPassword,
      'host': dbHost,
      'database': dbName,
      'raise_on_warnings': dbRaiseOnWarnings
   }

   DayOfWeek = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
   exitMsg = ""
   api = ""
   f = ""

   #mytime = time.localtime()
   #print("==> Script started. Time is " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
   sys.stdout.flush()
   sys.stderr.flush()

   conn = mysql.connector.connect(**dbConfig)
   query = ("SELECT UDate, DAYOFWEEK(UDate) as DOWN, substring(UTime,1,2) as the_hour, kWh FROM usage_e ORDER BY ID ASC" )
   cursor = conn.cursor()
   cursor.execute(query)
   resultSet = cursor.fetchall()
   # print( "There are {0} rows".format(len(resultSet)) )

   loop_counter = 0
   prevDate = ""
   hourCounter = 0
   kwhDate = 0

   for (UDate, DOWN, theHour, kwh) in resultSet:
      DOW = DayOfWeek[DOWN-1]
      printedDate = False
      loop_counter = loop_counter + 1
      if (prevDate == ""):   # Special Case: First Row
         prevDate = UDate
         kwhDate = kwh
         hourCounter = 1
      elif (UDate != prevDate):
         if (hourCounter != 24):
            kwhDate = round(kwhDate * Decimal(24/hourCounter),3)

         prevDate = UDate  # New Date, change prevDate to reflect new/current date
         print("{}\t{}\t{}".format(UDate, DOW, kwhDate))  # We're in a new date: print total for previous date

         kwhDate = kwh  # Reset to value of first hour of new date
         hourCounter = 1
      else:
         kwhDate += kwh
         hourCounter += 1

   conn.close()


# ==========================================================================
#                         M A I N   P R O G R A M
# Run only as a top-level script, i.e., not as an import
# Is there a benefit to running with function main() as far as process
# control/signal handling??
# ==========================================================================
if __name__ == '__main__':
   main()
