#!/usr/bin/python

# Script exit happens via external Ctrl-C or SIGINT.

import sys
import os
import decimal
import argparse
import signal
from time import time, ctime
import time

from xmlrpc.client import boolean
from emu_power import Emu

from PonderosaConfig import PonderosaConfig
from PonderosaDB import PonderosaDB

class PonderosaErrorHandler:
    def __init__(self,thePID,theAR):
        signal.signal(signal.SIGINT, self.catch)
        self.PID = thePID
        self.AR = theAR
    def catch(self, signalNumber, frame):
        mytime = time.localtime()
        print( f"\n==> PonderosaErrorHandler.py: Error Handler Entered.\n   Catching signal {str(signalNumber)} at {time.strftime('%H:%M:%S', mytime)}")
        if (os.path.exists(self.AR)):  # Remove "We are running" indicator file.
            print( f"   PonderosaErrorHandler.py: Removing file {self.AR}")
            os.remove(self.AR)
        else:
            print( f"   PonderosaErrorHandler.py: File does not exist: {self.AR}")

      # FINAL KILL: 21 = SIGBREAK) to kill sleep()
        print( "   PonderosaErrorHandler.py: Executing os.kill(" + str(self.PID) + ",21) or SIGBREAK")
        sys.stdout.flush()
        sys.stderr.flush()
        os.kill(self.PID,21)  # Kill SIGBREAK this process in sleep()

# =============================================================================
#                            M A I N   P R O G R A M
# =============================================================================
def main():
    PID = os.getpid()
    stopFile = ""
    stdout_old = sys.stdout
    stderr_old = sys.stderr
    the_port = ""
    alreadyRunning = ""
    emu_api = ""
    f = ""

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
    parser.add_argument('--force', dest='force', action='store_true')
    args = parser.parse_args()
    INI = args.ini
    force = args.force

    startTS = time.strftime('%Y%m%d-%H%M%S', time.localtime())
    PC = PonderosaConfig(INI,startTS)
    log_dir  = PC.getlog_dir()
    log_file = PC.getlog_file()
    the_port = PC.getthe_port()

    # Stop execution if this file is found
    stopFile = log_dir + "\\" + "stop.txt"
    if (os.path.exists(stopFile)):
        sys.exit(0)

    # CHECK: Are we currently running?
    # ================================
    alreadyRunning = log_dir + "\\" + "Ponderosa_Electricity_Usage.running"
    # Setup signal handler for abnormal or Ctrl-C exit
    mysig = PonderosaErrorHandler(PID,alreadyRunning)

    if (force):  # Used to force start like in a Windows Scheduled Task
        if (os.path.exists(alreadyRunning)):
            os.remove(alreadyRunning)
    else:
        if (os.path.exists(alreadyRunning)):
            with open(log_dir + "\\" + "already.txt","a") as fw:
                fw.write("==> Script is already running (File=" + alreadyRunning + ") at " + startTS +  "\n")
                print("==> Script is already running (File=" + alreadyRunning + ") at " + startTS +  "\n")
            sys.exit(0)

    # Redirect stdout and stderr to a log file
    # ========================================
    log_path = log_dir + "\\" + log_file
    if (os.path.exists(log_path)):
        os.remove(log_path)
    stdout_old = sys.stdout
    stderr_old = sys.stderr
    sys.stdout = open(log_path,"a")
    sys.stderr = open(log_path,"a")

    DBC = PonderosaDB(PC.getdbConfig())

    with open(alreadyRunning,"w") as ar:
        ar.write(str(PID)+"\n")

    if (os.path.exists(stopFile)):
        sys.exit(0)

    decimal.getcontext().prec = 3  # Receiving unit is accurate to 3 decimals

    mytime = time.localtime()
    print("==> Script started. Time is " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
    print("==> PID=" + str(PID) + "\n")
    sys.stdout.flush()
    sys.stderr.flush()

    # --------------------------------------------------------------------------
    # Try to start serial connection to EMU
    # --------------------------------------------------------------------------
    while (True):
        emu_api = Emu(debug=False,fresh_only=True,timeout=5,synchronous=True)
        EMU_Started = emu_api.start_serial(the_port)
        time.sleep(5)  # Wait for serial device to respond
        if (EMU_Started is not None):
            mytime = time.localtime()
            print("==> [Start] emu_api.start_serial on \"" + the_port + "\" at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
            break

        i  = 1
        mytime = time.localtime()
        print("==> [Start] emu_api.start_serial on \"" + the_port + "\" failure #" + str(i) + " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
        sys.stdout.flush()
        sys.stderr.flush()

        # Exit situation: we exceeded the number of attempts
        # --------------------------------------------------
        if (i >= 20):
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = stdout_old
            sys.stderr = stderr_old
            if (os.path.exists(alreadyRunning)):
                os.remove(alreadyRunning)
            mytime = time.localtime()
            errmsg = f"emu_api.start_serial failed on \"{the_port}\" at {time.strftime('%m/%d/%Y %H:%M:%S', mytime)}"
            raise Exception(errmsg)
        time.sleep(5)
        i = i + 1

    # --------------------------------------------------------------------------
    # Connection successful, print startup banner
    # --------------------------------------------------------------------------
    response = emu_api.get_device_info()
    time.sleep(5)
    print("Manufacturer:      " + response.manufacturer)
    print("Model ID:          " + response.model_id)
    print("Install Code:      " + response.install_code)
    print("Link Key:          " + response.link_key)
    print("Hardware Version:  " + response.hw_version)
    print("Firmware Version:  " + response.fw_version)
    print("Image Type:        " + response.fw_image_type)
    print("Date Code:         " + response.date_code)

    response = emu_api.get_meter_info()
    print("Meter Mac ID:      " + response.meter_mac + "\n\n")

    sys.stdout.flush()
    sys.stderr.flush()


    # --------------------------------------------------------------------------
    # Wait until top of the hour
    # --------------------------------------------------------------------------
    mytime = time.localtime()
    imin  = int(time.strftime('%M', mytime))
    isec  = int(time.strftime('%S', mytime))
    sec_sleep = 60*(60-imin-1) + (60-isec)
    print("==> Time is " + time.strftime('%m/%d/%Y %H:%M:%S', mytime) + ", sleeping for " + str(sec_sleep)+" seconds until top of the hour...")
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(sec_sleep)

    mytime = time.localtime()
    print("==> Sleep is done. Time is " + time.strftime('%m/%d/%Y %H:%M:%S', mytime) + "\n")

    sys.stdout.flush()
    sys.stderr.flush()

    runDays = 0
    loop_counter = 0
    minute_counter = 0
    minute_sumkw = 0
    the_hour_last = -1

    kWh_day = 0

    # ==========================================================================
    # Main Loop
    # ==========================================================================
    the_date_prev = "FIRST_LOOP_INTERATION"
    the_date_prev_db = "FIRST_LOOP_INTERATION"
    while True:
        if (os.path.exists(stopFile)):
            print("Stop file does exist, exiting.")
            sys.exit(0)

        loop_counter = loop_counter + 1

        # Get date, time and meter readings
        # ---------------------------------
        mytime      = time.localtime()
        the_date    = time.strftime('%m/%d/%Y', mytime)
        the_date_db = time.strftime('%Y-%m-%d', mytime)
        the_hour    = int(time.strftime('%H', mytime))

        keepTrying = True
        i = 0
        while (keepTrying):
            i = i + 1
            response = emu_api.get_instantaneous_demand()
            time.sleep(5)
            if (response is None):
                print(f"==> Call to emu_api.get_instantaneous_demand() failed! #{str(i)} at {time.strftime('%m/%d/%Y %H:%M:%S', mytime)}")
                sys.stdout.flush()
                sys.stderr.flush()
                if (i == 15):
                    keepTrying = False  #  Loop Done: Give up - too many tries
                else:
                    time.sleep(10)  # Loop NOT Done: Try again
            else:
                keepTrying = False  # Loop Done: Success

        if (keepTrying):
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = stdout_old
            sys.stderr = stderr_old
            if (os.path.exists(alreadyRunning)):
                os.remove(alreadyRunning)
            mytime = time.localtime()
            print("==> emu_api.get_instantaneous_demand() failed COMPLETELY  at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(2)

        # Get kWh from 3 values
        demand       = decimal.Decimal(response.demand)
        divisor      = decimal.Decimal(response.divisor)
        multiplier   = decimal.Decimal(response.multiplier)
        kw           = decimal.Decimal(multiplier*(demand/divisor))

        # For first time through loop
        if (the_date_prev == "FIRST_LOOP_INTERATION"):
            the_date_prev = the_date
        if (the_date_prev_db == "FIRST_LOOP_INTERATION"):
            the_date_prev_db = the_date_db

        sys.stdout.flush()
        sys.stderr.flush()

        # Check if we're done with an hour.  If so print sum.
        # ===================================================
        if (the_hour == the_hour_last):  # Still in same hour
            minute_sumkw = decimal.Decimal(minute_sumkw) + kw
            minute_counter = minute_counter + 1
        else:  # (a) Hour has changed: Print summary for previous hour, or (b) First time through loop
            if (minute_counter > 0):
                kWh = decimal.Decimal(minute_sumkw / minute_counter)
                mytime = time.localtime()
                print(f"==> DBC.Insert(): {time.strftime('%m/%d/%Y %H:%M:%S')} kWh={kWh}")
                DBC.insert(the_date_prev_db,the_hour_last_db,kWh)
                kWh_day += kWh
            minute_sumkw = kw  # Reset sum to current readung
            minute_counter = 1  # Reset counter
            the_hour_last = the_hour  # Be able to track if hour has changed
            the_hour_last_db = str(the_hour_last) + ":00:00"

            # Stop and start once every hour
            # ===============================
            emu_api.stop_serial()
            time.sleep(5)
            emu_api = Emu(debug=False,fresh_only=True,timeout=5,synchronous=True)
            EMU_Started = emu_api.start_serial(the_port)
            i  = 1
            while (not EMU_Started):
                mytime = time.localtime()
                print("==> [Restart] emu_api.start_serial on \"" + the_port + "\" failure #" + str(i) + " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
            if (i >= 20):
               sys.stdout.flush()
               sys.stderr.flush()
               sys.stdout = stdout_old
               sys.stderr = stderr_old
               if (os.path.exists(alreadyRunning)):
                  os.remove(alreadyRunning)
               mytime = time.localtime()
               print("==> [Restart] emu_api.start_serial failed on \"" + the_port +  "\" at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
               sys.exit(1)
            time.sleep(2)
            EMU_Started = emu_api.start_serial(the_port)
            i = i + 1
            mytime = time.localtime()

        # Midnight Check
        # ==============
        if (the_date != the_date_prev):
            runDays = runDays + 1
            print(f"\n==> New day detected: {the_date}; run_days={str(runDays)} at {time.strftime('%m/%d/%Y %H:%M:%S')}" )
            sys.stdout.flush()
            sys.stderr.flush()
            kWh_day = 0  # Reset Sum
            the_date_prev = the_date  # Update Last Date to Today
            the_date_prev_db = the_date_db  # Update Last Date to Today

        # Sleep until the top of the next minute which is probably
        # less than 60 seconds.  NOTE: SIGBREAK signal is used to
        # break of out sleep() when user Ctr-C on script within
        # CMD.EXE.  SIGINT signal could be used to stop script when
        # it is running within Windows Started Task.
        # ========================================================
        mytime = time.localtime()
        sec_sleep = 60 - int(time.strftime('%S', mytime))
        time.sleep(sec_sleep)


   # ==========================================================================
   #                        End of (Infinite) Main Loop
   # Script exit happens via external Ctrl-C or SIGINT.
   # ==========================================================================


# ==========================================================================
#                         M A I N   P R O G R A M
# Run only as a top-level script, i.e., not as an import
# Is there a benefit to running with function main() as far as process
# control/signal handling??
# ==========================================================================
if __name__ == '__main__':
   main()
