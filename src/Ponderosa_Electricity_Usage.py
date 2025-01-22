#!/usr/bin/python

# Script exit happens via external Ctrl-C or SIGINT.

import sys
import os
import decimal
import argparse

from time import time, ctime
import time
from xmlrpc.client import boolean
from emu_power import Emu

from PonderosaConfig import PonderosaConfig
from PonderosaDB import PonderosaDB
from PonderosaErrorHandler import PonderosaErrorHandler


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

    # Setup signal handler for abnormal or Ctrl-C exit
    mysig = PonderosaErrorHandler(PID,alreadyRunning)

    api = ""
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
    out_file = PC.getout_file()
    out_dir  = PC.getout_dir()

    # Stop execution if this file is found
    stopFile = log_dir + "\\" + "stop.txt"
    if (os.path.exists(stopFile)):
        sys.exit(0)

    # CHECK: Are we currently running?
    # ================================
    alreadyRunning = log_dir + "\\" + "Ponderosa_Electricity_Usage.running"
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
    api = Emu(debug=False,fresh_only=True,timeout=5,synchronous=True)
    startedOK = api.start_serial(the_port)
    i  = 1
    while (not startedOK):
        mytime = time.localtime()
        print("==> [Start] api.start_serial on " + the_port + " failure #" + str(i) + " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
        sys.stdout.flush()
        sys.stderr.flush()
        if (i >= 20):
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = stdout_old
            sys.stderr = stderr_old
            if (os.path.exists(alreadyRunning)):
                os.remove(alreadyRunning)
            mytime = time.localtime()
            print("==> [Start] api.start_serial failed on " + the_port +  " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
            sys.exit(1)
        time.sleep(5)
        startedOK = api.start_serial(the_port)
        i = i + 1

    # --------------------------------------------------------------------------
    # Connection successful, print startup banner
    # --------------------------------------------------------------------------
    mytime = time.localtime()
    print("==> [Start] api.start_serial on " + the_port + " succeeded at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))

    response = api.get_device_info()
    print("Manufacturer:      " + response.manufacturer)
    print("Model ID:          " + response.model_id)
    print("Install Code:      " + response.install_code)
    print("Link Key:          " + response.link_key)
    print("Hardware Version:  " + response.hw_version)
    print("Firmware Version:  " + response.fw_version)
    print("Image Type:        " + response.fw_image_type)
    print("Date Code:         " + response.date_code)

    response = api.get_meter_info()
    print("Meter Mac ID:      " + response.meter_mac + "\n\n")

    sys.stdout.flush()
    sys.stderr.flush()

    out_path = out_dir + "\\" + out_file
    print("\n==> Sending hour output to " + out_path)
    f = open(out_path,"a")
    f.write("Date\tTime\tkWh\n")
    f.flush()


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
    the_date_last = "FIRST_LOOP_INTERATION"
    the_date_last_db = "FIRST_LOOP_INTERATION"

    kWh_day = 0

    # ==========================================================================
    # Main Loop
    # ==========================================================================
    this_date = "<FIRST>"
    prev_date = this_date
    while True:
        if (os.path.exists(stopFile)):
            sys.exit(0)

        loop_counter = loop_counter + 1

        # Get date, time and meter readings
        # ---------------------------------
        mytime      = time.localtime()
        the_date    = time.strftime('%m/%d/%Y', mytime)
        the_date_db = time.strftime('%Y-%m-%d', mytime)
        the_hour    = int(time.strftime('%H', mytime))

        # For midnight comparsion
        if prev_date == "<FIRST>":
            prev_date = this_date
        this_date = the_date

        checkResponse = True
        i = 0
        while (checkResponse):
            i = i + 1
            response = api.get_instantaneous_demand()
            if (response is None):
                print("==> Call to api.get_instantaneous_demand() failed! #" + str(i) + " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
                checkResponse = True
            else:
                if (i == 15):
                    checkResponse = False  # Give up - too many tries
                else:
                    time.sleep(60)

        if (checkResponse):
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = stdout_old
            sys.stderr = stderr_old
            if (os.path.exists(alreadyRunning)):
                os.remove(alreadyRunning)
            mytime = time.localtime()
            print("==> api.get_instantaneous_demand() failed COMPLETELY  at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
            sys.exit(2)

        # Get kWh from 3 values
        demand       = decimal.Decimal(response.demand)
        divisor      = decimal.Decimal(response.divisor)
        multiplier   = decimal.Decimal(response.multiplier)
        kw           = decimal.Decimal(multiplier*(demand/divisor))

        # For first time through loop
        if (the_date_last == "FIRST_LOOP_INTERATION"):
            the_date_last = the_date
        if (the_date_last_db == "FIRST_LOOP_INTERATION"):
            the_date_last_db = the_date_db

        # Check if we're done with an hour.  If so print sum.
        # ===================================================
        if (the_hour == the_hour_last):  # Still in same hour
            minute_sumkw = decimal.Decimal(minute_sumkw) + kw
            minute_counter = minute_counter + 1
        else:  # (a) Hour has changed: Print summary for previous hour, or (b) First time through loop
            if (minute_counter > 0):
                kWh = decimal.Decimal(minute_sumkw / minute_counter)
                f.write(the_date_last + "[" + the_date_last_db + "]\t" + str(the_hour_last) + ":00\t" + str(kWh) + "\n")
                f.flush()
                DBC.insert(DBC,the_date_last_db,the_hour_last_db,kWh)
                kWh_day += kWh
            minute_sumkw = kw  # Reset sum to current readung
            minute_counter = 1  # Reset counter
            the_hour_last = the_hour  # Be able to track if hour has changed
            the_hour_last_db = str(the_hour_last) + ":00:00"

            # Stop and start once every hour
            # ===============================
            api.stop_serial()
            time.sleep(5)
            api = Emu(debug=False,fresh_only=True,timeout=5,synchronous=True)
            startedOK = api.start_serial(the_port)
            i  = 1
            while (not startedOK):
                mytime = time.localtime()
                print("==> [Restart] api.start_serial on " + the_port + " failure #" + str(i) + " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
            if (i >= 20):
               sys.stdout.flush()
               sys.stderr.flush()
               sys.stdout = stdout_old
               sys.stderr = stderr_old
               if (os.path.exists(alreadyRunning)):
                  os.remove(alreadyRunning)
               mytime = time.localtime()
               print("==> [Restart] api.start_serial failed on " + the_port +  " at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))
               sys.exit(1)
            time.sleep(2)
            startedOK = api.start_serial(the_port)
            i = i + 1
            mytime = time.localtime()
            # print("==> [Restart] api.start_serial on " + the_port + " succeeded at " + time.strftime('%m/%d/%Y %H:%M:%S', mytime))

        # Midnight Check
        # ==============
        if this_date != prev_date:
            #fdays.write(the_date_last + "\t" + str(kWh_day) + "\n")
            #fdays.flush()
            runDays = runDays + 1
            print("\n==> New day: run_days=" + str(runDays) + ", Date=" + the_date + ", loop_counter=" + str(loop_counter) + " " + time.strftime('%m/%d/%Y %H:%M:%S') )
            sys.stdout.flush()
            sys.stderr.flush()
            kWh_day = 0  # Reset Sum
            the_date_last = the_date  # Update Last Date to Today
            the_date_last_db = the_date_db  # Update Last Date to Today

        prev_date = this_date  # save date for comparison for midnight check

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
